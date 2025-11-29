"""Live API testing script."""

import asyncio
import json
import time
from contextlib import asynccontextmanager

import httpx
from semantic_layer.api.app import create_app
from semantic_layer.config import get_settings
from semantic_layer.connectors.base import ConnectionConfig
from semantic_layer.engine.query_engine import QueryEngine
from semantic_layer.models.schema import Schema, SchemaLoader

# Create a mock connector for testing
from unittest.mock import AsyncMock, MagicMock


class MockConnector:
    """Mock database connector for testing."""

    async def connect(self):
        pass

    async def disconnect(self):
        pass

    async def execute_query(self, sql: str, params=None):
        # Return mock data based on SQL
        if "orders" in sql.lower():
            return [
                {
                    "orders_status": "completed",
                    "orders_created_at": "2024-01-01",
                    "orders_count": 10,
                    "orders_total_revenue": 1500.0,
                },
                {
                    "orders_status": "pending",
                    "orders_created_at": "2024-01-01",
                    "orders_count": 5,
                    "orders_total_revenue": 750.0,
                },
                {
                    "orders_status": "cancelled",
                    "orders_created_at": "2024-01-02",
                    "orders_count": 2,
                    "orders_total_revenue": 200.0,
                },
            ]
        return []

    async def test_connection(self):
        return True

    @property
    def dialect(self):
        return "mock"


async def setup_test_app():
    """Set up test application with mock connector."""
    # Load schema
    schema = SchemaLoader.load_default()

    # Create mock connector
    connector = MockConnector()
    await connector.connect()

    # Create query engine
    query_engine = QueryEngine(schema, connector)

    # Import and modify the global variables
    import semantic_layer.api.app as app_module
    
    # Set global state
    app_module.query_engine = query_engine
    app_module.schema = schema

    # Create app (will use the global state we just set)
    app = create_app()

    return app


async def test_api():
    """Test the API endpoints."""
    print("=" * 70)
    print("LIVE API TESTING")
    print("=" * 70)

    # Create test app
    print("\n1. Setting up test application...")
    app = await setup_test_app()
    print("   ✓ Test app created")

    # Start test server
    import uvicorn

    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="error")
    server = uvicorn.Server(config)

    # Start server in background
    print("\n2. Starting test server...")
    server_task = asyncio.create_task(server.serve())
    await asyncio.sleep(2)  # Wait for server to start
    print("   ✓ Server started on http://127.0.0.1:8000")

    # Test endpoints
    base_url = "http://127.0.0.1:8000"

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: Health check
        print("\n3. Testing /health endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"   Status: {response.status_code}")
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            assert response.status_code == 200
            print("   ✓ Health check passed")
        except Exception as e:
            print(f"   ✗ Health check failed: {e}")

        # Test 2: Schema endpoint
        print("\n4. Testing /api/v1/schema endpoint...")
        try:
            response = await client.get(f"{base_url}/api/v1/schema")
            print(f"   Status: {response.status_code}")
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            assert response.status_code == 200
            assert "cubes" in data
            print("   ✓ Schema endpoint passed")
        except Exception as e:
            print(f"   ✗ Schema endpoint failed: {e}")

        # Test 3: Simple query
        print("\n5. Testing /api/v1/query (simple query)...")
        try:
            query_data = {
                "dimensions": ["orders.status"],
                "measures": ["orders.count", "orders.total_revenue"],
            }
            response = await client.post(
                f"{base_url}/api/v1/query", json=query_data, timeout=10.0
            )
            print(f"   Status: {response.status_code}")
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            assert response.status_code == 200
            assert "data" in data
            assert "meta" in data
            print("   ✓ Simple query passed")
        except Exception as e:
            print(f"   ✗ Simple query failed: {e}")
            if hasattr(e, "response"):
                print(f"   Response: {e.response.text}")

        # Test 4: Query with filters
        print("\n6. Testing /api/v1/query (with filters)...")
        try:
            query_data = {
                "dimensions": ["orders.status", "orders.created_at"],
                "measures": ["orders.count"],
                "filters": [
                    {
                        "dimension": "orders.status",
                        "operator": "equals",
                        "values": ["completed"],
                    }
                ],
                "limit": 5,
            }
            response = await client.post(
                f"{base_url}/api/v1/query", json=query_data, timeout=10.0
            )
            print(f"   Status: {response.status_code}")
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            assert response.status_code == 200
            print("   ✓ Query with filters passed")
        except Exception as e:
            print(f"   ✗ Query with filters failed: {e}")

        # Test 5: Error handling
        print("\n7. Testing error handling (invalid query)...")
        try:
            query_data = {
                "dimensions": ["orders.invalid_dimension"],
                "measures": ["orders.count"],
            }
            response = await client.post(
                f"{base_url}/api/v1/query", json=query_data, timeout=10.0
            )
            print(f"   Status: {response.status_code}")
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            # Should return error (400 or 500)
            assert response.status_code >= 400
            print("   ✓ Error handling works correctly")
        except Exception as e:
            print(f"   ⚠ Error test: {e}")

    # Shutdown server
    print("\n8. Shutting down server...")
    server.should_exit = True
    await asyncio.sleep(1)
    print("   ✓ Server stopped")

    print("\n" + "=" * 70)
    print("✓ ALL TESTS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_api())

