#!/bin/sh

#
# /srv/app/check_git.sh
#
# Copied from http://stackoverflow.com/questions/3258243/check-if-pull-needed-in-git
#
# Modified to work with older versions of git (< 2.0.0)
#

# Always fetch before comparing
git fetch

UPSTREAM=${1:-'@{u}'}
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")
BASE=$(git merge-base @ "$UPSTREAM")

if [ $LOCAL = $REMOTE ]; then
    echo "Up-to-date"
elif [ $LOCAL = $BASE ]; then
    echo "Need to pull"
elif [ $REMOTE = $BASE ]; then
    echo "Need to push"
else
    echo "Diverged"
fi