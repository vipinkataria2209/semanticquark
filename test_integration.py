"""Integration test with mock data for scenarios"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from semantic_layer.engine.query_engine import QueryEngine
from semantic_layer.models.cube import Cube
from semantic_layer.models.dimension import Dimension
from semantic_layer.models.measure import Measure
from semantic_layer.models.schema import Schema
from semantic_layer.query.query import Query, QueryFilter


async def test_integration():
    """Test integration with mock connector."""
    print("=" * 60)
    print("Integration Test - Mock Database")
    print("=" * 60)

    # Create a test schema
    print("\n1. Creating test schema...")
    schema = Schema()

    # Create test cube
    orders_cube = Cube(
        name="orders",
        table="orders",
        dimensions={
            "status": Dimension(name="status", type="string", sql="status"),
            "created_at": Dimension(name="created_at", type="time", sql="created_at"),
        },
        measures={
            "count": Measure(name="count", type="count", sql="id"),
            "total_revenue": Measure(name="total_revenue", type="sum", sql="total_amount"),
        },
    )
    schema.add_cube(orders_cube)
    print(f"   ✓ Schema created with cube: {orders_cube.name}")

    # Create mock connector
    print("\n2. Creating mock database connector...")
    mock_connector = MagicMock()
    mock_connector.execute_query = AsyncMock(
        return_value=[
            {"status": "completed", "created_at": "2024-01-01", "count": 10, "total_revenue": 1000.0},
            {"status": "pending", "created_at": "2024-01-01", "count": 5, "total_revenue": 500.0},
        ]
    )
    print("   ✓ Mock connector created")

    # Create query engine
    print("\n3. Creating query engine...")
    engine = QueryEngine(schema, mock_connector)
    print("   ✓ Query engine created")

    # Create and execute query
    print("\n4. Executing query...")
    query = Query(
        dimensions=["orders.status", "orders.created_at"],
        measures=["orders.count", "orders.total_revenue"],
        filters=[
            QueryFilter(dimension="orders.status", operator="equals", values=["completed", "pending"])
        ],
    )

    try:
        result = await engine.execute(query)
        print("   ✓ Query executed successfully")
        print(f"\n   Results:")
        print(f"   - Rows returned: {result['meta']['row_count']}")
        print(f"   - Execution time: {result['meta']['execution_time_ms']}ms")
        print(f"   - Data sample:")
        for row in result["data"][:2]:
            print(f"     {row}")
    except Exception as e:
        print(f"   ✗ Query execution failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "=" * 60)
    print("✓ Integration test passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_integration())

