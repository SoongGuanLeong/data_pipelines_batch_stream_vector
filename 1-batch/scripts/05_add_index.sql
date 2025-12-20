-- =====================================================
-- CDC PERFORMANCE INDEXES
-- =====================================================

--------------------------------------------------------
-- Geolocation (probably dirty & hence not indexed)
--------------------------------------------------------
CREATE INDEX idx_customers_zip_code
ON oltp.customers (customer_zip_code_prefix);

CREATE INDEX idx_sellers_zip_code
ON oltp.sellers (seller_zip_code_prefix);

--------------------------------------------------------
-- products - product_categories
--------------------------------------------------------
CREATE INDEX idx_products_category_name
ON oltp.products (product_category_name);

--------------------------------------------------------
-- orders - customers
--------------------------------------------------------
CREATE INDEX idx_orders_customer_id
ON oltp.orders (customer_id);

--------------------------------------------------------
-- items - orders / products / sellers
--------------------------------------------------------
CREATE INDEX idx_order_items_order_id
ON oltp.order_items (order_id);

CREATE INDEX idx_order_items_product_id
ON oltp.order_items (product_id);

CREATE INDEX idx_order_items_seller_id
ON oltp.order_items (seller_id);

--------------------------------------------------------
-- payments - orders
--------------------------------------------------------
CREATE INDEX idx_order_payments_order_id
ON oltp.order_payments (order_id);

--------------------------------------------------------
-- reviews - orders
--------------------------------------------------------
CREATE INDEX idx_order_reviews_order_id
ON oltp.order_reviews (order_id);
