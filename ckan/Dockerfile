FROM alpine:3.13

# Internals, you probably don't need to change these
ENV APP_DIR=/srv/app
ENV SRC_DIR=/srv/app/src
ENV CKAN_INI=${APP_DIR}/ckan.ini
ENV PIP_SRC=${SRC_DIR}
ENV CKAN_STORAGE_PATH=/var/lib/ckan
ENV GIT_URL=https://github.com/ckan/ckan.git
ENV TZ=UTC
RUN echo ${TZ} > /etc/timezone
# CKAN version to build
ENV GIT_BRANCH=ckan-2.9.8
# Customize these on the .env file if needed
ENV CKAN_SITE_URL=http://localhost:5000
ENV CKAN__PLUGINS image_view text_view recline_view datastore datapusher envvars

# UWSGI options
ENV UWSGI_HARAKIRI=50

WORKDIR ${APP_DIR}

# Install necessary packages to run CKAN
RUN apk add --no-cache tzdata \
        git \
        gettext \
        postgresql-client \
        python3 \
        libxml2 \
        libxslt \
        musl-dev \
        uwsgi \
        uwsgi-http \
        uwsgi-corerouter \
        uwsgi-python \
        py3-gevent \
        uwsgi-gevent \
        libmagic \
        curl \
        patch \
        sudo && \
    # Packages to build CKAN requirements and plugins
    apk add --no-cache --virtual .build-deps \
        postgresql-dev \
        gcc \
        make \
        g++ \
        autoconf \
        automake \
    	libtool \
        python3-dev \
        libxml2-dev \
        libxslt-dev \
        linux-headers \
        openssl-dev \
        libffi-dev \
        cargo \
    # Set up PROJ
        geos-dev \ 
        proj \
        proj-util \
        proj-dev && \
    # Create SRC_DIR
    mkdir -p ${SRC_DIR} && \
    # Install pip, supervisord and uwsgi
    curl -o ${SRC_DIR}/get-pip.py https://bootstrap.pypa.io/get-pip.py && \
    python3 ${SRC_DIR}/get-pip.py && \
    pip3 install supervisor && \
    mkdir /etc/supervisord.d && \
    #pip wheel --wheel-dir=/wheels uwsgi gevent && \
    rm -rf ${SRC_DIR}/get-pip.py

COPY setup/supervisord.conf /etc

# Install CKAN
RUN pip3 install -e git+${GIT_URL}@${GIT_BRANCH}#egg=ckan && \
    cd ${SRC_DIR}/ckan && \
    cp who.ini ${APP_DIR} && \
    pip3 install -r requirement-setuptools.txt && \
    pip3 install --no-binary markdown -r requirements.txt && \
    # Install CKAN envvars to support loading config from environment variables
    pip3 install -e git+https://github.com/okfn/ckanext-envvars.git#egg=ckanext-envvars && \
    # Create and update CKAN config
    ckan generate config ${CKAN_INI} && \
    ckan config-tool ${CKAN_INI} "beaker.session.secret = " && \
    ckan config-tool ${CKAN_INI} "ckan.plugins = ${CKAN__PLUGINS}"

# Create a local user and group to run the app
RUN addgroup -g 92 -S ckan && \
    adduser -u 92 -h /srv/app -s /bin/bash -D -G ckan ckan

# Create local storage folder
RUN mkdir -p ${CKAN_STORAGE_PATH} && \
    chown -R ckan:ckan ${CKAN_STORAGE_PATH}

COPY setup/prerun.py ${APP_DIR}
COPY setup/start_ckan.sh ${APP_DIR}
ADD https://raw.githubusercontent.com/ckan/ckan/${GIT_BRANCH}/wsgi.py ${APP_DIR}

# Create entrypoint directory for children image scripts
ONBUILD RUN mkdir /docker-entrypoint.d

RUN chown ckan -R /srv/app

RUN addgroup sudo && \
    adduser ckan sudo

EXPOSE 5000

HEALTHCHECK --interval=60s --timeout=5s --retries=5 CMD curl --fail http://localhost:5000/api/3/action/status_show || exit 1

# Make sure both files are not exactly the same
RUN if ! [ /usr/share/zoneinfo/${TZ} -ef /etc/localtime ]; then \
    cp /usr/share/zoneinfo/${TZ} /etc/localtime ;\
    fi ;

# Extensions
### XLoader - v0.12.2 ###
RUN pip3 install -e 'git+https://github.com/ckan/ckanext-xloader.git@0.12.2#egg=ckanext-xloader' && \ 
    pip3 install -r ${APP_DIR}/src/ckanext-xloader/requirements.txt && \
    pip3 install -U requests[security]

### Harvester - v1.5.1 ###
RUN echo "ckan/ckanext-harvest" && \
    pip3 install -e 'git+https://github.com/ckan/ckanext-harvest.git@v1.5.1#egg=ckanext-harvest' && \
    pip3 install -r ${APP_DIR}/src/ckanext-harvest/pip-requirements.txt

### Geoview - v0.0.20 ###
RUN echo "ckan/ckanext-geoview" && \
    pip3 install -e 'git+https://github.com/ckan/ckanext-geoview.git@v0.0.20#egg=ckanext-geoview' 

### Spatial - v2.0.0 ### 
RUN echo "ckan/ckanext-spatial" && \
    pip3 install -e 'git+https://github.com/ckan/ckanext-spatial.git@v2.0.0#egg=ckanext-spatial' && \
    pip3 install -r https://raw.githubusercontent.com/ckan/ckanext-spatial/bae9290395b252ee8e40056256fa694569d1d78b/requirements.txt

### DCAT - master (GeoDCAT-AP extended version) ###
RUN echo "mjanez/ckanext-dcat (GeoDCAT-AP extended version)" && \
    pip3 install -e git+https://github.com/mjanez/ckanext-dcat.git#egg=ckanext-dcat && \
    pip3 install -r https://raw.githubusercontent.com/mjanez/ckanext-dcat/master/requirements.txt

### Scheming - master (GeoDCAT-AP extended version) ###
RUN echo "mjanez/ckanext-scheming (GeoDCAT-AP extended version)" && \
    pip3 install -e git+https://github.com/mjanez/ckanext-scheming.git#egg=ckanext-scheming 

### Resource dictionary (Fix version) - main ###
RUN echo "mjanez/ckanext-resourcedictionary" && \
    pip3 install -e 'git+https://github.com/mjanez/ckanext-resourcedictionary.git#egg=ckanext-resourcedictionary'

### Pages - v0.5.1 ###
RUN echo "ckan/ckanext-pages" && \
    pip3 install -e git+https://github.com/ckan/ckanext-pages.git@v0.5.1#egg=ckanext-pages

### PDFView - v0.0.8 ###
RUN echo "ckan/ckanext-pdfview" && \
    pip3 install -e git+https://github.com/ckan/ckanext-pdfview.git@0.0.8#egg=ckanext-pdfview

# Used to configure the container environment by setting environment variables, creating users, running initialization scripts, .etc
COPY docker-entrypoint.d/* /docker-entrypoint.d/

# Apply any patches needed to CKAN core
COPY patches ${APP_DIR}/patches

RUN for d in $APP_DIR/patches/*; do \
    if [ -d $d ]; then \
    for f in `ls $d/*.patch | sort -g`; do \
    cd $SRC_DIR/`basename "$d"` && echo "$0: Applying patch $f to $SRC_DIR/`basename $d`"; patch -p1 < "$f" ; \
    done ; \
    fi ; \
    done

CMD ["/srv/app/start_ckan.sh"]
