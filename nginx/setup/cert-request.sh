#!/bin/sh

if [ ! -f /var/www/html ]; then
    mkdir -p /var/www/html
fi
 
if [ -n "$DOMAIN" ] && [ "$DOMAIN" != "localhost" ]; then
	certbot certonly \
			--config-dir ${LETSENCRYPT_DIR} ${LETSENCRYPT_DRYRUN} \
			--agree-tos \
			--domains "$DOMAIN" \
			--email $EMAIL \
			--expand \
			--noninteractive \
			--webroot \
			--webroot-path /var/www/html \
			$SSL_CERT_OPTIONS || true

	if [ -f ${LETSENCRYPT_DIR}/live/$DOMAIN/privkey.pem ]; then
		chmod +rx ${LETSENCRYPT_DIR}/live
		chmod +rx ${LETSENCRYPT_DIR}/archive
		chmod +r  ${LETSENCRYPT_DIR}/archive/${DOMAIN}/fullchain*.pem
		chmod +r  ${LETSENCRYPT_DIR}/archive/${DOMAIN}/privkey*.pem
		cp ${LETSENCRYPT_DIR}/live/$DOMAIN/privkey.pem /usr/share/nginx/certificates/privkey.pem
		cp ${LETSENCRYPT_DIR}/live/$DOMAIN/fullchain.pem /usr/share/nginx/certificates/fullchain.pem
		echo "Copied new certificate to /usr/share/nginx/certificates"
	fi
fi
