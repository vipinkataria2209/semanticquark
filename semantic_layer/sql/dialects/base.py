"""Base SQL dialect interface."""

from abc import ABC, abstractmethod
from typing import Optional


class BaseDialect(ABC):
    """Base class for SQL dialects."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get dialect name."""
        pass
    
    @abstractmethod
    def quote_identifier(self, identifier: str) -> str:
        """Quote an identifier (table/column name)."""
        pass
    
    @abstractmethod
    def quote_string(self, value: str) -> str:
        """Quote a string value."""
        pass
    
    @abstractmethod
    def date_trunc(self, field: str, granularity: str) -> str:
        """Generate DATE_TRUNC expression."""
        pass
    
    @abstractmethod
    def limit_clause(self, limit: int, offset: Optional[int] = None) -> str:
        """Generate LIMIT clause."""
        pass

