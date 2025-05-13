FROM nginx:stable-alpine

ENV NGINX_DIR=/etc/nginx

RUN apk update --no-cache && \
    apk upgrade --no-cache && \
    apk add --no-cache openssl

COPY setup/nginx.conf ${NGINX_DIR}/nginx.conf
COPY setup/index.html /usr/share/nginx/html/index.html
COPY setup/error.html /usr/share/nginx/html/error.html
COPY setup/default.conf ${NGINX_DIR}/conf.d/
COPY setup/ssl ${NGINX_DIR}/conf.d/ssl/

CMD ["nginx", "-g", "daemon off;"]
