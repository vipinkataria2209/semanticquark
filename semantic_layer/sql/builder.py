"""SQL query builder from semantic queries."""

from collections import deque
from typing import Dict, List, Optional, Set, Tuple

from semantic_layer.auth.base import SecurityContext
from semantic_layer.exceptions import ModelError, QueryError
from semantic_layer.models.cube import Cube
from semantic_layer.models.relationship import Relationship
from semantic_layer.models.schema import Schema
from semantic_layer.query.query import Query, LogicalFilter
from semantic_layer.security.rls import RLSFilter


class JoinInfo:
    """Information about a JOIN in a query."""

    def __init__(
        self,
        cube_name: str,
        table_alias: str,
        join_type: str = "LEFT JOIN",
        join_condition: Optional[str] = None,
    ):
        self.cube_name = cube_name
        self.table_alias = table_alias
        self.join_type = join_type
        self.join_condition = join_condition


class SQLBuilder:
    """Builds SQL queries from semantic queries."""

    def __init__(self, schema: Schema):
        """Initialize SQL builder with schema."""
        self.schema = schema
        self.with_queries: List[Dict[str, str]] = []  # List of CTEs: [{"alias": str, "query": str}]
        # Build relationship graph for path finding (similar to Cube.js JoinGraph)
        self._relationship_graph: Dict[str, Dict[str, Relationship]] = {}
        self._build_relationship_graph()

    def build(
        self, query: Query, security_context: Optional[SecurityContext] = None
    ) -> str:
        """Build SQL query from semantic query."""
        # Determine which cubes we need
        required_cubes = self._get_required_cubes(query)

        if not required_cubes:
            raise QueryError("No cubes found for query")

        # Build join plan
        primary_cube_name = list(required_cubes)[0]
        cube_aliases = self._build_join_plan(primary_cube_name, required_cubes)
        
        # Build SELECT clause
        select_parts = []
        group_by_parts = []
        
        # Track if primary key is included and if we can skip GROUP BY
        primary_key_dimension_path = None
        primary_key_dimension_sql = None
        primary_cube = self.schema.get_cube(primary_cube_name)
        
        # Find primary key dimension
        for dim_name, dimension in primary_cube.dimensions.items():
            if dimension.primary_key:
                primary_key_dimension_path = f"{primary_cube_name}.{dim_name}"
                break

        # Add dimensions
        for dim_path in query.dimensions:
            cube, dim_name = self.schema.get_cube_for_dimension(dim_path)
            dimension = cube.get_dimension(dim_name)
            table_alias = cube_aliases[cube.name]
            dim_sql = dimension.get_sql_expression(table_alias)
            select_parts.append(f"{dim_sql} AS {dim_path.replace('.', '_')}")
            
            # Track primary key SQL if this is the primary key
            if dim_path == primary_key_dimension_path:
                primary_key_dimension_sql = dim_sql
            
            group_by_parts.append(dim_sql)

        # Add time dimensions
        for td in query.time_dimensions:
            if td.granularity:
                cube, dim_name = self.schema.get_cube_for_dimension(td.dimension)
                dimension = cube.get_dimension(dim_name)
                table_alias = cube_aliases[cube.name]
                # Pass granularity to get_sql_expression
                dim_sql = dimension.get_sql_expression(table_alias, granularity=td.granularity)
                alias = f"{td.dimension.replace('.', '_')}_{td.granularity}"
                select_parts.append(f"{dim_sql} AS {alias}")
                group_by_parts.append(dim_sql)

        # Add measures
        for meas_path in query.measures:
            cube, meas_name = self.schema.get_cube_for_measure(meas_path)
            measure = cube.get_measure(meas_name)
            table_alias = cube_aliases[cube.name]
            meas_sql = measure.get_sql_expression(table_alias)
            select_parts.append(f"{meas_sql} AS {meas_path.replace('.', '_')}")

        # Build FROM and JOIN clauses
        primary_cube = self.schema.get_cube(primary_cube_name)
        primary_alias = cube_aliases[primary_cube_name]
        from_clause = f"FROM {primary_cube.table} AS {primary_alias}"
        
        join_clauses = self._build_join_clauses(primary_cube_name, required_cubes, cube_aliases)

        # Build WHERE clause
        where_conditions = []
        
        # Add query filters (supports logical operators)
        for filter_obj in query.filters:
            if isinstance(filter_obj, LogicalFilter):
                # Logical filter (AND/OR)
                condition = filter_obj.to_sql_condition(self.schema, cube_aliases)
                where_conditions.append(condition)
            else:
                # Regular QueryFilter
                dimension_name = filter_obj.dimension or filter_obj.member
                cube, dim_name = self.schema.get_cube_for_dimension(dimension_name)
                dimension = cube.get_dimension(dim_name)
                table_alias = cube_aliases[cube.name]
                dim_sql = dimension.get_sql_expression(table_alias)
                # Pass dimension type for proper type casting
                condition = filter_obj.to_sql_condition(dim_sql, dimension_type=dimension.type)
                where_conditions.append(condition)
        
        # Add time dimension date range filters
        for td in query.time_dimensions:
            if td.date_range:
                cube, dim_name = self.schema.get_cube_for_dimension(td.dimension)
                dimension = cube.get_dimension(dim_name)
                table_alias = cube_aliases[cube.name]
                dim_sql = dimension.get_sql_expression(table_alias)
                
                # Add date range filter
                if len(td.date_range) == 1:
                    # Single date - use >= for start of day
                    where_conditions.append(f"{dim_sql} >= '{td.date_range[0]}'")
                elif len(td.date_range) >= 2:
                    # Date range - use >= start AND <= end
                    where_conditions.append(f"{dim_sql} >= '{td.date_range[0]}'")
                    where_conditions.append(f"{dim_sql} <= '{td.date_range[1]}'")
        
        # Add RLS filters for each cube
        if security_context:
            for cube_name in required_cubes:
                cube = self.schema.get_cube(cube_name)
                table_alias = cube_aliases[cube_name]
                rls_filter = RLSFilter.apply_rls_filter(
                    cube=cube,
                    security_context=security_context,
                    table_alias=table_alias,
                )
                if rls_filter:
                    where_conditions.append(rls_filter)

        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)

        # Build GROUP BY clause
        # Optimization: Skip GROUP BY if:
        # 1. No measures (only dimensions)
        # 2. Primary key is included in dimensions
        # 3. Only one cube is involved (no joins)
        skip_group_by = (
            not query.measures and  # No measures
            primary_key_dimension_sql is not None and  # Primary key is included
            len(required_cubes) == 1  # Only one cube (no joins)
        )
        
        group_by_clause = ""
        if group_by_parts and not skip_group_by:
            group_by_clause = "GROUP BY " + ", ".join(group_by_parts)

        # Build HAVING clause for measure filters
        having_conditions = []
        for filter_obj in query.measure_filters:
            if isinstance(filter_obj, LogicalFilter):
                # Logical filter (AND/OR) for measures
                condition = filter_obj.to_sql_condition(self.schema, cube_aliases, is_measure_filter=True)
                having_conditions.append(condition)
            else:
                # Regular QueryFilter for measure
                measure_name = filter_obj.dimension or filter_obj.member
                cube, meas_name = self.schema.get_cube_for_measure(measure_name)
                measure = cube.get_measure(meas_name)
                table_alias = cube_aliases[cube.name]
                meas_sql = measure.get_sql_expression(table_alias)
                # For HAVING, we use the measure SQL expression directly
                condition = filter_obj.to_sql_condition(meas_sql, dimension_type="number")
                having_conditions.append(condition)
        
        having_clause = ""
        if having_conditions:
            having_clause = "HAVING " + " AND ".join(having_conditions)

        # Build ORDER BY clause
        order_by_clause = ""
        if query.order_by:
            order_parts = []
            for order in query.order_by:
                # Ensure order is a QueryOrderBy object with dimension attribute
                if not hasattr(order, 'dimension'):
                    continue  # Skip invalid order_by items
                
                # Try to get as dimension first, then as measure
                order_sql = None
                try:
                    cube, dim_name = self.schema.get_cube_for_dimension(order.dimension)
                    dimension = cube.get_dimension(dim_name)
                    table_alias = cube_aliases[cube.name]
                    order_sql = dimension.get_sql_expression(table_alias)
                except Exception:
                    # If not a dimension, try as measure
                    try:
                        cube, meas_name = self.schema.get_cube_for_measure(order.dimension)
                        measure = cube.get_measure(meas_name)
                        table_alias = cube_aliases[cube.name]
                        order_sql = measure.get_sql_expression(table_alias)
                    except Exception:
                        # Skip if neither dimension nor measure
                        continue
                
                if order_sql:
                    direction = order.direction.upper()
                    order_parts.append(f"{order_sql} {direction}")
            if order_parts:
                order_by_clause = "ORDER BY " + ", ".join(order_parts)

        # Build LIMIT and OFFSET
        limit_clause = ""
        if query.limit:
            limit_clause = f"LIMIT {query.limit}"
            if query.offset:
                limit_clause += f" OFFSET {query.offset}"

        # Build WITH clause (CTEs)
        with_clause = self._build_with_clause()

        # Assemble SQL
        sql_parts = [
            with_clause,
            "SELECT",
            ", ".join(select_parts),
            from_clause,
            join_clauses,
            where_clause,
            group_by_clause,
            having_clause,
            order_by_clause,
            limit_clause,
        ]

        sql = " ".join(filter(None, sql_parts))
        return sql
    
    def add_with_query(self, alias: str, query: str) -> None:
        """Add a CTE (Common Table Expression) to the query.
        
        Args:
            alias: The alias name for the CTE
            query: The SQL query for the CTE
        """
        self.with_queries.append({"alias": alias, "query": query})
    
    def _build_with_clause(self) -> str:
        """Build WITH clause from CTEs."""
        if not self.with_queries:
            return ""
        
        cte_definitions = [
            f"{cte['alias']} AS ({cte['query']})"
            for cte in self.with_queries
        ]
        newline = '\n'
        comma_newline = ',\n'
        return f"WITH{newline}{comma_newline.join(cte_definitions)}{newline}"

    def _build_join_plan(
        self, primary_cube_name: str, required_cubes: Set[str]
    ) -> Dict[str, str]:
        """Build a plan for joining cubes and return cube to alias mapping.
        
        This method assigns aliases to all cubes that will be joined, including
        intermediate cubes in paths (e.g., if joining orders->countries, we need
        aliases for orders, customers, and countries).
        """
        cube_aliases: Dict[str, str] = {primary_cube_name: "t0"}
        
        if len(required_cubes) == 1:
            return cube_aliases

        # Find all cubes that need to be joined (including intermediate cubes in paths)
        all_cubes_to_join = {primary_cube_name}
        remaining_cubes = required_cubes - {primary_cube_name}
        
        # For each required cube, find its path and add all intermediate cubes
        for cube_name in remaining_cubes:
            path = self._find_path_bfs(primary_cube_name, cube_name)
            if path:
                # Add all cubes in the path
                all_cubes_to_join.update(path)
        
        # Assign aliases to all cubes that need to be joined
        alias_counter = 1
        for cube_name in sorted(all_cubes_to_join):
            if cube_name not in cube_aliases:
                cube_aliases[cube_name] = f"t{alias_counter}"
                alias_counter += 1

        return cube_aliases

    def _build_join_clauses(
        self, primary_cube_name: str, required_cubes: Set[str], cube_aliases: Dict[str, str]
    ) -> str:
        """Build JOIN clauses for all required cubes.
        
        This method builds joins by finding paths from the primary cube to each
        required cube. For indirect paths (A->B->C), it builds joins incrementally,
        ensuring intermediate cubes are joined first.
        """
        if len(required_cubes) == 1:
            return ""

        join_clauses = []
        primary_cube = self.schema.get_cube(primary_cube_name)
        primary_alias = cube_aliases[primary_cube_name]
        joined_cubes = {primary_cube_name}

        # Build joins for each remaining cube
        remaining_cubes = required_cubes - {primary_cube_name}
        
        # Find paths for all remaining cubes
        cube_paths: Dict[str, List[str]] = {}
        for cube_name in remaining_cubes:
            path = self._find_path_bfs(primary_cube_name, cube_name)
            if path:
                cube_paths[cube_name] = path
        
        # Sort cubes by path length (shortest first) to ensure intermediate cubes are joined first
        sorted_cubes = sorted(cube_paths.items(), key=lambda x: len(x[1]))
        
        # Build joins following the paths
        for cube_name, path in sorted_cubes:
            # Join each hop in the path
            for i in range(len(path) - 1):
                hop_from = path[i]
                hop_to = path[i + 1]
                
                # Skip if already joined
                if hop_to in joined_cubes:
                    continue
                
                # Find join info for this hop
                join_info = None
                if hop_from in self._relationship_graph and hop_to in self._relationship_graph[hop_from]:
                    relationship = self._relationship_graph[hop_from][hop_to]
                    join_info = self._create_join_info(
                        relationship, hop_from, hop_to, cube_aliases
                    )
                elif hop_to in self._relationship_graph and hop_from in self._relationship_graph[hop_to]:
                    relationship = self._relationship_graph[hop_to][hop_from]
                    join_info = self._create_reverse_join_info(
                        relationship, hop_from, hop_to, cube_aliases
                    )
                
                if join_info:
                    target_cube = self.schema.get_cube(hop_to)
                    target_alias = cube_aliases[hop_to]
                    join_clause = f"{join_info.join_type} {target_cube.table} AS {target_alias} ON {join_info.join_condition}"
                    join_clauses.append(join_clause)
                    joined_cubes.add(hop_to)

        return " ".join(join_clauses) if join_clauses else ""

    def _build_relationship_graph(self) -> None:
        """Build a directed graph of all cube relationships for path finding.
        
        Similar to Cube.js JoinGraph.compile(), this builds an adjacency list
        representation of the relationship graph where:
        - Nodes are cube names
        - Edges are relationships between cubes
        - Graph is directed: from_cube -> to_cube
        """
        self._relationship_graph = {}
        
        # Build graph from all cubes and their relationships
        for cube_name, cube in self.schema.cubes.items():
            if cube_name not in self._relationship_graph:
                self._relationship_graph[cube_name] = {}
            
            # Add direct relationships (from_cube -> to_cube)
            for rel_name, relationship in cube.relationships.items():
                target_cube = relationship.cube
                # Store relationship with key as target cube name
                self._relationship_graph[cube_name][target_cube] = relationship

    def _find_join_path(
        self,
        from_cube: str,
        to_cube: str,
        already_joined: Set[str],
        cube_aliases: Dict[str, str],
    ) -> Optional[JoinInfo]:
        """Find a join path from one cube to another using BFS graph traversal.
        
        This implements the same functionality as Cube.js JoinGraph.buildJoinTreeForRoot(),
        using BFS (Breadth-First Search) to find the shortest path between cubes.
        Works for both direct relationships (A->B) and indirect paths (A->B->C).
        
        Args:
            from_cube: Source cube name
            to_cube: Target cube name
            already_joined: Set of cubes already joined (for optimization)
            cube_aliases: Mapping of cube names to table aliases
            
        Returns:
            JoinInfo for the first hop in the path, or None if no path exists
        """
        # If same cube, no join needed
        if from_cube == to_cube:
            return None
        
        # First, try direct relationship (fast path)
        if from_cube in self._relationship_graph:
            if to_cube in self._relationship_graph[from_cube]:
                relationship = self._relationship_graph[from_cube][to_cube]
                return self._create_join_info(
                    relationship, from_cube, to_cube, cube_aliases
                )
        
        # Check reverse relationships (if to_cube has relationship to from_cube)
        if to_cube in self._relationship_graph:
            if from_cube in self._relationship_graph[to_cube]:
                relationship = self._relationship_graph[to_cube][from_cube]
                return self._create_reverse_join_info(
                    relationship, from_cube, to_cube, cube_aliases
                )
        
        # Use BFS to find indirect path (A->B->C)
        path = self._find_path_bfs(from_cube, to_cube)
        if not path or len(path) < 2:
            return None
        
        # Return join info for the first hop in the path
        # The rest of the path will be handled in subsequent calls
        first_hop_from = path[0]
        first_hop_to = path[1]
        
        if first_hop_from in self._relationship_graph:
            if first_hop_to in self._relationship_graph[first_hop_from]:
                relationship = self._relationship_graph[first_hop_from][first_hop_to]
                return self._create_join_info(
                    relationship, first_hop_from, first_hop_to, cube_aliases
                )
        
        return None

    def _find_path_bfs(self, from_cube: str, to_cube: str) -> Optional[List[str]]:
        """Find shortest path between two cubes using BFS (Breadth-First Search).
        
        Similar to Cube.js graph.path() using Dijkstra, but uses BFS since
        all edges have weight 1 (unweighted graph). This ensures we find the
        shortest path (minimum number of hops) between cubes.
        
        The algorithm supports bidirectional traversal:
        - Forward: A -> B (A has relationship to B)
        - Reverse: A <- B (B has relationship to A, so we can traverse B -> A)
        
        Args:
            from_cube: Source cube name
            to_cube: Target cube name
            
        Returns:
            List of cube names representing the path, or None if no path exists
            Example: ['orders', 'customers', 'countries']
        """
        if from_cube == to_cube:
            return [from_cube]
        
        # BFS queue: (current_cube, path_so_far)
        queue = deque([(from_cube, [from_cube])])
        visited = {from_cube}
        
        # Build reverse index for efficient reverse relationship lookup
        # This avoids nested loops in the BFS traversal
        reverse_graph: Dict[str, Set[str]] = {}
        for source_cube, targets in self._relationship_graph.items():
            for target_cube in targets:
                if target_cube not in reverse_graph:
                    reverse_graph[target_cube] = set()
                reverse_graph[target_cube].add(source_cube)
        
        while queue:
            current_cube, path = queue.popleft()
            
            # Get all cubes directly connected via forward relationships
            if current_cube in self._relationship_graph:
                for next_cube, relationship in self._relationship_graph[current_cube].items():
                    if next_cube == to_cube:
                        # Found path!
                        return path + [next_cube]
                    
                    if next_cube not in visited:
                        visited.add(next_cube)
                        queue.append((next_cube, path + [next_cube]))
            
            # Get all cubes connected via reverse relationships (bidirectional traversal)
            if current_cube in reverse_graph:
                for prev_cube in reverse_graph[current_cube]:
                    if prev_cube == to_cube:
                        # Found path via reverse relationship!
                        return path + [prev_cube]
                    
                    if prev_cube not in visited:
                        visited.add(prev_cube)
                        queue.append((prev_cube, path + [prev_cube]))
        
        return None  # No path found

    def _create_join_info(
        self,
        relationship: Relationship,
        from_cube: str,
        to_cube: str,
        cube_aliases: Dict[str, str],
    ) -> JoinInfo:
        """Create join info from a relationship."""
        from_cube_obj = self.schema.get_cube(from_cube)
        to_cube_obj = self.schema.get_cube(to_cube)
        from_alias = cube_aliases[from_cube]
        to_alias = cube_aliases[to_cube]

        if relationship.type == "belongs_to":
            # from_cube has foreign_key pointing to to_cube
            left_key = relationship.foreign_key
            right_key = relationship.primary_key or "id"
            join_condition = f"{from_alias}.{left_key} = {to_alias}.{right_key}"
        elif relationship.type == "has_many" or relationship.type == "has_one":
            # from_cube is referenced by to_cube's foreign_key
            left_key = relationship.primary_key or "id"
            right_key = relationship.foreign_key
            join_condition = f"{from_alias}.{left_key} = {to_alias}.{right_key}"
        else:
            raise QueryError(f"Unsupported relationship type: {relationship.type}")

        return JoinInfo(
            cube_name=to_cube,
            table_alias=to_alias,
            join_type="LEFT JOIN",
            join_condition=join_condition,
        )

    def _create_reverse_join_info(
        self,
        relationship: Relationship,
        from_cube: str,
        to_cube: str,
        cube_aliases: Dict[str, str],
    ) -> JoinInfo:
        """Create join info from a reverse relationship."""
        from_cube_obj = self.schema.get_cube(from_cube)
        to_cube_obj = self.schema.get_cube(to_cube)
        from_alias = cube_aliases[from_cube]
        to_alias = cube_aliases[to_cube]

        if relationship.type == "belongs_to":
            # Reverse: to_cube belongs_to from_cube, so from_cube has_many to_cube
            left_key = relationship.primary_key or "id"
            right_key = relationship.foreign_key
            join_condition = f"{from_alias}.{left_key} = {to_alias}.{right_key}"
        elif relationship.type == "has_many" or relationship.type == "has_one":
            # Reverse: to_cube has_many from_cube, so from_cube belongs_to to_cube
            left_key = relationship.foreign_key
            right_key = relationship.primary_key or "id"
            join_condition = f"{from_alias}.{left_key} = {to_alias}.{right_key}"
        else:
            raise QueryError(f"Unsupported relationship type: {relationship.type}")

        return JoinInfo(
            cube_name=to_cube,
            table_alias=to_alias,
            join_type="LEFT JOIN",
            join_condition=join_condition,
        )

    def _get_required_cubes(self, query: Query) -> Set[str]:
        """Get set of cube names required for this query."""
        cubes: Set[str] = set()

        # Get cubes from dimensions
        for dim_path in query.dimensions:
            cube_name, _ = dim_path.split(".", 1)
            cubes.add(cube_name)

        # Get cubes from measures
        for meas_path in query.measures:
            cube_name, _ = meas_path.split(".", 1)
            cubes.add(cube_name)

        # Get cubes from filters
        for filter_obj in query.filters:
            if isinstance(filter_obj, LogicalFilter):
                # Recursively get cubes from nested filters
                if filter_obj.or_:
                    for nested_filter in filter_obj.or_:
                        if isinstance(nested_filter, LogicalFilter):
                            # Recursive call would be complex, so we'll extract from nested filters
                            cubes.update(self._get_cubes_from_filter(nested_filter))
                        else:
                            dimension_name = nested_filter.dimension or nested_filter.member
                            if dimension_name:
                                cube_name, _ = dimension_name.split(".", 1)
                                cubes.add(cube_name)
                elif filter_obj.and_:
                    for nested_filter in filter_obj.and_:
                        if isinstance(nested_filter, LogicalFilter):
                            cubes.update(self._get_cubes_from_filter(nested_filter))
                        else:
                            dimension_name = nested_filter.dimension or nested_filter.member
                            if dimension_name:
                                cube_name, _ = dimension_name.split(".", 1)
                                cubes.add(cube_name)
            else:
                dimension_name = filter_obj.dimension or filter_obj.member
                if dimension_name:
                    cube_name, _ = dimension_name.split(".", 1)
                    cubes.add(cube_name)

        # Get cubes from order_by
        for order in query.order_by:
            # Ensure order is a QueryOrderBy object with dimension attribute
            if hasattr(order, 'dimension') and order.dimension:
                cube_name, _ = order.dimension.split(".", 1)
                cubes.add(cube_name)

        return cubes

    def _get_cubes_from_filter(self, filter_obj) -> Set[str]:
        """Recursively extract cube names from a filter (handles LogicalFilter)."""
        cubes: Set[str] = set()
        if isinstance(filter_obj, LogicalFilter):
            if filter_obj.or_:
                for nested_filter in filter_obj.or_:
                    cubes.update(self._get_cubes_from_filter(nested_filter))
            elif filter_obj.and_:
                for nested_filter in filter_obj.and_:
                    cubes.update(self._get_cubes_from_filter(nested_filter))
        else:
            dimension_name = filter_obj.dimension or filter_obj.member
            if dimension_name:
                cube_name, _ = dimension_name.split(".", 1)
                cubes.add(cube_name)
        return cubes

