# DataHub Branding And Demo Data Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the standalone CKAN production bundle show `DataHub Open Data`, remove visible CKAN branding, seed the `minedu` organization plus a demo schools CSV dataset, and document the catalog URL.

**Architecture:** Add a tiny production-only CKAN extension that only registers template overrides and keeps the default CKAN layout. Keep all production settings driven by `.env` and the existing startup config script. Add an idempotent Bash seed command that uses local `ckanapi` inside the CKAN container, avoiding API token handling.

**Tech Stack:** CKAN 2.11, CKAN plugins/templates, Docker Compose, Bash, ckanapi, ckanext-dcat, ckanext-scheming.

---

## File Structure

- Create `ckan-docker-prod/ckan/ckanext-datahub/setup.py`: installable CKAN extension package metadata and plugin entry point.
- Create `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/__init__.py`: package marker.
- Create `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/plugin.py`: minimal `IConfigurer` plugin that registers templates.
- Create `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/templates/footer.html`: default CKAN footer override with DataHub branding and no visible CKAN links.
- Modify `ckan-docker-prod/ckan/Dockerfile`: copy and install `ckanext-datahub`.
- Modify `ckan-docker-prod/.env.example`: tracked production template with DataHub title, description, plugin, and `minedu` defaults.
- Modify `ckan-docker-prod/.env`: local ignored runtime env, changing only non-secret branding and organization lines.
- Modify `ckan-docker-prod/ckan/docker-entrypoint.d/02_setup_prod_config.sh`: write title and description into `ckan.ini` on startup.
- Modify `ckan-docker-prod/bin/verify-prod`: add branding smoke checks.
- Create `ckan-docker-prod/bin/seed-demo-data`: idempotent demo organization, dataset, and CSV resource seeding command.
- Modify `ckan-docker-prod/README.md`: document DataHub branding, seed command, and catalog URLs.

### Task 1: Add Branding Smoke Checks

**Files:**
- Modify: `ckan-docker-prod/bin/verify-prod`

- [ ] **Step 1: Replace `verify-prod` with checks that currently fail**

Use this full file content:

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

status_json="$(docker compose exec -T ckan wget -qO- http://localhost:5000/api/action/status_show)"
printf '%s' "$status_json" | grep -q '"success": true'
printf '%s' "$status_json" | grep -q '"datahub_branding"'
printf '%s' "$status_json" | grep -Eq '"site_title" ?: ?"DataHub Open Data"'

docker compose exec -T ckan wget -qO- http://localhost:5000/catalog.ttl | grep -q "dcat:Catalog"

docker compose exec -T ckan sh -c "grep -Eq '^ckan.site_url ?= ?' /srv/app/ckan.ini"
docker compose exec -T ckan sh -c "grep -Eq '^ckan.site_title ?= ?DataHub Open Data$' /srv/app/ckan.ini"
docker compose exec -T ckan sh -c "grep -Eq '^ckan.site_description ?= ?Katalog otvorenych dat$' /srv/app/ckan.ini"
docker compose exec -T ckan sh -c "grep -Eq '^ckan.uploads_enabled ?= ?true$' /srv/app/ckan.ini"
docker compose exec -T ckan sh -c "grep -Eq '^ckan.locale_default ?= ?sk$' /srv/app/ckan.ini"
docker compose exec -T ckan sh -c "grep -Eq '^scheming.dataset_schemas ?= ?ckanext.idsk:schemas/dcat_ap_sk.yaml$' /srv/app/ckan.ini"
docker compose exec -T ckan sh -c "grep -Eq '^ckanext.dcat.rdf.profiles ?= ?euro_dcat_ap_2 euro_dcat_ap_scheming$' /srv/app/ckan.ini"

home_html="$(docker compose exec -T ckan wget -qO- http://localhost:5000)"
printf '%s' "$home_html" | grep -q "DataHub Open Data"
if printf '%s' "$home_html" | grep -Eq "Powered by CKAN|CKAN API|CKAN Association|ckan-footer-logo"; then
  echo "Visible CKAN branding is still present on the homepage." >&2
  exit 1
fi

site_url="$(docker compose exec -T ckan sh -c "grep -E '^ckan.site_url ?= ?' /srv/app/ckan.ini | sed -E 's/^ckan.site_url ?= ?//'")"
echo "CKAN site URL: $site_url"

if [ "$site_url" = "https://CHANGE-ME.example.sk" ] || [ "$site_url" = "http://localhost:5000" ]; then
  echo "Warning: CKAN_SITE_URL is not a final public HTTPS URL. Do not register LKOD until this is updated." >&2
fi

echo "Production smoke check passed."
```

- [ ] **Step 2: Run the smoke check to verify the expected failure**

Run from `ckan-docker-prod`:

```bash
bash bin/verify-prod
```

Expected: FAIL because the running stack does not yet expose the `datahub_branding` plugin or `DataHub Open Data`.

### Task 2: Add The DataHub Branding Extension

**Files:**
- Create: `ckan-docker-prod/ckan/ckanext-datahub/setup.py`
- Create: `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/__init__.py`
- Create: `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/plugin.py`
- Create: `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/templates/footer.html`
- Modify: `ckan-docker-prod/ckan/Dockerfile`
- Modify: `ckan-docker-prod/.env.example`
- Modify: `ckan-docker-prod/.env`
- Modify: `ckan-docker-prod/ckan/docker-entrypoint.d/02_setup_prod_config.sh`

- [ ] **Step 1: Create the extension setup file**

Create `ckan-docker-prod/ckan/ckanext-datahub/setup.py`:

```python
from setuptools import find_namespace_packages, setup

setup(
    name="ckanext-datahub",
    version="0.1.0",
    packages=find_namespace_packages(include=["ckanext.*"]),
    include_package_data=True,
    package_data={
        "ckanext.datahub": [
            "templates/*.html",
        ],
    },
    entry_points="""
        [ckan.plugins]
        datahub_branding=ckanext.datahub.plugin:DataHubBrandingPlugin
    """,
)
```

- [ ] **Step 2: Create the package marker**

Create `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/__init__.py`:

```python
"""DataHub Open Data CKAN branding extension."""
```

- [ ] **Step 3: Create the CKAN plugin**

Create `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/plugin.py`:

```python
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class DataHubBrandingPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    def update_config(self, config):
        toolkit.add_template_directory(config, "templates")
```

- [ ] **Step 4: Override only the default footer**

Create `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/templates/footer.html`:

```html
{% set dataset_type = h.default_package_type() %}
{% set org_type = h.default_group_type('organization') %}

<footer class="site-footer">
  <div class="container">
    {% block footer_content %}
    <div class="row">
      <div class="col-md-8 footer-links">
        {% block footer_nav %}
          <ul class="list-unstyled">
            {% block footer_links %}
              <li><a href="{{ h.url_for('home.about') }}">{{ _('About {0}').format(g.site_title) }}</a></li>
              <li><a href="{{ h.url_for(dataset_type ~ '.search') }}">{{ _('Datasets') }}</a></li>
              <li><a href="{{ h.url_for(org_type ~ '.index') }}">{{ _('Organizations') }}</a></li>
            {% endblock %}
          </ul>
        {% endblock %}
      </div>
      <div class="col-md-4 attribution">
        {% block footer_attribution %}
          <p><strong>DataHub Open Data</strong></p>
          {% if g.site_description %}
            <p>{{ g.site_description }}</p>
          {% endif %}
        {% endblock %}
        {% block footer_lang %}
          {% snippet "snippets/language_selector.html" %}
        {% endblock %}
      </div>
    </div>
    {% endblock %}
  </div>
</footer>
```

- [ ] **Step 5: Install the extension in the production CKAN image**

Replace `ckan-docker-prod/ckan/Dockerfile` with:

```dockerfile
FROM ckan/ckan-base:2.11

COPY --chown=ckan-sys:ckan-sys docker-entrypoint.d/* /docker-entrypoint.d/
COPY --chown=ckan-sys:ckan-sys ckanext-idsk /srv/app/src/ckanext-idsk
COPY --chown=ckan-sys:ckan-sys ckanext-datahub /srv/app/src/ckanext-datahub

USER root

RUN pip3 install --no-cache-dir -e /srv/app/src/ckanext-idsk \
    && pip3 install --no-cache-dir -e /srv/app/src/ckanext-datahub \
    && pip3 install --no-cache-dir ckanext-dcat ckanext-scheming

USER ckan
```

- [ ] **Step 6: Update tracked production defaults**

In `ckan-docker-prod/.env.example`, set these non-secret values:

```dotenv
CKAN__SITE_TITLE=DataHub Open Data
CKAN__SITE_DESCRIPTION=Katalog otvorenych dat
CKAN__PLUGINS="image_view text_view datatables_view datastore datapusher envvars dcat dcat_json_interface structured_data scheming_datasets datahub_branding"
CKANEXT__IDSK__DEFAULT_ORGANIZATION=minedu
CKANEXT__IDSK__DEFAULT_ORGANIZATION_TITLE=Ministerstvo skolstva, vyskumu, vyvoja a mladeze Slovenskej republiky
CKANEXT__IDSK__DEFAULT_ORGANIZATION_DESCRIPTION=Default open data publisher for this portal.
```

- [ ] **Step 7: Update the local ignored runtime env**

In `ckan-docker-prod/.env`, change only these non-secret lines:

```dotenv
CKAN__SITE_TITLE=DataHub Open Data
CKAN__SITE_DESCRIPTION=Katalog otvorenych dat
CKAN__PLUGINS="image_view text_view datatables_view datastore datapusher envvars dcat dcat_json_interface structured_data scheming_datasets datahub_branding"
CKANEXT__IDSK__DEFAULT_ORGANIZATION=minedu
CKANEXT__IDSK__DEFAULT_ORGANIZATION_TITLE=Ministerstvo skolstva, vyskumu, vyvoja a mladeze Slovenskej republiky
CKANEXT__IDSK__DEFAULT_ORGANIZATION_DESCRIPTION=Default open data publisher for this portal.
```

- [ ] **Step 8: Apply title and description during CKAN startup**

Replace `ckan-docker-prod/ckan/docker-entrypoint.d/02_setup_prod_config.sh` with:

```bash
#!/bin/bash
set -e

echo "Applying production CKAN configuration"

ckan config-tool "$CKAN_INI" "ckan.site_url=${CKAN__SITE_URL:-$CKAN_SITE_URL}"
ckan config-tool "$CKAN_INI" "ckan.site_title=${CKAN__SITE_TITLE:-DataHub Open Data}"
ckan config-tool "$CKAN_INI" "ckan.site_description=${CKAN__SITE_DESCRIPTION:-Katalog otvorenych dat}"
ckan config-tool "$CKAN_INI" "ckan.locale_default=${CKAN__LOCALE_DEFAULT:-sk}"
ckan config-tool "$CKAN_INI" "ckan.uploads_enabled=${CKAN__UPLOADS_ENABLED:-true}"
ckan config-tool "$CKAN_INI" "ckan.storage_path=${CKAN__STORAGE_PATH:-$CKAN_STORAGE_PATH}"
ckan config-tool "$CKAN_INI" "ckan.max_resource_size=${CKAN__MAX_RESOURCE_SIZE:-100}"
ckan config-tool "$CKAN_INI" "ckan.max_image_size=${CKAN__MAX_IMAGE_SIZE:-10}"

ckan config-tool "$CKAN_INI" "ckan.datapusher.url=${CKAN__DATAPUSHER__URL:-$CKAN_DATAPUSHER_URL}"
ckan config-tool "$CKAN_INI" "ckan.datapusher.callback_url_base=${CKAN__DATAPUSHER__CALLBACK_URL_BASE:-http://ckan:5000}"
ckan config-tool "$CKAN_INI" "ckan.datapusher.api_token=${CKAN__DATAPUSHER__API_TOKEN}"

ckan config-tool "$CKAN_INI" "scheming.dataset_schemas=${CKAN___SCHEMING__DATASET_SCHEMAS:-ckanext.idsk:schemas/dcat_ap_sk.yaml}"
ckan config-tool "$CKAN_INI" "scheming.presets=${CKAN___SCHEMING__PRESETS:-ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml}"
ckan config-tool "$CKAN_INI" "ckanext.dcat.rdf.profiles=${CKANEXT__DCAT__RDF__PROFILES:-euro_dcat_ap_2 euro_dcat_ap_scheming}"
```

- [ ] **Step 9: Rebuild and restart the stack**

Run from `ckan-docker-prod`:

```bash
docker compose up -d --build
```

Expected: CKAN image rebuilds, services become running or healthy.

- [ ] **Step 10: Run the smoke check to verify branding passes**

Run:

```bash
bash bin/verify-prod
```

Expected: PASS with `Production smoke check passed.`

- [ ] **Step 11: Commit branding changes**

```bash
git add ckan-docker-prod/ckan/Dockerfile ckan-docker-prod/ckan/ckanext-datahub ckan-docker-prod/.env.example ckan-docker-prod/ckan/docker-entrypoint.d/02_setup_prod_config.sh ckan-docker-prod/bin/verify-prod
git commit -m "feat: add DataHub branding to production CKAN"
```

### Task 3: Add Demo Data Seed Command

**Files:**
- Create: `ckan-docker-prod/bin/seed-demo-data`

- [ ] **Step 1: Create the seed command**

Create `ckan-docker-prod/bin/seed-demo-data`:

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

docker compose ps --status running ckan >/dev/null

docker compose exec -T ckan bash -s <<'REMOTE'
set -euo pipefail

CONFIG=/srv/app/ckan.ini
CKAN_USER="${CKAN_SYSADMIN_NAME:-ckan_admin}"
CSV=/tmp/datahub-demo-schools.csv
PACKAGE_ID=testovaci-zoznam-skol
RESOURCE_NAME="Zoznam skol - demo CSV"

cat > "$CSV" <<'CSV'
nazov_skoly,typ_skoly,obec,okres,kraj
Zakladna skola Demo 01,zakladna skola,Bratislava,Bratislava I,Bratislavsky
Gymnazium Demo 02,gymnazium,Kosice,Kosice I,Kosicky
Stredna odborna skola Demo 03,stredna odborna skola,Zilina,Zilina,Zilinsky
Zakladna skola Demo 04,zakladna skola,Nitra,Nitra,Nitriansky
Gymnazium Demo 05,gymnazium,Presov,Presov,Presovsky
Stredna priemyselna skola Demo 06,stredna odborna skola,Trnava,Trnava,Trnavsky
Zakladna skola Demo 07,zakladna skola,Banska Bystrica,Banska Bystrica,Banskobystricky
Spojena skola Demo 08,spojena skola,Trencin,Trencin,Trenciansky
Zakladna skola Demo 09,zakladna skola,Martin,Martin,Zilinsky
Gymnazium Demo 10,gymnazium,Poprad,Poprad,Presovsky
CSV

if ckanapi -c "$CONFIG" -u "$CKAN_USER" action organization_show id=minedu -j >/tmp/datahub-org.json 2>/tmp/datahub-org.err; then
  ckanapi -c "$CONFIG" -u "$CKAN_USER" action organization_patch \
    id=minedu \
    title="Ministerstvo školstva, výskumu, vývoja a mládeže Slovenskej republiky" \
    description="Publikacna organizacia pre otvorene data rezortu skolstva." \
    state=active >/dev/null
else
  ckanapi -c "$CONFIG" -u "$CKAN_USER" action organization_create \
    name=minedu \
    title="Ministerstvo školstva, výskumu, vývoja a mládeže Slovenskej republiky" \
    description="Publikacna organizacia pre otvorene data rezortu skolstva." \
    state=active >/dev/null
fi

if ckanapi -c "$CONFIG" -u "$CKAN_USER" action package_show id="$PACKAGE_ID" -j >/tmp/datahub-package.json 2>/tmp/datahub-package.err; then
  ckanapi -c "$CONFIG" -u "$CKAN_USER" action package_patch \
    id="$PACKAGE_ID" \
    title="Testovaci zoznam skol" \
    notes="Synteticky testovaci dataset s 10 skolami na overenie publikovania CSV zdroja a DCAT katalogu." \
    owner_org=minedu \
    theme=http://publications.europa.eu/resource/authority/data-theme/EDUC \
    frequency=http://publications.europa.eu/resource/authority/frequency/ANNUAL \
    license_id=cc-by \
    tag_string=demo,skoly,vzdelavanie \
    contact_name="DataHub Open Data" \
    contact_email=opendata@example.gov.sk \
    private:false >/dev/null
else
  ckanapi -c "$CONFIG" -u "$CKAN_USER" action package_create \
    name="$PACKAGE_ID" \
    title="Testovaci zoznam skol" \
    notes="Synteticky testovaci dataset s 10 skolami na overenie publikovania CSV zdroja a DCAT katalogu." \
    owner_org=minedu \
    theme=http://publications.europa.eu/resource/authority/data-theme/EDUC \
    frequency=http://publications.europa.eu/resource/authority/frequency/ANNUAL \
    license_id=cc-by \
    tag_string=demo,skoly,vzdelavanie \
    contact_name="DataHub Open Data" \
    contact_email=opendata@example.gov.sk \
    private:false >/dev/null
fi

ckanapi -c "$CONFIG" -u "$CKAN_USER" action package_show id="$PACKAGE_ID" -j >/tmp/datahub-package.json

resource_id="$(python3 - <<'PY'
import json

with open("/tmp/datahub-package.json", encoding="utf-8") as package_file:
    package = json.load(package_file)

for resource in package.get("resources", []):
    if resource.get("name") == "Zoznam skol - demo CSV":
        print(resource["id"])
        break
PY
)"

if [ -n "$resource_id" ]; then
  ckanapi -c "$CONFIG" -u "$CKAN_USER" action resource_patch \
    id="$resource_id" \
    name="$RESOURCE_NAME" \
    description="Synteticky CSV subor s 10 demo skolami." \
    format=CSV \
    upload@"$CSV" >/dev/null
else
  ckanapi -c "$CONFIG" -u "$CKAN_USER" action resource_create \
    package_id="$PACKAGE_ID" \
    name="$RESOURCE_NAME" \
    description="Synteticky CSV subor s 10 demo skolami." \
    format=CSV \
    upload@"$CSV" >/dev/null
fi

ckan -c "$CONFIG" search-index rebuild -q "$PACKAGE_ID"

site_url="$(ckanapi -c "$CONFIG" -u "$CKAN_USER" action status_show -j | python3 -c 'import json, sys; print(json.load(sys.stdin)["site_url"].rstrip("/"))')"

echo "Demo data seeded."
echo "Organization: ${site_url}/organization/minedu"
echo "Dataset: ${site_url}/dataset/testovaci-zoznam-skol"
echo "Catalog: ${site_url}/catalog.ttl"
REMOTE
```

- [ ] **Step 2: Run the seed command**

Run from `ckan-docker-prod`:

```bash
bash bin/seed-demo-data
```

Expected output includes:

```text
Demo data seeded.
Organization: http://localhost:5000/organization/minedu
Dataset: http://localhost:5000/dataset/testovaci-zoznam-skol
Catalog: http://localhost:5000/catalog.ttl
```

- [ ] **Step 3: Verify the organization exists**

Run:

```bash
docker compose exec -T ckan ckanapi -c /srv/app/ckan.ini -u ckan_admin action organization_show id=minedu -j | grep -q '"name":"minedu"'
```

Expected: command exits 0.

- [ ] **Step 4: Verify the demo dataset and 10-row CSV resource**

Run:

```bash
docker compose exec -T ckan ckanapi -c /srv/app/ckan.ini -u ckan_admin action package_show id=testovaci-zoznam-skol -j > /tmp/datahub-package.json
python - <<'PY'
import json
from pathlib import Path

package = json.loads(Path("/tmp/datahub-package.json").read_text(encoding="utf-8"))
assert package["name"] == "testovaci-zoznam-skol"
assert package["owner_org"]
resource = next(r for r in package["resources"] if r["name"] == "Zoznam skol - demo CSV")
assert resource["format"] == "CSV"
print(resource["id"])
PY
```

Expected: command exits 0 and prints one resource id.

- [ ] **Step 5: Verify the dataset appears in DCAT**

Run:

```bash
docker compose exec -T ckan wget -qO- http://localhost:5000/catalog.ttl | grep -q "testovaci-zoznam-skol"
docker compose exec -T ckan wget -qO- http://localhost:5000/dataset/testovaci-zoznam-skol.ttl | grep -q "dcat:Dataset"
```

Expected: both commands exit 0.

- [ ] **Step 6: Run the seed command again to verify idempotency**

Run:

```bash
bash bin/seed-demo-data
```

Expected: PASS and no duplicate resource named `Zoznam skol - demo CSV`.

- [ ] **Step 7: Commit seed command**

```bash
git add ckan-docker-prod/bin/seed-demo-data
git commit -m "feat: add production demo data seed command"
```

### Task 4: Document DataHub Branding, Seed Data, And Catalog URL

**Files:**
- Modify: `ckan-docker-prod/README.md`

- [ ] **Step 1: Add the DataHub branding note after the services list**

Add this section after `## Services`:

```markdown
## Branding

The production bundle uses the default CKAN layout with a small DataHub branding extension. Users should see `DataHub Open Data` instead of visible CKAN branding such as `Powered by CKAN`.
```

- [ ] **Step 2: Replace the default organization section with seed instructions**

Replace the existing `## Default Organization` section with:

```markdown
## Demo Organization And Dataset

Seed the default publisher organization and demo schools dataset after the stack is running:

```bash
bash bin/seed-demo-data
```

The command creates or updates:

- organization `minedu`
- dataset `testovaci-zoznam-skol`
- one uploaded CSV resource with 10 synthetic school rows

The command is idempotent and can be run repeatedly without creating duplicate organizations, datasets, or resources.
```

- [ ] **Step 3: Add explicit local and public catalog URLs**

In `## LKOD Publication Checklist`, keep the existing public URL warning and add:

```markdown
For local testing on this machine, the catalog URL is:

```text
http://localhost:5000/catalog.ttl
```

For slovensko.sk registration, use the public HTTPS URL exposed by the server reverse proxy:

```text
https://tvoja-domena.sk/catalog.ttl
```
```

- [ ] **Step 4: Run final verification**

Run from `ckan-docker-prod`:

```bash
bash bin/verify-prod
bash bin/seed-demo-data
docker compose exec -T ckan wget -qO- http://localhost:5000/catalog.ttl | grep -q "testovaci-zoznam-skol"
```

Expected: all commands exit 0.

- [ ] **Step 5: Commit documentation**

```bash
git add ckan-docker-prod/README.md
git commit -m "docs: document DataHub seed data and catalog URL"
```

## Final Verification

Run from `ckan-docker-prod`:

```bash
docker compose ps
bash bin/verify-prod
bash bin/seed-demo-data
docker compose exec -T ckan wget -qO- http://localhost:5000 | grep -q "DataHub Open Data"
docker compose exec -T ckan wget -qO- http://localhost:5000 | grep -Eq "Powered by CKAN|CKAN API|CKAN Association|ckan-footer-logo" && exit 1 || true
docker compose exec -T ckan wget -qO- http://localhost:5000/catalog.ttl | grep -q "testovaci-zoznam-skol"
```

Expected:

- services are running
- production smoke check passes
- seed command passes
- homepage contains `DataHub Open Data`
- homepage does not contain visible CKAN branding
- catalog contains `testovaci-zoznam-skol`

## Catalog URL To Give The User

For this local machine:

```text
http://localhost:5000/catalog.ttl
```

For slovensko.sk after server deployment behind the public reverse proxy:

```text
https://tvoja-domena.sk/catalog.ttl
```
