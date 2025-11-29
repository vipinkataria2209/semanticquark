# Component Architecture Diagram - Block View

## Complete Component Architecture (18 Components)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           SEMANTIC LAYER PLATFORM                                    │
│                              Component Architecture                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    API LAYER                                         │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐        │
│  │   REST API       │      │   GraphQL API    │      │   SQL API        │        │
│  │                  │      │                  │      │                  │        │
│  │  • POST /query   │      │  • /graphql      │      │  • POST /sql     │        │
│  │  • GET /schema   │      │  • Dynamic       │      │  • Direct SQL    │        │
│  │  • GET /health   │      │    Schema        │      │    Execution     │        │
│  │  • FastAPI       │      │  • Strawberry    │      │  • Security     │        │
│  └──────────────────┘      └──────────────────┘      └──────────────────┘        │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP Requests
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              QUERY PROCESSING LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐        │
│  │  Query Parser    │      │  Query Validator  │      │  Query Engine    │        │
│  │                  │      │                  │      │                  │        │
│  │  • JSON → Query  │      │  • Validate refs  │      │  • Orchestrates  │        │
│  │  • Parse struct  │      │  • Check types    │      │  • Coordinates   │        │
│  │  • Extract fields│      │  • Resolve cubes  │      │  • Executes flow│        │
│  └──────────────────┘      └──────────────────┘      └──────────────────┘        │
│                                                                                     │
│  ┌──────────────────┐      ┌──────────────────┐                                  │
│  │  SQL Builder     │      │  Query Optimizer  │                                  │
│  │                  │      │                  │                                  │
│  │  • Generate SQL  │      │  • Remove dups    │                                  │
│  │  • Build JOINs   │      │  • Optimize filters│                                  │
│  │  • Apply filters │      │  • Join ordering  │                                  │
│  │  • GROUP BY      │      │  • Predicate push │                                  │
│  └──────────────────┘      └──────────────────┘                                  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Validated Query
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              SEMANTIC MODEL LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐        │
│  │  Schema Loader   │      │   Cube Manager    │      │ Dimension/Measure│        │
│  │                  │      │                  │      │    Manager       │        │
│  │  • Load YAML     │      │  • Manage cubes   │      │  • Dimensions    │        │
│  │  • Parse models  │      │  • Validate       │      │  • Measures      │        │
│  │  • Build schema  │      │  • Relationships │      │  • Types         │        │
│  └──────────────────┘      └──────────────────┘      └──────────────────┘        │
│                                                                                     │
│  ┌──────────────────┐                                                              │
│  │ Relationship      │                                                              │
│  │    Manager        │                                                              │
│  │  • Join paths     │                                                              │
│  │  • Relationships  │                                                              │
│  └──────────────────┘                                                              │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Semantic Objects
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            PERFORMANCE OPTIMIZATION                                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐        │
│  │  Cache Manager   │      │ Pre-Agg Manager   │      │ Pre-Agg Scheduler│        │
│  │                  │      │                  │      │                  │        │
│  │  • Redis Cache   │      │  • Match queries │      │  • Schedule      │        │
│  │  • Memory Cache  │      │  • Route queries  │      │    refresh       │        │
│  │  • Key Generator │      │  • Storage mgmt   │      │  • Auto refresh  │        │
│  │  • TTL Management│      │  • Table creation│      │  • Manual refresh│        │
│  └──────────────────┘      └──────────────────┘      └──────────────────┘        │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Cache/Pre-Agg Check
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              SECURITY LAYER                                         │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐        │
│  │  JWT Auth        │      │  API Key Auth     │      │  Authorization   │        │
│  │                  │      │                  │      │                  │        │
│  │  • Token validate│      │  • Key validate   │      │  • RBAC          │        │
│  │  • User context  │      │  • User mapping  │      │  • Permissions   │        │
│  │  • Expiration    │      │  • Key rotation  │      │  • Resource ACL │        │
│  └──────────────────┘      └──────────────────┘      └──────────────────┘        │
│                                                                                     │
│  ┌──────────────────┐                                                              │
│  │ Row-Level Security│                                                              │
│  │                  │                                                              │
│  │  • RLS rules     │                                                              │
│  │  • Context filter│                                                              │
│  │  • SQL injection │                                                              │
│  └──────────────────┘                                                              │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Security Context
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            OBSERVABILITY LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌──────────────────┐      ┌──────────────────┐                                  │
│  │  Query Logger    │      │  Metrics Collector│                                  │
│  │                  │      │                  │                                  │
│  │  • Structured log│      │  • Prometheus     │                                  │
│  │  • Query details │      │  • Query metrics │                                  │
│  │  • Execution time │      │  • Cache stats   │                                  │
│  │  • User context  │      │  • Error tracking│                                  │
│  │  • Cache hit/miss│      │  • Performance   │                                  │
│  └──────────────────┘      └──────────────────┘                                  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Logged & Monitored
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              DATABASE LAYER                                         │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐        │
│  │ PostgreSQL       │      │  MySQL           │      │  Base Connector  │        │
│  │  Connector       │      │  Connector       │      │  Interface       │        │
│  │                  │      │                  │      │                  │        │
│  │  • asyncpg       │      │  • aiomysql      │      │  • Abstract base │        │
│  │  • Connection    │      │  • Connection    │      │  • Common        │        │
│  │    pooling       │      │    pooling       │      │    interface     │        │
│  │  • Async exec    │      │  • Async exec    │      │  • Extensible    │        │
│  └──────────────────┘      └──────────────────┘      └──────────────────┘        │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ SQL Queries
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              DATABASE LAYER                                         │
│                                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   orders     │  │  customers   │  │  products    │  │  payments   │          │
│  │   table      │  │   table      │  │   table      │  │   table      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                                     │
│  ┌──────────────┐  ┌──────────────┐                                                │
│  │ order_items  │  │  categories  │                                                │
│  │   table      │  │   table      │                                                │
│  └──────────────┘  └──────────────┘                                                │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         DEVELOPER EXPERIENCE LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐        │
│  │  Hot Reload      │      │  Python SDK      │      │  CLI Tools       │        │
│  │                  │      │                  │      │                  │        │
│  │  • File watcher  │      │  • Client lib    │      │  • validate       │        │
│  │  • Auto reload   │      │  • Query methods│      │  • test          │        │
│  │  • Schema update │      │  • Schema access │      │  • dev server    │        │
│  └──────────────────┘      └──────────────────┘      └──────────────────┘        │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## Component Count by Layer

| Layer | Components | Details |
|-------|-----------|---------|
| **API Layer** | 3 | REST API, GraphQL API, SQL API |
| **Query Processing** | 5 | Parser, Validator, Engine, SQL Builder, Optimizer |
| **Semantic Model** | 4 | Schema Loader, Cube Manager, Dimension/Measure Manager, Relationship Manager |
| **Performance** | 3 | Cache Manager, Pre-Agg Manager, Pre-Agg Scheduler |
| **Security** | 4 | JWT Auth, API Key Auth, Authorization, RLS |
| **Observability** | 2 | Query Logger, Metrics Collector |
| **Database** | 3 | PostgreSQL Connector, MySQL Connector, Base Interface |
| **Developer Experience** | 3 | Hot Reload, Python SDK, CLI Tools |
| **TOTAL** | **18** | |

## Data Flow Through Components

```
Client Request
    │
    ▼
┌─────────────────┐
│   REST API      │ ──┐
│   GraphQL API   │ ──┼──► Authentication (JWT/API Key)
│   SQL API       │ ──┘
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Query Parser   │ ──► Query Validator
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Schema Manager │ ──► Resolve cubes, dimensions, measures
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Query Engine   │ ──┐
└────────┬────────┘   │
         │            │
         ├────────────┼──► Cache Check (Redis/Memory)
         │            │
         ├────────────┼──► Pre-Aggregation Check
         │            │
         ├────────────┼──► Row-Level Security (RLS)
         │            │
         ▼            │
┌─────────────────┐  │
│  SQL Builder    │  │
└────────┬────────┘  │
         │            │
         ▼            │
┌─────────────────┐  │
│ Query Optimizer │  │
└────────┬────────┘  │
         │            │
         ▼            │
┌─────────────────┐  │
│ DB Connector    │  │
└────────┬────────┘  │
         │            │
         ▼            │
┌─────────────────┐  │
│   PostgreSQL    │  │
│   MySQL         │  │
└────────┬────────┘  │
         │            │
         │            │
         └────────────┘
         │
         ▼
┌─────────────────┐
│ Result Formatter│
└────────┬────────┘
         │
         ├──► Query Logger (log query details)
         │
         ├──► Metrics Collector (record metrics)
         │
         ├──► Cache Store (store result)
         │
         ▼
    JSON Response
```

## Component Interactions

### 1. Query Execution Flow
```
REST API → Parser → Validator → Schema Manager → Query Engine → 
SQL Builder → Optimizer → Cache Check → Pre-Agg Check → 
RLS Application → DB Connector → Database → Result Formatter → 
Logger → Metrics → Cache Store → Response
```

### 2. Authentication Flow
```
Request → JWT/API Key Auth → Authorization Check → 
Security Context → RLS Application → Query Execution
```

### 3. Caching Flow
```
Query → Cache Key Generation → Cache Check → 
[Cache Hit] → Return Cached Result
[Cache Miss] → Execute Query → Store in Cache → Return Result
```

### 4. Pre-Aggregation Flow
```
Query → Pre-Agg Matching → Check Availability → 
[Match Found] → Route to Pre-Agg Table → Return Result
[No Match] → Execute on Base Table → Return Result
```

### 5. Hot Reload Flow
```
File Change → File Watcher → Schema Reload → 
Update Query Engine → Update SQL Builder → Ready
```

## Component Dependencies

```
API Layer
    └──► Query Processing Layer
            └──► Semantic Model Layer
                    └──► Performance Layer
                            └──► Security Layer
                                    └──► Observability Layer
                                            └──► Database Layer
                                                    └──► Developer Experience Layer
```

## Detailed Component Descriptions

### API Layer (3 components)

#### 1. REST API (FastAPI)
**Purpose**: Primary HTTP interface for executing semantic queries and accessing platform functionality.

**Key Responsibilities**:
- Receives HTTP POST requests with JSON query payloads
- Validates request format and structure
- Routes requests to appropriate handlers
- Returns standardized JSON responses with data and metadata
- Provides auto-generated API documentation (Swagger/OpenAPI)

**Key Features**:
- **Query Endpoint** (`POST /api/v1/query`): Accepts semantic queries in JSON format, executes them, and returns results
- **Schema Endpoint** (`GET /api/v1/schema`): Returns available cubes, dimensions, measures, and relationships
- **Health Endpoint** (`GET /health`): Provides system status and connectivity checks
- **Pre-aggregation Endpoints**: Manage pre-aggregation definitions and refresh schedules
- **Query Logs Endpoint**: Access structured query logs for analysis
- **Metrics Endpoint**: Expose Prometheus-compatible metrics

**Request/Response Flow**:
- Client sends JSON query → REST API validates → Routes to Query Engine → Returns formatted JSON response
- Supports pagination, filtering, ordering, and limit parameters
- Includes execution metadata (time, row count, cache status)

**Integration Points**:
- Integrates with Query Engine for query execution
- Uses Authentication middleware for security
- Connects to Query Logger for audit trail
- Exposes Metrics Collector data

**Pseudocode - REST API Request Handling**:
```
FUNCTION handle_query_request(http_request):
    // Step 1: Extract and validate request
    json_body = EXTRACT_JSON_BODY(http_request)
    IF json_body IS INVALID:
        RETURN HTTP_400_ERROR("Invalid JSON format")
    END IF
    
    // Step 2: Authenticate request
    security_context = AUTHENTICATE_REQUEST(http_request)
    IF security_context IS NULL:
        RETURN HTTP_401_ERROR("Authentication required")
    END IF
    
    // Step 3: Authorize access
    IF NOT AUTHORIZE(security_context, "query", "execute"):
        RETURN HTTP_403_ERROR("Access denied")
    END IF
    
    // Step 4: Execute query via Query Engine
    query_result = QUERY_ENGINE.execute(json_body, security_context)
    
    // Step 5: Format response
    response = {
        "data": query_result.data,
        "meta": {
            "execution_time_ms": query_result.execution_time,
            "row_count": query_result.row_count,
            "cache_hit": query_result.cache_hit
        }
    }
    
    // Step 6: Return response
    RETURN HTTP_200_OK(response)
END FUNCTION
```

---

#### 2. GraphQL API (Strawberry)
**Purpose**: Provides flexible, self-documenting query interface with dynamic schema generation.

**Key Responsibilities**:
- Dynamically generates GraphQL schema from semantic models
- Allows clients to request only needed fields
- Supports nested queries and relationships
- Provides introspection capabilities for schema discovery

**Key Features**:
- **Dynamic Schema**: Automatically creates GraphQL types from semantic cubes
- **Field Selection**: Clients specify exactly which dimensions/measures to retrieve
- **Relationship Queries**: Supports nested queries across related cubes
- **Type System**: Maps semantic types (string, number, time) to GraphQL types
- **Introspection**: Enables schema exploration via GraphQL introspection queries

**Query Capabilities**:
- Single cube queries: Query dimensions and measures from one cube
- Multi-cube queries: Query across related cubes with automatic JOINs
- Filtering: Apply filters using GraphQL arguments
- Aggregation: Request aggregated measures with grouping

**Advantages**:
- Reduces over-fetching (only requested fields returned)
- Single endpoint for all queries
- Self-documenting schema
- Better for complex nested data structures

**Integration Points**:
- Uses Query Engine for actual query execution
- Leverages Schema Manager for type information
- Applies same security and caching as REST API

**Pseudocode - GraphQL Query Resolution**:
```
FUNCTION resolve_graphql_query(graphql_query, schema):
    // Step 1: Parse GraphQL query
    parsed_query = PARSE_GRAPHQL(graphql_query)
    
    // Step 2: Generate semantic query from GraphQL
    semantic_query = {
        dimensions: [],
        measures: [],
        filters: []
    }
    
    // Step 3: Extract fields from GraphQL query
    FOR EACH field IN parsed_query.fields:
        IF field.type == "dimension":
            semantic_query.dimensions.ADD(field.name)
        ELSE IF field.type == "measure":
            semantic_query.measures.ADD(field.name)
        END IF
        
        // Handle nested fields (relationships)
        IF field.has_nested_fields():
            nested_query = RESOLVE_NESTED_FIELDS(field, schema)
            semantic_query.ADD(nested_query)
        END IF
    END FOR
    
    // Step 4: Extract filters from GraphQL arguments
    IF parsed_query.has_arguments():
        FOR EACH argument IN parsed_query.arguments:
            filter = CONVERT_ARGUMENT_TO_FILTER(argument)
            semantic_query.filters.ADD(filter)
        END FOR
    END IF
    
    // Step 5: Execute via Query Engine
    result = QUERY_ENGINE.execute(semantic_query)
    
    // Step 6: Format as GraphQL response
    graphql_response = FORMAT_GRAPHQL_RESPONSE(result, parsed_query)
    
    RETURN graphql_response
END FUNCTION
```

---

#### 3. SQL API
**Purpose**: Allows direct SQL execution for SQL-native tools and advanced users who need raw SQL access.

**Key Responsibilities**:
- Accepts raw SQL queries from clients
- Validates SQL for security (prevents dangerous operations)
- Applies row-level security if enabled
- Executes SQL and returns results in standardized format

**Key Features**:
- **SQL Validation**: Prevents DROP, DELETE, TRUNCATE, and other destructive operations
- **Security Enforcement**: Applies RLS rules even for direct SQL
- **Parameter Binding**: Supports parameterized queries for security
- **Result Formatting**: Returns results in consistent JSON format
- **Error Handling**: Provides detailed error messages for SQL errors

**Use Cases**:
- Integration with SQL-native BI tools
- Advanced analytics requiring custom SQL
- Data exploration and ad-hoc queries
- Migration from existing SQL-based systems

**Security Considerations**:
- Validates SQL syntax before execution
- Applies user context and RLS rules
- Logs all SQL queries for audit
- Limits query complexity and execution time

**Integration Points**:
- Uses Database Connector for execution
- Applies Security middleware
- Integrates with Query Logger

### Query Processing (5 components)

#### 4. Query Parser
**Purpose**: Transforms user-submitted JSON queries into structured internal Query objects.

**Key Responsibilities**:
- Parses JSON query structure into internal representation
- Extracts dimensions, measures, filters, ordering, and pagination
- Validates JSON structure and required fields
- Creates Query object with all parsed components

**Input Format**:
- JSON object with dimensions, measures, filters, order, limit fields
- Supports "cube.field" notation for referencing semantic concepts
- Handles nested filter structures with operators and values

**Processing Steps**:
1. Parse JSON structure and validate format
2. Extract dimension references (e.g., "orders.status")
3. Extract measure references (e.g., "orders.revenue")
4. Parse filter conditions with operators and values
5. Extract ordering specifications
6. Extract pagination parameters (limit, offset)
7. Create internal Query object

**Output**:
- Structured Query object ready for validation
- Contains all query components in normalized format
- Preserves original query structure for error reporting

**Error Handling**:
- Detects malformed JSON
- Identifies missing required fields
- Provides helpful error messages for invalid structures

**Pseudocode - Query Parsing**:
```
FUNCTION parse_query(json_input):
    // Step 1: Parse JSON structure
    TRY:
        query_dict = JSON_PARSE(json_input)
    CATCH json_error:
        RETURN ERROR("Invalid JSON format: " + json_error.message)
    END TRY
    
    // Step 2: Create Query object
    query = NEW Query()
    
    // Step 3: Parse dimensions
    IF query_dict.has("dimensions"):
        FOR EACH dim_ref IN query_dict["dimensions"]:
            IF NOT MATCHES_PATTERN(dim_ref, "cube.field"):
                RETURN ERROR("Invalid dimension format. Use 'cube.field'")
            END IF
            
            (cube_name, field_name) = SPLIT(dim_ref, ".")
            query.dimensions.ADD({
                cube: cube_name,
                field: field_name,
                full_reference: dim_ref
            })
        END FOR
    END IF
    
    // Step 4: Parse measures
    IF query_dict.has("measures"):
        FOR EACH meas_ref IN query_dict["measures"]:
            IF NOT MATCHES_PATTERN(meas_ref, "cube.field"):
                RETURN ERROR("Invalid measure format. Use 'cube.field'")
            END IF
            
            (cube_name, field_name) = SPLIT(meas_ref, ".")
            query.measures.ADD({
                cube: cube_name,
                field: field_name,
                full_reference: meas_ref
            })
        END FOR
    END IF
    
    // Step 5: Parse filters
    IF query_dict.has("filters"):
        FOR EACH filter_dict IN query_dict["filters"]:
            filter = {
                dimension: filter_dict["dimension"],
                operator: filter_dict["operator"],
                value: filter_dict["value"]
            }
            query.filters.ADD(filter)
        END FOR
    END IF
    
    // Step 6: Parse ordering
    IF query_dict.has("order"):
        FOR EACH order_spec IN query_dict["order"]:
            query.order.ADD({
                field: order_spec["field"],
                direction: order_spec["direction"]  // "asc" or "desc"
            })
        END FOR
    END IF
    
    // Step 7: Parse pagination
    IF query_dict.has("limit"):
        query.limit = query_dict["limit"]
    END IF
    
    IF query_dict.has("offset"):
        query.offset = query_dict["offset"]
    END IF
    
    // Step 8: Validate at least one dimension or measure
    IF query.dimensions.IS_EMPTY() AND query.measures.IS_EMPTY():
        RETURN ERROR("Query must include at least one dimension or measure")
    END IF
    
    RETURN query
END FUNCTION
```

---

#### 5. Query Validator
**Purpose**: Validates that all query references exist in the semantic model and are correctly typed.

**Key Responsibilities**:
- Validates cube references exist in semantic model
- Validates dimension/measure references within cubes
- Checks filter operators are compatible with dimension types
- Ensures query structure is semantically correct

**Validation Rules**:
- **Reference Format**: Must use "cube.field" notation
- **Cube Existence**: Referenced cubes must exist in schema
- **Field Existence**: Dimensions/measures must exist in their cubes
- **Type Compatibility**: Filter operators must match dimension types
  - String dimensions: equals, contains, startsWith, endsWith
  - Number dimensions: equals, greater_than, less_than, between
  - Time dimensions: equals, before, after, on, between
- **Required Fields**: Query must have at least one dimension or measure

**Validation Process**:
1. Split "cube.field" references into cube and field names
2. Look up cube in semantic model
3. Look up field (dimension or measure) in cube
4. Validate filter operators match dimension types
5. Validate filter values match expected formats
6. Return validated Query object or detailed error

**Error Messages**:
- Provides specific error messages with available alternatives
- Lists available cubes when cube not found
- Lists available dimensions/measures when field not found
- Suggests correct operators for type mismatches

**Pseudocode - Query Validation**:
```
FUNCTION validate_query(query, semantic_model):
    // Step 1: Validate dimensions
    FOR EACH dimension IN query.dimensions:
        // Check cube exists
        IF NOT semantic_model.has_cube(dimension.cube):
            available_cubes = semantic_model.list_cube_names()
            RETURN ERROR("Cube '" + dimension.cube + "' not found. Available: " + available_cubes)
        END IF
        
        cube = semantic_model.get_cube(dimension.cube)
        
        // Check dimension exists in cube
        IF NOT cube.has_dimension(dimension.field):
            available_dims = cube.list_dimension_names()
            RETURN ERROR("Dimension '" + dimension.field + "' not in cube '" + dimension.cube + "'. Available: " + available_dims)
        END IF
    END FOR
    
    // Step 2: Validate measures
    FOR EACH measure IN query.measures:
        IF NOT semantic_model.has_cube(measure.cube):
            RETURN ERROR("Cube '" + measure.cube + "' not found")
        END IF
        
        cube = semantic_model.get_cube(measure.cube)
        
        IF NOT cube.has_measure(measure.field):
            available_measures = cube.list_measure_names()
            RETURN ERROR("Measure '" + measure.field + "' not in cube '" + measure.cube + "'. Available: " + available_measures)
        END IF
    END FOR
    
    // Step 3: Validate filters
    FOR EACH filter IN query.filters:
        // Resolve dimension
        IF NOT semantic_model.has_cube(filter.dimension.cube):
            RETURN ERROR("Cube not found in filter")
        END IF
        
        cube = semantic_model.get_cube(filter.dimension.cube)
        dimension = cube.get_dimension(filter.dimension.field)
        
        // Check operator compatibility with dimension type
        valid_operators = GET_VALID_OPERATORS(dimension.type)
        IF NOT valid_operators.CONTAINS(filter.operator):
            RETURN ERROR("Operator '" + filter.operator + "' not valid for dimension type '" + dimension.type + "'. Use: " + valid_operators)
        END IF
        
        // Validate filter value format
        IF NOT IS_VALID_FILTER_VALUE(filter.value, filter.operator):
            RETURN ERROR("Invalid filter value format for operator '" + filter.operator + "'")
        END IF
    END FOR
    
    // Step 4: Return validated query
    RETURN VALIDATED_QUERY(query)
END FUNCTION

FUNCTION GET_VALID_OPERATORS(dimension_type):
    SWITCH dimension_type:
        CASE "string":
            RETURN ["equals", "not_equals", "contains", "startsWith", "endsWith", "set", "not_set"]
        CASE "number":
            RETURN ["equals", "not_equals", "greater_than", "less_than", "between", "set", "not_set"]
        CASE "time":
            RETURN ["equals", "before", "after", "on", "between", "set", "not_set"]
        CASE "boolean":
            RETURN ["equals"]
        DEFAULT:
            RETURN []
    END SWITCH
END FUNCTION
```

---

#### 6. Query Engine
**Purpose**: Orchestrates the complete query execution flow, coordinating all components.

**Key Responsibilities**:
- Coordinates query execution from start to finish
- Manages caching (check cache, store results)
- Routes queries to pre-aggregations when available
- Applies security context and RLS rules
- Handles errors and provides consistent error responses
- Tracks execution time and performance metrics

**Execution Flow**:
1. **Query Optimization**: Applies optimization rules
2. **Pre-Aggregation Check**: Looks for matching pre-aggregations
3. **Cache Check**: Checks if query result is cached
4. **Security Application**: Applies RLS and authorization
5. **SQL Generation**: Uses SQL Builder to generate SQL
6. **Query Execution**: Executes SQL via Database Connector
7. **Result Formatting**: Formats results with metadata
8. **Cache Storage**: Stores results in cache
9. **Logging**: Logs query execution details
10. **Metrics**: Records performance metrics

**Integration Points**:
- Coordinates with all other components
- Manages cache lifecycle
- Routes to pre-aggregations
- Applies security rules
- Logs and monitors execution

**Performance Features**:
- Parallel cache and pre-aggregation checks
- Efficient result streaming for large datasets
- Connection pooling management
- Query timeout handling

**Pseudocode - Query Engine Execution Flow**:
```
FUNCTION execute_query(query, user_context):
    start_time = GET_CURRENT_TIME()
    
    // Step 1: Optimize query
    optimized_query = QUERY_OPTIMIZER.optimize(query)
    
    // Step 2: Check for pre-aggregation match
    pre_agg = PRE_AGGREGATION_MANAGER.find_matching(optimized_query)
    IF pre_agg IS NOT NULL AND pre_agg.exists():
        // Route to pre-aggregation table
        sql = BUILD_SQL_FROM_PRE_AGG(optimized_query, pre_agg)
        result = DATABASE_CONNECTOR.execute(sql)
        execution_time = GET_CURRENT_TIME() - start_time
        
        // Log and return
        QUERY_LOGGER.log(query, result, execution_time, user_context, cache_hit=false, pre_agg_used=true)
        METRICS_COLLECTOR.record_query(execution_time, false, true)
        RETURN FORMAT_RESULT(result, execution_time)
    END IF
    
    // Step 3: Check cache
    cache_key = CACHE_KEY_GENERATOR.generate(optimized_query, user_context)
    cached_result = CACHE.get(cache_key)
    IF cached_result IS NOT NULL:
        execution_time = GET_CURRENT_TIME() - start_time
        QUERY_LOGGER.log(query, cached_result, execution_time, user_context, cache_hit=true)
        METRICS_COLLECTOR.record_cache_hit()
        RETURN cached_result
    END IF
    
    // Step 4: Apply Row-Level Security
    IF user_context IS NOT NULL:
        optimized_query = RLS_MANAGER.apply(optimized_query, user_context)
    END IF
    
    // Step 5: Generate SQL
    sql = SQL_BUILDER.build(optimized_query)
    
    // Step 6: Execute query
    TRY:
        raw_result = DATABASE_CONNECTOR.execute(sql)
        execution_time = GET_CURRENT_TIME() - start_time
    CATCH database_error:
        QUERY_LOGGER.log_error(query, database_error, user_context)
        METRICS_COLLECTOR.record_error()
        RETURN ERROR("Query execution failed: " + database_error.message)
    END TRY
    
    // Step 7: Format result
    formatted_result = RESULT_FORMATTER.format(raw_result, execution_time)
    
    // Step 8: Store in cache
    CACHE.set(cache_key, formatted_result, ttl=3600)
    
    // Step 9: Log and record metrics
    QUERY_LOGGER.log(query, formatted_result, execution_time, user_context, cache_hit=false)
    METRICS_COLLECTOR.record_query(execution_time, false, false)
    
    // Step 10: Return result
    RETURN formatted_result
END FUNCTION
```

---

#### 7. SQL Builder
**Purpose**: Translates validated semantic queries into optimized PostgreSQL SQL statements.

**Key Responsibilities**:
- Generates SELECT clause with dimensions and aggregated measures
- Builds FROM clause with base table and JOINs for multi-cube queries
- Constructs WHERE clause from filter conditions
- Creates GROUP BY clause for aggregations
- Adds ORDER BY and LIMIT clauses
- Applies RLS conditions to WHERE clause

**SQL Generation Strategy**:
1. **SELECT Clause**: Maps dimensions to SQL expressions, aggregates measures
2. **FROM Clause**: Identifies base table, adds JOINs for related cubes
3. **JOIN Planning**: Determines join paths between cubes using relationships
4. **WHERE Clause**: Converts semantic filters to SQL conditions
5. **GROUP BY**: Includes all dimension expressions when measures present
6. **ORDER BY**: Converts ordering specifications to SQL
7. **LIMIT/OFFSET**: Adds pagination

**Multi-Cube Query Handling**:
- Analyzes query to identify required cubes
- Finds relationships between cubes in semantic model
- Generates LEFT JOIN statements with proper join conditions
- Manages table aliases to avoid conflicts
- Handles complex join paths (A → B → C)

**SQL Security**:
- Uses parameterized queries to prevent SQL injection
- Escapes all user-provided values
- Validates SQL expressions from semantic models
- Applies RLS conditions securely

**Optimization Features**:
- Only selects required columns
- Optimizes JOIN order when possible
- Pushes filters before JOINs when beneficial
- Uses appropriate aggregation functions

**Pseudocode - SQL Generation**:
```
FUNCTION build_sql(query, semantic_model):
    // Step 1: Identify required cubes
    required_cubes = EXTRACT_CUBES(query.dimensions, query.measures, query.filters)
    
    // Step 2: Build SELECT clause
    select_clause = []
    
    // Add dimensions to SELECT
    FOR EACH dimension IN query.dimensions:
        cube = semantic_model.get_cube(dimension.cube)
        dim_obj = cube.get_dimension(dimension.field)
        sql_expr = dim_obj.get_sql_expression()
        
        // Apply time granularity if needed
        IF dim_obj.is_time_dimension() AND dim_obj.has_granularity():
            sql_expr = APPLY_TIME_GRANULARITY(sql_expr, dim_obj.granularity)
        END IF
        
        alias = dimension.cube + "_" + dimension.field
        select_clause.ADD(sql_expr + " AS " + alias)
    END FOR
    
    // Add measures to SELECT (with aggregation)
    FOR EACH measure IN query.measures:
        cube = semantic_model.get_cube(measure.cube)
        meas_obj = cube.get_measure(measure.field)
        aggregation = GET_AGGREGATION_FUNCTION(meas_obj.type)
        sql_expr = meas_obj.get_sql_expression()
        
        alias = measure.cube + "_" + measure.field
        select_clause.ADD(aggregation + "(" + sql_expr + ") AS " + alias)
    END FOR
    
    // Step 3: Build FROM clause with JOINs
    base_cube = required_cubes[0]
    from_clause = "FROM " + base_cube.table + " AS " + base_cube.name
    
    // Add JOINs for additional cubes
    FOR EACH additional_cube IN required_cubes[1:]:
        relationship = FIND_RELATIONSHIP(base_cube, additional_cube, semantic_model)
        join_condition = relationship.from_cube + "." + relationship.from_field + 
                        " = " + additional_cube.name + "." + relationship.to_field
        from_clause = from_clause + " LEFT JOIN " + additional_cube.table + 
                     " AS " + additional_cube.name + " ON " + join_condition
    END FOR
    
    // Step 4: Build WHERE clause
    where_conditions = []
    FOR EACH filter IN query.filters:
        cube = semantic_model.get_cube(filter.dimension.cube)
        dimension = cube.get_dimension(filter.dimension.field)
        condition = CONVERT_FILTER_TO_SQL(filter, dimension)
        where_conditions.ADD(condition)
    END FOR
    
    where_clause = ""
    IF where_conditions.IS_NOT_EMPTY():
        where_clause = "WHERE " + JOIN(where_conditions, " AND ")
    END IF
    
    // Step 5: Build GROUP BY clause
    group_by_clause = ""
    IF query.measures.IS_NOT_EMPTY():
        group_by_fields = []
        FOR EACH dimension IN query.dimensions:
            cube = semantic_model.get_cube(dimension.cube)
            dim_obj = cube.get_dimension(dimension.field)
            group_by_fields.ADD(dim_obj.get_sql_expression())
        END FOR
        group_by_clause = "GROUP BY " + JOIN(group_by_fields, ", ")
    END IF
    
    // Step 6: Build ORDER BY clause
    order_by_clause = ""
    IF query.order.IS_NOT_EMPTY():
        order_by_fields = []
        FOR EACH order_spec IN query.order:
            field_sql = RESOLVE_FIELD_SQL(order_spec.field, semantic_model)
            order_by_fields.ADD(field_sql + " " + order_spec.direction)
        END FOR
        order_by_clause = "ORDER BY " + JOIN(order_by_fields, ", ")
    END IF
    
    // Step 7: Assemble complete SQL
    sql = "SELECT " + JOIN(select_clause, ", ") + "\n"
    sql = sql + from_clause + "\n"
    IF where_clause != "":
        sql = sql + where_clause + "\n"
    END IF
    IF group_by_clause != "":
        sql = sql + group_by_clause + "\n"
    END IF
    IF order_by_clause != "":
        sql = sql + order_by_clause + "\n"
    END IF
    IF query.limit IS NOT NULL:
        sql = sql + "LIMIT " + query.limit
    END IF
    
    RETURN sql
END FUNCTION

FUNCTION CONVERT_FILTER_TO_SQL(filter, dimension):
    dimension_sql = dimension.get_sql_expression()
    operator_sql = CONVERT_OPERATOR_TO_SQL(filter.operator)
    value_sql = ESCAPE_VALUE(filter.value, dimension.type)
    
    RETURN dimension_sql + " " + operator_sql + " " + value_sql
END FUNCTION
```

---

#### 8. Query Optimizer
**Purpose**: Applies optimization rules to queries before execution to improve performance.

**Key Responsibilities**:
- Removes duplicate dimensions and measures
- Optimizes filter ordering (most selective first)
- Optimizes JOIN order for multi-cube queries
- Applies predicate pushdown when possible
- Estimates query cost for routing decisions

**Optimization Rules**:
1. **Duplicate Removal**: Eliminates duplicate dimensions/measures in query
2. **Filter Optimization**: Reorders filters by selectivity
3. **Join Optimization**: Determines optimal JOIN order based on:
   - Table sizes (smaller tables first)
   - Filter selectivity
   - Index availability
4. **Predicate Pushdown**: Moves filters closer to data source
5. **Column Pruning**: Removes unused columns from SELECT

**Cost Estimation**:
- Estimates query execution cost
- Considers table sizes, filter selectivity, join complexity
- Used for deciding between cache, pre-aggregation, or direct query

**Integration**:
- Works with Query Engine before SQL generation
- Provides optimized query to SQL Builder
- Considers cache and pre-aggregation availability

### Semantic Model (4 components)

#### 9. Schema Loader
**Purpose**: Loads, parses, and validates YAML semantic model files into structured schema objects.

**Key Responsibilities**:
- Scans directory for YAML model files
- Parses YAML syntax into Python objects
- Validates model structure and syntax
- Builds complete Schema object with all cubes
- Handles model reloading during development

**Loading Process**:
1. **File Discovery**: Scans models directory for `.yaml` files
2. **YAML Parsing**: Parses each YAML file into dictionary structure
3. **Model Validation**: Validates required fields and structure
4. **Cube Creation**: Creates Cube objects from YAML definitions
5. **Schema Assembly**: Combines all cubes into Schema object
6. **Relationship Resolution**: Resolves relationships between cubes

**Model File Structure**:
- One YAML file per cube (e.g., `orders.yaml`, `products.yaml`)
- Contains cube metadata, dimensions, measures, relationships
- Supports comments and documentation
- Version-controlled and human-readable

**Validation Features**:
- Validates YAML syntax
- Checks required fields are present
- Validates SQL expressions
- Ensures cube names are unique
- Validates relationship references

**Hot Reload Support**:
- Monitors file changes during development
- Automatically reloads schema when files change
- Updates Query Engine with new schema
- Provides feedback on reload status

**Pseudocode - Schema Loading**:
```
FUNCTION load_schema(models_directory):
    schema = NEW Schema()
    
    // Step 1: Discover YAML files
    yaml_files = DISCOVER_YAML_FILES(models_directory)
    
    // Step 2: Load and parse each file
    FOR EACH yaml_file IN yaml_files:
        TRY:
            yaml_content = READ_FILE(yaml_file)
            cube_dict = YAML_PARSE(yaml_content)
            
            // Step 3: Validate cube structure
            IF NOT VALIDATE_CUBE_STRUCTURE(cube_dict):
                RETURN ERROR("Invalid cube structure in " + yaml_file)
            END IF
            
            // Step 4: Create Cube object
            cube = CREATE_CUBE_FROM_DICT(cube_dict)
            
            // Step 5: Validate cube
            validation_result = VALIDATE_CUBE(cube)
            IF NOT validation_result.is_valid():
                RETURN ERROR("Cube validation failed: " + validation_result.errors)
            END IF
            
            // Step 6: Add to schema
            schema.add_cube(cube)
            
        CATCH parse_error:
            RETURN ERROR("Failed to parse " + yaml_file + ": " + parse_error.message)
        END TRY
    END FOR
    
    // Step 7: Resolve relationships
    schema.resolve_relationships()
    
    // Step 8: Validate relationships
    relationship_errors = VALIDATE_RELATIONSHIPS(schema)
    IF relationship_errors.IS_NOT_EMPTY():
        RETURN ERROR("Relationship validation failed: " + relationship_errors)
    END IF
    
    RETURN schema
END FUNCTION

FUNCTION VALIDATE_CUBE_STRUCTURE(cube_dict):
    // Check required fields
    IF NOT cube_dict.has("name"):
        RETURN false
    END IF
    
    IF NOT cube_dict.has("table"):
        RETURN false
    END IF
    
    // Check dimensions and measures exist
    IF NOT cube_dict.has("dimensions") AND NOT cube_dict.has("measures"):
        RETURN false
    END IF
    
    RETURN true
END FUNCTION
```

---

#### 10. Cube Manager
**Purpose**: Manages cube definitions, providing access to dimensions, measures, and cube metadata.

**Key Responsibilities**:
- Stores and manages cube definitions
- Provides lookup methods for dimensions and measures
- Validates cube structure and relationships
- Manages cube-level metadata (table, description, RLS rules)

**Cube Structure**:
- **Metadata**: Name, table name, description
- **Dimensions**: Collection of dimension definitions
- **Measures**: Collection of measure definitions
- **Relationships**: Connections to other cubes
- **Pre-aggregations**: Pre-computed aggregation definitions
- **RLS Rules**: Row-level security SQL expressions

**Key Operations**:
- **Get Dimension**: Retrieve dimension by name with validation
- **Get Measure**: Retrieve measure by name with validation
- **List Dimensions**: Get all available dimensions
- **List Measures**: Get all available measures
- **Validate**: Check cube structure is correct

**Integration**:
- Used by Query Validator to check references
- Used by SQL Builder to get SQL expressions
- Used by Schema Manager for cube lookups

**Pseudocode - Cube Operations**:
```
FUNCTION get_dimension(cube, dimension_name):
    IF NOT cube.dimensions.has(dimension_name):
        available = cube.dimensions.list_names()
        RETURN ERROR("Dimension '" + dimension_name + "' not found. Available: " + available)
    END IF
    
    RETURN cube.dimensions.get(dimension_name)
END FUNCTION

FUNCTION get_measure(cube, measure_name):
    IF NOT cube.measures.has(measure_name):
        available = cube.measures.list_names()
        RETURN ERROR("Measure '" + measure_name + "' not found. Available: " + available)
    END IF
    
    RETURN cube.measures.get(measure_name)
END FUNCTION

FUNCTION validate_cube(cube):
    errors = []
    
    // Validate cube name
    IF cube.name IS EMPTY:
        errors.ADD("Cube name is required")
    END IF
    
    // Validate table name
    IF cube.table IS EMPTY:
        errors.ADD("Table name is required")
    END IF
    
    // Validate dimensions
    FOR EACH dimension IN cube.dimensions:
        IF dimension.sql IS EMPTY:
            errors.ADD("Dimension '" + dimension.name + "' missing SQL expression")
        END IF
        
        IF NOT IS_VALID_TYPE(dimension.type):
            errors.ADD("Dimension '" + dimension.name + "' has invalid type")
        END IF
    END FOR
    
    // Validate measures
    FOR EACH measure IN cube.measures:
        IF measure.sql IS EMPTY:
            errors.ADD("Measure '" + measure.name + "' missing SQL expression")
        END IF
        
        IF NOT IS_VALID_AGGREGATION(measure.type):
            errors.ADD("Measure '" + measure.name + "' has invalid aggregation type")
        END IF
    END FOR
    
    RETURN ValidationResult(errors)
END FUNCTION
```

---

#### 11. Dimension/Measure Manager
**Purpose**: Manages individual dimension and measure definitions with their types, SQL expressions, and metadata.

**Key Responsibilities**:
- Stores dimension definitions (type, SQL, description)
- Stores measure definitions (aggregation type, SQL, description)
- Provides SQL expressions for query generation
- Handles calculated dimensions and measures
- Manages time dimension granularities

**Dimension Features**:
- **Types**: string, number, time, boolean
- **SQL Expression**: Column name or custom SQL
- **Time Granularities**: day, week, month, quarter, year (for time dimensions)
- **Calculated Dimensions**: Custom SQL expressions
- **Primary Keys**: Identification of primary key dimensions

**Measure Features**:
- **Aggregation Types**: sum, count, avg, min, max, count_distinct
- **SQL Expression**: Column or calculated expression
- **Calculated Measures**: Formulas and ratios
- **Format**: Currency, percentage, number formatting

**SQL Expression Handling**:
- Provides SQL expressions for SELECT clause
- Handles time granularity with DATE_TRUNC
- Applies calculated dimension expressions
- Generates aggregation functions for measures

**Type Management**:
- Validates dimension types match filter operators
- Ensures measure types are valid aggregations
- Provides type information for validation

**Pseudocode - Dimension/Measure SQL Expression**:
```
FUNCTION get_dimension_sql_expression(dimension):
    // Base SQL expression
    sql_expr = dimension.sql
    
    // Apply time granularity if time dimension
    IF dimension.type == "time" AND dimension.has_granularity():
        sql_expr = APPLY_TIME_GRANULARITY(sql_expr, dimension.granularity)
    END IF
    
    // Apply calculated dimension expression if exists
    IF dimension.has_calculated_expression():
        sql_expr = dimension.calculated_expression
        // Substitute dimension references in expression
        sql_expr = SUBSTITUTE_DIMENSION_REFERENCES(sql_expr, dimension.cube)
    END IF
    
    RETURN sql_expr
END FUNCTION

FUNCTION APPLY_TIME_GRANULARITY(sql_expr, granularity):
    SWITCH granularity:
        CASE "day":
            RETURN "DATE_TRUNC('day', " + sql_expr + ")"
        CASE "week":
            RETURN "DATE_TRUNC('week', " + sql_expr + ")"
        CASE "month":
            RETURN "DATE_TRUNC('month', " + sql_expr + ")"
        CASE "quarter":
            RETURN "DATE_TRUNC('quarter', " + sql_expr + ")"
        CASE "year":
            RETURN "DATE_TRUNC('year', " + sql_expr + ")"
        DEFAULT:
            RETURN sql_expr
    END SWITCH
END FUNCTION

FUNCTION get_measure_sql_expression(measure):
    // Base SQL expression
    sql_expr = measure.sql
    
    // Apply calculated measure expression if exists
    IF measure.has_calculated_expression():
        sql_expr = measure.calculated_expression
        // Substitute measure references in expression
        sql_expr = SUBSTITUTE_MEASURE_REFERENCES(sql_expr, measure.cube)
    END IF
    
    // Return with aggregation function
    aggregation = GET_AGGREGATION_FUNCTION(measure.type)
    RETURN aggregation + "(" + sql_expr + ")"
END FUNCTION

FUNCTION GET_AGGREGATION_FUNCTION(measure_type):
    SWITCH measure_type:
        CASE "sum":
            RETURN "SUM"
        CASE "count":
            RETURN "COUNT"
        CASE "avg":
            RETURN "AVG"
        CASE "min":
            RETURN "MIN"
        CASE "max":
            RETURN "MAX"
        CASE "count_distinct":
            RETURN "COUNT(DISTINCT"
        DEFAULT:
            RETURN "SUM"
    END SWITCH
END FUNCTION
```

---

#### 12. Relationship Manager
**Purpose**: Manages relationships between cubes, enabling multi-cube queries with automatic JOINs.

**Key Responsibilities**:
- Stores relationship definitions between cubes
- Determines join paths for multi-cube queries
- Provides join conditions for SQL generation
- Manages relationship types (belongs_to, has_many, has_one)

**Relationship Structure**:
- **From Cube**: Source cube name
- **From Field**: Field in source cube
- **To Cube**: Target cube name
- **To Field**: Field in target cube (usually primary key)
- **Type**: Relationship cardinality

**Join Path Resolution**:
- Finds shortest path between cubes when multiple relationships exist
- Handles indirect relationships (A → B → C)
- Determines join order for optimal performance
- Manages table aliases to avoid conflicts

**Join Generation**:
- Creates LEFT JOIN statements
- Generates join conditions (ON clauses)
- Handles multiple joins in single query
- Ensures proper join order

**Use Cases**:
- Multi-cube queries (e.g., orders + products)
- Cross-cube filtering
- Related data retrieval
- Complex analytical queries

### Performance (3 components)

#### 13. Cache Manager
**Purpose**: Provides multi-level caching to store query results and dramatically improve response times.

**Key Responsibilities**:
- Stores query results in cache with TTL (time-to-live)
- Checks cache before query execution
- Generates unique cache keys from queries
- Manages cache invalidation
- Supports both Redis (distributed) and in-memory caching

**Caching Strategy**:
- **Cache Key Generation**: Creates unique keys from query structure and user context
- **TTL Management**: Sets expiration times for cache entries
- **Cache Hit Detection**: Checks if query result exists in cache
- **Cache Storage**: Stores formatted results for fast retrieval

**Multi-Level Caching**:
1. **Redis Cache**: Distributed cache for multi-instance deployments
   - Shared across multiple server instances
   - Persistent across restarts
   - Supports large result sets
2. **In-Memory Cache**: Fast local cache for single-instance deployments
   - Lowest latency
   - Limited by memory size
   - Lost on restart

**Cache Key Components**:
- Query dimensions and measures
- Filter conditions
- Ordering specifications
- User context (for RLS-aware caching)
- Model version (for cache invalidation on schema changes)

**Cache Invalidation**:
- Time-based expiration (TTL)
- Schema change invalidation
- Manual invalidation via API
- Selective invalidation by cube

**Performance Impact**:
- Cache hits: <5ms response time
- Cache misses: Full query execution time
- Typical cache hit rate: 60-80% for repeated queries

**Pseudocode - Cache Management**:
```
FUNCTION get_cached_result(query, user_context):
    // Step 1: Generate cache key
    cache_key = GENERATE_CACHE_KEY(query, user_context)
    
    // Step 2: Check cache
    cached_result = CACHE.get(cache_key)
    
    IF cached_result IS NOT NULL:
        // Check if expired
        IF cached_result.is_expired():
            CACHE.delete(cache_key)
            RETURN NULL
        END IF
        
        RETURN cached_result
    END IF
    
    RETURN NULL
END FUNCTION

FUNCTION GENERATE_CACHE_KEY(query, user_context):
    // Include query structure
    key_parts = []
    key_parts.ADD("dims:" + SORT_AND_JOIN(query.dimensions))
    key_parts.ADD("meas:" + SORT_AND_JOIN(query.measures))
    key_parts.ADD("filters:" + SORT_AND_JOIN(query.filters))
    key_parts.ADD("order:" + SORT_AND_JOIN(query.order))
    key_parts.ADD("limit:" + query.limit)
    
    // Include user context for RLS-aware caching
    IF user_context IS NOT NULL:
        key_parts.ADD("user:" + user_context.user_id)
        key_parts.ADD("roles:" + SORT_AND_JOIN(user_context.roles))
    END IF
    
    // Include schema version for cache invalidation
    key_parts.ADD("schema_v:" + SCHEMA_VERSION)
    
    // Generate hash
    key_string = JOIN(key_parts, "|")
    cache_key = HASH(key_string)
    
    RETURN "query:" + cache_key
END FUNCTION

FUNCTION store_in_cache(query, result, user_context, ttl):
    cache_key = GENERATE_CACHE_KEY(query, user_context)
    
    cache_entry = {
        data: result.data,
        meta: result.meta,
        timestamp: GET_CURRENT_TIME(),
        expires_at: GET_CURRENT_TIME() + ttl
    }
    
    CACHE.set(cache_key, cache_entry, ttl)
END FUNCTION

FUNCTION invalidate_cache(cube_name):
    // Invalidate all cache entries for a specific cube
    cache_keys = CACHE.list_keys("query:*")
    
    FOR EACH key IN cache_keys:
        cached_entry = CACHE.get(key)
        IF cached_entry.contains_cube(cube_name):
            CACHE.delete(key)
        END IF
    END FOR
END FUNCTION
```

---

#### 14. Pre-Aggregation Manager
**Purpose**: Manages pre-computed aggregated data tables for common query patterns, providing sub-second response times.

**Key Responsibilities**:
- Matches incoming queries to pre-aggregation definitions
- Routes queries to pre-aggregation tables when available
- Manages pre-aggregation storage (materialized tables)
- Handles pre-aggregation creation and updates

**Pre-Aggregation Concept**:
- Pre-computes common aggregations (e.g., daily revenue by category)
- Stores results in materialized database tables
- Queries matching pre-aggregation pattern use pre-computed data
- Dramatically faster than computing aggregations on-the-fly

**Matching Algorithm**:
1. **Dimension Matching**: Query dimensions must be subset of pre-aggregation dimensions
2. **Measure Matching**: Query measures must be subset of pre-aggregation measures
3. **Time Granularity**: Time dimensions must match granularity (day, week, month)
4. **Filter Compatibility**: Query filters must be compatible with pre-aggregation

**Storage Management**:
- Creates materialized tables/views in database
- Names tables with predictable patterns
- Manages table lifecycle (create, update, drop)
- Tracks pre-aggregation metadata

**Query Routing**:
- Checks if query matches any pre-aggregation
- Routes to pre-aggregation table if match found
- Falls back to base table if no match
- Handles partial matches (future enhancement)

**Performance Impact**:
- Pre-aggregation queries: 10-50ms (vs 500ms+ for base queries)
- Reduces database load significantly
- Enables real-time dashboards

**Pseudocode - Pre-Aggregation Matching and Routing**:
```
FUNCTION find_matching_pre_aggregation(query):
    best_match = NULL
    best_score = 0
    
    FOR EACH pre_agg IN pre_aggregations:
        match_score = CALCULATE_MATCH_SCORE(query, pre_agg)
        
        IF match_score > best_score:
            best_score = match_score
            best_match = pre_agg
        END IF
    END FOR
    
    // Only return if match is good enough
    IF best_score >= MIN_MATCH_SCORE:
        RETURN best_match
    END IF
    
    RETURN NULL
END FUNCTION

FUNCTION CALCULATE_MATCH_SCORE(query, pre_agg):
    score = 0
    
    // Check dimension matching
    query_dims = SET(query.dimensions)
    pre_agg_dims = SET(pre_agg.dimensions)
    
    IF query_dims.IS_SUBSET_OF(pre_agg_dims):
        score = score + 50  // Good match
    ELSE:
        RETURN 0  // No match
    END IF
    
    // Check measure matching
    query_measures = SET(query.measures)
    pre_agg_measures = SET(pre_agg.measures)
    
    IF query_measures.IS_SUBSET_OF(pre_agg_measures):
        score = score + 30  // Good match
    ELSE:
        RETURN 0  // No match
    END IF
    
    // Check time granularity match
    IF query.has_time_dimension() AND pre_agg.has_time_dimension():
        IF query.time_granularity == pre_agg.granularity:
            score = score + 20  // Perfect granularity match
        ELSE:
            // Partial match, but can still use
            score = score + 10
        END IF
    END IF
    
    RETURN score
END FUNCTION

FUNCTION route_to_pre_aggregation(query, pre_agg):
    // Check if pre-aggregation exists and is fresh
    IF NOT PRE_AGG_STORAGE.exists(pre_agg):
        RETURN NULL  // Pre-aggregation not built yet
    END IF
    
    IF NOT PRE_AGG_STORAGE.is_fresh(pre_agg):
        RETURN NULL  // Pre-aggregation is stale
    END IF
    
    // Build SQL query against pre-aggregation table
    pre_agg_table = PRE_AGG_STORAGE.get_table_name(pre_agg)
    sql = BUILD_SQL_FROM_PRE_AGG(query, pre_agg, pre_agg_table)
    
    RETURN sql
END FUNCTION

FUNCTION BUILD_SQL_FROM_PRE_AGG(query, pre_agg, pre_agg_table):
    // Build SELECT clause from query dimensions/measures
    select_clause = BUILD_SELECT_CLAUSE(query.dimensions, query.measures)
    
    // FROM pre-aggregation table
    from_clause = "FROM " + pre_agg_table
    
    // Build WHERE clause from query filters
    where_clause = BUILD_WHERE_CLAUSE(query.filters)
    
    // Build ORDER BY
    order_by_clause = BUILD_ORDER_BY_CLAUSE(query.order)
    
    // Assemble SQL
    sql = "SELECT " + select_clause + "\n" + 
          from_clause + "\n" + 
          where_clause + "\n" + 
          order_by_clause
    
    RETURN sql
END FUNCTION
```

---

#### 15. Pre-Aggregation Scheduler
**Purpose**: Automatically refreshes pre-aggregations on schedule to keep data current.

**Key Responsibilities**:
- Parses refresh schedules from pre-aggregation definitions
- Schedules background refresh tasks
- Executes refresh queries to update pre-aggregation tables
- Provides manual refresh capability via API

**Refresh Strategies**:
- **Time-based**: Refresh every N seconds/minutes/hours/days
- **Manual**: Trigger refresh via API endpoint
- **Event-based**: Refresh on data changes (future enhancement)
- **Incremental**: Update only changed data (future enhancement)

**Scheduling Process**:
1. **Parse Schedule**: Reads refresh_key from pre-aggregation definition
2. **Create Task**: Schedules background task with specified interval
3. **Execute Refresh**: Runs aggregation query and updates table
4. **Track Status**: Monitors refresh success/failure

**Refresh Execution**:
- Generates aggregation query from pre-aggregation definition
- Executes query against base tables
- Replaces or updates pre-aggregation table
- Handles errors and retries

**Manual Refresh**:
- API endpoint: `POST /api/v1/pre-aggregations/{name}/refresh`
- Allows on-demand refresh for testing or urgent updates
- Returns refresh status and timing information

**Monitoring**:
- Tracks last refresh time
- Monitors refresh duration
- Alerts on refresh failures
- Provides refresh history

### Security (4 components)

#### 16. JWT Authentication
**Purpose**: Provides secure token-based authentication for API access.

**Key Responsibilities**:
- Validates JWT tokens from request headers
- Extracts user information from token claims
- Manages token expiration and refresh
- Creates security context for authenticated users

**Authentication Flow**:
1. **Token Extraction**: Reads JWT from Authorization header
2. **Token Validation**: Verifies signature and expiration
3. **Claim Extraction**: Extracts user ID, roles, permissions from token
4. **Context Creation**: Creates SecurityContext object
5. **Request Injection**: Injects context into request for downstream use

**Token Structure**:
- **Header**: Algorithm and token type
- **Payload**: User ID, roles, permissions, expiration
- **Signature**: Cryptographic signature for validation

**Security Features**:
- Signature verification prevents token tampering
- Expiration checking ensures tokens are current
- Role and permission claims for authorization
- Secure token storage recommendations

**Integration**:
- Used by API middleware for request authentication
- Provides user context to Query Engine
- Enables RLS and authorization decisions

**Pseudocode - JWT Authentication**:
```
FUNCTION authenticate_jwt(request):
    // Step 1: Extract token from header
    auth_header = request.headers.get("Authorization")
    IF auth_header IS NULL:
        RETURN NULL
    END IF
    
    // Extract token (format: "Bearer <token>")
    IF NOT auth_header.STARTS_WITH("Bearer "):
        RETURN NULL
    END IF
    
    token = auth_header.SUBSTRING(7)  // Remove "Bearer "
    
    // Step 2: Validate token signature
    IF NOT VALIDATE_TOKEN_SIGNATURE(token):
        RETURN NULL  // Invalid signature
    END IF
    
    // Step 3: Decode token
    TRY:
        claims = DECODE_JWT_TOKEN(token)
    CATCH decode_error:
        RETURN NULL
    END TRY
    
    // Step 4: Check expiration
    IF claims.expires_at < GET_CURRENT_TIME():
        RETURN NULL  // Token expired
    END IF
    
    // Step 5: Create security context
    security_context = {
        user_id: claims.user_id,
        roles: claims.roles,
        permissions: claims.permissions,
        tenant_id: claims.tenant_id,
        authenticated: true,
        auth_method: "JWT"
    }
    
    RETURN security_context
END FUNCTION

FUNCTION VALIDATE_TOKEN_SIGNATURE(token):
    // Split token into parts
    parts = token.SPLIT(".")
    IF parts.length != 3:
        RETURN false
    END IF
    
    header = parts[0]
    payload = parts[1]
    signature = parts[2]
    
    // Verify signature using secret key
    expected_signature = HMAC_SHA256(header + "." + payload, SECRET_KEY)
    
    RETURN signature == expected_signature
END FUNCTION
```

---

#### 17. API Key Authentication
**Purpose**: Provides simple key-based authentication for programmatic access.

**Key Responsibilities**:
- Validates API keys from request headers or query parameters
- Maps API keys to user accounts
- Manages API key lifecycle (create, revoke, rotate)
- Tracks API key usage

**Authentication Flow**:
1. **Key Extraction**: Reads API key from header or query parameter
2. **Key Lookup**: Finds associated user account
3. **Validation**: Checks if key is active and not expired
4. **Context Creation**: Creates SecurityContext with user information
5. **Usage Tracking**: Logs API key usage for monitoring

**API Key Management**:
- **Key Generation**: Creates cryptographically secure keys
- **Key Storage**: Stores keys securely (hashed)
- **Key Rotation**: Supports key rotation for security
- **Key Revocation**: Allows immediate key deactivation

**Use Cases**:
- Service-to-service authentication
- Automated scripts and tools
- Long-lived access tokens
- Integration with external systems

**Security Features**:
- Keys can be scoped to specific resources
- Supports key expiration
- Usage rate limiting
- Audit logging of key usage

**Pseudocode - API Key Authentication**:
```
FUNCTION authenticate_api_key(request):
    // Step 1: Extract API key from header or query parameter
    api_key = request.headers.get("X-API-Key")
    IF api_key IS NULL:
        api_key = request.query_params.get("api_key")
    END IF
    
    IF api_key IS NULL:
        RETURN NULL
    END IF
    
    // Step 2: Look up API key in database
    key_record = API_KEY_DATABASE.find_by_key(api_key)
    IF key_record IS NULL:
        RETURN NULL  // Key not found
    END IF
    
    // Step 3: Check if key is active
    IF NOT key_record.is_active:
        RETURN NULL  // Key is inactive
    END IF
    
    // Step 4: Check expiration
    IF key_record.expires_at IS NOT NULL AND key_record.expires_at < GET_CURRENT_TIME():
        RETURN NULL  // Key expired
    END IF
    
    // Step 5: Check rate limit
    IF EXCEEDS_RATE_LIMIT(api_key):
        RETURN NULL  // Rate limit exceeded
    END IF
    
    // Step 6: Update usage tracking
    RECORD_API_KEY_USAGE(api_key, request)
    
    // Step 7: Create security context
    security_context = {
        user_id: key_record.user_id,
        roles: key_record.roles,
        permissions: key_record.permissions,
        tenant_id: key_record.tenant_id,
        authenticated: true,
        auth_method: "API_KEY"
    }
    
    RETURN security_context
END FUNCTION

FUNCTION EXCEEDS_RATE_LIMIT(api_key):
    key_record = API_KEY_DATABASE.find_by_key(api_key)
    
    // Check requests in last minute
    recent_requests = COUNT_REQUESTS(api_key, last_minute=1)
    
    IF recent_requests > key_record.rate_limit:
        RETURN true
    END IF
    
    RETURN false
END FUNCTION
```

---

#### 18. Authorization (RBAC)
**Purpose**: Enforces role-based access control to restrict what users can access.

**Key Responsibilities**:
- Checks user permissions before query execution
- Enforces role-based access rules
- Manages resource-level permissions
- Provides permission checking API

**RBAC Model**:
- **Roles**: Collections of permissions (e.g., "analyst", "admin")
- **Permissions**: Actions on resources (e.g., "read:orders", "write:pre_aggregations")
- **Resource Types**: Cubes, pre-aggregations, system settings
- **Actions**: read, write, delete, manage

**Permission Checking**:
1. **Extract User Roles**: Gets roles from security context
2. **Load Permissions**: Retrieves permissions for user roles
3. **Check Resource**: Verifies user has permission for requested resource
4. **Check Action**: Verifies user has permission for requested action
5. **Allow/Deny**: Grants or denies access

**Access Control Rules**:
- **Cube Access**: Control which cubes users can query
- **Measure Access**: Restrict access to sensitive measures
- **Pre-aggregation Access**: Control who can manage pre-aggregations
- **System Access**: Admin-only operations

**Integration**:
- Applied by API middleware before query execution
- Works with JWT and API Key authentication
- Complements Row-Level Security

**Pseudocode - Authorization (RBAC)**:
```
FUNCTION check_authorization(user_context, resource, action):
    // Step 1: Get user roles
    user_roles = user_context.roles
    IF user_roles.IS_EMPTY():
        RETURN false  // No roles assigned
    END IF
    
    // Step 2: Collect all permissions from roles
    all_permissions = NEW Set()
    
    FOR EACH role IN user_roles:
        role_permissions = ROLE_DATABASE.get_permissions(role)
        all_permissions.ADD_ALL(role_permissions)
    END FOR
    
    // Step 3: Check if user has required permission
    required_permission = action + ":" + resource
    
    IF all_permissions.CONTAINS(required_permission):
        RETURN true
    END IF
    
    // Step 4: Check wildcard permissions
    IF all_permissions.CONTAINS(action + ":*"):
        RETURN true  // User has action on all resources
    END IF
    
    IF all_permissions.CONTAINS("*:" + resource):
        RETURN true  // User has all actions on resource
    END IF
    
    IF all_permissions.CONTAINS("*:*"):
        RETURN true  // User has all permissions (admin)
    END IF
    
    RETURN false
END FUNCTION

FUNCTION authorize_query(user_context, query):
    // Check cube access
    cubes = EXTRACT_CUBES(query)
    
    FOR EACH cube IN cubes:
        IF NOT check_authorization(user_context, "cube:" + cube.name, "read"):
            RETURN ERROR("Access denied to cube: " + cube.name)
        END IF
    END FOR
    
    // Check measure access (for sensitive measures)
    FOR EACH measure IN query.measures:
        IF IS_SENSITIVE_MEASURE(measure):
            IF NOT check_authorization(user_context, "measure:" + measure.full_reference, "read"):
                RETURN ERROR("Access denied to measure: " + measure.full_reference)
            END IF
        END IF
    END FOR
    
    RETURN true
END FUNCTION
```

---

#### 19. Row-Level Security (RLS)
**Purpose**: Filters data rows based on user context, ensuring users only see authorized data.

**Key Responsibilities**:
- Applies RLS rules from semantic models
- Substitutes user context variables in RLS SQL
- Injects RLS conditions into WHERE clauses
- Ensures data isolation between users/tenants

**RLS Rule Definition**:
- Defined in semantic model as SQL expression
- Uses variables like `${USER_DEPARTMENT}`, `${USER_REGION}`
- Applied automatically to all queries for that cube
- Cannot be bypassed by users

**RLS Application Process**:
1. **Rule Extraction**: Gets RLS SQL from cube definition
2. **Context Substitution**: Replaces variables with user context values
3. **SQL Injection**: Adds RLS condition to WHERE clause
4. **Query Execution**: Executes query with RLS applied

**Use Cases**:
- **Multi-tenancy**: Isolate data by tenant/organization
- **Department Access**: Restrict access by department
- **Regional Access**: Filter by geographic region
- **Role-based Filtering**: Different data for different roles

**Security Guarantees**:
- Applied at SQL level (cannot be bypassed)
- Automatic application (no user action required)
- Transparent to end users
- Logged for audit purposes

**Example RLS Rules**:
- `department = ${USER_DEPARTMENT}`: Users see only their department's data
- `region IN ${USER_REGIONS}`: Users see data for their assigned regions
- `created_by = ${USER_ID}`: Users see only data they created

### Observability (2 components)

#### 20. Query Logger
**Purpose**: Provides structured logging of all queries for auditing, debugging, and analysis.

**Key Responsibilities**:
- Logs every query execution with complete context
- Records execution time and performance metrics
- Tracks cache hits and misses
- Captures user context and security information
- Provides query log API for retrieval

**Log Structure**:
- **Timestamp**: When query was executed
- **User Context**: User ID, roles, IP address
- **Query Details**: Dimensions, measures, filters, ordering
- **Execution Metrics**: Execution time, row count, cache status
- **Generated SQL**: SQL that was executed (for debugging)
- **Error Information**: Error details if query failed

**Logging Levels**:
- **INFO**: Successful query executions
- **WARNING**: Slow queries, cache misses
- **ERROR**: Query failures, validation errors
- **DEBUG**: Detailed execution traces

**Use Cases**:
- **Audit Trail**: Compliance and security auditing
- **Performance Analysis**: Identify slow queries
- **Usage Analytics**: Understand query patterns
- **Debugging**: Troubleshoot query issues
- **Cost Analysis**: Track database usage

**Log Storage**:
- Structured JSON format for easy parsing
- Can be stored in files, database, or log aggregation systems
- Supports log rotation and retention policies
- Query log API for programmatic access

**Integration**:
- Integrated into Query Engine execution flow
- Logs before and after query execution
- Captures errors and exceptions
- Works with all authentication methods

**Pseudocode - Query Logging**:
```
FUNCTION log_query(query, result, execution_time, user_context, cache_hit, pre_agg_used):
    log_entry = {
        timestamp: GET_CURRENT_TIME(),
        user_id: user_context.user_id IF user_context IS NOT NULL ELSE "anonymous",
        user_roles: user_context.roles IF user_context IS NOT NULL ELSE [],
        query: {
            dimensions: query.dimensions,
            measures: query.measures,
            filters: query.filters,
            order: query.order,
            limit: query.limit
        },
        execution_time_ms: execution_time,
        cache_hit: cache_hit,
        pre_aggregation_used: pre_agg_used,
        rows_returned: result.row_count,
        sql_generated: result.sql IF result.has_sql() ELSE NULL,
        error: NULL
    }
    
    // Write to structured log
    LOGGER.info(JSON.stringify(log_entry))
    
    // Optionally store in database for analytics
    IF ENABLE_QUERY_ANALYTICS:
        QUERY_ANALYTICS_DB.insert(log_entry)
    END IF
END FUNCTION

FUNCTION log_query_error(query, error, user_context):
    log_entry = {
        timestamp: GET_CURRENT_TIME(),
        user_id: user_context.user_id IF user_context IS NOT NULL ELSE "anonymous",
        query: {
            dimensions: query.dimensions,
            measures: query.measures,
            filters: query.filters
        },
        error: {
            type: error.type,
            message: error.message,
            stack_trace: error.stack_trace
        },
        execution_time_ms: NULL
    }
    
    LOGGER.error(JSON.stringify(log_entry))
END FUNCTION
```

---

#### 21. Metrics Collector (Prometheus)
**Purpose**: Collects and exposes performance metrics in Prometheus format for monitoring and alerting.

**Key Responsibilities**:
- Tracks query execution metrics (count, duration, errors)
- Monitors cache performance (hits, misses, hit rate)
- Records system metrics (active connections, queue size)
- Exposes metrics via Prometheus endpoint
- Provides metrics for alerting

**Metrics Collected**:

**Query Metrics**:
- `query_count`: Total number of queries executed
- `query_duration_seconds`: Query execution time histogram
- `query_errors`: Number of failed queries
- `query_cache_hits`: Number of cache hits
- `query_cache_misses`: Number of cache misses

**System Metrics**:
- `active_connections`: Number of active database connections
- `connection_pool_size`: Connection pool size
- `pre_aggregation_count`: Number of pre-aggregations
- `schema_reload_count`: Number of schema reloads

**Performance Metrics**:
- `sql_generation_time`: Time to generate SQL
- `cache_lookup_time`: Time to check cache
- `pre_agg_match_time`: Time to match pre-aggregations

**Metrics Format**:
- Prometheus-compatible format
- Exposed at `/metrics` endpoint
- Supports labels for filtering and grouping
- Histogram buckets for latency analysis

**Use Cases**:
- **Monitoring**: Real-time system health monitoring
- **Alerting**: Set up alerts for errors, slow queries
- **Performance Analysis**: Track performance trends
- **Capacity Planning**: Understand system load
- **SLA Tracking**: Monitor query performance SLAs

**Integration**:
- Integrated into Query Engine
- Records metrics automatically
- Works with Prometheus, Grafana, and other monitoring tools

### Database (3 components)

#### 22. PostgreSQL Connector
**Purpose**: Provides full-featured connectivity to PostgreSQL databases with async execution and connection pooling.

**Key Responsibilities**:
- Manages connection pool to PostgreSQL database
- Executes SQL queries asynchronously
- Handles query results and formatting
- Manages connection lifecycle and health
- Provides database-specific optimizations

**Connection Management**:
- **Connection Pool**: Maintains pool of reusable connections
- **Pool Configuration**: Min/max connections, timeout settings
- **Connection Health**: Monitors and replaces unhealthy connections
- **Async Execution**: Non-blocking query execution using asyncpg

**Query Execution**:
- **Parameterized Queries**: Prevents SQL injection
- **Result Formatting**: Converts database rows to dictionaries
- **Error Handling**: Handles database errors gracefully
- **Timeout Management**: Prevents long-running queries

**PostgreSQL-Specific Features**:
- **JSON Support**: Handles PostgreSQL JSON types
- **Array Support**: Supports PostgreSQL array types
- **Advanced Types**: Handles UUID, timestamp, numeric types
- **Query Optimization**: Leverages PostgreSQL query planner

**Performance Features**:
- Async execution for high concurrency
- Connection pooling for efficiency
- Prepared statements for repeated queries
- Result streaming for large datasets

**Error Handling**:
- Connection errors with retry logic
- Query timeout handling
- Transaction rollback on errors
- Detailed error messages

**Pseudocode - Database Connector Execution**:
```
FUNCTION execute_query(sql, parameters):
    connection = NULL
    
    TRY:
        // Step 1: Acquire connection from pool
        connection = CONNECTION_POOL.acquire(timeout=30)
        
        IF connection IS NULL:
            RETURN ERROR("Failed to acquire database connection")
        END IF
        
        // Step 2: Execute query with timeout
        start_time = GET_CURRENT_TIME()
        result = connection.execute(sql, parameters, timeout=60)
        execution_time = GET_CURRENT_TIME() - start_time
        
        // Step 3: Format results
        formatted_result = FORMAT_RESULTS(result)
        
        // Step 4: Release connection
        CONNECTION_POOL.release(connection)
        
        RETURN formatted_result
        
    CATCH connection_error:
        IF connection IS NOT NULL:
            CONNECTION_POOL.release(connection)
        END IF
        
        // Retry with exponential backoff
        RETURN RETRY_WITH_BACKOFF(sql, parameters, retry_count=3)
        
    CATCH timeout_error:
        IF connection IS NOT NULL:
            connection.cancel()  // Cancel query
            CONNECTION_POOL.release(connection)
        END IF
        
        RETURN ERROR("Query timeout after 60 seconds")
        
    CATCH sql_error:
        IF connection IS NOT NULL:
            CONNECTION_POOL.release(connection)
        END IF
        
        RETURN ERROR("SQL error: " + sql_error.message)
    END TRY
END FUNCTION

FUNCTION FORMAT_RESULTS(result):
    formatted_rows = []
    
    FOR EACH row IN result.rows:
        formatted_row = {}
        
        FOR EACH column IN result.columns:
            value = row[column.name]
            
            // Convert database types to JSON-serializable types
            IF value IS Decimal:
                formatted_row[column.name] = value.to_float()
            ELSE IF value IS datetime:
                formatted_row[column.name] = value.to_iso_string()
            ELSE IF value IS date:
                formatted_row[column.name] = value.to_iso_string()
            ELSE:
                formatted_row[column.name] = value
            END IF
        END FOR
        
        formatted_rows.ADD(formatted_row)
    END FOR
    
    RETURN formatted_rows
END FUNCTION

FUNCTION RETRY_WITH_BACKOFF(sql, parameters, retry_count):
    FOR attempt IN 1 TO retry_count:
        wait_time = CALCULATE_BACKOFF(attempt)  // 1s, 2s, 4s
        SLEEP(wait_time)
        
        TRY:
            RETURN execute_query(sql, parameters)
        CATCH error:
            IF attempt == retry_count:
                RETURN ERROR("Failed after " + retry_count + " retries: " + error.message)
            END IF
        END TRY
    END FOR
END FUNCTION
```

---

#### 23. MySQL Connector
**Purpose**: Provides connectivity to MySQL databases with async execution support.

**Key Responsibilities**:
- Manages connections to MySQL database
- Executes SQL queries asynchronously
- Handles MySQL-specific data types
- Provides connection pooling

**MySQL-Specific Features**:
- **Data Type Handling**: Converts MySQL types to Python types
- **Character Sets**: Handles UTF-8 and other character sets
- **Transaction Support**: Manages transactions appropriately
- **MySQL Dialect**: Adapts SQL generation for MySQL syntax

**Connection Management**:
- Uses aiomysql for async MySQL operations
- Connection pooling similar to PostgreSQL
- Health monitoring and connection recovery
- Configurable pool settings

**Compatibility**:
- Works with same semantic models as PostgreSQL
- Handles SQL dialect differences automatically
- Supports same query patterns
- Compatible with all platform features

---

#### 24. Base Connector Interface
**Purpose**: Defines abstract interface for database connectors, enabling extensibility to other databases.

**Key Responsibilities**:
- Defines common interface all connectors must implement
- Specifies required methods and signatures
- Enables pluggable connector architecture
- Provides base functionality shared by all connectors

**Interface Methods**:
- `execute_query(sql, parameters)`: Execute SQL and return results
- `get_schema()`: Retrieve database schema information
- `test_connection()`: Verify database connectivity
- `get_dialect()`: Return SQL dialect information
- `close()`: Clean up connections

**Extensibility**:
- New databases can be added by implementing interface
- No changes to core platform required
- Consistent behavior across all databases
- Easy testing with mock connectors

**Future Connectors**:
- Snowflake connector (cloud data warehouse)
- BigQuery connector (Google Cloud)
- Redshift connector (AWS)
- SQL Server connector (Microsoft)
- SQLite connector (embedded database)

**Benefits**:
- Database-agnostic platform design
- Easy to add new database support
- Consistent API across databases
- Testable with mock implementations

### Developer Experience (3 components)

#### 25. Hot Reload (File Watcher)
**Purpose**: Automatically reloads semantic models when files change during development, eliminating need for server restarts.

**Key Responsibilities**:
- Monitors model files for changes (create, modify, delete)
- Detects file system events in models directory
- Triggers schema reload when changes detected
- Updates Query Engine with new schema
- Provides feedback on reload status

**File Watching Process**:
1. **Directory Monitoring**: Watches models directory for file changes
2. **Change Detection**: Detects when YAML files are modified
3. **Debouncing**: Waits for file writes to complete (prevents multiple reloads)
4. **Schema Reload**: Reloads all model files
5. **Engine Update**: Updates Query Engine with new schema
6. **Status Notification**: Logs reload success or errors

**Development Benefits**:
- **Fast Iteration**: No server restart needed
- **Immediate Feedback**: See changes instantly
- **Error Detection**: Catch model errors quickly
- **Productivity**: Faster development cycle

**Reload Behavior**:
- **Full Reload**: Reloads all models, not just changed files
- **Validation**: Validates new schema before applying
- **Error Handling**: Preserves old schema if reload fails
- **Pre-aggregation Update**: Updates pre-aggregation registrations

**Configuration**:
- Enabled by default in development mode
- Can be disabled for production
- Configurable debounce delay
- Watch multiple directories

**Pseudocode - Hot Reload File Watching**:
```
FUNCTION watch_model_files(models_directory):
    // Step 1: Set up file watcher
    watcher = CREATE_FILE_WATCHER(models_directory)
    
    // Step 2: Register change handler
    watcher.on_change = FUNCTION(file_path, event_type):
        // Debounce rapid changes
        DEBOUNCE(500ms, FUNCTION():
            TRY:
                // Reload schema
                new_schema = SCHEMA_LOADER.reload(models_directory)
                
                // Update Query Engine
                QUERY_ENGINE.update_schema(new_schema)
                
                // Update SQL Builder
                SQL_BUILDER.update_schema(new_schema)
                
                // Update Pre-Aggregation Manager
                PRE_AGGREGATION_MANAGER.register_from_schema(new_schema)
                
                // Log success
                LOGGER.info("Schema reloaded: " + file_path)
                
            CATCH error:
                LOGGER.error("Failed to reload schema: " + error.message)
                // Keep old schema on error
            END TRY
        END FUNCTION)
    END FUNCTION
    
    // Step 3: Start watching
    watcher.start()
    
    RETURN watcher
END FUNCTION

FUNCTION DEBOUNCE(delay, callback):
    // Cancel previous timeout
    IF debounce_timer IS NOT NULL:
        CANCEL_TIMER(debounce_timer)
    END IF
    
    // Set new timeout
    debounce_timer = SET_TIMEOUT(callback, delay)
END FUNCTION
```

---

#### 26. Python SDK
**Purpose**: Provides Python client library for programmatic interaction with the semantic layer platform.

**Key Responsibilities**:
- Provides easy-to-use Python API for querying
- Handles HTTP communication with REST API
- Formats requests and parses responses
- Provides type hints and documentation
- Handles authentication and errors

**SDK Features**:
- **Query Execution**: Execute semantic queries from Python code
- **Schema Access**: Retrieve available cubes, dimensions, measures
- **Type Safety**: Type hints for better IDE support
- **Error Handling**: Clear error messages and exceptions
- **Async Support**: Async/await support for concurrent queries

**Usage Pattern**:
```python
# Initialize client
client = SemanticLayerClient(api_url="http://localhost:8000")

# Execute query
result = client.query(
    dimensions=["orders.status"],
    measures=["orders.revenue", "orders.count"],
    filters=[{"dimension": "orders.status", "operator": "equals", "value": "completed"}]
)

# Access results
for row in result.data:
    print(f"{row['orders_status']}: {row['orders_revenue']}")
```

**Integration Benefits**:
- **Data Science**: Easy integration with Pandas, Jupyter
- **ML Workflows**: Embed queries in ML pipelines
- **Automation**: Script-based query execution
- **Testing**: Programmatic testing of queries

**Advanced Features**:
- **Batch Queries**: Execute multiple queries efficiently
- **Result Streaming**: Handle large result sets
- **Caching**: Client-side caching support
- **Authentication**: Handles JWT and API key auth

**Pseudocode - Python SDK Client**:
```
CLASS SemanticLayerClient:
    FUNCTION __init__(api_url, api_key=None, jwt_token=None):
        self.api_url = api_url
        self.api_key = api_key
        self.jwt_token = jwt_token
        self.http_client = CREATE_HTTP_CLIENT()
    END FUNCTION
    
    FUNCTION query(dimensions, measures, filters=None, order=None, limit=None):
        // Build query request
        query_request = {
            dimensions: dimensions,
            measures: measures
        }
        
        IF filters IS NOT NULL:
            query_request.filters = filters
        END IF
        
        IF order IS NOT NULL:
            query_request.order = order
        END IF
        
        IF limit IS NOT NULL:
            query_request.limit = limit
        END IF
        
        // Execute HTTP request
        headers = BUILD_HEADERS(self.api_key, self.jwt_token)
        response = self.http_client.post(
            self.api_url + "/api/v1/query",
            json=query_request,
            headers=headers
        )
        
        // Parse response
        IF response.status_code == 200:
            return response.json()
        ELSE:
            RAISE ERROR("Query failed: " + response.text)
        END IF
    END FUNCTION
    
    FUNCTION get_schema():
        headers = BUILD_HEADERS(self.api_key, self.jwt_token)
        response = self.http_client.get(
            self.api_url + "/api/v1/schema",
            headers=headers
        )
        
        IF response.status_code == 200:
            return response.json()
        ELSE:
            RAISE ERROR("Failed to get schema: " + response.text)
        END IF
    END FUNCTION
    
    FUNCTION BUILD_HEADERS(api_key, jwt_token):
        headers = {"Content-Type": "application/json"}
        
        IF api_key IS NOT NULL:
            headers["X-API-Key"] = api_key
        END IF
        
        IF jwt_token IS NOT NULL:
            headers["Authorization"] = "Bearer " + jwt_token
        END IF
        
        RETURN headers
    END FUNCTION
END CLASS
```

---

#### 27. CLI Tools
**Purpose**: Provides command-line interface for development, validation, and operations.

**Key Responsibilities**:
- Validates semantic models for correctness
- Tests model definitions with sample queries
- Starts development server with hot reload
- Provides helpful error messages and feedback

**Available Commands**:

**1. `validate` Command**:
- **Purpose**: Validates YAML semantic model files
- **Usage**: `semanticquark validate <path>`
- **Features**:
  - Validates YAML syntax
  - Checks required fields
  - Validates SQL expressions
  - Reports cube, dimension, measure counts
  - Provides detailed error messages

**2. `test` Command**:
- **Purpose**: Tests semantic models with sample queries
- **Usage**: `semanticquark test <path>`
- **Features**:
  - Tests all cubes in schema
  - Validates dimension accessibility
  - Validates measure accessibility
  - Reports test results
  - Identifies issues early

**3. `dev` Command**:
- **Purpose**: Starts development server
- **Usage**: `semanticquark dev [--port PORT] [--reload]`
- **Features**:
  - Starts FastAPI server
  - Enables hot reload for development
  - Configurable host and port
  - Auto-reloads on code changes
  - Development-friendly defaults

**CLI Benefits**:
- **Quick Validation**: Validate models before deployment
- **Local Development**: Easy local server startup
- **CI/CD Integration**: Use in automated pipelines
- **Developer Productivity**: Fast feedback loop

**Error Messages**:
- Clear, actionable error messages
- Suggests fixes for common issues
- Points to specific files and lines
- Provides context for errors

---

## Sequence Diagrams and Component Flow Diagrams

For detailed sequence diagrams and component flow diagrams showing how all components interact, see the separate document:

**📄 [SEQUENCE_AND_FLOW_DIAGRAMS.md](SEQUENCE_AND_FLOW_DIAGRAMS.md)**

This document includes:

### Sequence Diagrams:
1. **Complete Query Execution Sequence** - Full flow from client request to response
2. **Authentication and Authorization Sequence** - Security flow with JWT/API keys and RBAC
3. **Caching Flow Sequence** - Cache hit/miss scenarios
4. **Pre-Aggregation Routing Sequence** - How queries are routed to pre-aggregations
5. **Error Handling Sequence** - Error handling at different stages

### Component Flow Diagrams:
1. **Complete Query Execution Flow** - End-to-end query processing
2. **Authentication and Security Flow** - Auth, authorization, and RLS flow
3. **Caching Decision Flow** - Cache decision tree
4. **Pre-Aggregation Matching Flow** - How queries match pre-aggregations
5. **Multi-Cube Join Flow** - Automatic JOIN generation for multi-cube queries
6. **Schema Loading and Hot Reload Flow** - Model loading and development reload

### Additional Resources:
- **Component Interaction Matrix** - Shows which components interact with each other
- **Data Flow Summary** - Quick reference for common flows

These diagrams provide visual representations of:
- Component interactions and message passing
- Decision points and conditional flows
- Error handling paths
- Performance optimization flows
- Security enforcement flows

All diagrams use ASCII art format suitable for documentation and academic papers.

