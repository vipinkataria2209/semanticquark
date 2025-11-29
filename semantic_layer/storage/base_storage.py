"""Base storage interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseStorage(ABC):
    """Base interface for storage backends."""
    
    @abstractmethod
    async def store(self, key: str, data: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Store data."""
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete data."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if data exists."""
        pass

