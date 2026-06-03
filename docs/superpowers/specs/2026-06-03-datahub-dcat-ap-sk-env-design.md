# DataHub DCAT-AP-SK Env-Driven Output Design

## Context

The production deployment already exposes CKAN DCAT endpoints such as `/catalog.ttl`, `/catalog.jsonld`, and `/catalog.xml` through `ckanext-dcat`. The current RDF output has the right broad shape for a local catalogue: it includes `dcat:Catalog`, `dcat:Dataset`, `dcat:Distribution`, and dataset/distribution links.

The output is not yet ready for registration or harvesting by `data.slovensko.sk` because several Slovak DCAT-AP-SK values are missing or emitted as plain literals instead of controlled-vocabulary IRIs. The production deployment must keep CKAN as the source of catalogue data while making the exported RDF comply with the expected Slovak metadata shape.

## Goal

Make the production `catalog.ttl` output ready for a Ministry of Education local open-data catalogue by adding an env-configurable DCAT-AP-SK post-processing profile to `ckanext-datahub`.

The deployment must allow ministry-specific values to be changed in `.env` without editing Python code.

## Non-Goals

- Do not replace CKAN's dynamic DCAT endpoint with a static RDF file.
- Do not switch the deployment to a SPARQL endpoint.
- Do not hard-code ministry identifiers or legal terms in the RDF profile implementation.
- Do not change unrelated IDSK test files outside `ckan-docker-prod`.

## Recommended Approach

Add a custom RDF profile named `datahub_dcat_ap_sk` in `ckanext-datahub` and configure it after the existing profiles:

```text
euro_dcat_ap_2 euro_dcat_ap_scheming datahub_dcat_ap_sk
```

The existing `euro_dcat_ap_2` and scheming profiles continue to serialize CKAN packages and resources. The DataHub profile then normalizes the resulting RDF graph for the Slovak profile.

## Environment Configuration

Add these variables to `.env.example` and the generated production `.env`:

```env
DATAHUB_DCAT_PUBLISHER_URI=https://data.gov.sk/id/legal-subject/00164381
DATAHUB_DCAT_PUBLISHER_NAME=Ministerstvo školstva, výskumu, vývoja a mládeže Slovenskej republiky
DATAHUB_DCAT_CONTACT_NAME=DataHub Open Data
DATAHUB_DCAT_CONTACT_EMAIL=opendata@example.gov.sk
DATAHUB_DCAT_DEFAULT_FORMAT_URI=http://publications.europa.eu/resource/authority/file-type/CSV
DATAHUB_DCAT_DEFAULT_MEDIA_TYPE_URI=http://www.iana.org/assignments/media-types/text/csv
DATAHUB_DCAT_TERMS_AUTHORS_WORK_TYPE=https://data.gov.sk/def/authors-work-type/3
DATAHUB_DCAT_TERMS_ORIGINAL_DATABASE_TYPE=https://data.gov.sk/def/original-database-type/3
DATAHUB_DCAT_TERMS_DATABASE_PROTECTED_BY_SPECIAL_RIGHTS_TYPE=https://data.gov.sk/def/codelist/database-creator-special-rights-type/2
DATAHUB_DCAT_TERMS_PERSONAL_DATA_CONTAINMENT_TYPE=https://data.gov.sk/def/personal-data-occurence-type/2
```

The default values target the Ministry of Education, research, development, and youth with IČO `00164381`. The final production server can override all of them in `.env`.

## RDF Requirements

For `dcat:Catalog`, the profile must ensure:

- `dct:publisher` points to `DATAHUB_DCAT_PUBLISHER_URI`.
- The publisher URI is typed as `foaf:Agent`.
- The publisher has `foaf:name` from `DATAHUB_DCAT_PUBLISHER_NAME`.
- Existing `dct:title`, `dct:description`, `foaf:homepage`, and `dcat:dataset` remain intact.

For every `dcat:Dataset`, the profile must ensure:

- `dct:publisher` points to `DATAHUB_DCAT_PUBLISHER_URI`.
- `dcat:keyword` is present, using CKAN tags where available.
- `dcat:contactPoint` is present when contact env values are configured and the dataset lacks a contact.
- Existing `dcat:theme`, `dct:accrualPeriodicity`, `dct:title`, `dct:description`, and `dcat:distribution` remain intact.

For every file-based `dcat:Distribution`, the profile must ensure:

- `dcat:accessURL` remains present.
- `dcat:downloadURL` is present and defaults to the same URI as `dcat:accessURL` when the distribution represents a downloadable file.
- `dct:format` is an IRI from `DATAHUB_DCAT_DEFAULT_FORMAT_URI` for CSV resources instead of a plain literal like `"CSV"`.
- `dcat:mediaType` is an IRI from `DATAHUB_DCAT_DEFAULT_MEDIA_TYPE_URI` for CSV resources instead of a plain literal like `"text/csv"`.
- `leg:termsOfUse` is present with `leg:TermsOfUse` and the four env-configured legal classification IRIs.

## Implementation Shape

Create a small module in `ckanext.datahub` for the profile. It should subclass or use `RDFProfile` and implement:

- `graph_from_catalog`
- `graph_from_dataset`
- no-op `parse_dataset`, unless import behavior is later needed

Register the profile in `setup.py` under the `ckan.rdf.profiles` entry point group.

The production entrypoint must set:

```text
ckanext.dcat.rdf.profiles=euro_dcat_ap_2 euro_dcat_ap_scheming datahub_dcat_ap_sk
```

unless explicitly overridden by `CKANEXT__DCAT__RDF__PROFILES`.

## Validation

Extend `bin/verify-prod` so it parses `catalog.ttl` with `rdflib` inside the CKAN container and checks:

- exactly one or more `dcat:Catalog` entries exist.
- every catalog has `dct:publisher` equal to the configured publisher URI.
- every dataset has `dct:publisher`, `dcat:theme`, `dct:accrualPeriodicity`, `dcat:keyword`, and `dcat:distribution`.
- every distribution has `dcat:accessURL`, `dcat:downloadURL`, `dct:format` as an IRI, `dcat:mediaType` as an IRI, and `leg:termsOfUse`.
- no distribution keeps `dct:format "CSV"` or `dcat:mediaType "text/csv"` as plain literals.

The existing smoke checks for CKAN status, catalogue availability, branding, and site URL warnings remain.

## Risks

The main risk is entry-point ordering. The DataHub profile must run after `euro_dcat_ap_2` and `euro_dcat_ap_scheming`; otherwise it may normalize an incomplete graph. The smoke test will catch this by checking the final RDF output, not just configuration.

Another risk is over-applying CSV defaults to non-CSV resources. The first implementation should normalize resources whose existing format/media type indicates CSV or whose URL ends in `.csv`. Other formats can keep their existing values until format-specific mappings are added.

## Acceptance Criteria

- `catalog.ttl` still responds with HTTP 200 and `text/turtle`.
- `catalog.ttl` contains the ministry publisher URI configured from `.env`.
- the demo dataset contains keywords, theme, frequency, publisher, and distribution.
- the demo CSV distribution contains `downloadURL`, controlled-vocabulary `format`, controlled-vocabulary `mediaType`, and Slovak `termsOfUse`.
- `bash bin/verify-prod` passes after rebuilding the CKAN service.
- the final catalog URL remains `/catalog.ttl`, with production readiness depending on changing `CKAN_SITE_URL` to a public HTTPS URL.
