#!/bin/sh

# SPDX-FileCopyrightText: 2024 PNED G.I.E.
#
# SPDX-License-Identifier: AGPL-3.0-only


echo "[DEFAULT] Setting up debug"
#ckan config-tool $CKAN_INI  -s DEFAULT "debug = $CKAN___DEBUG"

echo "[logger_ckanext] Setting up level"
#ckan config-tool $CKAN_INI  -s logger_ckanext "level = $CKAN___LOGGER_CKANEXT__LEVEL"
