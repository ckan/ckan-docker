FROM ckan/ckan-base:2.11

# Install any extensions needed by your CKAN instance
# See Dockerfile.dev for more details and examples

ARG CKANEXT_DCAT_VER
ENV CKANEXT_DCAT_VER=${CKANEXT_DCAT_VER:-v2.4.2}

USER root

RUN  pip3 install -e git+https://github.com/ckan/ckanext-dcat.git@$CKANEXT_DCAT_VER#egg=ckanext-dcat && \
    pip3 install -r https://raw.githubusercontent.com/ckan/ckanext-dcat/$CKANEXT_DCAT_VER/requirements.txt

RUN pip install -e "git+https://github.com/ckan/ckanext-scheming.git#egg=ckanext-scheming"

# Copy custom initialization scripts
COPY --chown=ckan-sys:ckan-sys docker-entrypoint.d/* /docker-entrypoint.d/

# Apply any patches needed to CKAN core or any of the built extensions (not the
# runtime mounted ones)
COPY --chown=ckan-sys:ckan-sys patches ${APP_DIR}/patches

USER ckan

RUN for d in $APP_DIR/patches/*; do \
        if [ -d $d ]; then \
            for f in `ls $d/*.patch | sort -g`; do \
                cd $SRC_DIR/`basename "$d"` && echo "$0: Applying patch $f to $SRC_DIR/`basename $d`"; patch -p1 < "$f" ; \
            done ; \
        fi ; \
    done
