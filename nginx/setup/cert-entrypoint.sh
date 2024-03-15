#!/bin/sh

export DOMAIN=${DOMAIN}
export EMAIL=${EMAIL}
export SSL_CERT_OPTIONS=${SSL_CERT_OPTIONS}
export LETSENCRYPT_DIR=${LETSENCRYPT_DIR}
export LETSENCRYPT_DRYRUN=${LETSENCRYPT_DRYRUN}

# Ensure we have a folder for the certificates
if [ ! -d /usr/share/nginx/certificates ]; then
    echo "Creating certificate folder"
    mkdir -p /usr/share/nginx/certificates
fi

### If certificates do not exist yet, create self-signed ones before we start nginx
if [ ! -f /usr/share/nginx/certificates/fullchain.pem ]; then
    echo "Generating self-signed certificate"
    openssl genrsa -out /usr/share/nginx/certificates/privkey.pem 4096
    openssl req -new -key /usr/share/nginx/certificates/privkey.pem -out /usr/share/nginx/certificates/cert.csr -nodes -subj \
    "/C=PT/ST=World/L=World/O=$ORGANISATION/CN=$DOMAIN"
    openssl x509 -req -days 365 -in /usr/share/nginx/certificates/cert.csr -signkey /usr/share/nginx/certificates/privkey.pem -out /usr/share/nginx/certificates/fullchain.pem
fi

if [ -n "$DOMAIN" ] && [ "$DOMAIN" != "localhost" ] && [ -n "${SSL_AUTO_CERT}" ] && ${SSL_AUTO_CERT}; then
    ### Send certbot emission/renewal to background
    echo "Scheduling periodic check if certificate should be renewed"
    $(while :; do /opt/request.sh; sleep "${SSL_CERT_RENEW}"; done;) &

    ### Check for changes in the certificate (i.e renewals or first start) in the background
    $(while inotifywait -e close_write /usr/share/nginx/certificates; do echo "Reloading nginx with new certificate"; nginx -s reload; done) &
fi

### Start nginx with daemon off as our main pid
echo "Starting nginx"
nginx -g 'daemon off;'
