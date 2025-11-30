"""Integration tests to verify features work end-to-end in Docker."""

import pytest
from semantic_layer.query.parser import QueryParser
from semantic_layer.query.query import Query, QueryFilter, LogicalFilter, QueryTimeDimension


class TestIntegrationLogicalFilters:
    """Integration tests for logical filters."""
    
    def test_complex_nested_logical_filter(self):
        """Test complex nested logical filter like Cube.js example."""
        request_data = {
            "measures": ["visitors.count"],
            "filters": [
                {
                    "or": [
                        {
                            "member": "visitors.source",
                            "operator": "equals",
                            "values": ["some"]
                        },
                        {
                            "and": [
                                {
                                    "member": "visitors.source",
                                    "operator": "equals",
                                    "values": ["other"]
                                },
                                {
                                    "member": "visitor_checkins.cards_count",
                                    "operator": "equals",
                                    "values": ["0"]
                                }
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
        
        # First item should be a QueryFilter
        assert isinstance(query.filters[0].or_[0], QueryFilter)
        assert query.filters[0].or_[0].member == "visitors.source"
        
        # Second item should be a LogicalFilter (AND)
        assert isinstance(query.filters[0].or_[1], LogicalFilter)
        assert query.filters[0].or_[1].and_ is not None
        assert len(query.filters[0].or_[1].and_) == 2


class TestIntegrationRelativeDates:
    """Integration tests for relative date ranges."""
    
    def test_time_dimension_with_last_week(self):
        """Test time dimension with 'last week' relative date."""
        request_data = {
            "measures": ["stories.count"],
            "timeDimensions": [
                {
                    "dimension": "stories.time",
                    "dateRange": "last week",
                    "granularity": "day"
                }
            ]
        }
        
        query = QueryParser.parse(request_data)
        assert len(query.time_dimensions) == 1
        assert query.time_dimensions[0].date_range is not None
        assert len(query.time_dimensions[0].date_range) == 2
        # Should be parsed to absolute dates
        assert query.time_dimensions[0].date_range[0] != "last week"
        assert query.time_dimensions[0].date_range[1] != "last week"
        # Should be valid date format
        assert len(query.time_dimensions[0].date_range[0]) == 10  # YYYY-MM-DD
        assert len(query.time_dimensions[0].date_range[1]) == 10
    
    def test_compare_date_range_with_relative_dates(self):
        """Test compare date range with relative dates."""
        request_data = {
            "measures": ["stories.count"],
            "timeDimensions": [
                {
                    "dimension": "stories.time",
                    "compareDateRange": [
                        "this week",
                        "last week"
                    ],
                    "granularity": "month"
                }
            ]
        }
        
        query = QueryParser.parse(request_data)
        assert query.time_dimensions[0].compare_date_range is not None
        assert len(query.time_dimensions[0].compare_date_range) == 2
        # Both should be parsed to absolute dates
        assert len(query.time_dimensions[0].compare_date_range[0]) == 2
        assert len(query.time_dimensions[0].compare_date_range[1]) == 2


class TestIntegrationCombined:
    """Integration tests combining all features."""
    
    def test_all_features_together(self):
        """Test logical filters + relative dates + compare date range together."""
        request_data = {
            "measures": ["orders.revenue"],
            "dimensions": ["orders.status"],
            "timeDimensions": [
                {
                    "dimension": "orders.created_at",
                    "granularity": "day",
                    "dateRange": "last 7 days"
                }
            ],
            "filters": [
                {
                    "or": [
                        {"member": "orders.status", "operator": "equals", "values": ["completed"]},
                        {"member": "orders.status", "operator": "equals", "values": ["pending"]}
                    ]
                }
            ],
            "order_by": [{"dimension": "orders.revenue", "direction": "desc"}],
            "limit": 10
        }
        
        query = QueryParser.parse(request_data)
        
        # Verify all components
        assert len(query.measures) == 1
        assert len(query.dimensions) == 1
        assert len(query.time_dimensions) == 1
        assert len(query.filters) == 1
        assert len(query.order_by) == 1
        assert query.limit == 10
        
        # Verify logical filter
        assert isinstance(query.filters[0], LogicalFilter)
        assert query.filters[0].or_ is not None
        
        # Verify relative date was parsed
        assert query.time_dimensions[0].date_range is not None
        assert len(query.time_dimensions[0].date_range) == 2
        assert query.time_dimensions[0].date_range[0] != "last 7 days"  # Should be parsed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

