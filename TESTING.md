# Testing Guide for SemanticQuark

This guide explains how to test all functionality of the SemanticQuark platform using Docker Compose.

## Prerequisites

- Docker and Docker Compose installed
- curl (for API testing)
- Python 3.11+ (optional, for local testing)

## Quick Start

### 1. Start Services

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Start all services (PostgreSQL, Redis, and SemanticQuark)
./scripts/test_setup.sh
```

Or manually:

```bash
docker-compose up -d
```

### 2. Verify Services

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f semanticquark
```

### 3. Run Test Queries

```bash
# Run automated test suite
./scripts/test_queries.sh
```

## Manual Testing

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "schema_loaded": true
}
```

### Get Schema

```bash
curl http://localhost:8000/api/v1/schema
```

### Execute Query

#### Simple Count Query

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "measures": ["orders.count"]
  }'
```

#### Query with Dimensions

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "dimensions": ["orders.status"],
    "measures": ["orders.count", "orders.total_revenue"]
  }'
```

#### Query with Filters

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "dimensions": ["orders.status"],
    "measures": ["orders.count"],
    "filters": [
      {
        "dimension": "orders.status",
        "operator": "equals",
        "values": ["completed"]
      }
    ]
  }'
```

#### Query with Time Dimension

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "dimensions": ["orders.created_at"],
    "measures": ["orders.count"],
    "timeDimensions": [
      {
        "dimension": "orders.created_at",
        "granularity": "day"
      }
    ]
  }'
```

### Query Logs

```bash
curl http://localhost:8000/api/v1/logs?limit=10
```

### Metrics

```bash
curl http://localhost:8000/api/v1/metrics
```

### Pre-Aggregations

```bash
# List pre-aggregations
curl http://localhost:8000/api/v1/pre-aggregations

# Refresh a pre-aggregation
curl -X POST http://localhost:8000/api/v1/pre-aggregations/orders_daily/refresh
```

### GraphQL API

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ orders { count totalRevenue } }"
  }'
```

### SQL API

```bash
curl -X POST http://localhost:8000/api/v1/sql \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT COUNT(*) FROM orders"
  }'
```

## Testing Features

### 1. Caching

1. Execute a query and note the execution time
2. Execute the same query again
3. Check the response metadata for `cache_hit: true`
4. The second query should be much faster

### 2. Pre-Aggregations

1. Define a pre-aggregation in your model YAML:
```yaml
pre_aggregations:
  - name: orders_daily
    dimensions: [status, created_at]
    measures: [count, total_revenue]
    time_dimension: created_at
    granularity: day
    refresh_key:
      every: 1 hour
```

2. Reload the schema:
```bash
curl -X POST http://localhost:8000/api/v1/reload
```

3. Execute a query that matches the pre-aggregation
4. Check the response metadata for `pre_aggregation_used: true`

### 3. Authentication (if enabled)

```bash
# With JWT token
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"measures": ["orders.count"]}'

# With API key
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"measures": ["orders.count"]}'
```

### 4. Row-Level Security (if enabled)

When RLS is configured in your cube:
```yaml
security:
  row_filter: "{CUBE}.user_id = {USER_CONTEXT.user_id}"
```

Queries will automatically filter based on the user context.

## Database Access

### Connect to PostgreSQL

```bash
docker-compose exec postgres psql -U semanticquark -d semanticquark_db
```

### Connect to Redis

```bash
docker-compose exec redis redis-cli
```

## Troubleshooting

### Services won't start

```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart
```

### Application errors

```bash
# View application logs
docker-compose logs -f semanticquark

# Check database connection
docker-compose exec postgres pg_isready -U semanticquark

# Check Redis connection
docker-compose exec redis redis-cli ping
```

### Schema not loading

1. Check that models directory exists: `ls models/`
2. Check model files are valid YAML
3. Check application logs for errors
4. Try reloading schema: `curl -X POST http://localhost:8000/api/v1/reload`

## Clean Up

```bash
# Stop services
docker-compose down

# Stop and remove volumes (deletes data)
docker-compose down -v
```

## Performance Testing

### Load Testing with Apache Bench

```bash
# Install ab if needed
# macOS: brew install httpd
# Linux: apt-get install apache2-utils

# Test query endpoint
ab -n 1000 -c 10 -p query.json -T application/json \
  http://localhost:8000/api/v1/query
```

### Monitor Performance

```bash
# Watch metrics
watch -n 1 'curl -s http://localhost:8000/api/v1/metrics | python3 -m json.tool'

# Check query logs
watch -n 1 'curl -s http://localhost:8000/api/v1/logs?limit=5 | python3 -m json.tool'
```

## Next Steps

- Review `IMPLEMENTATION_PROGRESS.md` for completed features
- Check `PRD_COMPLETE_SEMANTIC_LAYER.md` for full feature list
- Explore the API documentation at http://localhost:8000/docs (Swagger UI)

