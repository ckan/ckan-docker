# DataHub DCAT-AP-SK 3.0 Documents Design

## Context

The production deployment in `ckan-docker-prod` already exposes CKAN RDF endpoints through `ckanext-dcat`:

- `/catalog.ttl`
- `/dataset/{dataset-id}.ttl`

The current output is close to a valid local open-data catalog, but it still reflects DCAT-AP v2 configuration and misses several Slovak DCAT-AP-SK 3.0 document-interface expectations. The attached validation notes show concrete issues in the generated RDF: Slovak text literals do not have `@sk`, `dct:spatial` is missing, the catalog dataset links are not the intended dataset detail document URLs, and the verifier does not yet validate individual dataset Turtle documents.

Official DCAT-AP-SK 3.0 documentation describes the document interface as a catalog file containing a `dcat:Catalog` with `dcat:dataset` links. When the national catalog opens those dataset URLs, it expects complete RDF dataset records including their distributions and data services. Dataset, distribution, and data service resources must be IRIs, not RDF blank nodes.

Sources:

- https://github.com/slovak-egov/centralny-model-udajov/blob/develop/tbox/national/dcat-ap-sk/index.html
- https://raw.githubusercontent.com/slovak-egov/centralny-model-udajov/develop/tbox/national/dcat-ap-sk/index.html
- https://docs.ckan.org/projects/ckanext-dcat/en/latest/endpoints/
- https://docs.ckan.org/projects/ckanext-dcat/en/latest/profiles/

## Goal

Make the CKAN production package generate DCAT-AP-SK 3.0 compatible RDF documents for Slovak open-data harvesting:

- the catalog endpoint remains `/catalog.ttl`;
- every catalog `dcat:dataset` value points to the dataset detail RDF document, for example `/dataset/testovaci-zoznam-skol.ttl`;
- the dataset detail endpoint returns a complete dataset record with dataset metadata, contact point, spatial coverage, distribution metadata, and legal terms;
- all deployment-specific values continue to come from `.env` where practical.

## Non-Goals

- Do not replace CKAN with a static catalog generator.
- Do not add a SPARQL endpoint.
- Do not attempt full HVD dataset support in this pass.
- Do not add unrelated UI or IDSK design changes.
- Do not make `localhost` production-ready; `CKAN_SITE_URL` must still be changed to a public HTTPS URL before registration.

## Recommended Approach

Keep using `ckanext-dcat` and extend the existing `datahub_dcat_ap_sk` RDF profile.

Use the CKAN profile chain:

```text
euro_dcat_ap_3 euro_dcat_ap_scheming datahub_dcat_ap_sk
```

`euro_dcat_ap_3` provides the DCAT-AP 3 base mapping. `euro_dcat_ap_scheming` keeps current CKAN scheming field support. `datahub_dcat_ap_sk` remains the final graph normalizer for Slovak-specific requirements and env-driven ministry metadata.

This is preferred over a custom serializer because CKAN and `ckanext-dcat` already provide the catalog and dataset RDF endpoints, format negotiation, and stable extension points for custom RDF profiles.

## RDF Shape

### Catalog Document

`/catalog.ttl` must contain one `dcat:Catalog` resource with:

- `dct:title` as an `rdf:langString` with `@sk`;
- `dct:description` as an `rdf:langString` with `@sk`;
- `dct:publisher` equal to `DATAHUB_DCAT_PUBLISHER_URI`;
- `foaf:homepage` as an IRI;
- `dcat:contactPoint` with a `vcard:Organization`, `vcard:fn` as `@sk`, and `vcard:hasEmail`;
- `dcat:dataset` links to dataset detail documents, not only CKAN internal dataset UUID pages.

For the local demo this means a catalog dataset link like:

```turtle
<http://localhost:5000> a dcat:Catalog ;
    dcat:dataset <http://localhost:5000/dataset/testovaci-zoznam-skol.ttl> .
```

On a server, `CKAN_SITE_URL` changes this to the public HTTPS host.

### Dataset Document

`/dataset/{name}.ttl` must contain a complete `dcat:Dataset` record with:

- dataset subject IRI equal to the dataset detail document URL;
- `dct:title` and `dct:description` as `@sk`;
- `dct:publisher` equal to `DATAHUB_DCAT_PUBLISHER_URI`;
- optional `dct:issued` and `dct:modified` as `xsd:dateTime` when CKAN provides dates;
- `dcat:theme` as an IRI from the EU data-theme authority;
- `dct:accrualPeriodicity` as an IRI from the EU frequency authority;
- `dcat:keyword` values as `@sk`;
- `dct:spatial` with the default Slovak coverage `https://data.gov.sk/id/nuts1/SK0`;
- `dct:type` with default dataset type `https://data.gov.sk/def/dataset-type/1`;
- `dcat:contactPoint` with Slovak-labeled contact information;
- `dcat:landingPage` pointing to the human CKAN dataset page;
- `dcat:distribution` links to complete distribution resources.

### Distribution Resources

For file-based resources, each `dcat:Distribution` must have:

- an IRI resource subject, not a blank node;
- `dct:title` as `@sk` when present;
- `dct:description` as `@sk` when present;
- `dcat:accessURL`;
- `dcat:downloadURL`;
- `dcat:accessURL` equal to `dcat:downloadURL` for a downloadable file;
- `dct:format` as an IRI;
- `dcat:mediaType` as an IRI;
- exactly one `leg:termsOfUse` blank node with the four configured legal classification IRIs.

CSV resources keep:

```text
DATAHUB_DCAT_DEFAULT_FORMAT_URI=http://publications.europa.eu/resource/authority/file-type/CSV
DATAHUB_DCAT_DEFAULT_MEDIA_TYPE_URI=http://www.iana.org/assignments/media-types/text/csv
```

Non-CSV resources must not be forced to CSV values.

## Environment Configuration

Keep existing env values and add these:

```env
DATAHUB_DCAT_CATALOG_TITLE=DataHub Open Data
DATAHUB_DCAT_CATALOG_DESCRIPTION=Katalóg otvorených dát
DATAHUB_DCAT_DEFAULT_LANGUAGE=sk
DATAHUB_DCAT_DEFAULT_SPATIAL_URI=https://data.gov.sk/id/nuts1/SK0
DATAHUB_DCAT_DEFAULT_DATASET_TYPE_URI=https://data.gov.sk/def/dataset-type/1
```

Existing values remain:

```env
DATAHUB_DCAT_PUBLISHER_URI=https://data.gov.sk/id/legal-subject/00164381
DATAHUB_DCAT_PUBLISHER_NAME=Ministerstvo školstva, výskumu, vývoja a mládeže Slovenskej republiky
DATAHUB_DCAT_CONTACT_NAME=DataHub Open Data tím
DATAHUB_DCAT_CONTACT_EMAIL=opendata@example.gov.sk
DATAHUB_DCAT_DEFAULT_FORMAT_URI=http://publications.europa.eu/resource/authority/file-type/CSV
DATAHUB_DCAT_DEFAULT_MEDIA_TYPE_URI=http://www.iana.org/assignments/media-types/text/csv
DATAHUB_DCAT_TERMS_AUTHORS_WORK_TYPE=https://data.gov.sk/def/authors-work-type/3
DATAHUB_DCAT_TERMS_ORIGINAL_DATABASE_TYPE=https://data.gov.sk/def/original-database-type/3
DATAHUB_DCAT_TERMS_DATABASE_PROTECTED_BY_SPECIAL_RIGHTS_TYPE=https://data.gov.sk/def/codelist/database-creator-special-rights-type/2
DATAHUB_DCAT_TERMS_PERSONAL_DATA_CONTAINMENT_TYPE=https://data.gov.sk/def/personal-data-occurence-type/2
```

## Implementation Notes

The implementation should stay scoped to `ckan-docker-prod`.

Expected file changes:

- `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/dcat_ap_sk.py`
- `ckan-docker-prod/ckan/docker-entrypoint.d/02_setup_prod_config.sh`
- `ckan-docker-prod/.env.example`
- `ckan-docker-prod/docker-compose.yml`
- `ckan-docker-prod/bin/verify-prod`
- `ckan-docker-prod/bin/seed-demo-data`
- `ckan-docker-prod/README.md`

The RDF profile should:

- bind useful namespaces including `leg`, `dcatap`, `filetype`, `freq`, `theme`, and `text`;
- replace plain literals for Slovak text metadata with `Literal(value, lang="sk")`;
- avoid duplicate untyped and language-tagged versions of the same title/description/keyword;
- normalize the catalog subject and dataset subject to the document interface URLs;
- preserve CKAN-generated dates, resource URLs, byte size, and existing controlled-vocabulary IRIs where valid;
- add missing defaults only when CKAN does not provide a value.

## Validation

`bin/verify-prod` must parse both:

- `http://localhost:5000/catalog.ttl`
- `http://localhost:5000/dataset/testovaci-zoznam-skol.ttl`

The verifier must fail if:

- catalog title or description is missing `@sk`;
- catalog dataset links do not end with `.ttl`;
- a dataset detail document lacks `dcat:Dataset`;
- dataset title, description, or keyword lacks `@sk`;
- dataset lacks `dct:spatial`;
- dataset lacks `dct:type`;
- dataset lacks `dcat:landingPage`;
- distribution title or description is present without `@sk`;
- a CSV distribution keeps literal `"CSV"` or `"text/csv"`;
- a non-CSV distribution is forced to CSV defaults.

The existing checks for publisher, legal terms, `downloadURL`, configuration, branding, and localhost warnings remain.

## Demo Data

Update the demo seed so that the visible CKAN data and RDF are Slovak, not ASCII fallback text:

- dataset title: `Testovací zoznam škôl`;
- dataset description: `Syntetický testovací dataset s 10 školami na overenie publikovania CSV zdroja a DCAT katalógu.`;
- tags: `demo`, `školy`, `vzdelávanie`;
- resource title: `Zoznam škôl - demo CSV`;
- resource description: `Syntetický CSV súbor s 10 demo školami.`;
- contact name: `DataHub Open Data tím`.

The dataset slug can remain `testovaci-zoznam-skol` so local URLs stay stable.

## Acceptance Criteria

- `CKANEXT__DCAT__RDF__PROFILES` defaults to `euro_dcat_ap_3 euro_dcat_ap_scheming datahub_dcat_ap_sk`.
- `/catalog.ttl` returns a `dcat:Catalog` with Slovak language-tagged title and description.
- `/catalog.ttl` links the demo dataset as `/dataset/testovaci-zoznam-skol.ttl`.
- `/dataset/testovaci-zoznam-skol.ttl` returns a complete `dcat:Dataset` with `@sk` text metadata, publisher, theme, frequency, keywords, spatial coverage, dataset type, contact point, landing page, and distribution.
- The demo CSV distribution has `accessURL`, `downloadURL`, controlled-vocabulary CSV format/media type IRIs, `@sk` title/description, byte size when CKAN provides it, and `leg:termsOfUse`.
- `bash bin/verify-prod` passes after rebuilding the CKAN service and reseeding demo data.
- The README documents both required URLs: `/catalog.ttl` for the catalog and `/dataset/{dataset-name}.ttl` for each dataset detail document.

## Risks

`ckanext-dcat` may still emit Hydra paging metadata on `/catalog.ttl`. The Slovak document-interface examples do not require Hydra, but the current CKAN endpoint includes it. The first implementation should not try to remove Hydra unless it breaks validation, because it is emitted by the upstream endpoint and is separate from the catalog/dataset RDF shape.

The document-interface requirement says dataset, distribution, and data service resources must be IRIs, while `leg:termsOfUse` examples use a blank node. The implementation will keep `leg:termsOfUse` as a blank node because the SHACL shape expects a `leg:TermsOfUse` node and the official examples use blank nodes for legal terms.

Localhost output is acceptable only for local testing. The deployment remains not registerable until `CKAN_SITE_URL` and `CKAN__SITE_URL` are changed to a public HTTPS URL reachable from the national portal.
