"""Callback manager for handling multiple callback handlers."""

from typing import Any, List, Optional
from uuid import UUID, uuid4

from semantic_layer.monitoring.callbacks import BaseQueryCallback


class CallbackManager:
    """Manages multiple callback handlers.
    
    This class coordinates the execution of multiple callback handlers,
    allowing users to chain together different monitoring solutions.
    """

    def __init__(self, callbacks: Optional[List[BaseQueryCallback]] = None):
        """Initialize callback manager.
        
        Args:
            callbacks: List of callback handlers to manage
        """
        self.callbacks: List[BaseQueryCallback] = callbacks or []

    def add_callback(self, callback: BaseQueryCallback) -> None:
        """Add a callback handler.
        
        Args:
            callback: The callback handler to add
        """
        self.callbacks.append(callback)

    def remove_callback(self, callback: BaseQueryCallback) -> None:
        """Remove a callback handler.
        
        Args:
            callback: The callback handler to remove
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def clear_callbacks(self) -> None:
        """Clear all callback handlers."""
        self.callbacks.clear()

    async def on_query_start(
        self,
        serialized: dict,
        inputs: dict,
        *,
        run_id: Optional[UUID] = None,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
        **kwargs: Any,
    ) -> UUID:
        """Fire on_query_start on all callbacks.
        
        Args:
            serialized: Serialized representation of the query
            inputs: Input parameters
            run_id: Optional run ID (will generate if not provided)
            parent_run_id: Optional parent run ID
            tags: Optional tags
            metadata: Optional metadata
            
        Returns:
            The run_id used for this query
        """
        if run_id is None:
            run_id = uuid4()

        for callback in self.callbacks:
            if not callback.ignore_queries:
                try:
                    callback.on_query_start(
                        serialized=serialized,
                        inputs=inputs,
                        run_id=run_id,
                        parent_run_id=parent_run_id,
                        tags=tags,
                        metadata=metadata,
                        **kwargs,
                    )
                except Exception as e:
                    if callback.raise_error:
                        raise
                    # Log error but continue with other callbacks
                    import logging
                    logging.warning(f"Callback {callback.__class__.__name__} failed: {e}")

        return run_id

    async def on_query_end(
        self,
        outputs: dict,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Fire on_query_end on all callbacks.
        
        Args:
            outputs: Query results and metadata
            run_id: Unique identifier for this query run
            parent_run_id: Optional parent run ID
        """
        for callback in self.callbacks:
            if not callback.ignore_queries:
                try:
                    callback.on_query_end(
                        outputs=outputs,
                        run_id=run_id,
                        parent_run_id=parent_run_id,
                        **kwargs,
                    )
                except Exception as e:
                    if callback.raise_error:
                        raise
                    import logging
                    logging.warning(f"Callback {callback.__class__.__name__} failed: {e}")

    async def on_query_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Fire on_query_error on all callbacks.
        
        Args:
            error: The exception that occurred
            run_id: Unique identifier for this query run
            parent_run_id: Optional parent run ID
        """
        for callback in self.callbacks:
            if not callback.ignore_errors:
                try:
                    callback.on_query_error(
                        error=error,
                        run_id=run_id,
                        parent_run_id=parent_run_id,
                        **kwargs,
                    )
                except Exception as e:
                    if callback.raise_error:
                        raise
                    import logging
                    logging.warning(f"Callback {callback.__class__.__name__} failed: {e}")

    async def on_cache_hit(
        self,
        cache_key: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Fire on_cache_hit on all callbacks.
        
        Args:
            cache_key: The cache key that was hit
            run_id: Unique identifier for this query run
            parent_run_id: Optional parent run ID
        """
        for callback in self.callbacks:
            if not callback.ignore_cache:
                try:
                    callback.on_cache_hit(
                        cache_key=cache_key,
                        run_id=run_id,
                        parent_run_id=parent_run_id,
                        **kwargs,
                    )
                except Exception as e:
                    if callback.raise_error:
                        raise
                    import logging
                    logging.warning(f"Callback {callback.__class__.__name__} failed: {e}")

    async def on_cache_miss(
        self,
        cache_key: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Fire on_cache_miss on all callbacks.
        
        Args:
            cache_key: The cache key that was missed
            run_id: Unique identifier for this query run
            parent_run_id: Optional parent run ID
        """
        for callback in self.callbacks:
            if not callback.ignore_cache:
                try:
                    callback.on_cache_miss(
                        cache_key=cache_key,
                        run_id=run_id,
                        parent_run_id=parent_run_id,
                        **kwargs,
                    )
                except Exception as e:
                    if callback.raise_error:
                        raise
                    import logging
                    logging.warning(f"Callback {callback.__class__.__name__} failed: {e}")

    async def on_pre_agg_used(
        self,
        pre_agg_name: str,
        dimensions: list[str],
        measures: list[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Fire on_pre_agg_used on all callbacks.
        
        Args:
            pre_agg_name: Name of the pre-aggregation
            dimensions: Dimensions used
            measures: Measures used
            run_id: Unique identifier for this query run
            parent_run_id: Optional parent run ID
        """
        for callback in self.callbacks:
            if not callback.ignore_pre_agg:
                try:
                    callback.on_pre_agg_used(
                        pre_agg_name=pre_agg_name,
                        dimensions=dimensions,
                        measures=measures,
                        run_id=run_id,
                        parent_run_id=parent_run_id,
                        **kwargs,
                    )
                except Exception as e:
                    if callback.raise_error:
                        raise
                    import logging
                    logging.warning(f"Callback {callback.__class__.__name__} failed: {e}")

    async def on_pre_agg_skipped(
        self,
        reason: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Fire on_pre_agg_skipped on all callbacks.
        
        Args:
            reason: Reason why pre-aggregation was skipped
            run_id: Unique identifier for this query run
            parent_run_id: Optional parent run ID
        """
        for callback in self.callbacks:
            if not callback.ignore_pre_agg:
                try:
                    callback.on_pre_agg_skipped(
                        reason=reason,
                        run_id=run_id,
                        parent_run_id=parent_run_id,
                        **kwargs,
                    )
                except Exception as e:
                    if callback.raise_error:
                        raise
                    import logging
                    logging.warning(f"Callback {callback.__class__.__name__} failed: {e}")

    async def on_sql_generated(
        self,
        sql: str,
        execution_time_ms: float,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Fire on_sql_generated on all callbacks.
        
        Args:
            sql: The generated SQL query
            execution_time_ms: Time taken to execute
            run_id: Unique identifier for this query run
            parent_run_id: Optional parent run ID
        """
        for callback in self.callbacks:
            if not callback.ignore_sql:
                try:
                    callback.on_sql_generated(
                        sql=sql,
                        execution_time_ms=execution_time_ms,
                        run_id=run_id,
                        parent_run_id=parent_run_id,
                        **kwargs,
                    )
                except Exception as e:
                    if callback.raise_error:
                        raise
                    import logging
                    logging.warning(f"Callback {callback.__class__.__name__} failed: {e}")

    async def on_custom_event(
        self,
        name: str,
        data: dict,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        metadata: Optional[dict] = None,
        **kwargs: Any,
    ) -> None:
        """Fire on_custom_event on all callbacks.
        
        Args:
            name: Name of the custom event
            data: Event data dictionary
            run_id: Unique identifier for this query run
            parent_run_id: Optional parent run ID
            metadata: Optional metadata dictionary
        """
        for callback in self.callbacks:
            try:
                callback.on_custom_event(
                    name=name,
                    data=data,
                    run_id=run_id,
                    parent_run_id=parent_run_id,
                    metadata=metadata,
                    **kwargs,
                )
            except Exception as e:
                if callback.raise_error:
                    raise
                import logging
                logging.warning(f"Callback {callback.__class__.__name__} failed: {e}")

