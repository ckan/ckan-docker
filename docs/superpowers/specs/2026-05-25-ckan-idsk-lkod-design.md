# CKAN IDSK LKOD Portal Design

Date: 2026-05-25

## Goal

Build one open data portal for one institution, currently the Ministry of Education context in this repository. The portal should let an authenticated user publish open data through a simple CKAN-backed workflow and expose a harvestable DCAT/LKOD link suitable for registration on data.slovensko.sk.

The target experience is:

1. User logs in.
2. User adds a dataset through an IDSK-styled publishing flow.
3. Dataset is assigned to one default organization.
4. User uploads a file or provides a resource URL.
5. CKAN stores the dataset and resource.
6. The portal shows public dataset links and the catalog DCAT link.
7. An administrator registers the catalog link on data.slovensko.sk.

This is not a multi-tenant portal in the current phase. Organization creation is an administrative setup task, not a normal publishing step.

## Current State

The project runs CKAN 2.11.5 in Docker Compose with PostgreSQL, Solr, Redis, DataPusher, nginx, and the following active CKAN extensions:

- image_view
- text_view
- datatables_view
- datastore
- datapusher
- envvars
- dcat
- dcat_json_interface
- structured_data
- idsk_theme

The custom `ckanext-idsk` extension currently registers template and public directories only. It includes IDSK frontend CSS assets and overrides a small set of templates:

- base
- header
- footer
- home/index

The current platform is only partially IDSK:

- IDSK CSS is served.
- Header, footer, and homepage use IDSK/GOVUK-style classes.
- CKAN workflow pages such as login, dataset forms, organization pages, resource upload, breadcrumbs, and errors still use default CKAN/Bootstrap markup.
- Header and footer reference missing SVG logo files, causing 404s.
- Some Slovak text in configuration and templates appears mojibake-corrupted.

The current DCAT state is a useful base:

- `ckanext-dcat` is installed.
- `/catalog.ttl` responds.
- The current catalog export is empty because there are no datasets yet.
- `CKANEXT_DCAT_RDF_PROFILES=euro_dcat_ap_2` is configured in `.env`.

The current implementation is not yet a complete DCAT-AP-SK LKOD implementation. `euro_dcat_ap_2` is close to European DCAT-AP 2.x, but the Slovak profile needs explicit fields, controlled vocabularies, and validation.

## Design Direction

Use CKAN as the backend and extend `ckanext-idsk` into a full IDSK publishing portal.

Do not build a separate frontend in this phase. CKAN already provides authentication, users, organizations, datasets, resources, file storage, DataStore, DataPusher, and DCAT endpoints. A separate frontend would add avoidable authentication, API, state, and maintenance complexity before the core metadata workflow is proven.

## Functional Scope

### Default Organization

The portal has one configured default publishing organization.

Implementation should provide one of these mechanisms:

- A configuration setting such as `ckanext.idsk.default_organization`.
- A startup/admin script that creates the organization if missing.
- Validation that prevents publishing if the default organization does not exist.

Normal users should not need to create or choose organizations during the first version of the publishing workflow.

### Publishing Workflow

The core workflow should be a simplified IDSK wizard or guided form:

1. Dataset metadata
   - title
   - description
   - keywords
   - theme
   - update frequency
   - license
   - contact point
   - temporal coverage where applicable
   - spatial coverage where applicable

2. Resource
   - upload file, or
   - external URL
   - resource title
   - format
   - description

3. Review
   - show entered metadata
   - show any missing required DCAT-AP-SK fields
   - allow save as draft if draft support is implemented
   - publish only when required metadata is valid

4. Published links
   - public dataset page
   - dataset RDF, for example `/dataset/<name>.ttl`
   - catalog RDF, for example `/catalog.ttl`

### Uploads

File upload must be verified end to end:

- CKAN must accept resource uploads.
- Uploaded files must be persisted in Docker volume-backed CKAN storage.
- Public download URLs must be stable.
- DataPusher/DataStore behavior must be tested for CSV resources.

Current `.env` contains upload-related variables, but runtime `ckan.ini` should be checked and corrected because `ckan.uploads_enabled` appears blank in the running container.

### DCAT/LKOD Export

The first public LKOD target should be a DCAT document endpoint, not SPARQL.

Primary link:

- `/catalog.ttl`

Useful supporting links:

- `/catalog.rdf`
- `/catalog.jsonld`
- `/dataset/<dataset-name>.ttl`

The export must include datasets and distributions with stable IRIs. The site URL must be the real production HTTPS domain before registration on data.slovensko.sk. `localhost` is acceptable only for local development.

### DCAT-AP-SK Metadata

The portal should add a Slovak metadata schema on top of CKAN's default dataset model. The recommended implementation is `ckanext-scheming` plus a custom schema aligned with DCAT-AP-SK.

The schema should at minimum cover required practical fields for registration and harvesting:

- dataset title
- dataset description
- dataset theme using an accepted controlled vocabulary
- update frequency using an accepted controlled vocabulary
- keywords
- license
- publisher/default organization
- contact point
- distribution/resource title
- distribution access URL or download URL
- distribution format/media type

If `ckanext-dcat` cannot serialize required Slovak-specific fields correctly with `euro_dcat_ap_2`, add a custom RDF profile that extends the European DCAT-AP profile and maps CKAN fields to DCAT-AP-SK terms and controlled vocabulary values.

## IDSK UI Scope

The goal is "whole publishing portal feels IDSK", not just header and footer.

Pages to restyle or replace:

- home
- login
- password reset
- user dashboard
- dataset search and dataset detail
- dataset create/edit
- resource create/edit/upload
- organization detail
- account/profile pages needed by publishers
- common error pages
- flash messages and validation errors
- breadcrumbs and navigation

The implementation should use IDSK form, button, validation, table, warning, stepper/progress, header, footer, and layout patterns. Bootstrap classes should not dominate visible publishing screens.

## Non-Goals For This Phase

- Multi-tenant onboarding for many institutions.
- Self-service organization creation by every user.
- SPARQL endpoint hosting.
- External identity integration.
- Complex approval workflow unless required later.
- Fully replacing CKAN's internal admin screens.

## Error Handling

The publishing flow should clearly handle:

- missing required metadata
- invalid controlled vocabulary values
- failed file uploads
- unsupported file formats
- DataPusher failures
- missing default organization
- unauthenticated access
- unauthorized publishing attempts

Validation errors should use IDSK error summary and field-level messages.

## Testing And Verification

Minimum verification before calling the platform complete:

1. Docker stack starts cleanly.
2. Login works.
3. Default organization exists.
4. User can create a dataset through the IDSK flow.
5. User can upload a CSV resource.
6. Dataset page is public.
7. Uploaded resource download URL works.
8. `/dataset/<name>.ttl` returns RDF for the dataset.
9. `/catalog.ttl` includes the dataset.
10. RDF includes dataset and distribution metadata.
11. DCAT output is checked against DCAT-AP-SK expectations.
12. Key publishing pages are visually checked at desktop and mobile widths.
13. Broken static assets are fixed.
14. Slovak text renders correctly.

## Risks

- CKAN default templates are broad; making every page IDSK can become large. Start with publisher-critical pages first.
- `euro_dcat_ap_2` may not be enough for DCAT-AP-SK. Plan for a custom profile or schema mapping.
- Local Docker currently has Windows-specific issues: CRLF in `01_setup_datapusher.sh`, and Windows curl TLS problems against the local self-signed certificate.
- The production `CKAN_SITE_URL` and HTTPS certificate must be correct before using the LKOD link externally.

## Recommended Implementation Order

1. Stabilize runtime basics: encoding, missing assets, CRLF script, upload config.
2. Create default organization setup and verify upload/publish flow with standard CKAN screens.
3. Add metadata schema and validation for DCAT-AP-SK-required fields.
4. Verify DCAT output with one real dataset and one resource.
5. Build IDSK publishing screens for the main workflow.
6. Restyle supporting user and dataset pages.
7. Add regression checks for Docker startup, publishing, upload, and RDF output.

