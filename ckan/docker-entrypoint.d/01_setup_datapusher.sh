#!/bin/bash

if [[ "$CKAN__PLUGINS" == *"datapusher"* ]]; then
   echo "[INFO] DataPusher plugin detected. Preparing token..."

   # Wait until CKAN is responsive
   echo "[INFO] Waiting for CKAN sysadmin user '$CKAN_SYSADMIN_NAME'..."
   for i in {1..10}; do
      if ckan -c "$CKAN_INI" user show "$CKAN_SYSADMIN_NAME" &> /dev/null; then
         echo "[INFO] User $CKAN_SYSADMIN_NAME found."
         break
      fi
      echo "[WAIT] Waiting... ($i/10)"
      sleep 3
   done

   # Create sysadmin user if not found
   if ! ckan -c "$CKAN_INI" user show "$CKAN_SYSADMIN_NAME" &> /dev/null; then
      echo "[INFO] Creating user $CKAN_SYSADMIN_NAME..."
      ckan -c "$CKAN_INI" sysadmin add "$CKAN_SYSADMIN_NAME" --force \
           --email "${CKAN_SYSADMIN_EMAIL:-admin@example.com}" \
           --password "${CKAN_SYSADMIN_PASSWORD:-pass123}"
   fi

   # Set the token
   if [ -z "$CKAN__DATAPUSHER__API_TOKEN" ]; then
      echo "[INFO] Generating DataPusher API token..."
      token=$(ckan -c "$CKAN_INI" user token add "$CKAN_SYSADMIN_NAME" datapusher | tail -n 1 | tr -d '\r')
      ckan config-tool "$CKAN_INI" "ckan.datapusher.api_token=${token}"
      echo "[OK] Token applied."
   else
      echo "[INFO] CKAN__DATAPUSHER__API_TOKEN already set. Skipping token generation."
   fi
else
   echo "[INFO] DataPusher plugin not enabled. Skipping setup."
fi
