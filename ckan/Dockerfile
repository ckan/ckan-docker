FROM ckan/ckan-base:2.10.1

# Install any extensions needed by your CKAN instance
# See Dockerfile.dev for more details and examples


RUN  pip3 install -e git+https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-gdi-userportal.git@main#egg=ckanext-gdi-userportal && \
     pip3 install -r ${APP_DIR}/src/ckanext-gdi-userportal/requirements.txt

RUN  pip3 install -e git+https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-dcat.git@master#egg=ckanext-dcat && \
     pip3 install -r ${APP_DIR}/src/ckanext-dcat/requirements.txt

RUN  pip3 install -e git+https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-harvest.git@v1.5.6#egg=ckanext-harvest && \
     pip3 install -r ${APP_DIR}/src/ckanext-harvest/requirements.txt

RUN  pip3 install -e git+https://github.com/GenomicDataInfrastructure/gdi-userportal-ckanext-scheming.git@master#egg=ckanext-scheming

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
