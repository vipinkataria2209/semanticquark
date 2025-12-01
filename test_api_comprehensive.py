"""Comprehensive API test suite."""

import asyncio
import json
import sys
from pathlib import Path

import httpx


async def test_api_comprehensive(base_url: str = "http://localhost:8000"):
    """Comprehensive API testing."""
    print("=" * 70)
    print("COMPREHENSIVE API TEST SUITE")
    print("=" * 70)
    print(f"Testing API at: {base_url}")
    print()

    results = {"passed": 0, "failed": 0, "tests": []}

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Health Check
        print("Test 1: Health Check")
        print("-" * 70)
        try:
            response = await client.get(f"{base_url}/health")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert data.get("status") == "healthy", "Status should be healthy"
            print("✅ PASSED")
            results["passed"] += 1
            results["tests"].append({"name": "Health Check", "status": "PASSED"})
        except Exception as e:
            print(f"❌ FAILED: {e}")
            results["failed"] += 1
            results["tests"].append({"name": "Health Check", "status": "FAILED", "error": str(e)})
        print()

        # Test 2: Schema Endpoint
        print("Test 2: Schema Endpoint")
        print("-" * 70)
        try:
            response = await client.get(f"{base_url}/api/v1/schema")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert "cubes" in data, "Response should contain 'cubes'"
            assert len(data["cubes"]) > 0, "Should have at least one cube"
            print(f"✅ PASSED - Found {len(data['cubes'])} cubes")
            results["passed"] += 1
            results["tests"].append({"name": "Schema Endpoint", "status": "PASSED"})
        except Exception as e:
            print(f"❌ FAILED: {e}")
            results["failed"] += 1
            results["tests"].append({"name": "Schema Endpoint", "status": "FAILED", "error": str(e)})
        print()

        # Test 3: Simple Query - Dimensions Only
        print("Test 3: Simple Query (Dimensions Only)")
        print("-" * 70)
        try:
            query_data = {
                "dimensions": ["orders.id", "orders.status", "orders.total_amount"],
                "limit": 5
            }
            response = await client.post(f"{base_url}/api/v1/query", json=query_data)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert "data" in data, "Response should contain 'data'"
            assert "meta" in data, "Response should contain 'meta'"
            print(f"✅ PASSED - Returned {len(data.get('data', []))} rows")
            results["passed"] += 1
            results["tests"].append({"name": "Simple Query (Dimensions)", "status": "PASSED"})
        except Exception as e:
            print(f"❌ FAILED: {e}")
            if hasattr(e, "response") and e.response:
                print(f"   Response: {e.response.text[:200]}")
            results["failed"] += 1
            results["tests"].append({"name": "Simple Query (Dimensions)", "status": "FAILED", "error": str(e)})
        print()

        # Test 4: Query with Measures
        print("Test 4: Query with Measures")
        print("-" * 70)
        try:
            query_data = {
                "dimensions": ["orders.status"],
                "measures": ["orders.count", "orders.total_revenue"],
                "limit": 10
            }
            response = await client.post(f"{base_url}/api/v1/query", json=query_data)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert "data" in data, "Response should contain 'data'"
            assert len(data.get("data", [])) > 0, "Should return at least one row"
            print(f"✅ PASSED - Returned {len(data.get('data', []))} rows")
            results["passed"] += 1
            results["tests"].append({"name": "Query with Measures", "status": "PASSED"})
        except Exception as e:
            print(f"❌ FAILED: {e}")
            if hasattr(e, "response") and e.response:
                print(f"   Response: {e.response.text[:200]}")
            results["failed"] += 1
            results["tests"].append({"name": "Query with Measures", "status": "FAILED", "error": str(e)})
        print()

        # Test 5: Query with Filters
        print("Test 5: Query with Filters")
        print("-" * 70)
        try:
            query_data = {
                "dimensions": ["orders.status", "orders.created_at"],
                "measures": ["orders.count"],
                "filters": [
                    {
                        "dimension": "orders.status",
                        "operator": "equals",
                        "values": ["completed"]
                    }
                ],
                "limit": 5
            }
            response = await client.post(f"{base_url}/api/v1/query", json=query_data)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert "data" in data, "Response should contain 'data'"
            print(f"✅ PASSED - Returned {len(data.get('data', []))} rows")
            results["passed"] += 1
            results["tests"].append({"name": "Query with Filters", "status": "PASSED"})
        except Exception as e:
            print(f"❌ FAILED: {e}")
            if hasattr(e, "response") and e.response:
                print(f"   Response: {e.response.text[:200]}")
            results["failed"] += 1
            results["tests"].append({"name": "Query with Filters", "status": "FAILED", "error": str(e)})
        print()

        # Test 6: Query with Time Dimension
        print("Test 6: Query with Time Dimension")
        print("-" * 70)
        try:
            query_data = {
                "timeDimensions": [
                    {
                        "dimension": "orders.created_at",
                        "granularity": "month",
                        "dateRange": ["2024-01-01", "2024-12-31"]
                    }
                ],
                "measures": ["orders.count", "orders.total_revenue"],
                "limit": 10
            }
            response = await client.post(f"{base_url}/api/v1/query", json=query_data)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert "data" in data, "Response should contain 'data'"
            print(f"✅ PASSED - Returned {len(data.get('data', []))} rows")
            results["passed"] += 1
            results["tests"].append({"name": "Query with Time Dimension", "status": "PASSED"})
        except Exception as e:
            print(f"❌ FAILED: {e}")
            if hasattr(e, "response") and e.response:
                print(f"   Response: {e.response.text[:200]}")
            results["failed"] += 1
            results["tests"].append({"name": "Query with Time Dimension", "status": "FAILED", "error": str(e)})
        print()

        # Test 7: Error Handling - Invalid Dimension
        print("Test 7: Error Handling (Invalid Dimension)")
        print("-" * 70)
        try:
            query_data = {
                "dimensions": ["orders.invalid_dimension"],
                "measures": ["orders.count"]
            }
            response = await client.post(f"{base_url}/api/v1/query", json=query_data)
            # Should return error (400 or 500)
            assert response.status_code >= 400, f"Expected error status, got {response.status_code}"
            print("✅ PASSED - Error handled correctly")
            results["passed"] += 1
            results["tests"].append({"name": "Error Handling", "status": "PASSED"})
        except Exception as e:
            print(f"❌ FAILED: {e}")
            results["failed"] += 1
            results["tests"].append({"name": "Error Handling", "status": "FAILED", "error": str(e)})
        print()

        # Test 8: Query with Order By
        print("Test 8: Query with Order By")
        print("-" * 70)
        try:
            query_data = {
                "dimensions": ["orders.status"],
                "measures": ["orders.total_revenue"],
                "order_by": [
                    {
                        "dimension": "orders.status",
                        "direction": "desc"
                    }
                ],
                "limit": 5
            }
            response = await client.post(f"{base_url}/api/v1/query", json=query_data)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert "data" in data, "Response should contain 'data'"
            print(f"✅ PASSED - Returned {len(data.get('data', []))} rows")
            results["passed"] += 1
            results["tests"].append({"name": "Query with Order By", "status": "PASSED"})
        except Exception as e:
            print(f"❌ FAILED: {e}")
            if hasattr(e, "response") and e.response:
                print(f"   Response: {e.response.text[:200]}")
            results["failed"] += 1
            results["tests"].append({"name": "Query with Order By", "status": "FAILED", "error": str(e)})
        print()

    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {results['passed'] + results['failed']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print()

    if results["failed"] > 0:
        print("Failed Tests:")
        for test in results["tests"]:
            if test["status"] == "FAILED":
                print(f"  - {test['name']}: {test.get('error', 'Unknown error')}")
        print()

    return results


if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    results = asyncio.run(test_api_comprehensive(base_url))
    sys.exit(0 if results["failed"] == 0 else 1)

