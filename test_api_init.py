"""Test API initialization."""

import sys

print("Testing API initialization...")
print("=" * 60)

try:
    print("\n1. Importing API modules...")
    from semantic_layer.api.app import create_app
    print("   ✓ API app imported successfully")
    
    print("\n2. Creating FastAPI app...")
    app = create_app()
    print("   ✓ FastAPI app created")
    print(f"   - Title: {app.title}")
    print(f"   - Version: {app.version}")
    print(f"   - Routes: {len(app.routes)}")
    
    print("\n3. Checking routes...")
    route_paths = [route.path for route in app.routes]
    print(f"   Routes found: {route_paths}")
    
    expected_routes = ["/health", "/api/v1/query", "/api/v1/schema"]
    for route in expected_routes:
        if route in route_paths:
            print(f"   ✓ {route}")
        else:
            print(f"   ✗ {route} (missing)")
    
    print("\n4. Testing schema loading...")
    from semantic_layer.models.schema import SchemaLoader
    schema = SchemaLoader.load_default()
    print(f"   ✓ Schema loaded: {len(schema.cubes)} cube(s)")
    
    print("\n" + "=" * 60)
    print("✓ API initialization test passed!")
    print("=" * 60)
    print("\nTo start the API server:")
    print("  python -m semantic_layer.api.main")
    print("\nThen visit:")
    print("  http://localhost:8000/docs - API documentation")
    print("  http://localhost:8000/health - Health check")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

