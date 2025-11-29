-- Initialize database with sample data for testing

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(50) PRIMARY KEY,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL
);

-- Create customers table (for relationship testing)
CREATE TABLE IF NOT EXISTS customers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

-- Insert sample customers
INSERT INTO customers (id, name, email, created_at) VALUES
    ('customer_1', 'John Doe', 'john@example.com', '2024-01-01 10:00:00'),
    ('customer_2', 'Jane Smith', 'jane@example.com', '2024-01-02 11:00:00'),
    ('customer_3', 'Bob Johnson', 'bob@example.com', '2024-01-03 12:00:00')
ON CONFLICT (id) DO NOTHING;

-- Insert sample orders
INSERT INTO orders (id, status, created_at, customer_id, total_amount) VALUES
    ('order_1', 'completed', '2024-01-15 10:00:00', 'customer_1', 100.50),
    ('order_2', 'completed', '2024-01-15 11:00:00', 'customer_1', 250.75),
    ('order_3', 'pending', '2024-01-15 12:00:00', 'customer_2', 75.25),
    ('order_4', 'completed', '2024-01-16 10:00:00', 'customer_2', 300.00),
    ('order_5', 'cancelled', '2024-01-16 11:00:00', 'customer_3', 50.00),
    ('order_6', 'completed', '2024-01-16 12:00:00', 'customer_3', 150.00),
    ('order_7', 'completed', '2024-01-17 10:00:00', 'customer_1', 200.00),
    ('order_8', 'pending', '2024-01-17 11:00:00', 'customer_2', 125.50),
    ('order_9', 'completed', '2024-01-17 12:00:00', 'customer_3', 175.75),
    ('order_10', 'completed', '2024-01-18 10:00:00', 'customer_1', 90.25)
ON CONFLICT (id) DO NOTHING;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);

