#!/bin/bash

#TODO: Correct views.

# Add CKAN Resource views to the CKAN config file
echo "Loading resource views in the CKAN config file"
ckan config-tool $CKAN_INI \
    "ckan.views.default_views = $CKAN__VIEWS__DEFAULT_VIEWS" \
    "ckan.preview.json_formats = $CKAN__PREVIEW__JSON_FORMATS" \
    "ckan.preview.xml_formats = $CKAN__PREVIEW__XML_FORMATS" \
    "ckan.preview.text_formats = $CKAN__PREVIEW__TEXT_FORMATS" \
    "ckan.preview.loadable = $CKAN__PREVIEW__LOADABLE"

# Add CKAN Resource geoviews to the CKAN config file
echo "Loading geoviews in the CKAN config file"
ckan config-tool $CKAN_INI \
    "ckanext.geoview.ol_viewer.formats = $CKANEXT__GEOVIEW__OL_VIEWER__FORMATS" \
    "ckanext.geoview.shp_viewer.srid = $CKANEXT__GEOVIEW__SHP_VIEWER__SRID" \
    "ckanext.geoview.shp_viewer.encoding = $CKANEXT__GEOVIEW__SHP_VIEWER__ENCODING" \
    "ckanext.geoview.geojson.max_file_size = $CKANEXT__GEOVIEW__GEOJSON__MAX_FILE_SIZE"