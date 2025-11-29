"""Metrics collection for monitoring."""

import time
from collections import defaultdict
from typing import Dict, List

try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    Counter = None
    Histogram = None
    Gauge = None


class MetricsCollector:
    """Collects metrics for monitoring."""

    def __init__(self, enabled: bool = True):
        """Initialize metrics collector."""
        self.enabled = enabled
        self._query_count = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._error_count = 0
        self._query_times: List[float] = []
        
        if PROMETHEUS_AVAILABLE and enabled:
            self.query_counter = Counter(
                "semanticquark_queries_total",
                "Total number of queries",
                ["status"]
            )
            self.query_duration = Histogram(
                "semanticquark_query_duration_seconds",
                "Query execution duration",
                buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
            )
            self.cache_hit_counter = Counter(
                "semanticquark_cache_hits_total",
                "Total cache hits"
            )
            self.cache_miss_counter = Counter(
                "semanticquark_cache_misses_total",
                "Total cache misses"
            )
            self.error_counter = Counter(
                "semanticquark_errors_total",
                "Total errors",
                ["error_type"]
            )
        else:
            self.query_counter = None
            self.query_duration = None
            self.cache_hit_counter = None
            self.cache_miss_counter = None
            self.error_counter = None

    def record_query(self, execution_time_ms: float, cache_hit: bool = False, error: bool = False) -> None:
        """Record a query execution."""
        if not self.enabled:
            return
        
        self._query_count += 1
        execution_time_s = execution_time_ms / 1000.0
        self._query_times.append(execution_time_s)
        
        # Keep only last 1000 query times
        if len(self._query_times) > 1000:
            self._query_times = self._query_times[-1000:]
        
        if cache_hit:
            self._cache_hits += 1
            if self.cache_hit_counter:
                self.cache_hit_counter.inc()
        else:
            self._cache_misses += 1
            if self.cache_miss_counter:
                self.cache_miss_counter.inc()
        
        if error:
            self._error_count += 1
            if self.error_counter:
                self.error_counter.labels(error_type="execution").inc()
        
        if self.query_counter:
            status = "error" if error else "success"
            self.query_counter.labels(status=status).inc()
        
        if self.query_duration:
            self.query_duration.observe(execution_time_s)

    def get_stats(self) -> Dict[str, any]:
        """Get current statistics."""
        cache_hit_rate = 0.0
        if self._query_count > 0:
            cache_hit_rate = (self._cache_hits / self._query_count) * 100
        
        avg_time = 0.0
        p95_time = 0.0
        p99_time = 0.0
        if self._query_times:
            sorted_times = sorted(self._query_times)
            avg_time = sum(sorted_times) / len(sorted_times)
            p95_idx = int(len(sorted_times) * 0.95)
            p99_idx = int(len(sorted_times) * 0.99)
            p95_time = sorted_times[p95_idx] if p95_idx < len(sorted_times) else sorted_times[-1]
            p99_time = sorted_times[p99_idx] if p99_idx < len(sorted_times) else sorted_times[-1]
        
        return {
            "total_queries": self._query_count,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": cache_hit_rate,
            "errors": self._error_count,
            "avg_execution_time_ms": avg_time * 1000,
            "p95_execution_time_ms": p95_time * 1000,
            "p99_execution_time_ms": p99_time * 1000,
        }

