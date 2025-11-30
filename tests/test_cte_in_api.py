"""Test CTE support in API requests."""

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
            "created_at": Dimension(name="created_at", type="time", sql="created_at"),
        },
        measures={
            "total_revenue": Measure(name="total_revenue", type="sum", sql="total_amount"),
            "count": Measure(name="count", type="count", sql="id"),
        }
    )
    
    return Schema(cubes={"orders": orders_cube})


class TestCTEInAPIRequests:
    """Test CTE support in API request format."""
    
    def test_simple_cte_in_request(self, test_schema):
        """Test simple CTE in API request."""
        request_data = {
            "measures": ["orders.total_revenue"],
            "dimensions": ["orders.status"],
            "ctes": [
                {
                    "alias": "monthly_orders",
                    "query": "SELECT status, SUM(total_amount) AS revenue FROM orders GROUP BY status"
                }
            ]
        }
        
        query = QueryParser.parse(request_data)
        
        assert len(query.ctes) == 1
        assert query.ctes[0]["alias"] == "monthly_orders"
        assert "SELECT status" in query.ctes[0]["query"]
        
        # Build SQL
        builder = SQLBuilder(test_schema)
        for cte in query.ctes:
            builder.add_with_query(cte["alias"], cte["query"])
        sql = builder.build(query)
        
        assert sql.upper().startswith("WITH")
        assert "monthly_orders" in sql
    
    def test_multiple_ctes_in_request(self, test_schema):
        """Test multiple CTEs in API request."""
        request_data = {
            "measures": ["orders.total_revenue"],
            "dimensions": ["orders.status"],
            "ctes": [
                {
                    "alias": "daily_orders",
                    "query": "SELECT DATE_TRUNC('day', created_at) AS day, status, SUM(total_amount) AS revenue FROM orders GROUP BY day, status"
                },
                {
                    "alias": "monthly_orders",
                    "query": "SELECT DATE_TRUNC('month', day) AS month, status, SUM(revenue) AS monthly_revenue FROM daily_orders GROUP BY month, status"
                }
            ]
        }
        
        query = QueryParser.parse(request_data)
        
        assert len(query.ctes) == 2
        assert query.ctes[0]["alias"] == "daily_orders"
        assert query.ctes[1]["alias"] == "monthly_orders"
        
        # Build SQL
        builder = SQLBuilder(test_schema)
        for cte in query.ctes:
            builder.add_with_query(cte["alias"], cte["query"])
        sql = builder.build(query)
        
        assert sql.upper().startswith("WITH")
        assert "daily_orders" in sql
        assert "monthly_orders" in sql
        assert sql.count("AS (") == 2  # Two CTE definitions
    
    def test_cte_with_where_and_having(self, test_schema):
        """Test CTE with WHERE and HAVING in main query."""
        request_data = {
            "measures": ["orders.total_revenue"],
            "dimensions": ["orders.status"],
            "filters": [
                {"member": "orders.status", "operator": "equals", "values": ["completed"]}
            ],
            "measureFilters": [
                {"member": "orders.total_revenue", "operator": "gt", "values": [5000]}
            ],
            "ctes": [
                {
                    "alias": "base_data",
                    "query": "SELECT status, total_amount FROM orders WHERE created_at >= '2024-01-01'"
                }
            ]
        }
        
        query = QueryParser.parse(request_data)
        
        assert len(query.ctes) == 1
        assert len(query.filters) >= 1  # Dimension filter
        assert len(query.measure_filters) >= 1  # Measure filter
        
        # Build SQL
        builder = SQLBuilder(test_schema)
        for cte in query.ctes:
            builder.add_with_query(cte["alias"], cte["query"])
        sql = builder.build(query)
        
        sql_upper = sql.upper()
        assert "WITH" in sql_upper
        assert "WHERE" in sql_upper
        assert "HAVING" in sql_upper
        assert "base_data" in sql
    
    def test_empty_ctes_list(self, test_schema):
        """Test query without CTEs."""
        request_data = {
            "measures": ["orders.total_revenue"],
            "dimensions": ["orders.status"],
            "ctes": []
        }
        
        query = QueryParser.parse(request_data)
        
        assert len(query.ctes) == 0
        
        # Build SQL
        builder = SQLBuilder(test_schema)
        sql = builder.build(query)
        
        # Should not have WITH clause
        assert not sql.upper().startswith("WITH")
    
    def test_no_ctes_field(self, test_schema):
        """Test query without ctes field (backward compatibility)."""
        request_data = {
            "measures": ["orders.total_revenue"],
            "dimensions": ["orders.status"]
        }
        
        query = QueryParser.parse(request_data)
        
        assert len(query.ctes) == 0
        
        # Build SQL
        builder = SQLBuilder(test_schema)
        sql = builder.build(query)
        
        # Should work normally without CTEs
        assert "SELECT" in sql.upper()
        assert "FROM" in sql.upper()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

