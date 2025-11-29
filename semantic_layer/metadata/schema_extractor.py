"""Extract database schemas."""

from typing import Dict, List, Any
from semantic_layer.metadata.introspection import DatabaseIntrospector


class SchemaExtractor:
    """Extracts database schema information."""
    
    def __init__(self, introspector: DatabaseIntrospector):
        """Initialize schema extractor."""
        self.introspector = introspector
    
    async def extract_schema(self) -> Dict[str, Any]:
        """Extract complete database schema."""
        tables = await self.introspector.get_tables()
        
        schema = {
            "tables": {},
        }
        
        for table in tables:
            columns = await self.introspector.get_table_columns(table)
            foreign_keys = await self.introspector.get_foreign_keys(table)
            
            schema["tables"][table] = {
                "columns": columns,
                "foreign_keys": foreign_keys,
            }
        
        return schema

