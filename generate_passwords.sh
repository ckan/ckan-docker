#!/bin/sh

set -a
. ./.env
pwfile=".ckpw"
dbpwfile=".dbpw"
touch ${pwfile} && touch ${dbpwfile}
chmod 600 ${pwfile} && chmod 600 ${dbpwfile}
python3 ./generate_passwords.py
chmod 400 ${pwfile} && chmod 400 ${dbpwfile}
sleep 1