"""Schema parser - parses YAML/JSON cube definitions."""

from pathlib import Path
from typing import Dict

import yaml

from semantic_layer.exceptions import ModelError
from semantic_layer.models.cube import Cube
from semantic_layer.models.dimension import Dimension
from semantic_layer.models.measure import Measure
from semantic_layer.models.relationship import Relationship


class SchemaParser:
    """Parses schema definitions from YAML/JSON files."""
    
    @staticmethod
    def parse_file(file_path: str | Path) -> Dict:
        """Parse a YAML file into a dictionary."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise ModelError(f"Schema file not found: {file_path}")
        
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
        
        return data
    
    @staticmethod
    def parse_cube(data: dict) -> Cube:
        """Parse a cube from dictionary data."""
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

