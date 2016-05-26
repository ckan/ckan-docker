_src
====

_Clone your source code here._

<br>

## CKAN

The absolute minimum you need is basic CKAN. Clone CKAN into this directory:

	cd ckan-docker/_src/ # If you're not here already
	git clone https://github.com/ckan/ckan.git

## Extensions

Clone the source code for your extensions here as well.

	git clone https://github.com/cphsolutionslab/ckanext-dataproxy.git

Default extensions that ship with ckan-docker are found in _src/ckan/ckanext. Do not install your own plugins there. If you installed dataproxy, your _src/ckan directory would look like:

	_src (CKAN source code & extensions)
	├── ckan
	└── ckanext-dataproxy
	    ├── ckanext
	    ├── ... (various other files)
	    ├── requirements.txt
	    └── setup.py

## Python dependencies

Pip requirements are installed when the image is built. All you need is a requirement file named `requirements.txt` or `pip-requirements.txt`.

[When booting](https://github.com/ckan/ckan-docker/blob/master/Dockerfile#L44), ckan-docker loops through extensions, installing their `requirements.txt`s and `setup.py`s.

To rebuild the image, run `fig build ckan` (or `fig build --no-cache ckan`), or if you're using the [fig container](https://github.com/ckan/ckan-docker/blob/1750619291e73db6258395a5026ee0b55c1b37de/docker/fig/README.md#using-the-fig-container), you'll run `fig build` within `docker exec`.


## System dependencies

For some extensions, you may need additional system-level dependencies (i.e. Debian packages).

For example, [ckanext-dataproxy](https://github.com/cphsolutionslab/ckanext-dataproxy) requires `build-essentials`, `libmysqlclient-dev`, and `freetds-dev`.

In ckan-docker/Dockerfile, add these dependencies to an apt-get block. Remember to add a ` \` line break after every package name, except the last. For this example (`build-essential` was [specified earlier](https://github.com/ckan/ckan-docker/blob/master/Dockerfile#L19) ):

[ckan-docker/Dockerfile](https://github.com/ckan/ckan-docker/blob/master/Dockerfile#L22)
```sh

RUN DEBIAN_FRONTEND=noninteractive apt-get -qq -y install \
        apache2 \
        libapache2-mod-wsgi \
        postfix \
        git \
        libgeos-c1 \
        supervisor \
        libmysqlclient-dev \
        freetds-dev

```

Rebuild the image after adding system dependencies.

