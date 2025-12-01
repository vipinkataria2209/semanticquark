"""Base callback handler for SemanticQuark queries."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from uuid import UUID
import uuid


class BaseQueryCallback(ABC):
    """Base callback handler for SemanticQuark queries.
    
    This class provides a flexible, extensible interface for monitoring
    query execution. Subclasses can implement specific callback methods
    to track different aspects of query processing.
    
    Inspired by LangChain's callback handler pattern for maximum extensibility.
    """

    raise_error: bool = False
    """Whether to raise errors if callback execution fails."""

    # Filtering properties
    @property
    def ignore_queries(self) -> bool:
        """Whether to ignore query callbacks."""
        return False

    @property
    def ignore_cache(self) -> bool:
        """Whether to ignore cache callbacks."""
        return False

    @property
    def ignore_pre_agg(self) -> bool:
        """Whether to ignore pre-aggregation callbacks."""
        return False

    @property
    def ignore_errors(self) -> bool:
        """Whether to ignore error callbacks."""
        return False

    @property
    def ignore_sql(self) -> bool:
        """Whether to ignore SQL generation callbacks."""
        return False

    # Query Events
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
        """Called when query execution starts.
        
        Args:
            serialized: Serialized representation of the query
            inputs: Input parameters (dimensions, measures, filters, etc.)
            run_id: Unique identifier for this query run
            parent_run_id: Parent run ID if this is a nested query
            tags: Optional tags for categorization
            metadata: Optional metadata dictionary
        """
        pass

    def on_query_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when query execution completes successfully.
        
        Args:
            outputs: Query results and metadata
            run_id: Unique identifier for this query run
            parent_run_id: Parent run ID if this is a nested query
        """
        pass

    def on_query_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when query execution fails.
        
        Args:
            error: The exception that occurred
            run_id: Unique identifier for this query run
            parent_run_id: Parent run ID if this is a nested query
        """
        pass

    # Cache Events
    def on_cache_hit(
        self,
        cache_key: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when cache hit occurs.
        
        Args:
            cache_key: The cache key that was hit
            run_id: Unique identifier for this query run
            parent_run_id: Parent run ID if this is a nested query
        """
        pass

    def on_cache_miss(
        self,
        cache_key: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when cache miss occurs.
        
        Args:
            cache_key: The cache key that was missed
            run_id: Unique identifier for this query run
            parent_run_id: Parent run ID if this is a nested query
        """
        pass

    # Pre-aggregation Events
    def on_pre_agg_used(
        self,
        pre_agg_name: str,
        dimensions: list[str],
        measures: list[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when pre-aggregation is used.
        
        Args:
            pre_agg_name: Name of the pre-aggregation
            dimensions: Dimensions used in the pre-aggregation
            measures: Measures used in the pre-aggregation
            run_id: Unique identifier for this query run
            parent_run_id: Parent run ID if this is a nested query
        """
        pass

    def on_pre_agg_skipped(
        self,
        reason: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when pre-aggregation is skipped.
        
        Args:
            reason: Reason why pre-aggregation was skipped
            run_id: Unique identifier for this query run
            parent_run_id: Parent run ID if this is a nested query
        """
        pass

    # SQL Events
    def on_sql_generated(
        self,
        sql: str,
        execution_time_ms: float,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when SQL is generated and executed.
        
        Args:
            sql: The generated SQL query
            execution_time_ms: Time taken to execute the SQL
            run_id: Unique identifier for this query run
            parent_run_id: Parent run ID if this is a nested query
        """
        pass

    # Custom Events
    def on_custom_event(
        self,
        name: str,
        data: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Called for custom events.
        
        Args:
            name: Name of the custom event
            data: Event data dictionary
            run_id: Unique identifier for this query run
            parent_run_id: Parent run ID if this is a nested query
            metadata: Optional metadata dictionary
        """
        pass

