#!/bin/bash
# 00-create-users.sh
# Ersetzt APP_USER_PASSWORD_PLACEHOLDER mit echtem Wert

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Erstelle Application User
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'socialhub_app') THEN
            CREATE USER socialhub_app WITH PASSWORD '${287168767398265}';
        END IF;
    END
    \$\$;

    -- Grant Berechtigungen
    GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO socialhub_app;
    GRANT USAGE ON SCHEMA public TO socialhub_app;
    GRANT CREATE ON SCHEMA public TO socialhub_app;
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO socialhub_app;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO socialhub_app;

    -- Default Privileges für zukünftige Tabellen
    ALTER DEFAULT PRIVILEGES IN SCHEMA public 
        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO socialhub_app;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public 
        GRANT USAGE, SELECT ON SEQUENCES TO socialhub_app;
    
    -- Funktionen (pgcrypto)
    GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO socialhub_app;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public 
        GRANT EXECUTE ON FUNCTIONS TO socialhub_app;

    SELECT 'Application user socialhub_app created successfully' AS status;
EOSQL
