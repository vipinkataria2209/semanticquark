"""Query builder (backward compatibility layer)."""

# Backward compatibility: redirect old imports to new location
import warnings

warnings.warn(
    "semantic_layer.query_builder is deprecated. Use semantic_layer.sql instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import from new location
from semantic_layer.sql import SQLBuilder, SQLGenerator, QueryOptimizer

__all__ = ["SQLBuilder", "SQLGenerator", "QueryOptimizer"]
