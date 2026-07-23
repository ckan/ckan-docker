# Data@Spark deployment layer

This directory layers the Data@Spark site onto the official CKAN Compose
deployment without replacing the upstream Compose files.

The image pins:

- CKAN `2.11.5`
- `ckanext-spark` at an immutable Git commit
- the CKAN 2.11 Solr 9 image

## Configure

Create local environment files from the public examples:

```bash
cp .env.example .env
cp data-at-spark/.env.example data-at-spark/.env
```

Replace every credential and secret in `.env`. The Data@Spark file contains
only site and version settings; use a different site URL for a local or future
integration environment.

## Render the merged configuration

```bash
docker compose \
  --env-file .env \
  --env-file data-at-spark/.env \
  -f docker-compose.yml \
  -f data-at-spark/compose.yml \
  config
```

## Build and start

```bash
docker compose \
  --env-file .env \
  --env-file data-at-spark/.env \
  -f docker-compose.yml \
  -f data-at-spark/compose.yml \
  build ckan

docker compose \
  --env-file .env \
  --env-file data-at-spark/.env \
  -f docker-compose.yml \
  -f data-at-spark/compose.yml \
  up
```

These commands describe the Docker Compose baseline. Fedora/rootless Podman
support is tracked separately so runtime-specific differences do not become
Data@Spark application configuration.

## Artifact promotion

Build and tag the image with the source Git SHA. Integration and production
must deploy that same immutable image; only their configuration differs.
