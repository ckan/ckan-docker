FROM nginx:stable-alpine

ENV NGINX_DIR=/etc/nginx

COPY setup/index.html /usr/share/nginx/html/index.html
COPY setup/*.conf ${NGINX_DIR}/conf.d/

#RUN mkdir -p /tmp/nginx/cache

EXPOSE 81