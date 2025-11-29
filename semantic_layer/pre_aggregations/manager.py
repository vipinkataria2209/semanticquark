"""Pre-aggregation manager."""

from typing import Dict, List, Optional

from semantic_layer.connectors.base import BaseConnector
from semantic_layer.models.cube import Cube
from semantic_layer.models.schema import Schema
from semantic_layer.pre_aggregations.base import BasePreAggregation, PreAggregationDefinition
from semantic_layer.query.query import Query
from semantic_layer.query_builder.sql_builder import SQLBuilder


class PreAggregationManager:
    """Manages pre-aggregations."""

    def __init__(
        self,
        schema: Schema,
        connector: BaseConnector,
        storage: Optional[BasePreAggregation] = None,
    ):
        """Initialize pre-aggregation manager."""
        self.schema = schema
        self.connector = connector
        self.storage = storage
        self.sql_builder = SQLBuilder(schema)
        self._definitions: Dict[str, PreAggregationDefinition] = {}

    def register(self, definition: PreAggregationDefinition) -> None:
        """Register a pre-aggregation definition."""
        self._definitions[definition.name] = definition

    def find_matching_pre_aggregation(self, query: Query) -> Optional[PreAggregationDefinition]:
        """Find a pre-aggregation that matches the query."""
        for definition in self._definitions.values():
            if definition.matches_query(query):
                return definition
        return None

    async def build_pre_aggregation_sql(self, definition: PreAggregationDefinition) -> str:
        """Build SQL for creating pre-aggregation."""
        # Create a query from the pre-aggregation definition
        dimensions = [f"{definition.cube}.{dim}" for dim in definition.dimensions]
        measures = [f"{definition.cube}.{meas}" for meas in definition.measures]
        
        from semantic_layer.query.query import Query as QueryObj
        query = QueryObj(
            dimensions=dimensions,
            measures=measures,
            filters=[],
            order_by=[],
        )
        
        # Generate SQL
        sql = self.sql_builder.build(query)
        
        return sql

    async def create_pre_aggregation(self, definition: PreAggregationDefinition) -> None:
        """Create a pre-aggregation."""
        if not self.storage:
            return
        
        # Build SQL
        sql = await self.build_pre_aggregation_sql(definition)
        
        # Create pre-aggregation
        await self.storage.create(definition, sql)

    async def refresh_pre_aggregation(self, definition: PreAggregationDefinition) -> None:
        """Refresh a pre-aggregation."""
        if not self.storage:
            return
        
        # Build SQL
        sql = await self.build_pre_aggregation_sql(definition)
        
        # Refresh pre-aggregation
        await self.storage.refresh(definition, sql)

