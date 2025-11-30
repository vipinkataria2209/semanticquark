"""Query engine - orchestrates query execution."""

import time
from typing import Any, Dict, Optional

from typing import Any, Dict, Optional

from semantic_layer.auth.base import SecurityContext
from semantic_layer.cache.base import BaseCache
from semantic_layer.cache.key_generator import CacheKeyGenerator
from semantic_layer.drivers.base_driver import BaseDriver
from semantic_layer.exceptions import ExecutionError
from semantic_layer.monitoring.logging import QueryLogger
from semantic_layer.monitoring.metrics import MetricsCollector
from semantic_layer.models.schema import Schema
from semantic_layer.pre_aggregations.manager import PreAggregationManager
from semantic_layer.query.query import Query, QueryTimeDimension
from semantic_layer.sql.optimizer import QueryOptimizer
from semantic_layer.sql.builder import SQLBuilder
from semantic_layer.result.formatter import ResultFormatter


class QueryEngine:
    """Orchestrates query execution."""

    def __init__(
        self,
        schema: Schema,
        connector: BaseDriver,
        cache: Optional[BaseCache] = None,
        cache_ttl: int = 3600,
        query_logger: Optional[QueryLogger] = None,
        pre_aggregation_manager: Optional[PreAggregationManager] = None,
        metrics_collector: Optional[MetricsCollector] = None,
    ):
        """Initialize query engine."""
        self.schema = schema
        self.connector = connector
        self.cache = cache
        self.cache_ttl = cache_ttl
        self.query_logger = query_logger or QueryLogger()
        self.pre_aggregation_manager = pre_aggregation_manager
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.sql_builder = SQLBuilder(schema)
        self.result_formatter = ResultFormatter()
        self.cache_key_generator = CacheKeyGenerator()
        self.query_optimizer = QueryOptimizer()

    def _transform_compare_date_range(self, query: Query) -> list[Query]:
        """Transform compare date range query into multiple queries.
        
        If a time dimension has compare_date_range, this method creates
        one query per date range in the compare_date_range list.
        """
        # Find time dimension with compare_date_range
        compare_date_range_td = None
        compare_date_range_index = None
        
        for index, td in enumerate(query.time_dimensions):
            if td.compare_date_range is not None:
                if compare_date_range_td is not None:
                    raise ValueError("compareDateRange can only exist for one timeDimension")
                compare_date_range_td = td
                compare_date_range_index = index
        
        # If no compare_date_range found, return single query
        if compare_date_range_td is None:
            return [query]
        
        # Create one query per date range
        queries = []
        for date_range in compare_date_range_td.compare_date_range:
            # Create new time dimensions list
            new_time_dimensions = []
            for idx, td in enumerate(query.time_dimensions):
                if idx == compare_date_range_index:
                    # Replace compare_date_range with date_range
                    new_td = QueryTimeDimension(
                        dimension=td.dimension,
                        granularity=td.granularity,
                        date_range=date_range,
                        compare_date_range=None
                    )
                    new_time_dimensions.append(new_td)
                else:
                    new_time_dimensions.append(td)
            
            # Create new query with updated time dimensions
            new_query = Query(
                dimensions=query.dimensions.copy(),
                measures=query.measures.copy(),
                filters=query.filters.copy(),
                measure_filters=query.measure_filters.copy(),
                time_dimensions=new_time_dimensions,
                order_by=query.order_by.copy(),
                limit=query.limit,
                offset=query.offset,
                ctes=query.ctes.copy(),
            )
            queries.append(new_query)
        
        return queries

    async def execute(
        self, query: Query, user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a semantic query and return formatted results.
        
        If the query has compare_date_range, it will be transformed into
        multiple queries and results will be combined.
        """
        start_time = time.time()
        cache_hit = False

        try:
            # Check for compare date range and transform if needed
            queries = self._transform_compare_date_range(query)
            
            # If multiple queries (compare date range), execute all and combine
            if len(queries) > 1:
                # Find original compare_date_range from original query
                original_compare_date_range = None
                for td in query.time_dimensions:
                    if td.compare_date_range:
                        original_compare_date_range = td.compare_date_range
                        break
                
                results_list = []
                for q in queries:
                    result = await self._execute_single_query(q, user_context, start_time)
                    results_list.append(result)
                
                # Combine results with period indicators
                combined_data = []
                for idx, result in enumerate(results_list):
                    for row in result.get("data", []):
                        # Add period indicator
                        if original_compare_date_range and idx < len(original_compare_date_range):
                            date_range = original_compare_date_range[idx]
                            row["_compareDateRange"] = f"{date_range[0]} to {date_range[1]}"
                        combined_data.append(row)
                
                # Return combined result
                return {
                    "data": combined_data,
                    "meta": {
                        "query": {
                            "dimensions": query.dimensions,
                            "measures": query.measures,
                            "time_dimensions": [td.dict() for td in query.time_dimensions],
                        },
                        "execution_time_ms": (time.time() - start_time) * 1000,
                        "row_count": len(combined_data),
                        "compare_date_range": True,
                    }
                }
            
            # Single query execution
            query = queries[0]
            return await self._execute_single_query(query, user_context, start_time)
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            # Log error
            user_id = user_context.get("user_id") if user_context else None
            self.query_logger.log_query(
                query=query,
                execution_time_ms=execution_time,
                cache_hit=False,
                error=str(e),
                user_id=user_id,
            )
            
            # Record error metrics
            self.metrics_collector.record_query(
                execution_time_ms=execution_time,
                cache_hit=False,
                error=True,
            )
            
            raise ExecutionError(
                f"Query execution failed: {str(e)}",
                details={"execution_time_ms": execution_time},
            ) from e

    async def _execute_single_query(
        self, query: Query, user_context: Optional[Dict[str, Any]] = None, start_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """Execute a single query (internal method)."""
        if start_time is None:
            start_time = time.time()
        cache_hit = False

        try:
            # Optimize query
            query = self.query_optimizer.optimize(query)
            
            # Check for pre-aggregation match
            pre_agg_used = False
            pre_agg_table = None
            pre_agg = None
            if self.pre_aggregation_manager:
                pre_agg = self.pre_aggregation_manager.find_matching_pre_aggregation(query)
                if pre_agg and self.pre_aggregation_manager.storage:
                    # Check if pre-aggregation exists
                    exists = await self.pre_aggregation_manager.storage.exists(pre_agg)
                    if exists:
                        # Get pre-aggregation table name
                        pre_agg_table = await self.pre_aggregation_manager.storage.get_table_name(pre_agg)
                        pre_agg_used = True
            
            # Check cache first
            if self.cache:
                cache_key = self.cache_key_generator.generate(query, user_context)
                cached_result = await self.cache.get(cache_key)
                if cached_result is not None:
                    cache_hit = True
                    cached_result["meta"]["cache_hit"] = True
                    cached_result["meta"]["execution_time_ms"] = (time.time() - start_time) * 1000
                    return cached_result

            # Convert user_context to SecurityContext if provided
            security_context = None
            if user_context:
                security_context = SecurityContext(**user_context)
            
            # Apply CTEs from query to SQLBuilder BEFORE building SQL
            # Clear any existing CTEs from previous queries first
            if not hasattr(self.sql_builder, 'with_queries'):
                self.sql_builder.with_queries = []
            self.sql_builder.with_queries.clear()
            
            # Add CTEs from current query
            for cte in query.ctes:
                self.sql_builder.add_with_query(cte["alias"], cte["query"])
            
            # Generate SQL from semantic query with security context
            # If pre-aggregation is available, use it
            if pre_agg_used and pre_agg_table:
                # Modify query to use pre-aggregation table
                # Temporarily override the cube's table
                cube = self.schema.get_cube(pre_agg.cube)
                original_table = cube.table
                cube.table = pre_agg_table
                try:
                    sql = self.sql_builder.build(query, security_context=security_context)
                finally:
                    # Restore original table
                    cube.table = original_table
            else:
                sql = self.sql_builder.build(query, security_context=security_context)
            
            # Clear CTEs after building SQL (for next query)
            # Reset the with_queries list for the next query
            if hasattr(self.sql_builder, 'with_queries'):
                self.sql_builder.with_queries.clear()

            # Execute query
            results = await self.connector.execute_query(sql)

            # Format results
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            formatted_results = self.result_formatter.format(results, query, execution_time)

            # Add SQL to metadata for debugging
            formatted_results["meta"]["sql"] = sql
            formatted_results["meta"]["cache_hit"] = False
            formatted_results["meta"]["pre_aggregation_used"] = pre_agg_used
            formatted_results["meta"]["query_cost"] = self.query_optimizer.estimate_cost(query)

            # Store in cache
            if self.cache and not cache_hit:
                cache_key = self.cache_key_generator.generate(query, user_context)
                await self.cache.set(cache_key, formatted_results, ttl=self.cache_ttl)

            # Log query
            user_id = user_context.get("user_id") if user_context else None
            self.query_logger.log_query(
                query=query,
                execution_time_ms=execution_time,
                cache_hit=cache_hit,
                user_id=user_id,
                sql=sql,
            )
            
            # Record metrics
            self.metrics_collector.record_query(
                execution_time_ms=execution_time,
                cache_hit=cache_hit,
                error=False,
            )

            return formatted_results

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            # Log error
            user_id = user_context.get("user_id") if user_context else None
            self.query_logger.log_query(
                query=query,
                execution_time_ms=execution_time,
                cache_hit=False,
                error=str(e),
                user_id=user_id,
            )
            
            # Record error metrics
            self.metrics_collector.record_query(
                execution_time_ms=execution_time,
                cache_hit=False,
                error=True,
            )
            
            raise ExecutionError(
                f"Query execution failed: {str(e)}",
                details={"execution_time_ms": execution_time},
            ) from e

