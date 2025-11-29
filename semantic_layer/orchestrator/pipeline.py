"""Query execution pipeline."""

from typing import Any, Dict, List, Optional

from semantic_layer.query.query import Query
from semantic_layer.drivers.base_driver import BaseDriver
from semantic_layer.sql.generator import SQLGenerator
from semantic_layer.result.formatter import ResultFormatter


class QueryPipeline:
    """Query execution pipeline."""
    
    def __init__(
        self,
        sql_generator: SQLGenerator,
        driver: BaseDriver,
        result_formatter: ResultFormatter,
    ):
        """Initialize query pipeline."""
        self.sql_generator = sql_generator
        self.driver = driver
        self.result_formatter = result_formatter
    
    async def execute(
        self,
        query: Query,
        security_context: Optional[Any] = None,
        pre_aggregation_table: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Execute query through pipeline."""
        # Generate SQL
        sql = self.sql_generator.generate(query, security_context)
        
        # If pre-aggregation table is provided, modify SQL to use it
        if pre_aggregation_table:
            # Replace table name in FROM clause
            # This is a simplified approach - in production, would need proper SQL parsing
            sql = sql.replace(
                f"FROM {query.dimensions[0].split('.')[0]}",
                f"FROM {pre_aggregation_table}"
            )
        
        # Execute query
        results = await self.driver.execute_query(sql)
        
        # Format results
        formatted_results = self.result_formatter.format(results)
        
        return formatted_results

