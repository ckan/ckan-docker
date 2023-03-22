#!/bin/bash

# Add ckanext.xloader.api_token to the CKAN config file
echo "Loading ckanext-xloader settings in the CKAN config file"
ckan config-tool $CKAN_INI \
    "ckanext.xloader.api_token = xxx" \
    "ckanext.xloader.jobs_db.uri = $CKANEXT__XLOADER__JOBS__DB_URI"

# Create ckanext-xloader API_TOKEN
echo "Set up ckanext.xloader.api_token in the CKAN config file"
ckan config-tool $CKAN_INI "ckanext.xloader.api_token = $(ckan -c $CKAN_INI user token add ckan_admin xloader | tail -n 1 | tr -d '\t')"

# Setup worker
ckan config-tool $CKAN_INI jobs worker