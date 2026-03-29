-- Geolocation is probably dirty / duplicated / enrichment 
-- (two FKs below might not work and can be removed)

-- -- customers - geolocations_enrichment
-- ALTER TABLE oltp.customers
--     ADD CONSTRAINT fk_customer_zip_code
--     FOREIGN KEY (customer_zip_code_prefix) 
--     REFERENCES oltp.geolocations_enrichment(geolocation_zip_code_prefix);

-- -- sellers - geolocations_enrichment
-- ALTER TABLE oltp.sellers
--     ADD CONSTRAINT fk_seller_zip_code 
--     FOREIGN KEY (seller_zip_code_prefix) 
--     REFERENCES oltp.geolocations_enrichment(geolocation_zip_code_prefix);

-- products - product_categories
ALTER TABLE oltp.products
    ADD CONSTRAINT fk_product_category
    FOREIGN KEY (product_category_name) 
    REFERENCES oltp.product_categories(product_category_name);

-- orders - customers
ALTER TABLE oltp.orders
    ADD CONSTRAINT fk_order_customer
    FOREIGN KEY (customer_id) 
    REFERENCES oltp.customers(customer_id);

-- items - orders
ALTER TABLE oltp.order_items
    ADD CONSTRAINT fk_order_item_order
    FOREIGN KEY (order_id) 
    REFERENCES oltp.orders(order_id);

-- items - products
ALTER TABLE oltp.order_items
    ADD CONSTRAINT fk_order_item_product
    FOREIGN KEY (product_id) 
    REFERENCES oltp.products(product_id);

-- items - sellers
ALTER TABLE oltp.order_items
    ADD CONSTRAINT fk_order_item_seller
    FOREIGN KEY (seller_id) 
    REFERENCES oltp.sellers(seller_id);

-- payments - orders
ALTER TABLE oltp.order_payments
    ADD CONSTRAINT fk_order_payment_order
    FOREIGN KEY (order_id) 
    REFERENCES oltp.orders(order_id);

-- reviews - orders
ALTER TABLE oltp.order_reviews
    ADD CONSTRAINT fk_order_review_order
    FOREIGN KEY (order_id) 
    REFERENCES oltp.orders(order_id);
