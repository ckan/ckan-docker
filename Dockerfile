FROM ckan/ckan-base:testing-only.2.9

LABEL maintainer="brett@kowh.ai"

#RUN apk update \
#    && apk upgrade \
#    && apk add --no-cache libffi-dev \
#    libmagic
    

# Set up environment variables
ENV APP_DIR=/srv/app
ENV TZ=UTC
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

RUN echo ${TZ} > /etc/timezone

# Make sure both files are not exactly the same
RUN if ! [ /usr/share/zoneinfo/${TZ} -ef /etc/localtime ]; then \
        cp /usr/share/zoneinfo/${TZ} /etc/localtime ;\
    fi ;

#RUN pip3 install -e 'git+https://github.com/DataShades/ckanext-xloader@py3#egg=ckanext-xloader'
#RUN pip3 install -r ${APP_DIR}/src/ckanext-xloader/requirements.txt
#RUN pip3 install -U requests[security]

# Install any extensions needed by your CKAN instance
# (Make sure to add the plugins to CKAN__PLUGINS in the .env file)
# For instance:
#RUN pip install -e git+https://github.com/ckan/ckanext-pages.git#egg=ckanext-pages && \
#    pip install -e git+https://github.com/ckan/ckanext-dcat.git@v0.0.6#egg=ckanext-dcat && \
#    pip install -r https://raw.githubusercontent.com/ckan/ckanext-dcat/v0.0.6/requirements.txt

# Install the extension(s) you wrote for your own project
# RUN pip install -e git+https://github.com/your-org/ckanext-your-extension.git@v1.0.0#egg=ckanext-your-extension

# Apply any patches needed to CKAN core or any of the built extensions (not the
# runtime mounted ones)
# See https://github.com/okfn/docker-ckan#applying-patches

#COPY patches ${APP_DIR}/patches

# Copy patches and apply patches script
COPY ./patches ${SRC_DIR}/patches
COPY ./scripts/apply_ckan_patches.sh ${SRC_DIR}/apply_ckan_patches.sh
# Apply patches
#RUN ${SRC_DIR}/apply_ckan_patches.sh

RUN for d in ${APP_DIR}/patches/*; do \
        if [ -d $d ]; then \
            for f in `ls $d/*.patch | sort -g`; do \
                cd $SRC_DIR/`basename "$d"` && echo "$0: Applying patch $f to $SRC_DIR/`basename $d`"; patch -p1 < "$f" ; \
            done ; \
        fi ; \
    done
