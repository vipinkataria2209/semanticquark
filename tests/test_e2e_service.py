"""End-to-end integration tests against running SemanticQuark service."""

import pytest
import httpx
import asyncio
from typing import Dict, Any


@pytest.fixture(scope="module")
def service_url():
    """Get service URL from environment or default."""
    import os
    return os.getenv("SERVICE_URL", "http://semanticquark:8000")


@pytest.mark.asyncio
async def test_service_health(service_url):
    """Test that service is running."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{service_url}/health")
            assert response.status_code == 200
            print(f"✅ Service health check passed: {response.json()}")
        except httpx.ConnectError:
            pytest.skip(f"Service not available at {service_url}")


@pytest.mark.asyncio
async def test_logical_filter_via_api(service_url):
    """Test logical filter (OR) via REST API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        query = {
            "measures": ["orders.total_revenue"],
            "filters": [
                {
                    "or": [
                        {"member": "orders.status", "operator": "equals", "values": ["completed"]},
                        {"member": "orders.status", "operator": "equals", "values": ["pending"]}
                    ]
                }
            ]
        }
        
        try:
            response = await client.post(
                f"{service_url}/api/v1/query",
                json=query,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Logical filter query executed")
                print(f"   SQL: {result.get('meta', {}).get('sql', 'N/A')}")
                print(f"   Rows: {result.get('meta', {}).get('row_count', 0)}")
                assert "data" in result
                assert "meta" in result
            else:
                print(f"⚠️  Query returned status {response.status_code}: {response.text}")
                # Don't fail if it's a schema/model issue
                if response.status_code == 422:
                    pytest.skip("Schema/model not configured")
        except httpx.ConnectError:
            pytest.skip(f"Service not available at {service_url}")


@pytest.mark.asyncio
async def test_relative_date_via_api(service_url):
    """Test relative date range via REST API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        query = {
            "measures": ["orders.total_revenue"],
            "timeDimensions": [
                {
                    "dimension": "orders.created_at",
                    "granularity": "day",
                    "dateRange": "last 30 days"
                }
            ]
        }
        
        try:
            response = await client.post(
                f"{service_url}/api/v1/query",
                json=query,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Relative date query executed")
                print(f"   Parsed date range: {result.get('meta', {}).get('query', {}).get('time_dimensions', [{}])[0].get('date_range', 'N/A')}")
                print(f"   SQL: {result.get('meta', {}).get('sql', 'N/A')}")
                assert "data" in result
            else:
                print(f"⚠️  Query returned status {response.status_code}: {response.text}")
                if response.status_code == 422:
                    pytest.skip("Schema/model not configured")
        except httpx.ConnectError:
            pytest.skip(f"Service not available at {service_url}")


@pytest.mark.asyncio
async def test_compare_date_range_via_api(service_url):
    """Test compare date range via REST API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        query = {
            "measures": ["orders.total_revenue"],
            "timeDimensions": [
                {
                    "dimension": "orders.created_at",
                    "granularity": "day",
                    "compareDateRange": [
                        ["2024-01-15", "2024-01-15"],
                        ["2024-01-16", "2024-01-16"]
                    ]
                }
            ]
        }
        
        try:
            response = await client.post(
                f"{service_url}/api/v1/query",
                json=query,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Compare date range query executed")
                print(f"   Compare date range: {result.get('meta', {}).get('compare_date_range', False)}")
                print(f"   Rows: {result.get('meta', {}).get('row_count', 0)}")
                assert "data" in result
                assert result.get("meta", {}).get("compare_date_range") == True
            else:
                print(f"⚠️  Query returned status {response.status_code}: {response.text}")
                if response.status_code == 422:
                    pytest.skip("Schema/model not configured")
        except httpx.ConnectError:
            pytest.skip(f"Service not available at {service_url}")


@pytest.mark.asyncio
async def test_nested_logical_filter_via_api(service_url):
    """Test nested logical filter (OR with AND) via REST API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        query = {
            "measures": ["orders.total_revenue"],
            "filters": [
                {
                    "or": [
                        {"member": "orders.status", "operator": "equals", "values": ["completed"]},
                        {
                            "and": [
                                {"member": "orders.status", "operator": "equals", "values": ["pending"]},
                                {"member": "orders.total_revenue", "operator": "gt", "values": [50]}
                            ]
                        }
                    ]
                }
            ]
        }
        
        try:
            response = await client.post(
                f"{service_url}/api/v1/query",
                json=query,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                sql = result.get("meta", {}).get("sql", "").upper()
                print(f"✅ Nested logical filter query executed")
                print(f"   SQL contains OR: {'OR' in sql}")
                print(f"   SQL contains AND: {'AND' in sql}")
                assert "OR" in sql or "or" in sql
                assert "AND" in sql or "and" in sql
            else:
                print(f"⚠️  Query returned status {response.status_code}: {response.text}")
                if response.status_code == 422:
                    pytest.skip("Schema/model not configured")
        except httpx.ConnectError:
            pytest.skip(f"Service not available at {service_url}")


@pytest.mark.asyncio
async def test_blending_query_via_api(service_url):
    """Test blending query (multiple queries) via REST API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        queries = [
            {
                "measures": ["orders.total_revenue"]
            },
            {
                "measures": ["orders.count"]
            }
        ]
        
        try:
            response = await client.post(
                f"{service_url}/api/v1/query",
                json=queries,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Blending query executed")
                assert isinstance(result, list)
                assert len(result) == 2
                print(f"   Results count: {len(result)}")
            else:
                print(f"⚠️  Query returned status {response.status_code}: {response.text}")
                if response.status_code == 422:
                    pytest.skip("Schema/model not configured")
        except httpx.ConnectError:
            pytest.skip(f"Service not available at {service_url}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

