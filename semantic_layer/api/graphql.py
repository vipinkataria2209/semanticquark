"""GraphQL API implementation."""

from typing import Any, Dict, List, Optional

try:
    from strawberry import Schema as StrawberrySchema
    from strawberry.fastapi import GraphQLRouter
    import strawberry
    GRAPHQL_AVAILABLE = True
    _graphql_import_error = None
except ImportError as e:
    GRAPHQL_AVAILABLE = False
    StrawberrySchema = None
    GraphQLRouter = None
    strawberry = None
    _graphql_import_error = str(e)

from semantic_layer.orchestrator import QueryEngine
from semantic_layer.exceptions import ExecutionError
from semantic_layer.schema import Schema
from semantic_layer.query.parser import QueryParser
from semantic_layer.query.query import Query


if GRAPHQL_AVAILABLE:
    @strawberry.type
    class QueryMeta:
        """Query metadata."""
        execution_time_ms: float
        row_count: int
        cache_hit: bool
        sql: Optional[str] = None

    @strawberry.type
    class QueryResult:
        """Query result."""
        data: str  # JSON string representation
        meta: QueryMeta

    @strawberry.input
    class FilterInput:
        """Filter input."""
        dimension: str
        operator: str
        values: List[str]

    @strawberry.input
    class OrderByInput:
        """Order by input."""
        dimension: str
        direction: str = "asc"

    @strawberry.input
    class QueryInput:
        """Query input."""
        dimensions: Optional[List[str]] = None
        measures: Optional[List[str]] = None
        filters: Optional[List[FilterInput]] = None
        order_by: Optional[List[OrderByInput]] = None
        limit: Optional[int] = None
        offset: Optional[int] = None

    @strawberry.type
    class QueryRoot:
        """GraphQL query root."""

        @strawberry.field
        async def query(
            self,
            info,
            dimensions: Optional[List[str]] = None,
            measures: Optional[List[str]] = None,
            filters: Optional[List[FilterInput]] = None,
            order_by: Optional[List[OrderByInput]] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
        ) -> QueryResult:
            """Execute a semantic query."""
            # Get query engine from context
            query_engine: QueryEngine = info.context.get("query_engine")
            if not query_engine:
                raise ExecutionError("Query engine not available")
            
            user_context: Optional[Dict[str, Any]] = info.context.get("user_context")
            
            # Convert GraphQL input to Query object
            filter_objs = []
            if filters:
                from semantic_layer.query.query import QueryFilter
                for f in filters:
                    filter_objs.append(
                        QueryFilter(
                            dimension=f.dimension,
                            operator=f.operator,
                            values=f.values,
                        )
                    )
            
            order_objs = []
            if order_by:
                from semantic_layer.query.query import QueryOrderBy
                for o in order_by:
                    order_objs.append(
                        QueryOrderBy(dimension=o.dimension, direction=o.direction)
                    )
            
            query = Query(
                dimensions=dimensions or [],
                measures=measures or [],
                filters=filter_objs,
                order_by=order_objs,
                limit=limit,
                offset=offset,
            )
            
            # Execute query
            result = await query_engine.execute(query, user_context=user_context)
            
            # Convert to GraphQL types
            import json
            meta = QueryMeta(
                execution_time_ms=result["meta"]["execution_time_ms"],
                row_count=result["meta"]["row_count"],
                cache_hit=result["meta"].get("cache_hit", False),
                sql=result["meta"].get("sql"),
            )
            
            # Convert data to JSON string for GraphQL
            data_json = json.dumps(result["data"])
            
            return QueryResult(data=data_json, meta=meta)

    def create_graphql_schema() -> Optional[StrawberrySchema]:
        """Create GraphQL schema."""
        if not GRAPHQL_AVAILABLE:
            return None
        return StrawberrySchema(query=QueryRoot)

    def create_graphql_router(
        query_engine: QueryEngine,
    ) -> Optional[GraphQLRouter]:
        """Create GraphQL router."""
        if not GRAPHQL_AVAILABLE:
            return None
        
        schema = create_graphql_schema()
        if not schema:
            return None
        
        # Create router with context - strawberry expects a callable that returns context
        def get_context():
            return {
                "query_engine": query_engine,
                "user_context": None
            }
        
        # GraphQLRouter expects schema and context_getter
        router = GraphQLRouter(schema=schema, context_getter=get_context)
        return router

else:

    def create_graphql_schema():
        """Create GraphQL schema (not available)."""
        # Return None instead of raising - allows app to start without GraphQL
        return None

    def create_graphql_router(query_engine: QueryEngine):
        """Create GraphQL router (not available)."""
        # Return None instead of raising - allows app to start without GraphQL
        # The error message will be logged in app.py
        return None

