#!/bin/bash

if [[ $CKAN__PLUGINS == *"dsetsearch"* ]]; then

  # Show commands that are run
  set -x

  ckan config-tool --edit ./ckan.ini ckan.auth.public_user_details=false
  ckan config-tool --edit ./ckan.ini ckan.cors.origin_allow_all=true

  # Keep the favicon value unchanged; its config setting differs across CKAN versions.
  ckan config-tool --edit ./ckan.ini ckan.favicon='/NCARfavicon.ico'

  # The harvester doesn't inherit environment variables, so we set the
  # important ones in the config file.
  ckan config-tool --edit ./ckan.ini ckan.site_url="${CKAN_SITE_URL}"
  ckan config-tool --edit ./ckan.ini sqlalchemy.url="${CKAN_SQLALCHEMY_URL}"
  ckan config-tool --edit ./ckan.ini solr_url="${CKAN_SOLR_URL}"
  ckan config-tool --edit ./ckan.ini ckan.redis.url="${CKAN_REDIS_URL}"

  ckan config-tool ./ckan.ini ckanext.dsetsearch.enable_search_format_ui=true
  ckan config-tool ./ckan.ini ckanext.dsetsearch.enable_publisher_facet=true
  ckan config-tool ./ckan.ini ckanext_dsetsearch_banner_message='test'


  ckan config-tool ./ckan.ini ckanext.repo.srcpath=$SRC_DIR
  ckan config-tool ./ckan.ini ckanext.repo.repos='ckan NCAR/ckanext-dsetsearch'

  # NOTE: the CKAN_HARVEST_USERNAME must have admin rights, and belong to the WAF organization,
  # or harvesting will fail with permission errors.
  ckan config-tool ./ckan.ini ckanext.spatial.harvest.user_name=${CKAN_HARVEST_USERNAME}

  # Add configuration toggle for enabling/disabling harvest error email notification
  ckan config-tool ./ckan.ini ckan.harvest.status_mail.errored=true
  ckan config-tool ./ckan.ini ckan.harvest.mq.type=redis
  ckan config-tool ./ckan.ini ckan.harvest.log_scope=1 
  ckan config-tool ./ckan.ini ckan.harvest.log_timeframe=10 
  ckan config-tool ./ckan.ini ckan.harvest.log_level=info
  ckan config-tool ./ckan.ini ckan.harvest.timeout=360       # Six hours

  ckan config-tool ./ckan.ini ckanext.spatial.search_backend=solr-spatial-field
  ckan config-tool ./ckan.ini ckanext.spatial.use_postgis_sorting=false
  ckan config-tool ./ckan.ini ckan.spatial.validator.profiles='iso19139, dset-minimum-fields-production, geographic-extent-validator, temporal-extent-validator, collections-validator'
  ckan config-tool ./ckan.ini ckanext.spatial.common_map.type=custom 
  ckan config-tool ./ckan.ini ckanext.spatial.common_map.custom.url='https://tile.openstreetmap.org/{z}/{x}/{y}.png'
  ckan config-tool ./ckan.ini ckanext.spatial.common_map.attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  ckan config-tool --edit ./ckan.ini error_email_from=donotreply@ucar.edu

  #  These settings are subject to change, depending on the deployment
  ckan config-tool --edit ./ckan.ini ckan.site_title='DASH Search (Development)'
  ckan config-tool --edit ./ckan.ini ckan.site_description='NCAR data search and discovery'

  ckan config-tool ./ckan.ini googleanalytics.id="${CKAN_GOOGLEANALYTICS_ID}"
  ckan config-tool ./ckan.ini googleanalytics.account="${CKAN_GOOGLEANALYTICS_ACCOUNT}"
  ckan config-tool ./ckan.ini googleanalytics.username="${CKAN_GOOGLEANALYTICS_USERNAME}"
  ckan config-tool ./ckan.ini googleanalytics.password="${CKAN_GOOGLEANALYTICS_PASSWORD}"

  # Change Solr query parser to allow point location queries
  #sed -i "s|ckan.search.solr_allowed_query_parsers = |ckan.search.solr_allowed_query_parsers = field|" /etc/ckan/default/ckan.ini
  #ckan config-tool --edit ./ckan.ini ckan.search.solr_allowed_query_parsers=field

  # Allow the harvest user to create collections (groups in CKAN) at harvest time (MAY BE UNNEEDED).
  # sed -i "s|ckan.auth.user_create_groups = false|ckan.auth.user_create_groups = true|" /etc/ckan/default/ckan.ini


  # Update Email Notification settings in [app:main] section

#  ckan config-tool --edit ./ckan.ini email_to=yourEmail@ucar.edu
#  ckan config-tool --edit ./ckan.ini smtp.server=smtp.gmail.com:587
#  ckan config-tool --edit ./ckan.ini smtp.starttls=True
#  ckan config-tool --edit ./ckan.ini smtp.user=yourEmail@ucar.edu
#  ckan config-tool --edit ./ckan.ini smtp.password=your_CIT_Password
#  ckan config-tool --edit ./ckan.ini smtp.mail_from=vagrant-ckan@ucar.edu
fi