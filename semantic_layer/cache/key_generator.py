"""Cache key generation for queries."""

import hashlib
import json
from typing import Any, Dict, Optional

from semantic_layer.query.query import Query, LogicalFilter, QueryFilter


class CacheKeyGenerator:
    """Generates cache keys from queries."""

    @staticmethod
    def _serialize_filter(filter_obj) -> Dict[str, Any]:
        """Serialize a filter (handles both QueryFilter and LogicalFilter)."""
        if isinstance(filter_obj, LogicalFilter):
            if filter_obj.or_:
                return {"or": [CacheKeyGenerator._serialize_filter(f) for f in filter_obj.or_]}
            elif filter_obj.and_:
                return {"and": [CacheKeyGenerator._serialize_filter(f) for f in filter_obj.and_]}
            return {}
        elif isinstance(filter_obj, QueryFilter):
            return {
                "dimension": filter_obj.dimension or filter_obj.member,
                "operator": filter_obj.operator,
                "values": sorted(filter_obj.values) if filter_obj.values else []
            }
        return {"unknown": str(type(filter_obj))}

    @staticmethod
    def generate(query: Query, user_context: Optional[Dict[str, Any]] = None, model_version: str = "1.0") -> str:
        """Generate cache key from query."""
        # Create a dictionary representation of the query
        query_dict = {
            "dimensions": sorted(query.dimensions),
            "measures": sorted(query.measures),
            "filters": [CacheKeyGenerator._serialize_filter(f) for f in query.filters],
            "measure_filters": [CacheKeyGenerator._serialize_filter(f) for f in query.measure_filters],
            "order_by": [
                {"dimension": o.dimension, "direction": o.direction}
                for o in query.order_by
            ],
            "limit": query.limit,
            "offset": query.offset,
            "user_context": user_context or {},
            "model_version": model_version,
        }
        
        # Create hash from query dictionary
        query_json = json.dumps(query_dict, sort_keys=True)
        query_hash = hashlib.sha256(query_json.encode()).hexdigest()[:16]
        
        return f"query:{query_hash}"

