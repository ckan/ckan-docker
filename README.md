<h1 align="center">CKAN Docker Compose - Open Data & GIS</h1>
<p align="center">
<a href="https://github.com/OpenDataGIS/ckan"><img src="https://img.shields.io/badge/Docker%20CKAN-2.9.8-brightgreen" alt="CKAN Versions"></a>


<p align="center">
    <a href="#overview">Overview</a> •
    <a href="#ckan-docker-roadmap">Branch roadmap</a> •
    <a href="#environment-docker">Environment: docker</a> •
    <a href="#install-build-and-run-ckan-plus-dependencies">Install CKAN</a> •
    <a href="#ckan-images">CKAN images</a> •   
    <a href="#extending-the-base-images">Extending guide</a> •
    <a href="#applying-patches">Applying patches</a> •
    <a href="#ckan-docker-addons">Addons</a>
</p>

**Requirements**:
* [Docker](https://docs.docker.com/get-docker/)

## Overview
Contains Docker images for the different components of CKAN Cloud and a Docker compose environment (based on [ckan](https://github.com/ckan/ckan)) for development and testing Open Data portals.

>**Warning**:<br>
>This is a **custom installation of Docker Compose** with specific extensions for spatial data and [GeoDCAT-AP](https://github.com/SEMICeu/GeoDCAT-AP)/[INSPIRE](https://github.com/INSPIRE-MIF/technical-guidelines) metadata [profiles](https://en.wikipedia.org/wiki/Geospatial_metadata). For official installations, please have a look: [CKAN documentation: Installation](https://docs.ckan.org/en/latest/maintaining/installing/index.html).

Available components:
* CKAN custom image based on the official CKAN repo [ckan-docker-base](https://github.com/ckan/ckan-docker-base)

The non-CKAN images are as follows:
* PostgreSQL: Official PostgreSQL image. Database files are stored in a named volume.
* Solr: CKAN's [pre-configured Solr image](https://github.com/ckan/ckan-solr). The index data is stored in a named volume and has a spatial schema. [^1]
* Redis: standard Redis image
* NGINX: latest stable nginx image that includes SSL and Non-SSL endpoints

| Repository | Type | Docker tag | Size | Notes |
| --- | --- | --- | --- | --- |
| PostgreSQL 12.14 | base image | [`postgres/postgres:12-alpine`](https://hub.docker.com/layers/library/postgres/12-alpine/images/sha256-e07198f71e85eccd6c351bb4eb0b2ff833bef2dd6ea314f6442c2dc47535fbb7?context=explore) | 87.09 MB |   Custom Dockerfile: [`postgresql/Dockerfile`](/postgresql/Dockerfile) |
| Solr 8.11.1 | base image | [`ckan/ckan-solr:2.9-solr8-spatial`](https://registry.hub.docker.com/layers/ckan/ckan-solr/2.9-solr8-spatial/images/sha256-b5ee4979891c7dd1f10d2ac2cbdd4d80ff656879edb0f0493616be7b4cf8bc3a?context=explore) | 331.1 MB |  - |
| Redis 6.2.11 | base image | [`redis/redis:6`](https://hub.docker.com/layers/library/redis/6/images/sha256-e10c69dc5f9b27c47874060962fdaa26ec0df592205d6d21402945267081b434?context=explore) | 39.32 MB |  - |
| NGINX 1.22.1 | base image | [`nginx:stable-alpine`](https://hub.docker.com/layers/library/nginx/stable-alpine/images/sha256-ff2a5d557ca22fa93669f5e70cfbeefda32b98f8fd3d33b38028c582d700f93a?context=explore) | 9.74 MB |  Custom Dockerfile: [`nginx/Dockerfile`](/nginx/Dockerfile) |


The site is configured using environment variables that you can set in the `.env` file.


### ckan-docker roadmap
Information about extensions installed in the `main` image. More info described in the [Extending the base images](#extending-the-base-images)

>**Note**<br>
> Switch branches to see the `roadmap` for other projects: [ckan-docker/branches](https://github.com/mjanez/ckan-docker/branches)


| **Element** | **Description**                                                                         | **version** | **Status**                   | **DEV**[^2] | **PRO**[^3]  | **Remarks**                                                                                                                                                                                                                                                                                                                                                             |
|-------------|-----------------------------------------------------------------------------------------|-------------|------------------------------|---------|---------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Core        | [CKAN](https://github.com/mjanez/ckan-docker)                                           | 2.9.8      | Completed                    | ✔️      | ✔️      | Stable installation for version 2.9.8 (Production & Dev images) via Docker Compose based on [official images](https://github.com/ckan/ckan-docker-base)). Initial configuration, basic customisation and operation guide.                                                                                                                                              |
| Core +      | [Datastore](https://github.com/mjanez/ckan-docker)                                      | 2.9.8      | Completed                    | ✔️      | ✔️      | Stable installation (Production & Dev images) via Docker Compose.                                                                                                                                                                                                                                                                                                       |
| Core +      | [~~Datapusher~~](https://github.com/mjanez/ckan-docker)                                     | 0.0.19      | Deprecated                    | ❌      | ❌      | Updated to [xloader](https://github.com/ckan/ckanext-xloader), an express Loader - quickly load data into DataStore.                                                                                                                                |
| Extension   | [ckanext-xloader](https://github.com/ckan/ckanext-xloader)                              | 0.12.2        | Completed                    | ✔️      | ✔️      | Stable installation, a replacement for DataPusher because it offers ten times the speed and more robustness                                                                                                                                                                                                                                                                  |
| Extension   | [ckanext-harvest](https://github.com/ckan/ckanext-harvest)                              | 1.5.1       | Completed                    | ✔️      | ✔️      | Stable installation, necessary for the implementation of the Collector ([ogc_ckan](#recollector-ckan))                                                                                                                                                                                                                                                                  |
| Extension   | [ckanext-geoview](https://github.com/ckan/ckanext-geoview)                              | 0.0.20      | Completed                    | ✔️      | ✔️      | Stable installation.                                                                                                                                                                                                                                                                                                                                                    |
| Extension   | [ckanext-spatial](https://github.com/ckan/ckanext-spatial)                              | 2.0.0       | Completed                    | ✔️      | ✔️      | Stable installation, necessary for the implementation of the Collector ([ogc_ckan](#recollector-ckan))                                                                                                                                                                                                                                                                  |
| Extension   | [ckanext-dcat](https://github.com/mjanez/ckanext-dcat)                                  | 1.2.0       | Completed                    | ✔️      | ✔️      | Stable installation, include DCAT-AP 2.1 profile compatible with GeoDCAT-AP.                                                                                                                                                                                                                                                                                            |
| Extension   | [ckanext-scheming](https://github.com/mjanez/ckanext-scheming)                          | 3.0.0       | WIP                          | ✔️      | ✔️      | Stable installation. Customised ckanext schema[^4] based on the [Spanish Metadata Core](https://datos.gob.es/es/doc-tags/nti-risp) with the aim of completing the minimum metadata elements included in the current datasets in accordance with [GeoDCAT-AP](https://semiceu.github.io/GeoDCAT-AP/releases/) and [INSPIRE](https://inspire.ec.europa.eu/about-inspire). |
| Extension   | [ckanext-resourcedictionary](https://github.com/OpenDataGIS/ckanext-resourcedictionary) | main        | Completed                    | ✔️      | ✔️      | Stable installation. This extension extends the default CKAN Data Dictionary functionality by adding possibility to create data dictionary before actual data is uploaded to datastore.                                                                                                                                                                                 |
| Extension   | [ckanext-pages](https://github.com/ckan/ckanext-pages)                                  | 0.5.1       | Completed                    | ✔️      | ✔️      | Stable installation. This extension gives you an easy way to add simple pages to CKAN.                                                                                                                                                                                                                                                                                  |
| Extension   | [ckanext-pdfview](https://github.com/ckan/ckanext-pdfview)                              | 0.0.8       | Completed                    | ✔️      | ✔️      | Stable installation. This extension provides a view plugin for PDF files using an html object tag.                                                                                                                                                                                                                                                                      |
| Software    | [docker-pycsw](https://github.com/mjanez/ckan-pycsw)                                    | main        | Ready to use standalone version | ✔️      | ❌       | Stable installation. PyCSW Endpoint of Open Data Portal with docker compose config. Harvest the CKAN catalogue in a CSW endpoint based on existing spatial datasets in the open data portal.                                                                                                                                                                            |


## Environment: docker
### docker compose *vs* docker-compose
All Docker Compose commands in this README will use the V2 version of Compose ie: `docker compose`. The older version (V1) used the `docker-compose` command. Please see [Docker Compose](https://docs.docker.com/compose/compose-v2/) for
more information.

### Upgrade docker-engine
To upgrade Docker Engine, first run sudo `apt-get update`, then follow the [installation instructions](https://docs.docker.com/engine/install/debian/#install-using-the-repository), choosing the new version you want to install.

To verify a successful Docker installation, run `docker run hello-world` and `docker version`. These commands should output 
versions for client and server.

### Docker. Basic commands
#### Linux post-install steps
[These optional post-installation procedures](https://docs.docker.com/engine/install/linux-postinstall/) shows you how to configure your Linux host machine to work better with Docker. For example, managing docker with [a non-root user](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user).

#### Configure Docker to start on boot
```bash
sudo systemctl enable docker

# To disable this behavior, use disable instead.
sudo systemctl disable docker
```

#### Clear all Docker unused objects (images, containers, networks, local volumes)
```bash
docker system prune # Clear all

docker image prune # Clear unused images
docker container prune # Clear unused containers
docker volume prune # Clear unused volumes
docker network prune # Clear unused networks
```

### Docker Compose. Basic commands
More info about Docker Compose commands at [docker compose reference](https://docs.docker.com/compose/reference/).

```bash
# Basic. All containers or specific container: <container>
## Starts existing containers for a service.
docker compose start <container>

## Restarts existing containers/container for a service.
docker compose restart <container>

## Stops running containers without removing them.
docker compose stop <container>

## Pauses running containers of a service.
docker compose pause <container>

## Unpauses paused containers of a service.
docker compose unpause <container>

# Display the logs of a container. Is it possible to retrieve only the last n seconds or other
docker logs [--since 60s]  <container> -f 

## Lists containers.
docker compose ps

## Remove all docker compose project
docker compose rm <container>


# Build.
## Builds, (re)creates, starts, and attaches to containers for a service.
docker compose [-f <docker compose-file>] up

## Build & up all the containers.
docker compose [-f <docker compose-file>] up -d --build

## To avoid using a cache of the previous build while creating a new image.
docker compose [-f <docker compose-file>] build --no-cache

## Build a project with a specific Docker Compose prefix.
docker compose [-f <docker compose-file>] -p <my_project> up -d --build


# Down
# Stops containers and removes containers, networks, volumes, and images created by up.
docker compose [-p <my_project>] down
```

## Install (build and run) CKAN plus dependencies
### Base mode
Use this if you are a maintainer and will not be making code changes to CKAN or to CKAN extensions

Copy the included `.env.example` and rename it to `.env`. Modify it depending on your own needs.

>**Note**:<br>
> Please note that when accessing CKAN directly (via a browser) ie: not going through NGINX you will need to make sure you have "ckan" set up to be an alias to localhost in the local hosts file. Either that or you will need to change the `.env` entry for `CKAN_SITE_URL`

>**Warning**:<br>
> Using the default values on the `.env.example` file will get you a working CKAN instance. There is a sysadmin user created by default with the values defined in `CKAN_SYSADMIN_NAME` and `CKAN_SYSADMIN_PASSWORD`(`ckan_admin` and `test1234` by default). This should be obviously changed before running this setup as a public CKAN instance.

Clone project
```shell
cd /path/to/my/project
git clone https://github.com/mjanez/ckan-docker.git
```

To build the images:

	docker compose build

To start the containers:

	docker compose up

This will start up the containers in the current window. By default the containers will log direct to this window with each container
using a different colour. You could also use the -d "detach mode" option ie: `docker compose up -d` if you wished to use the current 
window for something else.

>**Note**<br>
> Or `docker compose up --build` to build & up the containers.

At the end of the container start sequence there should be 6 containers running

![Screenshot 2022-12-12 at 10 36 21 am](https://user-images.githubusercontent.com/54408245/207012236-f9571baa-4d99-4ffe-bd93-30b11c4829e0.png)

After this step, CKAN should be running at `CKAN_SITE_URL`.


### Development mode
Use this mode if you are making code changes to CKAN and either creating new extensions or making code changes to existing extensions. This mode also uses the `.env` file for config options.

To develop local extensions use the `docker compose.dev.yml` file:

To build the images:

	docker compose -f docker-compose.dev.yml build

To start the containers:

	docker compose -f docker-compose.dev.yml up

See [CKAN Images](#ckan-images) for more details of what happens when using development mode.


#### Create an extension
You can use the ckan [extension](https://docs.ckan.org/en/latest/extensions/tutorial.html#creating-a-new-extension) instructions to create a CKAN extension, only executing the command inside the CKAN container and setting the mounted `src/` folder as output:

    docker compose -f docker compose.dev.yml exec ckan-dev /bin/sh -c "ckan generate extension --output-dir /srv/app/src_extensions"
    
![Screenshot 2023-02-22 at 1 45 55 pm](https://user-images.githubusercontent.com/54408245/220623568-b4e074c7-6d07-4d27-ae29-35ce70961463.png)


The new extension files and directories are created in the `/srv/app/src_extensions/` folder in the running container. They will also exist in the local src/ directory as local `/src` directory is mounted as `/srv/app/src_extensions/` on the ckan container. You might need to change the owner of its folder to have the appropiate permissions.


## CKAN images
![ckan images](https://user-images.githubusercontent.com/54408245/207079416-a01235af-2dea-4425-b6fd-f8c3687dd993.png)

The Docker image config files used to build your CKAN project are located in the `ckan/` folder. There are two Docker files:

* `Dockerfile`: this is based on `ckan/ckan-base:<version>`, a base image located in the DockerHub repository, that has CKAN installed along with all its dependencies, properly configured and running on [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) (production setup)
* `Dockerfile.dev`:  this is based on `ckan/ckan-base:<version>-dev` also located located in the DockerHub repository, and extends `ckan/ckan-base:<version>` to include:

  * Any extension cloned on the `src` folder will be installed in the CKAN container when booting up Docker Compose (`docker compose up`). This includes installing any requirements listed in a `requirements.txt` (or `pip-requirements.txt`) file and running `python setup.py develop`.
  * CKAN is started running this: `/usr/bin/ckan -c /srv/app/ckan.ini run -H 0.0.0.0`.
  * Make sure to add the local plugins to the `CKAN__PLUGINS` env var in the `.env` file.


## CKAN images enhancement
### Extending the base images
You can modify the docker files to build your own customized image tailored to your project, installing any extensions and extra requirements needed. For example here is where you would update to use a different CKAN base image ie: `ckan/ckan-base:<new version>`

To perform extra initialization steps you can add scripts to your custom images and copy them to the `/docker-entrypoint.d` folder (The folder should be created for you when you build the image). Any `*.sh` and `*.py` file in that folder will be executed just after the main initialization script ([`prerun.py`](https://github.com/ckan/ckan-docker-base/blob/main/ckan-2.9/base/setup/prerun.py)) is executed and just before the web server and supervisor processes are started.

For instance, consider the following custom image:

```bash
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
FROM ckan/ckan-base:2.9.8-dev

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

```bash
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

>**Note**:<br>
> Git diff is a command to output the changes between two sources inside the Git repository. The data sources can be two different branches, commits, files, etc.
> * Show changes between working directory and staging area:
>   `git diff > [file.patch]`
> * Shows any changes between the staging area and the repository:
>   `git diff --staged [file]`


## ckan-docker addons
### VSCode dev containers
The [Visual Studio Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers) extension is a powerful tool that enables developers to use a container as a complete development environment. With this extension, developers can open any folder inside a container and take advantage of the full range of features provided by Visual Studio Code. To do this, developers create a `devcontainer.json `file in their project that specifies how to access or create a development container with a predefined tool and runtime stack. This allows developers to work in an isolated environment, ensuring that the development environment is consistent across team members and that project dependencies are easy to manage.

![Developing inside a Container](https://code.visualstudio.com/assets/docs/devcontainers/containers/architecture-containers.png)

1. Install [VSCode](https://code.visualstudio.com/).

1. Install the[ Remote Development extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) for VSCode. 

3. In your project directory, create a file named `devcontainer.json.` This file will contain the configuration for your `dev container`.

4. In the `devcontainer.json` file, specify the Docker image that you want to use for your `dev container`. 

5. Specify any additional configuration settings for your `dev container`, such as environment variables, ports to expose, and startup commands.

6. Open your project in a `dev container` by using the Remote Development extension in VSCode. You can do this by clicking the `Open Folder in Container` button in the command palette or by opening the folder using the `Remote-Containers: Open Folder in Container` command. Also you can attach to an active container `Attach to Running Container`.

7. VSCode will start a new container based on the configuration settings in your `devcontainer.json` file. Once the container is started, you can work on your project just like you would on your local machine.


### pdb
Add these lines to the `ckan-dev` service in the docker compose.dev.yml file

![pdb](https://user-images.githubusercontent.com/54408245/179964232-9e98a451-5fe9-4842-ba9b-751bcc627730.png)

Debug with pdb (example) - Interact with `docker attach $(docker container ls -qf name=ckan)`

command: `python -m pdb /usr/lib/ckan/venv/bin/ckan --config /srv/app/ckan.ini run --host 0.0.0.0 --passthrough-errors`


### Datastore and datapusher
The Datastore database and user is created as part of the entrypoint scripts for the db container. There is also a Datapusher container running the latest version of Datapusher.


### NGINX
The base Docker Compose configuration uses an NGINX image as the front-end (ie: reverse proxy). It includes HTTPS running on port number 8443 and an HTTP port (81). A "self-signed" SSL certificate is generated beforehand and the server certificate and key files are included. The NGINX `server_name` directive and the `CN` field in the SSL certificate have been both set to 'localhost'. This should obviously not be used for production.

Creating the SSL cert and key files as follows:
`openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -subj "/C=DE/ST=Berlin/L=Berlin/O=None/CN=localhost" -keyout ckan-local.key -out ckan-local.crt`
The `ckan-local.*` files will then need to be moved into the nginx/setup/ directory


### envvars
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


### ckan-pycsw
[ckan-pycsw](https://github.com/mjanez/ckan-pycsw) is a docker compose environment (based on [pycsw](https://github.com/geopython/pycsw)) for development and testing with CKAN Open Data portals.[^5]

Available components:
* **pycsw**: The pycsw app. An [OARec](https://ogcapi.ogc.org/records) and [OGC CSW](https://opengeospatial.org/standards/cat) server implementation written in Python.
* **ckan2pycsw**: Software to achieve interoperability with the open data portals based on CKAN. To do this, ckan2pycsw reads data from an instance using the CKAN API, generates ISO-19115/ISO-19139 metadata using [pygeometa](https://geopython.github.io/pygeometa/), or a custom schema that is based on a customized CKAN schema, and populates a [pycsw](https://pycsw.org/) instance that exposes the metadata using CSW and OAI-PMH.


[^1]: Contains fields needed for the [ckanext-spatial geo search](https://docs.ckan.org/projects/ckanext-spatial/en/latest/spatial-search.html)
[^2]: Development environment.
[^3]: Production environment.
[^4]: [ckan_geodcatap](https://github.com/mjanez/ckanext-scheming/blob/036b8c6503059e0d42b0eba180d5bd39205c64a3/ckanext/scheming/ckan_geodcatap.yaml), more info: https://github.com/mjanez/ckanext-scheming/pull/1
[^5]: A fork of [COATNor/coat2pycsw](https://github.com/COATnor/coat2pycsw) that has been extended to meet the needs of harvesting GeoDCAT-AP metadata according to INSPIRE ISO19139.
