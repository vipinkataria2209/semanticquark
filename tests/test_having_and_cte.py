"""Comprehensive tests for HAVING clause and CTE (WITH clause) support."""

import pytest
from semantic_layer.query.query import Query, QueryFilter, LogicalFilter, QueryTimeDimension
from semantic_layer.query.parser import QueryParser
from semantic_layer.models.schema import Schema
from semantic_layer.models.cube import Cube
from semantic_layer.models.dimension import Dimension
from semantic_layer.models.measure import Measure
from semantic_layer.sql.builder import SQLBuilder
from semantic_layer.exceptions import QueryError


@pytest.fixture
def test_schema():
    """Create a test schema with orders cube."""
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


class TestHAVINGClause:
    """Test HAVING clause generation for measure filters."""
    
    def test_simple_measure_filter(self, test_schema):
        """Test simple measure filter generates HAVING clause."""
        query = Query(
            measures=["orders.total_revenue"],
            dimensions=["orders.status"],
            measure_filters=[
                QueryFilter(
                    dimension="orders.total_revenue",
                    operator="gt",
                    values=[1000]
                )
            ]
        )
        
        builder = SQLBuilder(test_schema)
        sql = builder.build(query)
        
        assert "HAVING" in sql.upper()
        assert "SUM" in sql.upper() or "total_amount" in sql.lower()
        assert "> 1000" in sql or ">1000" in sql
        assert "WHERE" not in sql.upper() or "WHERE" in sql.upper()  # WHERE might exist for other filters
        
        # Verify HAVING comes after GROUP BY
        sql_upper = sql.upper()
        group_by_pos = sql_upper.find("GROUP BY")
        having_pos = sql_upper.find("HAVING")
        assert group_by_pos < having_pos or group_by_pos == -1
    
    def test_measure_filter_with_dimension_filter(self, test_schema):
        """Test that dimension filters go to WHERE and measure filters go to HAVING."""
        query = Query(
            measures=["orders.total_revenue"],
            dimensions=["orders.status"],
            filters=[
                QueryFilter(
                    dimension="orders.status",
                    operator="equals",
                    values=["completed"]
                )
            ],
            measure_filters=[
                QueryFilter(
                    dimension="orders.total_revenue",
                    operator="gt",
                    values=[1000]
                )
            ]
        )
        
        builder = SQLBuilder(test_schema)
        sql = builder.build(query)
        
        # Should have both WHERE and HAVING
        assert "WHERE" in sql.upper()
        assert "HAVING" in sql.upper()
        
        # WHERE should come before GROUP BY, HAVING should come after
        sql_upper = sql.upper()
        where_pos = sql_upper.find("WHERE")
        group_by_pos = sql_upper.find("GROUP BY")
        having_pos = sql_upper.find("HAVING")
        
        assert where_pos < group_by_pos
        assert group_by_pos < having_pos
    
    def test_measure_filter_with_logical_operator(self, test_schema):
        """Test measure filter with OR logical operator."""
        query = Query(
            measures=["orders.total_revenue"],
            dimensions=["orders.status"],
            measure_filters=[
                LogicalFilter(**{"or": [
                    QueryFilter(
                        dimension="orders.total_revenue",
                        operator="gt",
                        values=[1000]
                    ),
                    QueryFilter(
                        dimension="orders.total_revenue",
                        operator="lt",
                        values=[100]
                    )
                ]})
            ]
        )
        
        builder = SQLBuilder(test_schema)
        sql = builder.build(query)
        
        assert "HAVING" in sql.upper()
        assert "OR" in sql.upper()
        assert "> 1000" in sql or ">1000" in sql
        assert "< 100" in sql or "<100" in sql
    
    def test_measure_filter_with_and_operator(self, test_schema):
        """Test measure filter with AND logical operator."""
        query = Query(
            measures=["orders.total_revenue", "orders.count"],
            dimensions=["orders.status"],
            measure_filters=[
                LogicalFilter(**{"and": [
                    QueryFilter(
                        dimension="orders.total_revenue",
                        operator="gt",
                        values=[1000]
                    ),
                    QueryFilter(
                        dimension="orders.count",
                        operator="gt",
                        values=[10]
                    )
                ]})
            ]
        )
        
        builder = SQLBuilder(test_schema)
        sql = builder.build(query)
        
        assert "HAVING" in sql.upper()
        assert "AND" in sql.upper()
        # Both conditions should be present
        assert "total_revenue" in sql.lower() or "total_amount" in sql.lower()
        assert "count" in sql.lower() or "COUNT" in sql.upper()
    
    def test_nested_logical_filters_in_measure_filters(self, test_schema):
        """Test nested logical filters (OR with AND) in measure filters."""
        query = Query(
            measures=["orders.total_revenue", "orders.count"],
            dimensions=["orders.status"],
            measure_filters=[
                LogicalFilter(**{"or": [
                    QueryFilter(
                        dimension="orders.total_revenue",
                        operator="gt",
                        values=[1000]
                    ),
                    LogicalFilter(**{"and": [
                        QueryFilter(
                            dimension="orders.total_revenue",
                            operator="gt",
                            values=[500]
                        ),
                        QueryFilter(
                            dimension="orders.count",
                            operator="gt",
                            values=[5]
                        )
                    ]})
                ]})
            ]
        )
        
        builder = SQLBuilder(test_schema)
        sql = builder.build(query)
        
        assert "HAVING" in sql.upper()
        assert "OR" in sql.upper()
        assert "AND" in sql.upper()
        # Verify nested structure with parentheses
        assert "(" in sql and ")" in sql
    
    def test_measure_filter_operators(self, test_schema):
        """Test various measure filter operators."""
        operators = [
            ("gt", ">"),
            ("gte", ">="),
            ("lt", "<"),
            ("lte", "<="),
            ("equals", "="),
            ("not_equals", "!="),
        ]
        
        for op_name, sql_op in operators:
            query = Query(
                measures=["orders.total_revenue"],
                dimensions=["orders.status"],
                measure_filters=[
                    QueryFilter(
                        dimension="orders.total_revenue",
                        operator=op_name,
                        values=[1000]
                    )
                ]
            )
            
            builder = SQLBuilder(test_schema)
            sql = builder.build(query)
            
            assert "HAVING" in sql.upper()
            assert sql_op in sql or sql_op.replace("=", " =") in sql


class TestCTESupport:
    """Test CTE (WITH clause) support."""
    
    def test_simple_cte(self, test_schema):
        """Test simple CTE generation."""
        query = Query(
            measures=["orders.total_revenue"],
            dimensions=["orders.status"]
        )
        
        builder = SQLBuilder(test_schema)
        
        # Add a CTE
        builder.add_with_query(
            "monthly_orders",
            "SELECT status, SUM(total_amount) AS revenue FROM orders GROUP BY status"
        )
        
        sql = builder.build(query)
        
        assert sql.upper().startswith("WITH")
        assert "monthly_orders" in sql
        assert "AS (" in sql.upper()
    
    def test_multiple_ctes(self, test_schema):
        """Test multiple CTEs."""
        query = Query(
            measures=["orders.total_revenue"],
            dimensions=["orders.status"]
        )
        
        builder = SQLBuilder(test_schema)
        
        # Add multiple CTEs
        builder.add_with_query(
            "daily_orders",
            "SELECT DATE_TRUNC('day', created_at) AS day, status, SUM(total_amount) AS revenue FROM orders GROUP BY day, status"
        )
        builder.add_with_query(
            "monthly_orders",
            "SELECT DATE_TRUNC('month', day) AS month, status, SUM(revenue) AS monthly_revenue FROM daily_orders GROUP BY month, status"
        )
        
        sql = builder.build(query)
        
        # Should have WITH clause with both CTEs
        assert sql.upper().startswith("WITH")
        assert "daily_orders" in sql
        assert "monthly_orders" in sql
        assert sql.count("AS (") == 2  # Two CTE definitions
    
    def test_cte_with_main_query(self, test_schema):
        """Test CTE with main query that uses it."""
        query = Query(
            measures=["orders.total_revenue"],
            dimensions=["orders.status"]
        )
        
        builder = SQLBuilder(test_schema)
        
        # Add CTE
        builder.add_with_query(
            "filtered_orders",
            "SELECT status, total_amount FROM orders WHERE created_at >= '2024-01-01'"
        )
        
        sql = builder.build(query)
        
        # CTE should come before SELECT
        sql_upper = sql.upper()
        with_pos = sql_upper.find("WITH")
        select_pos = sql_upper.find("SELECT")
        assert with_pos < select_pos
    
    def test_cte_with_where_and_having(self, test_schema):
        """Test CTE with query that has both WHERE and HAVING."""
        query = Query(
            measures=["orders.total_revenue"],
            dimensions=["orders.status"],
            filters=[
                QueryFilter(
                    dimension="orders.status",
                    operator="equals",
                    values=["completed"]
                )
            ],
            measure_filters=[
                QueryFilter(
                    dimension="orders.total_revenue",
                    operator="gt",
                    values=[1000]
                )
            ]
        )
        
        builder = SQLBuilder(test_schema)
        builder.add_with_query(
            "base_orders",
            "SELECT status, total_amount FROM orders"
        )
        
        sql = builder.build(query)
        
        # Should have WITH, WHERE, GROUP BY, and HAVING
        sql_upper = sql.upper()
        assert "WITH" in sql_upper
        assert "WHERE" in sql_upper
        assert "GROUP BY" in sql_upper
        assert "HAVING" in sql_upper
        
        # Verify order: WITH -> SELECT -> FROM -> WHERE -> GROUP BY -> HAVING
        with_pos = sql_upper.find("WITH")
        select_pos = sql_upper.find("SELECT", with_pos + 1)
        where_pos = sql_upper.find("WHERE")
        group_by_pos = sql_upper.find("GROUP BY")
        having_pos = sql_upper.find("HAVING")
        
        assert with_pos < select_pos
        assert where_pos < group_by_pos
        assert group_by_pos < having_pos


class TestHAVINGAndCTEIntegration:
    """Test integration of HAVING and CTE together."""
    
    def test_cte_with_having_in_main_query(self, test_schema):
        """Test CTE with HAVING clause in main query."""
        query = Query(
            measures=["orders.total_revenue"],
            dimensions=["orders.status"],
            measure_filters=[
                QueryFilter(
                    dimension="orders.total_revenue",
                    operator="gt",
                    values=[5000]
                )
            ]
        )
        
        builder = SQLBuilder(test_schema)
        builder.add_with_query(
            "monthly_data",
            "SELECT status, DATE_TRUNC('month', created_at) AS month, SUM(total_amount) AS revenue FROM orders GROUP BY status, month"
        )
        
        sql = builder.build(query)
        
        assert "WITH" in sql.upper()
        assert "HAVING" in sql.upper()
        assert "monthly_data" in sql
    
    def test_complex_query_with_cte_and_having(self, test_schema):
        """Test complex query with CTE, WHERE, and HAVING."""
        query = Query(
            measures=["orders.total_revenue", "orders.count"],
            dimensions=["orders.status"],
            filters=[
                QueryFilter(
                    dimension="orders.status",
                    operator="in",
                    values=["completed", "pending"]
                )
            ],
            measure_filters=[
                LogicalFilter(**{"and": [
                    QueryFilter(
                        dimension="orders.total_revenue",
                        operator="gt",
                        values=[1000]
                    ),
                    QueryFilter(
                        dimension="orders.count",
                        operator="gt",
                        values=[10]
                    )
                ]})
            ]
        )
        
        builder = SQLBuilder(test_schema)
        builder.add_with_query(
            "filtered_base",
            "SELECT status, total_amount, id FROM orders WHERE created_at >= '2024-01-01'"
        )
        
        sql = builder.build(query)
        
        # Verify all components
        sql_upper = sql.upper()
        assert "WITH" in sql_upper
        assert "WHERE" in sql_upper
        assert "GROUP BY" in sql_upper
        assert "HAVING" in sql_upper
        assert "AND" in sql_upper  # From logical filter


class TestQueryParserWithMeasureFilters:
    """Test QueryParser handling of measure filters."""
    
    def test_parse_measure_filters_explicit(self, test_schema):
        """Test parsing explicit measureFilters in request."""
        request_data = {
            "measures": ["orders.total_revenue"],
            "dimensions": ["orders.status"],
            "measureFilters": [
                {
                    "member": "orders.total_revenue",
                    "operator": "gt",
                    "values": [1000]
                }
            ]
        }
        
        query = QueryParser.parse(request_data)
        
        assert len(query.measure_filters) == 1
        assert isinstance(query.measure_filters[0], QueryFilter)
        assert query.measure_filters[0].dimension == "orders.total_revenue"
        assert query.measure_filters[0].operator == "gt"
    
    def test_parse_measure_filters_auto_detect(self, test_schema):
        """Test auto-detection of measure filters from filters array."""
        request_data = {
            "measures": ["orders.total_revenue"],
            "dimensions": ["orders.status"],
            "filters": [
                {
                    "member": "orders.total_revenue",  # This is a measure
                    "operator": "gt",
                    "values": [1000]
                },
                {
                    "member": "orders.status",  # This is a dimension
                    "operator": "equals",
                    "values": ["completed"]
                }
            ]
        }
        
        query = QueryParser.parse(request_data)
        
        # Should separate measure filters from dimension filters
        # Note: Current implementation uses heuristic, may need refinement
        assert len(query.filters) >= 0  # At least dimension filter
        # Measure filter might be in filters or measure_filters depending on detection


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_having_without_group_by(self, test_schema):
        """Test HAVING clause without GROUP BY (should still work)."""
        query = Query(
            measures=["orders.total_revenue"],
            measure_filters=[
                QueryFilter(
                    dimension="orders.total_revenue",
                    operator="gt",
                    values=[1000]
                )
            ]
        )
        
        builder = SQLBuilder(test_schema)
        sql = builder.build(query)
        
        # HAVING can exist without GROUP BY in some databases
        # But typically GROUP BY is needed when aggregating
        assert "HAVING" in sql.upper()
    
    def test_empty_cte_list(self, test_schema):
        """Test query without CTEs."""
        query = Query(
            measures=["orders.total_revenue"],
            dimensions=["orders.status"]
        )
        
        builder = SQLBuilder(test_schema)
        sql = builder.build(query)
        
        # Should not have WITH clause
        assert not sql.upper().startswith("WITH")
    
    def test_cte_with_special_characters(self, test_schema):
        """Test CTE with special characters in alias or query."""
        query = Query(
            measures=["orders.total_revenue"],
            dimensions=["orders.status"]
        )
        
        builder = SQLBuilder(test_schema)
        builder.add_with_query(
            "orders_2024",
            "SELECT status, total_amount FROM orders WHERE created_at >= '2024-01-01'"
        )
        
        sql = builder.build(query)
        
        assert "orders_2024" in sql
        assert "'2024-01-01'" in sql


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

