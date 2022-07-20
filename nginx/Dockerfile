FROM nginx:stable-alpine

ENV NGINX_DIR=/etc/nginx

COPY setup/nginx.conf ${NGINX_DIR}/nginx.conf
COPY setup/index.html /usr/share/nginx/html/index.html
COPY setup/default.conf ${NGINX_DIR}/conf.d/

EXPOSE 81