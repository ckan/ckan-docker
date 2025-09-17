#!/bin/bash

##################################
# /srv/app/finish_jobs.sh
##################################

set -x

/usr/local/bin/ckan -c /srv/app/ckan.ini harvester run
