# CKAN Docker Production Deployment

This folder contains a standalone production deployment for a CKAN open data portal with DCAT export for LKOD registration.

The stack does not terminate public HTTPS. Put it behind an external reverse proxy such as nginx, Caddy, or Traefik.

## Services

- CKAN 2.11
- PostgreSQL
- Solr
- Redis
- DataPusher

## Branding

The production bundle uses the default CKAN layout with a small DataHub branding extension. Users should see `DataHub Open Data` instead of visible CKAN branding such as `Powered by CKAN`.

## First Setup

This prepared local bundle includes an ignored `.env` file with generated secrets. Keep that file with the deployment package when copying `ckan-docker-prod` to a server.

The tracked `.env.example` file remains a template only.

Before exposing the portal publicly:

- Keep `.env` out of Git.
- Check `CKAN_SYSADMIN_EMAIL`.
- Set SMTP values if password reset or mail notifications are required.
- Replace `CKAN_SITE_URL` and `CKAN__SITE_URL` with the final public HTTPS URL.

The current local default is:

```text
http://localhost:5000
```

Do not register the LKOD catalog while `CKAN_SITE_URL` is `http://localhost:5000`.

## Start

Default mode exposes CKAN only on localhost:

```bash
docker compose up -d --build
```

Your external reverse proxy can route to:

```text
http://127.0.0.1:5000
```

If `CKAN_PORT_HOST` is changed in `.env`, use that port instead.

## Optional Docker Reverse Proxy Network

Create the external network once:

```bash
docker network create reverse-proxy
```

Start with the proxy override:

```bash
docker compose -f docker-compose.yml -f docker-compose.proxy.yml up -d --build
```

A reverse proxy container on the same network can route to:

```text
http://ckan-prod:5000
```

## Verify Runtime

After the stack is running:

```bash
bin/verify-prod
```

The script checks:

- running compose services
- CKAN status API
- `catalog.ttl`
- DataHub branding
- upload configuration
- Slovak locale configuration
- configured public site URL

## Demo Organization And Dataset

Seed the default publisher organization and demo schools dataset after the stack is running:

```bash
bash bin/seed-demo-data
```

The command creates or updates:

- organization `minedu`
- dataset `testovaci-zoznam-skol`
- one uploaded CSV resource with 10 synthetic school rows

The command is idempotent and can be run repeatedly without creating duplicate organizations, datasets, or resources.

## LKOD Publication Checklist

Before registering the catalog URL through the Slovak open data publication flow:

- The public reverse proxy serves the portal over trusted HTTPS.
- `CKAN_SITE_URL` and `CKAN__SITE_URL` match the public HTTPS URL.
- At least one public dataset exists.
- The dataset has at least one resource or distribution.
- The catalog URL is publicly reachable:

For local testing on this machine, the catalog URL is:

```text
http://localhost:5000/catalog.ttl
```

For slovensko.sk registration, use the public HTTPS URL exposed by the server reverse proxy:

```text
https://your-public-domain.example/catalog.ttl
```

- Dataset RDF is publicly reachable:

```text
https://your-public-domain.example/dataset/<dataset-name>.ttl
```

The national portal should receive the public `catalog.ttl` URL, not a localhost URL, private IP address, or Docker hostname.

## Useful Commands

Show services:

```bash
docker compose ps
```

Show CKAN logs:

```bash
docker compose logs -f ckan
```

Open a CKAN shell command:

```bash
docker compose exec -T ckan ckan -c /srv/app/ckan.ini --help
```

Stop the stack:

```bash
docker compose down
```

Stop and remove data volumes:

```bash
docker compose down -v
```
