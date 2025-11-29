"""Result formatter for query results."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List

from semantic_layer.query.query import Query


class ResultFormatter:
    """Formats query results for API responses."""

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        """Serialize value to JSON-compatible type."""
        if isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, bytes):
            return value.decode('utf-8', errors='ignore')
        return value

    @staticmethod
    def format(
        results: List[Dict[str, Any]], query: Query, execution_time_ms: float
    ) -> Dict[str, Any]:
        """Format query results into API response format."""
        # Normalize column names (remove table aliases)
        normalized_results = []
        for row in results:
            normalized_row = {}
            for key, value in row.items():
                # Convert snake_case to original format if needed
                normalized_key = key
                # Serialize value to JSON-compatible type
                normalized_row[normalized_key] = ResultFormatter._serialize_value(value)
            normalized_results.append(normalized_row)

        return {
            "data": normalized_results,
            "meta": {
                "query": {
                    "dimensions": query.dimensions,
                    "measures": query.measures,
                    "filters": [f.dict() for f in query.filters],
                },
                "execution_time_ms": round(execution_time_ms, 2),
                "row_count": len(normalized_results),
            },
        }

