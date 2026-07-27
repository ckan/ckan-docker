# ckanext-s3filestore local MinIO spike (issue #9, Phase 1)

This is a **test-only, credential-free** overlay that layers a local MinIO
backend onto the Data@Spark Compose stack so `ckanext-s3filestore` can be
exercised end-to-end without any real cloud account. It does not modify the
base `docker-compose.yml` or `data-at-spark/compose.yml` — it only adds
services and env-driven `ckan` overrides on top of them.

Phase 1 validates the deployment/config contract locally. A later phase
points the same extension at a real Cloudflare R2 bucket; that phase is out
of scope here and no R2 configuration is added by this overlay.

## What this adds

- The `data-at-spark/Dockerfile` build now installs `ckanext-s3filestore`
  pinned to an exact upstream commit (immutable, same pattern as
  `ckanext-spark`). This happens unconditionally as part of the Data@Spark
  image; the plugin is **not** enabled by default (see `data-at-spark/.env.example`) — only this overlay enables and configures it.
- `minio`: a single-node MinIO server, private storage bucket.
- `minio-init`: a one-shot `mc` job that creates the bucket deterministically
  and explicitly denies anonymous/public access, then exits. `ckan` waits on
  its successful completion before starting.
- `ckan` environment overrides that enable the `s3filestore` plugin and
  configure it via `ckanext-envvars`-compatible variables (private ACL,
  signed URLs, path-style MinIO endpoint).
- `direct_upload.py`: an import-path proof that creates a private CKAN
  dataset, generates a resource UUID, uploads bytes directly to its
  deterministic key with boto3's multipart transfer manager, creates the CKAN
  resource once the object exists, and leaves the dataset private for review.

## Configure

Run every command in this document from the repository root:

```bash
cp .env.example .env
cp data-at-spark/minio-spike/.env.example data-at-spark/minio-spike/.env

set -a
. data-at-spark/minio-spike/.env
set +a
```

Every value in `data-at-spark/minio-spike/.env.example` is a local/example
credential for a throwaway container on your own machine. Never reuse them
and never point `CKANEXT__S3FILESTORE__HOST_NAME` at a real S3/R2 endpoint
with this overlay. The root `.env` supplies the base stack's required image
versions and settings; the exported spike environment supplies MinIO overrides.

## Render the merged configuration

```bash
podman compose \
  --env-file .env \
  -f docker-compose.yml \
  -f data-at-spark/compose.yml \
  -f data-at-spark/minio-spike/compose.yml \
  config
```

(Substitute `docker compose` if you are using Docker instead of Podman.)

## Build and start

```bash
podman compose \
  --env-file .env \
  -f docker-compose.yml \
  -f data-at-spark/compose.yml \
  -f data-at-spark/minio-spike/compose.yml \
  build ckan

podman compose \
  --env-file .env \
  -f docker-compose.yml \
  -f data-at-spark/compose.yml \
  -f data-at-spark/minio-spike/compose.yml \
  up
```

Tear down with the same file set plus `down`. On Fedora/rootless Podman, the
base stack's existing SELinux (`:Z`/`:z`) handling and rootless behavior
(`docs/podman.md`) are unchanged; the only bind mount this overlay adds is
`init-bucket.sh`, mounted read-only with `:Z` since it is owned exclusively
by the `minio-init` container.

## Validate without a real cloud account

```bash
python3 data-at-spark/minio-spike/validate.py
```

This always statically checks: the immutable commit pin (Dockerfile + build
arg default), the rendered service/config contract (private ACL, path-style
addressing, MinIO host, bucket-creation dependency ordering), and the absence
of committed `.env` files or Kubernetes `Secret` manifests anywhere in the
repository. If `podman` is available it additionally renders the merged
Compose config and re-checks the pinned commit against the live output; if
not, that step is reported as a skipped warning rather than a failure.

Once the stack is running, copy a test CSV into the CKAN container, where
boto3 and requests are already installed, then execute the import-path proof:

```bash
das_compose=(
  podman compose
  --env-file .env
  -f docker-compose.yml
  -f data-at-spark/compose.yml
  -f data-at-spark/minio-spike/compose.yml
)

"${das_compose[@]}" cp ./sample.csv ckan:/tmp/sample.csv

token=$(
  "${das_compose[@]}" exec -T ckan \
    ckan user token add -q ckan_admin minio-spike 2>/dev/null |
  tail -1
)

"${das_compose[@]}" exec -T \
  -e CKAN_API_TOKEN="$token" \
  ckan python /opt/data-at-spark/direct_upload.py /tmp/sample.csv
```

The script always leaves the dataset private. Publish it separately only after
an operator has verified the registered resource, authorization behavior,
checksum, and DataPusher result. The script is a test harness, not the semester
import pipeline.

## Verified behavior

The complete local path was exercised on 2026-07-24 with CKAN 2.11.5:

- CKAN accepted a caller-generated resource UUID.
- boto3 uploaded the object before the single final `resource_create`.
- anonymous CKAN access to the private dataset returned `401`.
- direct anonymous MinIO access returned `403`.
- authorized CKAN access redirected to a short-lived signed URL, which returned
  the original bytes and matching SHA-256 checksum.
- DataPusher followed the authorized CKAN download and populated two CSV rows
  in DataStore while the dataset remained private.
- after a separate publication action, anonymous CKAN download redirected to a
  working signed URL.
- forced final-registration failure removed the already-uploaded object rather
  than silently leaving it orphaned.

Creating a placeholder resource before uploading was also tested and rejected:
it caused DataPusher to fetch the placeholder immediately. The UUID-first,
object-first sequence in `direct_upload.py` avoids that race.

CKAN `resource_delete` returned success but did **not** delete the corresponding
MinIO object. This is explicit, reproducible behavior—not a silently accepted
partial failure—but it blocks production acceptance until Data@Spark defines
and implements deletion/purge and retention semantics.

## Security boundary

- **Access control stays in CKAN.** This spike does not add
  `ckanext-restricted`. Dataset visibility is whatever CKAN's own
  private/public model says it is; `ckanext-s3filestore` only changes
  *where bytes are stored*, not who is authorized to fetch them.
  `ckanext-s3filestore` checks CKAN's package/resource authorization and
  redirects to a **short-lived signed URL** only after that check passes — it
  does not proxy the bytes itself.
- **The MinIO bucket is private** (`ckanext.s3filestore.acl=private`, and
  `mc anonymous set none` on the bucket itself). Nothing is reachable by
  anonymous S3 requests; every read goes through a signed URL CKAN issues
  after authorization.
- **No secrets are committed.** Only `.env.example` files are tracked; real
  `.env` files are gitignored, and this overlay never touches Kubernetes
  Secret resources or int/prod overlays.
- **This is a local/dev-only trust boundary.** MinIO here has no TLS (the
  configured endpoint is `http://minio:9000`) and runs on the same Compose
  network as `ckan`. That
  is acceptable for a local spike and is not how the real R2-backed
  deployment will be configured.

## Known blocking limitation for production acceptance

The validated upstream candidate
(`keitaroinc/ckanext-s3filestore@e972ae3c36489dcfc716f75063ac64c13cde1146`,
covered by upstream CI for CKAN 2.11 / Python 3.10) has a correctness issue in
`BaseS3Uploader.upload_to_key`: it calls `upload_file.read()` and passes the
full byte string to boto3 as `Body`, rather than streaming or using a
multipart upload. **Do not treat multi-gigabyte uploads as safe** with this
extension as-is — every upload is fully buffered in CKAN worker memory first.
This extension is not patched or forked in this task. Automated imports should
use the direct multipart path demonstrated by `direct_upload.py`; interactive
web uploads still require an upstream fix, a maintained fork, or a conservative
upload-size ceiling before accepting large files in production.

`resource_delete` also leaves the stored object in place. Production must add
an explicit object purge/retention path and verify it against the selected
object store.
