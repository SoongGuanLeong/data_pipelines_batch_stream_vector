\set ON_ERROR_STOP on
SET client_min_messages TO WARNING;

\set data_dir '../docker/datasets'

BEGIN;

-- customers - 99441 rows
TRUNCATE TABLE staging.customers;
COPY staging.customers
FROM :'data_dir'/olist_customers_dataset.csv
WITH (FORMAT csv, HEADER true);

-- Geolocations (optional enrichment) - 1000163 rows
TRUNCATE TABLE staging.geolocations_enrichment;
COPY staging.geolocations_enrichment
FROM :'data_dir'/olist_geolocation_dataset.csv
WITH (FORMAT csv, HEADER true);

-- Sellers - 3095 rows
TRUNCATE TABLE staging.sellers;
COPY staging.sellers
FROM :'data_dir'/olist_sellers_dataset.csv
WITH (FORMAT csv, HEADER true);

-- Product Categories - 71 rows
TRUNCATE TABLE staging.product_categories;
COPY staging.product_categories
FROM :'data_dir'/product_category_name_translation.csv
WITH (FORMAT csv, HEADER true);

-- Products - 32951 rows
TRUNCATE TABLE staging.products;
COPY staging.products
FROM :'data_dir'/olist_products_dataset.csv
WITH (FORMAT csv, HEADER true);

-- Orders - 99441 rows
TRUNCATE TABLE staging.orders;
COPY staging.orders
FROM :'data_dir'/olist_orders_dataset.csv
WITH (FORMAT csv, HEADER true);

-- Order Items - 112650 rows
TRUNCATE TABLE staging.order_items;
COPY staging.order_items
FROM :'data_dir'/olist_order_items_dataset.csv
WITH (FORMAT csv, HEADER true);

-- Order Payments - 103886 rows
TRUNCATE TABLE staging.order_payments;
COPY staging.order_payments
FROM :'data_dir'/olist_order_payments_dataset.csv
WITH (FORMAT csv, HEADER true);

-- Order Reviews - 104719 rows (only this is different - 99224, some rows are empty)
TRUNCATE TABLE staging.order_reviews;
COPY staging.order_reviews
FROM :'data_dir'/olist_order_reviews_dataset.csv
WITH (FORMAT csv, HEADER true);

COMMIT;

ANALYZE staging;

-- post-load check
SELECT * FROM (
    SELECT 'customers' AS table_name, COUNT(*) FROM staging.customers
    UNION ALL
    SELECT 'geolocations', COUNT(*) FROM staging.geolocations_enrichment
    UNION ALL
    SELECT 'sellers', COUNT(*) FROM staging.sellers
    UNION ALL
    SELECT 'product_categories', COUNT(*) FROM staging.product_categories
    UNION ALL
    SELECT 'products', COUNT(*) FROM staging.products
    UNION ALL
    SELECT 'orders', COUNT(*) FROM staging.orders
    UNION ALL
    SELECT 'order_items', COUNT(*) FROM staging.order_items
    UNION ALL
    SELECT 'order_payments', COUNT(*) FROM staging.order_payments
    UNION ALL
    SELECT 'order_reviews', COUNT(*) FROM staging.order_reviews;
) t
ORDER BY table_name;
