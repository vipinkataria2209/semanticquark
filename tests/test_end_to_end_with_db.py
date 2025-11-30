"""End-to-end integration tests that require actual database execution."""

import pytest
import asyncio
import os
from semantic_layer.query.parser import QueryParser
from semantic_layer.models.schema import Schema
from semantic_layer.models.cube import Cube
from semantic_layer.models.dimension import Dimension
from semantic_layer.models.measure import Measure
from semantic_layer.drivers.postgres_driver import PostgresDriver
from semantic_layer.drivers.base_driver import ConnectionConfig
from semantic_layer.orchestrator.orchestrator import QueryEngine
from semantic_layer.cache.memory import MemoryCache


@pytest.fixture(scope="module")
async def db_driver():
    """Create database connection for tests."""
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://semanticquark:semanticquark123@postgres:5432/semanticquark_db"
    )
    
    config = ConnectionConfig(
        url=database_url,
        pool_size=5,
        max_overflow=10
    )
    
    driver = PostgresDriver(config)
    await driver.connect()
    
    # Create test table if it doesn't exist
    try:
        await driver.execute_query("""
            CREATE TABLE IF NOT EXISTS orders (
                id VARCHAR(50) PRIMARY KEY,
                status VARCHAR(20) NOT NULL,
                created_at TIMESTAMP NOT NULL,
                customer_id VARCHAR(50) NOT NULL,
                total_amount DECIMAL(10, 2) NOT NULL
            )
        """)
        
        # Insert test data
        await driver.execute_query("""
            INSERT INTO orders (id, status, created_at, customer_id, total_amount) VALUES
                ('order_1', 'completed', '2024-01-15 10:00:00', 'customer_1', 100.50),
                ('order_2', 'completed', '2024-01-15 11:00:00', 'customer_1', 250.75),
                ('order_3', 'pending', '2024-01-15 12:00:00', 'customer_2', 75.25),
                ('order_4', 'completed', '2024-01-16 10:00:00', 'customer_2', 300.00),
                ('order_5', 'cancelled', '2024-01-16 11:00:00', 'customer_3', 50.00)
            ON CONFLICT (id) DO NOTHING
        """)
    except Exception as e:
        print(f"Note: Table may already exist: {e}")
    
    yield driver
    await driver.disconnect()


@pytest.fixture
def test_schema():
    """Create a test schema with orders cube."""
    orders_cube = Cube(
        name="orders",
        table="orders",
        dimensions=[
            Dimension(name="status", type="string", sql="status"),
            Dimension(name="created_at", type="time", sql="created_at"),
        ],
        measures=[
            Measure(name="revenue", type="sum", sql="total_amount"),
            Measure(name="count", type="count", sql="id"),
        ]
    )
    
    return Schema(cubes={"orders": orders_cube})


@pytest.mark.asyncio
async def test_logical_filter_execution(db_driver, test_schema):
    """Test that logical filters work in actual SQL execution."""
    cache = MemoryCache()
    engine = QueryEngine(
        schema=test_schema,
        connector=db_driver,
        cache=cache
    )
    
    query_data = {
        "measures": ["orders.revenue"],
        "filters": [
            {
                "or": [
                    {"member": "orders.status", "operator": "equals", "values": ["completed"]},
                    {"member": "orders.status", "operator": "equals", "values": ["pending"]}
                ]
            }
        ]
    }
    
    query = QueryParser.parse(query_data)
    result = await engine.execute(query)
    
    assert "data" in result
    assert "meta" in result
    assert "sql" in result["meta"]
    # SQL should contain OR
    assert "OR" in result["meta"]["sql"].upper() or "or" in result["meta"]["sql"]
    print(f"✅ Generated SQL: {result['meta']['sql']}")
    print(f"✅ Result rows: {len(result['data'])}")


@pytest.mark.asyncio
async def test_relative_date_execution(db_driver, test_schema):
    """Test that relative dates work in actual SQL execution."""
    cache = MemoryCache()
    engine = QueryEngine(
        schema=test_schema,
        connector=db_driver,
        cache=cache
    )
    
    query_data = {
        "measures": ["orders.revenue"],
        "timeDimensions": [
            {
                "dimension": "orders.created_at",
                "granularity": "day",
                "dateRange": "last 30 days"  # Relative date
            }
        ]
    }
    
    query = QueryParser.parse(query_data)
    
    # Verify relative date was parsed
    assert query.time_dimensions[0].date_range[0] != "last 30 days"
    assert len(query.time_dimensions[0].date_range) == 2
    
    result = await engine.execute(query)
    
    assert "data" in result
    assert "sql" in result["meta"]
    # SQL should contain date range
    assert "orders.created_at" in result["meta"]["sql"].lower()
    print(f"✅ Generated SQL: {result['meta']['sql']}")
    print(f"✅ Parsed date range: {query.time_dimensions[0].date_range}")


@pytest.mark.asyncio
async def test_compare_date_range_execution(db_driver, test_schema):
    """Test compare date range query execution."""
    cache = MemoryCache()
    engine = QueryEngine(
        schema=test_schema,
        connector=db_driver,
        cache=cache
    )
    
    query_data = {
        "measures": ["orders.revenue"],
        "timeDimensions": [
            {
                "dimension": "orders.created_at",
                "granularity": "day",
                "compareDateRange": [
                    ["2024-01-15", "2024-01-15"],  # Day 1
                    ["2024-01-16", "2024-01-16"]   # Day 2
                ]
            }
        ]
    }
    
    query = QueryParser.parse(query_data)
    
    # Should transform into 2 queries
    queries = engine._transform_compare_date_range(query)
    assert len(queries) == 2
    
    result = await engine.execute(query)
    
    assert "data" in result
    assert result["meta"].get("compare_date_range") == True
    # Should have results from both date ranges
    print(f"✅ Compare date range executed")
    print(f"✅ Result rows: {len(result['data'])}")
    print(f"✅ SQL: {result['meta']['sql']}")


@pytest.mark.asyncio
async def test_nested_logical_filter_execution(db_driver, test_schema):
    """Test nested logical filter (OR with AND) execution."""
    cache = MemoryCache()
    engine = QueryEngine(
        schema=test_schema,
        connector=db_driver,
        cache=cache
    )
    
    query_data = {
        "measures": ["orders.revenue"],
        "filters": [
            {
                "or": [
                    {"member": "orders.status", "operator": "equals", "values": ["completed"]},
                    {
                        "and": [
                            {"member": "orders.status", "operator": "equals", "values": ["pending"]},
                            {"member": "orders.revenue", "operator": "gt", "values": [50]}
                        ]
                    }
                ]
            }
        ]
    }
    
    query = QueryParser.parse(query_data)
    result = await engine.execute(query)
    
    assert "data" in result
    assert "sql" in result["meta"]
    sql = result["meta"]["sql"].upper()
    # Should have OR and AND
    assert "OR" in sql
    assert "AND" in sql
    print(f"✅ Nested logical filter SQL: {result['meta']['sql']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

