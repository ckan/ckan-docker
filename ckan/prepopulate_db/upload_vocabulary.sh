#!/bin/bash

set -e

psql postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:5432/$CKAN_DB -c "\copy public.term_translation FROM  '/prepopulate_db/common_vocabulary_tags.csv' WITH (DELIMITER ',', FORMAT CSV, HEADER TRUE);"
