### Please note that this re-purposed CKAN Docker repo is a WORK IN PROGRESS ###
### It should not be used to install CKAN via Docker until this page is updated ###

-------------------------------------
(From Adria)
Be limited in scope, and act as a base that users can extend to their own needs
Be opinionated, and provide one way to do things
Be automatically tested
-------------------------------------

should we have an nginx container included? maybe just instructions on how to include one

ARG should be used for sensitive variables so as to keep the values of these variables 
out of the build and hence will not show with an "inspect image" command

Do we pre-build a CKAN image and use that (and extend) as the base image OR 
    just build it from scratch and while saving to storage what we need to

To use local storage for the ckan.ini file and the CKAN src code, do the following:

# docker-compose up -d --build
# mkdir local
# docker cp ckan:/srv/app/ckan.ini ./local/ckan.ini
# docker cp ckan:/srv/app/src ./local/src
Stop/Remove ckan container
Start ckan container as follows
Use a bind mount for the config file (ckan.ini)
# docker run -p 0.0.0.0:5000:5000 --net ckan-docker_default --hostname ckan --name ckan \
        --env-file=./environ --mount type=bind,source=$(pwd)/local/ckan.ini,target=/srv/app/ckan.ini \
        --mount type=bind,source=$(pwd)/local/src,target=/srv/app/src \
        -d ckan-docker_ckan

Maybe include a script to replace docker-compose if required
