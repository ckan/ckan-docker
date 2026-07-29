# Data@Spark runtime automation

This is the narrow runtime layer for the single-host deployment described in
the orchestration repository. It excludes AWS, DNS,
Cloudflare, R2, or credentials.

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
