# Docker Compose setup for CKAN


* [Overview](#overview)
* [Installing Docker](#installing-docker)
* [docker compose vs docker-compose](#docker-compose-vs-docker-compose)
* [Install CKAN plus dependencies](#install-ckan-plus-dependencies)
* [Development mode](#development-mode)
   * [Create an extension](#create-an-extension)
* [CKAN images](#ckan-images)
   * [Extending the base images](#extending-the-base-images)
   * [Applying patches](#applying-patches)
* [Debugging with pdb](#pdb)
* [Datastore and Datapusher](#Datastore-and-datapusher)
* [NGINX](#nginx)
* [The ckanext-envvars extension](#envvars)


## 1.  Overview

This is a set of configuration and setup files to run a CKAN site.

The CKAN images used are from the official CKAN [ckan-docker](https://github.com/ckan/ckan-docker-base) repo

The non-CKAN images are as follows:

* DataPusher: CKAN's [pre-configured DataPusher image](https://github.com/ckan/ckan-base/tree/main/datapusher).
* PostgreSQL: Official PostgreSQL image. Database files are stored in a named volume.
* Solr: CKAN's [pre-configured Solr image](https://github.com/ckan/ckan-solr). Index data is stored in a named volume.
* Redis: standard Redis image
* NGINX: latest stable nginx image that includes SSL and Non-SSL endpoints

The site is configured using environment variables that you can set in the `.env` file.

## 2.  Installing Docker

Install Docker by following the following instructions: [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)

To verify a successful Docker installation, run `docker run hello-world` and `docker version`. These commands should output 
versions for client and server.

## 3.  docker compose *vs* docker-compose

All Docker Compose commands in this README will use the V2 version of Compose ie: `docker compose`. The older version (V1) 
used the `docker-compose` command. Please see [Docker Compose](https://docs.docker.com/compose/compose-v2/) for
more information.

## 4.  Install (build and run) CKAN plus dependencies

#### Base mode

Use this if you are a maintainer and will not be making code changes to CKAN or to CKAN extensions

Copy the included `.env.example` and rename it to `.env`. Modify it depending on your own needs.

Using the default values on the `.env.example` file will get you a working CKAN instance. There is a sysadmin user created by default with the values defined in `CKAN_SYSADMIN_NAME` and `CKAN_SYSADMIN_PASSWORD`(`ckan_admin` and `test1234` by default). This should be obviously changed before running this setup as a public CKAN instance.

To build the images:

	docker compose build

To start the containers:

	docker compose up

This will start up the containers in the current window. By default the containers will log direct to this window with each container
using a different colour. You could also use the -d "detach mode" option ie: `docker compose up -d` if you wished to use the current 
window for something else.

At the end of the container start sequence there should be 6 containers running

![Screenshot 2022-12-12 at 10 36 21 am](https://user-images.githubusercontent.com/54408245/207012236-f9571baa-4d99-4ffe-bd93-30b11c4829e0.png)

After this step, CKAN should be running at `CKAN_SITE_URL`.


#### Development mode

Use this mode if you are making code changes to CKAN and either creating new extensions or making code changes to existing extensions. This mode also uses the `.env` file for config options.

To develop local extensions use the `docker-compose.dev.yml` file:

To build the images:

	docker compose -f docker-compose.dev.yml build

To start the containers:

	docker compose -f docker-compose.dev.yml up

See [CKAN Images](#ckan-images) for more details of what happens when using development mode.



##### Create an extension

You can use the ckan [extension](https://docs.ckan.org/en/latest/extensions/tutorial.html#creating-a-new-extension) instructions to create a CKAN extension, only executing the command inside the CKAN container and setting the mounted `src/` folder as output:

    docker compose -f docker-compose.dev.yml exec ckan-dev /bin/sh -c "ckan generate extension --output-dir /srv/app/src_extensions"
    
![Screenshot 2023-02-22 at 1 45 55 pm](https://user-images.githubusercontent.com/54408245/220623568-b4e074c7-6d07-4d27-ae29-35ce70961463.png)


The new extension files and directories are created in the `/srv/app/src_extensions/` folder in the running container. They will also exist in the local src/ directory as local `/src` directory is mounted as `/srv/app/src_extensions/` on the ckan container. You might need to change the owner of its folder to have the appropiate permissions.


## 5. CKAN images
![ckan images](https://user-images.githubusercontent.com/54408245/207079416-a01235af-2dea-4425-b6fd-f8c3687dd993.png)



The Docker image config files used to build your CKAN project are located in the `ckan/` folder. There are two Docker files:

* `Dockerfile`: this is based on `ckan/ckan-base:<version>`, a base image located in the DockerHub repository, that has CKAN installed along with all its dependencies, properly configured and running on [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) (production setup)
* `Dockerfile.dev`:  this is based on `ckan/ckan-base:<version>-dev` also located located in the DockerHub repository, and extends `ckan/ckan-base:<version>` to include:

  * Any extension cloned on the `src` folder will be installed in the CKAN container when booting up Docker Compose (`docker compose up`). This includes installing any requirements listed in a `requirements.txt` (or `pip-requirements.txt`) file and running `python setup.py develop`.
  * CKAN is started running this: `/usr/bin/ckan -c /srv/app/ckan.ini run -H 0.0.0.0`.
  * Make sure to add the local plugins to the `CKAN__PLUGINS` env var in the `.env` file.


## 6. Extending the base images

You can modify the docker files to build your own customized image tailored to your project, installing any extensions and extra requirements needed. For example here is where you would update to use a different CKAN base image ie: `ckan/ckan-base:<new version>`

To perform extra initialization steps you can add scripts to your custom images and copy them to the `/docker-entrypoint.d` folder (The folder should be created for you when you build the image). Any `*.sh` and `*.py` file in that folder will be executed just after the main initialization script ([`prerun.py`](https://github.com/ckan/ckan-docker-base/blob/main/ckan-2.9/base/setup/prerun.py)) is executed and just before the web server and supervisor processes are started.

For instance, consider the following custom image:

```
ckan
├── docker-entrypoint.d
│   └── setup_validation.sh
├── Dockerfile
└── Dockerfile.dev

```

We want to install an extension like [ckanext-validation](https://github.com/frictionlessdata/ckanext-validation) that needs to create database tables on startup time. We create a `setup_validation.sh` script in a `docker-entrypoint.d` folder with the necessary commands:

```bash
#!/bin/bash

# Create DB tables if not there
ckan -c /srv/app/ckan.ini validation init-db 
```

And then in our `Dockerfile.dev` file we install the extension and copy the initialization scripts:

```Dockerfile
FROM ckan/ckan-base:2.9.7-dev

RUN pip install -e git+https://github.com/frictionlessdata/ckanext-validation.git#egg=ckanext-validation && \
    pip install -r https://raw.githubusercontent.com/frictionlessdata/ckanext-validation/master/requirements.txt

COPY docker-entrypoint.d/* /docker-entrypoint.d/
```

NB: There are a number of extension examples commented out in the Dockerfile.dev file

## 7. Applying patches

When building your project specific CKAN images (the ones defined in the `ckan/` folder), you can apply patches 
to CKAN core or any of the built extensions. To do so create a folder inside `ckan/patches` with the name of the
package to patch (ie `ckan` or `ckanext-??`). Inside you can place patch files that will be applied when building
the images. The patches will be applied in alphabetical order, so you can prefix them sequentially if necessary.

For instance, check the following example image folder:

```
ckan
├── patches
│   ├── ckan
│   │   ├── 01_datasets_per_page.patch
│   │   ├── 02_groups_per_page.patch
│   │   ├── 03_or_filters.patch
│   └── ckanext-harvest
│       └── 01_resubmit_objects.patch
├── setup
├── Dockerfile
└── Dockerfile.dev

```

## 8. pdb

Add these lines to the `ckan-dev` service in the docker-compose.dev.yml file

![pdb](https://user-images.githubusercontent.com/54408245/179964232-9e98a451-5fe9-4842-ba9b-751bcc627730.png)

Debug with pdb (example) - Interact with `docker attach $(docker container ls -qf name=ckan)`

command: `python -m pdb /usr/lib/ckan/venv/bin/ckan --config /srv/app/ckan.ini run --host 0.0.0.0 --passthrough-errors`

## 9. Datastore and datapusher

The Datastore database and user is created as part of the entrypoint scripts for the db container. There is also a Datapusher container 
running the latest version of Datapusher.

## 10. NGINX

The base Docker Compose configuration uses an NGINX image as the front-end (ie: reverse proxy). It includes HTTPS running on port number 8443 and an HTTP port (81). A "self-signed" SSL certificate is generated beforehand and the server certificate and key files are included. The NGINX `server_name` directive and the `CN` field in the SSL certificate have been both set to 'localhost'. This should obviously not be used for production.

Creating the SSL cert and key files as follows:
`openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -subj "/C=DE/ST=Berlin/L=Berlin/O=None/CN=localhost" -keyout ckan-local.key -out ckan-local.crt`
The `ckan-local.*` files will then need to be moved into the nginx/setup/ directory

## 11. envvars

The ckanext-envvars extension is used in the CKAN Docker base repo to build the base images.
This extension checks for environmental variables conforming to an expected format and updates the corresponding CKAN config settings with its value.

For the extension to correctly identify which env var keys map to the format used for the config object, env var keys should be formatted in the following way:

  All uppercase
  Replace periods ('.') with two underscores ('__')
  Keys must begin with 'CKAN' or 'CKANEXT'

For example:

  * `CKAN__PLUGINS="envvars image_view text_view recline_view datastore datapusher"`
  * `CKAN__DATAPUSHER__CALLBACK_URL_BASE=http://ckan:5000`

These parameters can be added to the `.env` file 

For more information please see [ckanext-envvars](https://github.com/okfn/ckanext-envvars)
