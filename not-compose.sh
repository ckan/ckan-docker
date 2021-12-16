#!/bin/bash

#
# Create the network first
#
docker network create ckan-net
#


# Redis - Run only (image already built)
#
REDIS_CONTAINERNAME=redis
REDIS_HOSTNAME=redis

docker run -d -it --net ckan-net --name ${REDIS_CONTAINERNAME} --hostname ${REDIS_HOSTNAME} redis:latest

#
# Solr - Run/Build
#
SOLR_CONTAINERNAME=solr
SOLR_HOSTNAME=solr
SOLR_IMAGENAME=solr

cd solr
docker image build -t ${SOLR_IMAGENAME} .
docker run -d -it --net ckan-net --name ${SOLR_CONTAINERNAME} --hostname ${SOLR_HOSTNAME} \
                        -v solr_core:/opt/solr/server/solr ${SOLR_IMAGENAME}
cd -

#
# PostgreSQL (DB) - Run/Build
#
DB_CONTAINERNAME=db
DB_HOSTNAME=db
DB_IMAGENAME=db

cd postgresql
docker image build -t ${DB_IMAGENAME} .
docker run -d -it --net ckan-net --name ${DB_CONTAINERNAME} --hostname ${DB_HOSTNAME} --env-file=../environ \
                        -v pg_data:/var/lib/postgresql/data ${DB_IMAGENAME}
cd -

#
# CKAN - Run/Build
#
CKAN_CONTAINERNAME=ckan
CKAN_HOSTNAME=ckan
CKAN_IMAGENAME=ckan

cd ckan
docker image build -t ${CKAN_IMAGENAME} .
docker run -d -it --net ckan-net --name ${CKAN_CONTAINERNAME} --hostname ${CKAN_HOSTNAME} --env-file=../environ \
                        -v ckan_storage:/var/lib/ckan ${CKAN_IMAGENAME}
cd -

#
# Nginx - Run/Build
#
NGINX_CONTAINERNAME=nginx
NGINX_HOSTNAME=nginx
NGINX_IMAGENAME=nginx

cd nginx
docker image build -t ${NGINX_IMAGENAME} .
docker run -d -it --net ckan-net --name ${NGINX_CONTAINERNAME} --hostname ${NGINX_HOSTNAME} -p 0.0.0.0:80:80 ${NGINX_IMAGENAME}
cd -

#
# PostgreSQL client
#
docker run -d -it --net ckan-net --name postgres-client --hostname postgres-client -e POSTGRES_PASSWORD=ckan -p 5432:5432 postgres
