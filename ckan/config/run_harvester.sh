#!/bin/bash
 
##################################
# /srv/app/run_harvester.sh
##################################

set -x

WAF_FOLDER='/var/www/html/'

ABORT_FAILED_JOBS='/usr/local/bin/ckan -c /srv/app/ckan.ini harvester abort-failed-jobs'


# Try aborting any hung harvest jobs.  We need to resync with the DB after a DB server timeout.
$ABORT_FAILED_JOBS


directories=$( ls -d $WAF_FOLDER*/ )

for directory in $directories; do
    cd $directory
    git remote update

    unset changed
    /srv/app/check_git.sh | grep -q -v 'Up-to-date' && changed=1

    # Update local git repository of metadata records.
    git pull

    if [ -n "$changed" ]; then

        WAF_NAME=`basename $directory`

        # Trigger harvesting for this harvest source.
        /usr/local/bin/ckan -c /srv/app/ckan.ini harvester job ${WAF_NAME}

    fi
done
