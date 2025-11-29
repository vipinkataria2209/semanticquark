"""Background task runner."""

import asyncio
from typing import List
from semantic_layer.scheduling.jobs import Job


class BackgroundTaskRunner:
    """Runs background tasks."""
    
    def __init__(self):
        """Initialize task runner."""
        self.tasks: List[asyncio.Task] = []
        self.running = False
    
    async def start(self):
        """Start background task runner."""
        self.running = True
    
    async def stop(self):
        """Stop background task runner."""
        self.running = False
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
    
    async def run_job(self, job: Job):
        """Run a job in the background."""
        task = asyncio.create_task(job.execute())
        self.tasks.append(task)
        return task

