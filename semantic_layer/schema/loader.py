"""Schema loader - loads schema definitions from files."""

from pathlib import Path
from typing import Dict, Optional

from semantic_layer.config import get_settings
from semantic_layer.exceptions import ModelError
from semantic_layer.schema.parser import SchemaParser
from semantic_layer.models.schema import Schema
from semantic_layer.models.cube import Cube
from semantic_layer.schema.validator import SchemaValidator


class SchemaLoader:
    """Loads schema definitions from YAML files."""
    
    @staticmethod
    def load_from_file(file_path: str | Path) -> Schema:
        """Load schema from a YAML file."""
        data = SchemaParser.parse_file(file_path)
        return SchemaLoader.load_from_dict(data)
    
    @staticmethod
    def load_from_dict(data: dict) -> Schema:
        """Load schema from a dictionary."""
        schema = Schema()
        cubes_data = data.get("cubes", [])
        
        for cube_data in cubes_data:
            cube = SchemaParser.parse_cube(cube_data)
            schema.add_cube(cube)
        
        return schema
    
    @staticmethod
    def load_from_directory(directory: str | Path) -> Schema:
        """Load all schema files from a directory."""
        directory = Path(directory)
        if not directory.exists():
            raise ModelError(f"Schema directory not found: {directory}")
        
        schema = Schema()
        yaml_files = list(directory.glob("*.yaml")) + list(directory.glob("*.yml"))
        
        for yaml_file in yaml_files:
            file_schema = SchemaLoader.load_from_file(yaml_file)
            for cube in file_schema.cubes.values():
                schema.add_cube(cube)
        
        return schema
    
    @staticmethod
    def load_default() -> Schema:
        """Load schema from default models directory."""
        settings = get_settings()
        models_path = Path(settings.models_path)
        return SchemaLoader.load_from_directory(models_path)
    
    @staticmethod
    def validate_and_load(file_path: str | Path) -> Schema:
        """Load and validate a schema file."""
        schema = SchemaLoader.load_from_file(file_path)
        errors = SchemaValidator.validate_schema(schema)
        if errors:
            raise ModelError(f"Schema validation failed: {', '.join(errors)}")
        return schema

