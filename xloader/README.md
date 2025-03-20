### Implementing XLoader as a replacement for DataPusher
----
 
#### Here are the instructions

Basically it's just a matter of replacing files from the xloader directory overriding files in the root directory

##### For Production (base)

 1. `cd xloader/`
 2. `cp .env ..`
 3. `cp docker-compose.yml ..`
 4. `cp Dockerfile ../ckan`
 5. `cp -pr docker-entrypoint.d/ ../ckan`

##### For Development

 1. `cd xloader/`
 2. `cp .env ..`
 3. `cp docker-compose-dev.yml ..`
 4. `cp Dockerfile.dev ../ckan`
 5. `cp -pr docker-entrypoint.d/ ../ckan`