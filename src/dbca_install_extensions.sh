
#!/bin/sh

### Extensions that need upgrading to be compatiable with CKAN 2.10 ###
# Uncomment the following lines to install these extension you are working on to upgrade to CKAN 2.10

cd src/

## Must Have ##
# QA
# git clone https://github.com/dbca-wa/ckanext-qa.git
# These extensions will be installed by default, but we don't want them
# sed -i".$(date +%Y%m%d_%H%M%S).bak" -e '/ckanext-report/d' -e '/ckanext-archiver/d' ckanext-qa/dev-requirements.txt
# Office Docs
# git clone https://github.com/dbca-wa/ckanext-officedocs

## Should have ##
# Geopusher
# git clone https://github.com/dbca-wa/ckanext-geopusher.git

## Could have ##
# Cesium Preview
# git clone https://github.com/dbca-wa/ckanext-cesiumpreview.git
# Featured Views
# git clone https://github.com/dbca-wa/ckanext-featuredviews

echo "Ready to build project: ahoy build"