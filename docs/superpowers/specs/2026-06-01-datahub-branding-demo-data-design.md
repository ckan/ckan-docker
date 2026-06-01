# DataHub Branding And Demo Data Design

## Context

The `ckan-docker-prod` folder is a standalone production deployment for a Slovak open data portal. It currently runs CKAN with the default CKAN theme, DCAT export, scheming, DataPusher, PostgreSQL, Solr, and Redis. The IDSK visual theme is intentionally disabled.

The next change must keep the default CKAN look and feel while replacing visible CKAN branding with `DataHub Open Data`, adding a default publisher organization, adding a demo dataset with 10 schools, and documenting the catalog URL that will be registered for Slovak open data harvesting.

## Decisions

- The production UI must show `DataHub Open Data` as the portal brand.
- Visible CKAN branding, including footer text such as `Powered by CKAN`, must not be shown to users.
- The default CKAN layout and styling must remain in use. The IDSK theme must not be re-enabled.
- The publishing organization slug will be `minedu`.
- The organization title will be `Ministerstvo školstva, výskumu, vývoja a mládeže Slovenskej republiky`.
- The demo dataset will contain synthetic test data, not real school records.
- The demo data resource will be a CSV file with 10 school rows.
- The local catalog URL is `http://localhost:5000/catalog.ttl`.
- The URL for slovensko.sk must be the public HTTPS equivalent after deployment, for example `https://tvoja-domena.sk/catalog.ttl`.

## Proposed Architecture

### Branding

Add a small production-only CKAN extension, for example `ckanext-datahub`, inside `ckan-docker-prod/ckan`. The extension will only register templates and a minimal plugin class. It will not add IDSK assets, custom CSS, or a new visual theme.

The extension will override only the default CKAN template fragments needed to remove visible CKAN branding and show `DataHub Open Data`. The production environment files will set:

- `CKAN__SITE_TITLE=DataHub Open Data`
- `CKAN__SITE_DESCRIPTION=Katalóg otvorených dát`

The production startup config script will write the site title and site description into `ckan.ini` so the values are applied reliably on container startup.

### Demo Data Seeding

Add an idempotent helper command in `ckan-docker-prod/bin`, for example `seed-demo-data`.

The command will run against the active Docker Compose stack and create or update:

- organization `minedu`
- dataset `testovaci-zoznam-skol`
- one CSV resource containing 10 synthetic school rows

The command must be safe to run repeatedly. Existing objects with the same slugs will be updated instead of duplicated.

The CSV should use clear Slovak columns, for example:

- `nazov_skoly`
- `typ_skoly`
- `obec`
- `okres`
- `kraj`

### Catalog URL

The CKAN DCAT extension already exposes the catalog at `/catalog.ttl`. For the local deployment this is:

```text
http://localhost:5000/catalog.ttl
```

For slovensko.sk registration this must be changed to the public HTTPS URL served by the reverse proxy:

```text
https://tvoja-domena.sk/catalog.ttl
```

The README and verification output should make this distinction explicit so `localhost` is not registered as a production catalog URL.

## Data Flow

1. The operator starts the production stack with Docker Compose.
2. CKAN startup applies production config from `.env`.
3. The DataHub branding extension is loaded as part of `CKAN__PLUGINS`.
4. The operator runs `bin/seed-demo-data`.
5. The seed command creates or updates the `minedu` organization, demo dataset, and CSV resource.
6. CKAN DCAT exposes the dataset through the catalog RDF endpoint.
7. The operator uses `/catalog.ttl` as the catalog URL for local testing and the public HTTPS equivalent for slovensko.sk.

## Error Handling

- If Docker Compose services are not running, `seed-demo-data` should exit with a clear message.
- If the CKAN API or CLI call fails, the command should fail non-zero.
- If the resource already exists, it should be updated rather than duplicated.
- The command must not print generated secrets from `.env`.

## Verification

After implementation:

- Run the production smoke check.
- Verify the homepage no longer contains visible `Powered by CKAN`.
- Verify `DataHub Open Data` appears in the page title or visible brand area.
- Run the demo seed command.
- Verify organization `minedu` exists.
- Verify dataset `testovaci-zoznam-skol` exists and is public.
- Verify the CSV resource contains 10 rows.
- Verify `http://localhost:5000/catalog.ttl` contains the demo dataset.

## Out Of Scope

- Re-enabling the IDSK theme.
- Creating a custom full visual design.
- Registering the catalog on slovensko.sk from this environment.
- Using real school records.
- Configuring the final public domain or TLS certificate.
