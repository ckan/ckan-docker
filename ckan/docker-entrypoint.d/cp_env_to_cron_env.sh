# SPDX-FileCopyrightText: Stichting Health-RI
#
# SPDX-License-Identifier: AGPL-3.0-only

#!/bin/sh

# Dump environment variables to a file that will be sourced by cron
printenv | sed 's/^\(.*\)$/export \1/g' > /etc/profile.d/custom_env.sh
