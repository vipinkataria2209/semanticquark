"""PostgreSQL SQL dialect."""

from typing import Optional

from semantic_layer.sql.dialects.base import BaseDialect


class PostgresDialect(BaseDialect):
    """PostgreSQL SQL dialect."""
    
    @property
    def name(self) -> str:
        return "postgresql"
    
    def quote_identifier(self, identifier: str) -> str:
        """Quote PostgreSQL identifier."""
        return f'"{identifier}"'
    
    def quote_string(self, value: str) -> str:
        """Quote PostgreSQL string."""
        escaped_value = value.replace("'", "''")
        return f"'{escaped_value}'"
    
    def date_trunc(self, field: str, granularity: str) -> str:
        """Generate PostgreSQL DATE_TRUNC expression."""
        return f"DATE_TRUNC('{granularity}', {field})"
    
    def limit_clause(self, limit: int, offset: Optional[int] = None) -> str:
        """Generate PostgreSQL LIMIT clause."""
        if offset:
            return f"LIMIT {limit} OFFSET {offset}"
        return f"LIMIT {limit}"

