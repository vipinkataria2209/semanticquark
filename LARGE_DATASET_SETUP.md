# Large Dataset Setup Guide

## Overview

This guide explains how to set up the **large dataset** with **22,510+ records** across 6 tables for comprehensive testing.

---

## What's Included

### Database Tables

1. **categories** - 10 product categories
2. **customers** - 2,000 customer records
3. **products** - 500 products
4. **orders** - 5,000 orders
5. **order_items** - 10,000 order line items
6. **payments** - 5,000 payment transactions

**Total**: **22,510 records**

---

## Setup Instructions

### Step 1: Stop Existing Database

```bash
docker-compose down postgres
```

### Step 2: Remove Old Data (Optional)

If you want a fresh start:

```bash
docker volume rm semantic_layer_analytics_postgres_data
```

### Step 3: Start Database with Large Dataset

The `docker-compose.yml` is already configured to use `init_db_large.sql`:

```bash
docker-compose up -d postgres
```

The database will automatically:
- Create all 6 tables
- Insert 22,510+ records
- Create indexes for performance
- Create views for convenience

### Step 4: Wait for Initialization

The initialization takes **2-5 minutes** depending on your system. Monitor progress:

```bash
docker-compose logs -f postgres
```

You'll see a message when complete:
```
Database initialization complete!
Categories: 10
Customers: 2000
Products: 500
Orders: 5000
Order Items: 10000
Payments: 5000
```

### Step 5: Verify Data

```bash
# Check record counts
docker-compose exec postgres psql -U semanticquark -d semanticquark_db -c "
SELECT 
    'categories' as table_name, COUNT(*) as count FROM categories
UNION ALL SELECT 'customers', COUNT(*) FROM customers
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'payments', COUNT(*) FROM payments;
"
```

### Step 6: Restart Application

```bash
docker-compose restart semanticquark
```

The application will automatically load all the new semantic models.

---

## Semantic Models

All semantic models are ready:

- ✅ `models/orders.yaml` - Orders cube
- ✅ `models/customers.yaml` - Customers cube
- ✅ `models/products.yaml` - Products cube
- ✅ `models/payments.yaml` - Payments cube
- ✅ `models/order_items.yaml` - Order items cube
- ✅ `models/categories.yaml` - Categories cube

---

## Test Queries

### Query Orders

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "measures": ["orders.count", "orders.total_revenue"],
    "dimensions": ["orders.status"]
  }'
```

### Query Products

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "measures": ["products.count", "products.total_stock"],
    "dimensions": ["products.is_active"]
  }'
```

### Query Customers

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "measures": ["customers.count"],
    "dimensions": ["customers.state"]
  }'
```

### Query Payments

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "measures": ["payments.total_amount"],
    "dimensions": ["payments.payment_method"]
  }'
```

### Complex Multi-Cube Query

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "dimensions": ["orders.status", "orders.order_date"],
    "measures": ["orders.count", "orders.total_revenue"],
    "timeDimensions": [{
      "dimension": "orders.order_date",
      "granularity": "month"
    }]
  }'
```

---

## Performance Testing

With 22,510+ records, you can now test:

- **Query Performance**: Test with large datasets
- **Caching**: Verify cache effectiveness with large result sets
- **Pre-aggregations**: Test pre-aggregation system
- **Multi-cube Joins**: Test complex relationships
- **Time-based Queries**: Test time dimension aggregations

---

## Sample Statistics

### Orders Distribution
- Status: Evenly distributed across 6 statuses
- Date Range: Past 365 days
- Amount Range: $10 - $1,000
- Average: ~$500 per order

### Products Distribution
- Categories: 50 products per category
- Price Range: $9.99 - $1,000
- Stock: 10 - 1,000 units
- Active: 90% active, 10% inactive

### Customers Distribution
- Cities: 10 major US cities
- States: 10 US states
- Registration: Past 365 days
- Orders: 1-10 orders per customer (average ~2.5)

---

## Troubleshooting

### Database Takes Too Long

If initialization is slow:
- Check system resources (CPU, RAM)
- Ensure Docker has enough resources allocated
- Wait for completion (can take 5+ minutes)

### Missing Data

If data seems incomplete:
- Check logs: `docker-compose logs postgres`
- Verify initialization completed successfully
- Check for errors in the logs

### Application Can't Connect

If the app can't connect:
- Ensure database is healthy: `docker-compose ps postgres`
- Check connection string in docker-compose.yml
- Restart application: `docker-compose restart semanticquark`

---

## Switching Back to Small Dataset

If you want to use the small dataset (10 orders):

1. Edit `docker-compose.yml`:
```yaml
- ./scripts/init_db_large.sql:/docker-entrypoint-initdb.d/init_db.sql
```
Change to:
```yaml
- ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init_db.sql
```

2. Reset database:
```bash
docker-compose down postgres
docker volume rm semantic_layer_analytics_postgres_data
docker-compose up -d postgres
```

---

## Next Steps

1. ✅ Database initialized with 22,510+ records
2. ✅ Semantic models created for all tables
3. ✅ Test queries with large dataset
4. ✅ Verify performance and caching
5. ✅ Test pre-aggregations with real data volume

Enjoy testing with realistic data volumes! 🚀

