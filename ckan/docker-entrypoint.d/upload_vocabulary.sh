#!/bin/bash

# SPDX-FileCopyrightText: 2006-2024 Open Knowledge Foundation and contributors
# SPDX-FileContributor: Stichting Health-RI
# SPDX-License-Identifier: AGPL-3.0-only

set -e

psql postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:5432/$CKAN_DB <<-EOSQL

  SELECT
      EXISTS(SELECT 1 FROM public.term_translation) as table_not_empty
  \gset
  \if :table_not_empty
      \echo 'term_translation table is not empty, updating'
      create table public.temp (term text, term_translation text, lang_code text);
      \copy public.temp FROM  '/docker-entrypoint.d/common_vocabulary_tags.csv' WITH (DELIMITER ',', FORMAT CSV, HEADER TRUE);
      delete from public.term_translation using public.temp where public.term_translation.term = public.temp.term and public.term_translation.term_translation = public.temp.term_translation and public.term_translation.lang_code = public.temp.lang_code;
      insert into public.term_translation (term, term_translation, lang_code) select term, term_translation, lang_code from public.temp;
      drop table public.temp;
  \else
      \copy public.term_translation FROM  '/docker-entrypoint.d/common_vocabulary_tags.csv' WITH (DELIMITER ',', FORMAT CSV, HEADER TRUE);
      \echo 'term_translation initialized with common_vocabulary_tags.csv'
  \endif

EOSQL
