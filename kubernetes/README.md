# Kubernetes deployment

This directory provides a Kustomize baseline for CKAN and the services used by
the Compose deployment. It is intentionally independent of a Kubernetes
distribution, ingress controller, certificate manager, storage provisioner,
and secret manager.

## Layout

- `base/` contains the reusable workloads, services, probes, and storage
  interfaces.
- `overlays/int/` and `overlays/prod/` demonstrate environment-specific
  namespaces and public CKAN configuration.

Both overlays inherit the same CKAN image reference. Promote one immutable
image digest by replacing `docker.io/ckan/ckan-base:2.11` at render or delivery
time in both environments.

## Prerequisites

- a default StorageClass, or patches that set `storageClassName`
- an externally managed Secret named `ckan-secrets`
- a CKAN image compatible with this repository's production image contract
- an ingress or gateway configured separately for the `ckan` Service

The baseline uses one CKAN replica because the default storage claim requests
`ReadWriteOnce`. A production overlay may increase replicas only when its
storage provider supports shared `ReadWriteMany` access, or after object
storage replaces the shared filesystem.

## Secret contract

Create `ckan-secrets` in the target namespace without committing its values.
The Secret must contain:

- `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`
- `CKAN_DB_USER`, `CKAN_DB_PASSWORD`, and `CKAN_DB`
- `DATASTORE_READONLY_USER`, `DATASTORE_READONLY_PASSWORD`, and `DATASTORE_DB`
- `CKAN_SQLALCHEMY_URL`
- `CKAN_DATASTORE_WRITE_URL` and `CKAN_DATASTORE_READ_URL`
- `CKAN___SECRET_KEY`
- `CKAN___WTF_CSRF_SECRET_KEY`
- `CKAN___API_TOKEN__JWT__ENCODE__SECRET`
- `CKAN___API_TOKEN__JWT__DECODE__SECRET`
- `CKAN_SYSADMIN_NAME`, `CKAN_SYSADMIN_PASSWORD`, and `CKAN_SYSADMIN_EMAIL`

The three database URLs must use the Kubernetes Service hostname `db`.

## Render and validate

Kustomize is built into `kubectl`:

```bash
kubectl kustomize kubernetes/overlays/int
kubectl kustomize kubernetes/overlays/prod
```

Before deployment, replace the CKAN image with the exact digest produced by
the image pipeline:

```bash
kubectl kustomize kubernetes/overlays/int |
  sed 's|docker.io/ckan/ckan-base:2.11|registry.example/ckan@sha256:DIGEST|' |
  kubectl apply -f -
```

Use a delivery system's native image substitution in production rather than
the illustrative `sed` command. Supply the same digest to both overlays.

## Fresh deployment order

1. Create the target namespace.
2. Create `ckan-secrets` through the cluster's secret-management mechanism.
3. Apply the rendered overlay.
4. Wait for the `ckan-initialize` Job to complete.
5. Wait for the `ckan-rebuild-search` Job to complete.
6. Wait for the `ckan` Deployment to become available.
7. Configure ingress and TLS for the overlay's public URL.

The initialization Job owns database migration, DataStore permissions, Solr
connectivity checks, and initial sysadmin creation. The search Job waits for
initialization and then rebuilds the index. CKAN web pods set
`MAINTENANCE_MODE=true`, preventing replicas from racing setup operations.

Kubernetes Jobs are immutable. Before applying a changed CKAN image or
configuration that requires another migration or reindex, delete only the
relevant completed Job and reapply the overlay:

```bash
kubectl -n data-at-spark-int delete job ckan-initialize --ignore-not-found
kubectl -n data-at-spark-int delete job ckan-rebuild-search --ignore-not-found
```

Deployments, StatefulSets, probes, and restart policies provide reconciliation
after an ordinary process or container failure. This baseline does not claim
multi-node database or Solr high availability.
