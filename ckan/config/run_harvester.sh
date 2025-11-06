#!/bin/bash
 
##################################
# /srv/app/run_harvester.sh
##################################
export PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/srv/app/.local/bin

set -x

WAF_FOLDER='/var/www/html/'
MARK_JOBS_FINISHED='/usr/local/bin/ckan -c /srv/app/ckan.ini harvester run'

# Try marking any jobs as finished before looking for hung jobs.
# NOTE: we can't do this for long-running jobs without causing strange behavior in the harvest queue.
# This can only be done safely if the job is finished running and fetch_consumer.log output has stopped.
$MARK_JOBS_FINISHED


directories=$( ls -d $WAF_FOLDER*/ )

for directory in $directories; do
    cd $directory
    git remote update

    unset changed
    /srv/app/check_git.sh | grep -q -v 'Up-to-date' && changed=1


    # Update local git repository of metadata records.
    if [ -n "$changed" ]; then
        git pull

        WAF_NAME=`basename $directory`

        # Trigger harvesting for this harvest source.
        /usr/local/bin/ckan -c /srv/app/ckan.ini harvester job ${WAF_NAME}

    fi
done

# Wait for fetch_consumer.log to stop growing
logsize=`wc /var/log/ckan/std/fetch_consumer.log | awk '{print $1;}'`
logsize_old=-1
while [ "$logsize" '!=' "$logsize_old" ]; do
    sleep 30
    logsize_old=$logsize
    logsize=`wc /var/log/ckan/std/fetch_consumer.log | awk '{print $1;}'`
    echo "logsize == $logsize; logsize_old == $logsize_old"
done

# Mark running jobs as finished
$MARK_JOBS_FINISHED