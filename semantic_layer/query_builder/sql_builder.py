"""SQL query builder from semantic queries."""

from typing import Dict, List, Optional, Set, Tuple

from semantic_layer.auth.base import SecurityContext
from semantic_layer.exceptions import ModelError, QueryError
from semantic_layer.models.cube import Cube
from semantic_layer.models.relationship import Relationship
from semantic_layer.models.schema import Schema
from semantic_layer.query.query import Query
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

        # Add dimensions
        for dim_path in query.dimensions:
            cube, dim_name = self.schema.get_cube_for_dimension(dim_path)
            dimension = cube.get_dimension(dim_name)
            table_alias = cube_aliases[cube.name]
            dim_sql = dimension.get_sql_expression(table_alias)
            select_parts.append(f"{dim_sql} AS {dim_path.replace('.', '_')}")
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
        
        # Add query filters
        for filter_obj in query.filters:
            cube, dim_name = self.schema.get_cube_for_dimension(filter_obj.dimension)
            dimension = cube.get_dimension(dim_name)
            table_alias = cube_aliases[cube.name]
            dim_sql = dimension.get_sql_expression(table_alias)
            # Pass dimension type for proper type casting
            condition = filter_obj.to_sql_condition(dim_sql, dimension_type=dimension.type)
            where_conditions.append(condition)
        
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
        group_by_clause = ""
        if group_by_parts:
            group_by_clause = "GROUP BY " + ", ".join(group_by_parts)

        # Build ORDER BY clause
        order_by_clause = ""
        if query.order_by:
            order_parts = []
            for order in query.order_by:
                cube, dim_name = self.schema.get_cube_for_dimension(order.dimension)
                dimension = cube.get_dimension(dim_name)
                table_alias = cube_aliases[cube.name]
                dim_sql = dimension.get_sql_expression(table_alias)
                direction = order.direction.upper()
                order_parts.append(f"{dim_sql} {direction}")
            order_by_clause = "ORDER BY " + ", ".join(order_parts)

        # Build LIMIT and OFFSET
        limit_clause = ""
        if query.limit:
            limit_clause = f"LIMIT {query.limit}"
            if query.offset:
                limit_clause += f" OFFSET {query.offset}"

        # Assemble SQL
        sql_parts = [
            "SELECT",
            ", ".join(select_parts),
            from_clause,
            join_clauses,
            where_clause,
            group_by_clause,
            order_by_clause,
            limit_clause,
        ]

        sql = " ".join(filter(None, sql_parts))
        return sql

    def _build_join_plan(
        self, primary_cube_name: str, required_cubes: Set[str]
    ) -> Dict[str, str]:
        """Build a plan for joining cubes and return cube to alias mapping."""
        cube_aliases: Dict[str, str] = {primary_cube_name: "t0"}
        
        if len(required_cubes) == 1:
            return cube_aliases

        # Find join paths from primary cube to all other cubes
        remaining_cubes = required_cubes - {primary_cube_name}
        alias_counter = 1

        for cube_name in remaining_cubes:
            if cube_name not in cube_aliases:
                cube_aliases[cube_name] = f"t{alias_counter}"
                alias_counter += 1

        return cube_aliases

    def _build_join_clauses(
        self, primary_cube_name: str, required_cubes: Set[str], cube_aliases: Dict[str, str]
    ) -> str:
        """Build JOIN clauses for all required cubes."""
        if len(required_cubes) == 1:
            return ""

        join_clauses = []
        primary_cube = self.schema.get_cube(primary_cube_name)
        primary_alias = cube_aliases[primary_cube_name]
        joined_cubes = {primary_cube_name}

        # Build joins for each remaining cube
        remaining_cubes = required_cubes - {primary_cube_name}
        
        for cube_name in remaining_cubes:
            join_info = self._find_join_path(primary_cube_name, cube_name, joined_cubes, cube_aliases)
            if join_info:
                target_cube = self.schema.get_cube(cube_name)
                target_alias = cube_aliases[cube_name]
                join_clause = f"{join_info.join_type} {target_cube.table} AS {target_alias} ON {join_info.join_condition}"
                join_clauses.append(join_clause)
                joined_cubes.add(cube_name)

        return " ".join(join_clauses) if join_clauses else ""

    def _find_join_path(
        self,
        from_cube: str,
        to_cube: str,
        already_joined: Set[str],
        cube_aliases: Dict[str, str],
    ) -> Optional[JoinInfo]:
        """Find a join path from one cube to another."""
        from_cube_obj = self.schema.get_cube(from_cube)
        
        # Check direct relationships
        for rel_name, relationship in from_cube_obj.relationships.items():
            if relationship.cube == to_cube:
                return self._create_join_info(
                    relationship, from_cube, to_cube, cube_aliases
                )

        # Check reverse relationships (if to_cube has relationship to from_cube)
        to_cube_obj = self.schema.get_cube(to_cube)
        for rel_name, relationship in to_cube_obj.relationships.items():
            if relationship.cube == from_cube:
                # Reverse the relationship
                return self._create_reverse_join_info(
                    relationship, from_cube, to_cube, cube_aliases
                )

        # If no direct relationship, try to find a path through other cubes
        # This is a simplified version - in production, you'd want a proper pathfinding algorithm
        return None

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
            cube_name, _ = filter_obj.dimension.split(".", 1)
            cubes.add(cube_name)

        # Get cubes from order_by
        for order in query.order_by:
            cube_name, _ = order.dimension.split(".", 1)
            cubes.add(cube_name)

        return cubes

