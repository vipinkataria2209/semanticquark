"""Schema validator - validates cube definitions."""

from typing import List

from semantic_layer.exceptions import ModelError
from semantic_layer.models.cube import Cube
from semantic_layer.models.schema import Schema


class SchemaValidator:
    """Validates schema definitions."""
    
    @staticmethod
    def validate_cube(cube: Cube) -> List[str]:
        """Validate a cube definition and return list of errors."""
        errors = []
        
        # Validate cube name
        if not cube.name:
            errors.append("Cube name is required")
        
        # Validate table
        if not cube.table:
            errors.append(f"Cube '{cube.name}' must have a table name")
        
        # Validate dimensions and measures
        if not cube.dimensions and not cube.measures:
            errors.append(f"Cube '{cube.name}' must have at least one dimension or measure")
        
        # Validate each dimension
        for dim_name, dimension in cube.dimensions.items():
            if not dimension.sql and not dimension.expression:
                errors.append(f"Dimension '{dim_name}' in cube '{cube.name}' must have sql or expression")
        
        # Validate each measure
        for meas_name, measure in cube.measures.items():
            if not measure.sql and not measure.expression and not measure.formula:
                errors.append(f"Measure '{meas_name}' in cube '{cube.name}' must have sql, expression, or formula")
        
        return errors
    
    @staticmethod
    def validate_schema(schema: Schema) -> List[str]:
        """Validate a complete schema and return list of errors."""
        errors = []
        
        # Validate each cube
        for cube_name, cube in schema.cubes.items():
            cube_errors = SchemaValidator.validate_cube(cube)
            errors.extend([f"Cube '{cube_name}': {err}" for err in cube_errors])
        
        # Validate relationships
        for cube_name, cube in schema.cubes.items():
            for rel_name, relationship in cube.relationships.items():
                target_cube = relationship.cube
                if target_cube not in schema.cubes:
                    errors.append(
                        f"Relationship '{rel_name}' in cube '{cube_name}' references "
                        f"non-existent cube '{target_cube}'"
                    )
        
        return errors

