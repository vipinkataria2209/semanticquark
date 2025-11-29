"""Logging (backward compatibility layer)."""

# Backward compatibility: redirect old imports to new location
import warnings

warnings.warn(
    "semantic_layer.logging is deprecated. Use semantic_layer.monitoring instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import from new location
from semantic_layer.monitoring import QueryLogger

__all__ = ["QueryLogger"]

