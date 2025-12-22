-- check 
SHOW wal_level;

-- update wal_level if needed in the file postgresql.conf

-- wal_level = logical
-- max_replication_slots = 10   -- or enough for your tables
-- max_wal_senders = 10

-- needed for CDC
CREATE PUBLICATION olist_pub FOR TABLE 
    oltp.customers, 
    oltp.sellers, 
    oltp.products, 
    oltp.orders, 
    oltp.order_items, 
    oltp.order_payments, 
    oltp.order_reviews;
