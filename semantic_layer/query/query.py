"""Query representation."""

from typing import Any, List, Optional, Union, TYPE_CHECKING

from pydantic import BaseModel, Field, field_validator, field_serializer, model_validator

# Forward reference will be resolved after LogicalFilter is defined


class LogicalFilter(BaseModel):
    """Represents a logical filter (AND/OR) containing other filters."""
    
    or_: Optional[List[Any]] = Field(
        None, alias="or", description="OR logical operator - array of filters"
    )
    and_: Optional[List[Any]] = Field(
        None, alias="and", description="AND logical operator - array of filters"
    )
    
    @model_validator(mode='after')
    def validate_logical(self):
        """Validate that exactly one of 'or' or 'and' is provided."""
        if not self.or_ and not self.and_:
            raise ValueError("Logical filter must have either 'or' or 'and' property")
        if self.or_ and self.and_:
            raise ValueError("Logical filter cannot have both 'or' and 'and' properties")
        return self
    
    def to_sql_condition(self, schema, cube_aliases, is_measure_filter: bool = False) -> str:
        """Convert logical filter to SQL WHERE or HAVING condition.
        
        Args:
            schema: Schema object
            cube_aliases: Dictionary mapping cube names to table aliases
            is_measure_filter: If True, treat filters as measure filters (for HAVING clause)
        """
        if self.or_:
            conditions = []
            for filter_item in self.or_:
                if isinstance(filter_item, LogicalFilter):
                    conditions.append(f"({filter_item.to_sql_condition(schema, cube_aliases, is_measure_filter)})")
                else:
                    # QueryFilter
                    member_name = filter_item.dimension or filter_item.member
                    if is_measure_filter:
                        # For measure filters, get measure SQL
                        cube, meas_name = schema.get_cube_for_measure(member_name)
                        measure = cube.get_measure(meas_name)
                        table_alias = cube_aliases[cube.name]
                        member_sql = measure.get_sql_expression(table_alias)
                        condition = filter_item.to_sql_condition(member_sql, dimension_type="number")
                    else:
                        # For dimension filters, get dimension SQL
                        cube, dim_name = schema.get_cube_for_dimension(member_name)
                        dimension = cube.get_dimension(dim_name)
                        table_alias = cube_aliases[cube.name]
                        member_sql = dimension.get_sql_expression(table_alias)
                        condition = filter_item.to_sql_condition(member_sql, dimension_type=dimension.type)
                    conditions.append(condition)
            return " OR ".join(conditions)
        elif self.and_:
            conditions = []
            for filter_item in self.and_:
                if isinstance(filter_item, LogicalFilter):
                    conditions.append(f"({filter_item.to_sql_condition(schema, cube_aliases, is_measure_filter)})")
                else:
                    # QueryFilter
                    member_name = filter_item.dimension or filter_item.member
                    if is_measure_filter:
                        # For measure filters, get measure SQL
                        cube, meas_name = schema.get_cube_for_measure(member_name)
                        measure = cube.get_measure(meas_name)
                        table_alias = cube_aliases[cube.name]
                        member_sql = measure.get_sql_expression(table_alias)
                        condition = filter_item.to_sql_condition(member_sql, dimension_type="number")
                    else:
                        # For dimension filters, get dimension SQL
                        cube, dim_name = schema.get_cube_for_dimension(member_name)
                        dimension = cube.get_dimension(dim_name)
                        table_alias = cube_aliases[cube.name]
                        member_sql = dimension.get_sql_expression(table_alias)
                        condition = filter_item.to_sql_condition(member_sql, dimension_type=dimension.type)
                    conditions.append(condition)
            return " AND ".join(conditions)
        else:
            raise ValueError("Logical filter must have either 'or' or 'and' property")


class QueryFilter(BaseModel):
    """Represents a filter in a query."""

    dimension: Optional[str] = Field(None, description="Dimension to filter on (e.g., 'orders.status')")
    member: Optional[str] = Field(None, description="Member to filter on (alias for dimension)")
    operator: str = Field(..., description="Filter operator (equals, not_equals, contains, etc.)")
    values: List[Union[str, int, float]] = Field(default_factory=list, description="Filter values")
    
    @field_validator('values', mode='before')
    @classmethod
    def validate_values(cls, v: Any) -> List[Union[str, int, float]]:
        """Convert values to appropriate types."""
        if not isinstance(v, list):
            return [v]
        return v
    
    @model_validator(mode='after')
    def validate_dimension_or_member(self):
        """Validate that either dimension or member is provided."""
        if not self.dimension and not self.member:
            raise ValueError("Filter must have either 'dimension' or 'member' property")
        # Use dimension if member is provided (for compatibility)
        if self.member and not self.dimension:
            self.dimension = self.member
        return self

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


class QueryTimeDimension(BaseModel):
    """Represents a time dimension in a query."""

    dimension: str = Field(..., description="Time dimension (e.g., 'orders.created_at')")
    granularity: Optional[str] = Field(None, description="Time granularity (day, month, year, etc.)")
    date_range: Optional[List[str]] = Field(None, description="Date range [start, end]")
    compare_date_range: Optional[List[List[str]]] = Field(
        None, 
        description="Compare date ranges [[start1, end1], [start2, end2], ...]"
    )

    def model_copy(self, **kwargs):
        """Create a copy of the model with updated fields."""
        return super().model_copy(**kwargs)
    
    def _parse_date_range(self, date_range: Union[str, List[str]]) -> List[str]:
        """Parse date range - handles both absolute and relative dates."""
        from semantic_layer.utils.date_parser import parse_relative_date
        
        if isinstance(date_range, str):
            # Relative date like "last week"
            return parse_relative_date(date_range)
        elif isinstance(date_range, list):
            # Check if any element is a relative date string
            parsed = []
            for item in date_range:
                if isinstance(item, str) and not item[0].isdigit():
                    # Might be relative date
                    try:
                        parsed_dates = parse_relative_date(item)
                        parsed.extend(parsed_dates)
                    except ValueError:
                        # Not a relative date, use as-is
                        parsed.append(item)
                else:
                    parsed.append(item)
            return parsed
        return date_range


class Query(BaseModel):
    """Represents a semantic query."""

    dimensions: List[str] = Field(default_factory=list, description="Dimensions to group by")
    measures: List[str] = Field(default_factory=list, description="Measures to aggregate")
    filters: List[Union[QueryFilter, LogicalFilter]] = Field(
        default_factory=list, 
        description="Dimension filters to apply in WHERE clause (can include logical operators)"
    )
    measure_filters: List[Union[QueryFilter, LogicalFilter]] = Field(
        default_factory=list,
        description="Measure filters to apply in HAVING clause (can include logical operators)"
    )
    time_dimensions: List[QueryTimeDimension] = Field(
        default_factory=list, 
        description="Time dimensions with granularity and date ranges"
    )
    order_by: List[QueryOrderBy] = Field(default_factory=list, description="Ordering")
    limit: Optional[int] = Field(None, description="Limit number of results")
    offset: Optional[int] = Field(None, description="Offset for pagination")
    ctes: List[dict[str, str]] = Field(
        default_factory=list,
        description="Common Table Expressions (CTEs) - [{'alias': str, 'query': str}]"
    )

    def validate(self) -> None:
        """Validate the query."""
        if not self.dimensions and not self.measures and not any(
            td.granularity for td in self.time_dimensions
        ):
            raise ValueError("Query must have at least one dimension, measure, or time dimension with granularity")
        
        # Validate that compare_date_range is only in one time dimension
        compare_date_range_count = sum(
            1 for td in self.time_dimensions if td.compare_date_range is not None
        )
        if compare_date_range_count > 1:
            raise ValueError("compareDateRange can only exist for one timeDimension")

