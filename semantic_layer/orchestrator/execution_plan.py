"""Query execution planning."""

from typing import Any, Dict, Optional

from semantic_layer.query.query import Query
from semantic_layer.schema.types import Schema
from semantic_layer.pre_aggregations.manager import PreAggregationManager


class ExecutionPlan:
    """Represents a query execution plan."""
    
    def __init__(
        self,
        query: Query,
        schema: Schema,
        pre_aggregation_manager: Optional[PreAggregationManager] = None,
    ):
        """Initialize execution plan."""
        self.query = query
        self.schema = schema
        self.pre_aggregation_manager = pre_aggregation_manager
        self.use_pre_aggregation = False
        self.pre_aggregation = None
        self.pre_aggregation_table = None
    
    async def plan(self) -> "ExecutionPlan":
        """Plan query execution."""
        # Check for pre-aggregation match
        if self.pre_aggregation_manager:
            pre_agg = self.pre_aggregation_manager.find_matching_pre_aggregation(self.query)
            if pre_agg and self.pre_aggregation_manager.storage:
                exists = await self.pre_aggregation_manager.storage.exists(pre_agg)
                if exists:
                    self.use_pre_aggregation = True
                    self.pre_aggregation = pre_agg
                    self.pre_aggregation_table = await self.pre_aggregation_manager.storage.get_table_name(pre_agg)
        
        return self

