FROM solr:6.6.6

# Enviroment variables
ENV SOLR_CORE ckan
ENV SOLR_VERSION 6.6.6
ENV CKAN_VERSION 2.9.4
###TODO!!! CKAN_VERSION to be passed in as an ARG

# root user for initial config
USER root

# Create directories
RUN mkdir -p /opt/solr/server/solr/${SOLR_CORE}/conf && \
    mkdir -p /opt/solr/server/solr/${SOLR_CORE}/data && \
    mkdir -p /opt/solr/server/solr/${SOLR_CORE}/data/index

# Add files
COPY solrconfig-${CKAN_VERSION}.xml /opt/solr/server/solr/${SOLR_CORE}/conf/solrconfig.xml
ADD https://raw.githubusercontent.com/ckan/ckan/ckan-${CKAN_VERSION}/ckan/config/solr/schema.xml \
https://raw.githubusercontent.com/apache/lucene-solr/releases/lucene-solr/${SOLR_VERSION}/solr/server/solr/configsets/basic_configs/conf/currency.xml \
https://raw.githubusercontent.com/apache/lucene-solr/releases/lucene-solr/${SOLR_VERSION}/solr/server/solr/configsets/basic_configs/conf/synonyms.txt \
https://raw.githubusercontent.com/apache/lucene-solr/releases/lucene-solr/${SOLR_VERSION}/solr/server/solr/configsets/basic_configs/conf/stopwords.txt \
https://raw.githubusercontent.com/apache/lucene-solr/releases/lucene-solr/${SOLR_VERSION}/solr/server/solr/configsets/basic_configs/conf/protwords.txt \
https://raw.githubusercontent.com/apache/lucene-solr/releases/lucene-solr/${SOLR_VERSION}/solr/server/solr/configsets/data_driven_schema_configs/conf/elevate.xml \
/opt/solr/server/solr/${SOLR_CORE}/conf/

# Create core.properties
RUN echo name=${SOLR_CORE} > /opt/solr/server/solr/${SOLR_CORE}/core.properties

# Giving ownership to Solr
RUN chown -R ${SOLR_USER}:${SOLR_USER} /opt/solr/server/solr/${SOLR_CORE}

# non-root user for runtime
USER ${SOLR_USER}:${SOLR_USER}
