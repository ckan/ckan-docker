# SPDX-FileCopyrightText: 2006-2023 Open Knowledge Foundation and contributors
#
# SPDX-License-Identifier: AGPL-3.0-only

FROM postgres:12-alpine

# Include extra setup scripts (eg datastore)
COPY --chown=postgres:postgres docker-entrypoint-initdb.d /docker-entrypoint-initdb.d
