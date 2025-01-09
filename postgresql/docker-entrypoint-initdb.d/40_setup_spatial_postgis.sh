#!/bin/bash
# Initialize PostGIS extension in PostgreSQL

echo "Initializing PostGIS extension in PostgreSQL..."

# Connect to PostgreSQL and enable PostGIS extension
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS postgis;
    CREATE EXTENSION IF NOT EXISTS postgis_topology;
EOSQL

