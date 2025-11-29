"""Distributed tracing utilities."""

from typing import Dict, Any, Optional
import uuid
from datetime import datetime


class TraceContext:
    """Trace context for distributed tracing."""
    
    def __init__(self, trace_id: Optional[str] = None, span_id: Optional[str] = None):
        """Initialize trace context."""
        self.trace_id = trace_id or str(uuid.uuid4())
        self.span_id = span_id or str(uuid.uuid4())
        self.start_time = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "start_time": self.start_time.isoformat(),
        }


class Tracer:
    """Distributed tracing."""
    
    @staticmethod
    def start_trace(operation: str) -> TraceContext:
        """Start a new trace."""
        return TraceContext()
    
    @staticmethod
    def end_trace(context: TraceContext, metadata: Optional[Dict[str, Any]] = None):
        """End a trace."""
        end_time = datetime.utcnow()
        duration = (end_time - context.start_time).total_seconds()
        
        trace_data = {
            **context.to_dict(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "metadata": metadata or {},
        }
        
        # In production, would send to tracing backend (Jaeger, Zipkin, etc.)
        return trace_data

