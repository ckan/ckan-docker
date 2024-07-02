# SPDX-FileCopyrightText: 2006-2024 Open Knowledge Foundation and contributors
# SPDX-FileContributor: PNED G.I.E.
# SPDX-FileContributor: Stichting Health-RI
#
# SPDX-License-Identifier: AGPL-3.0-only

FROM ckan/ckan-base:2.10.4

# Install any extensions needed by your CKAN instance
# See Dockerfile.dev for more details and examples

RUN  pip3 install -e git+https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-gdi-userportal.git@v1.2.3#egg=ckanext-gdi-userportal && \
    pip3 install -r ${APP_DIR}/src/ckanext-gdi-userportal/requirements.txt

RUN  pip3 install -e git+https://github.com/ckan/ckanext-dcat.git@v1.5.1#egg=ckanext-dcat && \
    pip3 install -r ${APP_DIR}/src/ckanext-dcat/requirements.txt

RUN pip3 install -e git+https://github.com/ckan/ckanext-harvest.git@v1.5.6#egg=ckanext-harvest && \
    pip3 install -r ${APP_DIR}/src/ckanext-harvest/requirements.txt

RUN git clone https://github.com/CivityNL/ckanext-scheming.git ${APP_DIR}/src/ckanext-scheming && \
    cd "${APP_DIR}/src/ckanext-scheming" && \
    git checkout release-3.0.0-civity && \
    pip3 install -e .

RUN  pip3 install -e git+https://github.com/DataShades/ckanext-oidc-pkce.git@v0.3.1#egg=ckanext-oidc-pkce && \
    pip3 install -r ${APP_DIR}/src/ckanext-oidc-pkce/requirements.txt

RUN  pip3 install -e git+https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-fairdatapoint.git@v1.2.2#egg=ckanext-fairdatapoint && \
    pip3 install -r ${APP_DIR}/src/ckanext-fairdatapoint/requirements.txt

# Install Supervisor and cron
RUN apk update \
    && apk add --no-cache supervisor cronie \
    && rm -rf /var/cache/apk/*

# Create log directories for CKAN harvester
RUN mkdir -p /var/log/ckan/std && chown -R ckan:ckan /var/log/ckan

# Copy custom initialization scripts
COPY docker-entrypoint.d/* /docker-entrypoint.d/
COPY config/ckan_harvesting.conf /etc/supervisord.d/ckan_harvesting.conf

# Copy crontab file to the cron.d directory
ADD config/crontab-harvester /etc/cron.d/crontab-harvester

# Give execution rights on the cron job
RUN chmod 644 /etc/cron.d/crontab-harvester

# Apply cron job
RUN crontab -u ckan /etc/cron.d/crontab-harvester

# Create log file for cron
RUN touch /var/log/cron.log && chown ckan:ckan /var/log/cron.log

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

ENV CKAN__PLUGINS="envvars image_view text_view recline_view scheming_datasets scheming_organizations dcat dcat_json_interface harvest ckan_harvester dcat_rdf_harvester dcat_json_harvester fairdatapointharvester oidc_pkce gdi_userportal activity"

COPY  --chown=ckan:ckan setup/prerun.py ${APP_DIR}

# TODO 
# 1. Remove this command once the issue is fixed
# https://github.com/ckan/ckan-docker-base/issues/41
RUN mkdir /var/lib/ckan/storage
RUN mkdir /var/lib/ckan/storage/uploads
RUN mkdir /var/lib/ckan/storage/uploads/group
RUN chmod -R u+rwx "/var/lib/ckan"
