"""Query engine (backward compatibility layer)."""

# Backward compatibility: redirect old imports to new location
import warnings

warnings.warn(
    "semantic_layer.engine is deprecated. Use semantic_layer.orchestrator instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import from new location
from semantic_layer.orchestrator import QueryEngine

__all__ = ["QueryEngine"]
