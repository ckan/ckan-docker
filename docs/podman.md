# Running CKAN with rootless Podman

The standard CKAN Compose files are the source of truth for Docker and Podman.
No duplicate Podman stack is required. The shared files include three portable
compatibility details:

- explicit PostgreSQL variable interpolation for podman-compose
- fully qualified container image references for noninteractive pulls
- an SELinux-private (`:Z`) label on the development source bind mount

The production stack uses named volumes, which Podman labels automatically.
Do not add `:Z` to named volumes.

## Requirements

- Podman 5 or later
- a Compose provider available through `podman compose`
- rootless subordinate UID/GID ranges configured by the host distribution

On Fedora, `podman-compose` is available from the Fedora repositories. Verify
the provider selected by Podman:

```bash
podman compose version
```

## Configure

Copy the public example and replace every credential and secret:

```bash
cp .env.example .env
```

## Production-mode Compose stack

Render the merged model before building:

```bash
podman compose \
  --env-file .env \
  -f docker-compose.yml \
  config
```

Build and start:

```bash
podman compose \
  --env-file .env \
  -f docker-compose.yml \
  build

podman compose \
  --env-file .env \
  -f docker-compose.yml \
  up
```

## Development stack on SELinux

The development Compose file mounts `./src` using the `:Z` option. Podman
assigns a private SELinux label so CKAN can read extension source while SELinux
remains enforcing.

```bash
podman compose \
  --env-file .env \
  -f docker-compose.dev.yml \
  config

podman compose \
  --env-file .env \
  -f docker-compose.dev.yml \
  up
```

Use `:z` instead only when the same bind-mounted content must be shared by
multiple, independently managed containers. Data owned exclusively by this
stack should use `:Z`.

## Rootless behavior

The default host ports (`5000` and `8443`) are unprivileged and work without
root. Keep host ports at or above the system's unprivileged-port threshold.
Do not run the stack with `sudo podman`; doing so creates a separate root-owned
container and volume namespace.

Stop the stack with the same file set used to start it:

```bash
podman compose \
  --env-file .env \
  -f docker-compose.yml \
  down
```
