"""Metrics callback handler."""

from typing import Any, Dict, Optional
from uuid import UUID

from semantic_layer.monitoring.callbacks import BaseQueryCallback
from semantic_layer.monitoring.metrics import MetricsCollector


class MetricsCallbackHandler(BaseQueryCallback):
    """Callback handler that collects metrics using MetricsCollector.
    
    This handler wraps the existing MetricsCollector to provide
    callback-based metrics collection while maintaining backward compatibility.
    """

    def __init__(self, metrics_collector: Optional[MetricsCollector] = None, enabled: bool = True):
        """Initialize metrics callback handler.
        
        Args:
            metrics_collector: Optional MetricsCollector instance (creates new one if not provided)
            enabled: Whether metrics collection is enabled
        """
        self.metrics_collector = metrics_collector or MetricsCollector(enabled=enabled)

    def on_query_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Record successful query metrics."""
        execution_time_ms = outputs.get("meta", {}).get("execution_time_ms", 0)
        cache_hit = outputs.get("meta", {}).get("cache_hit", False)

        self.metrics_collector.record_query(
            execution_time_ms=execution_time_ms,
            cache_hit=cache_hit,
            error=False,
        )

    def on_query_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Record error metrics."""
        execution_time_ms = kwargs.get("execution_time_ms", 0)

        self.metrics_collector.record_query(
            execution_time_ms=execution_time_ms,
            cache_hit=False,
            error=True,
        )

    def on_cache_hit(
        self,
        cache_key: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Record cache hit."""
        # Metrics are recorded in on_query_end, but we can track here too
        pass

    def on_cache_miss(
        self,
        cache_key: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Record cache miss."""
        # Metrics are recorded in on_query_end, but we can track here too
        pass

    def get_stats(self):
        """Get current statistics from the underlying MetricsCollector."""
        return self.metrics_collector.get_stats()

