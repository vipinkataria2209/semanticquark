"""Job definitions for scheduling."""

from typing import Any, Dict, Callable, Optional
from datetime import datetime
from enum import Enum


class JobStatus(Enum):
    """Job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job:
    """Represents a scheduled job."""
    
    def __init__(
        self,
        name: str,
        func: Callable,
        schedule: str,
        args: Optional[tuple] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ):
        """Initialize job."""
        self.name = name
        self.func = func
        self.schedule = schedule  # Cron expression or interval
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.status = JobStatus.PENDING
        self.last_run: Optional[datetime] = None
        self.next_run: Optional[datetime] = None
        self.error: Optional[str] = None
    
    async def execute(self):
        """Execute the job."""
        self.status = JobStatus.RUNNING
        self.last_run = datetime.utcnow()
        try:
            if asyncio.iscoroutinefunction(self.func):
                result = await self.func(*self.args, **self.kwargs)
            else:
                result = self.func(*self.args, **self.kwargs)
            self.status = JobStatus.COMPLETED
            return result
        except Exception as e:
            self.status = JobStatus.FAILED
            self.error = str(e)
            raise


import asyncio

