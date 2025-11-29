"""Cache key generation for queries."""

import hashlib
import json
from typing import Any, Dict, Optional

from semantic_layer.query.query import Query


class CacheKeyGenerator:
    """Generates cache keys from queries."""

    @staticmethod
    def generate(query: Query, user_context: Optional[Dict[str, Any]] = None, model_version: str = "1.0") -> str:
        """Generate cache key from query."""
        # Create a dictionary representation of the query
        query_dict = {
            "dimensions": sorted(query.dimensions),
            "measures": sorted(query.measures),
            "filters": [
                {
                    "dimension": f.dimension,
                    "operator": f.operator,
                    "values": sorted(f.values) if f.values else []
                }
                for f in sorted(query.filters, key=lambda x: x.dimension)
            ],
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

