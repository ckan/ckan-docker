#!/bin/bash

# Add ckanext-dcat settings to the CKAN config file
echo "Loading ckanext-dcat settings in the CKAN config file"
ckan config-tool $CKAN_INI \
    "ckanext.dcat.base_uri = $CKANEXT__DCAT__BASE_URI" \
    "ckanext.dcat.rdf.profiles = $CKANEXT__DCAT__RDF_PROFILES"