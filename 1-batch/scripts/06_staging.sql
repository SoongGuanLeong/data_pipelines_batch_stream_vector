CREATE SCHEMA IF NOT EXISTS staging;

-- Customers
DROP TABLE IF EXISTS staging.customers;
CREATE TABLE staging.customers (
    customer_id TEXT PRIMARY KEY,
    customer_unique_id TEXT,
    customer_zip_code_prefix TEXT,
    customer_city TEXT,
    customer_state TEXT
);

-- Geolocations (optional enrichment)
DROP TABLE IF EXISTS staging.geolocations_enrichment;
CREATE TABLE staging.geolocations_enrichment (
    geolocation_zip_code_prefix TEXT,
    geolocation_lat NUMERIC,
    geolocation_lng NUMERIC,
    geolocation_city TEXT,
    geolocation_state TEXT
);

-- Sellers
DROP TABLE IF EXISTS staging.sellers;
CREATE TABLE staging.sellers (
    seller_id TEXT PRIMARY KEY,
    seller_zip_code_prefix TEXT,
    seller_city TEXT,
    seller_state TEXT
);

-- Product Categories
DROP TABLE IF EXISTS staging.product_categories;
CREATE TABLE staging.product_categories (
    product_category_name TEXT PRIMARY KEY,
    product_category_name_english TEXT
);

-- Products
DROP TABLE IF EXISTS staging.products;
CREATE TABLE staging.products (
    product_id TEXT PRIMARY KEY,
    product_category_name TEXT,
    product_name_length INT,
    product_description_length INT,
    product_photos_qty INT,
    product_weight_g INT,
    product_length_cm INT,
    product_height_cm INT,
    product_width_cm INT
);

-- Orders
DROP TABLE IF EXISTS staging.orders;
CREATE TABLE staging.orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT,
    order_status TEXT,
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

-- Order Items
DROP TABLE IF EXISTS staging.order_items;
CREATE TABLE staging.order_items (
    order_id TEXT,
    order_item_id INT,
    product_id TEXT,
    seller_id TEXT,
    shipping_limit_date TIMESTAMP,
    price NUMERIC,
    freight_value NUMERIC,
    PRIMARY KEY (order_id, order_item_id)
);

-- Order Payments
DROP TABLE IF EXISTS staging.order_payments;
CREATE TABLE staging.order_payments (
    order_id TEXT,
    payment_sequential INT,
    payment_type TEXT,
    payment_installments INT,
    payment_value NUMERIC,
    PRIMARY KEY (order_id, payment_sequential)
);

-- Order Reviews
DROP TABLE IF EXISTS staging.order_reviews;
CREATE TABLE staging.order_reviews (
    review_id TEXT,
    order_id TEXT,
    review_score INT,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP
);
