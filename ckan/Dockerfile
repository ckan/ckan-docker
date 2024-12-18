# SPDX-FileCopyrightText: 2006-2024 Open Knowledge Foundation and contributors
# SPDX-FileContributor: PNED G.I.E.
# SPDX-FileContributor: Stichting Health-RI
#
# SPDX-License-Identifier: AGPL-3.0-only

FROM docker.io/ckan/ckan-base:2.10.6

RUN  pip3 install -e git+https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-gdi-userportal.git@v1.3.8#egg=ckanext-gdi-userportal && \
    pip3 install -r ${APP_DIR}/src/ckanext-gdi-userportal/requirements.txt

RUN  pip3 install -e git+https://github.com/ckan/ckanext-dcat.git@v2.1.0#egg=ckanext-dcat && \
    pip3 install -r ${APP_DIR}/src/ckanext-dcat/requirements.txt

RUN pip3 install -e git+https://github.com/ckan/ckanext-harvest.git@v1.6.0#egg=ckanext-harvest && \
    pip3 install -r ${APP_DIR}/src/ckanext-harvest/requirements.txt

RUN pip3 install -e git+https://github.com/CivityNL/ckanext-scheming.git@release-3.0.0-civity#egg=ckanext-scheming[requirements]

RUN  pip3 install -e git+https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-fairdatapoint.git@v1.3.2#egg=ckanext-fairdatapoint && \
    pip3 install -r ${APP_DIR}/src/ckanext-fairdatapoint/requirements.txt

# Create log directories for CKAN harvester
RUN mkdir -p /var/log/ckan/std && chown -R ckan:ckan /var/log/ckan

# Copy custom initialization scripts
COPY docker-entrypoint.d/* /docker-entrypoint.d/

# Config cron job for harvesting
COPY config/supervisord.conf /etc/supervisord.d/ckan.conf
COPY config/crontab ${APP_DIR}/crontab
RUN crontab ${APP_DIR}/crontab

# Apply any patches needed to CKAN core or any of the built extensions (not the
# runtime mounted ones)
COPY patches ${APP_DIR}/patches

RUN for d in $APP_DIR/patches/*; do \
    if [ -d $d ]; then \
    for f in `ls $d/*.patch | sort -g`; do \
    cd $SRC_DIR/`basename "$d"` && echo "$0: Applying patch $f to $SRC_DIR/`basename $d`"; patch -p1 < "$f" ; \
    done ; \
    fi ; \
    done

ENV CKAN__PLUGINS="image_view text_view datatables_view envvars scheming_datasets scheming_organizations dcat dcat_json_interface harvest ckan_harvester dcat_rdf_harvester dcat_json_harvester fairdatapointharvester gdi_userportal activity"

COPY  --chown=ckan:ckan setup/prerun.py ${APP_DIR}

# TODO 
# 1. Remove this command once the issue is fixed
# https://github.com/ckan/ckan-docker-base/issues/41
RUN mkdir -p /var/lib/ckan/storage/uploads/group && \
    mkdir -p /var/lib/ckan/storage/uploads/user && \
    chmod -R u+rwx "/var/lib/ckan"

# https://github.com/ckan/ckan-docker-base/issues/82
# CVE-2024-32002 was found on git and related packages
RUN apk del git git-perl perl-git
