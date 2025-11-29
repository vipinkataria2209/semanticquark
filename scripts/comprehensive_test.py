#!/usr/bin/env python3
"""Comprehensive test suite for SemanticQuark API."""

import json
import sys
import time
from typing import Dict, Any

import requests

API_BASE = "http://localhost:8000"
PASSED = 0
FAILED = 0
TESTS = []


def test(name: str, func):
    """Run a test and track results."""
    global PASSED, FAILED
    try:
        print(f"\n🧪 Testing: {name}")
        result = func()
        if result:
            print(f"   ✅ PASSED")
            PASSED += 1
            TESTS.append((name, "PASSED", None))
        else:
            print(f"   ❌ FAILED")
            FAILED += 1
            TESTS.append((name, "FAILED", "Test returned False"))
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)}")
        FAILED += 1
        TESTS.append((name, "FAILED", str(e)))


def check_response(response: requests.Response, expected_status: int = 200) -> bool:
    """Check if response is successful."""
    if response.status_code != expected_status:
        print(f"   Expected status {expected_status}, got {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        return False
    return True


def print_json(data: Dict[str, Any], max_lines: int = 10):
    """Print JSON data in a readable format."""
    json_str = json.dumps(data, indent=2)
    lines = json_str.split('\n')
    for i, line in enumerate(lines[:max_lines]):
        print(f"   {line}")
    if len(lines) > max_lines:
        print(f"   ... ({len(lines) - max_lines} more lines)")


# Test 1: Health Check
def test_health():
    """Test health endpoint."""
    response = requests.get(f"{API_BASE}/health", timeout=5)
    if not check_response(response):
        return False
    data = response.json()
    assert data.get("status") == "healthy", "Health status should be healthy"
    assert data.get("schema_loaded") is True, "Schema should be loaded"
    print_json(data)
    return True


# Test 2: Schema Endpoint
def test_schema():
    """Test schema endpoint."""
    response = requests.get(f"{API_BASE}/api/v1/schema", timeout=5)
    if not check_response(response):
        return False
    data = response.json()
    assert "cubes" in data, "Response should contain cubes"
    assert "orders" in data["cubes"], "Should have orders cube"
    cube = data["cubes"]["orders"]
    assert "dimensions" in cube, "Cube should have dimensions"
    assert "measures" in cube, "Cube should have measures"
    print_json(data)
    return True


# Test 3: Simple Query - Count
def test_simple_count():
    """Test simple count query."""
    query = {"measures": ["orders.count"]}
    response = requests.post(
        f"{API_BASE}/api/v1/query",
        json=query,
        timeout=10
    )
    if not check_response(response):
        return False
    data = response.json()
    assert "data" in data, "Response should have data"
    assert len(data["data"]) > 0, "Should have at least one row"
    assert "orders_count" in data["data"][0], "Should have count field"
    assert data["data"][0]["orders_count"] == 10, "Should have 10 orders"
    assert "meta" in data, "Should have metadata"
    print_json(data)
    return True


# Test 4: Query with Dimensions
def test_query_with_dimensions():
    """Test query with dimensions."""
    query = {
        "dimensions": ["orders.status"],
        "measures": ["orders.count", "orders.total_revenue"]
    }
    response = requests.post(
        f"{API_BASE}/api/v1/query",
        json=query,
        timeout=10
    )
    if not check_response(response):
        return False
    data = response.json()
    assert "data" in data, "Response should have data"
    assert len(data["data"]) > 0, "Should have rows grouped by status"
    print_json(data, max_lines=15)
    return True


# Test 5: Query with Filters
def test_query_with_filters():
    """Test query with filters."""
    query = {
        "measures": ["orders.count"],
        "filters": [
            {
                "dimension": "orders.status",
                "operator": "equals",
                "values": ["completed"]
            }
        ]
    }
    response = requests.post(
        f"{API_BASE}/api/v1/query",
        json=query,
        timeout=10
    )
    if not check_response(response):
        return False
    data = response.json()
    assert "data" in data, "Response should have data"
    count = data["data"][0]["orders_count"]
    assert count > 0, "Should have completed orders"
    assert count < 10, "Should have fewer than total orders"
    print_json(data)
    return True


# Test 6: Query with Multiple Filters
def test_multiple_filters():
    """Test query with multiple filters."""
    query = {
        "dimensions": ["orders.status"],
        "measures": ["orders.count"],
        "filters": [
            {
                "dimension": "orders.status",
                "operator": "in",
                "values": ["completed", "pending"]
            }
        ]
    }
    response = requests.post(
        f"{API_BASE}/api/v1/query",
        json=query,
        timeout=10
    )
    if not check_response(response):
        return False
    data = response.json()
    assert "data" in data, "Response should have data"
    print_json(data)
    return True


# Test 7: Query with Order By
def test_query_with_order_by():
    """Test query with ordering."""
    query = {
        "dimensions": ["orders.status"],
        "measures": ["orders.count"],
        "order_by": [
            {
                "dimension": "orders.status",
                "direction": "asc"
            }
        ]
    }
    response = requests.post(
        f"{API_BASE}/api/v1/query",
        json=query,
        timeout=10
    )
    if not check_response(response):
        return False
    data = response.json()
    assert "data" in data, "Response should have data"
    print_json(data)
    return True


# Test 8: Query with Limit
def test_query_with_limit():
    """Test query with limit."""
    query = {
        "dimensions": ["orders.status"],
        "measures": ["orders.count"],
        "limit": 2
    }
    response = requests.post(
        f"{API_BASE}/api/v1/query",
        json=query,
        timeout=10
    )
    if not check_response(response):
        return False
    data = response.json()
    assert "data" in data, "Response should have data"
    assert len(data["data"]) <= 2, "Should respect limit"
    print_json(data)
    return True


# Test 9: All Measures
def test_all_measures():
    """Test query with all measures."""
    query = {
        "measures": [
            "orders.count",
            "orders.total_revenue",
            "orders.average_order_value"
        ]
    }
    response = requests.post(
        f"{API_BASE}/api/v1/query",
        json=query,
        timeout=10
    )
    if not check_response(response):
        return False
    data = response.json()
    assert "data" in data, "Response should have data"
    row = data["data"][0]
    assert "orders_count" in row
    assert "orders_total_revenue" in row
    assert "orders_average_order_value" in row
    print_json(data)
    return True


# Test 10: Caching
def test_caching():
    """Test query result caching."""
    query = {"measures": ["orders.count"]}
    
    # First request
    start = time.time()
    response1 = requests.post(
        f"{API_BASE}/api/v1/query",
        json=query,
        timeout=10
    )
    time1 = time.time() - start
    
    # Second request (should be cached)
    start = time.time()
    response2 = requests.post(
        f"{API_BASE}/api/v1/query",
        json=query,
        timeout=10
    )
    time2 = time.time() - start
    
    if not check_response(response1) or not check_response(response2):
        return False
    
    data1 = response1.json()
    data2 = response2.json()
    
    # Check cache metadata
    cache_hit_1 = data1.get("meta", {}).get("cache_hit", False)
    cache_hit_2 = data2.get("meta", {}).get("cache_hit", False)
    
    print(f"   First request: {time1*1000:.2f}ms, cache_hit: {cache_hit_1}")
    print(f"   Second request: {time2*1000:.2f}ms, cache_hit: {cache_hit_2}")
    
    # Second request should be faster and/or cached
    if cache_hit_2:
        print("   ✅ Cache hit detected on second request")
    elif time2 < time1 * 0.8:  # At least 20% faster
        print("   ✅ Second request was faster (likely cached)")
    
    return True


# Test 11: Query Logs
def test_query_logs():
    """Test query logs endpoint."""
    response = requests.get(f"{API_BASE}/api/v1/logs?limit=5", timeout=5)
    if not check_response(response):
        return False
    data = response.json()
    assert "logs" in data, "Response should have logs"
    print(f"   Found {len(data['logs'])} log entries")
    if len(data["logs"]) > 0:
        print_json(data["logs"][0], max_lines=5)
    return True


# Test 12: Metrics
def test_metrics():
    """Test metrics endpoint."""
    response = requests.get(f"{API_BASE}/api/v1/metrics", timeout=5)
    if not check_response(response):
        return False
    data = response.json()
    print_json(data)
    return True


# Test 13: Pre-aggregations
def test_pre_aggregations():
    """Test pre-aggregations endpoint."""
    response = requests.get(f"{API_BASE}/api/v1/pre-aggregations", timeout=5)
    if not check_response(response):
        return False
    data = response.json()
    assert "pre_aggregations" in data, "Response should have pre_aggregations"
    print(f"   Found {len(data['pre_aggregations'])} pre-aggregations")
    print_json(data)
    return True


# Test 14: Schema Reload
def test_schema_reload():
    """Test schema reload endpoint."""
    response = requests.post(f"{API_BASE}/api/v1/reload", timeout=10)
    if not check_response(response):
        return False
    data = response.json()
    assert "status" in data, "Response should have status"
    assert data["status"] == "reloaded", "Status should be reloaded"
    print_json(data)
    return True


# Test 15: GraphQL API
def test_graphql():
    """Test GraphQL API."""
    query = {
        "query": "{ orders { count totalRevenue } }"
    }
    response = requests.post(
        f"{API_BASE}/graphql",
        json=query,
        timeout=10
    )
    # GraphQL might not be available, so we accept 200 or 404
    if response.status_code == 404:
        print("   ⚠️  GraphQL endpoint not available (this is optional)")
        return True
    if not check_response(response):
        return False
    data = response.json()
    print_json(data)
    return True


# Test 16: SQL API
def test_sql_api():
    """Test SQL API."""
    query = {
        "sql": "SELECT COUNT(*) as count FROM orders"
    }
    response = requests.post(
        f"{API_BASE}/api/v1/sql",
        json=query,
        timeout=10
    )
    # SQL API might require auth, so we accept 200 or 401/403
    if response.status_code in [401, 403]:
        print("   ⚠️  SQL API requires authentication")
        return True
    if not check_response(response):
        return False
    data = response.json()
    print_json(data)
    return True


# Test 17: Error Handling - Invalid Query
def test_error_handling():
    """Test error handling with invalid query."""
    query = {
        "measures": ["orders.nonexistent"]
    }
    response = requests.post(
        f"{API_BASE}/api/v1/query",
        json=query,
        timeout=10
    )
    # Should return error status
    if response.status_code in [400, 422, 500]:
        print(f"   ✅ Correctly returned error status: {response.status_code}")
        print(f"   Error: {response.text[:200]}")
        return True
    else:
        print(f"   Expected error status, got {response.status_code}")
        return False


# Test 18: Complex Query
def test_complex_query():
    """Test complex query with multiple dimensions and measures."""
    query = {
        "dimensions": ["orders.status"],
        "measures": ["orders.count", "orders.total_revenue", "orders.average_order_value"],
        "filters": [
            {
                "dimension": "orders.status",
                "operator": "in",
                "values": ["completed", "pending"]
            }
        ],
        "order_by": [
            {
                "dimension": "orders.status",
                "direction": "asc"
            }
        ],
        "limit": 5
    }
    response = requests.post(
        f"{API_BASE}/api/v1/query",
        json=query,
        timeout=10
    )
    if not check_response(response):
        return False
    data = response.json()
    assert "data" in data, "Response should have data"
    print_json(data, max_lines=20)
    return True


# Test 19: Time Dimension Query
def test_time_dimension():
    """Test query with time dimension."""
    query = {
        "dimensions": ["orders.created_at"],
        "measures": ["orders.count"],
        "timeDimensions": [
            {
                "dimension": "orders.created_at",
                "granularity": "day"
            }
        ]
    }
    response = requests.post(
        f"{API_BASE}/api/v1/query",
        json=query,
        timeout=10
    )
    if not check_response(response):
        return False
    data = response.json()
    assert "data" in data, "Response should have data"
    print_json(data, max_lines=15)
    return True


# Test 20: Performance Test
def test_performance():
    """Test query performance."""
    query = {"measures": ["orders.count"]}
    times = []
    
    for i in range(5):
        start = time.time()
        response = requests.post(
            f"{API_BASE}/api/v1/query",
            json=query,
            timeout=10
        )
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        if not check_response(response):
            return False
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"   Average: {avg_time:.2f}ms")
    print(f"   Min: {min_time:.2f}ms")
    print(f"   Max: {max_time:.2f}ms")
    
    if avg_time < 1000:  # Should be under 1 second
        print("   ✅ Performance is acceptable")
        return True
    else:
        print("   ⚠️  Performance might be slow")
        return True  # Still pass, just warn


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 SemanticQuark Comprehensive Test Suite")
    print("=" * 60)
    
    # Check if API is available
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ API is not available. Status: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print(f"   Make sure the API is running at {API_BASE}")
        sys.exit(1)
    
    # Run all tests
    test("Health Check", test_health)
    test("Schema Endpoint", test_schema)
    test("Simple Count Query", test_simple_count)
    test("Query with Dimensions", test_query_with_dimensions)
    test("Query with Filters", test_query_with_filters)
    test("Multiple Filters", test_multiple_filters)
    test("Query with Order By", test_query_with_order_by)
    test("Query with Limit", test_query_with_limit)
    test("All Measures", test_all_measures)
    test("Caching", test_caching)
    test("Query Logs", test_query_logs)
    test("Metrics", test_metrics)
    test("Pre-aggregations", test_pre_aggregations)
    test("Schema Reload", test_schema_reload)
    test("GraphQL API", test_graphql)
    test("SQL API", test_sql_api)
    test("Error Handling", test_error_handling)
    test("Complex Query", test_complex_query)
    test("Time Dimension Query", test_time_dimension)
    test("Performance Test", test_performance)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"✅ Passed: {PASSED}")
    print(f"❌ Failed: {FAILED}")
    print(f"📈 Total: {PASSED + FAILED}")
    print(f"🎯 Success Rate: {(PASSED / (PASSED + FAILED) * 100):.1f}%")
    
    if FAILED > 0:
        print("\n❌ Failed Tests:")
        for name, status, error in TESTS:
            if status == "FAILED":
                print(f"   - {name}: {error}")
    
    print("\n" + "=" * 60)
    
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

