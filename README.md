# Docker Compose setup for CKAN


* [Overview](#overview)
* [Quick start](#quick-start)
* [Development mode](#development-mode)
   * [Create an extension](#create-an-extension)
* [CKAN images](#ckan-images)
   * [Extending the base images](#extending-the-base-images)
   * [Applying patches](#applying-patches)
* [Debugging with pdb](#pdb)
* [Known Issues](#known-issues)


## Overview

This is a set of configuration and setup files to run a CKAN site.

The CKAN images used are from the official CKAN [ckan-docker](https://github.com/ckan/ckan-docker) repo

The non-CKAN images are as follows:

* DataPusher: modified from the datapusher image build configuration from the [OKFN docker-ckan](https://github.com/okfn/docker-ckan) repo
* PostgreSQL: Official PostgreSQL image. Database files are stored in a named volume.
* Solr: CKAN's [pre-configured Solr image](https://github.com/ckan/ckan-solr). Index data is stored in a named volume.
* Redis: standard Redis image

The site is configured via env vars (the base CKAN image loads [ckanext-envvars](https://github.com/okfn/ckanext-envvars)), that you can set in the `.env` file.

## Quick start

Copy the included `.env.example` and rename it to `.env` to modify it depending on your own needs.

Using the default values on the `.env.example` file will get you a working CKAN instance. There is a sysadmin user created by default with the values defined in `CKAN_SYSADMIN_NAME` and `CKAN_SYSADMIN_PASSWORD`(`ckan_admin` and `test1234` by default). This should be obviously changed before running this setup as a public CKAN instance.

To build the images:

	docker-compose build

To start the containers:

	docker-compose up

## Development mode

To develop local extensions use the `docker-compose.dev.yml` file:

To build the images:

	docker-compose -f docker-compose.dev.yml build

To start the containers:

	docker-compose -f docker-compose.dev.yml up

See [CKAN Images](#ckan-images) for more details of what happens when using development mode.


### Create an extension

You can use the ckan [extension](https://docs.ckan.org/en/latest/extensions/tutorial.html#creating-a-new-extension) instructions to create a CKAN extension, only executing the command inside the CKAN container and setting the mounted `src/` folder as output:

    docker-compose -f docker-compose.dev.yml exec ckan-dev /bin/bash -c "ckan generate extension --output-dir /srv/app/src_extensions"

The new extension files and directories will be created in the `src/` folder. You might need to change the owner of its folder to have the appropiate permissions.


## CKAN images
![CKAN ckan-docker image](https://user-images.githubusercontent.com/54408245/179516510-f881cc94-7f95-4737-8450-8e2ece4325c3.png)


The Docker images used to build your CKAN project are located in the `ckan/` folder. There are two Docker files:

* `Dockerfile`: this is based on `ckan/ckan-base:<version>`, a base image located in the DockerHub repository, that has CKAN installed along with all its dependencies, properly configured and running on [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) (production setup)
* `Dockerfile.dev`:  this is based on `ckan/ckan-base:<version>-dev` also located located in the DockerHub repository, and extends `ckan/ckan-base:<version>` to include:

  * Any extension cloned on the `src` folder will be installed in the derived CKAN container when booting up Docker Compose (`docker-compose up`). This includes installing any requirements listed in a `requirements.txt` (or `pip-requirements.txt`) file and running `python setup.py develop`.
  * CKAN will be started running `ckan -c /srv/app/ckan.ini run`.
  * Make sure to add the local plugins to the `CKAN__PLUGINS` env var in the `.env` file.

From these two base images you can build your own customized image tailored to your project, installing any extensions and extra requirements needed.

### Extending the base images

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
FROM ckan/ckan-base:2.9.5-dev

RUN pip install -e git+https://github.com/frictionlessdata/ckanext-validation.git#egg=ckanext-validation && \
    pip install -r https://raw.githubusercontent.com/frictionlessdata/ckanext-validation/master/requirements.txt

COPY docker-entrypoint.d/* /docker-entrypoint.d/
```

### Applying patches

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

## pdb

Add these lines to the `ckan-dev` service in the docker-compose.dev.yml file

![pdb](https://user-images.githubusercontent.com/54408245/179964232-9e98a451-5fe9-4842-ba9b-751bcc627730.png)

Debug with pdb (example) - Interact with `docker attach $(docker container ls -qf name=ckan)`

command: `python -m pdb /usr/lib/ckan/venv/bin/ckan --config /srv/app/ckan.ini run --host 0.0.0.0 --passthrough-errors`

## Known Issues

* Running the tests: Running the tests for CKAN or an extension inside the container will delete your current database. We need to patch CKAN core in our image to work around that.
