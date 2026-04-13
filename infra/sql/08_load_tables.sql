-- order of loading matters due to FK constraints
-- table without FKs first (refer ERD diagram)

-- product_categories
INSERT INTO oltp.product_categories (
    product_category_name,
    product_category_name_english
)
SELECT DISTINCT
    product_category_name,
    product_category_name_english
FROM staging.product_categories
WHERE product_category_name IS NOT NULL  -- this table don't have PK
ON CONFLICT (product_category_name) DO NOTHING;

-- geolocations (enrichment)
INSERT INTO oltp.geolocations_enrichment (
    geolocation_zip_code_prefix,
    geolocation_lat,
    geolocation_lng,
    geolocation_city,
    geolocation_state
)
SELECT DISTINCT
    geolocation_zip_code_prefix,
    geolocation_lat,
    geolocation_lng,
    geolocation_city,
    geolocation_state
FROM staging.geolocations_enrichment
WHERE geolocation_zip_code_prefix IS NOT NULL;  -- this table don't have PK

-- customers
INSERT INTO oltp.customers (
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
)
SELECT DISTINCT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
FROM staging.customers
ON CONFLICT (customer_id) DO NOTHING;

-- sellers
INSERT INTO oltp.sellers (
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
)
SELECT DISTINCT
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM staging.sellers
ON CONFLICT (seller_id) DO NOTHING;

-- products
INSERT INTO oltp.products (
    product_id,
    product_category_name,
    product_name_length,
    product_description_length,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm
)
SELECT DISTINCT
    product_id,
    product_category_name,
    product_name_length,
    product_description_length,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm
FROM staging.products
ON CONFLICT (product_id) DO NOTHING;

-- orders
INSERT INTO oltp.orders (
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date
)
SELECT DISTINCT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date
FROM staging.orders
ON CONFLICT (order_id) DO NOTHING;

-- order_items
INSERT INTO oltp.order_items (
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date,
    price,
    freight_value
)
SELECT
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date,
    price,
    freight_value
FROM staging.order_items
ON CONFLICT (order_id, order_item_id) DO NOTHING;

-- order_payments
INSERT INTO oltp.order_payments (
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value
)
SELECT
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value
FROM staging.order_payments
ON CONFLICT (order_id, payment_sequential) DO NOTHING;

-- order_reviews
INSERT INTO oltp.order_reviews (
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,
    review_creation_date,
    review_answer_timestamp
)
SELECT
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,
    review_creation_date,
    review_answer_timestamp
FROM staging.order_reviews
ON CONFLICT (review_id) DO NOTHING;

-- Backfills missing categories
-- Leaves product_category_name_english as NULL
INSERT INTO oltp.product_categories (product_category_name)
SELECT DISTINCT product_category_name
FROM staging.products
WHERE product_category_name IS NOT NULL
ON CONFLICT (product_category_name) DO NOTHING;


-- post-load check (only order reviews is different - 98410 rows)
SELECT 'customers', COUNT(*) FROM oltp.customers
UNION ALL
SELECT 'sellers', COUNT(*) FROM oltp.sellers
UNION ALL
SELECT 'products', COUNT(*) FROM oltp.products
UNION ALL
SELECT 'orders', COUNT(*) FROM oltp.orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM oltp.order_items
UNION ALL
SELECT 'order_payments', COUNT(*) FROM oltp.order_payments
UNION ALL
SELECT 'order_reviews', COUNT(*) FROM oltp.order_reviews;

-- FK integrity checks - no rows should be returned
-- orders → customers
SELECT COUNT(*)
FROM oltp.orders o
LEFT JOIN oltp.customers c
  ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- order_items → orders
SELECT COUNT(*)
FROM oltp.order_items oi
LEFT JOIN oltp.orders o
  ON oi.order_id = o.order_id
WHERE o.order_id IS NULL;

-- order_items → products
SELECT COUNT(*)
FROM oltp.order_items oi
LEFT JOIN oltp.products p
  ON oi.product_id = p.product_id
WHERE p.product_id IS NULL;

-- order_items → sellers
SELECT COUNT(*)
FROM oltp.order_items oi
LEFT JOIN oltp.sellers s
  ON oi.seller_id = s.seller_id
WHERE s.seller_id IS NULL;

-- order_payments → orders
SELECT COUNT(*)
FROM oltp.order_payments op
LEFT JOIN oltp.orders o
  ON op.order_id = o.order_id
WHERE o.order_id IS NULL;

-- order_reviews → orders
SELECT COUNT(*)
FROM oltp.order_reviews r
LEFT JOIN oltp.orders o
  ON r.order_id = o.order_id
WHERE o.order_id IS NULL;

-- products → product_categories (this fail checks)
SELECT COUNT(*)
FROM oltp.products p
LEFT JOIN oltp.product_categories pc
  ON p.product_category_name = pc.product_category_name
WHERE pc.product_category_name IS NULL;

-- FK validation: ensure all NON-NULL product_category_name values
-- in oltp.products have a matching parent row in oltp.product_categories.
-- NULL category values are allowed by design and are NOT FK violations.
SELECT COUNT(*)
FROM oltp.products p
LEFT JOIN oltp.product_categories pc
  ON p.product_category_name = pc.product_category_name
WHERE p.product_category_name IS NOT NULL
  AND pc.product_category_name IS NULL;

-- rerun insert into until post-load check (should return the same counts)
