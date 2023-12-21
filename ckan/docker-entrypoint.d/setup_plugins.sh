#!/bin/bash

# Update the config file with each extension config-options
echo "Setting up plugins"

ckan config-tool $CKAN_INI "ckan.plugins = envvars image_view text_view recline_view scheming_datasets scheming_organizations gdi_userportal dcat harvest ckan_harvester dcat_rdf_harvester dcat_json_harvester dcat_json_interface oidc_pkce fairdatapointharvester"
