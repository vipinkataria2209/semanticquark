"""Base driver interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from semantic_layer.plugins.base import PluginInterface


class ConnectionConfig(BaseModel):
    """Database connection configuration."""

    url: str
    pool_size: int = 10
    max_overflow: int = 20


class BaseDriver(PluginInterface, ABC):
    """Base class for database drivers."""
    
    @property
    def plugin_type(self) -> str:
        """Plugin type identifier."""
        return "driver"
    
    def __init__(self, config: Optional[ConnectionConfig] = None):
        """Initialize connector with configuration.
        
        Args:
            config: Connection configuration (optional for plugin initialization)
        """
        if config is not None:
            self.config = config
        else:
            self.config = None
        self._pool = None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize driver from config dict (PluginInterface method).
        
        Args:
            config: Configuration dictionary
        """
        self.config = ConnectionConfig(**config)
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Return configuration schema for this driver.
        
        Returns:
            Dict[str, Any]: Configuration schema
        """
        return {
            "url": {
                "type": "string",
                "description": "Database connection URL",
                "required": True
            },
            "pool_size": {
                "type": "integer",
                "description": "Connection pool size",
                "default": 10
            },
            "max_overflow": {
                "type": "integer",
                "description": "Maximum pool overflow",
                "default": 20
            }
        }

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

