"""Schema loader and manager."""

import os
from pathlib import Path
from typing import Dict, Optional

import yaml

from semantic_layer.config import get_settings
from semantic_layer.exceptions import ModelError
from semantic_layer.models.cube import Cube


class Schema:
    """Manages a collection of cubes."""

    def __init__(self, cubes: Optional[Dict[str, Cube]] = None):
        """Initialize schema with cubes."""
        self.cubes: Dict[str, Cube] = cubes or {}

    def add_cube(self, cube: Cube) -> None:
        """Add a cube to the schema."""
        if cube.name in self.cubes:
            raise ModelError(f"Cube '{cube.name}' already exists in schema")
        cube.validate()
        self.cubes[cube.name] = cube

    def get_cube(self, name: str) -> Cube:
        """Get a cube by name."""
        if name not in self.cubes:
            raise ModelError(f"Cube '{name}' not found in schema")
        return self.cubes[name]

    def get_cube_for_dimension(self, dimension_path: str) -> tuple[Cube, str]:
        """Get cube and dimension name from dimension path (e.g., 'orders.status')."""
        parts = dimension_path.split(".", 1)
        if len(parts) != 2:
            raise ModelError(f"Invalid dimension path: {dimension_path}. Expected format: 'cube.dimension'")

        cube_name, dimension_name = parts
        cube = self.get_cube(cube_name)
        return cube, dimension_name

    def get_cube_for_measure(self, measure_path: str) -> tuple[Cube, str]:
        """Get cube and measure name from measure path (e.g., 'orders.total')."""
        parts = measure_path.split(".", 1)
        if len(parts) != 2:
            raise ModelError(f"Invalid measure path: {measure_path}. Expected format: 'cube.measure'")

        cube_name, measure_name = parts
        cube = self.get_cube(cube_name)
        return cube, measure_name


class SchemaLoader:
    """Loads schema definitions from YAML files."""

    @staticmethod
    def load_from_file(file_path: str | Path) -> Schema:
        """Load schema from a YAML file."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise ModelError(f"Schema file not found: {file_path}")

        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        return SchemaLoader.load_from_dict(data)

    @staticmethod
    def load_from_dict(data: dict) -> Schema:
        """Load schema from a dictionary."""
        schema = Schema()
        cubes_data = data.get("cubes", [])

        for cube_data in cubes_data:
            cube = SchemaLoader._parse_cube(cube_data)
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
    def _parse_cube(data: dict) -> Cube:
        """Parse a cube from dictionary data."""
        from semantic_layer.models.dimension import Dimension
        from semantic_layer.models.measure import Measure
        from semantic_layer.models.relationship import Relationship

        # Parse dimensions
        dimensions = {}
        for dim_name, dim_data in data.get("dimensions", {}).items():
            if isinstance(dim_data, str):
                dimensions[dim_name] = Dimension(name=dim_name, sql=dim_data)
            else:
                dimensions[dim_name] = Dimension(name=dim_name, **dim_data)

        # Parse measures
        measures = {}
        for meas_name, meas_data in data.get("measures", {}).items():
            if isinstance(meas_data, str):
                measures[meas_name] = Measure(name=meas_name, sql=meas_data)
            else:
                measures[meas_name] = Measure(name=meas_name, **meas_data)

        # Parse relationships
        relationships = {}
        for rel_name, rel_data in data.get("relationships", {}).items():
            relationships[rel_name] = Relationship(name=rel_name, **rel_data)

        return Cube(
            name=data["name"],
            table=data.get("table", ""),
            dimensions=dimensions,
            measures=measures,
            relationships=relationships,
            description=data.get("description"),
            sql=data.get("sql"),
            security=data.get("security"),
            pre_aggregations=data.get("pre_aggregations", []),
            meta=data.get("meta", {}),
        )

