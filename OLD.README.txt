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

Dev Mode (OKFN)

The differences between Docker dev abd Docker base is as the following:

docker-compose.dev.yml
    solr: explicitly puts in ports (8983:8983)
    db: Doesn't pass in environment and arg values
    ckan: has extra volume bind mount (./src:/srv/app/src_extensions)

Dockerfile.dev
    Takes the base image and
        Adds a new directory (SRC_EXTENSIONS_DIR=/srv/app/src_extensions)
        installs libffi-dev
        installs dev-requirements.txt
        runs different start script (start_ckan_development.sh) which installs any extension located in SRC_EXTENSIONS_DIR 
        runs a typical Dev install
            pip install -r pip-requirements.txt
            pip install -r requirements.txt
            pip install -r dev-requirements.txt
            python3 setup.py develop
            ckan config-tool test.ini
            ckan config-tool $CKAN_INI -s DEFAULT "debug = true"
            ckan config-tool $CKAN_INI "ckan.plugins = $CKAN__PLUGINS"
            ckan config-tool $SRC_DIR/ckan/test-core.ini \
                "sqlalchemy.url = $TEST_CKAN_SQLALCHEMY_URL" \
                "ckan.datastore.write_url = $TEST_CKAN_DATASTORE_WRITE_URL" \
                "ckan.datastore.read_url = $TEST_CKAN_DATASTORE_READ_URL" \
                "solr_url = $TEST_CKAN_SOLR_URL" \
                "ckan.redis.url = $TEST_CKAN_REDIS_URL"

    All other steps are similar to the base Dockerfile

