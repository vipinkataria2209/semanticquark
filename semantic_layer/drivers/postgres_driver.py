"""PostgreSQL connector."""

from typing import Any, Dict, List, Optional

import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from typing import Optional, Dict, Any
from semantic_layer.drivers.base_driver import BaseDriver, ConnectionConfig
from semantic_layer.exceptions import ExecutionError


class PostgresDriver(BaseDriver):
    """PostgreSQL database driver."""
    
    @property
    def name(self) -> str:
        """Plugin name."""
        return "postgres"
    
    @property
    def version(self) -> str:
        """Plugin version."""
        return "1.0.0"
    
    @property
    def dialect(self) -> str:
        """Get SQL dialect name."""
        return "postgresql"

    def __init__(self, config: Optional[ConnectionConfig] = None):
        """Initialize PostgreSQL connector.
        
        Args:
            config: Connection configuration (optional for plugin initialization)
        """
        super().__init__(config)
        self.engine = None
        self.session_factory = None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize driver from config dict (PluginInterface method).
        
        Args:
            config: Configuration dictionary
        """
        super().initialize(config)
        self.engine = None
        self.session_factory = None

    async def connect(self) -> None:
        """Establish PostgreSQL connection."""
        try:
            self.engine = create_async_engine(
                self.config.url,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                echo=False,
            )
            self.session_factory = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )
        except Exception as e:
            raise ExecutionError(f"Failed to connect to PostgreSQL: {str(e)}") from e

    async def disconnect(self) -> None:
        """Close PostgreSQL connection."""
        if self.engine:
            try:
                await self.engine.dispose()
            except Exception as e:
                # Log error but don't raise - cleanup should be best-effort
                # This can happen if greenlet is not installed or during shutdown
                print(f"Warning: Error disposing engine: {str(e)}")
            finally:
                self.engine = None
                self.session_factory = None

    async def execute_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results."""
        if not self.engine:
            await self.connect()

        try:
            # Use asyncpg directly for better performance
            conn = await asyncpg.connect(self.config.url.replace("+asyncpg", "").replace("postgresql://", "postgresql://"))
            try:
                rows = await conn.fetch(sql)
                # Convert rows to list of dicts
                results = [dict(row) for row in rows]
                return results
            finally:
                await conn.close()
        except Exception as e:
            raise ExecutionError(f"Query execution failed: {str(e)}", details={"sql": sql}) from e

    async def test_connection(self) -> bool:
        """Test if connection is working."""
        try:
            result = await self.execute_query("SELECT 1 as test")
            return len(result) > 0
        except Exception:
            return False

