"""Query execution metrics."""

import time
from typing import Any, Dict, Optional


class QueryMetrics:
    """Tracks query execution metrics."""
    
    def __init__(self):
        """Initialize metrics."""
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.cache_hit: bool = False
        self.pre_aggregation_used: bool = False
        self.row_count: int = 0
        self.error: Optional[str] = None
    
    def start(self):
        """Start timing."""
        self.start_time = time.time()
    
    def end(self):
        """End timing."""
        self.end_time = time.time()
    
    @property
    def execution_time_ms(self) -> float:
        """Get execution time in milliseconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "execution_time_ms": self.execution_time_ms,
            "cache_hit": self.cache_hit,
            "pre_aggregation_used": self.pre_aggregation_used,
            "row_count": self.row_count,
            "error": self.error,
        }

