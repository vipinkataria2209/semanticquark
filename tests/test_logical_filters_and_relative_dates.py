"""Test cases for Logical Filters (AND/OR) and Relative Date Ranges."""

import pytest
from semantic_layer.query.query import Query, QueryFilter, LogicalFilter, QueryTimeDimension
from semantic_layer.query.parser import QueryParser
from semantic_layer.utils.date_parser import parse_relative_date


class TestRelativeDateParser:
    """Test relative date parsing."""
    
    def test_today(self):
        """Test parsing 'today'."""
        result = parse_relative_date("today")
        assert len(result) == 2
        assert result[0] == result[1]  # Same day
    
    def test_yesterday(self):
        """Test parsing 'yesterday'."""
        result = parse_relative_date("yesterday")
        assert len(result) == 2
    
    def test_last_week(self):
        """Test parsing 'last week'."""
        result = parse_relative_date("last week")
        assert len(result) == 2
    
    def test_last_month(self):
        """Test parsing 'last month'."""
        result = parse_relative_date("last month")
        assert len(result) == 2
    
    def test_last_7_days(self):
        """Test parsing 'last 7 days'."""
        result = parse_relative_date("last 7 days")
        assert len(result) == 2
    
    def test_from_to_format(self):
        """Test parsing 'from X to Y' format."""
        result = parse_relative_date("from 7 days ago to now")
        assert len(result) == 2


class TestLogicalFilters:
    """Test logical filter operators."""
    
    def test_or_filter(self):
        """Test OR logical filter."""
        request_data = {
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
        query = QueryParser.parse(request_data)
        assert len(query.filters) == 1
        assert isinstance(query.filters[0], LogicalFilter)
        assert query.filters[0].or_ is not None
        assert len(query.filters[0].or_) == 2
    
    def test_and_filter(self):
        """Test AND logical filter."""
        request_data = {
            "measures": ["orders.revenue"],
            "filters": [
                {
                    "and": [
                        {"member": "orders.amount", "operator": "gt", "values": [100]},
                        {"member": "orders.amount", "operator": "lt", "values": [1000]}
                    ]
                }
            ]
        }
        query = QueryParser.parse(request_data)
        assert len(query.filters) == 1
        assert isinstance(query.filters[0], LogicalFilter)
        assert query.filters[0].and_ is not None
        assert len(query.filters[0].and_) == 2
    
    def test_nested_logical_filters(self):
        """Test nested logical filters (OR with AND inside)."""
        request_data = {
            "measures": ["orders.revenue"],
            "filters": [
                {
                    "or": [
                        {"member": "orders.status", "operator": "equals", "values": ["completed"]},
                        {
                            "and": [
                                {"member": "orders.status", "operator": "equals", "values": ["pending"]},
                                {"member": "orders.amount", "operator": "gt", "values": [100]}
                            ]
                        }
                    ]
                }
            ]
        }
        query = QueryParser.parse(request_data)
        assert len(query.filters) == 1
        assert isinstance(query.filters[0], LogicalFilter)
        assert query.filters[0].or_ is not None
        assert len(query.filters[0].or_) == 2
        # Second item should be a LogicalFilter (AND)
        assert isinstance(query.filters[0].or_[1], LogicalFilter)
        assert query.filters[0].or_[1].and_ is not None


class TestRelativeDateRanges:
    """Test relative date ranges in time dimensions."""
    
    def test_time_dimension_with_relative_date(self):
        """Test time dimension with relative date range."""
        request_data = {
            "measures": ["orders.revenue"],
            "timeDimensions": [
                {
                    "dimension": "orders.created_at",
                    "granularity": "day",
                    "dateRange": "last week"
                }
            ]
        }
        query = QueryParser.parse(request_data)
        assert len(query.time_dimensions) == 1
        assert query.time_dimensions[0].date_range is not None
        assert len(query.time_dimensions[0].date_range) == 2
        # Should be parsed to absolute dates
        assert isinstance(query.time_dimensions[0].date_range[0], str)
        assert isinstance(query.time_dimensions[0].date_range[1], str)
    
    def test_time_dimension_with_today(self):
        """Test time dimension with 'today'."""
        request_data = {
            "measures": ["orders.revenue"],
            "timeDimensions": [
                {
                    "dimension": "orders.created_at",
                    "granularity": "day",
                    "dateRange": "today"
                }
            ]
        }
        query = QueryParser.parse(request_data)
        assert query.time_dimensions[0].date_range is not None
    
    def test_compare_date_range_with_relative_dates(self):
        """Test compare date range with relative dates."""
        request_data = {
            "measures": ["orders.revenue"],
            "timeDimensions": [
                {
                    "dimension": "orders.created_at",
                    "granularity": "month",
                    "compareDateRange": [
                        "last month",
                        "this month"
                    ]
                }
            ]
        }
        query = QueryParser.parse(request_data)
        assert query.time_dimensions[0].compare_date_range is not None
        assert len(query.time_dimensions[0].compare_date_range) == 2


class TestCombinedFeatures:
    """Test combining logical filters and relative dates."""
    
    def test_logical_filters_with_relative_dates(self):
        """Test logical filters with relative date ranges."""
        request_data = {
            "measures": ["orders.revenue"],
            "timeDimensions": [
                {
                    "dimension": "orders.created_at",
                    "granularity": "day",
                    "dateRange": "last week"
                }
            ],
            "filters": [
                {
                    "or": [
                        {"member": "orders.status", "operator": "equals", "values": ["completed"]},
                        {"member": "orders.status", "operator": "equals", "values": ["pending"]}
                    ]
                }
            ]
        }
        query = QueryParser.parse(request_data)
        assert len(query.time_dimensions) == 1
        assert len(query.filters) == 1
        assert isinstance(query.filters[0], LogicalFilter)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

