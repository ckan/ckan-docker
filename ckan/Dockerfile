FROM ckan/ckan-base:2.10.3

# Install any extensions needed by your CKAN instance
# See Dockerfile.dev for more details and examples


RUN  pip3 install -e git+https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-gdi-userportal.git@main#egg=ckanext-gdi-userportal && \
     pip3 install -r ${APP_DIR}/src/ckanext-gdi-userportal/requirements.txt

RUN  pip3 install -e git+https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-dcat.git@user-portal-v1.5.1#egg=ckanext-dcat && \
     pip3 install -r ${APP_DIR}/src/ckanext-dcat/requirements.txt

RUN  pip3 install -e git+https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-harvest.git@user-portal-v1.5.6#egg=ckanext-harvest && \
     pip3 install -r ${APP_DIR}/src/ckanext-harvest/requirements.txt

RUN  pip3 install -e git+https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-scheming.git@user-portal-v3.0.0#egg=ckanext-scheming

RUN  pip3 install -e git+https://github.com/DataShades/ckanext-oidc-pkce.git@v0.3.1#egg=ckanext-oidc-pkce && \
     pip3 install -r ${APP_DIR}/src/ckanext-oidc-pkce/requirements.txt

RUN  pip3 install -e git+https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-fairdatapoint.git@main#egg=ckanext-fairdatapoint && \
     pip3 install -r ${APP_DIR}/src/ckanext-fairdatapoint/requirements.txt


# Copy custom initialization scripts
COPY docker-entrypoint.d/* /docker-entrypoint.d/

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

ENV CKAN__PLUGINS="envvars image_view text_view recline_view scheming_datasets scheming_organizations gdi_userportal dcat harvest ckan_harvester dcat_rdf_harvester dcat_json_harvester dcat_json_interface oidc_pkce fairdatapointharvester"
ENV CKAN_SOLR_URL = http://test:8983/solr/ckan
ENV CKAN_SQLALCHEMY_URL=postgresql://ckandbuser:ckandbpassword@test/ckandb
