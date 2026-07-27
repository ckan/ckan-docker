
# --- Build the legend JS source code and ship it with CKAN ---
FROM node:26-alpine AS mapboxgl-legend-builder

WORKDIR /tmp/mapbox-gl-legend
RUN apk add git && \
  git clone https://github.com/natcap/mapbox-gl-legend.git . && \
  git checkout 924289931c9c502055900fc16d767313886ba9b0 && \
  npm install && \
  npm run build

# --- Build CKAN but use the modified JS source for the legend ---
FROM ckan/ckan-base:2.11.2

ARG GITHUB_USER
ARG GITHUB_REPO
ARG GITHUB_BRANCH

USER root

# Set up environment variables
ENV APP_DIR=/opt/ckan-catalog/data.naturalcapitalproject.stanford.edu
ENV TZ=UTC
RUN echo ${TZ} > /etc/timezone

# Make sure both files are not exactly the same
RUN if ! [ /usr/share/zoneinfo/${TZ} -ef /etc/localtime ]; then \
        cp /usr/share/zoneinfo/${TZ} /etc/localtime ;\
    fi ;

# Install package dependencies for ckanext-spatial
ENV PROJ_DIR=/usr
ENV PROJ_LIBDIR=/usr/lib
ENV PROJ_INCDIR=/usr/include
# Using latest commit from master branch to avoid having to compile PROJ from source
ENV CKANEXT_SPATIAL_GIT_REVISION=v2.2.0
RUN apt-get update && apt-get install -y libgeos-dev libgeos3.11.1 libproj-dev proj-bin python3-shapely
RUN pip3 install -e git+https://github.com/ckan/ckanext-spatial.git@$CKANEXT_SPATIAL_GIT_REVISION#egg=ckanext-spatial && \
    pip3 install -r https://raw.githubusercontent.com/ckan/ckanext-spatial/refs/tags/$CKANEXT_SPATIAL_GIT_REVISION/requirements.txt
RUN pip3 install -e git+https://github.com/ckan/ckanext-scheming.git@release-3.1.0#egg=ckanext-scheming
RUN pip3 install "numpy<2"

ENV CKANEXT_GOOGLEANALYTICS_GIT_REV=6484a04fdc5eca1cdee9e3ee3b4e881678d1538d
RUN pip3 install -e git+https://github.com/ckan/ckanext-googleanalytics.git@$CKANEXT_GOOGLEANALYTICS_GIT_REV#egg=ckanext-googleanalytics && \
    pip3 install -r https://raw.githubusercontent.com/ckan/ckanext-googleanalytics/$CKANEXT_GOOGLEANALYTICS_GIT_REV/requirements.txt && \
    python3 -m pip install oauth2client

ENV CKANEXT_ORFACET_GIT_REV=7a01391186761ff112a76bc7e62dd487330a2371
RUN pip3 install -e git+https://github.com/DataShades/ckanext-or_facet.git@$CKANEXT_ORFACET_GIT_REV#egg=ckanext-or_facet

RUN pip3 install -e git+https://github.com/datopian/ckanext-sitemap.git#egg=ckanext-sitemap

# NOTE: requires that the build context includes ./src/
COPY ./src/ckanext-natcap /srv/app/src/ckanext-natcap
RUN pip3 install -r /srv/app/src/ckanext-natcap/requirements.txt && \
    pip3 install -e /srv/app/src/ckanext-natcap

COPY ./src/ckanext-mappreview /srv/app/src/ckanext-mappreview
RUN pip3 install -r /srv/app/src/ckanext-mappreview/requirements.txt && \
    pip3 install -e /srv/app/src/ckanext-mappreview

COPY ./src/ckanext-zipexpand /srv/app/src/ckanext-zipexpand
RUN pip3 install -r /srv/app/src/ckanext-zipexpand/requirements.txt && \
    pip3 install -e /srv/app/src/ckanext-zipexpand

# Install any extensions needed by your CKAN instance
# See Dockerfile.dev for more details and examples

# $CKAN_INI is set by the base ckan image; location: /srv/app/ckan.ini
# Change the API Token header; the default `Authorization` interferes
# with Basic Auth, which is used by nginx on the data-staging site
RUN ckan config-tool $CKAN_INI --section app:main "apitoken_header_name=X-CKAN-API-TOKEN"
RUN ckan config-tool $CKAN_INI --section app:main 'scheming.presets=ckanext.scheming:presets.json'
RUN ckan config-tool $CKAN_INI --section app:main 'scheming.dataset_schemas=ckanext.natcap:schemas/natcap_dataset_schema.yml ckanext.natcap:schemas/natcap_collection_schema.yml'

# Copy custom initialization scripts
COPY ./ckan/docker-entrypoint.d/* /docker-entrypoint.d/

COPY --from=mapboxgl-legend-builder /tmp/mapbox-gl-legend/dist/cdn/mapbox-gl-legend.js /srv/app/src/ckanext-mappreview/ckanext/mappreview/assets/js/vendor/mapbox-gl-legend.js

# Apply any patches needed to CKAN core or any of the built extensions (not the
# runtime mounted ones)
COPY ./ckan/patches ${APP_DIR}/patches

RUN for d in $APP_DIR/patches/*; do \
        if [ -d $d ]; then \
            for f in `ls $d/*.patch | sort -g`; do \
                cd $SRC_DIR/`basename "$d"` && echo "$0: Applying patch $f to $SRC_DIR/`basename $d`"; patch -p1 < "$f" ; \
            done ; \
        fi ; \
    done
