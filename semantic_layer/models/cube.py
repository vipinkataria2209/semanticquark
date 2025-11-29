"""Cube model definition."""

from typing import Dict, List, Optional, Any

from pydantic import Field

from semantic_layer.exceptions import ModelError
from semantic_layer.models.base import BaseModelDefinition
from semantic_layer.models.dimension import Dimension
from semantic_layer.models.measure import Measure
from semantic_layer.models.relationship import Relationship


class Cube(BaseModelDefinition):
    """Represents a cube (logical data model)."""

    table: str = Field(..., description="Database table name")
    dimensions: Dict[str, Dimension] = Field(default_factory=dict, description="Dimensions in the cube")
    measures: Dict[str, Measure] = Field(default_factory=dict, description="Measures in the cube")
    relationships: Dict[str, Relationship] = Field(
        default_factory=dict, description="Relationships to other cubes"
    )
    sql: Optional[str] = Field(None, description="Custom SQL for the cube")
    security: Optional[Dict[str, Any]] = Field(
        None, description="Security configuration (row_filter, etc.)"
    )
    pre_aggregations: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="Pre-aggregation definitions"
    )

    def get_dimension(self, name: str) -> Dimension:
        """Get a dimension by name."""
        if name not in self.dimensions:
            raise ModelError(f"Dimension '{name}' not found in cube '{self.name}'")
        return self.dimensions[name]

    def get_measure(self, name: str) -> Measure:
        """Get a measure by name."""
        if name not in self.measures:
            raise ModelError(f"Measure '{name}' not found in cube '{self.name}'")
        return self.measures[name]

    def get_relationship(self, name: str) -> Relationship:
        """Get a relationship by name."""
        if name not in self.relationships:
            raise ModelError(f"Relationship '{name}' not found in cube '{self.name}'")
        return self.relationships[name]

    def validate(self) -> None:
        """Validate the cube definition."""
        if not self.table and not self.sql:
            raise ModelError(f"Cube '{self.name}' must have either 'table' or 'sql' defined")

        if not self.dimensions and not self.measures:
            raise ModelError(f"Cube '{self.name}' must have at least one dimension or measure")

