\set ON_ERROR_STOP on
SET client_min_messages TO WARNING;

-- check 
SHOW wal_level;

-- update wal_level if needed in the file postgresql.conf

-- wal_level = logical
-- max_replication_slots = 10   -- or enough for your tables
-- max_wal_senders = 10

-- needed for CDC
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_publication WHERE pubname = 'olist_pub'
    ) THEN
        CREATE PUBLICATION olist_pub FOR TABLE 
            oltp.customers, 
            oltp.sellers, 
            oltp.products, 
            oltp.orders, 
            oltp.order_items, 
            oltp.order_payments, 
            oltp.order_reviews;
    END IF;
END $$;

-- verify
SELECT pubname FROM pg_publication;

-- run the docker compose file after this
