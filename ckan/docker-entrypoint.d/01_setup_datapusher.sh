#!/bin/bash

if [[ $CKAN__PLUGINS == *"datapusher"* ]]; then
   # Datapusher settings have been configured in the .env file
   # Set API token if necessary
   if [ -z "$CKAN__DATAPUSHER__API_TOKEN" ] ; then
      echo "Set up ckan.datapusher.api_token in the CKAN config file"
      if ! datapusher_token="$(
         set -o pipefail
         ckan -c "$CKAN_INI" user token add \
            "${CKAN_SYSADMIN_NAME:-ckan_admin}" datapusher |
            tail -n 1 |
            tr -d '\t'
      )"; then
         echo "Could not create the DataPusher API token" >&2
         exit 1
      fi
      if [ -z "$datapusher_token" ]; then
         echo "Could not create the DataPusher API token" >&2
         exit 1
      fi
      ckan config-tool "$CKAN_INI" \
         "ckan.datapusher.api_token=$datapusher_token"
   fi
else
   echo "Not configuring DataPusher"
fi
