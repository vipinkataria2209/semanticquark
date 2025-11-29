# Sequence Diagrams and Component Flow Diagrams

This document contains detailed sequence diagrams and component flow diagrams for the Semantic Layer Platform, showing how components interact during various operations.

---

## 1. Sequence Diagrams

### 1.1 Complete Query Execution Sequence

This sequence diagram shows the complete flow of a semantic query from client request to response, including all component interactions.

```
┌──────┐    ┌─────┐    ┌───────┐    ┌────────┐    ┌─────────┐    ┌──────────┐    ┌────────┐    ┌────────┐
│Client│    │ API │    │Parser │    │ Schema │    │   SQL   │    │   Query  │    │ Cache  │    │   DB   │
│      │    │Layer│    │       │    │Manager │    │ Builder │    │  Engine  │    │Manager │    │Connector│
└───┬──┘    └──┬──┘    └───┬───┘    └───┬────┘    └────┬────┘    └────┬─────┘    └───┬────┘    └───┬────┘
    │          │            │            │              │              │              │              │
    │ POST /api/v1/query    │            │              │              │              │              │
    │ (JSON)                │            │              │              │              │              │
    │──────────────────────>│            │              │              │              │              │
    │          │            │            │              │              │              │              │
    │          │ Authenticate (JWT/API Key)            │              │              │              │
    │          │───────────────────────────────────────┼──────────────>│              │              │
    │          │            │            │              │              │              │              │
    │          │ Security Context                      │              │              │              │
    │          │<───────────────────────────────────────┼──────────────│              │              │
    │          │            │            │              │              │              │              │
    │          │ parse_query()          │              │              │              │              │
    │          │───────────>│            │              │              │              │              │
    │          │            │            │              │              │              │              │
    │          │            │ Parse JSON │              │              │              │              │
    │          │            │ Extract dims/measures    │              │              │              │
    │          │            │            │              │              │              │              │
    │          │ Query Object           │              │              │              │              │
    │          │<───────────│            │              │              │              │              │
    │          │            │            │              │              │              │              │
    │          │ validate_query()       │              │              │              │              │
    │          │────────────────────────>│              │              │              │              │
    │          │            │            │              │              │              │              │
    │          │            │            │ Resolve cubes│              │              │              │
    │          │            │            │ Check dims   │              │              │              │
    │          │            │            │ Check measures│              │              │              │
    │          │            │            │              │              │              │              │
    │          │ Validated Query        │              │              │              │              │
    │          │<────────────────────────│              │              │              │              │
    │          │            │            │              │              │              │              │
    │          │ execute_query()                        │              │              │              │
    │          │────────────────────────────────────────>│              │              │              │
    │          │            │            │              │              │              │              │
    │          │            │            │              │              │ Optimize Query│              │
    │          │            │            │              │              │<──────────────│              │
    │          │            │            │              │              │              │              │
    │          │            │            │              │              │ Optimized Query│              │
    │          │            │            │              │              │──────────────>│              │
    │          │            │            │              │              │              │              │
    │          │            │            │              │              │ Check Cache   │              │
    │          │            │            │              │              │──────────────>│              │
    │          │            │            │              │              │              │              │
    │          │            │            │              │              │ Cache Result  │              │
    │          │            │            │              │              │<──────────────│              │
    │          │            │            │              │              │              │              │
    │          │            │            │              │              │ [Cache Miss]  │              │
    │          │            │            │              │              │              │              │
    │          │            │            │              │              │ Check Pre-Agg │              │
    │          │            │            │              │              │──────────────>│              │
    │          │            │            │              │              │              │              │
    │          │            │            │              │              │ Pre-Agg Match  │              │
    │          │            │            │              │              │<──────────────│              │
    │          │            │            │              │              │              │              │
    │          │            │            │              │              │ Apply RLS     │              │
    │          │            │            │              │              │──────────────>│              │
    │          │            │            │              │              │              │              │
    │          │            │            │              │              │ RLS Applied   │              │
    │          │            │            │              │              │<──────────────│              │
    │          │            │            │              │              │              │              │
    │          │            │            │              │ build_sql()  │              │              │
    │          │            │            │              │<─────────────│              │              │
    │          │            │            │              │              │              │              │
    │          │            │            │ Get cube info│              │              │              │
    │          │            │            │<─────────────│              │              │              │
    │          │            │            │              │              │              │              │
    │          │            │            │ Cube/Dim/Meas│              │              │              │
    │          │            │            │──────────────>│              │              │              │
    │          │            │            │              │              │              │              │
    │          │            │            │              │ Generate SQL │              │              │
    │          │            │            │              │ (SELECT, FROM,│              │              │
    │          │            │            │              │ WHERE, etc)  │              │              │
    │          │            │            │              │              │              │              │
    │          │            │            │              │ SQL String   │              │              │
    │          │            │            │              │──────────────>│              │              │
    │          │            │            │              │              │              │              │
    │          │            │            │              │              │ execute_sql() │              │
    │          │            │            │              │              │───────────────>│              │
    │          │            │            │              │              │              │              │
    │          │            │            │              │              │              │ Execute SQL  │
    │          │            │            │              │              │              │ on Database  │
    │          │            │            │              │              │              │──────────────>│
    │          │            │            │              │              │              │              │
    │          │            │            │              │              │              │ [DB Processing│
    │          │            │            │              │              │              │  ~120ms]     │
    │          │            │            │              │              │              │              │
    │          │            │            │              │              │              │ Results      │
    │          │            │            │              │              │              │<──────────────│
    │          │            │            │              │              │              │              │
    │          │            │            │              │              │ Formatted Result│              │
    │          │            │            │              │              │<───────────────│              │
    │          │            │            │              │              │              │              │
    │          │            │            │              │              │ Store in Cache │              │
    │          │            │            │              │              │──────────────>│              │
    │          │            │            │              │              │              │              │
    │          │            │            │              │              │ Log Query     │              │
    │          │            │            │              │──────────────>│              │              │
    │          │            │            │              │              │              │              │
    │          │            │            │              │              │ Record Metrics│              │
    │          │            │            │              │──────────────>│              │              │
    │          │            │            │              │              │              │              │
    │          │            │            │              │              │ Final Result  │              │
    │          │            │            │              │<──────────────│              │              │
    │          │            │            │              │              │              │              │
    │          │ JSON Response          │              │              │              │              │
    │          │<───────────────────────────────────────│              │              │              │
    │          │            │            │              │              │              │              │
    │ 200 OK   │            │            │              │              │              │              │
    │ JSON     │            │            │              │              │              │              │
    │<─────────│            │            │              │              │              │              │
    │          │            │            │              │              │              │              │
    
Total Time: ~145ms
├─ API Layer: 2ms
├─ Parser: 5ms  
├─ Validator: 3ms
├─ Query Engine: 2ms
├─ SQL Builder: 8ms
├─ Database: 120ms
├─ Formatting: 3ms
└─ Logging/Metrics: 2ms
```

**Figure 1. Complete query execution sequence diagram**

---

### 1.2 Authentication and Authorization Sequence

This sequence diagram shows how authentication and authorization work together to secure API access.

```
┌──────┐    ┌─────┐    ┌──────────┐    ┌────────────┐    ┌──────────────┐    ┌────────┐
│Client│    │ API │    │   Auth   │    │Authorization│    │   Security   │    │ Query  │
│      │    │Layer│    │ (JWT/Key)│    │   (RBAC)   │    │   Context    │    │ Engine │
└───┬──┘    └──┬──┘    └────┬─────┘    └─────┬──────┘    └──────┬───────┘    └───┬────┘
    │          │             │                 │                  │                │
    │ POST /query            │                 │                  │                │
    │ (with token/key)       │                 │                  │                │
    │───────────────────────>│                 │                  │                │
    │          │             │                 │                  │                │
    │          │ authenticate()              │                  │                │
    │          │───────────>│                 │                  │                │
    │          │             │                 │                  │                │
    │          │             │ Extract token/key│                  │                │
    │          │             │ Validate signature│                  │                │
    │          │             │ Check expiration │                  │                │
    │          │             │                  │                  │                │
    │          │             │ User Info        │                  │                │
    │          │             │ (user_id, roles) │                  │                │
    │          │             │─────────────────>│                  │                │
    │          │             │                  │                  │                │
    │          │             │                  │ Create Security  │                │
    │          │             │                  │ Context          │                │
    │          │             │                  │─────────────────>│                │
    │          │             │                  │                  │                │
    │          │             │                  │ Security Context │                │
    │          │             │                  │<─────────────────│                │
    │          │             │                  │                  │                │
    │          │             │ Security Context│                  │                │
    │          │             │<─────────────────│                  │                │
    │          │             │                  │                  │                │
    │          │ Security Context               │                  │                │
    │          │<─────────────│                 │                  │                │
    │          │             │                  │                  │                │
    │          │ authorize("query", "execute")  │                  │                │
    │          │───────────────────────────────>│                  │                │
    │          │             │                  │                  │                │
    │          │             │                  │ Check permissions│                │
    │          │             │                  │ Get user roles   │                │
    │          │             │                  │ Check resource   │                │
    │          │             │                  │                  │                │
    │          │             │                  │ Permission Check │                │
    │          │             │                  │ Result           │                │
    │          │             │                  │<─────────────────│                │
    │          │             │                  │                  │                │
    │          │             │                  │                  │                │
    │          │ [Authorized] │                  │                  │                │
    │          │<─────────────│                 │                  │                │
    │          │             │                  │                  │                │
    │          │ Execute query with context     │                  │                │
    │          │───────────────────────────────────────────────────────────────────>│
    │          │             │                  │                  │                │
    │          │             │                  │                  │ Apply RLS      │
    │          │             │                  │                  │<───────────────│
    │          │             │                  │                  │                │
    │          │             │                  │                  │ Query with RLS │
    │          │             │                  │                  │───────────────>│
    │          │             │                  │                  │                │
    │          │             │                  │                  │ Results        │
    │          │             │                  │                  │<───────────────│
    │          │             │                  │                  │                │
    │          │ Results     │                  │                  │                │
    │          │<───────────────────────────────────────────────────────────────────│
    │          │             │                  │                  │                │
    │ 200 OK   │             │                  │                  │                │
    │<─────────│             │                  │                  │                │
    │          │             │                  │                  │                │
```

**Figure 2. Authentication and authorization sequence diagram**

---

### 1.3 Caching Flow Sequence

This sequence diagram shows how caching works, including cache hits and misses.

```
┌──────┐    ┌─────┐    ┌─────────┐    ┌────────┐    ┌──────────┐    ┌────────┐
│Client│    │ API │    │  Query  │    │ Cache  │    │   SQL    │    │   DB   │
│      │    │Layer│    │ Engine  │    │Manager │    │ Builder  │    │Connector│
└───┬──┘    └──┬──┘    └────┬────┘    └───┬────┘    └────┬─────┘    └───┬────┘
    │          │             │              │              │              │
    │ POST /query            │              │              │              │
    │───────────────────────>│              │              │              │
    │          │             │              │              │              │
    │          │ execute_query()            │              │              │
    │          │────────────>│              │              │              │
    │          │             │              │              │              │
    │          │             │ Generate Cache Key         │              │
    │          │             │──────────────>│              │              │
    │          │             │              │              │              │
    │          │             │              │ Cache Key    │              │
    │          │             │              │<─────────────│              │
    │          │             │              │              │              │
    │          │             │ Check Cache  │              │              │
    │          │             │──────────────>│              │              │
    │          │             │              │              │              │
    │          │             │              │ [Cache Hit]  │              │
    │          │             │              │ OR           │              │
    │          │             │              │ [Cache Miss] │              │
    │          │             │              │              │              │
    │          │             │ Cache Result │              │              │
    │          │             │<──────────────│              │              │
    │          │             │              │              │              │
    │          │             │ IF Cache Hit:│              │              │
    │          │             │   Return cached result      │              │
    │          │             │   (skip to end)             │              │
    │          │             │              │              │              │
    │          │             │ IF Cache Miss:              │              │
    │          │             │   Continue execution        │              │
    │          │             │              │              │              │
    │          │             │ build_sql()  │              │              │
    │          │             │─────────────────────────────>│              │
    │          │             │              │              │              │
    │          │             │              │ SQL String   │              │
    │          │             │              │──────────────>│              │
    │          │             │              │              │              │
    │          │             │              │              │ execute_sql() │
    │          │             │              │              │──────────────>│
    │          │             │              │              │              │
    │          │             │              │              │ [DB Query]   │
    │          │             │              │              │              │
    │          │             │              │              │ Results      │
    │          │             │              │              │<──────────────│
    │          │             │              │              │              │
    │          │             │ Formatted Result            │              │
    │          │             │<─────────────────────────────│              │
    │          │             │              │              │              │
    │          │             │ Store in Cache              │              │
    │          │             │──────────────>│              │              │
    │          │             │              │              │              │
    │          │             │              │ Cache Stored │              │
    │          │             │              │<─────────────│              │
    │          │             │              │              │              │
    │          │             │ Final Result │              │              │
    │          │             │──────────────│              │              │
    │          │             │              │              │              │
    │          │ Results     │              │              │              │
    │          │<─────────────│              │              │              │
    │          │             │              │              │              │
    │ 200 OK   │             │              │              │              │
    │<─────────│             │              │              │              │
    │          │             │              │              │              │
```

**Figure 3. Caching flow sequence diagram**

---

### 1.4 Pre-Aggregation Routing Sequence

This sequence diagram shows how queries are routed to pre-aggregation tables when available.

```
┌──────┐    ┌─────┐    ┌─────────┐    ┌──────────────┐    ┌──────────┐    ┌────────┐
│Client│    │ API │    │  Query  │    │ Pre-Agg      │    │ Pre-Agg  │    │   DB   │
│      │    │Layer│    │ Engine  │    │ Manager      │    │ Storage  │    │Connector│
└───┬──┘    └──┬──┘    └────┬────┘    └──────┬───────┘    └────┬─────┘    └───┬────┘
    │          │             │                 │                 │              │
    │ POST /query            │                 │                 │              │
    │───────────────────────>│                 │                 │              │
    │          │             │                 │                 │              │
    │          │ execute_query()               │                 │              │
    │          │────────────>│                 │                 │              │
    │          │             │                 │                 │              │
    │          │             │ Find Matching   │                 │              │
    │          │             │ Pre-Aggregation │                 │              │
    │          │             │─────────────────>│                 │              │
    │          │             │                 │                 │              │
    │          │             │                 │ Match Query     │              │
    │          │             │                 │ Dimensions      │              │
    │          │             │                 │ Measures        │              │
    │          │             │                 │ Granularity    │              │
    │          │             │                 │                 │              │
    │          │             │                 │ Matching Pre-Agg│              │
    │          │             │                 │<────────────────│              │
    │          │             │                 │                 │              │
    │          │             │ Check if exists │                 │              │
    │          │             │───────────────────────────────────>│              │
    │          │             │                 │                 │              │
    │          │             │                 │                 │ Check Table │
    │          │             │                 │                 │──────────────>│
    │          │             │                 │                 │              │
    │          │             │                 │                 │ Table Exists │
    │          │             │                 │                 │<──────────────│
    │          │             │                 │                 │              │
    │          │             │                 │ Check Freshness │              │
    │          │             │                 │─────────────────>│              │
    │          │             │                 │                 │              │
    │          │             │                 │                 │ Is Fresh?    │
    │          │             │                 │                 │<─────────────│
    │          │             │                 │                 │              │
    │          │             │                 │                 │              │
    │          │             │ IF Pre-Agg Available:              │              │
    │          │             │   Build SQL from Pre-Agg Table     │              │
    │          │             │   Execute on Pre-Agg Table        │              │
    │          │             │──────────────────────────────────────────────────>│
    │          │             │                 │                 │              │
    │          │             │                 │                 │              │
    │          │             │                 │                 │              │
    │          │             │ IF No Pre-Agg:   │                 │              │
    │          │             │   Build SQL from Base Table       │              │
    │          │             │   Execute on Base Table           │              │
    │          │             │──────────────────────────────────────────────────>│
    │          │             │                 │                 │              │
    │          │             │                 │                 │              │
    │          │             │ Results          │                 │              │
    │          │             │<──────────────────────────────────────────────────│
    │          │             │                 │                 │              │
    │          │ Results     │                 │                 │              │
    │          │<─────────────│                 │                 │              │
    │          │             │                 │                 │              │
    │ 200 OK   │             │                 │                 │              │
    │<─────────│             │                 │                 │              │
    │          │             │                 │                 │              │
```

**Figure 4. Pre-aggregation routing sequence diagram**

---

### 1.5 Error Handling Sequence

This sequence diagram shows how errors are handled at different stages of query execution.

```
┌──────┐    ┌─────┐    ┌───────┐    ┌────────┐    ┌─────────┐    ┌──────────┐
│Client│    │ API │    │Parser │    │ Schema │    │   SQL   │    │   DB     │
│      │    │Layer│    │       │    │Manager │    │ Builder │    │Connector │
└───┬──┘    └──┬──┘    └───┬───┘    └───┬────┘    └────┬────┘    └────┬─────┘
    │          │            │            │              │              │
    │ POST /query            │            │              │              │
    │ (invalid cube)        │            │              │              │
    │───────────────────────>│            │              │              │
    │          │             │            │              │              │
    │          │ parse_query()            │              │              │
    │          │───────────>│             │              │              │
    │          │             │            │              │              │
    │          │             │ Parse OK   │              │              │
    │          │             │────────────│              │              │
    │          │             │            │              │              │
    │          │ validate_query()         │              │              │
    │          │──────────────────────────>│              │              │
    │          │             │            │              │              │
    │          │             │            │ Lookup cube  │              │
    │          │             │            │ "invalid"    │              │
    │          │             │            │──────────────│              │
    │          │             │            │              │              │
    │          │             │            │ Cube NOT FOUND│              │
    │          │             │            │<─────────────│              │
    │          │             │            │              │              │
    │          │             │            │ ValidationError│              │
    │          │             │            │──────────────>│              │
    │          │             │            │              │              │
    │          │ ValidationError          │              │              │
    │          │<──────────────────────────│              │              │
    │          │             │            │              │              │
    │          │ Format Error Response    │              │              │
    │          │ {                        │              │              │
    │          │   "error": "Invalid cube",│              │              │
    │          │   "message": "Cube 'invalid' not found",│              │
    │          │   "available_cubes": [...]│              │              │
    │          │ }                        │              │              │
    │          │             │            │              │              │
    │ 400 Bad Request        │            │              │              │
    │<───────────────────────│            │              │              │
    │          │             │            │              │              │
    │          │             │            │              │              │
    │          │             │            │              │              │
    │          │ [Alternative: SQL Error]  │              │              │
    │          │             │            │              │              │
    │          │             │            │              │ build_sql()  │
    │          │             │            │              │──────────────>│
    │          │             │            │              │              │
    │          │             │            │              │ SQL Generated│
    │          │             │            │              │──────────────>│
    │          │             │            │              │              │
    │          │             │            │              │              │ execute_sql()
    │          │             │            │              │              │──────────────>│
    │          │             │            │              │              │              │
    │          │             │            │              │              │ SQL Error    │
    │          │             │            │              │              │<──────────────│
    │          │             │            │              │              │              │
    │          │             │            │              │ SQL Error    │              │
    │          │             │            │              │<─────────────│              │
    │          │             │            │              │              │              │
    │          │ SQL Error   │            │              │              │              │
    │          │<─────────────│            │              │              │              │
    │          │             │            │              │              │              │
    │          │ Format Error Response    │              │              │              │
    │          │ {                        │              │              │              │
    │          │   "error": "SQL execution failed",│              │              │              │
    │          │   "message": "column does not exist"│              │              │              │
    │          │ }                        │              │              │              │
    │          │             │            │              │              │              │
    │ 500 Internal Server Error           │              │              │              │
    │<───────────────────────│            │              │              │              │
    │          │             │            │              │              │              │
```

**Figure 5. Error handling sequence diagram**

---

## 2. Component Flow Diagrams

### 2.1 Complete Query Execution Flow

This diagram shows the complete flow of data and control through all components during query execution.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        QUERY EXECUTION FLOW                                  │
└─────────────────────────────────────────────────────────────────────────────┘

    Client Request (JSON)
           │
           ▼
    ┌──────────────┐
    │   REST API   │ ◄─── Authentication (JWT/API Key)
    │   GraphQL    │
    │   SQL API    │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Query Parser │ ──► Extract dimensions, measures, filters
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   Validator  │ ──► Check cube.field references
    │              │ ──► Validate types
    │              │ ──► Check operators
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Query Engine │
    └──────┬───────┘
           │
           ├─────────────────────────────────────┐
           │                                     │
           ▼                                     ▼
    ┌──────────────┐                    ┌──────────────┐
    │   Optimizer  │                    │ Cache Check  │
    │              │                    │              │
    │ • Remove     │                    │ • Generate   │
    │   duplicates │                    │   key        │
    │ • Optimize   │                    │ • Check cache│
    │   filters    │                    │ • Return if  │
    │ • Join order │                    │   hit        │
    └──────┬───────┘                    └──────┬───────┘
           │                                   │
           │                                   │ [Cache Miss]
           │                                   │
           ├───────────────────────────────────┘
           │
           ├─────────────────────────────────────┐
           │                                     │
           ▼                                     ▼
    ┌──────────────┐                    ┌──────────────┐
    │ Pre-Agg      │                    │   RLS        │
    │ Check        │                    │   Manager    │
    │              │                    │              │
    │ • Match      │                    │ • Get RLS    │
    │   query      │                    │   rules      │
    │ • Check      │                    │ • Substitute │
    │   available  │                    │   variables  │
    │ • Route if   │                    │ • Add WHERE  │
    │   match      │                    │   condition  │
    └──────┬───────┘                    └──────┬───────┘
           │                                   │
           │ [No Pre-Agg Match]                │
           │                                   │
           ├───────────────────────────────────┘
           │
           ▼
    ┌──────────────┐
    │  SQL Builder │
    │              │
    │ • SELECT     │
    │ • FROM + JOIN│
    │ • WHERE      │
    │ • GROUP BY   │
    │ • ORDER BY   │
    │ • LIMIT      │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   Database   │
    │  Connector   │
    │              │
    │ • Get conn   │
    │ • Execute    │
    │ • Format     │
    │ • Release    │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   Database   │
    │  (PostgreSQL)│
    │  (MySQL)     │
    └──────┬───────┘
           │
           │ Results
           │
           ▼
    ┌──────────────┐
    │   Formatter  │
    │              │
    │ • Convert    │
    │   types      │
    │ • Add meta   │
    └──────┬───────┘
           │
           ├─────────────────────────────────────┐
           │                                     │
           ▼                                     ▼
    ┌──────────────┐                    ┌──────────────┐
    │   Logger     │                    │   Metrics    │
    │              │                    │              │
    │ • Log query  │                    │ • Record     │
    │ • Log time   │                    │   metrics    │
    │ • Log user   │                    │ • Export     │
    └──────────────┘                    └──────────────┘
           │
           │
           ▼
    ┌──────────────┐
    │ Store Cache  │
    │              │
    │ • Generate   │
    │   key        │
    │ • Store with │
    │   TTL        │
    └──────────────┘
           │
           ▼
    JSON Response to Client
```

**Figure 6. Complete query execution flow diagram**

---

### 2.2 Authentication and Security Flow

This diagram shows how authentication, authorization, and RLS work together.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION & SECURITY FLOW                            │
└─────────────────────────────────────────────────────────────────────────────┘

    HTTP Request
           │
           ▼
    ┌──────────────┐
    │ Extract Auth │
    │ Header       │
    │              │
    │ • Authorization│
    │ • X-API-Key  │
    └──────┬───────┘
           │
           ├─────────────────────┐
           │                     │
           ▼                     ▼
    ┌──────────────┐    ┌──────────────┐
    │  JWT Auth    │    │ API Key Auth │
    │              │    │              │
    │ • Validate   │    │ • Lookup key │
    │   signature  │    │ • Check      │
    │ • Check exp  │    │   active     │
    │ • Decode     │    │ • Check exp  │
    └──────┬───────┘    └──────┬───────┘
           │                   │
           └─────────┬─────────┘
                     │
                     ▼
              ┌──────────────┐
              │   Security   │
              │   Context    │
              │              │
              │ • user_id    │
              │ • roles      │
              │ • permissions│
              │ • tenant_id  │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │Authorization │
              │   (RBAC)     │
              │              │
              │ • Get roles  │
              │ • Get perms  │
              │ • Check      │
              │   resource   │
              │ • Check      │
              │   action     │
              └──────┬───────┘
                     │
                     │ [Authorized]
                     │
                     ▼
              ┌──────────────┐
              │      RLS     │
              │   Manager    │
              │              │
              │ • Get RLS    │
              │   rules      │
              │ • Substitute │
              │   variables  │
              │ • Add WHERE  │
              └──────┬───────┘
                     │
                     ▼
              Query with Security Applied
```

**Figure 7. Authentication and security flow diagram**

---

### 2.3 Caching Decision Flow

This diagram shows the decision tree for cache hits and misses.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CACHING DECISION FLOW                                 │
└─────────────────────────────────────────────────────────────────────────────┘

    Query Arrives
           │
           ▼
    ┌──────────────┐
    │ Generate     │
    │ Cache Key    │
    │              │
    │ • Query hash │
    │ • User ctx   │
    │ • Schema ver │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Check Cache  │
    │              │
    │ • Redis      │
    │ • Memory     │
    └──────┬───────┘
           │
           ├─────────────────┐
           │                 │
           ▼                 ▼
    ┌──────────────┐  ┌──────────────┐
    │  Cache Hit   │  │ Cache Miss   │
    │              │  │              │
    │ • Return     │  │ • Continue   │
    │   cached     │  │   execution  │
    │ • Log hit    │  │              │
    │ • Record     │  │              │
    │   metrics    │  │              │
    └──────┬───────┘  └──────┬───────┘
           │                 │
           │                 │
           │                 ▼
           │          ┌──────────────┐
           │          │ Execute      │
           │          │ Query        │
           │          │              │
           │          │ • Build SQL │
           │          │ • Execute   │
           │          │ • Format    │
           │          └──────┬───────┘
           │                 │
           │                 ▼
           │          ┌──────────────┐
           │          │ Store in     │
           │          │ Cache        │
           │          │              │
           │          │ • Set TTL    │
           │          │ • Store key  │
           │          └──────┬───────┘
           │                 │
           └─────────────────┘
                   │
                   ▼
            Return Result
```

**Figure 8. Caching decision flow diagram**

---

### 2.4 Pre-Aggregation Matching Flow

This diagram shows how queries are matched to pre-aggregations.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PRE-AGGREGATION MATCHING FLOW                              │
└─────────────────────────────────────────────────────────────────────────────┘

    Query Arrives
           │
           ▼
    ┌──────────────┐
    │ Extract Query│
    │ Components   │
    │              │
    │ • Dimensions │
    │ • Measures   │
    │ • Filters    │
    │ • Granularity│
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Find All     │
    │ Pre-Aggs     │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ For Each     │
    │ Pre-Agg:     │
    └──────┬───────┘
           │
           ├─────────────────────────────────────┐
           │                                     │
           ▼                                     ▼
    ┌──────────────┐                    ┌──────────────┐
    │ Check        │                    │ Check        │
    │ Dimensions   │                    │ Measures     │
    │              │                    │              │
    │ Query dims   │                    │ Query meas   │
    │ ⊆ Pre-agg?   │                    │ ⊆ Pre-agg?   │
    └──────┬───────┘                    └──────┬───────┘
           │                                   │
           │ [Both Match]                      │
           │                                   │
           ├───────────────────────────────────┘
           │
           ▼
    ┌──────────────┐
    │ Check        │
    │ Granularity  │
    │              │
    │ Query gran = │
    │ Pre-agg gran?│
    └──────┬───────┘
           │
           ├─────────────────┐
           │                 │
           ▼                 ▼
    ┌──────────────┐  ┌──────────────┐
    │ Match Found  │  │ No Match     │
    │              │  │              │
    │ • Check if   │  │ • Use Base   │
    │   exists     │  │   Table      │
    │ • Check if   │  │              │
    │   fresh      │  │              │
    └──────┬───────┘  └──────┬───────┘
           │                 │
           │ [Available]     │
           │                 │
           ▼                 │
    ┌──────────────┐         │
    │ Route to     │         │
    │ Pre-Agg      │         │
    │ Table        │         │
    └──────┬───────┘         │
           │                 │
           └─────────────────┘
                   │
                   ▼
            Execute Query
```

**Figure 9. Pre-aggregation matching flow diagram**

---

### 2.5 Multi-Cube Join Flow

This diagram shows how multi-cube queries are handled with automatic JOIN generation.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      MULTI-CUBE JOIN FLOW                                    │
└─────────────────────────────────────────────────────────────────────────────┘

    Query with Multiple Cubes
           │
           ▼
    ┌──────────────┐
    │ Extract      │
    │ Cubes        │
    │              │
    │ • orders     │
    │ • products   │
    │ • customers  │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Identify     │
    │ Base Cube    │
    │              │
    │ (First cube  │
    │  or largest) │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ For Each     │
    │ Additional   │
    │ Cube:        │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Find         │
    │ Relationship │
    │              │
    │ • Direct?    │
    │ • Indirect?  │
    └──────┬───────┘
           │
           ├─────────────────┐
           │                 │
           ▼                 ▼
    ┌──────────────┐  ┌──────────────┐
    │ Direct       │  │ Indirect     │
    │ Relationship │  │ (BFS Search) │
    │              │  │              │
    │ • Get join   │  │ • Find path  │
    │   condition  │  │ • Build      │
    │              │  │   joins      │
    └──────┬───────┘  └──────┬───────┘
           │                 │
           └─────────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │ Build JOIN   │
              │ Clauses      │
              │              │
              │ • LEFT JOIN  │
              │ • ON clause  │
              │ • Alias      │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │ Generate SQL │
              │              │
              │ FROM base    │
              │ LEFT JOIN ...│
              └──────┬───────┘
                     │
                     ▼
              Execute SQL
```

**Figure 10. Multi-cube join flow diagram**

---

### 2.6 Schema Loading and Hot Reload Flow

This diagram shows how semantic models are loaded and reloaded during development.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  SCHEMA LOADING & HOT RELOAD FLOW                            │
└─────────────────────────────────────────────────────────────────────────────┘

    Application Startup
           │
           ▼
    ┌──────────────┐
    │ Scan Models  │
    │ Directory    │
    │              │
    │ • Find .yaml │
    │   files      │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ For Each     │
    │ YAML File:   │
    └──────┬───────┘
           │
           ├─────────────────────────────────────┐
           │                                     │
           ▼                                     ▼
    ┌──────────────┐                    ┌──────────────┐
    │ Parse YAML   │                    │ Validate     │
    │              │                    │ Structure    │
    │ • Load file  │                    │              │
    │ • Parse      │                    │ • Required   │
    │   syntax     │                    │   fields     │
    │              │                    │ • Types      │
    └──────┬───────┘                    └──────┬───────┘
           │                                   │
           └───────────────┬───────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Create Cube  │
                    │ Objects      │
                    │              │
                    │ • Dimensions │
                    │ • Measures   │
                    │ • Relations  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Build Schema │
                    │              │
                    │ • All cubes  │
                    │ • Relations  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Update      │
                    │ Components   │
                    │              │
                    │ • Query      │
                    │   Engine     │
                    │ • SQL Builder│
                    │ • Pre-Agg    │
                    │   Manager    │
                    └──────────────┘
                           │
                           │
    ┌──────────────────────┴──────────────────────┐
    │                                             │
    │  [Development Mode: File Watcher Active]   │
    │                                             │
    └──────────────────────┬──────────────────────┘
                           │
                           │ File Change Detected
                           │
                           ▼
                    ┌──────────────┐
                    │ Debounce     │
                    │ (500ms)      │
                    └──────┬───────┘
                           │
                           │ [After Debounce]
                           │
                           ▼
                    ┌──────────────┐
                    │ Reload       │
                    │ Schema       │
                    │              │
                    │ (Repeat      │
                    │  process)    │
                    └──────────────┘
```

**Figure 11. Schema loading and hot reload flow diagram**

---

## 3. Component Interaction Matrix

This matrix shows which components interact with each other.

| Component | Interacts With | Interaction Type |
|-----------|---------------|------------------|
| **REST API** | Query Engine, Auth, Logger | Calls, Uses |
| **GraphQL API** | Query Engine, Schema Manager | Calls, Uses |
| **SQL API** | Database Connector, RLS Manager | Calls, Uses |
| **Query Parser** | Query Validator | Passes Query Object |
| **Query Validator** | Schema Manager | Resolves References |
| **Query Engine** | All Components | Orchestrates |
| **SQL Builder** | Schema Manager, Relationship Manager | Gets Definitions |
| **Query Optimizer** | Query Engine | Optimizes Query |
| **Schema Loader** | File System | Reads YAML Files |
| **Cube Manager** | Query Validator, SQL Builder | Provides Cube Info |
| **Dimension/Measure Manager** | SQL Builder | Provides SQL Expressions |
| **Relationship Manager** | SQL Builder | Provides Join Paths |
| **Cache Manager** | Query Engine | Stores/Retrieves Results |
| **Pre-Aggregation Manager** | Query Engine, Pre-Agg Storage | Matches & Routes Queries |
| **Pre-Aggregation Scheduler** | Pre-Agg Manager, Database Connector | Refreshes Pre-Aggs |
| **JWT Auth** | Security Context | Creates Context |
| **API Key Auth** | Security Context | Creates Context |
| **Authorization** | Security Context | Checks Permissions |
| **RLS Manager** | Query Engine, SQL Builder | Applies RLS Rules |
| **Query Logger** | Query Engine | Logs Queries |
| **Metrics Collector** | Query Engine | Records Metrics |
| **Database Connector** | Database | Executes SQL |
| **Hot Reload** | Schema Loader, Query Engine | Triggers Reload |
| **Python SDK** | REST API | HTTP Client |
| **CLI Tools** | Schema Loader | Validates Models |

---

## 4. Data Flow Summary

### 4.1 Query Request Flow
```
Client → API Layer → Parser → Validator → Query Engine → 
SQL Builder → Database Connector → Database → 
Result Formatter → Logger → Metrics → Cache → Response
```

### 4.2 Authentication Flow
```
Request → Auth (JWT/API Key) → Security Context → 
Authorization → RLS Manager → Query Execution
```

### 4.3 Caching Flow
```
Query → Cache Key Generation → Cache Check → 
[Hit: Return] OR [Miss: Execute → Store → Return]
```

### 4.4 Pre-Aggregation Flow
```
Query → Pre-Agg Matching → Availability Check → 
[Match: Route to Pre-Agg] OR [No Match: Base Table]
```

---

This document provides comprehensive sequence and flow diagrams showing how all components interact in the Semantic Layer Platform.

