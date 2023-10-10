FROM nginx:stable-alpine

ARG CKAN_URL
ARG DOMAIN
ARG EMAIL
ARG SSL_CERT_OPTIONS
ARG SSL_CERT_RENEW

ENV CKAN_URL=${CKAN_URL}
ENV DOMAIN=${DOMAIN}
ENV EMAIL=${EMAIL}
ENV SSL_CERT_OPTIONS=${SSL_CERT_OPTIONS}
ENV SSL_CERT_RENEW=${SSL_CERT_RENEW}
ENV NGINX_DIR=/etc/nginx

RUN apk update --no-cache && \
    apk upgrade --no-cache && \
    apk add --no-cache openssl inotify-tools certbot

COPY setup/index.html /usr/share/nginx/html/index.html
COPY setup/nginx.conf ${NGINX_DIR}/nginx.conf
COPY setup/default.conf ${NGINX_DIR}/conf.d/default.conf.template
RUN envsubst '${DOMAIN}${CKAN_URL}' < ${NGINX_DIR}/conf.d/default.conf.template > ${NGINX_DIR}/conf.d/default.conf && \
    rm -f ${NGINX_DIR}/conf.d/default.conf.template && \
    mkdir -p /var/cache/nginx/proxycache && \
    mkdir -p /var/cache/nginx/proxytemp

WORKDIR /opt
COPY setup/cert-entrypoint.sh entrypoint.sh
COPY setup/cert-request.sh request.sh
COPY setup/health-check.sh status.sh

RUN chmod a+x entrypoint.sh && \
    chmod a+x request.sh && \
    chmod a+x status.sh

EXPOSE 80 443

ENTRYPOINT ["./entrypoint.sh"]
