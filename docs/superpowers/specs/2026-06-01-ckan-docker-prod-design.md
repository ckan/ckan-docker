# CKAN Docker Production Deployment Design

Date: 2026-06-01

## Goal

Create a standalone `ckan-docker-prod` deployment folder for a Slovak open data portal built on CKAN. The production stack must run CKAN with DCAT export, the IDSK theme extension, uploads, DataStore, DataPusher, PostgreSQL, Solr, and Redis.

The operational goal is simple:

1. A publisher creates a dataset in CKAN.
2. The publisher uploads or links data resources.
3. CKAN exposes the public DCAT catalog at `/catalog.ttl`.
4. An operator registers the final public catalog URL on the Slovak national open data portal.

The final public URL is not known yet, so the production environment must require a placeholder `CKAN_SITE_URL` that is replaced before any real registration.

## External Context

The Slovak open data flow centers on `data.slovensko.sk` and the electronic service for publishing open data, data services, and local catalogs. The relevant metadata profile is DCAT-AP-SK. DCAT-AP-SK supports catalog access through DCAT-AP documents or SPARQL. For this CKAN deployment, the practical first target is a DCAT document endpoint, because `ckanext-dcat` exposes CKAN catalog and dataset RDF endpoints directly.

Key sources:

- `https://mirri.gov.sk/sekcie/informatizacia/o-sekciach/centralna-datova-kancelaria/otvorene-udaje/`
- `https://www.slovensko.sk/sk/detail-sluzby?externalCode=ks_335404`
- `https://datova-kancelaria.github.io/dcat-ap-sk-2.0/`
- `https://docs.ckan.org/projects/ckanext-dcat/en/latest/endpoints/`

## Chosen Approach

Use a standalone production deployment folder with a default localhost port and an optional reverse proxy Docker network.

This balances the current unknowns:

- There is no final public domain yet.
- The server reverse proxy will be external to this stack.
- The stack still needs to be testable without the reverse proxy.
- The production files should not be mixed with the existing test/development compose files.

The default compose will publish CKAN only on `127.0.0.1:${CKAN_PORT_HOST}:5000`. A second compose override will optionally attach CKAN to an external `reverse-proxy` Docker network when the server proxy is containerized.

## Folder Structure

Create this new folder:

```text
ckan-docker-prod/
  .env.example
  README.md
  docker-compose.yml
  docker-compose.proxy.yml
  bin/
    verify-prod
  ckan/
    Dockerfile
    docker-entrypoint.d/
    ckanext-idsk/
  postgresql/
    Dockerfile
    docker-entrypoint-initdb.d/
```

No production nginx container is included. Public HTTPS, certificates, redirects, HSTS, compression, and public ports belong to the external reverse proxy.

## Services

The production compose will define:

- `ckan`: production CKAN service built from `ckan/Dockerfile`
- `db`: PostgreSQL with CKAN and DataStore initialization scripts
- `solr`: CKAN Solr image
- `redis`: Redis for CKAN cache/queue behavior
- `datapusher`: CKAN DataPusher image

The stack will use named Docker volumes:

- `ckan_storage`
- `pg_data`
- `solr_data`
- `pip_cache`
- `site_packages`

Internal services stay on internal Docker networks where possible:

- `dbnet`
- `solrnet`
- `redisnet`
- `ckannet`

Only CKAN is reachable from the host by default, and only through the localhost bind.

## Reverse Proxy Integration

Default mode:

```bash
docker compose up -d --build
```

The external reverse proxy on the host can route to:

```text
http://127.0.0.1:${CKAN_PORT_HOST}
```

Optional Docker network mode:

```bash
docker network create reverse-proxy
docker compose -f docker-compose.yml -f docker-compose.proxy.yml up -d --build
```

The reverse proxy container can then route to:

```text
http://ckan:5000
```

The public URL exposed by the reverse proxy must match `CKAN_SITE_URL` and `CKAN__SITE_URL`.

## CKAN Configuration

`.env.example` will include placeholders and production warnings for:

- `CKAN_SITE_URL=https://CHANGE-ME.example.sk`
- `CKAN__SITE_URL=https://CHANGE-ME.example.sk`
- secure PostgreSQL passwords
- CKAN sysadmin name, email, and password
- `CKAN___BEAKER__SESSION__SECRET`
- API token encode/decode secrets
- SMTP values
- CKAN upload size limits
- DataPusher callback URL
- Solr, Redis, and PostgreSQL connection URLs

The plugin chain will include:

```text
image_view text_view datatables_view datastore datapusher envvars dcat dcat_json_interface structured_data scheming_datasets idsk_theme
```

DCAT and scheming settings will include:

```text
CKANEXT__DCAT__RDF__PROFILES=euro_dcat_ap_2 euro_dcat_ap_scheming
CKAN___SCHEMING__DATASET_SCHEMAS=ckanext.idsk:schemas/dcat_ap_sk.yaml
CKAN___SCHEMING__PRESETS=ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml
```

If the custom Slovak RDF profile is completed and registered in `ckanext-idsk`, the DCAT profile chain can be extended with `idsk_dcat_ap_sk`.

## CKAN Image

The production CKAN image will:

- start from the CKAN 2.11 production base image
- copy `ckanext-idsk` into the image
- install `ckanext-idsk`
- install `ckanext-dcat`
- install `ckanext-scheming`
- copy Docker entrypoint scripts

The image should not mount the live source tree in production. Source code is baked into the image to make deployments repeatable.

## LKOD Publishing Flow

The operator flow is:

1. Copy `.env.example` to `.env`.
2. Replace all secrets and the placeholder public URL.
3. Start the stack.
4. Ensure the default publishing organization exists.
5. Create a dataset in CKAN.
6. Add at least one resource by upload or URL.
7. Verify the dataset page is public.
8. Verify the catalog URL returns RDF:

```text
https://public-domain.example.sk/catalog.ttl
```

9. Register that catalog URL through the Slovak open data publication flow.

`localhost`, private IP addresses, and internal Docker hostnames are not valid for registration because CKAN uses `CKAN_SITE_URL` to generate public links and RDF identifiers.

## Smoke Verification

Add `bin/verify-prod` with non-destructive checks:

- Docker compose services are running.
- CKAN status API responds successfully.
- `/catalog.ttl` is reachable from inside the CKAN container.
- upload and locale settings are present in generated `ckan.ini`.
- the configured public site URL is printed so the operator can see whether it is still the placeholder.

The default smoke script will not fail only because `CKAN_SITE_URL` is still `https://CHANGE-ME.example.sk`; that keeps the stack testable before a domain exists. A later strict production-readiness check can fail on the placeholder before real registration. The smoke script will not create datasets. Dataset publishing remains a manual or future end-to-end verification step because it requires a valid admin token and representative metadata.

## Non-Goals

- No nginx or TLS termination inside this production stack.
- No SPARQL endpoint in this phase.
- No automatic registration with `data.slovensko.sk`.
- No change to the existing root development/test compose files.
- No new frontend outside CKAN.

## Risks

- The final public domain must be set before registration; otherwise RDF links and identifiers will be wrong.
- DCAT-AP-SK validation may require a stricter custom RDF profile than the current European DCAT-AP profile plus scheming fields.
- Copying `ckanext-idsk` into the standalone deployment creates a maintenance sync point with the existing development copy. This is acceptable for an isolated production package but should be documented.
- The current working tree already has uncommitted changes in IDSK/DCAT-related files. Implementation must avoid overwriting those changes.

## Acceptance Criteria

- `ckan-docker-prod` exists as a standalone deployment folder.
- `docker-compose.yml` starts CKAN, PostgreSQL, Solr, Redis, and DataPusher without the root compose files.
- CKAN is reachable on `127.0.0.1:${CKAN_PORT_HOST}` by default.
- Optional reverse proxy Docker network support is available through an override compose file.
- `.env.example` clearly marks secrets and `CKAN_SITE_URL` as required production edits.
- `catalog.ttl` is reachable when the stack is running.
- Documentation explains what must be checked before registering the LKOD catalog URL.
