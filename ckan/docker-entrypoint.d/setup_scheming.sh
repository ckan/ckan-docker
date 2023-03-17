#!/bin/bash

# Update ckanext-scheming settings defined in the env var
echo "Loading ckanext-scheming settings into ckan.ini"
ckan config-tool $CKAN_INI \
    "scheming.dataset_schemas=$SCHEMA_CKANEXT_SCHEMING_DATASET_SCHEMA" \
    "scheming.group_schemas=$SCHEMA_CKANEXT_SCHEMING_GROUP_SCHEMAS" \
    "scheming.organization_schemas=$SCHEMA_CKANEXT_SCHEMING_ORGANIZATION_SCHEMAS" \
    "scheming.presets=$SCHEMA_CKANEXT_SCHEMING_PRESETS"