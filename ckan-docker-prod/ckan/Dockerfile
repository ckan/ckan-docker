FROM ckan/ckan-base:2.11

COPY --chown=ckan-sys:ckan-sys docker-entrypoint.d/* /docker-entrypoint.d/
COPY --chown=ckan-sys:ckan-sys ckanext-idsk /srv/app/src/ckanext-idsk
COPY --chown=ckan-sys:ckan-sys ckanext-datahub /srv/app/src/ckanext-datahub

USER root

RUN pip3 install --no-cache-dir -e /srv/app/src/ckanext-idsk \
    && pip3 install --no-cache-dir -e /srv/app/src/ckanext-datahub \
    && pip3 install --no-cache-dir ckanext-dcat ckanext-scheming

USER ckan
