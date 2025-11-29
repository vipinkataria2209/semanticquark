"""Measure model definition."""

from typing import Literal, Optional

from pydantic import Field

from semantic_layer.models.base import BaseModelDefinition


class Measure(BaseModelDefinition):
    """Represents a measure in a cube."""

    type: Literal["number", "count", "sum", "avg", "min", "max", "countDistinct", "calculated"] = Field(
        default="number", description="Aggregation type"
    )
    sql: str = Field(..., description="SQL expression for the measure")
    format: Optional[str] = Field(None, description="Format string for display")
    # Calculated measure support
    expression: Optional[str] = Field(None, description="SQL expression for calculated measure")
    formula: Optional[str] = Field(None, description="Formula for calculated measure (e.g., 'orders.revenue / orders.count')")

    def get_sql_expression(self, table_alias: str = "") -> str:
        """Get SQL expression for this measure with aggregation."""
        # Use expression if provided (calculated measure)
        if self.expression:
            sql_expr = self.expression
            sql_expr = sql_expr.replace("{CUBE}", table_alias if table_alias else "")
        elif self.formula:
            # Formula-based calculated measure (e.g., "orders.revenue / orders.count")
            # This would need to be resolved at query time with actual measure references
            sql_expr = self.formula
        else:
            sql_expr = self.sql
            if table_alias and "." not in sql_expr:
                sql_expr = f"{table_alias}.{sql_expr}"

        if self.type == "count":
            return f"COUNT({sql_expr})"
        elif self.type == "countDistinct":
            return f"COUNT(DISTINCT {sql_expr})"
        elif self.type == "sum":
            return f"SUM({sql_expr})"
        elif self.type == "avg":
            return f"AVG({sql_expr})"
        elif self.type == "min":
            return f"MIN({sql_expr})"
        elif self.type == "max":
            return f"MAX({sql_expr})"
        elif self.type == "calculated":
            # For calculated measures, return the expression as-is (should already be aggregated)
            return sql_expr
        else:
            return sql_expr

