"""Pre-aggregation storage implementation."""

from typing import Optional

from semantic_layer.drivers.base_driver import BaseDriver as BaseConnector
from semantic_layer.exceptions import ExecutionError
from semantic_layer.pre_aggregations.base import BasePreAggregation, PreAggregationDefinition


class DatabasePreAggregation(BasePreAggregation):
    """Store pre-aggregations as database tables."""

    def __init__(self, connector: BaseConnector, schema_name: str = "pre_aggregations"):
        """Initialize database pre-aggregation storage."""
        self.connector = connector
        self.schema_name = schema_name

    async def _ensure_schema(self) -> None:
        """Ensure pre-aggregation schema exists."""
        sql = f"CREATE SCHEMA IF NOT EXISTS {self.schema_name}"
        try:
            await self.connector.execute_query(sql)
        except Exception:
            # Schema might already exist or not supported
            pass

    async def get_table_name(self, definition: PreAggregationDefinition) -> str:
        """Get table name for pre-aggregation."""
        return f"{self.schema_name}.{definition.cube}_{definition.name}"

    async def exists(self, definition: PreAggregationDefinition) -> bool:
        """Check if pre-aggregation exists."""
        await self._ensure_schema()
        table_name = await self.get_table_name(definition)
        
        # Check if table exists
        check_sql = f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = '{self.schema_name}'
                AND table_name = '{definition.cube}_{definition.name}'
            )
        """
        try:
            results = await self.connector.execute_query(check_sql)
            return results[0].get("exists", False) if results else False
        except Exception:
            return False

    async def create(self, definition: PreAggregationDefinition, sql: str) -> None:
        """Create pre-aggregation table."""
        await self._ensure_schema()
        table_name = await self.get_table_name(definition)
        
        # Create table from query result
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} AS {sql}"
        
        try:
            await self.connector.execute_query(create_sql)
        except Exception as e:
            raise ExecutionError(f"Failed to create pre-aggregation: {str(e)}") from e

    async def refresh(self, definition: PreAggregationDefinition, sql: str) -> None:
        """Refresh pre-aggregation data."""
        table_name = await self.get_table_name(definition)
        
        # Truncate and repopulate
        truncate_sql = f"TRUNCATE TABLE {table_name}"
        insert_sql = f"INSERT INTO {table_name} {sql}"
        
        try:
            await self.connector.execute_query(truncate_sql)
            await self.connector.execute_query(insert_sql)
        except Exception as e:
            raise ExecutionError(f"Failed to refresh pre-aggregation: {str(e)}") from e

