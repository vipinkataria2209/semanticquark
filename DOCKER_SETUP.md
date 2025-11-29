# Docker Setup for SemanticQuark Testing

## 📦 What Was Created

### Core Files

1. **`docker-compose.yml`** - Orchestrates all services
   - PostgreSQL 15 database
   - Redis 7 cache
   - SemanticQuark application
   - Health checks and dependencies
   - Network configuration

2. **`Dockerfile`** - Application container
   - Python 3.11 base image
   - Dependencies installation
   - Application setup
   - Port exposure

3. **`.env.example`** - Configuration template
   - Database connection settings
   - Redis configuration
   - Cache settings
   - Authentication settings
   - Pre-aggregations settings

4. **`.dockerignore`** - Excludes unnecessary files from Docker build

### Scripts

1. **`scripts/init_db.sql`** - Database initialization
   - Creates `orders` table
   - Creates `customers` table
   - Inserts sample data (10 orders, 3 customers)
   - Creates indexes for performance

2. **`scripts/test_setup.sh`** - Automated setup
   - Starts all services
   - Waits for health checks
   - Verifies connectivity
   - Provides status information

3. **`scripts/test_queries.sh`** - Automated testing
   - Health check test
   - Schema endpoint test
   - Query execution tests
   - Filter tests
   - Logging tests
   - Metrics tests
   - Pre-aggregation tests

### Documentation

1. **`TESTING.md`** - Comprehensive testing guide
   - Manual testing instructions
   - API endpoint examples
   - Feature testing
   - Troubleshooting

2. **`QUICK_START.md`** - Quick reference guide
   - 3-step setup
   - Example queries
   - Common commands

## 🚀 Usage

### Start Everything

```bash
./scripts/test_setup.sh
```

Or manually:

```bash
docker-compose up -d
```

### Run Tests

```bash
./scripts/test_queries.sh
```

### View Logs

```bash
docker-compose logs -f semanticquark
```

### Stop Services

```bash
docker-compose down
```

## 🏗️ Architecture

```
┌─────────────────┐
│   PostgreSQL     │  Port 5432
│   (Database)     │
└─────────────────┘
         ▲
         │
┌─────────────────┐
│  SemanticQuark  │  Port 8000
│     (API)       │
└─────────────────┘
         ▲
         │
┌─────────────────┐
│     Redis       │  Port 6379
│     (Cache)     │
└─────────────────┘
```

## 📊 Services

| Service | Port | Purpose |
|---------|------|---------|
| PostgreSQL | 5432 | Main database |
| Redis | 6379 | Query result cache |
| SemanticQuark | 8000 | API server |

## 🔧 Configuration

All configuration is in `docker-compose.yml` environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `CACHE_ENABLED`: Enable/disable caching
- `CACHE_TYPE`: `redis` or `memory`
- `AUTH_ENABLED`: Enable/disable authentication
- `PRE_AGGREGATIONS_ENABLED`: Enable/disable pre-aggregations

## 📝 Sample Data

The database is initialized with:

- **3 customers**: John Doe, Jane Smith, Bob Johnson
- **10 orders**: Mix of completed, pending, and cancelled
- **Indexes**: On status, created_at, customer_id

## 🧪 Testing Features

The test suite covers:

1. ✅ Health checks
2. ✅ Schema endpoints
3. ✅ Basic queries
4. ✅ Dimension queries
5. ✅ Filtered queries
6. ✅ Query logging
7. ✅ Metrics collection
8. ✅ Pre-aggregations

## 🐛 Troubleshooting

### Port Conflicts

If ports are already in use, edit `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Database Connection Issues

Check PostgreSQL is ready:

```bash
docker-compose exec postgres pg_isready -U semanticquark
```

### Redis Connection Issues

Check Redis is ready:

```bash
docker-compose exec redis redis-cli ping
```

### Application Won't Start

Check logs:

```bash
docker-compose logs semanticquark
```

Common issues:
- Database not ready (wait longer)
- Missing dependencies (check Dockerfile)
- Configuration errors (check .env)

## 📚 Next Steps

1. Read `QUICK_START.md` for quick setup
2. Read `TESTING.md` for comprehensive testing
3. Review `IMPLEMENTATION_PROGRESS.md` for features
4. Check `PRD_COMPLETE_SEMANTIC_LAYER.md` for full docs

## 🎉 Ready to Test!

Everything is set up and ready for testing. Run:

```bash
./scripts/test_setup.sh
./scripts/test_queries.sh
```

Happy testing! 🚀

