# Docker Compose setup for CKAN


* [1. Overview](#1-overview)
* [2. Installing Docker](#2-installing-docker)
* [3. docker compose vs docker-compose](#3-docker-compose-vs-docker-compose)
* [4. Install (build and run) CKAN plus dependencies](#4-install-build-and-run-ckan-plus-dependencies)
  * [Base mode](#base-mode)
  * [Development mode](#development-mode)
    * [Create an extension](#create-an-extension)
    * [Running HTTPS on development mode](#running-https-on-development-mode)
    * [Remote Debugging with VS Code](#remote-debugging-with-vs-code)
    * [Updating the environment file for development mode](#updating-the-environment-file-for-development-mode)
* [5. CKAN images](#5-ckan-images)
  * [Extending the base images](#extending-the-base-images)
  * [Applying patches](#applying-patches)
* [6. Debugging with pdb](#6-debugging-with-pdb)
* [7. Datastore and Datapusher](#7-datastore-and-datapusher)
* [8. NGINX](#8-nginx)
* [9. ckanext-envvars](#9-ckanext-envvars)
* [10. CKAN_SITE_URL](#10-CKAN_SITE_URL)
* [11. Manage new users](#11-manage-new-users)
* [12. Changing the base image](#12-changing-the-base-image)
* [13. Replacing DataPusher with XLoader](#13-replacing-datapusher-with-xLoader)


## 1.  Overview

This is a set of configuration and setup files to run a CKAN site.

The CKAN images used are from the official CKAN [ckan-docker](https://github.com/ckan/ckan-docker-base) repo

The non-CKAN images are as follows:

* DataPusher: CKAN's [pre-configured DataPusher image](https://github.com/ckan/ckan-docker-base/tree/main/datapusher).
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

### Base mode

Use this if you are a maintainer and will not be making code changes to CKAN or to CKAN extensions

Copy the included `.env.example` and rename it to `.env`. Modify it depending on your own needs.

> [!WARNING]
> There is a sysadmin user created by default with the values defined in `CKAN_SYSADMIN_NAME` and `CKAN_SYSADMIN_PASSWORD` (`ckan_admin` and `test1234` by default). These must be changed before running this setup as a public CKAN instance.

To build the images:

	docker compose build

To start the containers:

	docker compose up

This will start up the containers in the current window. By default the containers will log direct to this window with each container
using a different colour. You could also use the -d "detach mode" option ie: `docker compose up -d` if you wished to use the current 
window for something else.

At the end of the container start sequence there should be 6 containers running:

```bash
$ docker compose ps
NAME                       IMAGE                              COMMAND                  SERVICE      CREATED         STATUS                   PORTS
ckan-docker-ckan-1         ckan-docker-ckan                   "/srv/app/start_ckan…"   ckan         4 minutes ago   Up 3 minutes (healthy)   5000/tcp
ckan-docker-datapusher-1   ckan/ckan-base-datapusher:0.0.20   "sh -c 'uwsgi --plug…"   datapusher   4 minutes ago   Up 4 minutes (healthy)   8800/tcp
ckan-docker-db-1           ckan-docker-db                     "docker-entrypoint.s…"   db           4 minutes ago   Up 4 minutes (healthy)
ckan-docker-nginx-1        ckan-docker-nginx                  "/bin/sh -c 'openssl…"   nginx        4 minutes ago   Up 2 minutes             80/tcp, 0.0.0.0:8443->443/tcp
ckan-docker-redis-1        redis:6                            "docker-entrypoint.s…"   redis        4 minutes ago   Up 4 minutes (healthy)
ckan-docker-solr-1         ckan/ckan-solr:2.10-solr9          "docker-entrypoint.s…"   solr         4 minutes ago   Up 4 minutes (healthy)
```

After this step, CKAN should be running at `CKAN_SITE_URL` (by default https://localhost:8443)


### Development mode

Use this mode if you are making code changes to CKAN and either creating new extensions or making code changes to existing extensions. This mode also uses the `.env` file for config options.

To develop local extensions use the `docker-compose.dev.yml` file with help from the scripts under `bin`:

dev script | description
--- | ---
`bin/ckan …` | exec `ckan` cli within the ckan-dev container
`bin/compose …` | dev docker compose commands
`bin/generate_extension` | generate extension in `src` directory
`bin/install_src` | install all extensions from `src` directory (ckan-dev does not need to be running)
`bin/reload` | reload ckan within the ckan-dev container without restarting
`bin/restart` | shut down and restart the whole ckan-dev container (use `bin/compose up -d` instead to reload new values from .env)
`bin/shell` | exec bash prompt within the ckan-dev container

To build the images:

	bin/compose build

To install extensions from the `src` directory:

	bin/install_src

To start the containers:

	bin/compose up

See [CKAN images](#5-ckan-images) for more details of what happens when using development mode.


#### Create an extension

You can use the ckan [extension](https://docs.ckan.org/en/latest/extensions/tutorial.html#creating-a-new-extension) instructions to create a CKAN extension, only executing the command inside the CKAN container and setting the mounted `src/` folder as output:

        bin/generate_extension

```
Extension's name [must begin 'ckanext-']: ckanext-mytheme
Author's name []: Joe Bloggs
Author's email []: joeb@example.com
Your Github user or organization name []: example
Brief description of the project []: My CKAN theme
List of keywords (separated by spaces) [CKAN]:
Do you want to include code examples? [y/N]: y

Written: /srv/app/src_extensions/ckanext-mytheme
```

The new extension files and directories are created in the `/srv/app/src_extensions/` folder in the running container. They will also exist in the local src/ directory as local `/src` directory is mounted as `/srv/app/src_extensions/` on the ckan container.


#### Running HTTPS on development mode

Sometimes is useful to run your local development instance under HTTPS, for instance if you are using authentication extensions like [ckanext-saml2auth](https://github.com/keitaroinc/ckanext-saml2auth). To enable it, set the following in your `.env` file:

```
  USE_HTTPS_FOR_DEV=true
```

and update the site URL setting:

```
  CKAN_SITE_URL=https://localhost:5000
```

After recreating the `ckan-dev` container, you should be able to access CKAN at https://localhost:5000


#### Remote Debugging with VS Code

[Visual Studio Code](https://code.visualstudio.com/) is a free IDE that includes remote
debugging for Python applications. To debug CKAN you must enable `debugpy` for your
development instance in your `.env` file:

```
  USE_DEBUGPY_FOR_DEV=true
```

Next run the install script to install debugpy:

	bin/install_src

Then start the containers in [development mode](#development-mode) and launch VS Code.

In VS Code:

1. Install the "Dev Container" extension: press CTRL+SHIFT+X, type "dev container", click "install"
2. Click the "Open a Remote Window" button in the bottom-left of the VS Code window
3. Click "Attach to Running Container..." and select your ckan-dev container, e.g. "ckan-docker-ckan-dev-1"
4. Click the "Run and Debug" icon on the left panel and choose to install the "Python Debugger"
5. Click "create a launch.json", select "Python Debugger", "Remote Attach", host "localhost" and port "5678"
6. Press F5 or click the "Run" menu and "Start Debugging"

You can now set breakpoints and remote debug your CKAN development instance.


#### Updating the environment file for development mode

The Docker Compose environment `.env` file by default is set up for production mode. There are a few changes needed if you would like to run in Development mode:

1. Change the `CKAN_SITE_URL` variable to be: http://localhost:5000
2. Update the `CKAN__DATAPUSHER__CALLBACK_URL_BASE` variable to use the `ckan-dev` container name: http://ckan-dev:5000


## 5. CKAN images
![ckan images](https://user-images.githubusercontent.com/54408245/207079416-a01235af-2dea-4425-b6fd-f8c3687dd993.png)



The Docker image config files used to build your CKAN project are located in the `ckan/` folder. There are two Docker files:

* `Dockerfile`: this is based on `ckan/ckan-base:<version>`, a base image located in the DockerHub repository, that has CKAN installed along with all its dependencies, properly configured and running on [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) (production setup)
* `Dockerfile.dev`:  this is based on `ckan/ckan-base:<version>-dev` also located located in the DockerHub repository, and extends `ckan/ckan-base:<version>` to include:

  * Any extension cloned on the `src` folder will be installed in the CKAN container when booting up Docker Compose (`docker compose up`). This includes installing any requirements listed in a `requirements.txt` (or `pip-requirements.txt`) file and running `python setup.py develop`.
  * CKAN is started running this: `/usr/bin/ckan -c /srv/app/ckan.ini run -H 0.0.0.0`.
  * Make sure to add the local plugins to the `CKAN__PLUGINS` env var in the `.env` file.

* Any custom changes to the scripts run during container start up can be made to scripts in the `setup/` directory. For instance if you wanted to change the port on which CKAN runs you would need to make changes to the Docker Compose yaml file, and the `start_ckan.sh.override` file. Then you would need to add the following line to the Dockerfile ie: `COPY setup/start_ckan.sh.override ${APP_DIR}/start_ckan.sh`. The `start_ckan.sh` file in the locally built image would override the `start_ckan.sh` file included in the base image

### Extending the base images

The CKAN base images are built from https://github.com/ckan/ckan-docker-base/

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

## 6. Debugging with pdb

Add these lines to the `ckan-dev` service in the docker-compose.dev.yml file

```yaml
stdin_open: true
tty: true
```

Debug with pdb (example) - Interact with `docker attach $(docker container ls -qf name=ckan)`

command: `python -m pdb /usr/lib/ckan/venv/bin/ckan --config /srv/app/ckan.ini run --host 0.0.0.0 --passthrough-errors`

## 7. Datastore and datapusher

The Datastore database and user is created as part of the entrypoint scripts for the db container. There is also a Datapusher container 
running the latest version of Datapusher.

## 8. NGINX

The base Docker Compose configuration uses an NGINX image as the front-end (ie: reverse proxy). It includes HTTPS running on port number 8443. A "self-signed" SSL certificate is generated as part of the ENTRYPOINT. The NGINX `server_name` directive and the `CN` field in the SSL certificate have been both set to 'localhost'. This should obviously not be used for production.

Creating the SSL cert and key files as follows:
`openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -subj "/C=DE/ST=Berlin/L=Berlin/O=None/CN=localhost" -keyout ckan-local.key -out ckan-local.crt`
The `ckan-local.*` files will then need to be moved into the nginx/setup/ directory

## 9. ckanext-envvars

The ckanext-envvars extension is used in the CKAN Docker base repo to build the base images.
This extension checks for environmental variables conforming to an expected format and updates the corresponding CKAN config settings with its value.

For the extension to correctly identify which env var keys map to the format used for the config object, env var keys should be formatted in the following way:

  All uppercase  
  Replace periods ('.') with two underscores ('__')  
  Keys must begin with 'CKAN' or 'CKANEXT', if they do not you can prepend them with '`CKAN___`' 

For example:

  * `CKAN__PLUGINS="envvars image_view text_view recline_view datastore datapusher"`
  * `CKAN__DATAPUSHER__CALLBACK_URL_BASE=http://ckan:5000`
  * `CKAN___BEAKER__SESSION__SECRET=CHANGE_ME`

These parameters can be added to the `.env` file 

For more information please see [ckanext-envvars](https://github.com/okfn/ckanext-envvars)

## 10. CKAN_SITE_URL

For convenience the CKAN_SITE_URL parameter should be set in the .env file. For development it can be set to http://localhost:5000 and non-development set to https://localhost:8443

## 11. Manage new users

1. Create a new user from the Docker host, for example to create a new user called 'admin'

   `docker compose exec ckan ckan user add admin email=admin@localhost`

   To set this user as a sysadmin run

   `docker compose exec ckan ckan sysadmin add admin`

   To delete the 'admin' user

   `docker compose exec ckan ckan user remove admin`

   In development mode use `bin/ckan` instead of `docker compose exec ckan ckan` for the above commands.


## 12. Changing the base image

The base image used in the CKAN Dockerfile and Dockerfile.dev can be changed so a different DockerHub image is used eg: ckan/ckan-base:2.10.5 can be used instead of ckan/ckan-base:2.11.0

## 13. Replacing DataPusher with XLoader

Check out the wiki page for this: https://github.com/ckan/ckan-docker/wiki/Replacing-DataPusher-with-XLoader

Copying and License
-------------------

This material is copyright (c) 2006-2023 Open Knowledge Foundation and contributors.

It is open and licensed under the GNU Affero General Public License (AGPL) v3.0
whose full text may be found at:

http://www.fsf.org/licensing/licenses/agpl-3.0.html
