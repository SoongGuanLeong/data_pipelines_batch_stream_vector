ALTER TABLE oltp.customers
ADD COLUMN loyalty_level TEXT;

INSERT INTO oltp.customers (customer_id, loyalty_level)
VALUES ('cdc_schema_test', 'gold');

DELETE FROM oltp.customers
WHERE customer_id = 'cdc_schema_test';

ALTER TABLE oltp.customers
DROP COLUMN loyalty_level;