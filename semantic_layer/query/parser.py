"""Query parser for API requests."""

from typing import Any, Dict, List

from semantic_layer.exceptions import QueryError
from semantic_layer.query.query import Query, QueryFilter, QueryOrderBy, QueryTimeDimension, LogicalFilter
from semantic_layer.utils.date_parser import parse_relative_date


class QueryParser:
    """Parses API requests into Query objects."""

    @staticmethod
    def parse(request_data: Dict[str, Any]) -> Query:
        """Parse a request dictionary into a Query object."""
        try:
            # Parse dimensions
            dimensions = request_data.get("dimensions", [])

            # Parse measures
            measures = request_data.get("measures", [])

            # Parse time dimensions
            time_dimensions = []
            for td_data in request_data.get("timeDimensions", []):
                if isinstance(td_data, dict):
                    # Parse date range (can be string for relative dates)
                    date_range = td_data.get("dateRange")
                    if isinstance(date_range, str):
                        # Relative date like "last week"
                        date_range = parse_relative_date(date_range)
                    
                    # Parse compare date range
                    compare_date_range = td_data.get("compareDateRange")
                    if compare_date_range:
                        parsed_compare = []
                        for dr in compare_date_range:
                            if isinstance(dr, str):
                                parsed_compare.append(parse_relative_date(dr))
                            elif isinstance(dr, list):
                                # Check if any element is relative
                                parsed_dr = []
                                for item in dr:
                                    if isinstance(item, str) and not (item[0].isdigit() if item else False):
                                        try:
                                            parsed = parse_relative_date(item)
                                            parsed_dr.extend(parsed)
                                        except ValueError:
                                            parsed_dr.append(item)
                                    else:
                                        parsed_dr.append(item)
                                parsed_compare.append(parsed_dr)
                            else:
                                parsed_compare.append(dr)
                        compare_date_range = parsed_compare
                    
                    time_dimensions.append(
                        QueryTimeDimension(
                            dimension=td_data["dimension"],
                            granularity=td_data.get("granularity"),
                            date_range=date_range,
                            compare_date_range=compare_date_range,
                        )
                    )

            # Parse filters (supports logical operators)
            filters = QueryParser._parse_filters(request_data.get("filters", []))

            # Parse order by
            order_by = []
            for order_data in request_data.get("order_by", []):
                if isinstance(order_data, dict):
                    order_by.append(
                        QueryOrderBy(
                            dimension=order_data["dimension"],
                            direction=order_data.get("direction", "asc"),
                        )
                    )
                elif isinstance(order_data, str):
                    # Simple format: "dimension" or "dimension:desc"
                    parts = order_data.split(":")
                    order_by.append(
                        QueryOrderBy(
                            dimension=parts[0],
                            direction=parts[1] if len(parts) > 1 else "asc",
                        )
                    )

            # Parse limit and offset
            limit = request_data.get("limit")
            offset = request_data.get("offset")

            query = Query(
                dimensions=dimensions,
                measures=measures,
                filters=filters,
                time_dimensions=time_dimensions,
                order_by=order_by,
                limit=limit,
                offset=offset,
            )

            query.validate()
            return query

        except (KeyError, ValueError, TypeError) as e:
            raise QueryError(f"Invalid query format: {str(e)}", details={"request": request_data}) from e
    
    @staticmethod
    def _parse_filters(filter_list: List[Any]) -> List[Any]:
        """Parse filters, handling logical operators (AND/OR)."""
        filters = []
        for filter_data in filter_list:
            if isinstance(filter_data, dict):
                # Check if it's a logical operator
                if "or" in filter_data:
                    # OR logical operator
                    or_filters = QueryParser._parse_filters(filter_data["or"])
                    filters.append(LogicalFilter(**{"or": or_filters}))  # Use alias
                elif "and" in filter_data:
                    # AND logical operator
                    and_filters = QueryParser._parse_filters(filter_data["and"])
                    filters.append(LogicalFilter(**{"and": and_filters}))  # Use alias
                else:
                    # Regular filter
                    filters.append(
                        QueryFilter(
                            dimension=filter_data.get("dimension"),
                            member=filter_data.get("member"),  # Support 'member' alias
                            operator=filter_data.get("operator", "equals"),
                            values=filter_data.get("values", []),
                        )
                    )
        return filters

