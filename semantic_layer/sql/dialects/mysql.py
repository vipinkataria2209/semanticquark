"""MySQL SQL dialect."""

from typing import Optional

from semantic_layer.sql.dialects.base import BaseDialect


class MySQLDialect(BaseDialect):
    """MySQL SQL dialect."""
    
    @property
    def name(self) -> str:
        return "mysql"
    
    def quote_identifier(self, identifier: str) -> str:
        """Quote MySQL identifier."""
        return f"`{identifier}`"
    
    def quote_string(self, value: str) -> str:
        """Quote MySQL string."""
        escaped_value = value.replace("'", "''")
        return f"'{escaped_value}'"
    
    def date_trunc(self, field: str, granularity: str) -> str:
        """Generate MySQL DATE_TRUNC expression."""
        # MySQL uses DATE_FORMAT instead of DATE_TRUNC
        format_map = {
            "second": "%Y-%m-%d %H:%i:%s",
            "minute": "%Y-%m-%d %H:%i:00",
            "hour": "%Y-%m-%d %H:00:00",
            "day": "%Y-%m-%d",
            "week": "%Y-%u",
            "month": "%Y-%m",
            "quarter": "%Y-Q%q",
            "year": "%Y",
        }
        format_str = format_map.get(granularity, "%Y-%m-%d")
        return f"DATE_FORMAT({field}, '{format_str}')"
    
    def limit_clause(self, limit: int, offset: Optional[int] = None) -> str:
        """Generate MySQL LIMIT clause."""
        if offset:
            return f"LIMIT {offset}, {limit}"
        return f"LIMIT {limit}"

