"""Data model definitions (backward compatibility layer)."""

# Keep original imports to avoid circular dependency
from semantic_layer.models.cube import Cube
from semantic_layer.models.dimension import Dimension
from semantic_layer.models.measure import Measure
from semantic_layer.models.relationship import Relationship
from semantic_layer.models.schema import Schema, SchemaLoader

# Warn about deprecation when imported
import warnings
import sys

if sys.modules.get('semantic_layer.models') == sys.modules[__name__]:
    warnings.warn(
        "semantic_layer.models is deprecated. Use semantic_layer.schema instead.",
        DeprecationWarning,
        stacklevel=2
    )

__all__ = [
    "Cube",
    "Dimension",
    "Measure",
    "Relationship",
    "Schema",
    "SchemaLoader",
]
