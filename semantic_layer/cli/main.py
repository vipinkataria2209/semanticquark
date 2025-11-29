"""Main CLI entry point."""

import click
from pathlib import Path

from semantic_layer.models.schema import SchemaLoader
from semantic_layer.exceptions import ModelError


@click.group()
def cli():
    """SemanticQuark CLI tools."""
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True))
def validate(path: str):
    """Validate semantic models."""
    try:
        path_obj = Path(path)
        if path_obj.is_file():
            schema = SchemaLoader.load_from_file(path_obj)
        else:
            schema = SchemaLoader.load_from_directory(path_obj)
        
        click.echo(f"✅ Valid schema: {len(schema.cubes)} cubes loaded")
        for cube_name, cube in schema.cubes.items():
            click.echo(f"  - {cube_name}: {len(cube.dimensions)} dimensions, {len(cube.measures)} measures")
    except ModelError as e:
        click.echo(f"❌ Validation error: {e}", err=True)
        exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable hot reload")
def dev(host: str, port: int, reload: bool):
    """Start development server."""
    import uvicorn
    from semantic_layer.api.app import create_app
    
    app = create_app()
    uvicorn.run(app, host=host, port=port, reload=reload)


@cli.command()
@click.argument("path", type=click.Path(exists=True))
def test(path: str):
    """Test semantic models with sample queries."""
    try:
        path_obj = Path(path)
        if path_obj.is_file():
            schema = SchemaLoader.load_from_file(path_obj)
        else:
            schema = SchemaLoader.load_from_directory(path_obj)
        
        click.echo(f"Testing schema with {len(schema.cubes)} cubes...")
        
        # Test each cube
        for cube_name, cube in schema.cubes.items():
            click.echo(f"\nTesting cube: {cube_name}")
            
            # Test dimension access
            for dim_name in cube.dimensions:
                try:
                    dim = cube.get_dimension(dim_name)
                    click.echo(f"  ✅ Dimension '{dim_name}': {dim.type}")
                except Exception as e:
                    click.echo(f"  ❌ Dimension '{dim_name}': {e}", err=True)
            
            # Test measure access
            for meas_name in cube.measures:
                try:
                    meas = cube.get_measure(meas_name)
                    click.echo(f"  ✅ Measure '{meas_name}': {meas.type}")
                except Exception as e:
                    click.echo(f"  ❌ Measure '{meas_name}': {e}", err=True)
        
        click.echo("\n✅ All tests passed!")
    except Exception as e:
        click.echo(f"❌ Test error: {e}", err=True)
        exit(1)


if __name__ == "__main__":
    cli()

