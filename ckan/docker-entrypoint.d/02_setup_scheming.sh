#!/bin/bash

ckan config-tool $CKAN_INI "scheming.dataset_schemas = ckanext.scheming:ckan_dataset_schema.yaml"
ckan config-tool $CKAN_INI "scheming.presets = ckanext.scheming:presets.json"
