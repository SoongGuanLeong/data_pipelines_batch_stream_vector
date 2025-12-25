-- 1. postgres >= 10
SELECT version();

-- 2. rolreplication = true
SELECT rolreplication
FROM pg_roles
WHERE rolname = current_user;

-- 3. wal_level = logical
SHOW wal_level;

-- 4. more than tables to replicate
SHOW max_replication_slots;
SHOW max_wal_senders;

-- 5. check if publication created in previous step still exists
SELECT * FROM pg_publication;