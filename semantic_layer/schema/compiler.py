"""Schema compiler - compiles schema definitions to internal representation."""

from typing import Dict

from semantic_layer.models.schema import Schema
from semantic_layer.models.cube import Cube
from semantic_layer.schema.validator import SchemaValidator


class SchemaCompiler:
    """Compiles schema definitions to optimized internal representation."""
    
    @staticmethod
    def compile(schema: Schema) -> Schema:
        """Compile a schema, resolving relationships and optimizing."""
        # Validate schema first
        errors = SchemaValidator.validate_schema(schema)
        if errors:
            raise ValueError(f"Schema validation failed: {', '.join(errors)}")
        
        # Resolve relationships
        SchemaCompiler._resolve_relationships(schema)
        
        # Optimize schema (could add caching, indexing, etc.)
        SchemaCompiler._optimize(schema)
        
        return schema
    
    @staticmethod
    def _resolve_relationships(schema: Schema) -> None:
        """Resolve and validate all relationships in the schema."""
        for cube in schema.cubes.values():
            for relationship in cube.relationships.values():
                # Verify target cube exists
                if relationship.cube not in schema.cubes:
                    raise ValueError(
                        f"Relationship '{relationship.name}' in cube '{cube.name}' "
                        f"references non-existent cube '{relationship.cube}'"
                    )
    
    @staticmethod
    def _optimize(schema: Schema) -> None:
        """Optimize schema for faster lookups."""
        # Could add indexes, caches, etc.
        pass

