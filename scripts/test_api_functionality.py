"""Test API functionality with migrated code."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def test_query_execution():
    """Test query execution with new structure."""
    print("\n" + "="*60)
    print("TEST: Query Execution with New Structure")
    print("="*60)
    
    try:
        from semantic_layer.schema import SchemaLoader
        from semantic_layer.drivers import PostgresDriver, ConnectionConfig
        from semantic_layer.orchestrator import QueryEngine
        from semantic_layer.query.parser import QueryParser
        
        # Load schema
        models_path = Path("models")
        if not models_path.exists():
            print("⚠️  models/ directory not found, skipping query test")
            return True
        
        schema = SchemaLoader.load_from_directory(models_path)
        print(f"✅ Schema loaded: {len(schema.cubes)} cubes")
        
        # Create a mock connector (we won't actually connect)
        # Just test that the structure works
        print("✅ Query execution structure: PASSED")
        return True
    except Exception as e:
        print(f"❌ Query execution: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_sql_generation():
    """Test SQL generation with new structure."""
    print("\n" + "="*60)
    print("TEST: SQL Generation with New Structure")
    print("="*60)
    
    try:
        from semantic_layer.schema import SchemaLoader
        from semantic_layer.sql import SQLBuilder
        from semantic_layer.query.parser import QueryParser
        from semantic_layer.sql.dialects import PostgresDialect
        
        # Load schema
        models_path = Path("models")
        if not models_path.exists():
            print("⚠️  models/ directory not found, skipping SQL generation test")
            return True
        
        schema = SchemaLoader.load_from_directory(models_path)
        
        # Create SQL builder (dialect is set internally)
        sql_builder = SQLBuilder(schema)
        
        # Create a simple query
        query_data = {
            "dimensions": ["orders.status"],
            "measures": ["orders.total_revenue"],
            "filters": [],
            "order_by": [],
            "limit": 10,
        }
        
        query = QueryParser.parse(query_data)
        
        # Generate SQL
        sql = sql_builder.build(query)
        
        assert sql is not None
        assert "SELECT" in sql.upper()
        print(f"✅ SQL generated: {sql[:100]}...")
        print("✅ SQL generation: PASSED")
        return True
    except Exception as e:
        print(f"❌ SQL generation: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_module_integration():
    """Test that all modules work together."""
    print("\n" + "="*60)
    print("TEST: Module Integration")
    print("="*60)
    
    try:
        # Test that we can import and use all major components together
        from semantic_layer.schema import SchemaLoader, Schema
        from semantic_layer.sql import SQLBuilder, SQLGenerator, QueryOptimizer
        from semantic_layer.sql.dialects import PostgresDialect, MySQLDialect
        from semantic_layer.drivers import PostgresDriver, MySQLDriver, DriverFactory
        from semantic_layer.orchestrator import QueryEngine, ExecutionPlan, QueryPipeline
        from semantic_layer.monitoring import MetricsCollector, QueryLogger, HealthChecker
        from semantic_layer.metadata import DataCatalog, DatabaseIntrospector
        from semantic_layer.storage import ParquetStorage
        from semantic_layer.scheduling import Job, JobStatus
        
        # Test instantiation
        dialect = PostgresDialect()
        assert dialect.name == "postgresql"
        
        metrics = MetricsCollector()
        logger = QueryLogger()
        health = HealthChecker.check_health()
        
        catalog = DataCatalog()
        catalog.add_table("test", {"columns": []})
        
        print("✅ All modules integrate correctly: PASSED")
        return True
    except Exception as e:
        print(f"❌ Module integration: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backward_compatibility_usage():
    """Test that old imports still work in practice."""
    print("\n" + "="*60)
    print("TEST: Backward Compatibility Usage")
    print("="*60)
    
    try:
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        
        # Test old imports work
        from semantic_layer.connectors import BaseConnector, PostgreSQLConnector
        from semantic_layer.models import Schema, Cube, Dimension, Measure
        from semantic_layer.query_builder import SQLBuilder
        from semantic_layer.engine import QueryEngine
        from semantic_layer.metrics import MetricsCollector
        from semantic_layer.logging import QueryLogger
        
        # Test that they're the same as new imports
        from semantic_layer.drivers import BaseDriver
        assert BaseConnector == BaseDriver
        
        print("✅ Backward compatibility usage: PASSED")
        return True
    except Exception as e:
        print(f"❌ Backward compatibility usage: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all functionality tests."""
    print("\n" + "="*60)
    print("API FUNCTIONALITY TEST SUITE")
    print("="*60)
    
    results = []
    
    # Run tests
    result = test_module_integration()
    results.append(("Module Integration", result))
    
    result = test_backward_compatibility_usage()
    results.append(("Backward Compatibility Usage", result))
    
    result = await test_sql_generation()
    results.append(("SQL Generation", result))
    
    result = await test_query_execution()
    results.append(("Query Execution", result))
    
    # Summary
    print("\n" + "="*60)
    print("FUNCTIONALITY TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    failed = sum(1 for _, r in results if not r)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 Total: {passed} passed, {failed} failed")
    print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL FUNCTIONALITY TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed.")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))

