# Data@Spark runtime automation

Read [`SHARED_HOST_BOOTSTRAP.md`](SHARED_HOST_BOOTSTRAP.md) before you provision
or configure the interim DigitalOcean hosts shared with Herbaria.

This is the narrow runtime layer for the single-host deployment described in
the orchestration repository. It excludes AWS, DNS,
Cloudflare, R2, or credentials.

The project-agnostic host bootstrap and webhook-listener roles
(`base_host`, `webhook_listener`) live in
[`BU-Spark/spark-ansible`](https://github.com/BU-Spark/spark-ansible), not
here — per ADR-0004 (spark-herbaria-dev) / ADR-0010 (this repo). Herbaria's
own runtime role (`herbaria_runtime`) lives in `se-symbiota-private`
(private), packaged the same way. Install both with
`ansible-galaxy collection install -r requirements.yml` before running
`playbooks/bootstrap.yml`, which is now the single composition entry point
required by both ADRs: `base_host`, `webhook_listener`,
`data_at_spark_runtime`, and `herbaria_runtime`, each invoked exactly once,
gated on whether a host's own inventory defines that project's variables.
See the comment at the top of `bootstrap.yml` for the full reasoning and
for where each project's inventory lives.

Each environment has its own checked-out runtime source tree, Compose project,
named volumes, and loopback port. The role verifies that each source checkout
is at `data_at_spark_runtime_source_sha`; this source is used only for the
locally built nginx and PostgreSQL support services. Its standalone deployment
Compose file omits the upstream `pip_cache` and `site_packages`
mounts, so no mutable package volume masks the digest-pinned CKAN image. CKAN
itself uses `ghcr.io/bu-spark/data-at-spark@sha256:<64 hex
characters>`.

Real inventories and `data_at_spark_secrets` stay outside Git. The role writes
them to the managed host's `.env` with mode `0600`. Git contains no values.
A production Caddyfile must import the rendered Caddy fragment.

Validate the contract without a managed host or credentials:

```bash
ansible-playbook -i inventories/example/hosts.yml playbooks/validate.yml
```

The validation playbook renders both environments in a temporary directory,
runs `podman compose config` for each one, checks the image, port, and volume
contract, and then removes the temporary output. It does not start containers,
contact a registry, or modify Caddy/systemd.

For a host run, create an external inventory that sets non-example source
checkouts, image digests, and every `data_at_spark_secrets` key. The host must
already have the `dataspark` user, rootless Podman, a working `podman compose`,
Caddy, lingering enabled for the deploy user, and source trees checked out at
the exact pinned revision.
After reviewing rendered files, opt in to unit activation with
`data_at_spark_runtime_manage_systemd: true`; Caddy integration remains a separate
host-level action. Caddy proxies to nginx over its loopback-only self-signed
TLS listener and disables upstream certificate verification only for that local
hop. The runtime service builds only the nginx and PostgreSQL
support images from its verified checkout; the CKAN service has no build stanza
and remains digest-pinned. The oneshot systemd unit orchestrates project
start and stop. Container health checks and restart policies report and handle
service failures; the systemd unit does not monitor detached containers.

## Local smoke test

`bin/local-smoke` prepares a single disposable local runtime without a cloud
account or external credentials. It uses the same runtime role and Compose
template as a host deployment, but renders into a private state directory and
uses a loopback-only TLS port. It never deletes named volumes.

Prerequisites are `ansible-playbook`, rootless `podman` with `podman compose`,
`openssl`, and (for `start`) permission to pull public container images. The
first `render` generates hexadecimal-only disposable values under
`${XDG_STATE_HOME:-$HOME/.local/state}/data-at-spark-smoke`; do not reuse that
directory for a real environment.

Run `start` from the host shell. The script refuses to start inside a container
or distrobox because rootless Podman DNS needs the host user systemd manager.

```bash
bin/local-smoke render
bin/local-smoke start
bin/local-smoke status
bin/local-smoke measure
bin/local-smoke logs
bin/local-smoke stop
```

The local CKAN endpoint is `https://127.0.0.1:18443`. `start` builds only the
nginx and PostgreSQL support images from a clean snapshot of the recorded
source revision and pulls the immutable public CKAN image. `logs` accepts extra
`podman compose logs` arguments, for example `bin/local-smoke logs -f ckan`.

After the stack has run for an hour, `bin/hourly-smoke-check` records health
and resource use, creates a dataset, uploads a small CSV, confirms search, and
waits for DataStore ingestion. It keeps the dataset for inspection and writes
a private report under the smoke state directory.

Schedule the check from the host user session:

```bash
systemd-run --user \
  --unit=data-at-spark-smoke-hourly-check \
  --on-active=1h \
  --collect \
  /absolute/path/to/data-at-spark/ansible/bin/hourly-smoke-check
```

## Backup and disposable restore test

`bin/runtime-backup` creates an application-consistent backup for the current
local-storage runtime. It briefly stops CKAN, DataPusher, and nginx while
PostgreSQL remains available. The resulting private directory contains custom
format dumps of `ckandb` and `datastore`, an export of the `ckan_storage`
volume, a secret-free manifest, and checksums. It never copies `.env`.

```bash
bin/runtime-backup \
  --runtime-dir /srv/data-at-spark/production \
  --compose-project data-at-spark-prod \
  --backup-dir /srv/data-at-spark/backups/production
```

An archive on the application host is not disaster recovery. Copy completed
backup directories to independently managed storage under a separate
retention policy.

Prove an archive with a project name that contains `restore` and differs from
the source project recorded in its manifest:

```bash
bin/runtime-restore-test \
  --runtime-dir /srv/data-at-spark/production \
  --compose-project data-at-spark-prod-restore-20260729 \
  --backup-dir /srv/data-at-spark/backups/production/backup-TIMESTAMP
```

The restore test verifies checksums, creates fresh PostgreSQL, Solr, and CKAN
storage volumes, restores both databases and local uploads, waits for CKAN,
and rebuilds the search index. Its exit trap removes the disposable project
and volumes. It refuses an existing project or volume.

These commands deliberately exclude Redis and Solr data: Redis is disposable,
and Solr is rebuilt from PostgreSQL. They currently support the local
`ckan_storage` volume. A deployment that uses R2, BU S3, Globus, or another
external filestore must add and verify that provider's independent
versioning, snapshot, or export procedure before treating a backup as
complete. A future managed PostgreSQL adapter can retain the same logical dump
format while changing how the commands connect to the databases.
