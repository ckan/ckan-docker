FROM alpine:3.13.5

ENV APP_DIR=/srv/app
ENV SRC_DIR=${APP_DIR}/src
ENV GIT_URL https://github.com/ckan/datapusher.git
ENV GIT_BRANCH 0.0.17
ENV JOB_CONFIG ${APP_DIR}/datapusher_settings.py
ENV CKAN__PLUGINS image_view text_view recline_view datastore datapusher envvars

WORKDIR ${APP_DIR}

RUN apk upgrade && \
    apk add --no-cache \
        python3 \
        curl \
        gcc \
        make \
        g++ \
        autoconf \
        automake \
        libtool \
        git \
        musl-dev \
        python3-dev \
        libffi-dev \
        openssl-dev \
        libxml2-dev \
        libxslt-dev \
        rust  \
        cargo

RUN apk add --no-cache \
        uwsgi \
        uwsgi-http \
        uwsgi-corerouter \
        uwsgi-python

# Create the src directory
RUN mkdir -p ${SRC_DIR}

# Install pip
RUN curl -o ${SRC_DIR}/get-pip.py https://bootstrap.pypa.io/get-pip.py && \
    python3 ${SRC_DIR}/get-pip.py

# Install datapusher
RUN cd ${SRC_DIR} && \
    git clone -b ${GIT_BRANCH} --depth=1 --single-branch ${GIT_URL} && \
    cd datapusher && \
    python3 setup.py install && \
    pip3 install --no-cache-dir -r requirements.txt

RUN cp ${APP_DIR}/src/datapusher/deployment/*.* ${APP_DIR} && \
    # Remove default values in ini file
    sed -i '/http/d' ${APP_DIR}/datapusher-uwsgi.ini && \
    sed -i '/wsgi-file/d' ${APP_DIR}/datapusher-uwsgi.ini && \
    sed -i '/virtualenv/d' ${APP_DIR}/datapusher-uwsgi.ini && \
    # Remove src files
    rm -rf ${APP_DIR}/src

# Create a 'ckan' local user and group to run the app
RUN addgroup -g 92 -S www-data && \
    adduser -u 92 -h /srv/app -H -D -S -G www-data www-data

# Set timezone
RUN echo "UTC" >  /etc/timezone && \
    # Change ownership to app user
    chown -R www-data:www-data /srv/app

EXPOSE 8800
CMD ["sh", "-c", \
    "uwsgi --plugins=http,python --http=0.0.0.0:8800 --socket=/tmp/uwsgi.sock --ini=`echo ${APP_DIR}`/datapusher-uwsgi.ini --wsgi-file=`echo ${APP_DIR}`/datapusher.wsgi"]
