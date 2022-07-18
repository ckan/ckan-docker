#!/bin/bash

# Stop all containers
docker kill $(docker ps -q)

# Remove all stopped containers
docker rm -f $(docker ps -aq)

# Remove all docker images
docker rmi $(docker images -q)

# Remove all volumes
docker volume rm $(docker volume ls -q)

# Remove ckan-docker_default network
docker network rm ckan-docker_default
