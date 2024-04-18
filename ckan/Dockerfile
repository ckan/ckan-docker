FROM ckan/ckan-base:2.10.4

# Install any extensions needed by your CKAN instance
# See Dockerfile.dev for more details and examples

### PDF View, Cryptography for RS256, S3 Filestore ###
RUN pip3 install ckanext-pdfview cryptography
RUN pip3 install -e git+https://github.com/keitaroinc/ckanext-s3filestore.git#egg=ckanext-s3filestore

# Copy keys
COPY keys/* /srv/app/

# Copy custom initialization scripts
COPY docker-entrypoint.d/* /docker-entrypoint.d/

# Copy custom supervisor conf
COPY supervisor-conf.d/* /etc/supervisord.d/


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
