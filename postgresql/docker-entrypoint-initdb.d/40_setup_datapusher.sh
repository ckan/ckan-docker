#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
  CREATE ROLE datapusher LOGIN PASSWORD '$CKAN_DB_PASSWORD';
  GRANT CREATE, CONNECT, TEMPORARY, SUPERUSER ON DATABASE datastore_default TO datapusher;
  GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA public TO datapusher;
EOSQL

postgres createuser -S -D -R -P datapusher_jobs
postgres createdb -O datapusher_jobs datapusher_jobs -E utf-8
