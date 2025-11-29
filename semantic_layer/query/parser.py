"""Query parser for API requests."""

from typing import Any, Dict

from semantic_layer.exceptions import QueryError
from semantic_layer.query.query import Query, QueryFilter, QueryOrderBy


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

            # Parse filters
            filters = []
            for filter_data in request_data.get("filters", []):
                if isinstance(filter_data, dict):
                    filters.append(
                        QueryFilter(
                            dimension=filter_data["dimension"],
                            operator=filter_data.get("operator", "equals"),
                            values=filter_data.get("values", []),
                        )
                    )

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
                order_by=order_by,
                limit=limit,
                offset=offset,
            )

            query.validate()
            return query

        except (KeyError, ValueError, TypeError) as e:
            raise QueryError(f"Invalid query format: {str(e)}", details={"request": request_data}) from e

