-- Usage (direct):
-- psql -d olist -v dataset_dir="/absolute/path/to/1-batch/dataset" -f 1-batch/scripts/07_load_staging.sql
--
-- Usage (with Makefile):
-- make load-staging DATASET_DIR=/absolute/path/to/1-batch/dataset

-- If dataset_dir is not passed, default to <current_working_directory>/docker/dataset.
-- assuming project root is where Makefile is located
\if :{?dataset_dir}
\else
\getenv dataset_dir PWD
\set dataset_dir :dataset_dir '/docker/dataset'
\endif

\echo Using dataset_dir= :dataset_dir

\set customers_csv :dataset_dir '/olist_customers_dataset.csv'
\set geolocations_csv :dataset_dir '/olist_geolocation_dataset.csv'
\set sellers_csv :dataset_dir '/olist_sellers_dataset.csv'
\set categories_csv :dataset_dir '/product_category_name_translation.csv'
\set products_csv :dataset_dir '/olist_products_dataset.csv'
\set orders_csv :dataset_dir '/olist_orders_dataset.csv'
\set order_items_csv :dataset_dir '/olist_order_items_dataset.csv'
\set order_payments_csv :dataset_dir '/olist_order_payments_dataset.csv'
\set order_reviews_csv :dataset_dir '/olist_order_reviews_dataset.csv'

SET client_min_messages TO WARNING;

-- optional cleanup before reload (idempotent reruns)
BEGIN;
TRUNCATE TABLE IF EXISTS staging.customers;
TRUNCATE TABLE IF EXISTS staging.geolocations_enrichment;
TRUNCATE TABLE IF EXISTS staging.sellers;
TRUNCATE TABLE IF EXISTS staging.product_categories;
TRUNCATE TABLE IF EXISTS staging.products;
TRUNCATE TABLE IF EXISTS staging.orders;
TRUNCATE TABLE IF EXISTS staging.order_items;
TRUNCATE TABLE IF EXISTS staging.order_payments;
TRUNCATE TABLE IF EXISTS staging.order_reviews;
COMMIT;

-- customers - 99441 rows
COPY staging.customers
FROM :'customers_csv'
WITH (FORMAT csv, HEADER true);

-- Geolocations (optional enrichment) - 1000163 rows
COPY staging.geolocations_enrichment
FROM :'geolocations_csv'
WITH (FORMAT csv, HEADER true);

-- Sellers - 3095 rows
COPY staging.sellers
FROM :'sellers_csv'
WITH (FORMAT csv, HEADER true);

-- Product Categories - 71 rows
COPY staging.product_categories
FROM :'categories_csv'
WITH (FORMAT csv, HEADER true);

-- Products - 32951 rows
COPY staging.products
FROM :'products_csv'
WITH (FORMAT csv, HEADER true);

-- Orders - 99441 rows
COPY staging.orders
FROM :'orders_csv'
WITH (FORMAT csv, HEADER true);

-- Order Items - 112650 rows
COPY staging.order_items
FROM :'order_items_csv'
WITH (FORMAT csv, HEADER true);

-- Order Payments - 103886 rows
COPY staging.order_payments
FROM :'order_payments_csv'/
WITH (FORMAT csv, HEADER true);

-- Order Reviews - 104719 rows (only this is different - 99224, some rows are empty)
COPY staging.order_reviews
FROM :'order_reviews_csv'
WITH (FORMAT csv, HEADER true);

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

ANALYZE staging;
