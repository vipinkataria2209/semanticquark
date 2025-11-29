"""Query optimizer for SQL generation."""

from typing import List, Set

from semantic_layer.query.query import Query


class QueryOptimizer:
    """Optimizes queries before SQL generation."""

    @staticmethod
    def optimize(query: Query) -> Query:
        """Optimize query."""
        # Remove duplicate dimensions
        query.dimensions = list(dict.fromkeys(query.dimensions))
        
        # Remove duplicate measures
        query.measures = list(dict.fromkeys(query.measures))
        
        # Optimize filters (combine similar filters)
        optimized_filters = QueryOptimizer._optimize_filters(query.filters)
        query.filters = optimized_filters
        
        # Optimize order_by (remove duplicates)
        seen_orders = set()
        optimized_orders = []
        for order in query.order_by:
            key = (order.dimension, order.direction)
            if key not in seen_orders:
                seen_orders.add(key)
                optimized_orders.append(order)
        query.order_by = optimized_orders
        
        return query

    @staticmethod
    def _optimize_filters(filters: List) -> List:
        """Optimize filter list."""
        # Group filters by dimension
        filter_groups = {}
        for f in filters:
            if f.dimension not in filter_groups:
                filter_groups[f.dimension] = []
            filter_groups[f.dimension].append(f)
        
        # Optimize each group
        optimized = []
        for dimension, group in filter_groups.items():
            if len(group) == 1:
                optimized.append(group[0])
            else:
                # Combine multiple filters on same dimension
                # For now, just keep all (could be smarter)
                optimized.extend(group)
        
        return optimized

    @staticmethod
    def estimate_cost(query: Query) -> int:
        """Estimate query cost (simplified)."""
        cost = 0
        
        # Base cost
        cost += 10
        
        # Cost per dimension
        cost += len(query.dimensions) * 2
        
        # Cost per measure
        cost += len(query.measures) * 5
        
        # Cost per filter
        cost += len(query.filters) * 3
        
        # Cost for joins (estimated from dimensions/measures)
        cubes = set()
        for dim in query.dimensions:
            cubes.add(dim.split(".")[0])
        for meas in query.measures:
            cubes.add(meas.split(".")[0])
        
        # More cubes = more joins = higher cost
        if len(cubes) > 1:
            cost += (len(cubes) - 1) * 20
        
        return cost

