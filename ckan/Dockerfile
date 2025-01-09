FROM ckan/ckan-base:2.11

USER root

# Add extensions
RUN pip3 install -e 'git+https://github.com/ckan/ckanext-spatial.git#egg=ckanext-spatial' && \ 
    pip3 install -r ${APP_DIR}/src/ckanext-spatial/requirements.txt && \
    pip3 install -e 'git+https://github.com/ckan/ckanext-geoview.git#egg=ckanext-geoview' && \
    pip3 install -e 'git+https://github.com/ckan/ckanext-pdfview#egg=ckanext-pdfview' && \
    pip3 install -e 'git+https://github.com/ckan/ckanext-scheming.git@master#egg=ckanext-scheming'
    
# Copy custom initialization scripts
COPY --chown=ckan-sys:ckan-sys docker-entrypoint.d/* /docker-entrypoint.d/

COPY --chown=ckan-sys:ckan-sys patches ${APP_DIR}/patches

COPY ./ckan_dataset_schema.yaml ${APP_DIR}/src/ckanext-scheming/ckanext/scheming

USER ckan

RUN for d in $APP_DIR/patches/*; do \
        if [ -d $d ]; then \
            for f in `ls $d/*.patch | sort -g`; do \
                cd $SRC_DIR/`basename "$d"` && echo "$0: Applying patch $f to $SRC_DIR/`basename $d`"; patch -p1 < "$f" ; \
            done ; \
        fi ; \
    done
