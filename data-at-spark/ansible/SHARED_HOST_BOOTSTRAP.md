# Shared host bootstrap plan

This plan provisions the interim DigitalOcean hosts shared by Data@Spark and
Herbaria. The paired decisions are Data@Spark ADR-0009 and Herbaria ADR-0003.

## Fixed infrastructure choices

| Item | Integration host | Production host |
|---|---|---|
| DigitalOcean region | NYC3 | NYC3 |
| Droplet name | `spark-shared-int` | `spark-shared-prod` |
| Droplet size | `s-2vcpu-4gb` | `s-4vcpu-8gb` |
| Workloads | Data@Spark integration; Herbaria int | Data@Spark production; Herbaria alpha |
| Volume count | 1 | 1 |
| Initial Volume size | 20 GiB | 20 GiB |
| Volume mount | `/mnt/spark-data` | `/mnt/spark-data` |
| Operating system | Fedora 44 Cloud | Fedora 44 Cloud |

Each 20 GiB Volume costs about $2 per month at the current $0.10/GiB rate.
The two Droplets and two Volumes cost about $76 per month before snapshots or
backup services. A Volume and its Droplet must use the same DigitalOcean
datacenter. A Volume can attach to one Droplet at a time.

Do not store Droplet IP addresses, SSH keys, inventory hostnames, or secret
values in this public repository. Store real inventory and secrets in the
approved external inventory or secret manager.

## Data layout

Use the DigitalOcean-formatted XFS filesystem. Mount it by UUID at
`/mnt/spark-data` with `defaults,nofail,discard,noatime,prjquota`. Do not format
the Volume during bootstrap.

Create this directory tree on both hosts:

```text
/mnt/spark-data/
├── data-at-spark/
│   ├── backups/
│   ├── ckan-storage/
│   └── postgres/
└── herbaria/
    ├── imglib/
    ├── logs/
    ├── mysql/
    └── temp/
```

Assign `data-at-spark/` to the `dataspark` user. Assign `herbaria/` to the
`symbiota` user. Do not grant one service user write access to the other
project's directory.

Bind Herbaria's project directory to the environment-specific path expected
by its deployment scripts:

- integration: `/mnt/symbiota/data/int`
- production: `/mnt/symbiota/data/alpha`

Update the Data@Spark Compose template to use bind mounts for PostgreSQL and
CKAN uploads. Keep rebuildable Solr and Redis data on the root disk unless a
restore test shows that this causes a problem. Do not rely on rootless
Podman's default named-volume path for persistent data.

## Ansible changes

Keep one parent inventory group and one child group per host tier:

- `shared_spark_hosts`
- `shared_int_hosts`
- `shared_prod_hosts`

Each host receives one Data@Spark environment only. The integration host must
not receive production secrets. The production host must not receive
integration secrets.

Add these roles:

1. `base_host`
   - Create the `dataspark` and `symbiota` users.
   - Install Podman, the Compose provider, Caddy, Git, and required packages.
   - Enable user lingering for both service users.
   - Configure the host firewall.
   - Mount the attached Volume and create the data directories.
2. `webhook_listener`
   - Install one `adnanh/webhook` instance per host.
   - Load hook definitions for both projects.
   - Keep secrets outside Git.
   - Route requests through TLS.
   - Validate signatures where the registry supports them.
3. `herbaria_runtime`
   - Clone or install the private deployment configuration.
   - Install the existing `containers/int` or `containers/alpha` launcher.
   - Render environment files from external secrets.
   - Install and enable the rootless systemd service.
4. `data_at_spark_runtime`
   - Clone each required source checkout at the selected commit SHA.
   - Pass only the environment assigned to the host.
   - Set `data_at_spark_runtime_manage_systemd: true` for deployment runs.
   - Render bind mounts that place persistent data on `/mnt/spark-data`.

Keep stable playbooks for host bootstrap and runtime deployment. Select the
host tier through inventory groups and group variables. Do not create a
separate playbook for each project and tier combination.

## Network policy

Apply these firewall rules:

- Restrict SSH to approved administrator source addresses.
- Allow public TCP 80 and 443 when Caddy terminates Data@Spark traffic.
- Do not expose database, Redis, Solr, or container loopback ports.
- Route webhook requests through the public TLS endpoint or the approved
  Cloudflare path. Do not expose an unprotected listener port.
- Allow outbound HTTPS, DNS, package repositories, registries, and the
  Cloudflare Tunnel connection.

Bootstrap permits key-only SSH from all sources until the operator confirms a
stable administrator CIDR. Replace the global SSH service rule with a source-
restricted rich rule before production launch.

Use Caddy for the Data@Spark hostnames. Repoint the existing Herbaria
Cloudflare Tunnel routes to the new Herbaria services. Confirm the webhook
route before you enable automatic deployment. Use manual deployment during
bootstrap.

## Provisioning record

Store the live inventory at
`data-at-spark/private/ansible/inventory/hosts.yml`. The wrapper repository
ignores `private/`, and the directory stays outside the public child
repositories. Record non-secret resource identifiers there after the operator
creates the resources:

| Field | Integration | Production |
|---|---|---|
| Droplet ID/name | pending | pending |
| Public address | external inventory | external inventory |
| Volume ID/name | pending | pending |
| Volume size | pending | pending |
| SSH host key fingerprint | external inventory | external inventory |

## Deployment sequence

1. Create both NYC3 Droplets and attach one NYC3 Volume to each Droplet.
2. Add the hosts and Volume identifiers to the external inventory.
3. Run the host-bootstrap playbook.
4. Check users, mounts, ownership, firewall rules, Podman, Caddy, and systemd.
5. Deploy Data@Spark integration and Herbaria int to the integration host.
6. Restore test data and run application smoke tests.
7. Deploy Data@Spark production and Herbaria alpha to the production host.
8. Restore the production or demo data and run application smoke tests.
9. Repoint Data@Spark DNS and the Herbaria Cloudflare Tunnel routes.
10. Configure webhook delivery and test one deployment for each project.
11. Run Data@Spark backup and isolated-restore tests.
12. Check Volume usage and set the first resize threshold.

## Acceptance checks

- Each host mounts its Volume after a reboot.
- Each service starts after a reboot without an interactive login.
- Each application writes persistent data under its project directory.
- Neither service user can write to the other project's directory.
- Public requests reach all four environment hostnames.
- Database and internal service ports reject public connections.
- A Data@Spark deployment does not restart Herbaria.
- A Herbaria deployment does not restart Data@Spark.
- Backups contain the database and upload data required for a restore.
- Monitoring reports root-disk and attached-Volume usage.

## Resize and recovery rules

DigitalOcean does not support shrinking a Volume. Take a Volume snapshot
before a resize. Expand the filesystem after DigitalOcean finishes the resize.

One project can consume the free space needed by the other project on the
same host. Add a warning threshold before either project reaches that point.
Use XFS project quotas if monitoring does not provide enough protection.

Droplet backups exclude attached Volumes. Use Volume snapshots or copy the
application backups off-host when faster recovery warrants the added cost.
