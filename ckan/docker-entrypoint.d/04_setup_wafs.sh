
# Add WAF for spatial harvesting

if [[ $CKAN__PLUGINS == *"spatial"* ]]; then

  # Add API token to admin user, so we can create an Organization, thereby allowing creation of a WAF.
#  if [ ! -d "/tmp/apikey.txt" ]; then
#      ckan -c ~/ckan.ini user token add ckan_admin api-token | tail -1 | xargs > /tmp/apikey.txt
#      apiKey=`cat /tmp/apikey.txt`
#      wget -O /tmp/responseOrg.json --header="Authorization: ${apiKey}" --post-data='{"name": "ncar", "title": "NCAR"}' 'http://localhost:5000/api/3/action/organization_create'
#  fi

  # Add API token to admin user, so we can create an Organization, thereby allowing creation of a WAF.
  # NOTE: The application is not always ready for HTTP requests at this point, so we avoid using the action API.
  if [ ! -d "/tmp/apikey.txt" ]; then
      ckan -c ~/ckan.ini user token add ckan_admin api-token | tail -1 | xargs > /tmp/apikey.txt
      pip install ckanapi
      /srv/app/.local/bin/ckanapi action organization_create name=ncar title=NCAR
  fi

  set -x
  cd /var/www/html
  rm -rf *
  # Create web-accessible folder structure
  if [ ! -d "/var/www/html/dset-web-accessible-folder-dev" ]; then
      cd /var/www/html

      ## Commands for dev-waf
      git clone https://github.com/NCAR/dset-web-accessible-folder-dev.git
      cd dset-web-accessible-folder-dev
      git fetch
      ckan -c ~/ckan.ini harvester source create "dev-waf2" "http://nginx:9000/dset-web-accessible-folder-dev" "waf" "DEV WAF2" "TRUE" "ncar" "MANUAL" '{"user" : "ckan_admin", "read_only": true}'


      ## Commands for mini-waf
      #git clone https://github.com/NCAR/sagedev-dset-harvest-test.git
      #cd sagedev-dset-harvest-test
      #git fetch
      #ckan -c ~/ckan.ini harvester source create "mini-waf" "http://nginx:9000/sagedev-dset-harvest-test" "waf" "MINI WAF" "TRUE" "ncar" "MANUAL" '{"user" : "ckan_admin", "read_only": true}'

      # We can't run this command right away, because nginx has not started up yet.
      #ckan -c ~/ckan.ini harvester run-test mini-waf
  fi

fi
