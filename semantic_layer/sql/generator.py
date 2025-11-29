"""Main SQL generator - entry point for SQL generation."""

from typing import Optional

from semantic_layer.auth.base import SecurityContext
from semantic_layer.schema.types import Schema
from semantic_layer.query.query import Query
from semantic_layer.sql.builder import SQLBuilder
from semantic_layer.sql.optimizer import QueryOptimizer


class SQLGenerator:
    """Main SQL generator - orchestrates SQL generation."""
    
    def __init__(self, schema: Schema):
        """Initialize SQL generator with schema."""
        self.schema = schema
        self.builder = SQLBuilder(schema)
        self.optimizer = QueryOptimizer()
    
    def generate(
        self, 
        query: Query, 
        security_context: Optional[SecurityContext] = None,
        optimize: bool = True
    ) -> str:
        """Generate SQL from semantic query."""
        # Optimize query if requested
        if optimize:
            query = self.optimizer.optimize(query)
        
        # Build SQL
        sql = self.builder.build(query, security_context)
        
        return sql

