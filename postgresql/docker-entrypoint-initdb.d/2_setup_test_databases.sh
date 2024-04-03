#!/bin/bash

# SPDX-FileCopyrightText: 2006-2024 Open Knowledge Foundation and contributors
# SPDX-FileContributor: PNED G.I.E.
#
# SPDX-License-Identifier: AGPL-3.0-only

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE ckan_test OWNER "$CKAN_DB_USER" ENCODING 'utf-8';
    CREATE DATABASE datastore_test OWNER "$CKAN_DB_USER" ENCODING 'utf-8';
EOSQL
