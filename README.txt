### Please note that this re-purposed CKAN Docker repo is a WORK IN PROGRESS ###
### It should not be used to install CKAN via Docker until this page is updated ###


Potential ideas/investigations from Keitaro (Marko Bocevski) : https://github.com/keitaroinc/docker-ckan:

- Maybe use build/up time variables loaded via the .env file, runtime variables loaded via a .ckan-env file - both
located at the root directory

- Look at using ghcr.io (GitHub Packages) to store Docker Images rather than DockerHub

- Should we use wheels too?

- Use Multi Stage Docker builds? 
    run some tests on image/container size with the different options
    a smaller production build vs a development build with all the dev tools

- Use SSL on the NGINX container port

- 2 networks: 1) Frontend 2) Backend

- Create/access a CKAN datapusher image rather than build one?

- all username/passwords as environment variables rather than hardcoded

- "/images" is a good folder name to use to be able to build all versions of CKAN and DataPusher images

- make sure the "development mode" path is taken cared of with any changes

- Create an admin user during the container deployment

- should there be a datapusher container built? maybe an xloader container?
