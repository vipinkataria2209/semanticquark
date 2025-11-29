"""Query engine - orchestrates query execution."""

import time
from typing import Any, Dict, Optional

from typing import Any, Dict, Optional

from semantic_layer.auth.base import SecurityContext
from semantic_layer.cache.base import BaseCache
from semantic_layer.cache.key_generator import CacheKeyGenerator
from semantic_layer.connectors.base import BaseConnector
from semantic_layer.exceptions import ExecutionError
from semantic_layer.logging.query_logger import QueryLogger
from semantic_layer.metrics.collector import MetricsCollector
from semantic_layer.models.schema import Schema
from semantic_layer.pre_aggregations.manager import PreAggregationManager
from semantic_layer.query.query import Query
from semantic_layer.query_builder.optimizer import QueryOptimizer
from semantic_layer.query_builder.sql_builder import SQLBuilder
from semantic_layer.result.formatter import ResultFormatter


class QueryEngine:
    """Orchestrates query execution."""

    def __init__(
        self,
        schema: Schema,
        connector: BaseConnector,
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

    async def execute(
        self, query: Query, user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a semantic query and return formatted results."""
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

