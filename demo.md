# SemanticQuark Complete Application Guide - Demo

This document covers everything about SemanticQuark: from startup to request handling to query execution.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Application Startup Journey](#application-startup-journey)
3. [Query Engine Components](#query-engine-components)
4. [Request Handling Flow](#request-handling-flow)
5. [Deep Dive Examples](#deep-dive-examples)

---

# Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Application                        │
│                    (Tableau, Python)                        │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP Request (JSON Query)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Uvicorn ASGI Server                       │
│                  (Async request handler)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Application                       │
│  • /api/v1/query  • /api/v1/schema  • /api/v1/logs         │
│  • /api/v1/sql    • /api/v1/metrics  • /graphql            │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐  ┌──────────┐  ┌──────────────┐
    │Auth     │  │QueryParser│  │QueryEngine   │
    │Middleware│  │  (JSON→  │  │ (Orchestrate)│
    │         │  │ Query obj)│  │              │
    └─────────┘  └──────────┘  └──────┬───────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
    ┌─────────┐              ┌──────────────┐            ┌──────────────┐
    │Cache    │              │SQLBuilder    │            │PreAgg Manager│
    │(Redis/  │              │(Semantic→SQL)│            │(Pre-computed)│
    │Memory)  │              └──────┬───────┘            └──────┬───────┘
    └─────────┘                     │                          │
                                    ▼                          │
                            ┌──────────────┐                   │
                            │Connector     │◄──────────────────┘
                            │(PostgreSQL)  │
                            └──────┬───────┘
                                   │
                                   ▼
                            PostgreSQL Database
                            (Execute SQL Query)
                                   │
                                   ▼
                            ┌──────────────┐
                            │Query Results │
                            │ (Raw data)   │
                            └──────┬───────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
    ┌─────────┐            ┌──────────────┐         ┌──────────────┐
    │QueryLogger         │ResultFormatter│        │MetricsCollector│
    │(Audit trail)       │(Results→JSON) │        │(Performance)   │
    └─────────┘            └──────────────┘         └──────────────┘
                                   │
                                   ▼
                            ┌──────────────┐
                            │JSON Response │
                            │+ Metadata    │
                            └──────┬───────┘
                                   │ HTTP Response
                                   ▼
                            User Application
```

---

# Application Startup Journey

## Step 0: The Entry Point

```bash
python -m semantic_layer.api.main
```

### main.py Initialization:

```python
# semantic_layer/api/main.py
from semantic_layer.api.app import create_app
from semantic_layer.config import get_settings

app = create_app()  # ← Creates FastAPI instance

if __name__ == "__main__":
    settings = get_settings()  # ← Load configuration
    uvicorn.run(
        "semantic_layer.api.main:app",
        host=settings.api_host,      # "0.0.0.0"
        port=settings.api_port,      # 8000
        reload=settings.api_debug,   # Hot reload in dev
    )
```

---

## Step 0.5: Configuration Loading

Configuration comes from (in priority order):

### 1. Environment Variables (Highest Priority)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=5

# Cache
CACHE_ENABLED=true
CACHE_TYPE=redis  # or "memory"
CACHE_TTL=3600  # 1 hour
REDIS_URL=redis://localhost:6379

# Authentication
AUTH_ENABLED=false
AUTH_TYPE=jwt  # or "api_key"
JWT_SECRET=your-secret-key

# Pre-aggregations
PRE_AGGREGATIONS_ENABLED=true

# API
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true  # Hot reload enabled

# Models
MODELS_PATH=./models  # Where YAML cube definitions are
```

### 2. .env File (Fallback)

```
API_HOST=0.0.0.0
API_PORT=8000
CACHE_TTL=3600
```

### 3. Default Values (Final Fallback)

```python
api_host = "0.0.0.0"
api_port = 8000
cache_ttl = 3600
cache_type = "memory"
```

---

## Step 1-2: FastAPI App Creation & Uvicorn Start

### Create FastAPI App

```python
def create_app() -> FastAPI:
    app = FastAPI(
        title="SemanticQuark API",
        version="0.1.0",
        lifespan=lifespan,  # ← Special async context manager
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app
```

### Uvicorn Starts

Uvicorn ASGI server starts listening on `0.0.0.0:8000`

**At this point:**
- FastAPI app object exists
- ✗ No database connection
- ✗ No schema loaded
- ✗ No cache connected
- ✗ NOT ready for requests yet

---

## Step 3: STARTUP PHASE - The Main Event

When a connection arrives, Uvicorn triggers the `lifespan` context manager:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # === STARTUP PHASE (everything initializes here) ===
    
    yield  # ← Application is NOW ready to serve requests
    
    # === SHUTDOWN PHASE (cleanup happens here) ===
```

---

### 3.1: Initialize Monitoring Systems

```python
# Initialize query logger (tracks all queries)
query_logger = QueryLogger(enabled=True)

# Initialize metrics collector (performance stats)
metrics_collector = MetricsCollector(enabled=True)
```

**What they track:**
- Query execution time
- Cache hit/miss rate
- Error rate
- Pre-aggregation usage
- User activity

**Status:** ✓ Monitoring is ready

---

### 3.2: Load Schema from Files ⭐ CRITICAL

This is where **your data model** is defined.

```python
try:
    schema = SchemaLoader.load_default()
    # Loads from models_path (default: ./models)
except Exception as e:
    print(f"Warning: Failed to load schema: {e}")
    schema = Schema()  # Empty schema if loading fails
```

#### What SchemaLoader Does:

```
Step 1: Find all .yaml/.yml/.json files
        └─ models/
           ├── orders.yaml
           ├── customers.yaml
           └── products.yaml

Step 2: Parse each file
        └─ YAML → Python dict

Step 3: Compile to Python objects
        └─ SchemaCompiler converts to Cube objects

Step 4: Validate cubes
        └─ SchemaValidator checks for errors

Step 5: Build relationship graph
        └─ orders → customers → products (for JOINs)

Step 6: Return Schema object
        └─ schema.cubes = {
             "orders": Cube(...),
             "customers": Cube(...),
           }
```

#### Example Cube Definition (YAML):

```yaml
# models/orders.yaml
name: orders
table: public.orders

dimensions:
  id:
    type: number
    sql: id
    primary_key: true
    
  status:
    type: string
    sql: status
    description: Order status
    
  created_at:
    type: time
    sql: created_at
    description: Order creation date

measures:
  revenue:
    type: sum
    sql: amount
    format: "$0,0.00"
    
  order_count:
    type: count
    sql: id

relationships:
  customer:
    type: belongs_to
    cube: customers
    foreign_key: customer_id
    primary_key: id
```

**Result in Python:**

```python
schema.cubes["orders"] = Cube(
    name="orders",
    table="public.orders",
    dimensions={
        "id": Dimension(type="number", sql="id", primary_key=True),
        "status": Dimension(type="string", sql="status"),
        "created_at": Dimension(type="time", sql="created_at"),
    },
    measures={
        "revenue": Measure(type="sum", sql="amount"),
        "order_count": Measure(type="count", sql="id"),
    },
    relationships={
        "customer": Relationship(type="belongs_to", cube="customers", ...),
    }
)
```

**Status:** ✓ Schema loaded with X cubes, Y dimensions, Z measures

---

### 3.3: Initialize Cache

```python
if settings.cache_enabled:
    if settings.cache_type == "redis":
        try:
            cache = RedisCache(redis_url=settings.redis_url)
            await cache.connect()  # ← Async connection
            print("Redis cache connected")
        except Exception as e:
            print(f"Fallback to memory cache: {e}")
            cache = MemoryCache()
    else:
        cache = MemoryCache()
else:
    cache = None
```

#### Cache Behavior:

```
Request 1 (first time):
  └─ Query: "SELECT status, SUM(amount) FROM orders"
     ├─ Generate cache key: hash(query + user_context)
     ├─ Check cache: MISS
     ├─ Execute query on database: 500ms
     ├─ Store result in cache: (TTL=3600s)
     └─ Return result to user

Request 2 (same query, within 1 hour):
  └─ Query: "SELECT status, SUM(amount) FROM orders"
     ├─ Generate cache key: hash(query + user_context)
     ├─ Check cache: HIT ✓
     └─ Return cached result: 10ms (50x faster!)

Request 3 (after 1 hour cache TTL expires):
  └─ Query: "SELECT status, SUM(amount) FROM orders"
     ├─ Generate cache key: hash(query + user_context)
     ├─ Check cache: MISS (expired)
     ├─ Execute query on database: 500ms
     ├─ Store result in cache: (new TTL=3600s)
     └─ Return result to user
```

**Status:** ✓ Cache initialized (Redis or Memory)

---

### 3.4: Initialize Authentication

```python
if settings.auth_enabled:
    if settings.auth_type == "jwt":
        auth = JWTAuth(secret=settings.jwt_secret, algorithm="HS256")
    elif settings.auth_type == "api_key":
        auth = APIKeyAuth(api_keys={...})
    else:
        auth = None
    
    app.state.auth = auth
    print(f"Authentication enabled: {settings.auth_type}")
else:
    auth = None
    app.state.auth = None
```

#### How JWT Auth Works:

```
1. Client sends request with JWT token
   Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

2. Auth middleware intercepts
   ├─ Extract token from header
   ├─ Verify signature (using jwt_secret)
   ├─ Decode payload
   └─ Extract user info (user_id, permissions, etc.)

3. Create SecurityContext object
   └─ user_id: "alice@company.com"
      permissions: ["query:read", "schema:read"]
      role: "analyst"

4. Attach to request
   └─ request.security_context = SecurityContext(...)

5. Endpoint receives SecurityContext
   └─ Can check permissions, apply row-level security, etc.
```

**Status:** ✓ Authentication ready (JWT/API Key)

---

### 3.5: Initialize Database Connector ⭐ CRITICAL

```python
if PostgresDriver is None:
    raise RuntimeError(
        "PostgreSQL driver not available. "
        "Install: pip install asyncpg sqlalchemy"
    )

conn_config = ConnectionConfig(
    url=settings.database_url_async,  # postgresql+asyncpg://...
    pool_size=settings.database_pool_size,  # 10
    max_overflow=settings.database_max_overflow,  # 5
)

connector = PostgresDriver(conn_config)
await connector.connect()  # ← Async connection to DB

app.state.connector = connector
```

#### PostgreSQL Connection Pool:

```
Connection Pool (size=10, max_overflow=5):

┌──────────────────────────────────┐
│     Available Connections        │
│                                  │
│  [●] [●] [●] [●] [●]           │ ← 5 active (in use)
│  [ ] [ ] [ ] [ ] [ ]           │ ← 5 idle (available)
│                                  │
│  Max overflow: 5                 │ ← Can create 5 more if needed
│  Total possible: 15 connections  │
└──────────────────────────────────┘
       ↓ connections
   PostgreSQL
   Database
```

#### Why Connection Pooling?

```
Without Connection Pool:
  Request 1: Open connection (100ms) → Execute query (200ms) → Close (50ms) = 350ms
  Request 2: Open connection (100ms) → Execute query (200ms) → Close (50ms) = 350ms
  Request 3: Open connection (100ms) → Execute query (200ms) → Close (50ms) = 350ms
  Total: 1050ms (opening/closing connections is slow!)

With Connection Pool:
  Request 1: Get conn from pool (1ms) → Execute query (200ms) = 201ms
  Request 2: Get conn from pool (1ms) → Execute query (200ms) = 201ms
  Request 3: Get conn from pool (1ms) → Execute query (200ms) = 201ms
  Total: 603ms (connections reused!)
  
  Savings: 447ms (43% faster) ✓
```

**Status:** ✓ Connected to PostgreSQL with connection pool

---

### 3.6: Initialize Pre-Aggregations ⭐ PERFORMANCE LAYER

```python
if settings.pre_aggregations_enabled:
    try:
        # 1. Create storage backend (database)
        pre_agg_storage = DatabasePreAggregation(connector)
        
        # 2. Create manager
        pre_aggregation_manager = PreAggregationManager(
            schema,
            connector,
            storage=pre_agg_storage,
        )
        
        # 3. Register pre-aggregations from cube definitions
        register_pre_aggregations()
        
        # 4. Start scheduler to refresh pre-aggs periodically
        pre_aggregation_scheduler = PreAggregationScheduler(
            pre_aggregation_manager,
            connector,
        )
        await pre_aggregation_scheduler.start()
        
        print("Pre-aggregations enabled")
    except Exception as e:
        print(f"Warning: Pre-aggregations not available: {e}")
        pre_aggregation_manager = None
else:
    pre_aggregation_manager = None
```

#### Pre-Aggregation Example Definition (in Cube YAML):

```yaml
# In orders cube
pre_aggregations:
  - name: "revenue_by_category_daily"
    dimensions: ["category"]
    measures: ["revenue"]
    time_dimension: "created_at"
    granularity: "day"
    refresh_key:
      every_hour: true
```

#### Without Pre-Aggregation (5000ms):

```sql
SELECT 
  category,
  SUM(amount) as revenue
FROM orders
WHERE created_at >= '2024-01-01'
GROUP BY category;

-- Scans 100M rows ⚠️
-- Takes 5 seconds
-- Happens every time
```

#### With Pre-Aggregation (50ms):

```sql
-- Pre-computed table is created automatically
SELECT 
  category,
  SUM(revenue) as revenue
FROM revenue_by_category_daily
WHERE date >= '2024-01-01';

-- Scans 365 rows (1 per day)
-- Takes 50ms ✓ 100x faster!
```

#### How Pre-Agg Works:

```
Step 1: Query arrives
  └─ "Get revenue by category"

Step 2: Pre-aggregation manager checks
  └─ "Do we have a pre-agg that matches this query?"

Step 3: If match found
  ├─ Check if pre-agg table exists
  ├─ Check if it's fresh (within refresh window)
  └─ YES: Use pre-agg table!

Step 4: Generate SQL using pre-agg table
  └─ Query uses small table (100 rows instead of 100M rows)

Step 5: Much faster execution
  └─ 50ms instead of 5000ms ✓

Step 6: Scheduler periodically refreshes
  └─ Every day/hour: Recalculate pre-agg table
  └─ Keeps results fresh
```

**Status:** ✓ Pre-aggregations registered and scheduler started

---

### 3.7: Initialize QueryEngine ⭐ THE MAIN ORCHESTRATOR

```python
query_engine = QueryEngine(
    schema,                           # ✓ Schema loaded
    connector,                        # ✓ Database connected
    cache=cache,                      # ✓ Cache initialized
    cache_ttl=settings.cache_ttl,     # 3600 seconds
    query_logger=query_logger,        # ✓ Logger ready
    pre_aggregation_manager=pre_aggregation_manager,  # ✓ Pre-aggs ready
    metrics_collector=metrics_collector,  # ✓ Metrics ready
)

app.state.query_engine = query_engine
```

#### What QueryEngine Now Has:

- ✓ Connection to schema (knows all cubes/dimensions/measures)
- ✓ Connection to database (can execute SQL)
- ✓ Connection to cache (can store/retrieve results)
- ✓ Pre-aggregation manager (can use optimized tables)
- ✓ Logger (will audit all queries)
- ✓ Metrics (will track performance)

**Status:** ✓ QueryEngine fully operational

---

### 3.8: Add GraphQL Router (Optional)

```python
try:
    graphql_router = create_graphql_router(query_engine)
    if graphql_router:
        app.include_router(graphql_router, prefix="/graphql", tags=["graphql"])
        print("GraphQL API enabled at /graphql")
except Exception as e:
    print(f"Warning: GraphQL not available: {e}")
    print("   Install with: pip install strawberry-graphql[fastapi]")
```

**Status:** ✓ GraphQL API available (if strawberry-graphql installed)

---

### 3.9: Start File Watcher (Development Mode)

```python
if settings.api_debug:
    try:
        file_watcher = FileWatcher(
            settings.models_path,
            lambda p: reload_schema()  # Called when files change
        )
        file_watcher.start()
        print(f"Hot reload enabled for {settings.models_path}")
    except Exception as e:
        print(f"File watcher not available: {e}")
```

#### How Hot Reload Works:

```
Development Flow:
  ├─ Edit models/orders.yaml
  ├─ File watcher detects change
  ├─ Automatically calls reload_schema()
  ├─ Schema reloaded in memory
  └─ New cube definition available immediately
     (No server restart needed!)

Benefits:
  - Change cube definitions instantly
  - Test new dimensions/measures without restarting
  - Faster development cycle
```

**Status:** ✓ Hot reload enabled (development mode)

---

## Step 4: Application Ready! ✅

After `yield` in the lifespan context manager:

```python
yield  # ← APPLICATION IS NOW READY TO SERVE REQUESTS
```

All these systems operational:
- ✓ Configuration loaded
- ✓ Schema compiled from YAML files
- ✓ Database connected with connection pool
- ✓ Cache initialized (Redis or Memory)
- ✓ Authentication ready (JWT or API Key)
- ✓ Pre-aggregations loaded and scheduler running
- ✓ QueryEngine operational and fully configured
- ✓ All API routes registered
- ✓ GraphQL API available (if installed)
- ✓ File watcher monitoring models/ (if dev mode)
- ✓ Ready to accept requests!

---

### Available API Endpoints

```
POST   /api/v1/query                      ← Execute semantic queries
GET    /api/v1/schema                     ← Get schema information
POST   /api/v1/sql                        ← Execute raw SQL
GET    /api/v1/logs                       ← View query execution logs
POST   /api/v1/reload                     ← Reload schema from files
GET    /api/v1/metrics                    ← Get performance metrics
GET    /api/v1/pre-aggregations           ← List all pre-aggregations
POST   /api/v1/pre-aggregations/{name}/refresh  ← Manually refresh pre-agg
GET    /health                            ← Health check endpoint
POST   /graphql                           ← GraphQL API (optional)
```

---

## Complete Startup Timeline

```
0.0s     Process starts
         └─ python -m semantic_layer.api.main

0.1s     Import modules
         └─ FastAPI, SQLAlchemy, AsyncPG, Redis, etc.

0.2s     App created
         └─ create_app() returns FastAPI instance

0.3s     Server starts
         └─ Uvicorn listening on 0.0.0.0:8000

0.4s     Lifespan startup begins
         ├─ 0.40s: QueryLogger initialized
         ├─ 0.45s: MetricsCollector initialized
         ├─ 0.60s: Schema loaded (parsing YAML files)
         ├─ 0.70s: Cache connected (Redis or Memory)
         ├─ 0.80s: Authentication initialized (JWT/API Key)
         ├─ 1.00s: Database connected (connection pool created)
         ├─ 1.20s: Pre-aggregations registered from schema
         ├─ 1.40s: Pre-aggregation scheduler started
         ├─ 1.50s: QueryEngine initialized with all components
         ├─ 1.60s: GraphQL router added (if installed)
         └─ 1.70s: File watcher started (development mode only)

✅ 1.8s   APPLICATION READY
          ├─ Listening on http://0.0.0.0:8000
          ├─ All endpoints operational
          ├─ Ready to accept requests
          └─ All optimization layers operational
```

---

## Step 5: SHUTDOWN PHASE

When server stops (Ctrl+C):

```python
# After "yield" in lifespan, shutdown code runs:

# 1. Stop pre-aggregation scheduler
if pre_aggregation_scheduler:
    await pre_aggregation_scheduler.stop()

# 2. Disconnect database
await connector.disconnect()
# All connection pool connections are closed

# 3. Disconnect cache
if cache and hasattr(cache, "disconnect"):
    await cache.disconnect()

# 4. Stop file watcher
if file_watcher:
    file_watcher.stop()

print("SemanticQuark shutdown complete")
```

---

# Query Engine Components

## What is the QueryEngine?

The QueryEngine is the **main orchestrator** that brings everything together to execute semantic queries.

## QueryEngine Initialization

```python
query_engine = QueryEngine(
    schema,                          # Data definitions (cubes, dimensions, measures)
    connector,                       # Database connection (execute SQL)
    cache=cache,                     # Result caching layer
    cache_ttl=settings.cache_ttl,    # How long to keep cached results
    query_logger=query_logger,       # Audit trail of all queries
    pre_aggregation_manager=pre_agg, # Pre-computed aggregate tables
    metrics_collector=metrics,       # Performance tracking
)
```

## 7-Layer Stack

```
┌─────────────────────────────────────┐
│  1. SCHEMA                          │ ← Data definitions (cubes, dimensions, measures)
├─────────────────────────────────────┤
│  2. CONNECTOR                       │ ← Database connection (execute SQL)
├─────────────────────────────────────┤
│  3. CACHE (with TTL)                │ ← Store query results (10ms vs 500ms)
├─────────────────────────────────────┤
│  4. PRE-AGGREGATION MANAGER         │ ← Use pre-computed aggregates (100x faster)
├─────────────────────────────────────┤
│  5. QUERY LOGGER                    │ ← Audit trail (who, what, when, how long)
├─────────────────────────────────────┤
│  6. METRICS COLLECTOR               │ ← Performance monitoring & alerts
├─────────────────────────────────────┤
│  7. SQL BUILDER + OPTIMIZER         │ ← Semantic → SQL translation
└─────────────────────────────────────┘
```

## What Each Component Does

| Component | What | Why |
|-----------|------|-----|
| **schema** | Holds all cubes/dimensions/measures | Validates & resolves references |
| **connector** | Executes SQL on database | Gets the actual data |
| **cache** | Stores query results for 1 hour | Same query = 10ms vs 500ms ✓ |
| **cache_ttl** | How long to keep cache (3600s = 1hr) | After TTL expires, fresh query runs |
| **query_logger** | Records all query executions | Debug, audit, find slow queries |
| **pre_aggregation_manager** | Pre-computed aggregate tables | Big queries: 5000ms → 50ms ✓ |
| **metrics_collector** | Tracks performance stats | Dashboard: throughput, latency, cache hit % |

---

# Request Handling Flow

## Step-by-Step: First Request

User sends:

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "dimensions": ["orders.status"],
    "measures": ["orders.revenue"],
    "limit": 10
  }'
```

### Processing Timeline (Cache Miss):

```
0ms      Request arrives at Uvicorn
         └─ HTTP POST /api/v1/query

5ms      Auth middleware runs
         ├─ Extract JWT token from header
         ├─ Verify signature
         └─ Create SecurityContext

10ms     Request handler
         ├─ Parse JSON
         ├─ QueryParser converts to Query object
         └─ Validate dimensions/measures exist in schema

15ms     QueryEngine.execute() called
         ├─ Check for compare_date_range (transform if needed)
         └─ Optimize query

16ms     Cache check
         ├─ Generate cache key: hash(query + user_context)
         ├─ Check cache: MISS (first request)
         └─ Continue to database

18ms     Pre-aggregation check
         ├─ Find matching pre-agg
         └─ Match found! "revenue_by_status"

20ms     SQLBuilder generates SQL
         ├─ Look up dimensions in schema
         ├─ Look up measures in schema
         └─ Generate: SELECT status, SUM(amount) FROM revenue_by_status

25ms     Connector.execute_query()
         ├─ Get connection from pool
         └─ Send SQL to PostgreSQL

25-250ms Database executes
         ├─ Query runs on PostgreSQL
         ├─ Scans pre-agg table (100 rows instead of 100M)
         └─ Returns results

250ms    Results received
         └─ Raw data from database

260ms    Result formatting
         ├─ ResultFormatter converts to JSON
         ├─ Add metadata (execution_time, query, sql)
         ├─ Store in cache (TTL=3600s)
         ├─ Log query execution (QueryLogger)
         └─ Record metrics (MetricsCollector)

270ms    HTTP Response sent
         └─ JSON with:
            {
              "data": [...],
              "meta": {
                "execution_time_ms": 270,
                "cache_hit": false,
                "pre_aggregation_used": true,
                "sql": "SELECT status, SUM(amount) FROM revenue_by_status"
              }
            }
```

**TOTAL: ~270ms for cache miss with pre-agg**

---

## Step-by-Step: Second Request (Same Query)

User sends identical query (within cache TTL):

```bash
# Same query as before
```

### Processing Timeline (Cache Hit):

```
0ms      Request arrives

5ms      Auth middleware

10ms     Request handler

15ms     QueryEngine.execute()
         ├─ Check cache
         ├─ Generate cache key: hash(query + user_context)
         ├─ Lookup cache
         └─ CACHE HIT! ✓

20ms     Return cached result
         └─ No database query needed!
         └─ Update cache_hit flag to true

HTTP Response sent
  └─ Same JSON as before, but cache_hit=true

TOTAL: ~20ms ✓ 13x faster!
```

---

## Performance Comparison

### Three Request Scenarios

#### Scenario 1: Cache Miss + Pre-Agg Used
```
Request: First time, pre-agg available
Database: 100 rows scanned (pre-agg table)
Time: 270ms
Cache: Stored for 1 hour
```

#### Scenario 2: Cache Hit
```
Request: Second request within 1 hour
Database: No query (served from cache)
Time: 20ms ✓ 13x faster
Cache: Hit
```

#### Scenario 3: Cache Miss Without Pre-Agg
```
Request: After 1 hour cache TTL expired, no pre-agg
Database: 100M rows scanned (full table)
Time: 5000ms ⚠️ Much slower
Cache: Stored for 1 hour
```

---

# Deep Dive Examples

## Example 1: Loading a Cube Definition

### models/orders.yaml

```yaml
name: orders
description: Orders cube
table: public.orders

dimensions:
  # Primary Key
  id:
    type: number
    sql: id
    primary_key: true
    description: Order ID
  
  # String Dimension
  status:
    type: string
    sql: status
    description: Order status (pending, completed, cancelled)
  
  # Time Dimension with Granularities
  created_at:
    type: time
    sql: created_at
    granularities:
      - second
      - minute
      - hour
      - day
      - week
      - month
      - quarter
      - year
    description: When order was created
  
  # Calculated Dimension (SQL expression)
  revenue_category:
    type: string
    sql: |
      CASE 
        WHEN amount > 1000 THEN 'High'
        WHEN amount > 100 THEN 'Medium'
        ELSE 'Low'
      END
    description: Revenue category based on amount

measures:
  # Sum Measure
  revenue:
    type: sum
    sql: amount
    format: "$0,0.00"
    description: Total order revenue
  
  # Count Measure
  order_count:
    type: count
    sql: id
    description: Number of orders
  
  # Count Distinct Measure
  unique_customers:
    type: countDistinct
    sql: customer_id
    description: Number of unique customers
  
  # Average Measure
  average_order_value:
    type: avg
    sql: amount
    format: "$0,0.00"
    description: Average order value

# Relationships to other cubes
relationships:
  customer:
    type: belongs_to
    cube: customers
    foreign_key: customer_id
    primary_key: id
    description: Each order belongs to one customer

# Pre-aggregations (pre-computed tables)
pre_aggregations:
  - name: "revenue_by_status_daily"
    dimensions:
      - status
    measures:
      - revenue
    time_dimension: created_at
    granularity: day
    refresh_key:
      every_hour: true
    description: Daily revenue by order status
```

### SchemaLoader Processing:

```
Step 1: Read orders.yaml
        └─ YAML → Python dict

Step 2: Create Dimension objects
        ├─ id: Dimension(type=number, sql="id", primary_key=True)
        ├─ status: Dimension(type=string, sql="status")
        ├─ created_at: Dimension(type=time, sql="created_at", granularities=[...])
        └─ revenue_category: Dimension(type=string, sql="CASE WHEN...")

Step 3: Create Measure objects
        ├─ revenue: Measure(type=sum, sql="amount")
        ├─ order_count: Measure(type=count, sql="id")
        ├─ unique_customers: Measure(type=countDistinct, sql="customer_id")
        └─ average_order_value: Measure(type=avg, sql="amount")

Step 4: Create Relationship objects
        └─ customer: Relationship(type=belongs_to, cube="customers", ...)

Step 5: Create PreAggregation objects
        └─ revenue_by_status_daily: PreAggregation(dimensions=[...], measures=[...])

Step 6: Create Cube object
        └─ Cube(
             name="orders",
             table="public.orders",
             dimensions={...},
             measures={...},
             relationships={...},
             pre_aggregations=[...]
           )

Step 7: Add to Schema
        └─ schema.cubes["orders"] = Cube(...)

Result: ✓ Cube loaded and ready for queries
```

---

## Example 2: Query Execution Flow

### User Query

```json
{
  "dimensions": ["orders.status"],
  "measures": ["orders.revenue"],
  "filters": [
    {
      "dimension": "orders.created_at",
      "operator": "after_date",
      "values": ["2024-01-01"]
    }
  ],
  "timeDimensions": [
    {
      "dimension": "orders.created_at",
      "granularity": "month"
    }
  ],
  "limit": 10
}
```

### QueryEngine Processing:

```
Step 1: QueryParser.parse()
        ├─ Extract dimensions: ["orders.status"]
        ├─ Extract measures: ["orders.revenue"]
        ├─ Extract filters: [created_at > "2024-01-01"]
        ├─ Extract time dimensions: [created_at with month granularity]
        ├─ Validate query has at least one dimension/measure
        └─ Create Query object

Step 2: Check for compare_date_range
        └─ None found, continue with single query

Step 3: Cache check
        ├─ Generate cache key
        └─ Check Redis/Memory: MISS

Step 4: QueryOptimizer.optimize()
        └─ Optimize the query for execution

Step 5: PreAggregationManager.find_matching_pre_aggregation()
        ├─ Look for pre-agg that matches:
        │  └─ dimensions: ["status"]
        │  └─ measures: ["revenue"]
        │  └─ time_dimension: created_at (daily)
        ├─ Check if match exists
        └─ Found: "revenue_by_status_daily" ✓

Step 6: SQLBuilder.build()
        ├─ Get required cubes: {"orders"}
        ├─ Resolve dimension paths
        │  └─ "orders.status" → orders.Dimension.status
        │  └─ dimensions[status].get_sql_expression() → "status"
        │  └─ "orders.created_at" with granularity "month"
        │  └─ → DATE_TRUNC('month', orders.created_at)
        ├─ Resolve measure paths
        │  └─ "orders.revenue" → orders.Measure.revenue
        │  └─ measures[revenue].get_sql_expression() → "SUM(amount)"
        ├─ Build SELECT clause
        │  └─ SELECT
        │       status,
        │       DATE_TRUNC('month', created_at),
        │       SUM(amount)
        ├─ Build FROM clause
        │  └─ FROM revenue_by_status_daily
        ├─ Build WHERE clause
        │  └─ WHERE DATE_TRUNC('month', created_at) >= '2024-01-01'
        ├─ Build GROUP BY clause
        │  └─ GROUP BY status, DATE_TRUNC('month', created_at)
        ├─ Build ORDER BY clause
        │  └─ ORDER BY status ASC
        ├─ Build LIMIT clause
        │  └─ LIMIT 10
        └─ Final SQL:
           SELECT
             status,
             DATE_TRUNC('month', created_at) AS created_at_month,
             SUM(amount) AS revenue
           FROM revenue_by_status_daily
           WHERE DATE_TRUNC('month', created_at) >= '2024-01-01'
           GROUP BY status, DATE_TRUNC('month', created_at)
           ORDER BY status ASC
           LIMIT 10

Step 7: Connector.execute_query(sql)
        ├─ Get connection from pool
        ├─ Send SQL to PostgreSQL
        ├─ PostgreSQL executes:
        │  └─ Scans revenue_by_status_daily table (100 rows)
        │  └─ Filters by date
        │  └─ Groups by status and month
        └─ Returns results (e.g., 3 rows)

Step 8: ResultFormatter.format()
        ├─ Convert PostgreSQL rows to JSON
        └─ Result:
           {
             "data": [
               {"status": "completed", "created_at_month": "2024-01", "revenue": 50000},
               {"status": "completed", "created_at_month": "2024-02", "revenue": 60000},
               {"status": "pending", "created_at_month": "2024-01", "revenue": 30000}
             ],
             "meta": {
               "execution_time_ms": 250,
               "cache_hit": false,
               "pre_aggregation_used": true,
               "sql": "SELECT status, DATE_TRUNC(...) ..."
             }
           }

Step 9: Cache.set()
        ├─ Store result in Redis/Memory
        ├─ TTL: 3600 seconds (1 hour)
        └─ Next request with same query will hit cache

Step 10: QueryLogger.log_query()
        ├─ Log query execution details
        ├─ User: <user_context>
        ├─ Dimensions: ["orders.status"]
        ├─ Measures: ["orders.revenue"]
        ├─ Execution time: 250ms
        ├─ Cache hit: false
        ├─ Pre-agg used: true
        └─ SQL: SELECT status, ...

Step 11: MetricsCollector.record_query()
        ├─ Record execution_time: 250ms
        ├─ Record cache_hit: false
        ├─ Record error: false
        └─ Update stats for dashboard

Step 12: Return response to user
         └─ JSON with data, metadata, sql, execution_time
```

---

## Example 3: Calculated Dimension

### Definition

```yaml
# In orders cube
dimensions:
  revenue_category:
    type: string
    sql: |
      CASE 
        WHEN amount > 1000 THEN 'High'
        WHEN amount > 100 THEN 'Medium'
        ELSE 'Low'
      END
```

### When User Requests It

```json
{
  "dimensions": ["orders.revenue_category"],
  "measures": ["orders.order_count"]
}
```

### How Dimension.get_sql_expression() Works

```python
def get_sql_expression(self, table_alias: str = "") -> str:
    # In this case, self.sql = "CASE WHEN amount > 1000..."
    
    base_sql = self.sql
    # base_sql = "CASE WHEN amount > 1000 THEN 'High'..."
    
    # For this example, no time granularity
    # (granularity only applies to type="time")
    
    return base_sql
    # Returns: CASE WHEN amount > 1000 THEN 'High'...
```

### Generated SQL

```sql
SELECT 
  CASE 
    WHEN amount > 1000 THEN 'High'
    WHEN amount > 100 THEN 'Medium'
    ELSE 'Low'
  END AS revenue_category,
  COUNT(*) AS order_count
FROM orders
GROUP BY 
  CASE 
    WHEN amount > 1000 THEN 'High'
    WHEN amount > 100 THEN 'Medium'
    ELSE 'Low'
  END
```

### Result

```
revenue_category | order_count
-----------------+------------
High             | 150
Medium           | 1200
Low              | 8650
```

---

## Example 4: Time Dimension with Granularity

### Definition

```yaml
# In orders cube
dimensions:
  created_at:
    type: time
    sql: created_at
    granularities:
      - day
      - month
      - year
```

### User Query with Month Granularity

```json
{
  "dimensions": [],
  "measures": ["orders.revenue"],
  "timeDimensions": [
    {
      "dimension": "orders.created_at",
      "granularity": "month",
      "dateRange": ["2024-01-01", "2024-12-31"]
    }
  ]
}
```

### How Dimension.get_sql_expression() Works

```python
def get_sql_expression(self, table_alias: str = "", granularity: str = None) -> str:
    # self.type = "time"
    # self.sql = "created_at"
    # granularity = "month"
    
    base_sql = self.sql  # "created_at"
    
    if self.type == "time" and granularity:
        # Apply time granularity
        return self._apply_time_granularity(base_sql, granularity)

def _apply_time_granularity(self, sql_expr: str, granularity: str) -> str:
    if granularity == "month":
        return f"DATE_TRUNC('month', {sql_expr})"
        # Returns: DATE_TRUNC('month', created_at)
```

### Generated SQL

```sql
SELECT 
  DATE_TRUNC('month', created_at) AS created_at_month,
  SUM(amount) AS revenue
FROM orders
WHERE created_at >= '2024-01-01' AND created_at <= '2024-12-31'
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY DATE_TRUNC('month', created_at)
```

### Result

```
created_at_month | revenue
-----------------+----------
2024-01-01       | 150000
2024-02-01       | 180000
2024-03-01       | 200000
...
2024-12-01       | 220000
```

---

## Example 5: Pre-Aggregation in Action

### Without Pre-Aggregation

**Query:** "Get revenue by category"

```sql
SELECT 
  category,
  SUM(amount)
FROM orders
GROUP BY category;
```

**Execution:**
- Scans **100M rows** in orders table
- Performs aggregation in real-time
- **Takes 5 seconds** ⚠️

---

### With Pre-Aggregation

**Pre-aggregation Definition:**

```yaml
# In orders cube
pre_aggregations:
  - name: "revenue_by_category_daily"
    dimensions: ["category"]
    measures: ["revenue"]
    time_dimension: created_at
    granularity: day
```

**What gets created (automatically):**

```sql
-- This table is created automatically by the scheduler
CREATE TABLE revenue_by_category_daily AS
SELECT 
  DATE_TRUNC('day', created_at) as date,
  category,
  SUM(amount) as revenue
FROM orders
GROUP BY DATE_TRUNC('day', created_at), category;

-- This table has ~300 rows (365 days × ~0.8 categories average)
-- Instead of 100M rows in orders table
```

**Query:** "Get revenue by category"

```sql
-- System automatically uses pre-agg instead of base table
SELECT 
  category,
  SUM(revenue)  -- Already computed!
FROM revenue_by_category_daily
GROUP BY category;
```

**Execution:**
- Scans **365 rows** in pre-agg table
- Aggregation is just summing pre-computed values
- **Takes 50ms** ✓ 100x faster!

---

## Example 6: Multi-Cube Query with Relationships

### Two Cubes with Relationship

```yaml
# models/orders.yaml
name: orders
table: public.orders
dimensions:
  id: {type: number, sql: id, primary_key: true}
measures:
  revenue: {type: sum, sql: amount}
relationships:
  customer:
    type: belongs_to
    cube: customers
    foreign_key: customer_id
```

```yaml
# models/customers.yaml
name: customers
table: public.customers
dimensions:
  id: {type: number, sql: id, primary_key: true}
  country: {type: string, sql: country}
measures:
  customer_count: {type: count, sql: id}
```

### User Query

```json
{
  "dimensions": ["customers.country"],
  "measures": ["orders.revenue"]
}
```

### SQLBuilder Processing

```
Step 1: Required cubes
        └─ {orders, customers}

Step 2: Build join plan
        ├─ Primary cube: orders (t0)
        ├─ Secondary cube: customers (t1)
        ├─ Relationship: orders.belongs_to(customers)
        └─ Join type: LEFT JOIN

Step 3: Build relationships
        └─ orders.customer_id = customers.id

Step 4: Generate SQL
```

### Generated SQL

```sql
SELECT 
  customers.country,
  SUM(orders.amount) AS revenue
FROM orders AS t0
LEFT JOIN customers AS t1 
  ON t0.customer_id = t1.id
GROUP BY customers.country
ORDER BY customers.country
```

### Result

```
country   | revenue
----------+-----------
USA       | 500000
UK        | 300000
Canada    | 200000
...
```

---

## Summary

This comprehensive demo covers:

1. **Startup Journey** - Every system that initializes
2. **Configuration** - Where settings come from
3. **Schema Loading** - How YAML becomes Python objects
4. **Database Connection** - Connection pooling
5. **Pre-Aggregations** - Query speedup (5000ms → 50ms)
6. **QueryEngine** - Main orchestrator
7. **Request Flow** - How requests are processed
8. **Cache** - Result caching (10ms hits)
9. **Examples** - Real-world scenarios with SQL

Everything is **ordered, sequential, and optimized** for production use!
