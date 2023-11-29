#!/bin/bash

if [[ $CKAN__PLUGINS == *"xloader"* ]]; then
    # Add ckan.xloader.api_token to the CKAN config file (updated with corrected value later)
    echo "Setting a temporary value for ckanext.xloader.api_token"
    ckan config-tool $CKAN_INI "ckanext.xloader.api_token=$(ckan -c $CKAN_INI user token add $CKAN_SYSADMIN_NAME xloader | tail -n 1 | tr -d '\t')"
fi

## Examples of how to initialise DB for the extensions
# if [[ $CKAN__PLUGINS == *"archiver"* ]]; then
#     ckan -c $CKAN_INI archiver init
# fi

# if [[ $CKAN__PLUGINS == *"report"* ]]; then
#     ckan -c $CKAN_INI report initdb
# fi

# if [[ $CKAN__PLUGINS == *"harvest"* ]]; then
#     ckan -c $CKAN_INI db upgrade -p harvest
# fi

if [[ $CKAN__PLUGINS == *"pages"* ]]; then
    ckan -c $CKAN_INI pages initdb
fi