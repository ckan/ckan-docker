# CKAN Docker Production Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a standalone `ckan-docker-prod` deployment folder for CKAN with DCAT/LKOD export, IDSK extension support, DataStore, DataPusher, PostgreSQL, Solr, Redis, and external reverse proxy integration.

**Architecture:** Build a production-only Docker Compose stack independent from the root development/test compose files. CKAN is exposed only on `127.0.0.1:${CKAN_PORT_HOST}:5000` by default, with an optional compose override for an external Docker reverse proxy network. Source code for `ckanext-idsk` is baked into the production CKAN image instead of mounted live.

**Tech Stack:** Docker Compose V2, CKAN 2.11, PostgreSQL 16 Alpine, `ckan/ckan-solr:2.11-solr9`, Redis 6, CKAN DataPusher, `ckanext-dcat`, `ckanext-scheming`, custom `ckanext-idsk`.

---

## File Structure

- Create `ckan-docker-prod/docker-compose.yml`: base production stack with CKAN, PostgreSQL, Solr, Redis, and DataPusher.
- Create `ckan-docker-prod/docker-compose.proxy.yml`: optional override that joins CKAN to an external reverse proxy network.
- Create `ckan-docker-prod/.env.example`: production configuration template with required secrets and public URL values.
- Create `ckan-docker-prod/README.md`: operator guide for reverse proxy use, startup, verification, and LKOD registration checks.
- Create `ckan-docker-prod/bin/verify-prod`: non-destructive runtime smoke check.
- Create `ckan-docker-prod/ckan/Dockerfile`: production CKAN image that installs DCAT, scheming, and `ckanext-idsk`.
- Copy `ckan/ckanext-idsk/` to `ckan-docker-prod/ckan/ckanext-idsk/`: production copy of the custom extension.
- Copy `ckan/docker-entrypoint.d/01_setup_datapusher.sh` to `ckan-docker-prod/ckan/docker-entrypoint.d/01_setup_datapusher.sh`: DataPusher token setup.
- Copy `postgresql/Dockerfile` to `ckan-docker-prod/postgresql/Dockerfile`: PostgreSQL image wrapper.
- Copy `postgresql/docker-entrypoint-initdb.d/10_create_ckandb.sh` to `ckan-docker-prod/postgresql/docker-entrypoint-initdb.d/10_create_ckandb.sh`: CKAN database init.
- Copy `postgresql/docker-entrypoint-initdb.d/20_create_datastore.sh` to `ckan-docker-prod/postgresql/docker-entrypoint-initdb.d/20_create_datastore.sh`: DataStore database init.
- Modify `.gitattributes`: force LF endings for production shell scripts.

Do not copy `postgresql/docker-entrypoint-initdb.d/30_setup_test_databases.sh` into production. Test databases are not part of the production stack.

---

### Task 1: Scaffold The Standalone Production Folder

**Files:**
- Create: `ckan-docker-prod/`
- Create: `ckan-docker-prod/bin/`
- Create: `ckan-docker-prod/ckan/docker-entrypoint.d/`
- Create: `ckan-docker-prod/ckan/ckanext-idsk/`
- Create: `ckan-docker-prod/postgresql/docker-entrypoint-initdb.d/`
- Modify: `.gitattributes`

- [ ] **Step 1: Create the production directory tree**

Run from the repository root:

```powershell
New-Item -ItemType Directory -Force -Path `
  .\ckan-docker-prod, `
  .\ckan-docker-prod\bin, `
  .\ckan-docker-prod\ckan, `
  .\ckan-docker-prod\ckan\docker-entrypoint.d, `
  .\ckan-docker-prod\postgresql, `
  .\ckan-docker-prod\postgresql\docker-entrypoint-initdb.d
```

Expected: PowerShell exits with code 0 and the listed directories exist.

- [ ] **Step 2: Copy the current IDSK extension and required init scripts**

Run from the repository root:

```powershell
Copy-Item -Recurse -Force .\ckan\ckanext-idsk .\ckan-docker-prod\ckan\ckanext-idsk
Copy-Item -Force .\ckan\docker-entrypoint.d\01_setup_datapusher.sh .\ckan-docker-prod\ckan\docker-entrypoint.d\01_setup_datapusher.sh
Copy-Item -Force .\postgresql\Dockerfile .\ckan-docker-prod\postgresql\Dockerfile
Copy-Item -Force .\postgresql\docker-entrypoint-initdb.d\10_create_ckandb.sh .\ckan-docker-prod\postgresql\docker-entrypoint-initdb.d\10_create_ckandb.sh
Copy-Item -Force .\postgresql\docker-entrypoint-initdb.d\20_create_datastore.sh .\ckan-docker-prod\postgresql\docker-entrypoint-initdb.d\20_create_datastore.sh
```

Expected: PowerShell exits with code 0. `ckan-docker-prod/postgresql/docker-entrypoint-initdb.d/30_setup_test_databases.sh` does not exist.

- [ ] **Step 3: Update `.gitattributes` for production shell scripts**

Replace `.gitattributes` with:

```gitattributes
*.sh text eol=lf
bin/* text eol=lf
ckan/docker-entrypoint.d/*.sh text eol=lf
postgresql/docker-entrypoint-initdb.d/*.sh text eol=lf
ckan-docker-prod/bin/* text eol=lf
ckan-docker-prod/ckan/docker-entrypoint.d/*.sh text eol=lf
ckan-docker-prod/postgresql/docker-entrypoint-initdb.d/*.sh text eol=lf
```

- [ ] **Step 4: Verify the scaffold**

Run:

```powershell
Test-Path .\ckan-docker-prod\ckan\ckanext-idsk\setup.py
Test-Path .\ckan-docker-prod\ckan\docker-entrypoint.d\01_setup_datapusher.sh
Test-Path .\ckan-docker-prod\postgresql\docker-entrypoint-initdb.d\10_create_ckandb.sh
Test-Path .\ckan-docker-prod\postgresql\docker-entrypoint-initdb.d\20_create_datastore.sh
Test-Path .\ckan-docker-prod\postgresql\docker-entrypoint-initdb.d\30_setup_test_databases.sh
```

Expected output:

```text
True
True
True
True
False
```

- [ ] **Step 5: Commit the scaffold**

Run:

```bash
git add .gitattributes ckan-docker-prod/ckan/ckanext-idsk ckan-docker-prod/ckan/docker-entrypoint.d/01_setup_datapusher.sh ckan-docker-prod/postgresql/Dockerfile ckan-docker-prod/postgresql/docker-entrypoint-initdb.d/10_create_ckandb.sh ckan-docker-prod/postgresql/docker-entrypoint-initdb.d/20_create_datastore.sh
git commit -m "chore: scaffold CKAN production deployment"
```

Expected: commit succeeds and includes only the production scaffold plus `.gitattributes`.

---

### Task 2: Add The Production CKAN Image

**Files:**
- Create: `ckan-docker-prod/ckan/Dockerfile`

- [ ] **Step 1: Create the production CKAN Dockerfile**

Create `ckan-docker-prod/ckan/Dockerfile` with:

```dockerfile
FROM ckan/ckan-base:2.11

COPY --chown=ckan-sys:ckan-sys docker-entrypoint.d/* /docker-entrypoint.d/
COPY --chown=ckan-sys:ckan-sys ckanext-idsk /srv/app/src/ckanext-idsk

USER root

RUN pip3 install --no-cache-dir -e /srv/app/src/ckanext-idsk \
    && pip3 install --no-cache-dir ckanext-dcat ckanext-scheming

USER ckan
```

- [ ] **Step 2: Verify the Dockerfile references only production-local paths**

Run:

```powershell
Select-String -Path .\ckan-docker-prod\ckan\Dockerfile -Pattern "\.\./|\.\.\\|/srv/app/src/ckanext-idsk|ckanext-dcat|ckanext-scheming"
```

Expected: output includes `/srv/app/src/ckanext-idsk`, `ckanext-dcat`, and `ckanext-scheming`, and does not include `../` or `..\`.

- [ ] **Step 3: Commit the production CKAN image definition**

Run:

```bash
git add ckan-docker-prod/ckan/Dockerfile
git commit -m "build: add production CKAN image"
```

Expected: commit succeeds.

---

### Task 3: Add Production Environment Template

**Files:**
- Create: `ckan-docker-prod/.env.example`

- [ ] **Step 1: Create `.env.example`**

Create `ckan-docker-prod/.env.example` with:

```dotenv
# Host binding. External reverse proxies can route to http://127.0.0.1:${CKAN_PORT_HOST}
CKAN_PORT_HOST=5000
REVERSE_PROXY_NETWORK=reverse-proxy

# Site identity. Replace both URL values with the final public HTTPS URL before LKOD registration.
TZ=Europe/Bratislava
CKAN_SITE_ID=ckan-prod
CKAN__SITE_ID=ckan-prod
CKAN_SITE_URL=https://CHANGE-ME.example.sk
CKAN__SITE_URL=https://CHANGE-ME.example.sk
CKAN__SITE_TITLE=Open Data Portal
CKAN__SITE_DESCRIPTION=Open data portal for Slovak public data.
CKAN__LOCALE_DEFAULT=sk

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CHANGE_ME_POSTGRES_PASSWORD
POSTGRES_DB=postgres
POSTGRES_HOST=db
CKAN_DB_USER=ckandbuser
CKAN_DB_PASSWORD=CHANGE_ME_CKAN_DB_PASSWORD
CKAN_DB=ckandb
DATASTORE_READONLY_USER=datastore_ro
DATASTORE_READONLY_PASSWORD=CHANGE_ME_DATASTORE_PASSWORD
DATASTORE_DB=datastore
CKAN_SQLALCHEMY_URL=postgresql://ckandbuser:CHANGE_ME_CKAN_DB_PASSWORD@db/ckandb
CKAN_DATASTORE_WRITE_URL=postgresql://ckandbuser:CHANGE_ME_CKAN_DB_PASSWORD@db/datastore
CKAN_DATASTORE_READ_URL=postgresql://datastore_ro:CHANGE_ME_DATASTORE_PASSWORD@db/datastore

# CKAN secrets and admin user. Replace every CHANGE_ME value before exposing the portal.
CKAN___BEAKER__SESSION__SECRET=CHANGE_ME_SESSION_SECRET
CKAN___API_TOKEN__JWT__ENCODE__SECRET=string:CHANGE_ME_API_TOKEN_SECRET
CKAN___API_TOKEN__JWT__DECODE__SECRET=string:CHANGE_ME_API_TOKEN_SECRET
CKAN_SYSADMIN_NAME=ckan_admin
CKAN_SYSADMIN_PASSWORD=CHANGE_ME_ADMIN_PASSWORD
CKAN_SYSADMIN_EMAIL=admin@example.invalid

# Uploads and storage
CKAN_STORAGE_PATH=/var/lib/ckan
CKAN__STORAGE_PATH=/var/lib/ckan
CKAN__UPLOADS_ENABLED=true
CKAN__MAX_RESOURCE_SIZE=100
CKAN__MAX_IMAGE_SIZE=10
CKAN_MAX_UPLOAD_SIZE_MB=100

# Mail
CKAN_SMTP_SERVER=smtp.example.invalid:587
CKAN_SMTP_STARTTLS=True
CKAN_SMTP_USER=CHANGE_ME_SMTP_USER
CKAN_SMTP_PASSWORD=CHANGE_ME_SMTP_PASSWORD
CKAN_SMTP_MAIL_FROM=opendata@example.invalid

# Solr
SOLR_IMAGE_VERSION=2.11-solr9
CKAN_SOLR_URL=http://solr:8983/solr/ckan

# Redis
REDIS_VERSION=6
CKAN_REDIS_URL=redis://redis:6379/1
CKAN__REDIS__URL=redis://redis:6379/1

# DataPusher
DATAPUSHER_VERSION=0.0.21
CKAN_DATAPUSHER_URL=http://datapusher:8800
CKAN__DATAPUSHER__URL=http://datapusher:8800
CKAN__DATAPUSHER__CALLBACK_URL_BASE=http://ckan:5000
CKAN__DATAPUSHER__API_TOKEN=

# Extensions
CKAN__PLUGINS="image_view text_view datatables_view datastore datapusher envvars dcat dcat_json_interface structured_data scheming_datasets idsk_theme"
CKAN__VIEWS__DEFAULT_VIEWS="image_view text_view datatables_view"
CKANEXT__DCAT__RDF__PROFILES=euro_dcat_ap_2 euro_dcat_ap_scheming
CKAN___SCHEMING__DATASET_SCHEMAS=ckanext.idsk:schemas/dcat_ap_sk.yaml
CKAN___SCHEMING__PRESETS=ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml
CKANEXT__IDSK__DEFAULT_ORGANIZATION=minedu
CKANEXT__IDSK__DEFAULT_ORGANIZATION_TITLE=Ministerstvo skolstva
CKANEXT__IDSK__DEFAULT_ORGANIZATION_DESCRIPTION=Default open data publisher for this portal.

# Basic production hardening
CKAN__AUTH__CREATE_USER_VIA_WEB=false
CKAN__AUTH__PUBLIC_USER_DETAILS=false
```

- [ ] **Step 2: Verify the CKAN and Solr versions match**

Run:

```powershell
Select-String -Path .\ckan-docker-prod\.env.example -Pattern "SOLR_IMAGE_VERSION=2.11-solr9"
Select-String -Path .\ckan-docker-prod\ckan\Dockerfile -Pattern "ckan/ckan-base:2.11"
```

Expected: both commands print one matching line.

- [ ] **Step 3: Commit the environment template**

Run:

```bash
git add ckan-docker-prod/.env.example
git commit -m "config: add production environment template"
```

Expected: commit succeeds.

---

### Task 4: Add Production Compose Files

**Files:**
- Create: `ckan-docker-prod/docker-compose.yml`
- Create: `ckan-docker-prod/docker-compose.proxy.yml`

- [ ] **Step 1: Create the base production compose file**

Create `ckan-docker-prod/docker-compose.yml` with:

```yaml
name: ckan-docker-prod

volumes:
  ckan_storage:
  pg_data:
  solr_data:
  pip_cache:
  site_packages:

services:
  ckan:
    build:
      context: ./ckan
      dockerfile: Dockerfile
      args:
        TZ: ${TZ}
    networks:
      ckannet:
      dbnet:
      solrnet:
      redisnet:
    ports:
      - "127.0.0.1:${CKAN_PORT_HOST}:5000"
    environment:
      TZ: ${TZ}
      CKAN_SITE_ID: ${CKAN_SITE_ID}
      CKAN__SITE_ID: ${CKAN__SITE_ID}
      CKAN_SITE_URL: ${CKAN_SITE_URL}
      CKAN__SITE_URL: ${CKAN__SITE_URL}
      CKAN__SITE_TITLE: ${CKAN__SITE_TITLE}
      CKAN__SITE_DESCRIPTION: ${CKAN__SITE_DESCRIPTION}
      CKAN__LOCALE_DEFAULT: ${CKAN__LOCALE_DEFAULT}
      CKAN_SQLALCHEMY_URL: ${CKAN_SQLALCHEMY_URL}
      CKAN_DATASTORE_WRITE_URL: ${CKAN_DATASTORE_WRITE_URL}
      CKAN_DATASTORE_READ_URL: ${CKAN_DATASTORE_READ_URL}
      CKAN_SOLR_URL: ${CKAN_SOLR_URL}
      CKAN_REDIS_URL: ${CKAN_REDIS_URL}
      CKAN__REDIS__URL: ${CKAN__REDIS__URL}
      CKAN_DATAPUSHER_URL: ${CKAN_DATAPUSHER_URL}
      CKAN__DATAPUSHER__URL: ${CKAN__DATAPUSHER__URL}
      CKAN__DATAPUSHER__CALLBACK_URL_BASE: ${CKAN__DATAPUSHER__CALLBACK_URL_BASE}
      CKAN__DATAPUSHER__API_TOKEN: ${CKAN__DATAPUSHER__API_TOKEN}
      CKAN_STORAGE_PATH: ${CKAN_STORAGE_PATH}
      CKAN__STORAGE_PATH: ${CKAN__STORAGE_PATH}
      CKAN__UPLOADS_ENABLED: ${CKAN__UPLOADS_ENABLED}
      CKAN__MAX_RESOURCE_SIZE: ${CKAN__MAX_RESOURCE_SIZE}
      CKAN__MAX_IMAGE_SIZE: ${CKAN__MAX_IMAGE_SIZE}
      CKAN_MAX_UPLOAD_SIZE_MB: ${CKAN_MAX_UPLOAD_SIZE_MB}
      CKAN___BEAKER__SESSION__SECRET: ${CKAN___BEAKER__SESSION__SECRET}
      CKAN___API_TOKEN__JWT__ENCODE__SECRET: ${CKAN___API_TOKEN__JWT__ENCODE__SECRET}
      CKAN___API_TOKEN__JWT__DECODE__SECRET: ${CKAN___API_TOKEN__JWT__DECODE__SECRET}
      CKAN_SYSADMIN_NAME: ${CKAN_SYSADMIN_NAME}
      CKAN_SYSADMIN_PASSWORD: ${CKAN_SYSADMIN_PASSWORD}
      CKAN_SYSADMIN_EMAIL: ${CKAN_SYSADMIN_EMAIL}
      CKAN_SMTP_SERVER: ${CKAN_SMTP_SERVER}
      CKAN_SMTP_STARTTLS: ${CKAN_SMTP_STARTTLS}
      CKAN_SMTP_USER: ${CKAN_SMTP_USER}
      CKAN_SMTP_PASSWORD: ${CKAN_SMTP_PASSWORD}
      CKAN_SMTP_MAIL_FROM: ${CKAN_SMTP_MAIL_FROM}
      CKAN__PLUGINS: ${CKAN__PLUGINS}
      CKAN__VIEWS__DEFAULT_VIEWS: ${CKAN__VIEWS__DEFAULT_VIEWS}
      CKANEXT__DCAT__RDF__PROFILES: ${CKANEXT__DCAT__RDF__PROFILES}
      CKAN___SCHEMING__DATASET_SCHEMAS: ${CKAN___SCHEMING__DATASET_SCHEMAS}
      CKAN___SCHEMING__PRESETS: ${CKAN___SCHEMING__PRESETS}
      CKANEXT__IDSK__DEFAULT_ORGANIZATION: ${CKANEXT__IDSK__DEFAULT_ORGANIZATION}
      CKANEXT__IDSK__DEFAULT_ORGANIZATION_TITLE: ${CKANEXT__IDSK__DEFAULT_ORGANIZATION_TITLE}
      CKANEXT__IDSK__DEFAULT_ORGANIZATION_DESCRIPTION: ${CKANEXT__IDSK__DEFAULT_ORGANIZATION_DESCRIPTION}
      CKAN__AUTH__CREATE_USER_VIA_WEB: ${CKAN__AUTH__CREATE_USER_VIA_WEB}
      CKAN__AUTH__PUBLIC_USER_DETAILS: ${CKAN__AUTH__PUBLIC_USER_DETAILS}
    depends_on:
      db:
        condition: service_healthy
      solr:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ckan_storage:/var/lib/ckan
      - pip_cache:/root/.cache/pip
      - site_packages:/usr/lib/python3.10/site-packages
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-qO", "/dev/null", "http://localhost:5000/api/action/status_show"]
      interval: 60s
      timeout: 10s
      retries: 3

  datapusher:
    image: ckan/ckan-base-datapusher:${DATAPUSHER_VERSION}
    networks:
      ckannet:
      dbnet:
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-qO", "/dev/null", "http://localhost:8800"]
      interval: 60s
      timeout: 10s
      retries: 3

  db:
    build:
      context: ./postgresql
    networks:
      dbnet:
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
      CKAN_DB_USER: ${CKAN_DB_USER}
      CKAN_DB_PASSWORD: ${CKAN_DB_PASSWORD}
      CKAN_DB: ${CKAN_DB}
      DATASTORE_READONLY_USER: ${DATASTORE_READONLY_USER}
      DATASTORE_READONLY_PASSWORD: ${DATASTORE_READONLY_PASSWORD}
      DATASTORE_DB: ${DATASTORE_DB}
    volumes:
      - pg_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "${POSTGRES_USER}", "-d", "${POSTGRES_DB}"]
      interval: 30s
      timeout: 10s
      retries: 5

  solr:
    image: ckan/ckan-solr:${SOLR_IMAGE_VERSION}
    networks:
      solrnet:
    volumes:
      - solr_data:/var/solr
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-qO", "/dev/null", "http://localhost:8983/solr/"]
      interval: 30s
      timeout: 10s
      retries: 5

  redis:
    image: redis:${REDIS_VERSION}
    networks:
      redisnet:
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "-e", "QUIT"]
      interval: 30s
      timeout: 10s
      retries: 5

networks:
  ckannet:
  dbnet:
    internal: true
  solrnet:
    internal: true
  redisnet:
    internal: true
```

- [ ] **Step 2: Create the optional reverse proxy network override**

Create `ckan-docker-prod/docker-compose.proxy.yml` with:

```yaml
services:
  ckan:
    networks:
      reverse-proxy:
        aliases:
          - ckan-prod

networks:
  reverse-proxy:
    external: true
    name: ${REVERSE_PROXY_NETWORK}
```

- [ ] **Step 3: Validate compose rendering with `.env.example`**

Run:

```powershell
docker compose --env-file .\ckan-docker-prod\.env.example -f .\ckan-docker-prod\docker-compose.yml config
```

Expected: command exits with code 0 and prints rendered compose YAML.

- [ ] **Step 4: Validate compose rendering with the proxy override**

Run:

```powershell
docker compose --env-file .\ckan-docker-prod\.env.example -f .\ckan-docker-prod\docker-compose.yml -f .\ckan-docker-prod\docker-compose.proxy.yml config
```

Expected: command exits with code 0 and rendered YAML includes `reverse-proxy` and alias `ckan-prod`.

- [ ] **Step 5: Commit the compose files**

Run:

```bash
git add ckan-docker-prod/docker-compose.yml ckan-docker-prod/docker-compose.proxy.yml
git commit -m "feat: add production Docker Compose stack"
```

Expected: commit succeeds.

---

### Task 5: Add Non-Destructive Runtime Verification

**Files:**
- Create: `ckan-docker-prod/bin/verify-prod`

- [ ] **Step 1: Create the smoke check script**

Create `ckan-docker-prod/bin/verify-prod` with:

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

if [ ! -f .env ]; then
  echo "Missing .env. Copy .env.example to .env and set production values first." >&2
  exit 1
fi

docker compose ps --status running >/dev/null

docker compose exec -T ckan wget -qO- http://localhost:5000/api/action/status_show | grep -q '"success": true'
docker compose exec -T ckan wget -qO- http://localhost:5000/catalog.ttl | grep -q "dcat:Catalog"

docker compose exec -T ckan sh -c "grep -q '^ckan.uploads_enabled = true$' /srv/app/ckan.ini"
docker compose exec -T ckan sh -c "grep -q '^ckan.locale_default = sk$' /srv/app/ckan.ini"

site_url="$(docker compose exec -T ckan sh -c "grep '^ckan.site_url = ' /srv/app/ckan.ini | sed 's/^ckan.site_url = //'")"
echo "CKAN site URL: $site_url"

if [ "$site_url" = "https://CHANGE-ME.example.sk" ]; then
  echo "Warning: CKAN_SITE_URL still uses the example value. Do not register LKOD until this is the final public HTTPS URL." >&2
fi

echo "Production smoke check passed."
```

- [ ] **Step 2: Verify the script contains no dataset mutation commands**

Run:

```powershell
Select-String -Path .\ckan-docker-prod\bin\verify-prod -Pattern "package_create|resource_create|package_delete|resource_delete|organization_create"
```

Expected: command prints no matches.

- [ ] **Step 3: Verify the script starts with a bash shebang**

Run:

```powershell
Get-Content .\ckan-docker-prod\bin\verify-prod -TotalCount 1
```

Expected output:

```text
#!/usr/bin/env bash
```

- [ ] **Step 4: Commit the verification script**

Run:

```bash
git add ckan-docker-prod/bin/verify-prod
git commit -m "test: add production smoke check"
```

Expected: commit succeeds.

---

### Task 6: Add Production Operator Documentation

**Files:**
- Create: `ckan-docker-prod/README.md`

- [ ] **Step 1: Create `README.md`**

Create `ckan-docker-prod/README.md` with:

```markdown
# CKAN Docker Production Deployment

This folder contains a standalone production deployment for a CKAN open data portal with DCAT export for LKOD registration.

The stack does not terminate public HTTPS. Put it behind an external reverse proxy such as nginx, Caddy, or Traefik.

## Services

- CKAN 2.11
- PostgreSQL
- Solr
- Redis
- DataPusher

## First Setup

Copy the environment template:

```bash
cp .env.example .env
```

Edit `.env` before exposing the portal:

- Replace `CKAN_SITE_URL` and `CKAN__SITE_URL` with the final public HTTPS URL.
- Replace every `CHANGE_ME` secret.
- Set a real `CKAN_SYSADMIN_EMAIL`.
- Set SMTP values if password reset or mail notifications are required.

Do not register the LKOD catalog while `CKAN_SITE_URL` is `https://CHANGE-ME.example.sk`.

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
- upload configuration
- Slovak locale configuration
- configured public site URL

## Default Organization

If the IDSK extension CLI is available, create or verify the default organization:

```bash
docker compose exec -T ckan ckan -c /srv/app/ckan.ini idsk ensure-default-organization
```

If the CLI is not available in the deployed extension version, create organization `minedu` manually in CKAN before publishing datasets.

## LKOD Publication Checklist

Before registering the catalog URL through the Slovak open data publication flow:

- The public reverse proxy serves the portal over trusted HTTPS.
- `CKAN_SITE_URL` and `CKAN__SITE_URL` match the public HTTPS URL.
- At least one public dataset exists.
- The dataset has at least one resource or distribution.
- The catalog URL is publicly reachable:

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
```

- [ ] **Step 2: Verify the documentation mentions the required LKOD URL**

Run:

```powershell
Select-String -Path .\ckan-docker-prod\README.md -Pattern "catalog.ttl|CKAN_SITE_URL|reverse proxy"
```

Expected: output includes matches for all three terms.

- [ ] **Step 3: Commit the operator documentation**

Run:

```bash
git add ckan-docker-prod/README.md
git commit -m "docs: add production deployment guide"
```

Expected: commit succeeds.

---

### Task 7: Final Static Verification

**Files:**
- Verify: `ckan-docker-prod/docker-compose.yml`
- Verify: `ckan-docker-prod/docker-compose.proxy.yml`
- Verify: `ckan-docker-prod/.env.example`
- Verify: `ckan-docker-prod/README.md`
- Verify: `ckan-docker-prod/bin/verify-prod`

- [ ] **Step 1: Check the production folder file list**

Run:

```powershell
Get-ChildItem -Recurse .\ckan-docker-prod | Select-Object -ExpandProperty FullName
```

Expected: output includes:

```text
ckan-docker-prod\.env.example
ckan-docker-prod\README.md
ckan-docker-prod\docker-compose.yml
ckan-docker-prod\docker-compose.proxy.yml
ckan-docker-prod\bin\verify-prod
ckan-docker-prod\ckan\Dockerfile
ckan-docker-prod\ckan\docker-entrypoint.d\01_setup_datapusher.sh
ckan-docker-prod\ckan\ckanext-idsk\setup.py
ckan-docker-prod\postgresql\Dockerfile
ckan-docker-prod\postgresql\docker-entrypoint-initdb.d\10_create_ckandb.sh
ckan-docker-prod\postgresql\docker-entrypoint-initdb.d\20_create_datastore.sh
```

- [ ] **Step 2: Confirm the production stack does not include nginx**

Run:

```powershell
Select-String -Path .\ckan-docker-prod\docker-compose.yml -Pattern "nginx"
```

Expected: command prints no matches.

- [ ] **Step 3: Confirm CKAN binds only to localhost by default**

Run:

```powershell
Select-String -Path .\ckan-docker-prod\docker-compose.yml -Pattern "127.0.0.1:\$\{CKAN_PORT_HOST\}:5000"
```

Expected: command prints the CKAN port mapping.

- [ ] **Step 4: Confirm the production PostgreSQL init does not create test databases**

Run:

```powershell
Test-Path .\ckan-docker-prod\postgresql\docker-entrypoint-initdb.d\30_setup_test_databases.sh
```

Expected output:

```text
False
```

- [ ] **Step 5: Render the base compose configuration**

Run:

```powershell
docker compose --env-file .\ckan-docker-prod\.env.example -f .\ckan-docker-prod\docker-compose.yml config
```

Expected: command exits with code 0. The rendered output includes services `ckan`, `db`, `solr`, `redis`, and `datapusher`.

- [ ] **Step 6: Render the proxy compose configuration**

Run:

```powershell
docker compose --env-file .\ckan-docker-prod\.env.example -f .\ckan-docker-prod\docker-compose.yml -f .\ckan-docker-prod\docker-compose.proxy.yml config
```

Expected: command exits with code 0. The rendered output includes external network `reverse-proxy`.

- [ ] **Step 7: Check final git status**

Run:

```bash
git status --short
```

Expected: only unrelated pre-existing working tree changes remain. If files under `ckan-docker-prod/` are shown as modified or untracked, review and commit them before completion.

