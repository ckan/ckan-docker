FROM ckan/ckan-base:2.11.3

ARG TOKEN

# Workaround from https://github.com/ckan/ckan-docker/issues/196
USER root
RUN mkdir /srv/app/.local && chown ckan /srv/app/.local
RUN mkdir /srv/app/.cache && chown ckan /srv/app/.cache

# Copy harvester scripts
COPY config/*.sh  /srv/app

RUN chown -R ckan:ckan-sys ${APP_DIR} && chmod 755 /srv/app/*.sh

USER ckan


# Install any extensions needed by your CKAN instance
# See Dockerfile.dev for more details and examples

### Harvester ###
RUN pip3 install -e 'git+https://github.com/NCAR/ckanext-harvest.git@main#egg=ckanext-harvest' && \
    pip3 install -r ${APP_DIR}/src/ckanext-harvest/pip-requirements.txt && \
    pip3 install -r ${APP_DIR}/src/ckanext-harvest/dev-requirements.txt

# will also require gather_consumer and fetch_consumer processes running (please see https://github.com/ckan/ckanext-harvest)

### Spatial Harvester ###
RUN pip3 install -e 'git+https://github.com/NCAR/ckanext-spatial.git@main#egg=ckanext-spatial' && \
    pip3 install -r ${APP_DIR}/src/ckanext-spatial/pip-requirements.txt

### Repo Info; required by dsetsearch plugin ###
RUN pip3 install -e 'git+https://github.com/NCAR/ckanext-repo.git@main#egg=ckanext-repo'

### DASH Search custom plugin
RUN  pip3 install -e "git+https://${TOKEN}@github.com/NCAR/ckanext-dsetsearch.git#egg=ckanext-dsetsearch" && \
     pip3 install -r ${APP_DIR}/src/ckanext-dsetsearch/pip-requirements.txt

### Plugins for filtering on publication date and temporal extent
RUN  pip3 install -e "git+https://github.com/NCAR/ckanext-datesearch.git#egg=ckanext-datesearch"

RUN  pip3 install -e "git+https://github.com/NCAR/ckanext-extentsearch.git#egg=ckanext-extentsearch"

### Provide sitemap and Pure feed
RUN  pip3 install -e "git+https://github.com/NCAR/ckanext-sitemap.git#egg=ckanext-sitemap"

### Provide Google Analytics
RUN  pip3 install -e "git+https://github.com/ckan/ckanext-googleanalytics.git#egg=ckanext-googleanalytics"


USER root

### Install everything we need for the harvester
# Install cron and supervisor.
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    supervisor \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/log/ckan/std /var/log/supervisor /etc/supervisor/conf.d \
    && chown -R ckan:ckan-sys /var/log/ckan /var/log/supervisor /etc/supervisor/conf.d

# Config cron job for harvesting
COPY config/supervisord.conf /etc/supervisord.d/ckan.conf
COPY config/crontab /etc/cron.d/ckan-cron

# Running cron as non-root user and give permission to ckan user
RUN chmod gu+rw /var/run && \
    chmod gu+s /usr/sbin/cron && \
    crontab -u ckan /etc/cron.d/ckan-cron

# Copy custom initialization scripts
COPY --chown=ckan-sys:ckan-sys docker-entrypoint.d/* /docker-entrypoint.d/
COPY --chown=ckan-sys:ckan-sys setup/prerun.py ${APP_DIR}

# Apply any patches needed to CKAN core or any of the built extensions (not the
# runtime mounted ones)
COPY --chown=ckan-sys:ckan-sys patches ${APP_DIR}/patches


# Add supervisord invocation during startup
RUN sed -i '/uwsgi \$UWSGI_OPTS/i\    supervisord --configuration \/etc\/supervisord.d\/ckan.conf &' ${APP_DIR}/start_ckan.sh

USER ckan
RUN for d in $APP_DIR/patches/*; do \
        if [ -d $d ]; then \
            for f in `ls $d/*.patch | sort -g`; do \
                cd $SRC_DIR/`basename "$d"` && echo "$0: Applying patch $f to $SRC_DIR/`basename $d`"; patch -p1 < "$f" ; \
            done ; \
        fi ; \
    done
