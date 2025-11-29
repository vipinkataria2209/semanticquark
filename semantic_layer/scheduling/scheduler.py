"""Pre-aggregation scheduler for background jobs."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from semantic_layer.drivers.base_driver import BaseDriver as BaseConnector
from semantic_layer.models.schema import Schema
from semantic_layer.pre_aggregations.manager import PreAggregationManager
from semantic_layer.pre_aggregations.storage import DatabasePreAggregation


class PreAggregationScheduler:
    """Schedules pre-aggregation refreshes."""

    def __init__(
        self,
        manager: PreAggregationManager,
        connector: BaseConnector,
    ):
        """Initialize scheduler."""
        self.manager = manager
        self.connector = connector
        self._running = False
        self._tasks: Dict[str, asyncio.Task] = {}

    async def start(self) -> None:
        """Start the scheduler."""
        self._running = True
        # Schedule all registered pre-aggregations
        for name, definition in self.manager._definitions.items():
            await self._schedule_pre_aggregation(definition)

    async def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False
        # Cancel all tasks
        for task in self._tasks.values():
            task.cancel()
        await asyncio.gather(*self._tasks.values(), return_exceptions=True)
        self._tasks.clear()

    async def _schedule_pre_aggregation(self, definition) -> None:
        """Schedule a pre-aggregation refresh."""
        refresh_key = definition.refresh_key or {}
        every = refresh_key.get("every")
        
        if not every:
            return
        
        # Parse refresh interval (e.g., "1 hour", "30 minutes")
        interval_seconds = self._parse_interval(every)
        if not interval_seconds:
            return
        
        async def refresh_loop():
            while self._running:
                try:
                    await self.manager.refresh_pre_aggregation(definition)
                    print(f"Refreshed pre-aggregation: {definition.name}")
                except Exception as e:
                    print(f"Error refreshing pre-aggregation {definition.name}: {e}")
                
                await asyncio.sleep(interval_seconds)
        
        task = asyncio.create_task(refresh_loop())
        self._tasks[definition.name] = task

    def _parse_interval(self, interval_str: str) -> Optional[int]:
        """Parse interval string to seconds."""
        interval_str = interval_str.lower().strip()
        
        if "second" in interval_str or "sec" in interval_str:
            num = int(interval_str.split()[0])
            return num
        elif "minute" in interval_str or "min" in interval_str:
            num = int(interval_str.split()[0])
            return num * 60
        elif "hour" in interval_str or "hr" in interval_str:
            num = int(interval_str.split()[0])
            return num * 3600
        elif "day" in interval_str:
            num = int(interval_str.split()[0])
            return num * 86400
        else:
            return None

    async def refresh_now(self, name: str) -> None:
        """Manually refresh a pre-aggregation."""
        if name not in self.manager._definitions:
            raise ValueError(f"Pre-aggregation '{name}' not found")
        
        definition = self.manager._definitions[name]
        await self.manager.refresh_pre_aggregation(definition)

