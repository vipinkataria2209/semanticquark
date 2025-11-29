"""Base pre-aggregation interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from semantic_layer.models.cube import Cube
from semantic_layer.query.query import Query


class PreAggregationDefinition:
    """Pre-aggregation definition."""

    def __init__(
        self,
        name: str,
        cube: str,
        dimensions: List[str],
        measures: List[str],
        time_dimension: Optional[str] = None,
        granularity: Optional[str] = None,
        refresh_key: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.cube = cube
        self.dimensions = dimensions
        self.measures = measures
        self.time_dimension = time_dimension
        self.granularity = granularity
        self.refresh_key = refresh_key or {}

    def matches_query(self, query: Query) -> bool:
        """Check if this pre-aggregation matches a query."""
        # Check if query uses this cube
        query_cubes = set()
        for dim in query.dimensions:
            cube_name = dim.split(".")[0]
            query_cubes.add(cube_name)
        for meas in query.measures:
            cube_name = meas.split(".")[0]
            query_cubes.add(cube_name)
        
        if self.cube not in query_cubes:
            return False
        
        # Check if query dimensions are subset of pre-aggregation dimensions
        query_dims = {dim.split(".")[1] for dim in query.dimensions if dim.startswith(f"{self.cube}.")}
        if not query_dims.issubset(set(self.dimensions)):
            return False
        
        # Check if query measures are subset of pre-aggregation measures
        query_meas = {meas.split(".")[1] for meas in query.measures if meas.startswith(f"{self.cube}.")}
        if not query_meas.issubset(set(self.measures)):
            return False
        
        return True


class BasePreAggregation(ABC):
    """Base interface for pre-aggregation storage."""

    @abstractmethod
    async def create(self, definition: PreAggregationDefinition, sql: str) -> None:
        """Create pre-aggregation table/view."""
        pass

    @abstractmethod
    async def refresh(self, definition: PreAggregationDefinition, sql: str) -> None:
        """Refresh pre-aggregation data."""
        pass

    @abstractmethod
    async def exists(self, definition: PreAggregationDefinition) -> bool:
        """Check if pre-aggregation exists."""
        pass

    @abstractmethod
    async def get_table_name(self, definition: PreAggregationDefinition) -> str:
        """Get table name for pre-aggregation."""
        pass

