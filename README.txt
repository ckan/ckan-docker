### Please note that this re-purposed CKAN Docker repo is a WORK IN PROGRESS ###
### It should not be used to install CKAN via Docker until this page is updated ###

- Maybe use build/up time variables loaded via the .env file, runtime variables loaded via a .ckan-env file - both
located at the root directory
- Look at using ghcr.io (GitHub Packages) to store Docker Images rather than DockerHub
- all username/passwords as environment variables rather than hardcoded
- make sure the "development mode" path is taken cared of with any change
- Create an admin user during the container deployment
- should there be a datapusher image pre-built like ckan? maybe an xloader image?


### Difference between ckan-base and ckan-dev ###

ckan-base
docker-compose up -d --build
docker-compose build
docker-compose up

ckan-dev
docker-compose -f docker-compose.dev.yml up -d --build
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up

