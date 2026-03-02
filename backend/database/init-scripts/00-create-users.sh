#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'socialhub_app') THEN
            CREATE USER socialhub_app WITH PASSWORD '${APP_USER_PASSWORD}';
        END IF;
    END
    \$\$;

    GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO socialhub_app;
    GRANT USAGE ON SCHEMA public TO socialhub_app;
    GRANT CREATE ON SCHEMA public TO socialhub_app;
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO socialhub_app;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO socialhub_app;

    ALTER DEFAULT PRIVILEGES IN SCHEMA public
        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO socialhub_app;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public
        GRANT USAGE, SELECT ON SEQUENCES TO socialhub_app;

    GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO socialhub_app;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public
        GRANT EXECUTE ON FUNCTIONS TO socialhub_app;

    SELECT 'Application user socialhub_app created successfully' AS status;
EOSQL

