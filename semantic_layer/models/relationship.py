"""Relationship model definition."""

from typing import Literal, Optional

from pydantic import Field

from semantic_layer.models.base import BaseModelDefinition


class Relationship(BaseModelDefinition):
    """Represents a relationship between cubes."""

    type: Literal["belongs_to", "has_many", "has_one"] = Field(
        ..., description="Type of relationship"
    )
    cube: str = Field(..., description="Name of the related cube")
    foreign_key: str = Field(..., description="Foreign key column")
    primary_key: Optional[str] = Field(None, description="Primary key column in related cube")

    def get_join_condition(
        self, left_table: str, left_key: str, right_table: str, right_key: str
    ) -> str:
        """Get SQL join condition."""
        return f"{left_table}.{left_key} = {right_table}.{right_key}"

