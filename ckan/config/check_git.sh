#!/bin/sh

#
# /srv/app/check_git.sh
#
# Copied from http://stackoverflow.com/questions/3258243/check-if-pull-needed-in-git
#
# Modified to work with older versions of git (< 2.0.0)
#

LOCAL=$(git rev-parse @{0})
REMOTE=$(git rev-parse @{u})
BASE=$(git merge-base @{0} @{u})

if [ $LOCAL = $REMOTE ]; then
    echo "Up-to-date"
elif [ $LOCAL = $BASE ]; then
    echo "Need to pull"
elif [ $REMOTE = $BASE ]; then
    echo "Need to push"
else
    echo "Diverged"
fi
