"""Comprehensive Docker tests for HAVING clause and CTE support."""

import asyncio
import httpx
import json
from typing import Dict, Any, List


BASE_URL = "http://localhost:8000"


async def test_query(url: str, query_data: Dict[str, Any], test_name: str) -> Dict[str, Any]:
    """Test a query and return results."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print(f"\n{'='*70}")
            print(f"TEST: {test_name}")
            print(f"{'='*70}")
            print(f"Request: {json.dumps(query_data, indent=2)}")
            
            response = await client.post(url, json=query_data)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS")
                print(f"Rows returned: {len(result.get('data', []))}")
                if 'meta' in result and 'sql' in result['meta']:
                    print(f"\nGenerated SQL:")
                    print(result['meta']['sql'])
                if result.get('data'):
                    print(f"\nFirst row: {result['data'][0]}")
                return {"status": "success", "result": result}
            else:
                error = response.text
                print(f"❌ FAILED: {error}")
                return {"status": "failed", "error": error}
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return {"status": "error", "error": str(e)}


async def run_all_tests():
    """Run all comprehensive tests."""
    print("="*70)
    print("COMPREHENSIVE DOCKER TESTS: HAVING CLAUSE & CTE")
    print("="*70)
    
    results = []
    
    # Test 1: Basic query (no HAVING, no CTE)
    results.append(await test_query(
        f"{BASE_URL}/api/v1/query",
        {
            "measures": ["orders.total_revenue"],
            "dimensions": ["orders.status"]
        },
        "1. Basic Query (Baseline)"
    ))
    
    # Test 2: HAVING clause with measure filter
    results.append(await test_query(
        f"{BASE_URL}/api/v1/query",
        {
            "measures": ["orders.total_revenue"],
            "dimensions": ["orders.status"],
            "measureFilters": [
                {
                    "member": "orders.total_revenue",
                    "operator": "gt",
                    "values": [0]
                }
            ]
        },
        "2. HAVING Clause (Measure Filter > 0)"
    ))
    
    # Test 3: HAVING clause with logical OR
    results.append(await test_query(
        f"{BASE_URL}/api/v1/query",
        {
            "measures": ["orders.total_revenue", "orders.count"],
            "dimensions": ["orders.status"],
            "measureFilters": [
                {
                    "or": [
                        {
                            "member": "orders.total_revenue",
                            "operator": "gt",
                            "values": [100]
                        },
                        {
                            "member": "orders.count",
                            "operator": "gt",
                            "values": [5]
                        }
                    ]
                }
            ]
        },
        "3. HAVING Clause (Logical OR)"
    ))
    
    # Test 4: HAVING clause with logical AND
    results.append(await test_query(
        f"{BASE_URL}/api/v1/query",
        {
            "measures": ["orders.total_revenue", "orders.count"],
            "dimensions": ["orders.status"],
            "measureFilters": [
                {
                    "and": [
                        {
                            "member": "orders.total_revenue",
                            "operator": "gt",
                            "values": [0]
                        },
                        {
                            "member": "orders.count",
                            "operator": "gt",
                            "values": [0]
                        }
                    ]
                }
            ]
        },
        "4. HAVING Clause (Logical AND)"
    ))
    
    # Test 5: WHERE + HAVING together
    results.append(await test_query(
        f"{BASE_URL}/api/v1/query",
        {
            "measures": ["orders.total_revenue"],
            "dimensions": ["orders.status"],
            "filters": [
                {
                    "member": "orders.status",
                    "operator": "equals",
                    "values": ["completed"]
                }
            ],
            "measureFilters": [
                {
                    "member": "orders.total_revenue",
                    "operator": "gt",
                    "values": [0]
                }
            ]
        },
        "5. WHERE + HAVING Together"
    ))
    
    # Test 6: Simple CTE
    results.append(await test_query(
        f"{BASE_URL}/api/v1/query",
        {
            "measures": ["orders.total_revenue"],
            "dimensions": ["orders.status"],
            "ctes": [
                {
                    "alias": "test_cte",
                    "query": "SELECT status, total_amount FROM orders LIMIT 10"
                }
            ]
        },
        "6. Simple CTE"
    ))
    
    # Test 7: Multiple CTEs
    results.append(await test_query(
        f"{BASE_URL}/api/v1/query",
        {
            "measures": ["orders.total_revenue"],
            "dimensions": ["orders.status"],
            "ctes": [
                {
                    "alias": "cte1",
                    "query": "SELECT status FROM orders LIMIT 5"
                },
                {
                    "alias": "cte2",
                    "query": "SELECT status FROM orders LIMIT 10"
                }
            ]
        },
        "7. Multiple CTEs"
    ))
    
    # Test 8: CTE with WHERE and HAVING
    results.append(await test_query(
        f"{BASE_URL}/api/v1/query",
        {
            "measures": ["orders.total_revenue"],
            "dimensions": ["orders.status"],
            "filters": [
                {
                    "member": "orders.status",
                    "operator": "equals",
                    "values": ["completed"]
                }
            ],
            "measureFilters": [
                {
                    "member": "orders.total_revenue",
                    "operator": "gt",
                    "values": [0]
                }
            ],
            "ctes": [
                {
                    "alias": "base_data",
                    "query": "SELECT status, total_amount FROM orders WHERE created_at >= '2024-01-01'"
                }
            ]
        },
        "8. CTE + WHERE + HAVING Combined"
    ))
    
    # Test 9: Complex nested logical filters in HAVING
    results.append(await test_query(
        f"{BASE_URL}/api/v1/query",
        {
            "measures": ["orders.total_revenue", "orders.count"],
            "dimensions": ["orders.status"],
            "measureFilters": [
                {
                    "or": [
                        {
                            "member": "orders.total_revenue",
                            "operator": "gt",
                            "values": [100]
                        },
                        {
                            "and": [
                                {
                                    "member": "orders.total_revenue",
                                    "operator": "gt",
                                    "values": [0]
                                },
                                {
                                    "member": "orders.count",
                                    "operator": "gt",
                                    "values": [0]
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "9. Complex Nested Logical Filters in HAVING"
    ))
    
    # Test 10: CTE with time dimension
    results.append(await test_query(
        f"{BASE_URL}/api/v1/query",
        {
            "measures": ["orders.total_revenue"],
            "timeDimensions": [
                {
                    "dimension": "orders.created_at",
                    "granularity": "month",
                    "dateRange": ["2024-01-01", "2024-12-31"]
                }
            ],
            "ctes": [
                {
                    "alias": "monthly_base",
                    "query": "SELECT DATE_TRUNC('month', created_at) AS month, SUM(total_amount) AS revenue FROM orders GROUP BY month"
                }
            ]
        },
        "10. CTE with Time Dimension"
    ))
    
    # Test 11: All features combined
    results.append(await test_query(
        f"{BASE_URL}/api/v1/query",
        {
            "measures": ["orders.total_revenue", "orders.count"],
            "dimensions": ["orders.status"],
            "filters": [
                {
                    "or": [
                        {
                            "member": "orders.status",
                            "operator": "equals",
                            "values": ["completed"]
                        },
                        {
                            "member": "orders.status",
                            "operator": "equals",
                            "values": ["pending"]
                        }
                    ]
                }
            ],
            "measureFilters": [
                {
                    "and": [
                        {
                            "member": "orders.total_revenue",
                            "operator": "gt",
                            "values": [0]
                        },
                        {
                            "member": "orders.count",
                            "operator": "gt",
                            "values": [0]
                        }
                    ]
                }
            ],
            "ctes": [
                {
                    "alias": "filtered_base",
                    "query": "SELECT status, total_amount, id FROM orders WHERE created_at >= '2024-01-01'"
                }
            ],
            "order_by": [
                {
                    "dimension": "orders.status",
                    "direction": "desc"
                }
            ],
            "limit": 10
        },
        "11. All Features Combined (WHERE + HAVING + CTE + ORDER BY + LIMIT)"
    ))
    
    # Test 12: Measure filter with different operators
    operators = ["gt", "gte", "lt", "lte", "equals", "not_equals"]
    for i, op in enumerate(operators):
        results.append(await test_query(
            f"{BASE_URL}/api/v1/query",
            {
                "measures": ["orders.total_revenue"],
                "dimensions": ["orders.status"],
                "measureFilters": [
                    {
                        "member": "orders.total_revenue",
                        "operator": op,
                        "values": [0] if op in ["gt", "gte", "lt", "lte"] else [0]
                    }
                ],
                "limit": 5
            },
            f"12.{i+1}. HAVING with {op} operator"
        ))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "success")
    failed = sum(1 for r in results if r.get("status") == "failed")
    errors = sum(1 for r in results if r.get("status") == "error")
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Errors: {errors}")
    
    if failed > 0 or errors > 0:
        print("\nFailed/Error Tests:")
        for i, result in enumerate(results, 1):
            if result.get("status") != "success":
                print(f"  Test {i}: {result.get('error', 'Unknown error')}")
    
    print("\n" + "="*70)
    
    return results


if __name__ == "__main__":
    asyncio.run(run_all_tests())

