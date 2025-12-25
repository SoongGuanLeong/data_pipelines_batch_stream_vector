-- INSERT UPDATE DELETE all tables involved in CDC
-- run each command one by one
-- we do not want to edit anything so we delete everything at the end

-- customers
INSERT INTO oltp.customers (
  customer_id,
  customer_unique_id,
  customer_zip_code_prefix,
  customer_city,
  customer_state
)
VALUES (
  'cdc_test_1',
  'cdc_test_1',
  '12345',
  'CDC_CITY',
  'SP'
);

UPDATE oltp.customers
SET customer_city = 'UPDATED_CITY'
WHERE customer_id = 'cdc_test_1';

DELETE FROM oltp.customers
WHERE customer_id = 'cdc_test_1';


-- orders (FK constraint: customers)
INSERT INTO oltp.customers (
  customer_id,
  customer_unique_id,
  customer_zip_code_prefix,
  customer_city,
  customer_state
)
VALUES (
  'c1',
  'c1',
  '12345',
  'CDC_CITY',
  'SP'
);

INSERT INTO oltp.orders (order_id, customer_id, order_status) 
VALUES ('o1','c1','created');

UPDATE oltp.orders 
SET order_status='shipped' 
WHERE order_id='o1';

DELETE FROM oltp.orders 
WHERE order_id='o1';

DELETE FROM oltp.customers 
WHERE customer_id='c1';


-- products (FK constraint:: product_categories)
INSERT INTO oltp.product_categories (product_category_name)
VALUES ('cat1');

INSERT INTO oltp.products (product_id, product_category_name, product_photos_qty) 
VALUES ('p1','cat1', 1);

UPDATE oltp.products 
SET product_photos_qty=2 
WHERE product_id='p1';

DELETE FROM oltp.products 
WHERE product_id='p1';

DELETE FROM oltp.product_categories 
WHERE product_category_name='cat1';


-- sellers
INSERT INTO oltp.sellers (seller_id, seller_city) 
VALUES ('s1','CITY');

UPDATE oltp.sellers SET seller_city='NEW_CITY'
WHERE seller_id='s1';

DELETE FROM oltp.sellers 
WHERE seller_id='s1';