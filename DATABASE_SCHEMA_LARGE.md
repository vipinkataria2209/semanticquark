# Large Database Schema - SemanticQuark

## Overview

This document describes the comprehensive database schema with **10,000+ rows** of realistic sample data for testing the SemanticQuark platform.

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────┐
│  categories │ (10 categories)
└──────┬──────┘
       │
       │ 1:N
┌──────▼──────┐
│  products   │ (500 products)
└─────────────┘

┌─────────────┐
│  customers  │ (2,000 customers)
└──────┬──────┘
       │
       │ 1:N
┌──────▼──────┐         ┌──────────────┐
│   orders    │────────│ order_items  │ (10,000 items)
└──────┬──────┘ 1:N    └──────┬───────┘
       │                       │
       │ 1:1                   │ N:1
       │                       │
┌──────▼──────┐         ┌──────▼───────┐
│  payments   │         │   products   │
└─────────────┘         └──────────────┘
```

---

## Tables

### 1. `categories` Table

**Purpose**: Product categories

**Schema**:
```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Sample Data**: 10 categories
- Electronics
- Clothing
- Home & Garden
- Books
- Sports & Outdoors
- Toys & Games
- Health & Beauty
- Automotive
- Food & Beverages
- Office Supplies

---

### 2. `customers` Table

**Purpose**: Customer information

**Schema**:
```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    address VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    country VARCHAR(50) DEFAULT 'USA',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Sample Data**: **2,000 customers**
- Randomly generated names
- Unique email addresses
- US addresses across 10 major cities
- Created over the past year

---

### 3. `products` Table

**Purpose**: Product catalog

**Schema**:
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category_id INTEGER REFERENCES categories(id),
    sku VARCHAR(50) UNIQUE,
    price DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2),
    stock_quantity INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Sample Data**: **500 products**
- Distributed across 10 categories
- Unique SKUs (SKU-000001 to SKU-000500)
- Prices: $9.99 to $1,000.00
- Stock quantities: 10 to 1,000
- 90% active, 10% inactive

---

### 4. `orders` Table

**Purpose**: Customer orders

**Schema**:
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shipped_date TIMESTAMP,
    delivered_date TIMESTAMP,
    subtotal DECIMAL(10, 2) NOT NULL,
    tax DECIMAL(10, 2) DEFAULT 0,
    shipping_cost DECIMAL(10, 2) DEFAULT 0,
    discount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    shipping_address VARCHAR(200),
    billing_address VARCHAR(200),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Sample Data**: **5,000 orders**
- Order numbers: ORD-00000001 to ORD-00005000
- Statuses: pending, processing, shipped, delivered, cancelled, refunded
- Dates: Spread over the past year
- Amounts: $10.00 to $1,000.00
- Tax: 8% of subtotal
- Shipping: $5.99 or $0.00
- Discounts: 5-20% on 30% of orders

---

### 5. `order_items` Table

**Purpose**: Individual items in each order

**Schema**:
```sql
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2) NOT NULL,
    discount DECIMAL(10, 2) DEFAULT 0,
    total_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Sample Data**: **10,000 order items**
- 1-5 items per order (average ~2 items)
- Links orders to products
- Quantity: 1 to 5
- Unit price from product price
- Discounts: 5-20% on 20% of items

---

### 6. `payments` Table

**Purpose**: Payment transactions

**Schema**:
```sql
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    amount DECIMAL(10, 2) NOT NULL,
    transaction_id VARCHAR(100),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Sample Data**: **5,000 payments** (one per order)
- Payment methods: credit_card, debit_card, paypal, bank_transfer, cash, gift_card
- Payment statuses: pending, processing, completed, processed, failed, refunded
- Transaction IDs: TXN-1000000000 to TXN-9999999999
- Amount matches order total
- Status correlates with order status

---

## Data Statistics

### Total Records

| Table | Row Count | Description |
|-------|-----------|-------------|
| categories | 10 | Product categories |
| customers | 2,000 | Customer records |
| products | 500 | Product catalog |
| orders | 5,000 | Customer orders |
| order_items | 10,000 | Order line items |
| payments | 5,000 | Payment transactions |
| **TOTAL** | **22,510** | **Total database records** |

### Data Distribution

**Orders by Status**:
- pending: ~17%
- processing: ~17%
- shipped: ~17%
- delivered: ~17%
- cancelled: ~17%
- refunded: ~15%

**Payment Methods**:
- credit_card: ~33%
- debit_card: ~17%
- paypal: ~17%
- bank_transfer: ~17%
- cash: ~8%
- gift_card: ~8%

**Products by Category**:
- Evenly distributed across 10 categories (~50 products each)

---

## Relationships

### Foreign Keys

1. `products.category_id` → `categories.id`
2. `orders.customer_id` → `customers.id`
3. `order_items.order_id` → `orders.id`
4. `order_items.product_id` → `products.id`
5. `payments.order_id` → `orders.id`

### Indexes

**Performance indexes created on**:
- `customers.email`
- `customers.created_at`
- `products.category_id`
- `products.sku`
- `orders.customer_id`
- `orders.status`
- `orders.order_date`
- `orders.order_number`
- `order_items.order_id`
- `order_items.product_id`
- `payments.order_id`
- `payments.payment_status`

---

## Views

### `order_summary` View

A convenient view that aggregates order information:

```sql
CREATE VIEW order_summary AS
SELECT 
    o.id,
    o.order_number,
    o.order_date,
    o.status,
    o.total_amount,
    c.first_name || ' ' || c.last_name as customer_name,
    c.email as customer_email,
    COUNT(oi.id) as item_count,
    SUM(oi.quantity) as total_quantity,
    p.payment_method,
    p.payment_status
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.id
LEFT JOIN order_items oi ON o.id = oi.order_id
LEFT JOIN payments p ON o.id = p.order_id
GROUP BY o.id, o.order_number, o.order_date, o.status, o.total_amount, 
         c.first_name, c.last_name, c.email, p.payment_method, p.payment_status;
```

---

## Sample Queries

### Count Records
```sql
SELECT 
    'categories' as table_name, COUNT(*) as count FROM categories
UNION ALL
SELECT 'customers', COUNT(*) FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL
SELECT 'payments', COUNT(*) FROM payments;
```

### Orders by Status
```sql
SELECT status, COUNT(*) as count, SUM(total_amount) as total
FROM orders
GROUP BY status
ORDER BY count DESC;
```

### Top Customers
```sql
SELECT 
    c.first_name || ' ' || c.last_name as customer_name,
    COUNT(o.id) as order_count,
    SUM(o.total_amount) as total_spent
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.first_name, c.last_name
ORDER BY total_spent DESC
LIMIT 10;
```

### Products by Category
```sql
SELECT 
    cat.name as category,
    COUNT(p.id) as product_count,
    AVG(p.price) as avg_price,
    SUM(p.stock_quantity) as total_stock
FROM categories cat
LEFT JOIN products p ON cat.id = p.category_id
GROUP BY cat.id, cat.name
ORDER BY product_count DESC;
```

### Revenue by Month
```sql
SELECT 
    DATE_TRUNC('month', order_date) as month,
    COUNT(*) as order_count,
    SUM(total_amount) as revenue
FROM orders
WHERE status = 'delivered'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month DESC;
```

---

## Usage

### Initialize Database

The large dataset is automatically loaded when the database container starts:

```bash
# Start database (will run init_db_large.sql)
docker-compose up -d postgres
```

### Reset Database

To reset and reload the data:

```bash
# Stop and remove database
docker-compose down postgres
docker volume rm semantic_layer_analytics_postgres_data

# Start fresh
docker-compose up -d postgres
```

### Verify Data

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

---

## Performance Considerations

- **Indexes**: All foreign keys and frequently queried columns are indexed
- **Data Volume**: ~22,500 records total
- **Query Performance**: Optimized for common query patterns
- **Storage**: Estimated ~50-100 MB (depending on PostgreSQL version)

---

## Notes

- Data is randomly generated but realistic
- Relationships are properly maintained
- Dates span the past year
- All constraints and foreign keys are enforced
- Suitable for testing complex queries and aggregations

