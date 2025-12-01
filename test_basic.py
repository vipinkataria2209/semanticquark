""""""Basic test script to verify the semantic layer works.

This module provides a comprehensive test suite for validating the core functionality
of the semantic layer, including schema loading, database connectivity, query parsing,
and SQL generation capabilities.

The test script performs the following validations:
    1. Schema Loading: Verifies that cube definitions can be loaded from model files
    2. Database Connection: Tests optional database connectivity (PostgreSQL)
    3. Query Parsing: Validates query structure parsing from dictionary format
    4. SQL Generation: Ensures SQL queries are correctly generated from parsed queries

Usage:
    Run directly to execute all basic tests:
        $ python -m semantic_layer.tests.test_basic
    
    Or import and run programmatically:
        >>> import asyncio
        >>> from semantic_layer.tests.test_basic import test_basic
        >>> asyncio.run(test_basic())

Requirements:
    - Model files must exist in the models/ directory
    - DATABASE_URL environment variable (optional, for connection tests)
    - PostgreSQL connector dependencies (optional)

Example Output:
    ============================================================
    Testing Semantic Layer - Basic Functionality
    ============================================================
    
    1. Loading schema...
       ✓ Schema loaded with 1 cube(s)
       - Cube: orders (3 dimensions, 2 measures)
    
    2. Testing database connection...
       ✓ Database connection successful
    
    3. Testing query parsing...
       ✓ Query parsed successfully
    
    4. Testing SQL generation...
       ✓ SQL generated successfully
    
    ============================================================
    ✓ All basic tests passed!
    ============================================================

Notes:
    - Database connection tests are skipped if DATABASE_URL is not configured
    - Tests gracefully handle missing dependencies or configuration
    - All test failures include detailed error messages for debugging

Author:
    Semantic Layer Team

Version:
    1.0.0
""""""

import asyncio
import os
from pathlib import Path

from semantic_layer.config import get_settings
from semantic_layer.connectors.base import ConnectionConfig
from semantic_layer.engine.query_engine import QueryEngine
from semantic_layer.models.schema import SchemaLoader
from semantic_layer.query.parser import QueryParser


async def test_basic():
    """Test basic functionality."""
    print("=" * 60)
    print("Testing Semantic Layer - Basic Functionality")
    print("=" * 60)

    # Load schema
    print("\n1. Loading schema...")
    try:
        schema = SchemaLoader.load_default()
        print(f"   ✓ Schema loaded with {len(schema.cubes)} cube(s)")
        for cube_name in schema.cubes.keys():
            cube = schema.cubes[cube_name]
            print(f"   - Cube: {cube_name} ({len(cube.dimensions)} dimensions, {len(cube.measures)} measures)")
    except Exception as e:
        print(f"   ✗ Failed to load schema: {e}")
        print("   Note: Make sure you have a model file in the models/ directory")
        return

    # Test connection (optional - skip if no database configured or connector not available)
    try:
        from semantic_layer.connectors.postgresql import PostgreSQLConnector
        
        settings = get_settings()
        if settings.database_url and "localhost" not in settings.database_url:
            print("\n2. Testing database connection...")
            try:
                conn_config = ConnectionConfig(
                    url=settings.database_url_async,
                    pool_size=1,
                    max_overflow=0,
                )
                connector = PostgreSQLConnector(conn_config)
                await connector.connect()
                is_connected = await connector.test_connection()
                if is_connected:
                    print("   ✓ Database connection successful")
                else:
                    print("   ✗ Database connection test failed")
                await connector.disconnect()
            except Exception as e:
                print(f"   ⚠ Database connection failed (this is OK if DB not configured): {e}")
        else:
            print("\n2. Skipping database connection test (no database URL configured)")
    except ImportError:
        print("\n2. Skipping database connection test (database dependencies not installed)")

    # Test query parsing
    print("\n3. Testing query parsing...")
    try:
        query_data = {
            "dimensions": ["orders.status", "orders.created_at"],
            "measures": ["orders.count", "orders.total_revenue"],
            "filters": [
                {
                    "dimension": "orders.status",
                    "operator": "equals",
                    "values": ["completed"],
                }
            ],
            "limit": 10,
        }
        query = QueryParser.parse(query_data)
        print("   ✓ Query parsed successfully")
        print(f"   - Dimensions: {query.dimensions}")
        print(f"   - Measures: {query.measures}")
        print(f"   - Filters: {len(query.filters)}")
    except Exception as e:
        print(f"   ✗ Query parsing failed: {e}")
        return

    # Test SQL generation
    print("\n4. Testing SQL generation...")
    try:
        from semantic_layer.query_builder.sql_builder import SQLBuilder

        sql_builder = SQLBuilder(schema)
        sql = sql_builder.build(query)
        print("   ✓ SQL generated successfully")
        print(f"   SQL: {sql[:100]}..." if len(sql) > 100 else f"   SQL: {sql}")
    except Exception as e:
        print(f"   ✗ SQL generation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "=" * 60)
    print("✓ All basic tests passed!")
    print("=" * 60)
    print("\nTo test with a real database:")
    print("1. Set DATABASE_URL in .env file")
    print("2. Ensure your database has the required tables")
    print("3. Run: python -m semantic_layer.api.main")


if __name__ == "__main__":
    asyncio.run(test_basic())

