# (from) July 7 2022
# This repo will be actively worked on from now.
# This file will be my ToDo list of things to take care of

ckan/ckan-docker-base: For the base images Dockerfiles (prod and dev) and related scripts
ckan/ckan-docker: For the project-oriented image template (prod and dev). Patching only done in Dev ### This repo!

All the other images should live in separate repos

1. Solr -           use ckan-solr   (https://github.com/ckan/ckan-solr)
2. PostgreSQL -     use current method (base image: postgres:12-alpine from DockerHub, enhanced in a Dockerfile) 
                    ### This may change to be more like Solr though
3. Redis -          use current method (DockerHub image: redis:${REDIS_VERSION} specified as a compose service in the compose file) 
                    latest image to used is redis:6
4. nginx -          base image: nginx:1.19.8-alpine from DockerHub, enhanced in a Dockerfile)
5. DataPusher -     built from the actual datapusher repo (https://github.com/ckan/datapusher)
6. CKAN Worker -    add new (ckan worker) container in the compose setup

Versions 2.9 and 2.10 (when it's out) only. Plan the repo layout for having multiple versions - OKFN could used as an example

Go through all the new changes in the current repo and use those for the new repo if they make sense
- Francesco's PR https://github.com/ckan/ckan/pull/4635 which is a beauty!
- use FROM ubuntu:focal for ckan
- Health Checks https://github.com/ckan/ckan/pull/6812
- Restarts https://github.com/ckan/ckan/pull/6569
- Make asure ARGs are used if they are added to compose file
- Check out Florian's docs https://github.com/dbca-wa/ckan/blob/dbca2022/doc/maintaining/installing/install-from-docker-compose.rst
- Check out Florian's repo https://github.com/dbca-wa/ckan/tree/dbca2022
- Documentation to be re-done from scratch...anything that could be useful can be mentioned here eg: local storage for ckan.ini
