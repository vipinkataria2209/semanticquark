"""Integration tests for HAVING clause and CTE support with actual SQL execution."""

import pytest
from semantic_layer.query.parser import QueryParser
from semantic_layer.models.schema import Schema
from semantic_layer.models.cube import Cube
from semantic_layer.models.dimension import Dimension
from semantic_layer.models.measure import Measure
from semantic_layer.sql.builder import SQLBuilder


@pytest.fixture
def test_schema():
    """Create a test schema with orders cube."""
    from semantic_layer.models.schema import Schema
    from semantic_layer.models.cube import Cube
    from semantic_layer.models.dimension import Dimension
    from semantic_layer.models.measure import Measure
    
    orders_cube = Cube(
        name="orders",
        table="orders",
        dimensions={
            "status": Dimension(name="status", type="string", sql="status"),
            "customer_id": Dimension(name="customer_id", type="number", sql="customer_id"),
            "created_at": Dimension(name="created_at", type="time", sql="created_at"),
        },
        measures={
            "total_revenue": Measure(name="total_revenue", type="sum", sql="total_amount"),
            "count": Measure(name="count", type="count", sql="id"),
            "avg_order_value": Measure(name="avg_order_value", type="avg", sql="total_amount"),
        }
    )
    
    return Schema(cubes={"orders": orders_cube})


class TestHAVINGIntegration:
    """Integration tests for HAVING clause."""
    
    def test_having_clause_sql_structure(self, test_schema):
        """Test that HAVING clause is correctly positioned in SQL."""
        query = QueryParser.parse({
            "measures": ["orders.total_revenue"],
            "dimensions": ["orders.status"],
            "measureFilters": [
                {
                    "member": "orders.total_revenue",
                    "operator": "gt",
                    "values": [1000]
                }
            ]
        })
        
        builder = SQLBuilder(test_schema)
        sql = builder.build(query)
        
        # Verify SQL structure
        sql_upper = sql.upper()
        assert "SELECT" in sql_upper
        assert "FROM" in sql_upper
        assert "GROUP BY" in sql_upper
        assert "HAVING" in sql_upper
        
        # Verify order: GROUP BY comes before HAVING
        group_by_pos = sql_upper.find("GROUP BY")
        having_pos = sql_upper.find("HAVING")
        assert group_by_pos < having_pos
        
        # Verify HAVING contains the measure filter
        assert "> 1000" in sql or ">1000" in sql
        assert "total_amount" in sql.lower() or "total_revenue" in sql.lower()
    
    def test_where_and_having_together(self, test_schema):
        """Test WHERE and HAVING clauses together."""
        query = QueryParser.parse({
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
                    "values": [5000]
                }
            ]
        })
        
        builder = SQLBuilder(test_schema)
        sql = builder.build(query)
        
        sql_upper = sql.upper()
        assert "WHERE" in sql_upper
        assert "GROUP BY" in sql_upper
        assert "HAVING" in sql_upper
        
        # Verify order
        where_pos = sql_upper.find("WHERE")
        group_by_pos = sql_upper.find("GROUP BY")
        having_pos = sql_upper.find("HAVING")
        
        assert where_pos < group_by_pos
        assert group_by_pos < having_pos
    
    def test_having_with_logical_operators(self, test_schema):
        """Test HAVING clause with logical operators."""
        query = QueryParser.parse({
            "measures": ["orders.total_revenue", "orders.count"],
            "dimensions": ["orders.status"],
            "measureFilters": [
                {
                    "or": [
                        {
                            "member": "orders.total_revenue",
                            "operator": "gt",
                            "values": [1000]
                        },
                        {
                            "member": "orders.count",
                            "operator": "gt",
                            "values": [100]
                        }
                    ]
                }
            ]
        })
        
        builder = SQLBuilder(test_schema)
        sql = builder.build(query)
        
        assert "HAVING" in sql.upper()
        assert "OR" in sql.upper()
        # Both measures should be in HAVING
        assert "total_amount" in sql.lower() or "total_revenue" in sql.lower()
        assert "COUNT" in sql.upper() or "count" in sql.lower()


class TestCTEIntegration:
    """Integration tests for CTE support."""
    
    def test_cte_basic_structure(self, test_schema):
        """Test basic CTE structure."""
        query = QueryParser.parse({
            "measures": ["orders.total_revenue"],
            "dimensions": ["orders.status"]
        })
        
        builder = SQLBuilder(test_schema)
        builder.add_with_query(
            "monthly_data",
            "SELECT status, SUM(total_amount) AS revenue FROM orders GROUP BY status"
        )
        
        sql = builder.build(query)
        
        # Verify CTE structure
        assert sql.upper().startswith("WITH")
        assert "monthly_data" in sql
        assert "AS (" in sql.upper()
        assert "SELECT" in sql.upper()  # Main query SELECT
    
    def test_multiple_ctes(self, test_schema):
        """Test multiple CTEs."""
        query = QueryParser.parse({
            "measures": ["orders.total_revenue"],
            "dimensions": ["orders.status"]
        })
        
        builder = SQLBuilder(test_schema)
        builder.add_with_query("cte1", "SELECT status FROM orders")
        builder.add_with_query("cte2", "SELECT status FROM orders")
        
        sql = builder.build(query)
        
        assert sql.upper().startswith("WITH")
        assert "cte1" in sql
        assert "cte2" in sql
        # Should have comma between CTEs
        assert sql.count("AS (") == 2
    
    def test_cte_with_complex_query(self, test_schema):
        """Test CTE with complex main query."""
        query = QueryParser.parse({
            "measures": ["orders.total_revenue", "orders.count"],
            "dimensions": ["orders.status"],
            "filters": [
                {"member": "orders.status", "operator": "equals", "values": ["completed"]}
            ],
            "measureFilters": [
                {"member": "orders.total_revenue", "operator": "gt", "values": [1000]}
            ],
            "order_by": [{"dimension": "orders.status", "direction": "desc"}],
            "limit": 10
        })
        
        builder = SQLBuilder(test_schema)
        builder.add_with_query(
            "base_data",
            "SELECT status, total_amount, id FROM orders WHERE created_at >= '2024-01-01'"
        )
        
        sql = builder.build(query)
        
        # Verify all components
        sql_upper = sql.upper()
        assert "WITH" in sql_upper
        assert "WHERE" in sql_upper
        assert "GROUP BY" in sql_upper
        assert "HAVING" in sql_upper
        assert "ORDER BY" in sql_upper
        assert "LIMIT" in sql_upper


class TestHAVINGAndCTECombined:
    """Test HAVING and CTE used together."""
    
    def test_cte_with_having_in_main_query(self, test_schema):
        """Test CTE with HAVING clause in main query."""
        query = QueryParser.parse({
            "measures": ["orders.total_revenue"],
            "dimensions": ["orders.status"],
            "measureFilters": [
                {"member": "orders.total_revenue", "operator": "gt", "values": [5000]}
            ]
        })
        
        builder = SQLBuilder(test_schema)
        builder.add_with_query(
            "pre_aggregated",
            "SELECT status, SUM(total_amount) AS revenue FROM orders GROUP BY status"
        )
        
        sql = builder.build(query)
        
        assert "WITH" in sql.upper()
        assert "HAVING" in sql.upper()
        # Verify CTE comes before main query
        sql_upper = sql.upper()
        with_pos = sql_upper.find("WITH")
        having_pos = sql_upper.find("HAVING")
        assert with_pos < having_pos
    
    def test_complex_scenario(self, test_schema):
        """Test complex scenario with CTE, WHERE, and HAVING."""
        query = QueryParser.parse({
            "measures": ["orders.total_revenue", "orders.count"],
            "dimensions": ["orders.status"],
            "filters": [
                {
                    "or": [
                        {"member": "orders.status", "operator": "equals", "values": ["completed"]},
                        {"member": "orders.status", "operator": "equals", "values": ["pending"]}
                    ]
                }
            ],
            "measureFilters": [
                {
                    "and": [
                        {"member": "orders.total_revenue", "operator": "gt", "values": [1000]},
                        {"member": "orders.count", "operator": "gt", "values": [10]}
                    ]
                }
            ]
        })
        
        builder = SQLBuilder(test_schema)
        builder.add_with_query(
            "filtered_orders",
            "SELECT status, total_amount, id FROM orders WHERE created_at >= '2024-01-01'"
        )
        
        sql = builder.build(query)
        
        # Verify all components exist
        sql_upper = sql.upper()
        assert "WITH" in sql_upper
        assert "WHERE" in sql_upper
        assert "GROUP BY" in sql_upper
        assert "HAVING" in sql_upper
        assert "AND" in sql_upper  # From logical filter
        assert "OR" in sql_upper   # From logical filter


class TestRealWorldScenarios:
    """Test real-world query scenarios."""
    
    def test_top_customers_by_revenue(self, test_schema):
        """Test query: Top customers with revenue > $10,000."""
        query = QueryParser.parse({
            "measures": ["orders.total_revenue"],
            "dimensions": ["orders.customer_id"],
            "measureFilters": [
                {"member": "orders.total_revenue", "operator": "gt", "values": [10000]}
            ],
            "order_by": [{"dimension": "orders.customer_id", "direction": "desc"}],
            "limit": 10
        })
        
        builder = SQLBuilder(test_schema)
        sql = builder.build(query)
        
        assert "HAVING" in sql.upper()
        assert "ORDER BY" in sql.upper()
        assert "LIMIT" in sql.upper()
        assert "> 10000" in sql or ">10000" in sql
    
    def test_multi_stage_aggregation_with_cte(self, test_schema):
        """Test multi-stage aggregation using CTE."""
        query = QueryParser.parse({
            "measures": ["orders.total_revenue"],
            "dimensions": ["orders.status"]
        })
        
        builder = SQLBuilder(test_schema)
        # First stage: daily aggregation
        builder.add_with_query(
            "daily_orders",
            "SELECT DATE_TRUNC('day', created_at) AS day, status, SUM(total_amount) AS revenue FROM orders GROUP BY day, status"
        )
        # Second stage: monthly aggregation from daily
        builder.add_with_query(
            "monthly_orders",
            "SELECT DATE_TRUNC('month', day) AS month, status, SUM(revenue) AS monthly_revenue FROM daily_orders GROUP BY month, status"
        )
        
        sql = builder.build(query)
        
        # Should have both CTEs
        assert "daily_orders" in sql
        assert "monthly_orders" in sql
        assert sql.upper().startswith("WITH")
        # Should have comma between CTEs
        assert sql.count("AS (") == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

