# DataHub DCAT-AP-SK Env Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `ckan-docker-prod` emit a slovensko.sk-ready DCAT-AP-SK catalogue whose ministry and legal metadata come from `.env`.

**Architecture:** Keep `ckanext-dcat` as the dynamic RDF generator. Add a final `datahub_dcat_ap_sk` RDF profile in `ckanext-datahub` that normalizes the generated graph using Docker-provided environment variables. Extend the production smoke test so the final `catalog.ttl` must contain Slovak publisher, keywords, download URL, controlled-vocabulary format/media type, and `leg:termsOfUse`.

**Tech Stack:** CKAN 2.11, ckanext-dcat, ckanext-scheming, rdflib, Docker Compose, Bash.

---

## File Structure

- Modify `ckan-docker-prod/.env.example`: add public DCAT-AP-SK env variables and default profile order.
- Modify ignored `ckan-docker-prod/.env`: add the same non-secret DCAT-AP-SK values for the local running stack.
- Modify `ckan-docker-prod/docker-compose.yml`: pass the new `DATAHUB_DCAT_*` variables into the CKAN container.
- Modify `ckan-docker-prod/ckan/docker-entrypoint.d/02_setup_prod_config.sh`: default `ckanext.dcat.rdf.profiles` to include `datahub_dcat_ap_sk`.
- Create `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/dcat_ap_sk.py`: final RDF graph normalizer.
- Modify `ckan-docker-prod/ckan/ckanext-datahub/setup.py`: register `datahub_dcat_ap_sk` under `ckan.rdf.profiles`.
- Modify `ckan-docker-prod/bin/verify-prod`: parse `catalog.ttl` with rdflib and enforce DCAT-AP-SK output requirements.
- Optionally modify `ckan-docker-prod/README.md`: document the env-driven DCAT configuration and final public URL requirement.

---

### Task 1: Tighten Production RDF Smoke Test

**Files:**
- Modify: `ckan-docker-prod/bin/verify-prod`

- [ ] **Step 1: Add a failing RDF validation block**

Append this block after the existing `catalog.ttl | grep -q "dcat:Catalog"` check:

```bash
docker compose exec -T ckan python - <<'PY'
import os
import sys
import urllib.request

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import DCAT, DCT, FOAF

LEG = Namespace("https://data.gov.sk/def/ontology/legislation/")

publisher_uri = URIRef(os.environ["DATAHUB_DCAT_PUBLISHER_URI"])
format_uri = URIRef(os.environ["DATAHUB_DCAT_DEFAULT_FORMAT_URI"])
media_type_uri = URIRef(os.environ["DATAHUB_DCAT_DEFAULT_MEDIA_TYPE_URI"])

terms_predicates = [
    LEG.authorsWorkType,
    LEG.originalDatabaseType,
    LEG.databaseProtectedBySpecialRightsType,
    LEG.personalDataContainmentType,
]

graph = Graph()
graph.parse(
    data=urllib.request.urlopen("http://localhost:5000/catalog.ttl").read(),
    format="turtle",
)

failures = []

catalogs = list(graph.subjects(RDF.type, DCAT.Catalog))
if not catalogs:
    failures.append("catalog.ttl has no dcat:Catalog")

for catalog in catalogs:
    if publisher_uri not in graph.objects(catalog, DCT.publisher):
        failures.append(f"{catalog} missing dct:publisher {publisher_uri}")
    if (publisher_uri, RDF.type, FOAF.Agent) not in graph:
        failures.append(f"{publisher_uri} missing foaf:Agent type")
    if not list(graph.objects(publisher_uri, FOAF.name)):
        failures.append(f"{publisher_uri} missing foaf:name")

datasets = list(graph.subjects(RDF.type, DCAT.Dataset))
if not datasets:
    failures.append("catalog.ttl has no dcat:Dataset")

for dataset in datasets:
    required_dataset_predicates = [
        (DCT.publisher, "dct:publisher"),
        (DCAT.theme, "dcat:theme"),
        (DCT.accrualPeriodicity, "dct:accrualPeriodicity"),
        (DCAT.keyword, "dcat:keyword"),
        (DCAT.distribution, "dcat:distribution"),
    ]
    for predicate, label in required_dataset_predicates:
        if not list(graph.objects(dataset, predicate)):
            failures.append(f"{dataset} missing {label}")
    if publisher_uri not in graph.objects(dataset, DCT.publisher):
        failures.append(f"{dataset} publisher is not {publisher_uri}")

distributions = list(graph.subjects(RDF.type, DCAT.Distribution))
if not distributions:
    failures.append("catalog.ttl has no dcat:Distribution")

for distribution in distributions:
    required_distribution_predicates = [
        (DCAT.accessURL, "dcat:accessURL"),
        (DCAT.downloadURL, "dcat:downloadURL"),
        (DCT["format"], "dct:format"),
        (DCAT.mediaType, "dcat:mediaType"),
        (LEG.termsOfUse, "leg:termsOfUse"),
    ]
    for predicate, label in required_distribution_predicates:
        if not list(graph.objects(distribution, predicate)):
            failures.append(f"{distribution} missing {label}")

    if format_uri not in graph.objects(distribution, DCT["format"]):
        failures.append(f"{distribution} missing controlled dct:format {format_uri}")
    if media_type_uri not in graph.objects(distribution, DCAT.mediaType):
        failures.append(
            f"{distribution} missing controlled dcat:mediaType {media_type_uri}"
        )
    if Literal("CSV") in graph.objects(distribution, DCT["format"]):
        failures.append(f"{distribution} still has literal dct:format CSV")
    if Literal("text/csv") in graph.objects(distribution, DCAT.mediaType):
        failures.append(f"{distribution} still has literal dcat:mediaType text/csv")

    for terms in graph.objects(distribution, LEG.termsOfUse):
        if (terms, RDF.type, LEG.TermsOfUse) not in graph:
            failures.append(f"{terms} missing leg:TermsOfUse type")
        for predicate in terms_predicates:
            if not list(graph.objects(terms, predicate)):
                failures.append(f"{terms} missing {predicate}")

if failures:
    print("DCAT-AP-SK RDF validation failed:", file=sys.stderr)
    for failure in failures:
        print(f"- {failure}", file=sys.stderr)
    sys.exit(1)

print("DCAT-AP-SK RDF validation passed.")
PY
```

- [ ] **Step 2: Run the smoke test and verify it fails**

Run:

```bash
cd ckan-docker-prod
bash bin/verify-prod
```

Expected: FAIL with errors mentioning missing `dct:publisher`, `dcat:downloadURL`, controlled `dct:format`, controlled `dcat:mediaType`, or `leg:termsOfUse`.

- [ ] **Step 3: Commit the failing validation**

Run:

```bash
git add ckan-docker-prod/bin/verify-prod
git commit -m "test: require DCAT AP SK RDF metadata"
```

---

### Task 2: Add Env Configuration Surface

**Files:**
- Modify: `ckan-docker-prod/.env.example`
- Modify: `ckan-docker-prod/.env`
- Modify: `ckan-docker-prod/docker-compose.yml`
- Modify: `ckan-docker-prod/ckan/docker-entrypoint.d/02_setup_prod_config.sh`

- [ ] **Step 1: Update `.env.example`**

Replace:

```env
CKANEXT__DCAT__RDF__PROFILES=euro_dcat_ap_2 euro_dcat_ap_scheming
```

with:

```env
CKANEXT__DCAT__RDF__PROFILES=euro_dcat_ap_2 euro_dcat_ap_scheming datahub_dcat_ap_sk
```

Add this block below the DCAT profile configuration:

```env
# DCAT-AP-SK publisher and legal metadata for slovensko.sk harvesting
DATAHUB_DCAT_PUBLISHER_URI=https://data.gov.sk/id/legal-subject/00164381
DATAHUB_DCAT_PUBLISHER_NAME=Ministerstvo školstva, výskumu, vývoja a mládeže Slovenskej republiky
DATAHUB_DCAT_CONTACT_NAME=DataHub Open Data
DATAHUB_DCAT_CONTACT_EMAIL=opendata@example.gov.sk
DATAHUB_DCAT_DEFAULT_FORMAT_URI=http://publications.europa.eu/resource/authority/file-type/CSV
DATAHUB_DCAT_DEFAULT_MEDIA_TYPE_URI=http://www.iana.org/assignments/media-types/text/csv
DATAHUB_DCAT_TERMS_AUTHORS_WORK_TYPE=https://data.gov.sk/def/authors-work-type/3
DATAHUB_DCAT_TERMS_ORIGINAL_DATABASE_TYPE=https://data.gov.sk/def/original-database-type/3
DATAHUB_DCAT_TERMS_DATABASE_PROTECTED_BY_SPECIAL_RIGHTS_TYPE=https://data.gov.sk/def/codelist/database-creator-special-rights-type/2
DATAHUB_DCAT_TERMS_PERSONAL_DATA_CONTAINMENT_TYPE=https://data.gov.sk/def/personal-data-occurence-type/2
```

- [ ] **Step 2: Update ignored `.env` with the same non-secret values**

Add the same DCAT profile value and `DATAHUB_DCAT_*` block to `ckan-docker-prod/.env`. Do not print or commit secrets from this file.

- [ ] **Step 3: Pass env variables into the CKAN container**

Add these lines to `services.ckan.environment` in `ckan-docker-prod/docker-compose.yml` after `CKANEXT__DCAT__RDF__PROFILES`:

```yaml
      DATAHUB_DCAT_PUBLISHER_URI: ${DATAHUB_DCAT_PUBLISHER_URI}
      DATAHUB_DCAT_PUBLISHER_NAME: ${DATAHUB_DCAT_PUBLISHER_NAME}
      DATAHUB_DCAT_CONTACT_NAME: ${DATAHUB_DCAT_CONTACT_NAME}
      DATAHUB_DCAT_CONTACT_EMAIL: ${DATAHUB_DCAT_CONTACT_EMAIL}
      DATAHUB_DCAT_DEFAULT_FORMAT_URI: ${DATAHUB_DCAT_DEFAULT_FORMAT_URI}
      DATAHUB_DCAT_DEFAULT_MEDIA_TYPE_URI: ${DATAHUB_DCAT_DEFAULT_MEDIA_TYPE_URI}
      DATAHUB_DCAT_TERMS_AUTHORS_WORK_TYPE: ${DATAHUB_DCAT_TERMS_AUTHORS_WORK_TYPE}
      DATAHUB_DCAT_TERMS_ORIGINAL_DATABASE_TYPE: ${DATAHUB_DCAT_TERMS_ORIGINAL_DATABASE_TYPE}
      DATAHUB_DCAT_TERMS_DATABASE_PROTECTED_BY_SPECIAL_RIGHTS_TYPE: ${DATAHUB_DCAT_TERMS_DATABASE_PROTECTED_BY_SPECIAL_RIGHTS_TYPE}
      DATAHUB_DCAT_TERMS_PERSONAL_DATA_CONTAINMENT_TYPE: ${DATAHUB_DCAT_TERMS_PERSONAL_DATA_CONTAINMENT_TYPE}
```

- [ ] **Step 4: Update the entrypoint default profile order**

Replace in `ckan-docker-prod/ckan/docker-entrypoint.d/02_setup_prod_config.sh`:

```bash
ckan config-tool "$CKAN_INI" "ckanext.dcat.rdf.profiles=${CKANEXT__DCAT__RDF__PROFILES:-euro_dcat_ap_2 euro_dcat_ap_scheming}"
```

with:

```bash
ckan config-tool "$CKAN_INI" "ckanext.dcat.rdf.profiles=${CKANEXT__DCAT__RDF__PROFILES:-euro_dcat_ap_2 euro_dcat_ap_scheming datahub_dcat_ap_sk}"
```

- [ ] **Step 5: Verify compose config resolves**

Run:

```bash
cd ckan-docker-prod
docker compose config --services
```

Expected: command exits 0 and lists `ckan`, `datapusher`, `db`, `solr`, and `redis`.

- [ ] **Step 6: Commit env surface changes**

Run:

```bash
git add ckan-docker-prod/.env.example ckan-docker-prod/docker-compose.yml ckan-docker-prod/ckan/docker-entrypoint.d/02_setup_prod_config.sh
git commit -m "feat: configure DataHub DCAT AP SK env values"
```

Do not add `ckan-docker-prod/.env`.

---

### Task 3: Implement DataHub DCAT-AP-SK RDF Profile

**Files:**
- Create: `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/dcat_ap_sk.py`
- Modify: `ckan-docker-prod/ckan/ckanext-datahub/setup.py`

- [ ] **Step 1: Create `dcat_ap_sk.py`**

Create `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/dcat_ap_sk.py` with:

```python
import os
from urllib.parse import urlparse

from rdflib import BNode, Literal, Namespace, RDF, URIRef

from ckanext.dcat.profiles import DCAT, DCT, FOAF, VCARD, RDFProfile


LEG = Namespace("https://data.gov.sk/def/ontology/legislation/")

DEFAULTS = {
    "DATAHUB_DCAT_PUBLISHER_URI": "https://data.gov.sk/id/legal-subject/00164381",
    "DATAHUB_DCAT_PUBLISHER_NAME": (
        "Ministerstvo školstva, výskumu, vývoja a mládeže Slovenskej republiky"
    ),
    "DATAHUB_DCAT_CONTACT_NAME": "DataHub Open Data",
    "DATAHUB_DCAT_CONTACT_EMAIL": "opendata@example.gov.sk",
    "DATAHUB_DCAT_DEFAULT_FORMAT_URI": (
        "http://publications.europa.eu/resource/authority/file-type/CSV"
    ),
    "DATAHUB_DCAT_DEFAULT_MEDIA_TYPE_URI": (
        "http://www.iana.org/assignments/media-types/text/csv"
    ),
    "DATAHUB_DCAT_TERMS_AUTHORS_WORK_TYPE": (
        "https://data.gov.sk/def/authors-work-type/3"
    ),
    "DATAHUB_DCAT_TERMS_ORIGINAL_DATABASE_TYPE": (
        "https://data.gov.sk/def/original-database-type/3"
    ),
    "DATAHUB_DCAT_TERMS_DATABASE_PROTECTED_BY_SPECIAL_RIGHTS_TYPE": (
        "https://data.gov.sk/def/codelist/database-creator-special-rights-type/2"
    ),
    "DATAHUB_DCAT_TERMS_PERSONAL_DATA_CONTAINMENT_TYPE": (
        "https://data.gov.sk/def/personal-data-occurence-type/2"
    ),
}


class DataHubDCATAPSKProfile(RDFProfile):
    def parse_dataset(self, dataset_dict, dataset_ref):
        return dataset_dict

    def graph_from_catalog(self, catalog_dict, catalog_ref):
        self._set_publisher(catalog_ref)

    def graph_from_dataset(self, dataset_dict, dataset_ref):
        self._set_publisher(dataset_ref)
        self._ensure_keywords(dataset_dict, dataset_ref)
        self._ensure_contact_point(dataset_ref)

        for distribution_ref in self.g.objects(dataset_ref, DCAT.distribution):
            self._normalize_distribution(distribution_ref)

    def _env(self, key):
        return os.environ.get(key, DEFAULTS[key]).strip()

    def _env_uri(self, key):
        return URIRef(self._env(key))

    def _publisher_uri(self):
        return self._env_uri("DATAHUB_DCAT_PUBLISHER_URI")

    def _set_publisher(self, subject):
        publisher = self._publisher_uri()

        self.g.remove((subject, DCT.publisher, None))
        self.g.add((subject, DCT.publisher, publisher))
        self.g.add((publisher, RDF.type, FOAF.Agent))
        self.g.add(
            (
                publisher,
                FOAF.name,
                Literal(self._env("DATAHUB_DCAT_PUBLISHER_NAME")),
            )
        )

    def _ensure_keywords(self, dataset_dict, dataset_ref):
        if list(self.g.objects(dataset_ref, DCAT.keyword)):
            return

        tags = dataset_dict.get("tags") or []
        for tag in tags:
            keyword = tag.get("display_name") or tag.get("name")
            if keyword:
                self.g.add((dataset_ref, DCAT.keyword, Literal(keyword)))

    def _ensure_contact_point(self, dataset_ref):
        if list(self.g.objects(dataset_ref, DCAT.contactPoint)):
            return

        contact_name = self._env("DATAHUB_DCAT_CONTACT_NAME")
        contact_email = self._env("DATAHUB_DCAT_CONTACT_EMAIL")
        if not contact_name and not contact_email:
            return

        contact = BNode()
        self.g.add((contact, RDF.type, VCARD.Organization))
        if contact_name:
            self.g.add((contact, VCARD.fn, Literal(contact_name)))
        if contact_email:
            self.g.add((contact, VCARD.hasEmail, URIRef(f"mailto:{contact_email}")))
        self.g.add((dataset_ref, DCAT.contactPoint, contact))

    def _normalize_distribution(self, distribution_ref):
        access_urls = list(self.g.objects(distribution_ref, DCAT.accessURL))
        if access_urls and not list(self.g.objects(distribution_ref, DCAT.downloadURL)):
            self.g.add((distribution_ref, DCAT.downloadURL, access_urls[0]))

        if self._is_csv_distribution(distribution_ref):
            self.g.remove((distribution_ref, DCT["format"], None))
            self.g.remove((distribution_ref, DCAT.mediaType, None))
            self.g.add(
                (
                    distribution_ref,
                    DCT["format"],
                    self._env_uri("DATAHUB_DCAT_DEFAULT_FORMAT_URI"),
                )
            )
            self.g.add(
                (
                    distribution_ref,
                    DCAT.mediaType,
                    self._env_uri("DATAHUB_DCAT_DEFAULT_MEDIA_TYPE_URI"),
                )
            )

        self._ensure_terms_of_use(distribution_ref)

    def _is_csv_distribution(self, distribution_ref):
        values = []
        for predicate in (DCT["format"], DCAT.mediaType, DCAT.accessURL, DCAT.downloadURL):
            values.extend(str(value).lower() for value in self.g.objects(distribution_ref, predicate))

        for value in values:
            parsed_path = urlparse(value).path.lower()
            if value in {"csv", "text/csv"}:
                return True
            if parsed_path.endswith(".csv"):
                return True
            if "file-type/csv" in value or "media-types/text/csv" in value:
                return True
        return False

    def _ensure_terms_of_use(self, distribution_ref):
        if list(self.g.objects(distribution_ref, LEG.termsOfUse)):
            return

        terms = BNode()
        self.g.add((terms, RDF.type, LEG.TermsOfUse))
        self.g.add(
            (
                terms,
                LEG.authorsWorkType,
                self._env_uri("DATAHUB_DCAT_TERMS_AUTHORS_WORK_TYPE"),
            )
        )
        self.g.add(
            (
                terms,
                LEG.originalDatabaseType,
                self._env_uri("DATAHUB_DCAT_TERMS_ORIGINAL_DATABASE_TYPE"),
            )
        )
        self.g.add(
            (
                terms,
                LEG.databaseProtectedBySpecialRightsType,
                self._env_uri(
                    "DATAHUB_DCAT_TERMS_DATABASE_PROTECTED_BY_SPECIAL_RIGHTS_TYPE"
                ),
            )
        )
        self.g.add(
            (
                terms,
                LEG.personalDataContainmentType,
                self._env_uri("DATAHUB_DCAT_TERMS_PERSONAL_DATA_CONTAINMENT_TYPE"),
            )
        )
        self.g.add((distribution_ref, LEG.termsOfUse, terms))
```

- [ ] **Step 2: Register the RDF profile entry point**

Replace the `entry_points` block in `ckan-docker-prod/ckan/ckanext-datahub/setup.py` with:

```python
    entry_points="""
        [ckan.plugins]
        datahub_branding=ckanext.datahub.plugin:DataHubBrandingPlugin

        [ckan.rdf.profiles]
        datahub_dcat_ap_sk=ckanext.datahub.dcat_ap_sk:DataHubDCATAPSKProfile
    """,
```

- [ ] **Step 3: Rebuild CKAN**

Run:

```bash
cd ckan-docker-prod
docker compose up -d --build ckan
```

Expected: CKAN image rebuilds and `ckan` becomes healthy.

- [ ] **Step 4: Verify the profile is configured**

Run:

```bash
cd ckan-docker-prod
docker compose exec -T ckan sh -c "grep -E '^ckanext.dcat.rdf.profiles ?= ?' /srv/app/ckan.ini"
```

Expected output contains:

```text
euro_dcat_ap_2 euro_dcat_ap_scheming datahub_dcat_ap_sk
```

- [ ] **Step 5: Run the smoke test**

Run:

```bash
cd ckan-docker-prod
bash bin/verify-prod
```

Expected: PASS and output includes:

```text
DCAT-AP-SK RDF validation passed.
Production smoke check passed.
```

- [ ] **Step 6: Commit profile implementation**

Run:

```bash
git add ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/dcat_ap_sk.py ckan-docker-prod/ckan/ckanext-datahub/setup.py
git commit -m "feat: add DataHub DCAT AP SK RDF profile"
```

---

### Task 4: Update Documentation and Final Verification

**Files:**
- Modify: `ckan-docker-prod/README.md`

- [ ] **Step 1: Document the DCAT-AP-SK env block**

Add this section after `## LKOD Publication Checklist`:

````markdown
## DCAT-AP-SK Metadata

The final RDF profile `datahub_dcat_ap_sk` reads Slovak publisher and legal metadata from `.env`.

The Ministry of Education defaults are:

```text
DATAHUB_DCAT_PUBLISHER_URI=https://data.gov.sk/id/legal-subject/00164381
DATAHUB_DCAT_PUBLISHER_NAME=Ministerstvo školstva, výskumu, vývoja a mládeže Slovenskej republiky
DATAHUB_DCAT_DEFAULT_FORMAT_URI=http://publications.europa.eu/resource/authority/file-type/CSV
DATAHUB_DCAT_DEFAULT_MEDIA_TYPE_URI=http://www.iana.org/assignments/media-types/text/csv
```

Before registering the catalogue, keep these values aligned with the real publisher and replace `CKAN_SITE_URL` with the final public HTTPS URL.
````

- [ ] **Step 2: Run demo seed**

Run:

```bash
cd ckan-docker-prod
bash bin/seed-demo-data
```

Expected output includes:

```text
Demo data seeded.
Catalog: http://localhost:5000/catalog.ttl
```

- [ ] **Step 3: Run final smoke test**

Run:

```bash
cd ckan-docker-prod
bash bin/verify-prod
```

Expected: PASS.

- [ ] **Step 4: Inspect the final RDF externally**

Run:

```powershell
$catalog = (Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:5000/catalog.ttl').Content
if ($catalog -notmatch 'https://data.gov.sk/id/legal-subject/00164381') { throw 'Missing ministry publisher URI' }
if ($catalog -notmatch 'leg:termsOfUse') { throw 'Missing Slovak termsOfUse' }
if ($catalog -notmatch 'dcat:downloadURL') { throw 'Missing downloadURL' }
if ($catalog -match 'dct:format \"CSV\"') { throw 'CSV format is still a literal' }
Write-Output 'External DCAT RDF check OK'
```

Expected:

```text
External DCAT RDF check OK
```

- [ ] **Step 5: Commit documentation and validation updates**

Run:

```bash
git add ckan-docker-prod/bin/verify-prod ckan-docker-prod/README.md
git commit -m "docs: document DataHub DCAT AP SK metadata"
```

If `verify-prod` was already committed in Task 1 and unchanged, commit only `README.md`.

---

## Completion Checklist

- [ ] `git status --short` shows only known unrelated user changes and ignored `.env` remains untracked/unstaged.
- [ ] `bash ckan-docker-prod/bin/verify-prod` passes.
- [ ] `http://localhost:5000/catalog.ttl` includes the ministry publisher URI.
- [ ] The final answer reports that the local URL remains `http://localhost:5000/catalog.ttl`.
- [ ] The final answer states that slovensko.sk registration still requires replacing localhost with a public HTTPS `CKAN_SITE_URL`.
