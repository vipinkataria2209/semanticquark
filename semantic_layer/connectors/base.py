"""Base connector interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ConnectionConfig(BaseModel):
    """Database connection configuration."""

    url: str
    pool_size: int = 10
    max_overflow: int = 20


class BaseConnector(ABC):
    """Base class for database connectors."""

    def __init__(self, config: ConnectionConfig):
        """Initialize connector with configuration."""
        self.config = config
        self._pool = None

    @abstractmethod
    async def connect(self) -> None:
        """Establish database connection."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection."""
        pass

    @abstractmethod
    async def execute_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results."""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if connection is working."""
        pass

    @property
    @abstractmethod
    def dialect(self) -> str:
        """Get SQL dialect name."""
        pass

