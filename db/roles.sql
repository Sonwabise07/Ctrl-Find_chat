-- Read-only role the assistant connects with. This is the hard safety boundary: it can only SELECT.
-- Run as a superuser. Re-run GRANT after applying proposed_migration.sql so the new tables are readable.
DO $$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'asset_assistant_ro') THEN
    CREATE ROLE asset_assistant_ro LOGIN PASSWORD 'change_me';
  END IF;
END $$;
GRANT USAGE ON SCHEMA asset_management TO asset_assistant_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA asset_management TO asset_assistant_ro;
ALTER ROLE asset_assistant_ro SET default_transaction_read_only = on;
ALTER ROLE asset_assistant_ro SET statement_timeout = '5s';
