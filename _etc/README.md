_etc
====

_This directory contains configuration files that are copied to /etc in the container when the Docker file is built, and when a child is built._


## Customisation

- Apache config
- CKAN config
	- You can specify custom options in the custom_options.ini file, they will be applied to the default ini file.
	- or override the default (generated) config with a volume
	- filenames (of the config & custom_options file) can be overriden with environment variables
- Cron jobs
- Postfix config
- Supervisor managed processes

_Ngnix is not installed in the CKAN container anymore. Use the official Ngnix container, or a custom built container instead_

- Nginx conf is stored in this folder for consistency.
- The default config uses "ckan" as a hostname, the corresponding IP address is resolved by linking the ckan container, which adds an entry in `/etc/hosts` inside the container.
Make sure you link your CKAN container as `my_ckan:ckan` or change the config.

## Usage

### Building the CKAN image
_i.e. This docker file_

This will copy the files using the [Docker `ADD` instruction](https://docs.docker.com/reference/builder/#add)

### Building a child image
_i.e. A different Docker from the CKAN image (downstream build)_


This will override the files using the [Docker `ONBUILD` instruction](https://docs.docker.com/reference/builder/#onbuild)

This means that when building a child image, you should have the same directory structure.
