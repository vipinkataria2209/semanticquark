# Foundational Components Guide - Python Semantic Layer Platform

This guide outlines how to build the foundational components for a Cube.js-like semantic layer platform in Python.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
│         (BI Tools, Dashboards, Custom Apps, APIs)            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ REST/GraphQL/SQL APIs
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    API Layer (FastAPI)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  REST    │  │ GraphQL  │  │   SQL    │  │   MDX    │   │
│  │  API     │  │   API    │  │   API    │  │   API    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ Query Requests
                        │
┌───────────────────────▼─────────────────────────────────────┐
│              Query Engine & Orchestration                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Query Parser → Query Optimizer → Query Executor    │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
│   Semantic   │ │   Cache     │ │  Security  │
│    Layer     │ │   Layer     │ │   Layer    │
│  (Models)    │ │  (Redis)    │ │  (RLS/ACL) │
└───────┬──────┘ └─────────────┘ └────────────┘
        │
        │
┌───────▼──────────────────────────────────────┐
│         Data Source Connectors                │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐│
│  │Postgres│ │Snowflake│ │BigQuery│ │  ...   ││
│  └────────┘ └────────┘ └────────┘ └────────┘│
└──────────────────────────────────────────────┘
```

## Core Foundational Components

### 1. Semantic Layer (Data Model Engine)

**Purpose**: Define and manage data models (cubes, dimensions, measures, relationships)

**Key Responsibilities**:
- Load and parse model definitions (YAML/JSON)
- Validate model schemas
- Resolve relationships and joins
- Generate SQL from semantic queries

**Implementation Structure**:
```
semantic_layer/
├── __init__.py
├── models/
│   ├── cube.py          # Cube definition
│   ├── dimension.py     # Dimension definition
│   ├── measure.py       # Measure definition
│   ├── relationship.py  # Relationships/joins
│   └── schema.py        # Schema loader/parser
├── parser/
│   ├── yaml_parser.py   # Parse YAML model files
│   ├── json_parser.py   # Parse JSON model files
│   └── validator.py     # Validate model definitions
└── query_builder/
    ├── sql_builder.py   # Convert semantic queries to SQL
    └── query_optimizer.py # Optimize generated SQL
```

**Technology Stack**:
- **Pydantic**: For model validation and type safety
- **PyYAML**: For parsing YAML model definitions
- **SQLAlchemy Core**: For SQL generation (not ORM, just SQL building)

### 2. Query Engine

**Purpose**: Parse, validate, optimize, and execute queries

**Key Responsibilities**:
- Parse incoming query requests (JSON/GraphQL/SQL)
- Validate queries against data models
- Optimize queries (join elimination, predicate pushdown)
- Execute queries against data sources
- Handle query result formatting

**Implementation Structure**:
```
query_engine/
├── __init__.py
├── parser/
│   ├── rest_parser.py      # Parse REST API queries
│   ├── graphql_parser.py   # Parse GraphQL queries
│   ├── sql_parser.py       # Parse SQL queries
│   └── query_ast.py        # Query Abstract Syntax Tree
├── optimizer/
│   ├── join_optimizer.py   # Optimize joins
│   ├── predicate_pushdown.py # Push filters down
│   └── aggregation_optimizer.py # Optimize aggregations
├── executor/
│   ├── base_executor.py    # Base executor interface
│   ├── sql_executor.py     # Execute SQL queries
│   └── result_formatter.py # Format query results
└── query_context.py        # Query execution context
```

**Technology Stack**:
- **Strawberry GraphQL**: For GraphQL API
- **sqlparse**: For SQL parsing
- **asyncpg/aiomysql**: For async database queries

### 3. Data Source Connectors

**Purpose**: Abstract different data sources behind a common interface

**Key Responsibilities**:
- Establish connections to various databases
- Execute queries
- Handle connection pooling
- Support async operations
- Map database-specific SQL dialects

**Implementation Structure**:
```
connectors/
├── __init__.py
├── base.py              # Base connector interface
├── postgresql.py        # PostgreSQL connector
├── mysql.py             # MySQL connector
├── snowflake.py         # Snowflake connector
├── bigquery.py          # BigQuery connector
├── redshift.py          # Redshift connector
├── sqlite.py            # SQLite connector
└── connection_pool.py   # Connection pooling
```

**Technology Stack**:
- **SQLAlchemy**: For database abstraction
- **asyncpg**: For async PostgreSQL
- **aiomysql**: For async MySQL
- **snowflake-connector-python**: For Snowflake
- **google-cloud-bigquery**: For BigQuery
- **boto3**: For AWS services (Redshift, Athena)

### 4. Caching Layer

**Purpose**: Cache query results and pre-aggregations for performance

**Key Responsibilities**:
- Cache query results with TTL
- Store pre-aggregated data
- Invalidate cache on data updates
- Support distributed caching

**Implementation Structure**:
```
cache/
├── __init__.py
├── cache_manager.py     # Main cache manager
├── redis_cache.py       # Redis implementation
├── memory_cache.py      # In-memory cache (dev/testing)
├── pre_aggregation.py   # Pre-aggregation storage
└── cache_key_builder.py # Build cache keys from queries
```

**Technology Stack**:
- **Redis**: For distributed caching
- **aioredis**: For async Redis operations
- **Apache Parquet**: For storing pre-aggregations
- **DuckDB**: For fast querying of pre-aggregations

### 5. Security & Access Control

**Purpose**: Implement row-level security, column-level security, and access control

**Key Responsibilities**:
- Authenticate users/API keys
- Apply row-level security filters
- Enforce column-level access
- Support multi-tenancy
- Audit logging

**Implementation Structure**:
```
security/
├── __init__.py
├── authentication.py    # User/API key authentication
├── authorization.py     # Access control logic
├── rls.py              # Row-level security
├── acl.py              # Access control lists
├── context.py          # Security context (user, tenant)
└── audit.py            # Audit logging
```

**Technology Stack**:
- **PyJWT**: For JWT token handling
- **python-jose**: For JWT validation
- **passlib**: For password hashing (if needed)

### 6. API Layer

**Purpose**: Expose REST, GraphQL, and SQL APIs

**Key Responsibilities**:
- Handle HTTP requests
- Parse and validate API requests
- Route to query engine
- Format responses
- Handle errors

**Implementation Structure**:
```
api/
├── __init__.py
├── rest/
│   ├── routes.py        # REST API routes
│   ├── schemas.py       # Request/response schemas
│   └── handlers.py      # Request handlers
├── graphql/
│   ├── schema.py        # GraphQL schema
│   ├── resolvers.py     # GraphQL resolvers
│   └── types.py         # GraphQL types
├── sql/
│   ├── routes.py        # SQL API routes
│   └── handlers.py      # SQL query handlers
└── middleware/
    ├── auth.py          # Authentication middleware
    ├── logging.py       # Request logging
    └── error_handler.py # Error handling
```

**Technology Stack**:
- **FastAPI**: For REST API (async, auto-docs)
- **Strawberry GraphQL**: For GraphQL API
- **Pydantic**: For request/response validation

### 7. Pre-Aggregation Engine

**Purpose**: Automatically pre-aggregate data for faster queries

**Key Responsibilities**:
- Identify queries that benefit from pre-aggregation
- Create and maintain pre-aggregation tables
- Route queries to pre-aggregations when available
- Incrementally update pre-aggregations

**Implementation Structure**:
```
pre_aggregation/
├── __init__.py
├── manager.py           # Pre-aggregation manager
├── builder.py           # Build pre-aggregation queries
├── scheduler.py         # Schedule pre-aggregation builds
├── storage.py           # Store pre-aggregations
└── router.py            # Route queries to pre-aggregations
```

**Technology Stack**:
- **Celery**: For background jobs
- **Apache Parquet**: For storage
- **DuckDB**: For querying pre-aggregations

## Project Structure

```
semantic_layer_analytics/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── docker-compose.yml
├── semantic_layer/
│   ├── __init__.py
│   ├── models/          # Data model definitions
│   ├── parser/          # Model parsers
│   └── query_builder/   # SQL generation
├── query_engine/
│   ├── __init__.py
│   ├── parser/          # Query parsers
│   ├── optimizer/       # Query optimization
│   └── executor/        # Query execution
├── connectors/
│   ├── __init__.py
│   └── [database].py    # Database connectors
├── cache/
│   ├── __init__.py
│   └── [cache_backend].py
├── security/
│   ├── __init__.py
│   ├── authentication.py
│   └── authorization.py
├── api/
│   ├── __init__.py
│   ├── rest/
│   ├── graphql/
│   └── sql/
├── pre_aggregation/
│   ├── __init__.py
│   └── manager.py
├── config/
│   ├── __init__.py
│   └── settings.py      # Configuration management
├── models/              # YAML/JSON model files
│   ├── cubes/
│   └── schemas/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
└── scripts/
    ├── migrate.py       # Model migration scripts
    └── seed.py          # Seed data
```

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Goal**: Get basic semantic layer working with simple queries

1. **Set up project structure**
   - Initialize Python project with FastAPI
   - Set up dependency management (poetry/pip)
   - Configure development environment

2. **Build semantic layer core**
   - Define Pydantic models for Cube, Dimension, Measure
   - Create YAML parser for model definitions
   - Implement basic schema validation

3. **Build basic query engine**
   - Create REST API endpoint
   - Parse simple queries (dimensions + measures)
   - Generate basic SQL queries

4. **Build database connector**
   - Implement PostgreSQL connector
   - Support async queries
   - Connection pooling

5. **Test with simple model**
   - Create sample data model
   - Test basic query execution
   - Verify SQL generation

### Phase 2: Core Features (Weeks 3-4)

**Goal**: Add essential features for production use

1. **Enhance query engine**
   - Support filters/where clauses
   - Support aggregations (sum, count, avg)
   - Support grouping by dimensions
   - Add query optimization

2. **Add caching**
   - Implement Redis caching
   - Cache query results with TTL
   - Cache key generation

3. **Add security**
   - API key authentication
   - Basic row-level security
   - Security context management

4. **Add GraphQL API**
   - Define GraphQL schema
   - Implement resolvers
   - Test GraphQL queries

### Phase 3: Advanced Features (Weeks 5-6)

**Goal**: Add performance and advanced capabilities

1. **Pre-aggregations**
   - Identify pre-aggregation opportunities
   - Build pre-aggregation tables
   - Route queries to pre-aggregations

2. **More data sources**
   - Add Snowflake connector
   - Add BigQuery connector
   - Test with multiple sources

3. **Query optimization**
   - Join optimization
   - Predicate pushdown
   - Query result streaming

4. **Monitoring**
   - Query logging
   - Performance metrics
   - Health checks

### Phase 4: Production Ready (Weeks 7-8)

**Goal**: Make it production-ready

1. **Error handling**
   - Comprehensive error handling
   - Error messages and codes
   - Error logging

2. **Documentation**
   - API documentation
   - Model definition guide
   - Deployment guide

3. **Testing**
   - Unit tests
   - Integration tests
   - Load testing

4. **Deployment**
   - Docker containerization
   - Kubernetes manifests
   - CI/CD pipeline

## Technology Stack Summary

### Core Framework
- **FastAPI**: Modern, fast web framework
- **Pydantic**: Data validation and settings
- **SQLAlchemy Core**: SQL generation (not ORM)

### Database & Connectors
- **asyncpg**: Async PostgreSQL
- **aiomysql**: Async MySQL
- **snowflake-connector-python**: Snowflake
- **google-cloud-bigquery**: BigQuery
- **boto3**: AWS services

### Caching
- **aioredis**: Async Redis client
- **DuckDB**: Fast analytical queries
- **Apache Parquet**: Columnar storage

### GraphQL
- **Strawberry GraphQL**: GraphQL framework

### Background Jobs
- **Celery**: Distributed task queue
- **Redis**: Celery broker

### Testing
- **pytest**: Testing framework
- **pytest-asyncio**: Async testing
- **httpx**: HTTP client for testing

### Development
- **black**: Code formatting
- **ruff**: Fast linter
- **mypy**: Type checking
- **pre-commit**: Git hooks

## Key Design Decisions

### 1. Async-First Architecture
- Use `async/await` throughout for better concurrency
- All database operations should be async
- API endpoints should be async

### 2. Schema-First Approach
- Models defined in YAML/JSON files
- Version control friendly
- Easy to validate and test

### 3. Pluggable Connectors
- Each database has its own connector
- Common interface for all connectors
- Easy to add new data sources

### 4. Query Optimization
- Optimize at multiple levels:
  - Semantic layer (join elimination)
  - SQL generation (predicate pushdown)
  - Database (use indexes)

### 5. Caching Strategy
- Cache at query level (full results)
- Cache at pre-aggregation level (partial results)
- Smart cache invalidation

## Next Steps

1. **Start with Phase 1**: Set up project and build basic semantic layer
2. **Create sample model**: Define a simple cube with dimensions and measures
3. **Test end-to-end**: Query → Parse → Generate SQL → Execute → Return results
4. **Iterate**: Add features incrementally based on requirements

## Example: Basic Query Flow

```
1. Client sends REST request:
   POST /api/v1/query
   {
     "dimensions": ["users.country", "users.created_at"],
     "measures": ["orders.total_revenue"],
     "filters": [{"dimension": "orders.status", "operator": "equals", "values": ["completed"]}]
   }

2. API Layer:
   - Validates request schema
   - Extracts security context (user, tenant)
   - Passes to query engine

3. Query Engine:
   - Parses query
   - Loads semantic models
   - Applies security filters (RLS)
   - Checks cache
   - Generates SQL

4. SQL Generation:
   - Resolves relationships (users → orders)
   - Builds JOIN clauses
   - Applies filters
   - Adds aggregations
   - Generates GROUP BY

5. Execution:
   - Gets database connection
   - Executes SQL
   - Formats results
   - Caches results

6. Response:
   - Returns JSON response
   - Includes metadata (query time, cache hit, etc.)
```

This foundation provides a solid base for building a production-ready semantic layer platform in Python.

