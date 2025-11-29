"""Query representation."""

from typing import Any, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class QueryFilter(BaseModel):
    """Represents a filter in a query."""

    dimension: str = Field(..., description="Dimension to filter on (e.g., 'orders.status')")
    operator: str = Field(..., description="Filter operator (equals, not_equals, contains, etc.)")
    values: List[Union[str, int, float]] = Field(default_factory=list, description="Filter values")
    
    @field_validator('values', mode='before')
    @classmethod
    def validate_values(cls, v: Any) -> List[Union[str, int, float]]:
        """Convert values to appropriate types."""
        if not isinstance(v, list):
            return [v]
        return v

    def to_sql_condition(self, dimension_sql: str, dimension_type: Optional[str] = None) -> str:
        """Convert filter to SQL WHERE condition."""
        # Helper to format value based on type
        def format_value(val: Union[str, int, float], dim_type: Optional[str] = None) -> tuple[str, bool]:
            """Format value for SQL based on its type.
            Returns (formatted_value, needs_cast) tuple.
            """
            # If dimension is number type, cast value to number
            if dim_type == "number":
                if isinstance(val, (int, float)):
                    return (str(val), False)
                else:
                    # Try to convert string to number
                    try:
                        num_val = float(val) if '.' in str(val) else int(val)
                        return (str(num_val), False)
                    except (ValueError, TypeError):
                        # If conversion fails, treat as string
                        escaped = str(val).replace("'", "''")
                        return (f"'{escaped}'", False)
            elif isinstance(val, (int, float)):
                # Numeric value - check if dimension needs casting
                if dim_type == "string":
                    # Dimension is string but value is numeric - need to cast
                    return (str(val), True)
                return (str(val), False)
            else:
                # Escape single quotes in string values to prevent SQL injection
                escaped = str(val).replace("'", "''")
                return (f"'{escaped}'", False)
        
        # Helper to escape string values
        def escape_value(val: str) -> str:
            return val.replace("'", "''")
        
        if self.operator == "equals":
            if len(self.values) == 1:
                val, needs_cast = format_value(self.values[0], dimension_type)
                dim_expr = f"CAST({dimension_sql} AS NUMERIC)" if needs_cast else dimension_sql
                return f"{dim_expr} = {val}"
            else:
                # For IN, check if any value needs casting
                formatted_values = [format_value(v, dimension_type) for v in self.values]
                needs_cast = any(cast for _, cast in formatted_values)
                dim_expr = f"CAST({dimension_sql} AS NUMERIC)" if needs_cast else dimension_sql
                values_str = ", ".join(val for val, _ in formatted_values)
                return f"{dim_expr} IN ({values_str})"
        elif self.operator == "not_equals":
            if len(self.values) == 1:
                val, needs_cast = format_value(self.values[0], dimension_type)
                dim_expr = f"CAST({dimension_sql} AS NUMERIC)" if needs_cast else dimension_sql
                return f"{dim_expr} != {val}"
            else:
                formatted_values = [format_value(v, dimension_type) for v in self.values]
                needs_cast = any(cast for _, cast in formatted_values)
                dim_expr = f"CAST({dimension_sql} AS NUMERIC)" if needs_cast else dimension_sql
                values_str = ", ".join(val for val, _ in formatted_values)
                return f"{dim_expr} NOT IN ({values_str})"
        elif self.operator == "in":
            formatted_values = [format_value(v, dimension_type) for v in self.values]
            needs_cast = any(cast for _, cast in formatted_values)
            dim_expr = f"CAST({dimension_sql} AS NUMERIC)" if needs_cast else dimension_sql
            values_str = ", ".join(val for val, _ in formatted_values)
            return f"{dim_expr} IN ({values_str})"
        elif self.operator == "not_in":
            formatted_values = [format_value(v, dimension_type) for v in self.values]
            needs_cast = any(cast for _, cast in formatted_values)
            dim_expr = f"CAST({dimension_sql} AS NUMERIC)" if needs_cast else dimension_sql
            values_str = ", ".join(val for val, _ in formatted_values)
            return f"{dim_expr} NOT IN ({values_str})"
        elif self.operator == "contains":
            val_str = escape_value(str(self.values[0]))
            return f"{dimension_sql} LIKE '%{val_str}%'"
        elif self.operator == "not_contains":
            val_str = escape_value(str(self.values[0]))
            return f"{dimension_sql} NOT LIKE '%{val_str}%'"
        elif self.operator == "starts_with" or self.operator == "startsWith":
            val_str = escape_value(str(self.values[0]))
            return f"{dimension_sql} LIKE '{val_str}%'"
        elif self.operator == "ends_with" or self.operator == "endsWith":
            val_str = escape_value(str(self.values[0]))
            return f"{dimension_sql} LIKE '%{val_str}'"
        elif self.operator == "set" or self.operator == "is_null":
            return f"{dimension_sql} IS NULL"
        elif self.operator == "not_set" or self.operator == "is_not_null":
            return f"{dimension_sql} IS NOT NULL"
        elif self.operator == "gt" or self.operator == "greater_than":
            val, needs_cast = format_value(self.values[0], dimension_type)
            # For comparison operators with numeric values, always cast dimension to be safe
            if isinstance(self.values[0], (int, float)):
                dim_expr = f"CAST({dimension_sql} AS NUMERIC)"
            else:
                dim_expr = dimension_sql
            return f"{dim_expr} > {val}"
        elif self.operator == "gte" or self.operator == "greater_than_or_equal":
            val, needs_cast = format_value(self.values[0], dimension_type)
            if isinstance(self.values[0], (int, float)):
                dim_expr = f"CAST({dimension_sql} AS NUMERIC)"
            else:
                dim_expr = dimension_sql
            return f"{dim_expr} >= {val}"
        elif self.operator == "lt" or self.operator == "less_than":
            val, needs_cast = format_value(self.values[0], dimension_type)
            if isinstance(self.values[0], (int, float)):
                dim_expr = f"CAST({dimension_sql} AS NUMERIC)"
            else:
                dim_expr = dimension_sql
            return f"{dim_expr} < {val}"
        elif self.operator == "lte" or self.operator == "less_than_or_equal":
            val, needs_cast = format_value(self.values[0], dimension_type)
            if isinstance(self.values[0], (int, float)):
                dim_expr = f"CAST({dimension_sql} AS NUMERIC)"
            else:
                dim_expr = dimension_sql
            return f"{dim_expr} <= {val}"
        elif self.operator == "before_date" or self.operator == "beforeDate":
            val_str = escape_value(str(self.values[0]))
            return f"{dimension_sql} < '{val_str}'"
        elif self.operator == "after_date" or self.operator == "afterDate":
            val_str = escape_value(str(self.values[0]))
            return f"{dimension_sql} > '{val_str}'"
        elif self.operator == "in_date_range" or self.operator == "inDateRange":
            if len(self.values) >= 2:
                val1 = escape_value(str(self.values[0]))
                val2 = escape_value(str(self.values[1]))
                return f"{dimension_sql} >= '{val1}' AND {dimension_sql} <= '{val2}'"
            else:
                raise ValueError("in_date_range requires at least 2 values")
        else:
            raise ValueError(f"Unsupported operator: {self.operator}")


class QueryOrderBy(BaseModel):
    """Represents ordering in a query."""

    dimension: str = Field(..., description="Dimension to order by")
    direction: str = Field(default="asc", description="Order direction (asc or desc)")


class Query(BaseModel):
    """Represents a semantic query."""

    dimensions: List[str] = Field(default_factory=list, description="Dimensions to group by")
    measures: List[str] = Field(default_factory=list, description="Measures to aggregate")
    filters: List[QueryFilter] = Field(default_factory=list, description="Filters to apply")
    order_by: List[QueryOrderBy] = Field(default_factory=list, description="Ordering")
    limit: Optional[int] = Field(None, description="Limit number of results")
    offset: Optional[int] = Field(None, description="Offset for pagination")

    def validate(self) -> None:
        """Validate the query."""
        if not self.dimensions and not self.measures:
            raise ValueError("Query must have at least one dimension or measure")

