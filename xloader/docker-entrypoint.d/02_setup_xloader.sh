#!/bin/bash

if [[ $CKAN__PLUGINS == *"xloader"* ]]; then
   # Datapusher settings have been configured in the .env file
   # Set API token if necessary
   if [ -z "$CKAN__XLOADER__API_TOKEN" ] ; then
      echo "Set up ckanext.xloader.api_token in the CKAN config file"
      ckan config-tool $CKAN_INI "ckanext.xloader.api_token=$(ckan -c $CKAN_INI user token add ckan_admin xloader | tail -n 1 | tr -d '\t')"
   fi
else
   echo "Not configuring xloader"
fi
