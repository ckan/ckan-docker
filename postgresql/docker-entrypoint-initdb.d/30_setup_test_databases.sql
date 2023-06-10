#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE ckan_test OWNER "$CKAN_DB_USER" ENCODING 'utf-8';
    CREATE DATABASE datastore_test OWNER "$CKAN_DB_USER" ENCODING 'utf-8';
EOSQL
