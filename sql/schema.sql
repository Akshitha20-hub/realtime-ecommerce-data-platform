-- PostgreSQL schema for e-commerce data warehouse
-- Table: customers
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    gender TEXT CHECK (gender IN ('M','F','Other')),
    age INTEGER CHECK (age >= 0),
    city TEXT,
    state TEXT,
    signup_date TIMESTAMP NOT NULL,
    customer_segment TEXT
);

-- Table: products
CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT,
    subcategory TEXT,
    price NUMERIC(12,2) CHECK (price >= 0),
    cost NUMERIC(12,2) CHECK (cost >= 0),
    stock_quantity INTEGER CHECK (stock_quantity >= 0),
    product_rating NUMERIC(3,2) CHECK (product_rating >= 0 AND product_rating <= 5)
);

-- Table: orders
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    order_date TIMESTAMP NOT NULL,
    order_status TEXT,
    shipping_city TEXT,
    shipping_state TEXT,
    payment_method TEXT,
    total_amount NUMERIC(12,2) CHECK (total_amount >= 0)
);

-- Table: order_items
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL REFERENCES orders(order_id),
    product_id TEXT NOT NULL REFERENCES products(product_id),
    quantity INTEGER CHECK (quantity > 0),
    unit_price NUMERIC(12,2) CHECK (unit_price >= 0),
    discount NUMERIC(12,2) DEFAULT 0 CHECK (discount >= 0),
    subtotal NUMERIC(12,2) CHECK (subtotal >= 0)
);

-- Table: payments
CREATE TABLE IF NOT EXISTS payments (
    payment_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL REFERENCES orders(order_id),
    payment_method TEXT,
    payment_status TEXT,
    payment_amount NUMERIC(12,2) CHECK (payment_amount >= 0),
    payment_date TIMESTAMP NOT NULL
);

-- Table: events
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    customer_id TEXT REFERENCES customers(customer_id),
    product_id TEXT REFERENCES products(product_id),
    event_type TEXT,
    event_timestamp TIMESTAMP NOT NULL,
    session_id TEXT
);

-- ETL run audit table
CREATE TABLE IF NOT EXISTS etl_run_log (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_timestamp TIMESTAMP DEFAULT now(),
    pipeline_name TEXT NOT NULL,
    dataset_name TEXT,
    rows_processed INTEGER,
    rows_success INTEGER,
    rows_failed INTEGER,
    status TEXT CHECK (status IN ('SUCCESS','FAILED')),
    error_message TEXT
);
