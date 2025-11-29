# Quick Start Guide - SemanticQuark

Get SemanticQuark up and running in minutes!

## Prerequisites

- Docker and Docker Compose
- curl (for testing)

## 🚀 Quick Start (3 Steps)

### Step 1: Start Services

```bash
./scripts/test_setup.sh
```

This will:
- Start PostgreSQL database
- Start Redis cache
- Start SemanticQuark API
- Initialize sample data
- Wait for all services to be ready

### Step 2: Test the API

```bash
./scripts/test_queries.sh
```

This runs a comprehensive test suite covering:
- Health checks
- Schema endpoints
- Query execution
- Filtering
- Logging
- Metrics
- Pre-aggregations

### Step 3: Try a Query

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "measures": ["orders.count"]
  }'
```

## 📊 What's Running?

- **API Server**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **API Docs**: http://localhost:8000/docs (Swagger UI)

## 🧪 Example Queries

### Count Orders

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"measures": ["orders.count"]}'
```

### Orders by Status

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "dimensions": ["orders.status"],
    "measures": ["orders.count", "orders.total_revenue"]
  }'
```

### Filtered Query

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "measures": ["orders.count"],
    "filters": [{
      "dimension": "orders.status",
      "operator": "equals",
      "values": ["completed"]
    }]
  }'
```

## 🛑 Stop Services

```bash
docker-compose down
```

To remove all data:

```bash
docker-compose down -v
```

## 📚 Next Steps

- Read [TESTING.md](TESTING.md) for comprehensive testing guide
- Check [IMPLEMENTATION_PROGRESS.md](IMPLEMENTATION_PROGRESS.md) for feature status
- Review [PRD_COMPLETE_SEMANTIC_LAYER.md](PRD_COMPLETE_SEMANTIC_LAYER.md) for full documentation

## 🐛 Troubleshooting

### Services won't start

```bash
# Check logs
docker-compose logs

# Restart
docker-compose restart
```

### Application errors

```bash
# View application logs
docker-compose logs -f semanticquark
```

### Port already in use

Edit `docker-compose.yml` to change ports:
- API: `8000:8000` → `8001:8000`
- PostgreSQL: `5432:5432` → `5433:5432`
- Redis: `6379:6379` → `6380:6379`

## 💡 Tips

- Use `docker-compose logs -f` to watch logs in real-time
- Access PostgreSQL: `docker-compose exec postgres psql -U semanticquark -d semanticquark_db`
- Access Redis: `docker-compose exec redis redis-cli`
- API auto-reloads on code changes (development mode)

