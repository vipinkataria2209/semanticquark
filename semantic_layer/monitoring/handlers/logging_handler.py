"""Logging callback handler."""

import json
import time
from typing import Any, Dict, Optional
from uuid import UUID

from semantic_layer.monitoring.callbacks import BaseQueryCallback
from semantic_layer.monitoring.logging import QueryLogger
from semantic_layer.query.query import Query


class LoggingCallbackHandler(BaseQueryCallback):
    """Callback handler that logs queries using QueryLogger.
    
    This handler wraps the existing QueryLogger to provide
    callback-based logging while maintaining backward compatibility.
    """

    def __init__(self, query_logger: Optional[QueryLogger] = None, enabled: bool = True):
        """Initialize logging callback handler.
        
        Args:
            query_logger: Optional QueryLogger instance (creates new one if not provided)
            enabled: Whether logging is enabled
        """
        self.query_logger = query_logger or QueryLogger(enabled=enabled)
        self._run_id_to_query: Dict[str, Query] = {}
        self._run_id_to_user_id: Dict[str, Optional[str]] = {}

    def on_query_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Store query information for later logging."""
        # Store metadata for use in on_query_end
        if metadata:
            self._run_id_to_user_id[str(run_id)] = metadata.get("user_id")

    def on_query_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Log successful query execution."""
        # Extract query from outputs if available
        query = kwargs.get("query")
        if query is None:
            # Try to reconstruct from outputs metadata
            meta = outputs.get("meta", {})
            # We can't fully reconstruct Query from outputs, so skip detailed logging
            return

        execution_time_ms = outputs.get("meta", {}).get("execution_time_ms", 0)
        cache_hit = outputs.get("meta", {}).get("cache_hit", False)
        sql = outputs.get("meta", {}).get("sql")
        user_id = self._run_id_to_user_id.pop(str(run_id), None)

        self.query_logger.log_query(
            query=query,
            execution_time_ms=execution_time_ms,
            cache_hit=cache_hit,
            error=None,
            user_id=user_id,
            sql=sql,
        )

    def on_query_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Log query error."""
        query = kwargs.get("query")
        if query is None:
            return

        execution_time_ms = kwargs.get("execution_time_ms", 0)
        user_id = self._run_id_to_user_id.pop(str(run_id), None)

        self.query_logger.log_query(
            query=query,
            execution_time_ms=execution_time_ms,
            cache_hit=False,
            error=str(error),
            user_id=user_id,
            sql=None,
        )

    def get_logs(self, limit: int = 100):
        """Get recent logs from the underlying QueryLogger."""
        return self.query_logger.get_logs(limit=limit)

    def clear_logs(self):
        """Clear all logs from the underlying QueryLogger."""
        self.query_logger.clear_logs()

