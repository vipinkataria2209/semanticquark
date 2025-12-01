"""Monitoring and observability for SemanticQuark."""

# Legacy imports (backward compatibility)
from semantic_layer.monitoring.logging import QueryLogger
from semantic_layer.monitoring.metrics import MetricsCollector

# New callback-based system
from semantic_layer.monitoring.callbacks import BaseQueryCallback
from semantic_layer.monitoring.callback_manager import CallbackManager

# Built-in handlers
from semantic_layer.monitoring.handlers import (
    LoggingCallbackHandler,
    MetricsCallbackHandler,
)

__all__ = [
    # Legacy
    "QueryLogger",
    "MetricsCollector",
    # New callback system
    "BaseQueryCallback",
    "CallbackManager",
    "LoggingCallbackHandler",
    "MetricsCallbackHandler",
]
