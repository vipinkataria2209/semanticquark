"""FastAPI application."""

from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, Union, List

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from semantic_layer.auth.base import BaseAuth, SecurityContext
from semantic_layer.auth.jwt_auth import JWTAuth
from semantic_layer.auth.api_key_auth import APIKeyAuth
from semantic_layer.cache.base import BaseCache
from semantic_layer.cache.memory import MemoryCache
from semantic_layer.cache.redis_cache import RedisCache
from semantic_layer.config import get_settings
from semantic_layer.drivers.base_driver import BaseDriver, ConnectionConfig
from semantic_layer.orchestrator import QueryEngine
from semantic_layer.exceptions import SemanticLayerError
from semantic_layer.schema import Schema, SchemaLoader
from semantic_layer.api.middleware import get_security_context, check_authorization
from semantic_layer.api.graphql import create_graphql_router
from semantic_layer.api.sql_api import execute_sql_query, SQLQueryRequest
from semantic_layer.monitoring import QueryLogger, MetricsCollector
from semantic_layer.sql import SQLBuilder
from semantic_layer.utils.file_watcher import FileWatcher
from semantic_layer.pre_aggregations.manager import PreAggregationManager
from semantic_layer.pre_aggregations.storage import DatabasePreAggregation
from semantic_layer.pre_aggregations.scheduler import PreAggregationScheduler
from semantic_layer.pre_aggregations.base import PreAggregationDefinition

# Import PostgreSQL driver conditionally
try:
    from semantic_layer.drivers import PostgresDriver
except ImportError:
    PostgresDriver = None


# Global state
query_engine: QueryEngine | None = None
schema: Schema | None = None
cache: Optional[BaseCache] = None
auth: Optional[BaseAuth] = None
connector: Optional[BaseDriver] = None
file_watcher: Optional[FileWatcher] = None
query_logger: Optional[QueryLogger] = None
metrics_collector: Optional[MetricsCollector] = None
pre_aggregation_manager: Optional[PreAggregationManager] = None
pre_aggregation_scheduler: Optional[PreAggregationScheduler] = None


def register_pre_aggregations() -> None:
    """Register pre-aggregations from schema."""
    global pre_aggregation_manager, schema
    if not pre_aggregation_manager or not schema:
        return
    
    # Clear existing registrations
    pre_aggregation_manager._definitions.clear()
    
    # Register pre-aggregations from all cubes
    for cube in schema.cubes.values():
        if cube.pre_aggregations:
            for pre_agg_data in cube.pre_aggregations:
                definition = PreAggregationDefinition(
                    name=pre_agg_data.get("name", f"{cube.name}_{len(pre_aggregation_manager._definitions)}"),
                    cube=cube.name,
                    dimensions=pre_agg_data.get("dimensions", []),
                    measures=pre_agg_data.get("measures", []),
                    time_dimension=pre_agg_data.get("time_dimension"),
                    granularity=pre_agg_data.get("granularity"),
                    refresh_key=pre_agg_data.get("refresh_key"),
                )
                pre_aggregation_manager.register(definition)
                print(f"Registered pre-aggregation: {definition.name} for cube {cube.name}")


def reload_schema() -> None:
    """Reload schema from files."""
    global schema, query_engine
    try:
        settings = get_settings()
        schema = SchemaLoader.load_default()
        if query_engine:
            query_engine.schema = schema
            query_engine.sql_builder = SQLBuilder(schema)
        register_pre_aggregations()
        print(f"Schema reloaded: {len(schema.cubes)} cubes")
    except Exception as e:
        print(f"Failed to reload schema: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    global query_engine, schema, cache, auth, connector, file_watcher, query_logger
    global pre_aggregation_manager, pre_aggregation_scheduler

    # Startup
    settings = get_settings()
    
    # Initialize query logger
    query_logger = QueryLogger(enabled=True)
    
    # Initialize metrics collector
    metrics_collector = MetricsCollector(enabled=True)

    # Load schema
    try:
        schema = SchemaLoader.load_default()
    except Exception as e:
        print(f"Warning: Failed to load schema: {e}")
        schema = Schema()

    # Initialize cache
    if settings.cache_enabled:
        if settings.cache_type == "redis":
            try:
                cache = RedisCache(redis_url=settings.redis_url)
                await cache.connect()
                print("Redis cache connected")
            except Exception as e:
                print(f"Warning: Failed to connect to Redis, using memory cache: {e}")
                cache = MemoryCache()
        else:
            cache = MemoryCache()
            print("Using in-memory cache")
    else:
        cache = None

    # Initialize authentication
    if settings.auth_enabled:
        if settings.auth_type == "jwt":
            auth = JWTAuth(secret=settings.jwt_secret, algorithm=settings.jwt_algorithm)
        elif settings.auth_type == "api_key":
            # API keys would be loaded from config/database
            auth = APIKeyAuth(api_keys={})
        else:
            auth = None
        app.state.auth = auth
        print(f"Authentication enabled: {settings.auth_type}")
    else:
        auth = None
        app.state.auth = None

    # Initialize connector
    if PostgresDriver is None:
        raise RuntimeError(
            "PostgreSQL driver not available. Install database dependencies: "
            "pip install asyncpg sqlalchemy"
        )
    
    conn_config = ConnectionConfig(
        url=settings.database_url_async,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
    )
    connector = PostgresDriver(conn_config)
    await connector.connect()
    
    # Store connector in app state for SQL API
    app.state.connector = connector

    # Initialize pre-aggregation storage and manager
    if settings.pre_aggregations_enabled:
        try:
            pre_agg_storage = DatabasePreAggregation(connector)
            pre_aggregation_manager = PreAggregationManager(
                schema,
                connector,
                storage=pre_agg_storage,
            )
            # Register pre-aggregations from schema
            register_pre_aggregations()
            
            # Initialize scheduler
            pre_aggregation_scheduler = PreAggregationScheduler(
                pre_aggregation_manager,
                connector,
            )
            await pre_aggregation_scheduler.start()
            print("Pre-aggregations enabled")
        except Exception as e:
            print(f"Warning: Pre-aggregations not available: {e}")
            pre_aggregation_manager = None
            pre_aggregation_scheduler = None
    else:
        pre_aggregation_manager = None
        pre_aggregation_scheduler = None

    # Initialize query engine with cache, logger, metrics, and pre-aggregations
    query_engine = QueryEngine(
        schema,
        connector,
        cache=cache,
        cache_ttl=settings.cache_ttl,
        query_logger=query_logger,
        pre_aggregation_manager=pre_aggregation_manager,
        metrics_collector=metrics_collector,
    )
    
    # Store query_engine in app state for GraphQL
    app.state.query_engine = query_engine

    # Add GraphQL router if available
    try:
        graphql_router = create_graphql_router(query_engine)
        if graphql_router:
            app.include_router(graphql_router, prefix="/graphql", tags=["graphql"])
            print("GraphQL API enabled at /graphql")
        else:
            # Check if it's an import issue
            from semantic_layer.api.graphql import _graphql_import_error
            if _graphql_import_error:
                print(f"⚠️  GraphQL not available: {_graphql_import_error}")
                print("   Install with: pip install strawberry-graphql[fastapi]")
            else:
                print("⚠️  GraphQL router not created (strawberry-graphql may not be installed)")
    except Exception as e:
        print(f"⚠️  GraphQL not available: {e}")
        import traceback
        traceback.print_exc()

    # Start file watcher for hot reload (development mode)
    if settings.api_debug:
        try:
            file_watcher = FileWatcher(settings.models_path, lambda p: reload_schema())
            file_watcher.start()
            print(f"Hot reload enabled for {settings.models_path}")
        except Exception as e:
            print(f"File watcher not available: {e}")

    yield

    # Shutdown
    if pre_aggregation_scheduler:
        await pre_aggregation_scheduler.stop()
    await connector.disconnect()
    if cache and hasattr(cache, "disconnect"):
        await cache.disconnect()
    if file_watcher:
        file_watcher.stop()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="SemanticQuark API",
        description="SemanticQuark - The Fundamental Building Block for Semantic Analytics. Python-based semantic layer platform.",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request models
    class QueryRequest(BaseModel):
        """Query request model."""

        dimensions: list[str] = []
        measures: list[str] = []
        filters: list[Dict[str, Any]] = []
        timeDimensions: list[Dict[str, Any]] = []  # Support timeDimensions
        order_by: list[Dict[str, Any]] = []
        limit: int | None = None
        offset: int | None = None

    # Error handler
    @app.exception_handler(SemanticLayerError)
    async def semantic_layer_error_handler(request: Request, exc: SemanticLayerError):
        """Handle semantic layer errors."""
        raise HTTPException(
            status_code=400,
            detail={"message": exc.message, "details": exc.details},
        )

    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "schema_loaded": schema is not None and len(schema.cubes) > 0}

    # Query endpoint
    @app.post("/api/v1/query")
    async def query(
        request: Union[QueryRequest, List[QueryRequest]],
        security_context: Optional[SecurityContext] = Depends(get_security_context),
    ):
        """Execute a semantic query or multiple queries (blending query).
        
        Supports:
        - Single query: {"dimensions": [...], "measures": [...]}
        - Blending query: [{"dimensions": [...]}, {"measures": [...]}]
        """
        if query_engine is None:
            raise HTTPException(status_code=503, detail="Query engine not initialized")

        from semantic_layer.query.parser import QueryParser

        # Check if array (blending query)
        if isinstance(request, list):
            # Blending query - execute multiple queries
            results = []
            for query_req in request:
                # Check authorization for each query
                if security_context:
                    await check_authorization(query_req, "query", "execute")
                
                # Parse and execute each query
                query_obj = QueryParser.parse(query_req.dict())
                user_context = security_context.to_dict() if security_context else None
                result = await query_engine.execute(query_obj, user_context=user_context)
                results.append(result)
            
            # Return array of results
            return {"data": results, "blending_query": True}
        
        # Single query (regular or compare date range)
        # Check authorization
        if security_context:
            await check_authorization(request, "query", "execute")

        # Parse request
        query_obj = QueryParser.parse(request.dict())

        # Execute query with security context
        user_context = security_context.to_dict() if security_context else None
        result = await query_engine.execute(query_obj, user_context=user_context)

        return result

    # Schema endpoint
    @app.get("/api/v1/schema")
    async def get_schema(
        request: Request,
        security_context: Optional[SecurityContext] = Depends(get_security_context),
    ):
        """Get schema information."""
        if schema is None:
            raise HTTPException(status_code=503, detail="Schema not loaded")

        # Check authorization
        if security_context:
            await check_authorization(request, "schema", "read")

        return {
            "cubes": {
                name: {
                    "name": cube.name,
                    "table": cube.table,
                    "dimensions": list(cube.dimensions.keys()),
                    "measures": list(cube.measures.keys()),
                }
                for name, cube in schema.cubes.items()
            }
        }

    # SQL API endpoint
    @app.post("/api/v1/sql")
    async def sql_query(
        request: Request,
        sql_request: SQLQueryRequest,
        security_context: Optional[SecurityContext] = Depends(get_security_context),
    ):
        """Execute raw SQL query."""
        # Check authorization
        if security_context:
            await check_authorization(request, "sql", "execute")
        
        return await execute_sql_query(request, sql_request, security_context)

    # Query logs endpoint
    @app.get("/api/v1/logs")
    async def get_logs(
        request: Request,
        limit: int = 100,
        security_context: Optional[SecurityContext] = Depends(get_security_context),
    ):
        """Get query logs."""
        if security_context:
            await check_authorization(request, "logs", "read")
        
        if query_logger:
            return {"logs": query_logger.get_logs(limit=limit)}
        return {"logs": []}

    # Reload schema endpoint
    @app.post("/api/v1/reload")
    async def reload_schema_endpoint(
        request: Request,
        security_context: Optional[SecurityContext] = Depends(get_security_context),
    ):
        """Reload schema from files."""
        if security_context:
            await check_authorization(request, "schema", "write")
        
        reload_schema()
        return {"status": "reloaded", "cubes": len(schema.cubes) if schema else 0}

    # Metrics endpoint
    @app.get("/api/v1/metrics")
    async def get_metrics(
        request: Request,
        security_context: Optional[SecurityContext] = Depends(get_security_context),
    ):
        """Get system metrics."""
        if security_context:
            await check_authorization(request, "metrics", "read")
        
        if metrics_collector:
            return metrics_collector.get_stats()
        return {}

    # Pre-aggregations endpoints
    @app.get("/api/v1/pre-aggregations")
    async def list_pre_aggregations(
        request: Request,
        security_context: Optional[SecurityContext] = Depends(get_security_context),
    ):
        """List all pre-aggregations."""
        if security_context:
            await check_authorization(request, "pre_aggregations", "read")
        
        if not pre_aggregation_manager:
            return {"pre_aggregations": []}
        
        return {
            "pre_aggregations": [
                {
                    "name": name,
                    "cube": defn.cube,
                    "dimensions": defn.dimensions,
                    "measures": defn.measures,
                }
                for name, defn in pre_aggregation_manager._definitions.items()
            ]
        }

    @app.post("/api/v1/pre-aggregations/{name}/refresh")
    async def refresh_pre_aggregation(
        name: str,
        request: Request,
        security_context: Optional[SecurityContext] = Depends(get_security_context),
    ):
        """Manually refresh a pre-aggregation."""
        if security_context:
            await check_authorization(request, "pre_aggregations", "write")
        
        if not pre_aggregation_scheduler:
            raise HTTPException(status_code=503, detail="Pre-aggregations not enabled")
        
        try:
            await pre_aggregation_scheduler.refresh_now(name)
            return {"status": "refreshed", "name": name}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    return app

