# CKAN IDSK LKOD Portal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the current CKAN Docker project into a one-institution IDSK-styled LKOD publishing portal with upload, required metadata, and harvestable DCAT links.

**Architecture:** Keep CKAN as the backend for users, organizations, datasets, resources, storage, DataStore, DataPusher, and DCAT endpoints. Extend the existing `ckanext-idsk` extension with focused helpers, schema, RDF profile hooks, and IDSK templates for the publisher workflow. Stabilize Docker/runtime configuration before building UI on top of it.

**Tech Stack:** CKAN 2.11, Docker Compose, ckanext-dcat, ckanext-scheming, Jinja2 templates, pytest, shell smoke checks, ID-SK Frontend assets.

---

## File Structure

- Modify `.env`: correct CKAN envvar mappings for upload, locale, scheming, DCAT profiles, site metadata, and default organization settings.
- Modify `.gitattributes`: force shell scripts to LF so Docker entrypoint scripts run on Linux.
- Modify `ckan/Dockerfile`: install `ckanext-scheming` alongside `ckanext-dcat`.
- Modify `ckan/docker-entrypoint.d/01_setup_datapusher.sh`: normalize LF and keep the existing DataPusher token setup logic.
- Modify `ckan/ckanext-idsk/setup.py`: add package data and RDF profile entry points.
- Modify `ckan/ckanext-idsk/ckanext/idsk/plugin.py`: register templates/assets, expose template helpers, register CLI commands.
- Create `ckan/ckanext-idsk/ckanext/idsk/organization.py`: default organization lookup and creation helper.
- Create `ckan/ckanext-idsk/ckanext/idsk/cli.py`: CKAN CLI command to ensure default organization.
- Create `ckan/ckanext-idsk/ckanext/idsk/profiles.py`: Slovak profile extension hook for DCAT serialization.
- Create `ckan/ckanext-idsk/ckanext/idsk/schemas/dcat_ap_sk.yaml`: ckanext-scheming dataset schema.
- Create `ckan/ckanext-idsk/ckanext/idsk/templates/package/snippets/package_form.html`: IDSK dataset metadata form.
- Create `ckan/ckanext-idsk/ckanext/idsk/templates/package/snippets/resource_form.html`: IDSK resource upload form.
- Create `ckan/ckanext-idsk/ckanext/idsk/templates/package/read.html`: dataset detail with DCAT links.
- Create `ckan/ckanext-idsk/ckanext/idsk/templates/user/login.html`: IDSK login page.
- Create `ckan/ckanext-idsk/ckanext/idsk/templates/dashboard/index.html`: publisher dashboard entry point.
- Create `ckan/ckanext-idsk/ckanext/idsk/public/css/idsk-ckan.css`: small bridge stylesheet for CKAN markup that remains visible.
- Create `ckan/ckanext-idsk/ckanext/idsk/tests/test_organization.py`: unit tests for default organization helper.
- Create `ckan/ckanext-idsk/ckanext/idsk/tests/test_helpers.py`: unit tests for published link helpers.
- Create `ckan/ckanext-idsk/ckanext/idsk/tests/test_profiles.py`: unit tests for RDF output expectations.
- Create `bin/verify_lkod_runtime`: smoke verification for Docker, static assets, upload config, and DCAT endpoints.

## Task 1: Runtime Stabilization

**Files:**
- Modify: `.env`
- Modify: `.gitattributes`
- Modify: `ckan/Dockerfile`
- Modify: `ckan/docker-entrypoint.d/01_setup_datapusher.sh`
- Modify: `ckan/ckanext-idsk/ckanext/idsk/templates/header.html`
- Modify: `ckan/ckanext-idsk/ckanext/idsk/templates/footer.html`
- Modify: `ckan/ckanext-idsk/ckanext/idsk/templates/base.html`
- Create: `ckan/ckanext-idsk/ckanext/idsk/public/css/idsk-ckan.css`
- Create: `bin/verify_lkod_runtime`

- [ ] **Step 1: Add the failing runtime smoke check**

Create `bin/verify_lkod_runtime`:

```bash
#!/usr/bin/env bash
set -euo pipefail

docker compose ps --status running >/dev/null

docker compose exec -T ckan wget -q --spider http://localhost:5000/@id-sk/frontend-3.0.0-beta.0.min.css
docker compose exec -T ckan wget -q --spider http://localhost:5000/assets/images/logo-moje.png
docker compose exec -T ckan wget -q --spider http://localhost:5000/catalog.ttl

docker compose exec -T ckan sh -c "grep -q '^ckan.uploads_enabled = true$' /srv/app/ckan.ini"
docker compose exec -T ckan sh -c "grep -q '^ckan.locale_default = sk$' /srv/app/ckan.ini"
docker compose exec -T ckan sh -c "grep -q 'ckanext.dcat.rdf.profiles = euro_dcat_ap_2 euro_dcat_ap_scheming idsk_dcat_ap_sk' /srv/app/ckan.ini"

docker compose exec -T ckan wget -qO- http://localhost:5000/api/action/status_show | grep -q '"success": true'
```

- [ ] **Step 2: Run the smoke check and verify it fails on current runtime gaps**

Run: `bash bin/verify_lkod_runtime`

Expected: fails before the runtime fixes because at least `ckan.uploads_enabled`, `ckan.locale_default`, or the DCAT profile chain is not present in `/srv/app/ckan.ini`.

- [ ] **Step 3: Force LF for shell scripts**

Create or update `.gitattributes`:

```gitattributes
*.sh text eol=lf
bin/* text eol=lf
ckan/docker-entrypoint.d/*.sh text eol=lf
postgresql/docker-entrypoint-initdb.d/*.sh text eol=lf
```

Normalize `ckan/docker-entrypoint.d/01_setup_datapusher.sh` so the file content is exactly:

```bash
#!/bin/bash

if [[ $CKAN__PLUGINS == *"datapusher"* ]]; then
   if [ -z "$CKAN__DATAPUSHER__API_TOKEN" ] ; then
      echo "Set up ckan.datapusher.api_token in the CKAN config file"
      ckan config-tool "$CKAN_INI" "ckan.datapusher.api_token=$(ckan -c "$CKAN_INI" user token add ckan_admin datapusher | tail -n 1 | tr -d '\t')"
   fi
else
   echo "Not configuring DataPusher"
fi
```

- [ ] **Step 4: Correct CKAN runtime configuration in `.env`**

Update these `.env` values:

```dotenv
CKAN_SITE_URL=https://localhost:8443
CKAN__SITE_URL=https://localhost:8443
CKAN__LOCALE_DEFAULT=sk
CKAN__UPLOADS_ENABLED=true
CKAN__STORAGE_PATH=/var/lib/ckan
CKAN__MAX_RESOURCE_SIZE=100
CKAN__MAX_IMAGE_SIZE=10

CKANEXT_DCAT_RDF_PROFILES=euro_dcat_ap_2 euro_dcat_ap_scheming idsk_dcat_ap_sk
CKAN___SCHEMING__DATASET_SCHEMAS=ckanext.idsk.schemas:dcat_ap_sk.yaml
CKAN___SCHEMING__PRESETS=ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml

CKANEXT__IDSK__DEFAULT_ORGANIZATION=minedu
CKANEXT__IDSK__DEFAULT_ORGANIZATION_TITLE=Ministerstvo školstva
CKANEXT__IDSK__DEFAULT_ORGANIZATION_DESCRIPTION=Predvolený poskytovateľ otvorených dát pre tento portál.

CKAN__SITE_TITLE=Open Data Portál
CKAN__SITE_DESCRIPTION=Náš nový portál pre otvorené dáta.
```

Replace the plugin line with:

```dotenv
CKAN__PLUGINS="image_view text_view datatables_view datastore datapusher envvars dcat dcat_json_interface structured_data scheming_datasets idsk_theme"
```

- [ ] **Step 5: Install ckanext-scheming in the CKAN image**

Update `ckan/Dockerfile` so the extension install block is:

```dockerfile
RUN pip3 install -e /srv/app/src/ckanext-idsk
RUN pip3 install ckanext-dcat ckanext-scheming
```

- [ ] **Step 6: Fix broken logo references and load bridge CSS**

In `ckan/ckanext-idsk/ckanext/idsk/templates/header.html`, replace:

```jinja2
<img src="{{ h.url_for_static('assets/images/logo-sk-color.svg') }}"
    alt="Logo Moje Slovensko s odkazom na titulnú stránku" />
```

with:

```jinja2
<img src="{{ h.url_for_static('assets/images/logo-moje.png') }}"
    alt="Open Data Portál" />
```

In `ckan/ckanext-idsk/ckanext/idsk/templates/footer.html`, replace:

```jinja2
<img src="{{ h.url_for_static('assets/images/logo-sk-black.svg') }}" alt="Slovensko.sk" />
```

with:

```jinja2
<img src="{{ h.url_for_static('assets/images/logo-moje.png') }}" alt="Open Data Portál" />
```

In `ckan/ckanext-idsk/ckanext/idsk/templates/base.html`, make the styles block:

```jinja2
{% block styles %}
{{ super() }}
<link rel="stylesheet" href="{{ h.url_for_static('@id-sk/frontend-3.0.0-beta.0.min.css') }}" />
<link rel="stylesheet" href="{{ h.url_for_static('css/idsk-ckan.css') }}" />
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
{% endblock %}
```

Create `ckan/ckanext-idsk/ckanext/idsk/public/css/idsk-ckan.css`:

```css
.main {
  background: #ffffff;
}

.container {
  max-width: 960px;
}

.toolbar,
.breadcrumb {
  font-family: "Source Sans Pro", arial, sans-serif;
}

.module {
  border: 0;
  box-shadow: none;
}

.module-heading,
.page-heading {
  font-family: "Source Sans Pro", arial, sans-serif;
  color: #000000;
}

.form-control {
  min-height: 40px;
  border: 2px solid #0b0c0c;
  border-radius: 0;
}

.btn-primary {
  background: #00703c;
  border-color: #00703c;
  border-radius: 0;
}
```

- [ ] **Step 7: Rebuild and rerun the smoke check**

Run:

```bash
docker compose up -d --build
bash bin/verify_lkod_runtime
```

Expected: `bash bin/verify_lkod_runtime` exits with code 0.

- [ ] **Step 8: Commit runtime stabilization**

Run:

```bash
git add .env .gitattributes ckan/Dockerfile ckan/docker-entrypoint.d/01_setup_datapusher.sh ckan/ckanext-idsk/ckanext/idsk/templates/header.html ckan/ckanext-idsk/ckanext/idsk/templates/footer.html ckan/ckanext-idsk/ckanext/idsk/templates/base.html ckan/ckanext-idsk/ckanext/idsk/public/css/idsk-ckan.css bin/verify_lkod_runtime
git commit -m "fix: stabilize CKAN IDSK runtime"
```

## Task 2: Default Organization Support

**Files:**
- Modify: `ckan/ckanext-idsk/setup.py`
- Modify: `ckan/ckanext-idsk/ckanext/idsk/plugin.py`
- Create: `ckan/ckanext-idsk/ckanext/idsk/organization.py`
- Create: `ckan/ckanext-idsk/ckanext/idsk/cli.py`
- Create: `ckan/ckanext-idsk/ckanext/idsk/tests/test_organization.py`

- [ ] **Step 1: Write unit tests for default organization helper**

Create `ckan/ckanext-idsk/ckanext/idsk/tests/test_organization.py`:

```python
from ckanext.idsk.organization import default_organization_payload


def test_default_organization_payload_uses_config_values():
    config = {
        "ckanext.idsk.default_organization": "minedu",
        "ckanext.idsk.default_organization_title": "Ministerstvo školstva",
        "ckanext.idsk.default_organization_description": "Open data provider",
    }

    payload = default_organization_payload(config)

    assert payload == {
        "name": "minedu",
        "title": "Ministerstvo školstva",
        "description": "Open data provider",
        "state": "active",
    }


def test_default_organization_payload_uses_stable_defaults():
    payload = default_organization_payload({})

    assert payload["name"] == "minedu"
    assert payload["title"] == "Ministerstvo školstva"
    assert payload["state"] == "active"
```

- [ ] **Step 2: Run tests and verify failure**

Run: `docker compose exec -T ckan pytest /srv/app/src/ckanext-idsk/ckanext/idsk/tests/test_organization.py -q`

Expected: fails because `ckanext.idsk.organization` does not exist.

- [ ] **Step 3: Implement organization helper**

Create `ckan/ckanext-idsk/ckanext/idsk/organization.py`:

```python
import ckan.plugins.toolkit as toolkit


DEFAULT_ORG_NAME = "minedu"
DEFAULT_ORG_TITLE = "Ministerstvo školstva"
DEFAULT_ORG_DESCRIPTION = "Predvolený poskytovateľ otvorených dát pre tento portál."


def default_organization_payload(config):
    return {
        "name": config.get("ckanext.idsk.default_organization", DEFAULT_ORG_NAME),
        "title": config.get("ckanext.idsk.default_organization_title", DEFAULT_ORG_TITLE),
        "description": config.get(
            "ckanext.idsk.default_organization_description",
            DEFAULT_ORG_DESCRIPTION,
        ),
        "state": "active",
    }


def ensure_default_organization(context=None, config=None):
    context = context or {"ignore_auth": True}
    config = config or toolkit.config
    payload = default_organization_payload(config)

    try:
        return toolkit.get_action("organization_show")(context, {"id": payload["name"]})
    except toolkit.ObjectNotFound:
        return toolkit.get_action("organization_create")(context, payload)
```

- [ ] **Step 4: Add CLI command**

Create `ckan/ckanext-idsk/ckanext/idsk/cli.py`:

```python
import click

from ckanext.idsk.organization import ensure_default_organization


@click.group(short_help="IDSK portal commands")
def idsk():
    pass


@idsk.command("ensure-default-organization")
def ensure_default_organization_command():
    organization = ensure_default_organization()
    click.echo(f"Default organization ready: {organization['name']}")


def get_commands():
    return [idsk]
```

- [ ] **Step 5: Register CLI command in plugin**

Update `ckan/ckanext-idsk/ckanext/idsk/plugin.py`:

```python
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.idsk import cli


class IDSKThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IClick)

    def update_config(self, config):
        toolkit.add_template_directory(config, "templates")
        toolkit.add_public_directory(config, "public")

    def get_helpers(self):
        return {}

    def get_commands(self):
        return cli.get_commands()
```

- [ ] **Step 6: Run unit tests**

Run: `docker compose exec -T ckan pytest /srv/app/src/ckanext-idsk/ckanext/idsk/tests/test_organization.py -q`

Expected: 2 passed.

- [ ] **Step 7: Verify CLI creates or finds organization**

Run:

```bash
docker compose exec -T ckan ckan -c /srv/app/ckan.ini idsk ensure-default-organization
docker compose exec -T ckan ckan -c /srv/app/ckan.ini organization list
```

Expected output includes:

```text
Default organization ready: minedu
minedu
```

- [ ] **Step 8: Commit default organization support**

Run:

```bash
git add ckan/ckanext-idsk/setup.py ckan/ckanext-idsk/ckanext/idsk/plugin.py ckan/ckanext-idsk/ckanext/idsk/organization.py ckan/ckanext-idsk/ckanext/idsk/cli.py ckan/ckanext-idsk/ckanext/idsk/tests/test_organization.py
git commit -m "feat: add default publishing organization"
```

## Task 3: Published Link Helpers

**Files:**
- Modify: `ckan/ckanext-idsk/ckanext/idsk/plugin.py`
- Create: `ckan/ckanext-idsk/ckanext/idsk/helpers.py`
- Create: `ckan/ckanext-idsk/ckanext/idsk/tests/test_helpers.py`

- [ ] **Step 1: Write helper tests**

Create `ckan/ckanext-idsk/ckanext/idsk/tests/test_helpers.py`:

```python
from ckanext.idsk.helpers import catalog_ttl_url, dataset_ttl_url


def test_catalog_ttl_url_uses_site_url_without_trailing_slash():
    assert catalog_ttl_url("https://example.gov.sk/") == "https://example.gov.sk/catalog.ttl"


def test_dataset_ttl_url_uses_dataset_name():
    dataset = {"name": "test-dataset"}

    assert dataset_ttl_url("https://example.gov.sk/", dataset) == "https://example.gov.sk/dataset/test-dataset.ttl"
```

- [ ] **Step 2: Run tests and verify failure**

Run: `docker compose exec -T ckan pytest /srv/app/src/ckanext-idsk/ckanext/idsk/tests/test_helpers.py -q`

Expected: fails because `ckanext.idsk.helpers` does not exist.

- [ ] **Step 3: Implement helpers**

Create `ckan/ckanext-idsk/ckanext/idsk/helpers.py`:

```python
import ckan.plugins.toolkit as toolkit


def _site_url(site_url=None):
    return (site_url or toolkit.config.get("ckan.site_url", "")).rstrip("/")


def catalog_ttl_url(site_url=None):
    return f"{_site_url(site_url)}/catalog.ttl"


def dataset_ttl_url(site_url_or_dataset=None, dataset=None):
    if dataset is None:
        dataset = site_url_or_dataset
        site_url = None
    else:
        site_url = site_url_or_dataset
    return f"{_site_url(site_url)}/dataset/{dataset['name']}.ttl"
```

- [ ] **Step 4: Register helpers**

Update `get_helpers()` in `ckan/ckanext-idsk/ckanext/idsk/plugin.py`:

```python
    def get_helpers(self):
        from ckanext.idsk import helpers

        return {
            "idsk_catalog_ttl_url": helpers.catalog_ttl_url,
            "idsk_dataset_ttl_url": helpers.dataset_ttl_url,
        }
```

- [ ] **Step 5: Run helper tests**

Run: `docker compose exec -T ckan pytest /srv/app/src/ckanext-idsk/ckanext/idsk/tests/test_helpers.py -q`

Expected: 2 passed.

- [ ] **Step 6: Commit published link helpers**

Run:

```bash
git add ckan/ckanext-idsk/ckanext/idsk/plugin.py ckan/ckanext-idsk/ckanext/idsk/helpers.py ckan/ckanext-idsk/ckanext/idsk/tests/test_helpers.py
git commit -m "feat: add DCAT link helpers"
```

## Task 4: DCAT-AP-SK Metadata Schema

**Files:**
- Modify: `ckan/ckanext-idsk/setup.py`
- Create: `ckan/ckanext-idsk/ckanext/idsk/schemas/dcat_ap_sk.yaml`

- [ ] **Step 1: Add package data support**

Update `ckan/ckanext-idsk/setup.py`:

```python
from setuptools import setup, find_packages

setup(
    name="ckanext-idsk",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "ckanext.idsk": [
            "schemas/*.yaml",
            "templates/**/*.html",
            "public/**/*",
        ],
    },
    entry_points="""
        [ckan.plugins]
        idsk_theme=ckanext.idsk.plugin:IDSKThemePlugin

        [ckan.rdf.profiles]
        idsk_dcat_ap_sk=ckanext.idsk.profiles:IDSKDCATAPSKProfile
    """,
)
```

- [ ] **Step 2: Add the metadata schema**

Create `ckan/ckanext-idsk/ckanext/idsk/schemas/dcat_ap_sk.yaml`:

```yaml
scheming_version: 2
dataset_type: dataset
about: DCAT-AP-SK aligned dataset schema for the IDSK LKOD portal
about_url: https://datova-kancelaria.github.io/dcat-ap-sk-2.0/

dataset_fields:
  - field_name: title
    label: Názov datasetu
    preset: title
    validators: not_empty unicode_safe

  - field_name: name
    label: URL identifikátor
    preset: dataset_slug
    validators: not_empty unicode_safe name_validator package_name_validator

  - field_name: notes
    label: Popis
    preset: markdown
    validators: not_empty unicode_safe

  - field_name: owner_org
    label: Organizácia
    preset: dataset_organization
    validators: owner_org_validator unicode_safe

  - field_name: theme
    label: Téma
    preset: select
    validators: not_empty unicode_safe
    choices:
      - value: http://publications.europa.eu/resource/authority/data-theme/EDUC
        label: Vzdelávanie, kultúra a šport
      - value: http://publications.europa.eu/resource/authority/data-theme/GOVE
        label: Vláda a verejný sektor
      - value: http://publications.europa.eu/resource/authority/data-theme/SOCI
        label: Populácia a spoločnosť

  - field_name: frequency
    label: Periodicita aktualizácie
    preset: select
    validators: not_empty unicode_safe
    choices:
      - value: http://publications.europa.eu/resource/authority/frequency/DAILY
        label: Denne
      - value: http://publications.europa.eu/resource/authority/frequency/WEEKLY
        label: Týždenne
      - value: http://publications.europa.eu/resource/authority/frequency/MONTHLY
        label: Mesačne
      - value: http://publications.europa.eu/resource/authority/frequency/ANNUAL
        label: Ročne
      - value: http://publications.europa.eu/resource/authority/frequency/IRREG
        label: Nepravidelne

  - field_name: license_id
    label: Licencia
    preset: select
    validators: not_empty unicode_safe
    choices_helper: license_options

  - field_name: tag_string
    label: Kľúčové slová
    preset: tag_string_autocomplete
    validators: not_empty unicode_safe

  - field_name: contact_name
    label: Kontaktná osoba alebo útvar
    preset: text
    validators: not_empty unicode_safe

  - field_name: contact_email
    label: Kontaktný e-mail
    preset: text
    validators: not_empty email_validator unicode_safe

  - field_name: temporal_start
    label: Začiatok časového pokrytia
    preset: date
    validators: ignore_missing isodate

  - field_name: temporal_end
    label: Koniec časového pokrytia
    preset: date
    validators: ignore_missing isodate

resource_fields:
  - field_name: url
    label: URL alebo nahraný súbor
    preset: resource_url_upload
    validators: not_empty unicode_safe

  - field_name: name
    label: Názov distribúcie
    preset: text
    validators: not_empty unicode_safe

  - field_name: description
    label: Popis distribúcie
    preset: markdown
    validators: ignore_missing unicode_safe

  - field_name: format
    label: Formát
    preset: resource_format_autocomplete
    validators: not_empty unicode_safe
```

- [ ] **Step 3: Rebuild and verify schema loads**

Run:

```bash
docker compose up -d --build
docker compose logs ckan --tail 120
```

Expected: CKAN starts without a scheming schema import error.

- [ ] **Step 4: Verify dataset form exposes schema fields**

Run:

```bash
docker compose exec -T ckan wget -qO- http://localhost:5000/dataset/new | grep -E "theme|frequency|contact_email"
```

Expected: command finds the schema field names in the HTML or returns 403 for anonymous users. If it returns 403, proceed and verify manually after login in Task 7.

- [ ] **Step 5: Commit metadata schema**

Run:

```bash
git add ckan/ckanext-idsk/setup.py ckan/ckanext-idsk/ckanext/idsk/schemas/dcat_ap_sk.yaml .env ckan/Dockerfile
git commit -m "feat: add DCAT-AP-SK metadata schema"
```

## Task 5: DCAT Profile Hook And RDF Verification

**Files:**
- Create: `ckan/ckanext-idsk/ckanext/idsk/profiles.py`
- Create: `ckan/ckanext-idsk/ckanext/idsk/tests/test_profiles.py`
- Modify: `ckan/ckanext-idsk/setup.py`

- [ ] **Step 1: Write RDF profile unit test**

Create `ckan/ckanext-idsk/ckanext/idsk/tests/test_profiles.py`:

```python
from rdflib import Graph, URIRef
from rdflib.namespace import DCTERMS

from ckanext.idsk.profiles import DCAT, IDSKDCATAPSKProfile


def test_profile_adds_theme_and_frequency_to_dataset_graph():
    graph = Graph()
    profile = IDSKDCATAPSKProfile(graph, compatibility_mode=False)
    dataset_ref = URIRef("https://example.gov.sk/dataset/skoly")
    dataset = {
        "theme": "http://publications.europa.eu/resource/authority/data-theme/EDUC",
        "frequency": "http://publications.europa.eu/resource/authority/frequency/MONTHLY",
    }

    profile.graph_from_dataset(dataset, dataset_ref)

    assert (
        dataset_ref,
        DCAT.theme,
        URIRef("http://publications.europa.eu/resource/authority/data-theme/EDUC"),
    ) in graph
    assert (
        dataset_ref,
        DCTERMS.accrualPeriodicity,
        URIRef("http://publications.europa.eu/resource/authority/frequency/MONTHLY"),
    ) in graph
```

- [ ] **Step 2: Run test and verify failure**

Run: `docker compose exec -T ckan pytest /srv/app/src/ckanext-idsk/ckanext/idsk/tests/test_profiles.py -q`

Expected: fails because `ckanext.idsk.profiles` does not exist.

- [ ] **Step 3: Implement profile hook**

Create `ckan/ckanext-idsk/ckanext/idsk/profiles.py`:

```python
from rdflib import Namespace, URIRef
from rdflib.namespace import DCTERMS

from ckanext.dcat.profiles import EuropeanDCATAP2Profile


DCAT = Namespace("http://www.w3.org/ns/dcat#")


class IDSKDCATAPSKProfile(EuropeanDCATAP2Profile):
    def graph_from_dataset(self, dataset_dict, dataset_ref):
        dataset_ref = super().graph_from_dataset(dataset_dict, dataset_ref)

        theme = self._get_dataset_value(dataset_dict, "theme")
        if theme:
            self.g.add((dataset_ref, DCAT.theme, URIRef(theme)))

        frequency = self._get_dataset_value(dataset_dict, "frequency")
        if frequency:
            self.g.add((dataset_ref, DCTERMS.accrualPeriodicity, URIRef(frequency)))

        return dataset_ref
```

- [ ] **Step 4: Confirm profile entry point exists**

Confirm `ckan/ckanext-idsk/setup.py` includes:

```python
[ckan.rdf.profiles]
idsk_dcat_ap_sk=ckanext.idsk.profiles:IDSKDCATAPSKProfile
```

- [ ] **Step 5: Run RDF profile tests**

Run: `docker compose exec -T ckan pytest /srv/app/src/ckanext-idsk/ckanext/idsk/tests/test_profiles.py -q`

Expected: 1 passed.

- [ ] **Step 6: Commit RDF profile hook**

Run:

```bash
git add ckan/ckanext-idsk/setup.py ckan/ckanext-idsk/ckanext/idsk/profiles.py ckan/ckanext-idsk/ckanext/idsk/tests/test_profiles.py
git commit -m "feat: add Slovak DCAT profile hook"
```

## Task 6: IDSK Login And Dashboard

**Files:**
- Create: `ckan/ckanext-idsk/ckanext/idsk/templates/user/login.html`
- Create: `ckan/ckanext-idsk/ckanext/idsk/templates/dashboard/index.html`

- [ ] **Step 1: Add IDSK login template**

Create `ckan/ckanext-idsk/ckanext/idsk/templates/user/login.html`:

```jinja2
{% ckan_extends %}

{% block primary_content %}
<section class="govuk-width-container">
  <div class="govuk-grid-row">
    <div class="govuk-grid-column-two-thirds">
      <h1 class="govuk-heading-xl">Prihlásenie</h1>
      <form action="" method="post" class="govuk-form-group">
        {{ h.csrf_input() }}
        <div class="govuk-form-group">
          <label class="govuk-label" for="field-login">Používateľské meno alebo e-mail</label>
          <input class="govuk-input" id="field-login" type="text" name="login" autocomplete="username">
        </div>
        <div class="govuk-form-group">
          <label class="govuk-label" for="field-password">Heslo</label>
          <input class="govuk-input" id="field-password" type="password" name="password" autocomplete="current-password">
        </div>
        <div class="govuk-checkboxes">
          <div class="govuk-checkboxes__item">
            <input class="govuk-checkboxes__input" id="field-remember" type="checkbox" name="remember" value="63072000" checked>
            <label class="govuk-label govuk-checkboxes__label" for="field-remember">Zapamätať prihlásenie</label>
          </div>
        </div>
        <button class="govuk-button" type="submit">Prihlásiť sa</button>
      </form>
      <p class="govuk-body"><a class="govuk-link" href="{{ h.url_for('user.request_reset') }}">Zabudnuté heslo</a></p>
    </div>
  </div>
</section>
{% endblock %}

{% block secondary_content %}{% endblock %}
```

- [ ] **Step 2: Add IDSK dashboard template**

Create `ckan/ckanext-idsk/ckanext/idsk/templates/dashboard/index.html`:

```jinja2
{% ckan_extends %}

{% block primary_content %}
<section class="govuk-width-container">
  <h1 class="govuk-heading-xl">Publikovanie otvorených dát</h1>
  <p class="govuk-body-l">Pridajte dataset, nahrajte súbor a získajte DCAT odkaz pre katalóg otvorených dát.</p>
  <a class="govuk-button" href="{{ h.url_for('dataset.new') }}">Pridať dataset</a>
  <a class="govuk-button govuk-button--secondary" href="{{ h.idsk_catalog_ttl_url() }}">Zobraziť catalog.ttl</a>
</section>
{% endblock %}

{% block secondary_content %}{% endblock %}
```

- [ ] **Step 3: Rebuild and verify pages render**

Run:

```bash
docker compose restart ckan
docker compose exec -T ckan wget -qO- http://localhost:5000/user/login | grep "Prihlásenie"
```

Expected: output contains `Prihlásenie`.

- [ ] **Step 4: Commit IDSK login and dashboard**

Run:

```bash
git add ckan/ckanext-idsk/ckanext/idsk/templates/user/login.html ckan/ckanext-idsk/ckanext/idsk/templates/dashboard/index.html
git commit -m "feat: add IDSK login and publisher dashboard"
```

## Task 7: IDSK Dataset And Resource Publishing Screens

**Files:**
- Create: `ckan/ckanext-idsk/ckanext/idsk/templates/package/snippets/package_form.html`
- Create: `ckan/ckanext-idsk/ckanext/idsk/templates/package/snippets/resource_form.html`
- Create: `ckan/ckanext-idsk/ckanext/idsk/templates/package/read.html`

- [ ] **Step 1: Add dataset form template**

Create `ckan/ckanext-idsk/ckanext/idsk/templates/package/snippets/package_form.html`:

```jinja2
{% import 'macros/form.html' as form %}

<div class="govuk-grid-row">
  <div class="govuk-grid-column-two-thirds">
    {{ form.input('title', label=_('Názov datasetu'), id='field-title', value=data.title, error=errors.title, classes=['control-full'], attrs={'class': 'govuk-input'}) }}
    {{ form.input('name', label=_('URL identifikátor'), id='field-name', value=data.name, error=errors.name, classes=['control-full'], attrs={'class': 'govuk-input'}) }}
    {{ form.markdown('notes', label=_('Popis'), id='field-notes', value=data.notes, error=errors.notes, attrs={'class': 'govuk-textarea'}) }}
    {{ form.input('tag_string', label=_('Kľúčové slová'), id='field-tags', value=data.tag_string, error=errors.tag_string, classes=['control-full'], attrs={'class': 'govuk-input'}) }}
    {{ form.input('contact_name', label=_('Kontaktná osoba alebo útvar'), id='field-contact-name', value=data.contact_name, error=errors.contact_name, classes=['control-full'], attrs={'class': 'govuk-input'}) }}
    {{ form.input('contact_email', label=_('Kontaktný e-mail'), id='field-contact-email', value=data.contact_email, error=errors.contact_email, classes=['control-full'], attrs={'class': 'govuk-input'}) }}
    {{ form.select('theme', label=_('Téma'), id='field-theme', options=[
      {'value': 'http://publications.europa.eu/resource/authority/data-theme/EDUC', 'text': _('Vzdelávanie, kultúra a šport')},
      {'value': 'http://publications.europa.eu/resource/authority/data-theme/GOVE', 'text': _('Vláda a verejný sektor')},
      {'value': 'http://publications.europa.eu/resource/authority/data-theme/SOCI', 'text': _('Populácia a spoločnosť')}
    ], selected=data.theme, error=errors.theme, attrs={'class': 'govuk-select'}) }}
    {{ form.select('frequency', label=_('Periodicita aktualizácie'), id='field-frequency', options=[
      {'value': 'http://publications.europa.eu/resource/authority/frequency/DAILY', 'text': _('Denne')},
      {'value': 'http://publications.europa.eu/resource/authority/frequency/WEEKLY', 'text': _('Týždenne')},
      {'value': 'http://publications.europa.eu/resource/authority/frequency/MONTHLY', 'text': _('Mesačne')},
      {'value': 'http://publications.europa.eu/resource/authority/frequency/ANNUAL', 'text': _('Ročne')},
      {'value': 'http://publications.europa.eu/resource/authority/frequency/IRREG', 'text': _('Nepravidelne')}
    ], selected=data.frequency, error=errors.frequency, attrs={'class': 'govuk-select'}) }}
    {{ form.required_message() }}
  </div>
</div>
```

- [ ] **Step 2: Add resource form template**

Create `ckan/ckanext-idsk/ckanext/idsk/templates/package/snippets/resource_form.html`:

```jinja2
{% import 'macros/form.html' as form %}

<div class="govuk-grid-row">
  <div class="govuk-grid-column-two-thirds">
    {{ form.input('name', label=_('Názov distribúcie'), id='field-name', value=data.name, error=errors.name, classes=['control-full'], attrs={'class': 'govuk-input'}) }}
    {{ form.markdown('description', label=_('Popis distribúcie'), id='field-description', value=data.description, error=errors.description, attrs={'class': 'govuk-textarea'}) }}
    {{ form.input('url', label=_('URL zdroja alebo nahraný súbor'), id='field-url', value=data.url, error=errors.url, classes=['control-full'], attrs={'class': 'govuk-input'}) }}
    {{ form.input('format', label=_('Formát'), id='field-format', value=data.format, error=errors.format, classes=['control-medium'], attrs={'class': 'govuk-input'}) }}
    {{ form.required_message() }}
  </div>
</div>
```

- [ ] **Step 3: Add dataset detail DCAT links**

Create `ckan/ckanext-idsk/ckanext/idsk/templates/package/read.html`:

```jinja2
{% ckan_extends %}

{% block primary_content_inner %}
  {{ super() }}
  <section class="govuk-inset-text">
    <h2 class="govuk-heading-m">Odkazy pre otvorené dáta</h2>
    <p class="govuk-body">
      <a class="govuk-link" href="{{ h.idsk_dataset_ttl_url(pkg) }}">DCAT záznam datasetu</a>
    </p>
    <p class="govuk-body">
      <a class="govuk-link" href="{{ h.idsk_catalog_ttl_url() }}">LKOD katalóg catalog.ttl</a>
    </p>
  </section>
{% endblock %}
```

- [ ] **Step 4: Restart CKAN and verify templates load**

Run:

```bash
docker compose restart ckan
docker compose exec -T ckan wget -qO- http://localhost:5000/user/login | grep "Prihlásenie"
```

Expected: CKAN renders without template syntax errors.

- [ ] **Step 5: Commit publishing templates**

Run:

```bash
git add ckan/ckanext-idsk/ckanext/idsk/templates/package/snippets/package_form.html ckan/ckanext-idsk/ckanext/idsk/templates/package/snippets/resource_form.html ckan/ckanext-idsk/ckanext/idsk/templates/package/read.html
git commit -m "feat: add IDSK dataset publishing screens"
```

## Task 8: End-To-End Publishing Verification

**Files:**
- Modify: `bin/verify_lkod_runtime`

- [ ] **Step 1: Extend smoke check with default organization and DCAT content checks**

Append to `bin/verify_lkod_runtime`:

```bash
docker compose exec -T ckan ckan -c /srv/app/ckan.ini idsk ensure-default-organization | grep -q "Default organization ready: minedu"
docker compose exec -T ckan wget -qO- http://localhost:5000/catalog.ttl | grep -q "dcat:Catalog"
```

- [ ] **Step 2: Create test dataset through CKAN API**

Run:

```bash
docker compose exec -T ckan ckan -c /srv/app/ckan.ini user token add ckan_admin e2e-smoke
```

Copy the token value printed by the command, then run from the host with the token in `CKAN_API_TOKEN`:

```bash
curl -k -H "Authorization: $CKAN_API_TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"smoke-dataset","title":"Smoke dataset","notes":"Dataset for LKOD smoke verification.","owner_org":"minedu","theme":"http://publications.europa.eu/resource/authority/data-theme/EDUC","frequency":"http://publications.europa.eu/resource/authority/frequency/MONTHLY","tag_string":"smoke,verification","license_id":"cc-by","contact_name":"Open Data tím","contact_email":"opendata@example.gov.sk"}' \
  https://localhost:8443/api/action/package_create
```

Expected JSON contains:

```json
"success": true
```

- [ ] **Step 3: Verify dataset RDF and catalog RDF**

Run:

```bash
docker compose exec -T ckan wget -qO- http://localhost:5000/dataset/smoke-dataset.ttl | grep -q "dcat:Dataset"
docker compose exec -T ckan wget -qO- http://localhost:5000/catalog.ttl | grep -q "smoke-dataset"
```

Expected: both commands exit with code 0.

- [ ] **Step 4: Verify CSV resource upload manually through UI**

Use the running portal at `https://localhost:8443`:

1. Log in as `ckan_admin`.
2. Open `/dataset/smoke-dataset/resource/new`.
3. Upload a small CSV file with columns `id,name`.
4. Save the resource.
5. Open the resource download URL.

Expected:

- Resource saves successfully.
- Download URL returns the uploaded CSV.
- DataPusher logs either show successful processing or a clear DataPusher-specific error.

- [ ] **Step 5: Run smoke check**

Run: `bash bin/verify_lkod_runtime`

Expected: exits with code 0.

- [ ] **Step 6: Commit verification updates**

Run:

```bash
git add bin/verify_lkod_runtime
git commit -m "test: add LKOD runtime verification"
```

## Task 9: Final Review And Documentation

**Files:**
- Modify: `README.md`
- Create: `docs/lkod-publishing.md`

- [ ] **Step 1: Add operator documentation**

Create `docs/lkod-publishing.md`:

```markdown
# LKOD Publishing Guide

## Local URL

Development portal:

`https://localhost:8443`

## Publishing Flow

1. Log in as a publisher.
2. Open the publisher dashboard.
3. Click `Pridať dataset`.
4. Fill in required metadata.
5. Add a resource by upload or URL.
6. Open the dataset page.
7. Use `catalog.ttl` as the LKOD catalog link.

## LKOD Links

Catalog:

`https://localhost:8443/catalog.ttl`

Dataset RDF:

`https://localhost:8443/dataset/<dataset-name>.ttl`

## Production Notes

Before registering the catalog on data.slovensko.sk:

1. Set `CKAN_SITE_URL` and `CKAN__SITE_URL` to the production HTTPS domain.
2. Use a trusted TLS certificate.
3. Verify `/catalog.ttl` is publicly accessible.
4. Verify at least one dataset includes a distribution.
5. Check the RDF against DCAT-AP-SK expectations.
```

- [ ] **Step 2: Link guide from README**

Add this section near the development instructions in `README.md`:

```markdown
## LKOD publishing

This project includes an IDSK-styled CKAN publishing flow for one institutional open data portal. See `docs/lkod-publishing.md` for the local publishing workflow, DCAT links, and production checks before registering the catalog on data.slovensko.sk.
```

- [ ] **Step 3: Run final verification**

Run:

```bash
bash bin/verify_lkod_runtime
docker compose ps
```

Expected:

- Smoke script exits with code 0.
- CKAN, db, solr, redis, datapusher, and nginx are running.

- [ ] **Step 4: Commit documentation**

Run:

```bash
git add README.md docs/lkod-publishing.md
git commit -m "docs: add LKOD publishing guide"
```

## Self-Review Notes

Spec coverage:

- One-institution portal: covered by Task 2 default organization and Task 9 docs.
- IDSK workflow: covered by Tasks 6 and 7.
- Upload and DataPusher verification: covered by Tasks 1 and 8.
- DCAT/LKOD links: covered by Tasks 3, 5, 8, and 9.
- DCAT-AP-SK metadata: covered by Tasks 4 and 5.
- Runtime issues found during audit: covered by Task 1.

Known implementation risk:

- CKAN template override names may need adjustment if CKAN 2.11 resolves a different snippet path for scheming forms. If a template does not render, inspect the rendered page and CKAN debug logs, then move the exact template content from Task 7 into the snippet path used by CKAN 2.11.
