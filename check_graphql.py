#!/usr/bin/env python3
"""Diagnostic script to check GraphQL availability."""

import sys
from pathlib import Path

print("=" * 60)
print("GraphQL Availability Diagnostic")
print("=" * 60)
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path[:3]}...")
print()

# Try importing strawberry
print("Testing strawberry-graphql import...")
try:
    from strawberry import Schema as StrawberrySchema
    from strawberry.fastapi import GraphQLRouter
    import strawberry
    print("✅ strawberry-graphql imports successfully!")
    print(f"   Strawberry version: {getattr(strawberry, '__version__', 'unknown')}")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print()
    print("Troubleshooting:")
    print("1. Check if strawberry-graphql is installed:")
    print("   pip show strawberry-graphql")
    print()
    print("2. Install it if missing:")
    print("   pip install 'strawberry-graphql[fastapi]>=0.200.0'")
    print()
    print("3. If using a virtual environment, ensure it's activated")
    sys.exit(1)

# Try importing semantic_layer GraphQL module
print()
print("Testing semantic_layer.api.graphql import...")
try:
    # Add project root to path
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    from semantic_layer.api.graphql import GRAPHQL_AVAILABLE, _graphql_import_error
    print(f"✅ semantic_layer.api.graphql imported successfully!")
    print(f"   GRAPHQL_AVAILABLE: {GRAPHQL_AVAILABLE}")
    if _graphql_import_error:
        print(f"   Import error: {_graphql_import_error}")
    else:
        print("   No import errors")
except Exception as e:
    print(f"❌ Failed to import semantic_layer.api.graphql: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 60)
print("✅ All checks passed! GraphQL should be available.")
print("=" * 60)

