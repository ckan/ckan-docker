This folder contains an initial Python script to sync and cache datasets from the CKAN API.

## Background

In order to bulk-add datasets to the NADIT instance we are using CKAN's API to federate metadata from opendata.swiss. 

The mechanism in this harvester promotes the publication of metadata in public, and may include references to non-open data sources, such as the complete BFS catalog of on-request-only publications.

Additional references:

- https://git.fhgr.ch/resto/harvester/-/issues/1
- https://github.com/ckan/ckanext-harvest
- https://github.com/ckan/ckanext-dcat/issues/227
- https://github.com/liip/ckanext-dcat_switzerland (see [blog post](https://www.liip.ch/en/blog/the-role-of-ckan-in-our-open-data-projects))
- https://difi.github.io/dcat-harvester/
