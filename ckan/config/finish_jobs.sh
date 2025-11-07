#!/bin/bash

##################################
# /srv/app/finish_jobs.sh
##################################
export PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/srv/app/.local/bin

set -x

date

/usr/local/bin/ckan -c /srv/app/ckan.ini harvester run
