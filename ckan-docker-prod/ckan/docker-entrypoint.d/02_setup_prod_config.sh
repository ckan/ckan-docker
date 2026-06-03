#!/bin/bash
set -e

echo "Applying production CKAN configuration"

ckan config-tool "$CKAN_INI" "ckan.site_url=${CKAN__SITE_URL:-$CKAN_SITE_URL}"
ckan config-tool "$CKAN_INI" "ckan.site_title=${CKAN__SITE_TITLE:-DataHub Open Data}"
ckan config-tool "$CKAN_INI" "ckan.site_description=${CKAN__SITE_DESCRIPTION:-Katalog otvorenych dat}"
ckan config-tool "$CKAN_INI" "ckan.locale_default=${CKAN__LOCALE_DEFAULT:-sk}"
ckan config-tool "$CKAN_INI" "ckan.uploads_enabled=${CKAN__UPLOADS_ENABLED:-true}"
ckan config-tool "$CKAN_INI" "ckan.storage_path=${CKAN__STORAGE_PATH:-$CKAN_STORAGE_PATH}"
ckan config-tool "$CKAN_INI" "ckan.max_resource_size=${CKAN__MAX_RESOURCE_SIZE:-100}"
ckan config-tool "$CKAN_INI" "ckan.max_image_size=${CKAN__MAX_IMAGE_SIZE:-10}"

ckan config-tool "$CKAN_INI" "ckan.datapusher.url=${CKAN__DATAPUSHER__URL:-$CKAN_DATAPUSHER_URL}"
ckan config-tool "$CKAN_INI" "ckan.datapusher.callback_url_base=${CKAN__DATAPUSHER__CALLBACK_URL_BASE:-http://ckan:5000}"
ckan config-tool "$CKAN_INI" "ckan.datapusher.api_token=${CKAN__DATAPUSHER__API_TOKEN}"

ckan config-tool "$CKAN_INI" "scheming.dataset_schemas=${CKAN___SCHEMING__DATASET_SCHEMAS:-ckanext.idsk:schemas/dcat_ap_sk.yaml}"
ckan config-tool "$CKAN_INI" "scheming.presets=${CKAN___SCHEMING__PRESETS:-ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml}"
ckan config-tool "$CKAN_INI" "ckanext.dcat.rdf.profiles=${CKANEXT__DCAT__RDF__PROFILES:-euro_dcat_ap_2 euro_dcat_ap_scheming datahub_dcat_ap_sk}"
