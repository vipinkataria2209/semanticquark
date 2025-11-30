-- Initialize database with comprehensive schema and large dataset for testing

-- Drop existing tables if they exist (for clean reset)
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- Create categories table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create customers table
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

-- Create products table
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

-- Create orders table
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

-- Create order_items table (many-to-many relationship)
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

-- Create payments table
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

-- Create indexes for better performance
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_created_at ON customers(created_at);
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_order_date ON orders(order_date);
CREATE INDEX idx_orders_order_number ON orders(order_number);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
CREATE INDEX idx_payments_order_id ON payments(order_id);
CREATE INDEX idx_payments_payment_status ON payments(payment_status);

-- Insert categories (10 categories)
INSERT INTO categories (name, description) VALUES
    ('Electronics', 'Electronic devices and accessories'),
    ('Clothing', 'Apparel and fashion items'),
    ('Home & Garden', 'Home improvement and garden supplies'),
    ('Books', 'Books and publications'),
    ('Sports & Outdoors', 'Sports equipment and outdoor gear'),
    ('Toys & Games', 'Toys and games for all ages'),
    ('Health & Beauty', 'Health and beauty products'),
    ('Automotive', 'Automotive parts and accessories'),
    ('Food & Beverages', 'Food and beverage products'),
    ('Office Supplies', 'Office and stationery supplies');

-- Generate customers (2000 customers)
INSERT INTO customers (first_name, last_name, email, phone, address, city, state, zip_code, country, created_at)
SELECT 
    first_names[1 + floor(random() * array_length(first_names, 1))::int],
    last_names[1 + floor(random() * array_length(last_names, 1))::int],
    'customer' || generate_series || '@example.com',
    '(' || (100 + floor(random() * 900)::int)::text || ') ' || 
    (100 + floor(random() * 900)::int)::text || '-' || 
    (1000 + floor(random() * 9000)::int)::text,
    (100 + floor(random() * 9000)::int)::text || ' ' ||
    (ARRAY['Main St', 'Oak Ave', 'Park Blvd', 'Elm St', 'Cedar Rd', 'Maple Dr', 'Pine Ln', 'First St', 'Second Ave', 'Third Blvd'])[1 + floor(random() * 10)::int],
    (ARRAY['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose'])[1 + floor(random() * 10)::int],
    (ARRAY['NY', 'CA', 'IL', 'TX', 'AZ', 'PA', 'TX', 'CA', 'TX', 'CA'])[1 + floor(random() * 10)::int],
    LPAD((10000 + floor(random() * 90000)::int)::text, 5, '0'),
    'USA',
    CURRENT_TIMESTAMP - (random() * interval '365 days')
FROM generate_series(1, 2000),
LATERAL (SELECT ARRAY['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica', 'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa', 'Matthew', 'Betty', 'Anthony', 'Margaret', 'Mark', 'Sandra', 'Donald', 'Ashley', 'Steven', 'Kimberly', 'Paul', 'Emily', 'Andrew', 'Donna', 'Joshua', 'Michelle'] as first_names) fn,
LATERAL (SELECT ARRAY['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores', 'Green', 'Adams'] as last_names) ln;

-- Generate products (500 products)
INSERT INTO products (name, description, category_id, sku, price, cost, stock_quantity, is_active, created_at)
SELECT 
    product_names[1 + floor(random() * array_length(product_names, 1))::int] || ' ' || 
    (ARRAY['Pro', 'Deluxe', 'Premium', 'Standard', 'Basic', 'Advanced', 'Ultra', 'Plus', 'Elite', 'Classic'])[1 + floor(random() * 10)::int],
    'High-quality ' || product_names[1 + floor(random() * array_length(product_names, 1))::int] || ' for your needs',
    1 + floor(random() * 10)::int,
    'SKU-' || LPAD(generate_series::text, 6, '0'),
    9.99 + (random() * 990.01),
    5.00 + (random() * 400.00),
    10 + floor(random() * 990)::int,
    CASE WHEN random() > 0.1 THEN TRUE ELSE FALSE END,
    CURRENT_TIMESTAMP - (random() * interval '180 days')
FROM generate_series(1, 500),
LATERAL (SELECT ARRAY['Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Speaker', 'Camera', 'Watch', 'Monitor', 'Keyboard', 'Mouse', 'Shirt', 'Pants', 'Shoes', 'Jacket', 'Hat', 'Book', 'Pen', 'Desk', 'Chair', 'Lamp', 'Ball', 'Bike', 'Tent', 'Backpack', 'Tool', 'Gadget', 'Device', 'Accessory', 'Item', 'Product'] as product_names) pn;

-- Generate orders (5000 orders)
INSERT INTO orders (customer_id, order_number, status, order_date, shipped_date, delivered_date, subtotal, tax, shipping_cost, discount, total_amount, shipping_address, billing_address, notes, created_at, updated_at)
SELECT 
    1 + floor(random() * 2000)::int,
    'ORD-' || LPAD(generate_series::text, 8, '0'),
    (ARRAY['pending', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded'])[1 + floor(random() * 6)::int],
    CURRENT_TIMESTAMP - (random() * interval '365 days'),
    CASE 
        WHEN random() > 0.3 THEN CURRENT_TIMESTAMP - (random() * interval '360 days')
        ELSE NULL
    END,
    CASE 
        WHEN random() > 0.5 THEN CURRENT_TIMESTAMP - (random() * interval '350 days')
        ELSE NULL
    END,
    10.00 + (random() * 990.00),
    (10.00 + (random() * 990.00)) * 0.08,
    CASE WHEN random() > 0.5 THEN 5.99 ELSE 0.00 END,
    CASE WHEN random() > 0.7 THEN (10.00 + (random() * 990.00)) * (0.05 + random() * 0.15) ELSE 0.00 END,
    10.00 + (random() * 990.00) + (10.00 + (random() * 990.00)) * 0.08 + 
    CASE WHEN random() > 0.5 THEN 5.99 ELSE 0.00 END - 
    CASE WHEN random() > 0.7 THEN (10.00 + (random() * 990.00)) * (0.05 + random() * 0.15) ELSE 0.00 END,
    (100 + floor(random() * 9000)::int)::text || ' ' ||
    (ARRAY['Main St', 'Oak Ave', 'Park Blvd', 'Elm St', 'Cedar Rd'])[1 + floor(random() * 5)::int] || ', ' ||
    (ARRAY['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'])[1 + floor(random() * 5)::int] || ', ' ||
    (ARRAY['NY', 'CA', 'IL', 'TX', 'AZ'])[1 + floor(random() * 5)::int] || ' ' ||
    LPAD((10000 + floor(random() * 90000)::int)::text, 5, '0'),
    (100 + floor(random() * 9000)::int)::text || ' ' ||
    (ARRAY['Main St', 'Oak Ave', 'Park Blvd', 'Elm St', 'Cedar Rd'])[1 + floor(random() * 5)::int] || ', ' ||
    (ARRAY['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'])[1 + floor(random() * 5)::int] || ', ' ||
    (ARRAY['NY', 'CA', 'IL', 'TX', 'AZ'])[1 + floor(random() * 5)::int] || ' ' ||
    LPAD((10000 + floor(random() * 90000)::int)::text, 5, '0'),
    CASE WHEN random() > 0.8 THEN 'Special instructions or notes' ELSE NULL END,
    CURRENT_TIMESTAMP - (random() * interval '365 days'),
    CURRENT_TIMESTAMP - (random() * interval '360 days')
FROM generate_series(1, 5000);

-- Generate order_items (10000 order items, 1-5 items per order)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount, total_price, created_at)
SELECT 
    o.id,
    1 + floor(random() * 500)::int,
    1 + floor(random() * 5)::int,
    p.price,
    CASE WHEN random() > 0.8 THEN p.price * (0.05 + random() * 0.15) ELSE 0.00 END,
    (p.price * (1 + floor(random() * 5)::int)) - 
    CASE WHEN random() > 0.8 THEN p.price * (0.05 + random() * 0.15) ELSE 0.00 END,
    o.order_date
FROM orders o
CROSS JOIN LATERAL (
    SELECT 1 + floor(random() * (1 + floor(random() * 4)::int))::int as item_count
) ic
CROSS JOIN LATERAL generate_series(1, ic.item_count)
CROSS JOIN LATERAL (
    SELECT price FROM products WHERE id = (1 + floor(random() * 500)::int) LIMIT 1
) p
LIMIT 10000;

-- Generate payments (5000 payments, one per order)
INSERT INTO payments (order_id, payment_method, payment_status, amount, transaction_id, payment_date, created_at)
SELECT 
    o.id,
    (ARRAY['credit_card', 'debit_card', 'paypal', 'bank_transfer', 'cash', 'gift_card'])[1 + floor(random() * 6)::int],
    CASE 
        WHEN o.status IN ('delivered', 'shipped') THEN 
            (ARRAY['completed', 'processed'])[1 + floor(random() * 2)::int]
        WHEN o.status = 'cancelled' THEN 'refunded'
        WHEN o.status = 'refunded' THEN 'refunded'
        ELSE (ARRAY['pending', 'processing', 'failed'])[1 + floor(random() * 3)::int]
    END,
    o.total_amount,
    'TXN-' || LPAD((1000000 + floor(random() * 9000000)::int)::text, 10, '0'),
    o.order_date + (random() * interval '1 day'),
    o.order_date
FROM orders o;

-- Update order totals based on order_items
UPDATE orders o
SET 
    subtotal = COALESCE((
        SELECT SUM(total_price) 
        FROM order_items 
        WHERE order_id = o.id
    ), o.subtotal),
    total_amount = COALESCE((
        SELECT SUM(total_price) 
        FROM order_items 
        WHERE order_id = o.id
    ), o.subtotal) + o.tax + o.shipping_cost - o.discount;

-- Create a view for order summary
CREATE OR REPLACE VIEW order_summary AS
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
GROUP BY o.id, o.order_number, o.order_date, o.status, o.total_amount, c.first_name, c.last_name, c.email, p.payment_method, p.payment_status;

-- Display summary statistics
DO $$
DECLARE
    customer_count INTEGER;
    product_count INTEGER;
    order_count INTEGER;
    order_item_count INTEGER;
    payment_count INTEGER;
    category_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO customer_count FROM customers;
    SELECT COUNT(*) INTO product_count FROM products;
    SELECT COUNT(*) INTO order_count FROM orders;
    SELECT COUNT(*) INTO order_item_count FROM order_items;
    SELECT COUNT(*) INTO payment_count FROM payments;
    SELECT COUNT(*) INTO category_count FROM categories;
    
    RAISE NOTICE 'Database initialization complete!';
    RAISE NOTICE 'Categories: %', category_count;
    RAISE NOTICE 'Customers: %', customer_count;
    RAISE NOTICE 'Products: %', product_count;
    RAISE NOTICE 'Orders: %', order_count;
    RAISE NOTICE 'Order Items: %', order_item_count;
    RAISE NOTICE 'Payments: %', payment_count;
END $$;

