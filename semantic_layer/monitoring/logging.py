"""Query logging implementation."""

import json
import time
from typing import Any, Dict, Optional

from semantic_layer.query.query import Query, LogicalFilter, QueryFilter


class QueryLogger:
    """Logs queries for monitoring and debugging."""

    def __init__(self, enabled: bool = True):
        """Initialize query logger."""
        self.enabled = enabled
        self._logs: list[Dict[str, Any]] = []

    def log_query(
        self,
        query: Query,
        execution_time_ms: float,
        cache_hit: bool = False,
        error: Optional[str] = None,
        user_id: Optional[str] = None,
        sql: Optional[str] = None,
    ) -> None:
        """Log a query execution."""
        if not self.enabled:
            return

        log_entry = {
            "timestamp": time.time(),
            "query_id": self._generate_query_id(query),
            "user_id": user_id,
            "dimensions": query.dimensions,
            "measures": query.measures,
            "filters": [self._serialize_filter(f) for f in query.filters],
            "execution_time_ms": execution_time_ms,
            "cache_hit": cache_hit,
            "sql": sql,
            "status": "success" if not error else "error",
            "error": error,
        }

        self._logs.append(log_entry)
        self._print_log(log_entry)

    def _generate_query_id(self, query: Query) -> str:
        """Generate a unique ID for the query."""
        import hashlib
        query_str = json.dumps(
            {
                "dimensions": query.dimensions,
                "measures": query.measures,
                "filters": [self._serialize_filter(f) for f in query.filters],
            },
            sort_keys=True,
        )
        return hashlib.md5(query_str.encode()).hexdigest()[:8]

    def _serialize_filter(self, filter_obj) -> Dict[str, Any]:
        """Serialize a filter (handles both QueryFilter and LogicalFilter)."""
        if isinstance(filter_obj, LogicalFilter):
            if filter_obj.or_:
                return {"or": [self._serialize_filter(f) for f in filter_obj.or_]}
            elif filter_obj.and_:
                return {"and": [self._serialize_filter(f) for f in filter_obj.and_]}
        elif isinstance(filter_obj, QueryFilter):
            return {
                "dimension": filter_obj.dimension or filter_obj.member,
                "operator": filter_obj.operator,
                "values": filter_obj.values,
            }
        return {"unknown": str(type(filter_obj))}

    def _print_log(self, log_entry: Dict[str, Any]) -> None:
        """Print log entry (can be replaced with proper logging)."""
        print(json.dumps(log_entry, indent=2))

    def get_logs(self, limit: int = 100) -> list[Dict[str, Any]]:
        """Get recent logs."""
        return self._logs[-limit:]

    def clear_logs(self) -> None:
        """Clear all logs."""
        self._logs.clear()

