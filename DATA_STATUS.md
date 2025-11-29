# Database Data Status

## Current Data Status

**Type**: **Sample/Test Data** (Not Real Production Data)

The database contains **synthetic test data** that was automatically inserted when the database was first initialized. This data is designed for testing and demonstration purposes.

---

## What Data Exists

### ✅ Sample Data is Present

When the PostgreSQL container starts for the first time, the initialization script (`scripts/init_db.sql`) automatically creates and populates the database with:

### Orders Table: 10 Sample Orders

| Order ID | Status     | Date       | Customer  | Amount  |
|----------|------------|------------|-----------|---------|
| order_1  | completed  | 2024-01-15 | customer_1 | $100.50 |
| order_2  | completed  | 2024-01-15 | customer_1 | $250.75 |
| order_3  | pending    | 2024-01-15 | customer_2 | $75.25  |
| order_4  | completed  | 2024-01-16 | customer_2 | $300.00 |
| order_5  | cancelled  | 2024-01-16 | customer_3 | $50.00  |
| order_6  | completed  | 2024-01-16 | customer_3 | $150.00 |
| order_7  | completed  | 2024-01-17 | customer_1 | $200.00 |
| order_8  | pending    | 2024-01-17 | customer_2 | $125.50 |
| order_9  | completed  | 2024-01-17 | customer_3 | $175.75 |
| order_10 | completed  | 2024-01-18 | customer_1 | $90.25  |

**Summary**:
- Total Orders: 10
- Completed: 7 orders ($1,267.25)
- Pending: 2 orders ($200.75)
- Cancelled: 1 order ($50.00)
- Total Revenue: $1,518.00

### Customers Table: 3 Sample Customers

| Customer ID | Name         | Email              |
|-------------|--------------|-------------------|
| customer_1  | John Doe     | john@example.com  |
| customer_2  | Jane Smith   | jane@example.com  |
| customer_3  | Bob Johnson  | bob@example.com   |

---

## Data Characteristics

### ✅ This is Test Data

- **Purpose**: Testing and demonstration
- **Source**: Hardcoded in `scripts/init_db.sql`
- **Realism**: Synthetic but realistic structure
- **Size**: Small dataset (10 orders, 3 customers)
- **Persistence**: Data persists in Docker volume

### ❌ This is NOT Real Production Data

- Not connected to a real e-commerce system
- Not live/real-time data
- Not production customer data
- Not actual business transactions

---

## How to Verify Data

### Start the Database

```bash
docker-compose up -d postgres
```

### Check Data

```bash
# Count orders
docker-compose exec postgres psql -U semanticquark -d semanticquark_db -c "SELECT COUNT(*) FROM orders;"

# View all orders
docker-compose exec postgres psql -U semanticquark -d semanticquark_db -c "SELECT * FROM orders;"

# View customers
docker-compose exec postgres psql -U semanticquark -d semanticquark_db -c "SELECT * FROM customers;"

# Summary statistics
docker-compose exec postgres psql -U semanticquark -d semanticquark_db -c "
SELECT 
    status,
    COUNT(*) as count,
    SUM(total_amount) as total
FROM orders
GROUP BY status;
"
```

---

## Adding Real Data

### Option 1: Import from CSV

```bash
# Create a CSV file with your data
# Then import it
docker-compose exec postgres psql -U semanticquark -d semanticquark_db -c "
COPY orders(id, status, created_at, customer_id, total_amount)
FROM '/path/to/your/data.csv'
DELIMITER ','
CSV HEADER;
"
```

### Option 2: Insert via SQL

```bash
docker-compose exec postgres psql -U semanticquark -d semanticquark_db -c "
INSERT INTO orders (id, status, created_at, customer_id, total_amount)
VALUES 
    ('real_order_1', 'completed', NOW(), 'customer_1', 500.00),
    ('real_order_2', 'pending', NOW(), 'customer_2', 750.00);
"
```

### Option 3: Connect to Your Database

Modify `docker-compose.yml` to connect to your existing database:

```yaml
environment:
  DATABASE_URL: postgresql://user:password@your-host:5432/your_database
```

### Option 4: Use Application API

Insert data via the application or connect to your production database.

---

## Data Persistence

### Where Data is Stored

- **Docker Volume**: `semantic_layer_analytics_postgres_data`
- **Location**: Managed by Docker
- **Persistence**: Data survives container restarts
- **Deletion**: Data is lost if volume is removed

### Backup Data

```bash
# Backup
docker-compose exec postgres pg_dump -U semanticquark semanticquark_db > backup.sql

# Restore
docker-compose exec -T postgres psql -U semanticquark semanticquark_db < backup.sql
```

### Reset Data

```bash
# Remove volume (deletes all data)
docker-compose down postgres
docker volume rm semantic_layer_analytics_postgres_data

# Start fresh (will run init script again)
docker-compose up -d postgres
```

---

## Summary

**Current Status**: ✅ **Sample Test Data Present**

- ✅ Database has 10 sample orders
- ✅ Database has 3 sample customers
- ✅ Data is automatically created on first startup
- ✅ Data persists in Docker volume
- ❌ This is NOT real production data
- ❌ This is NOT live/real-time data

**To Use Real Data**: Connect to your production database or import your data using one of the methods above.

