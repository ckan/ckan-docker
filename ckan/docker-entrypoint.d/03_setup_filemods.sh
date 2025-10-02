#!/bin/bash
  
  # Run 'git fetch' on each plugin; needed by repo_info plugin
  cd $SRC_DIR
  for dir in ckan*; do
     cd $dir
     echo "Running git fetch on $dir"
     git fetch
     cd ..
  done
  cd ..

  # Create directory structure expected by repo-info
  if [ ! -d "$SRC_DIR/NCAR" ]; then
     echo "Creating linked directory NCAR/ckanext-dsetsearch"
     cd $SRC_DIR
     mkdir NCAR
     cd NCAR
     ln -s $SRC_DIR/ckanext-dsetsearch .
     cd
  fi

  # Provide library needed by Google Analytics plugin
  if [[ $CKAN__PLUGINS == *"googleanalytics"* ]]; then
       pip install oauth2client==4.1.3
  fi

  # Initialize the harvester DB tables
  if [[ $CKAN__PLUGINS == *"harvest"* ]]; then
       ckan -c ~/ckan.ini db upgrade -p harvest
  fi

  # Use custom Solr schema for DASH Search
  # Link in our modified Solr schema file to be used for solr.
  cd $SRC_DIR/ckan/ckan/config/solr/
  mv schema.xml schema.xml.ORIG_INSTALLED
  ln -sf $SRC_DIR/ckanext-dsetsearch/solr/schema.solr-spatial-2.0.xml schema.xml



  
