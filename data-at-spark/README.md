# Data@Spark deployment layer

This directory layers the Data@Spark site onto the official CKAN Compose
deployment without replacing the upstream Compose files.

The image pins:

- CKAN `2.11.5`
- `ckanext-spark` at an immutable Git commit
- `ckanext-s3filestore` at an immutable Git commit (installed unconditionally;
  disabled by default — see below)
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

The `Build CKAN Docker` workflow publishes the application image to
`ghcr.io/bu-spark/data-at-spark`. A successful push to `master` publishes the
full source Git SHA as a release tag, records its immutable image digest, and
then advances the `integration` tag to that exact digest. The workflow will
reuse, but never overwrite, an existing source-SHA tag. Production must deploy
the integration-tested digest rather than rebuilding or deploying a moving
tag.

Publish the package publicly so the host can pull it without a registry
credential. GitHub creates a new container package as private. After the first
successful publish, an organization package administrator must change its
visibility. Do not add a personal access token to this repository to automate
that change.

## Local MinIO filestore spike (issue #9, Phase 1)

`ckanext-s3filestore` is installed in the image but is **not enabled** by the
plugin list above. A separate, test-only Compose overlay under
`data-at-spark/minio-spike/` adds a local MinIO backend, enables the plugin,
and configures it with example-only credentials, so it can be exercised
end-to-end without a real cloud account. See
`data-at-spark/minio-spike/README.md` for how to render, start, and validate
it, and for the security boundary and a known upstream streaming/multipart
limitation affecting large interactive web uploads.

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
