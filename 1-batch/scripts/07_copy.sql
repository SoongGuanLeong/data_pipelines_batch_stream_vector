-- optional safety checks
SET client_min_messages TO WARNING;

-- customers - 99441 rows
COPY staging.customers
FROM 'E:/Desktop/data_pipelines_batch_stream_vector/1-batch/dataset/olist_customers_dataset.csv'
WITH (FORMAT csv, HEADER true);

-- Geolocations (optional enrichment) - 1000163 rows
COPY staging.geolocations_enrichment
FROM 'E:/Desktop/data_pipelines_batch_stream_vector/1-batch/dataset/olist_geolocation_dataset.csv'
WITH (FORMAT csv, HEADER true);

-- Sellers - 3095 rows
COPY staging.sellers
FROM 'E:/Desktop/data_pipelines_batch_stream_vector/1-batch/dataset/olist_sellers_dataset.csv'
WITH (FORMAT csv, HEADER true);

-- Product Categories - 71 rows
COPY staging.product_categories
FROM 'E:/Desktop/data_pipelines_batch_stream_vector/1-batch/dataset/product_category_name_translation.csv'
WITH (FORMAT csv, HEADER true);

-- Products - 32951 rows
COPY staging.products
FROM 'E:/Desktop/data_pipelines_batch_stream_vector/1-batch/dataset/olist_products_dataset.csv'
WITH (FORMAT csv, HEADER true);

-- Orders - 99441 rows
COPY staging.orders
FROM 'E:/Desktop/data_pipelines_batch_stream_vector/1-batch/dataset/olist_orders_dataset.csv'
WITH (FORMAT csv, HEADER true);

-- Order Items - 112650 rows
COPY staging.order_items
FROM 'E:/Desktop/data_pipelines_batch_stream_vector/1-batch/dataset/olist_order_items_dataset.csv'
WITH (FORMAT csv, HEADER true);

-- Order Payments - 103886 rows
COPY staging.order_payments
FROM 'E:/Desktop/data_pipelines_batch_stream_vector/1-batch/dataset/olist_order_payments_dataset.csv'
WITH (FORMAT csv, HEADER true);

-- Order Reviews - 104719 rows (only this is different - 99224, some rows are empty)
COPY staging.order_reviews
FROM 'E:/Desktop/data_pipelines_batch_stream_vector/1-batch/dataset/olist_order_reviews_dataset.csv'
WITH (FORMAT csv, HEADER true);



-- post-load check
SELECT 'customers', COUNT(*) FROM staging.customers
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
