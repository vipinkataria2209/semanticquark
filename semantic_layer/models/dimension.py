"""Dimension model definition."""

from typing import Any, Dict, Literal, Optional

from pydantic import Field

from semantic_layer.models.base import BaseModelDefinition


class Dimension(BaseModelDefinition):
    """Represents a dimension in a cube."""

    type: Literal["string", "number", "time", "boolean"] = Field(
        default="string", description="Data type of the dimension"
    )
    sql: Optional[str] = Field(None, description="SQL expression for the dimension")
    primary_key: bool = Field(default=False, description="Whether this is a primary key")
    format: Optional[str] = Field(None, description="Format string for display")
    granularities: Optional[list[str]] = Field(
        None, description="Available time granularities (second, minute, hour, day, week, month, quarter, year)"
    )
    # Calculated dimension support
    expression: Optional[str] = Field(None, description="SQL expression for calculated dimension")
    sub_query: Optional[Dict[str, Any]] = Field(None, description="Sub-query for complex calculated dimensions")

    def get_sql_expression(self, table_alias: str = "", granularity: Optional[str] = None) -> str:
        """Get SQL expression for this dimension with optional granularity."""
        # Use expression if provided (calculated dimension)
        if self.expression:
            base_sql = self.expression
            # Replace {CUBE} placeholder with table alias
            base_sql = base_sql.replace("{CUBE}", table_alias if table_alias else "")
        elif self.sql:
            base_sql = self.sql
            if table_alias and "." not in base_sql:
                base_sql = f"{table_alias}.{base_sql}"
        else:
            base_sql = f"{table_alias}.{self.name}" if table_alias else self.name
        
        # Apply time granularity if this is a time dimension
        if self.type == "time" and granularity:
            return self._apply_time_granularity(base_sql, granularity)
        
        return base_sql

    def _apply_time_granularity(self, sql_expr: str, granularity: str) -> str:
        """Apply time granularity to SQL expression."""
        granularity = granularity.lower()
        
        # PostgreSQL date_trunc function
        if granularity == "second":
            return f"DATE_TRUNC('second', {sql_expr})"
        elif granularity == "minute":
            return f"DATE_TRUNC('minute', {sql_expr})"
        elif granularity == "hour":
            return f"DATE_TRUNC('hour', {sql_expr})"
        elif granularity == "day":
            return f"DATE_TRUNC('day', {sql_expr})"
        elif granularity == "week":
            return f"DATE_TRUNC('week', {sql_expr})"
        elif granularity == "month":
            return f"DATE_TRUNC('month', {sql_expr})"
        elif granularity == "quarter":
            return f"DATE_TRUNC('quarter', {sql_expr})"
        elif granularity == "year":
            return f"DATE_TRUNC('year', {sql_expr})"
        else:
            # Default to day if granularity not recognized
            return f"DATE_TRUNC('day', {sql_expr})"

