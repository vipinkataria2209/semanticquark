"""Metrics (backward compatibility layer)."""

# Backward compatibility: redirect old imports to new location
import warnings

warnings.warn(
    "semantic_layer.metrics is deprecated. Use semantic_layer.monitoring instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import from new location
from semantic_layer.monitoring import MetricsCollector

__all__ = ["MetricsCollector"]
