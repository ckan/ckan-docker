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
only site and version settings.

`int` is an environment name, not a source branch. Keep the Data@Spark site
URLs aligned with the deployment target:

- `https://int.data.buspark.io` for integration
- `https://data.buspark.io` for production

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

## Kubernetes overlays

The Kubernetes deployment overlays live under `data-at-spark/kubernetes/`:

- `data-at-spark/kubernetes/int`
- `data-at-spark/kubernetes/prod`

Render either overlay with `kubectl kustomize`:

```bash
kubectl kustomize data-at-spark/kubernetes/int
kubectl kustomize data-at-spark/kubernetes/prod
```

Both overlays inherit `kubernetes/base` and only layer Data@Spark-specific
identity, namespaces, and environment labels. Their namespaces enforce the
Kubernetes restricted Pod Security profile. Ingress, TLS, storage class, and
secret-manager wiring stay cluster-specific and must be supplied by the
deployment environment.

Before applying either overlay, render it and substitute the exact Data@Spark
image digest produced by the release pipeline:

```bash
kubectl kustomize data-at-spark/kubernetes/int > rendered-int.yaml
python3 kubernetes/substitute_ckan_image.py \
  registry.example/data-at-spark@sha256:DIGEST \
  rendered-int.yaml
```

Use the same immutable image reference for production. The substitution helper
fails unless the reference contains a full SHA-256 digest and exactly the CKAN
web, initialization, and reindex images are replaced.

For a fresh environment, apply the overlay's `namespace.yaml` first, create the
external `ckan-secrets` Secret in that namespace, then apply the promoted
rendered manifest. Do not commit the rendered manifest or Secret values.
