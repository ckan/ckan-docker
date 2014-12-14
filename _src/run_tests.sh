#!/bin/bash
set -e

. $CKAN_HOME/bin/activate

echo "Installing test dependencies"

cd $CKAN_HOME/src/
for package in *
do
  if [ -d "$package" ]; then
    cd $package
    # install dev requirements
    if [ -f "dev-requirements.txt" ]; then
      $CKAN_HOME/bin/pip install -r dev-requirements.txt
    elif [ -f "pip-requirements-test.txt" ]; then
      $CKAN_HOME/bin/pip install -r pip-requirements-test.txt
    fi
    cd ..
  fi
done


echo "Configuring dynamic URLs"
$CKAN_HOME/bin/paster --plugin=ckan config-tool $CKAN_HOME/src/ckan/test-core.ini -e \
  "sqlalchemy.url           = postgresql://ckan_default:pass@postgres:5432/ckan_test" \
  "solr_url                 = http://solr:8983/solr/ckan" \
  "ckan.datastore.write_url = postgresql://ckan_default:pass@postgres:5432/datastore_test" \
  "ckan.datastore.read_url  = postgresql://datastore_default:pass@postgres:5432/datastore_test" \
  "ckan.datapusher.url      = http://datapusher:8800/"

echo "Running Nose tests"

cd ckan
nosetests --ckan --reset-db --with-pylons=test-core.ini --nologcapture --with-coverage ckan ckanext
cd ..

