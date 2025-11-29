"""Base model classes."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class BaseModelDefinition(BaseModel):
    """Base class for model definitions."""

    name: str = Field(..., description="Name of the model element")
    description: Optional[str] = Field(None, description="Description of the element")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        """Pydantic config."""

        extra = "allow"
        frozen = False

