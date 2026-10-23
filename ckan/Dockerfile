FROM ckan/ckan-base:2.11

# The base image switches to the unprivileged `ckan` user; pip needs root to
# write to site-packages. Dropped back to `ckan` further down.
USER root

# Install any extensions needed by your CKAN instance
# See Dockerfile.dev for more details and examples

### Geoview - map previews for GeoJSON (and WMS/KML/SHP) resources ###
# Editable install into SRC_DIR, mirroring Dockerfile.dev - a plain wheel install
# lands outside CKAN's `ckanext` namespace package and fails to import.
RUN pip3 install -e 'git+https://github.com/ckan/ckanext-geoview.git@v0.3.1#egg=ckanext-geoview'

### Sofia - portal theme, installed from GitHub ###
RUN pip install --no-cache-dir -e \
    git+https://github.com/sofia-municipality/ckanext-sofia.git@main#egg=ckanext-sofia

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
