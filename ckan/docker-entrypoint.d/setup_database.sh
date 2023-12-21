#!/bin/bash

# Update the config file with each extension config-options
echo "Setting up database"

ckan config-tool $CKAN_INI "sqlalchemy.url = $CKAN_SQLALCHEMY_URL"
