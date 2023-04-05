#!/bin/sh

# Add ckan.datapusher.api_token to the CKAN config file (updated with corrected value later)
ckan config-tool $CKAN_INI ckan.datapusher.api_token=xxx

# Set up the Secret key used by Beaker and Flask
# This can be overriden using a CKAN___BEAKER__SESSION__SECRET env var
if grep -E "beaker.session.secret ?= ?$" ckan.ini
then
    echo "Setting beaker.session.secret in ini file"
    ckan config-tool $CKAN_INI "beaker.session.secret=$(python3 -c 'import secrets; print(secrets.token_urlsafe())')"
    ckan config-tool $CKAN_INI "WTF_CSRF_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe())')"
    JWT_SECRET=$(python3 -c 'import secrets; print("string:" + secrets.token_urlsafe())')
    ckan config-tool $CKAN_INI "api_token.jwt.encode.secret=${JWT_SECRET}"
    ckan config-tool $CKAN_INI "api_token.jwt.decode.secret=${JWT_SECRET}"
fi

# Run the prerun script to init CKAN and create the default admin user
sudo -u ckan -EH python3 prerun.py

echo "Set up ckan.datapusher.api_token in the CKAN config file"
ckan config-tool $CKAN_INI "ckan.datapusher.api_token=$(ckan -c $CKAN_INI user token add ckan_admin datapusher | tail -n 1 | tr -d '\t')"

# Run any startup scripts provided by images extending this one
if [[ -d "/docker-entrypoint.d" ]]
then
    for f in /docker-entrypoint.d/*; do
        case "$f" in
            *.sh)     echo "$0: Running init file $f"; . "$f" ;;
            *.py)     echo "$0: Running init file $f"; python3 "$f"; echo ;;
            *)        echo "$0: Ignoring $f (not an sh or py file)" ;;
        esac
        echo
    done
fi

# Set the common uwsgi options
UWSGI_OPTS="--plugins http,python \
            --socket /tmp/uwsgi.sock \
            --wsgi-file /srv/app/wsgi.py \
            --module wsgi:application \
            --uid 92 --gid 92 \
            --http 0.0.0.0:5000 \
            --master --enable-threads \
            --lazy-apps \
            -p 2 -L -b 32768 --vacuum \
            --harakiri $UWSGI_HARAKIRI"

if [ $? -eq 0 ]
then
    # Start supervisord
    supervisord --configuration /etc/supervisord.conf &
    # Start uwsgi
    sudo -u ckan -EH uwsgi $UWSGI_OPTS
else
  echo "[prerun] failed...not starting CKAN."
fi
