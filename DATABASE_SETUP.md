# Database Setup - SemanticQuark

## Database Configuration

### Database Type
**PostgreSQL 15** (Alpine Linux)

### Connection Details
- **Host**: `postgres` (Docker service name) or `localhost` (from host)
- **Port**: `5432`
- **Database Name**: `semanticquark_db`
- **Username**: `semanticquark`
- **Password**: `semanticquark123`
- **Connection URL**: `postgresql://semanticquark:semanticquark123@postgres:5432/semanticquark_db`

---

## Database Tables

### 1. `orders` Table

**Purpose**: E-commerce orders data for testing semantic queries

**Schema**:
```sql
CREATE TABLE orders (
    id VARCHAR(50) PRIMARY KEY,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL
);
```

**Columns**:
- `id` (VARCHAR(50), PRIMARY KEY) - Unique order identifier
- `status` (VARCHAR(20), NOT NULL) - Order status: 'completed', 'pending', 'cancelled'
- `created_at` (TIMESTAMP, NOT NULL) - Order creation timestamp
- `customer_id` (VARCHAR(50), NOT NULL) - Foreign key to customers table
- `total_amount` (DECIMAL(10, 2), NOT NULL) - Order total amount

**Indexes**:
- `idx_orders_status` - Index on `status` column
- `idx_orders_created_at` - Index on `created_at` column
- `idx_orders_customer_id` - Index on `customer_id` column

**Sample Data**: 10 orders
- 7 completed orders
- 2 pending orders
- 1 cancelled order
- Total revenue: $1,518.00
- Date range: 2024-01-15 to 2024-01-18

---

### 2. `customers` Table

**Purpose**: Customer data for relationship testing

**Schema**:
```sql
CREATE TABLE customers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL
);
```

**Columns**:
- `id` (VARCHAR(50), PRIMARY KEY) - Unique customer identifier
- `name` (VARCHAR(100), NOT NULL) - Customer name
- `email` (VARCHAR(100), NOT NULL) - Customer email
- `created_at` (TIMESTAMP, NOT NULL) - Customer creation timestamp

**Sample Data**: 3 customers
- customer_1: John Doe (john@example.com)
- customer_2: Jane Smith (jane@example.com)
- customer_3: Bob Johnson (bob@example.com)

---

## Sample Data Details

### Orders Data

| Order ID | Status     | Created At          | Customer ID | Total Amount |
|----------|------------|---------------------|-------------|--------------|
| order_1   | completed  | 2024-01-15 10:00:00 | customer_1  | $100.50      |
| order_2   | completed  | 2024-01-15 11:00:00 | customer_1  | $250.75      |
| order_3   | pending    | 2024-01-15 12:00:00 | customer_2  | $75.25       |
| order_4   | completed  | 2024-01-16 10:00:00 | customer_2  | $300.00      |
| order_5   | cancelled  | 2024-01-16 11:00:00 | customer_3  | $50.00       |
| order_6   | completed  | 2024-01-16 12:00:00 | customer_3  | $150.00      |
| order_7   | completed  | 2024-01-17 10:00:00 | customer_1  | $200.00      |
| order_8   | pending    | 2024-01-17 11:00:00 | customer_2  | $125.50      |
| order_9   | completed  | 2024-01-17 12:00:00 | customer_3  | $175.75      |
| order_10  | completed  | 2024-01-18 10:00:00 | customer_1  | $90.25       |

**Statistics**:
- Total Orders: 10
- Completed: 7 ($1,267.25)
- Pending: 2 ($200.75)
- Cancelled: 1 ($50.00)
- Total Revenue: $1,518.00
- Average Order Value: $151.80

---

## Semantic Model Mapping

### Orders Cube

The `orders` table is mapped to the `orders` cube in the semantic layer:

**Dimensions**:
- `id` → `orders.id` (string, primary key)
- `status` → `orders.status` (string)
- `created_at` → `orders.created_at` (time dimension)
- `customer_id` → `orders.customer_id` (string)

**Measures**:
- `count` → `orders.count` (COUNT of id)
- `total_revenue` → `orders.total_revenue` (SUM of total_amount)
- `average_order_value` → `orders.average_order_value` (AVG of total_amount)

**Pre-aggregations**:
- `orders_daily` - Daily aggregation by status and created_at

---

## Database Access

### From Host Machine

```bash
# Connect to PostgreSQL
psql -h localhost -p 5432 -U semanticquark -d semanticquark_db

# Or using connection string
psql postgresql://semanticquark:semanticquark123@localhost:5432/semanticquark_db
```

### From Docker Container

```bash
# Connect via docker-compose
docker-compose exec postgres psql -U semanticquark -d semanticquark_db

# Run SQL query
docker-compose exec postgres psql -U semanticquark -d semanticquark_db -c "SELECT COUNT(*) FROM orders;"
```

### Connection from Application

The application connects using:
```python
DATABASE_URL=postgresql://semanticquark:semanticquark123@postgres:5432/semanticquark_db
```

---

## Useful Queries

### Count Orders by Status
```sql
SELECT status, COUNT(*) as count
FROM orders
GROUP BY status;
```

### Total Revenue by Status
```sql
SELECT status, SUM(total_amount) as total_revenue
FROM orders
GROUP BY status;
```

### Orders by Date
```sql
SELECT DATE(created_at) as date, COUNT(*) as count
FROM orders
GROUP BY DATE(created_at)
ORDER BY date;
```

### Customer Order Summary
```sql
SELECT 
    c.name,
    COUNT(o.id) as order_count,
    SUM(o.total_amount) as total_spent
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name
ORDER BY total_spent DESC;
```

---

## Database Initialization

The database is automatically initialized when the PostgreSQL container starts for the first time. The initialization script (`scripts/init_db.sql`) is mounted to `/docker-entrypoint-initdb.d/init_db.sql` and runs automatically.

### Manual Initialization

If you need to reinitialize the database:

```bash
# Stop and remove the database container and volume
docker-compose down postgres
docker volume rm semantic_layer_analytics_postgres_data

# Start again (will run init script)
docker-compose up -d postgres
```

---

## Database Maintenance

### Backup Database
```bash
docker-compose exec postgres pg_dump -U semanticquark semanticquark_db > backup.sql
```

### Restore Database
```bash
docker-compose exec -T postgres psql -U semanticquark semanticquark_db < backup.sql
```

### View Database Size
```bash
docker-compose exec postgres psql -U semanticquark -d semanticquark_db -c "
SELECT 
    pg_size_pretty(pg_database_size('semanticquark_db')) as database_size;
"
```

### List All Tables
```bash
docker-compose exec postgres psql -U semanticquark -d semanticquark_db -c "\dt"
```

### View Table Structure
```bash
docker-compose exec postgres psql -U semanticquark -d semanticquark_db -c "\d orders"
```

---

## Performance Considerations

### Indexes
The database includes indexes on frequently queried columns:
- `status` - For filtering by order status
- `created_at` - For time-based queries
- `customer_id` - For customer relationship queries

### Query Optimization
- Use EXPLAIN ANALYZE to check query plans
- Monitor slow queries via application logs
- Consider adding more indexes based on query patterns

---

## Environment Variables

Database configuration can be changed via environment variables in `docker-compose.yml`:

```yaml
environment:
  POSTGRES_USER: semanticquark
  POSTGRES_PASSWORD: semanticquark123
  POSTGRES_DB: semanticquark_db
```

Or via `.env` file:
```
DATABASE_URL=postgresql://semanticquark:semanticquark123@localhost:5432/semanticquark_db
```

---

## Notes

- The database uses PostgreSQL 15 Alpine Linux image for smaller size
- Data persists in Docker volume `semantic_layer_analytics_postgres_data`
- The initialization script runs only on first container start
- Sample data is suitable for testing but should be replaced for production

