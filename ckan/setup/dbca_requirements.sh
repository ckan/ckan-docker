#!/bin/sh

## Must Have ##
# Archiver
pip3 install -e 'git+https://github.com/ckan/ckanext-archiver.git@master#egg=ckanext-archiver'
pip3 install -r ${SRC_DIR}/ckanext-archiver/requirements.txt

# DCAT
pip3 install -e git+https://github.com/ckan/ckanext-dcat.git@v1.5.1#egg=ckanext-dcat
pip3 install -r ${SRC_DIR}/ckanext-dcat/requirements.txt

# Harvester
pip3 install -e 'git+https://github.com/ckan/ckanext-harvest.git@v1.5.6#egg=ckanext-harvest'
pip3 install -r ${SRC_DIR}/ckanext-harvest/requirements.txt

# Hierarchy
pip3 install -e git+https://github.com/ckan/ckanext-hierarchy.git@v1.2.1#egg=ckanext-hierarchy
pip3 install -r ${SRC_DIR}/ckanext-hierarchy/requirements.txt

# Pages
pip3 install -e git+https://github.com/ckan/ckanext-pages.git@v0.5.2#egg=ckanext-pages

# Report
pip3 install -e git+http://github.com/ckan/ckanext-report.git@master#egg=ckanext-report
pip3 install -r ${SRC_DIR}/ckanext-report/requirements.txt

# Showcase
pip3 install -e git+https://github.com/ckan/ckanext-showcase.git@v1.6.1#egg=ckanext-showcase
pip3 install -r ${SRC_DIR}/ckanext-showcase/requirements.txt

# Scheming
pip3 install -e 'git+https://github.com/ckan/ckanext-scheming.git@release-3.0.0#egg=ckanext-scheming'

# Spatial
pip3 install -e git+https://github.com/ckan/ckanext-spatial.git@v2.1.1#egg=ckanext-spatial
pip3 install -r ${SRC_DIR}/ckanext-spatial/requirements.txt

# XLoader
pip3 install -e 'git+https://github.com/ckan/ckanext-xloader.git@1.0.1#egg=ckanext-xloader'
pip3 install -r ${SRC_DIR}/ckanext-xloader/requirements.txt

# 3rd Party #
# DOI
pip3 install -e git+https://github.com/NaturalHistoryMuseum/ckanext-doi@v3.1.9#egg=ckanext-doi