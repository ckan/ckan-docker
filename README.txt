### Please note that this re-purposed CKAN Docker repo is a WORK IN PROGRESS ###
### It should not be used to install CKAN via Docker until this page is updated ###


Potential ideas/investigations from Keitaro (Marko Bocevski) : https://github.com/keitaroinc/docker-ckan:

- Maybe use build/up time variables loaded via the .env file, runtime variables loaded via a .ckan-env file - both
located at the root directory
- Should we use wheels too? 
- 2 networks: 1) Frontend 2) Backend
- Create/access a CKAN datapusher image rather than build one?
- all username/passwords as environment variables rather than hardcoded
- "/images" is a good folder name to use to be able to build all versions of CKAN and DataPusher images
- include an "/examples" folder for examples of adding extentions xloader, harvester, etc

- make sure the "development mode" path is taken cared of with any changes
- Create an admin user during the container deployment
- should there be a datapusher container built? maybe an xloader container?
