# DataHub DCAT-AP-SK 3.0 Documents Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the `ckan-docker-prod` CKAN deployment emit DCAT-AP-SK 3.0 document-interface RDF for `/catalog.ttl` and `/dataset/{name}.ttl`.

**Architecture:** Keep `ckanext-dcat` as the endpoint provider and upgrade the configured base profile to `euro_dcat_ap_3`. Extend `ckanext-datahub`'s existing `datahub_dcat_ap_sk` profile as the final RDF graph normalizer for Slovak language tags, document endpoint IRIs, spatial/type defaults, legal terms, and CSV controlled-vocabulary values.

**Tech Stack:** CKAN 2.11, `ckanext-dcat`, `ckanext-scheming`, Python/RDFlib RDF profile, Bash production scripts, Docker Compose.

---

## Source References

- DCAT-AP-SK 3.0 document interface: https://raw.githubusercontent.com/slovak-egov/centralny-model-udajov/develop/tbox/national/dcat-ap-sk/index.html
- `ckanext-dcat` RDF endpoints: https://docs.ckan.org/projects/ckanext-dcat/en/latest/endpoints/
- `ckanext-dcat` profiles: https://docs.ckan.org/projects/ckanext-dcat/en/latest/profiles/
- Approved design: `docs/superpowers/specs/2026-06-03-datahub-dcat-ap-sk-3-documents-design.md`

## File Structure

- `ckan-docker-prod/bin/verify-prod`: production smoke test and executable RDF regression suite. This is the test harness for the work.
- `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/dcat_ap_sk.py`: custom RDF graph normalizer that runs after the CKAN DCAT base profiles.
- `ckan-docker-prod/ckan/docker-entrypoint.d/02_setup_prod_config.sh`: writes CKAN runtime config, including the DCAT profile chain.
- `ckan-docker-prod/.env.example`: documents env-driven defaults for a deployable server package.
- `ckan-docker-prod/docker-compose.yml`: passes env values into the CKAN container.
- `ckan-docker-prod/bin/seed-demo-data`: reseeds Slovak demo organization, dataset, tags, and CSV resource.
- `ckan-docker-prod/README.md`: documents the catalog and dataset detail RDF URLs.

## Dirty Worktree Guard

Before every commit, check:

```powershell
git -c safe.directory='C:/Users/ochot/OneDrive/Počítač/MinEdu/CKAN/ckan-docker' status --short
```

Known unrelated changes that must not be staged by this plan:

- `.env.example`
- `ckan/ckanext-idsk/setup.py`
- `ckan/ckanext-idsk/ckanext/idsk/schemas/`

---

### Task 1: Add Failing DCAT-AP-SK 3.0 Document Verifier

**Files:**
- Modify: `ckan-docker-prod/bin/verify-prod`

- [ ] **Step 1: Extend the embedded Python verifier with DCAT-AP-SK 3 constants**

Inside the Python heredoc in `ckan-docker-prod/bin/verify-prod`, keep the existing imports and add `Namespace` and `XSD`:

```python
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import DCTERMS, FOAF, RDF, XSD
```

Replace the existing namespace constants with:

```python
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCATAP = Namespace("http://data.europa.eu/r5r/")
LEG = Namespace("https://data.gov.sk/def/ontology/legislation/")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
```

Keep the existing `term(namespace, name)` helper; it will still work with `Namespace`.

- [ ] **Step 2: Read new env values in the verifier**

After the existing env reads, add:

```python
catalog_title = os.environ.get("DATAHUB_DCAT_CATALOG_TITLE")
catalog_description = os.environ.get("DATAHUB_DCAT_CATALOG_DESCRIPTION")
default_language = os.environ.get("DATAHUB_DCAT_DEFAULT_LANGUAGE")
default_spatial_uri = os.environ.get("DATAHUB_DCAT_DEFAULT_SPATIAL_URI")
default_dataset_type_uri = os.environ.get("DATAHUB_DCAT_DEFAULT_DATASET_TYPE_URI")
site_url = os.environ.get("CKAN_SITE_URL") or os.environ.get("CKAN__SITE_URL")
demo_dataset_name = "testovaci-zoznam-skol"
```

After the existing missing-env checks, add:

```python
if not catalog_title:
    failures.append("Missing DATAHUB_DCAT_CATALOG_TITLE.")
if not catalog_description:
    failures.append("Missing DATAHUB_DCAT_CATALOG_DESCRIPTION.")
if not default_language:
    failures.append("Missing DATAHUB_DCAT_DEFAULT_LANGUAGE.")
if not default_spatial_uri:
    failures.append("Missing DATAHUB_DCAT_DEFAULT_SPATIAL_URI.")
if not default_dataset_type_uri:
    failures.append("Missing DATAHUB_DCAT_DEFAULT_DATASET_TYPE_URI.")
if not site_url:
    failures.append("Missing CKAN_SITE_URL or CKAN__SITE_URL.")
```

After URIRef conversion of existing env values, add:

```python
default_spatial = URIRef(default_spatial_uri)
default_dataset_type = URIRef(default_dataset_type_uri)
site_url = site_url.rstrip("/")
expected_catalog = URIRef(site_url)
expected_demo_dataset_document = URIRef(f"{site_url}/dataset/{demo_dataset_name}.ttl")
expected_demo_dataset_page = URIRef(f"{site_url}/dataset/{demo_dataset_name}")
```

- [ ] **Step 3: Add language and exact-object helpers**

Below `format_values`, add:

```python
def literals_with_lang(graph, subject, predicate, lang):
    return {
        value
        for value in graph.objects(subject, predicate)
        if isinstance(value, Literal) and value.language == lang
    }


def require_lang_literal(failures, graph, subject, predicate, predicate_name, lang):
    values = literals_with_lang(graph, subject, predicate, lang)
    if not values:
        failures.append(f"{subject} is missing {predicate_name} literal with @{lang}.")


def require_exact_objects(failures, graph, subject, predicate, predicate_name, expected):
    actual = set(graph.objects(subject, predicate))
    if actual != expected:
        failures.append(
            f"{subject} {predicate_name} must exactly match "
            f"expected {format_values(expected)}, actual {format_values(actual)}."
        )


def require_iri(failures, graph, subject, predicate, predicate_name):
    for value in graph.objects(subject, predicate):
        if not isinstance(value, URIRef):
            failures.append(f"{subject} {predicate_name} must be an IRI, got {value.n3()}.")
```

- [ ] **Step 4: Fetch the demo dataset detail graph**

After the current catalog graph parse block, add:

```python
dataset_graph = Graph()
try:
    dataset_url = f"http://localhost:5000/dataset/{demo_dataset_name}.ttl"
    with urllib.request.urlopen(dataset_url) as response:
        dataset_graph.parse(data=response.read(), format="turtle")
except Exception as exc:
    failures.append(f"Unable to fetch or parse dataset detail TTL: {exc}")
    report_failures(failures)
    sys.exit(1)
```

- [ ] **Step 5: Strengthen catalog checks**

Inside the `for catalog in catalogs:` block, after publisher checks, add:

```python
    require_lang_literal(
        failures,
        graph,
        catalog,
        DCTERMS.title,
        "dct:title",
        default_language,
    )
    require_lang_literal(
        failures,
        graph,
        catalog,
        DCTERMS.description,
        "dct:description",
        default_language,
    )
    require_exact_objects(
        failures,
        graph,
        catalog,
        DCTERMS.title,
        "dct:title",
        {Literal(catalog_title, lang=default_language)},
    )
    require_exact_objects(
        failures,
        graph,
        catalog,
        DCTERMS.description,
        "dct:description",
        {Literal(catalog_description, lang=default_language)},
    )

    dataset_links = set(graph.objects(catalog, term(DCAT, "dataset")))
    if expected_demo_dataset_document not in dataset_links:
        failures.append(
            f"{catalog} dcat:dataset must include {expected_demo_dataset_document.n3()}."
        )
    for dataset_link in dataset_links:
        if not isinstance(dataset_link, URIRef):
            failures.append(f"{catalog} dcat:dataset must be an IRI, got {dataset_link.n3()}.")
        elif not str(dataset_link).endswith(".ttl"):
            failures.append(f"{catalog} dcat:dataset must point to a .ttl document: {dataset_link}.")
```

After publisher name checks, require the publisher name to be language-tagged:

```python
expected_publisher_names = {Literal(publisher_name, lang=default_language)}
```

- [ ] **Step 6: Add dataset detail document checks**

Before `if failures:`, add this block:

```python
detail_datasets = list(dataset_graph.subjects(RDF.type, term(DCAT, "Dataset")))
if expected_demo_dataset_document not in detail_datasets:
    failures.append(
        "Dataset detail document must contain the demo dcat:Dataset subject "
        f"{expected_demo_dataset_document.n3()}."
    )

for dataset in detail_datasets:
    require_lang_literal(
        failures,
        dataset_graph,
        dataset,
        DCTERMS.title,
        "dct:title",
        default_language,
    )
    require_lang_literal(
        failures,
        dataset_graph,
        dataset,
        DCTERMS.description,
        "dct:description",
        default_language,
    )
    require_lang_literal(
        failures,
        dataset_graph,
        dataset,
        term(DCAT, "keyword"),
        "dcat:keyword",
        default_language,
    )
    require_exact_objects(
        failures,
        dataset_graph,
        dataset,
        DCTERMS.publisher,
        "dct:publisher",
        {publisher},
    )
    require_exact_objects(
        failures,
        dataset_graph,
        dataset,
        DCTERMS.spatial,
        "dct:spatial",
        {default_spatial},
    )
    require_exact_objects(
        failures,
        dataset_graph,
        dataset,
        DCTERMS.type,
        "dct:type",
        {default_dataset_type},
    )
    landing_pages = set(dataset_graph.objects(dataset, term(DCAT, "landingPage")))
    if expected_demo_dataset_page not in landing_pages:
        failures.append(
            f"{dataset} dcat:landingPage must include {expected_demo_dataset_page.n3()}."
        )
    for distribution in dataset_graph.objects(dataset, term(DCAT, "distribution")):
        if not isinstance(distribution, URIRef):
            failures.append(f"{dataset} dcat:distribution must be an IRI, got {distribution.n3()}.")
```

- [ ] **Step 7: Apply distribution checks to catalog and dataset detail graphs**

Extract the existing distribution loop into a helper:

```python
def validate_distributions(
    failures,
    graph,
    default_format,
    default_media_type,
    terms_authors_work_type,
    terms_original_database_type,
    terms_database_protected_by_special_rights_type,
    terms_personal_data_containment_type,
    default_language,
):
    distributions = list(graph.subjects(RDF.type, term(DCAT, "Distribution")))
    if not distributions:
        failures.append("No dcat:Distribution found.")

    for distribution in distributions:
        required_distribution_predicates = [
            (term(DCAT, "accessURL"), "dcat:accessURL"),
            (term(DCAT, "downloadURL"), "dcat:downloadURL"),
            (DCTERMS.format, "dct:format"),
            (term(DCAT, "mediaType"), "dcat:mediaType"),
            (term(LEG, "termsOfUse"), "leg:termsOfUse"),
        ]
        for predicate, predicate_name in required_distribution_predicates:
            if not list(graph.objects(distribution, predicate)):
                add_missing(failures, distribution, predicate_name)

        require_lang_literal(
            failures,
            graph,
            distribution,
            DCTERMS.title,
            "dct:title",
            default_language,
        )
        if list(graph.objects(distribution, DCTERMS.description)):
            require_lang_literal(
                failures,
                graph,
                distribution,
                DCTERMS.description,
                "dct:description",
                default_language,
            )

        access_urls = set(graph.objects(distribution, term(DCAT, "accessURL")))
        download_urls = set(graph.objects(distribution, term(DCAT, "downloadURL")))
        if access_urls and download_urls and access_urls != download_urls:
            failures.append(
                f"{distribution} dcat:accessURL must equal dcat:downloadURL for file resources."
            )

        distribution_formats = set(graph.objects(distribution, DCTERMS.format))
        distribution_media_types = set(graph.objects(distribution, term(DCAT, "mediaType")))
        expected_formats = {default_format}
        expected_media_types = {default_media_type}

        if is_csv_distribution(graph, distribution, default_format, default_media_type):
            if distribution_formats != expected_formats:
                failures.append(
                    f"{distribution} CSV dct:format must exactly match "
                    f"expected {format_values(expected_formats)}, "
                    f"actual {format_values(distribution_formats)}."
                )
            if distribution_media_types != expected_media_types:
                failures.append(
                    f"{distribution} CSV dcat:mediaType must exactly match "
                    f"expected {format_values(expected_media_types)}, "
                    f"actual {format_values(distribution_media_types)}."
                )
        else:
            if default_format in distribution_formats:
                failures.append(
                    f"{distribution} non-CSV dct:format must not equal "
                    "DATAHUB_DCAT_DEFAULT_FORMAT_URI."
                )
            if default_media_type in distribution_media_types:
                failures.append(
                    f"{distribution} non-CSV dcat:mediaType must not equal "
                    "DATAHUB_DCAT_DEFAULT_MEDIA_TYPE_URI."
                )

        if (distribution, DCTERMS.format, Literal("CSV")) in graph:
            failures.append(f'{distribution} keeps literal dct:format "CSV".')
        if (distribution, term(DCAT, "mediaType"), Literal("text/csv")) in graph:
            failures.append(f'{distribution} keeps literal dcat:mediaType "text/csv".')

        for terms_of_use in graph.objects(distribution, term(LEG, "termsOfUse")):
            if (terms_of_use, RDF.type, term(LEG, "TermsOfUse")) not in graph:
                add_missing(failures, terms_of_use, "rdf:type leg:TermsOfUse")

            exact_terms_predicates = [
                (term(LEG, "authorsWorkType"), "leg:authorsWorkType", terms_authors_work_type),
                (term(LEG, "originalDatabaseType"), "leg:originalDatabaseType", terms_original_database_type),
                (
                    term(LEG, "databaseProtectedBySpecialRightsType"),
                    "leg:databaseProtectedBySpecialRightsType",
                    terms_database_protected_by_special_rights_type,
                ),
                (
                    term(LEG, "personalDataContainmentType"),
                    "leg:personalDataContainmentType",
                    terms_personal_data_containment_type,
                ),
            ]
            for predicate, predicate_name, expected_object in exact_terms_predicates:
                require_exact_objects(
                    failures,
                    graph,
                    terms_of_use,
                    predicate,
                    predicate_name,
                    {expected_object},
                )
```

Then replace the old inline distribution loop with two calls:

```python
validate_distributions(
    failures,
    graph,
    default_format,
    default_media_type,
    terms_authors_work_type,
    terms_original_database_type,
    terms_database_protected_by_special_rights_type,
    terms_personal_data_containment_type,
    default_language,
)
validate_distributions(
    failures,
    dataset_graph,
    default_format,
    default_media_type,
    terms_authors_work_type,
    terms_original_database_type,
    terms_database_protected_by_special_rights_type,
    terms_personal_data_containment_type,
    default_language,
)
```

- [ ] **Step 8: Update config smoke expectations**

Near the end of `verify-prod`, change:

```bash
docker compose exec -T ckan sh -c "grep -Eq '^ckan.site_description ?= ?Katalog otvorenych dat$' /srv/app/ckan.ini"
docker compose exec -T ckan sh -c "grep -Eq '^ckanext.dcat.rdf.profiles ?= ?euro_dcat_ap_2 euro_dcat_ap_scheming datahub_dcat_ap_sk$' /srv/app/ckan.ini"
```

to:

```bash
docker compose exec -T ckan sh -c "grep -Eq '^ckan.site_description ?= ?Katalóg otvorených dát$' /srv/app/ckan.ini"
docker compose exec -T ckan sh -c "grep -Eq '^ckanext.dcat.rdf.profiles ?= ?euro_dcat_ap_3 euro_dcat_ap_scheming datahub_dcat_ap_sk$' /srv/app/ckan.ini"
```

- [ ] **Step 9: Verify RED**

Run:

```powershell
& 'C:\Program Files\Git\bin\bash.exe' bin/verify-prod
```

Working directory:

```text
C:\Users\ochot\OneDrive\Počítač\MinEdu\CKAN\ckan-docker\ckan-docker-prod
```

Expected: FAIL. The output should include failures such as missing `@sk`, missing `dct:spatial`, missing `dct:type`, missing `dcat:landingPage`, or catalog dataset links not ending in `.ttl`.

- [ ] **Step 10: Commit verifier regression**

Stage and commit only the verifier:

```powershell
git -c safe.directory='C:/Users/ochot/OneDrive/Počítač/MinEdu/CKAN/ckan-docker' add -- ckan-docker-prod/bin/verify-prod
git -c safe.directory='C:/Users/ochot/OneDrive/Počítač/MinEdu/CKAN/ckan-docker' commit -m "test: require DCAT AP SK 3 document RDF"
```

---

### Task 2: Configure DCAT-AP 3 and Env Defaults

**Files:**
- Modify: `ckan-docker-prod/.env.example`
- Modify: `ckan-docker-prod/.env` (ignored runtime file, do not commit)
- Modify: `ckan-docker-prod/docker-compose.yml`
- Modify: `ckan-docker-prod/ckan/docker-entrypoint.d/02_setup_prod_config.sh`

- [ ] **Step 1: Update `.env.example` profile and metadata values**

In `ckan-docker-prod/.env.example`, change:

```env
CKAN__SITE_DESCRIPTION=Katalog otvorenych dat
CKANEXT__DCAT__RDF__PROFILES=euro_dcat_ap_2 euro_dcat_ap_scheming datahub_dcat_ap_sk
DATAHUB_DCAT_CONTACT_NAME=DataHub Open Data
```

to:

```env
CKAN__SITE_DESCRIPTION=Katalóg otvorených dát
CKANEXT__DCAT__RDF__PROFILES=euro_dcat_ap_3 euro_dcat_ap_scheming datahub_dcat_ap_sk
DATAHUB_DCAT_CONTACT_NAME=DataHub Open Data tím
```

Add the new values below the DCAT metadata section:

```env
DATAHUB_DCAT_CATALOG_TITLE=DataHub Open Data
DATAHUB_DCAT_CATALOG_DESCRIPTION=Katalóg otvorených dát
DATAHUB_DCAT_DEFAULT_LANGUAGE=sk
DATAHUB_DCAT_DEFAULT_SPATIAL_URI=https://data.gov.sk/id/nuts1/SK0
DATAHUB_DCAT_DEFAULT_DATASET_TYPE_URI=https://data.gov.sk/def/dataset-type/1
```

- [ ] **Step 2: Update ignored runtime `.env` without changing secrets**

In `ckan-docker-prod/.env`, change only the non-secret keys from Step 1:

```env
CKAN__SITE_DESCRIPTION=Katalóg otvorených dát
CKANEXT__DCAT__RDF__PROFILES=euro_dcat_ap_3 euro_dcat_ap_scheming datahub_dcat_ap_sk
DATAHUB_DCAT_CONTACT_NAME=DataHub Open Data tím
DATAHUB_DCAT_CATALOG_TITLE=DataHub Open Data
DATAHUB_DCAT_CATALOG_DESCRIPTION=Katalóg otvorených dát
DATAHUB_DCAT_DEFAULT_LANGUAGE=sk
DATAHUB_DCAT_DEFAULT_SPATIAL_URI=https://data.gov.sk/id/nuts1/SK0
DATAHUB_DCAT_DEFAULT_DATASET_TYPE_URI=https://data.gov.sk/def/dataset-type/1
```

Leave all generated passwords, tokens, database URLs, SMTP values, and admin credentials unchanged.

- [ ] **Step 3: Pass new env values to the CKAN service**

In `ckan-docker-prod/docker-compose.yml`, add these under the CKAN service environment block next to existing `DATAHUB_DCAT_*` entries:

```yaml
      DATAHUB_DCAT_CATALOG_TITLE: ${DATAHUB_DCAT_CATALOG_TITLE}
      DATAHUB_DCAT_CATALOG_DESCRIPTION: ${DATAHUB_DCAT_CATALOG_DESCRIPTION}
      DATAHUB_DCAT_DEFAULT_LANGUAGE: ${DATAHUB_DCAT_DEFAULT_LANGUAGE}
      DATAHUB_DCAT_DEFAULT_SPATIAL_URI: ${DATAHUB_DCAT_DEFAULT_SPATIAL_URI}
      DATAHUB_DCAT_DEFAULT_DATASET_TYPE_URI: ${DATAHUB_DCAT_DEFAULT_DATASET_TYPE_URI}
```

- [ ] **Step 4: Update entrypoint default profile chain**

In `ckan-docker-prod/ckan/docker-entrypoint.d/02_setup_prod_config.sh`, change:

```bash
ckan config-tool "$CKAN_INI" "ckan.site_description=${CKAN__SITE_DESCRIPTION:-Katalog otvorenych dat}"
ckan config-tool "$CKAN_INI" "ckanext.dcat.rdf.profiles=${CKANEXT__DCAT__RDF__PROFILES:-euro_dcat_ap_2 euro_dcat_ap_scheming datahub_dcat_ap_sk}"
```

to:

```bash
ckan config-tool "$CKAN_INI" "ckan.site_description=${CKAN__SITE_DESCRIPTION:-Katalóg otvorených dát}"
ckan config-tool "$CKAN_INI" "ckanext.dcat.rdf.profiles=${CKANEXT__DCAT__RDF__PROFILES:-euro_dcat_ap_3 euro_dcat_ap_scheming datahub_dcat_ap_sk}"
```

- [ ] **Step 5: Verify config script syntax**

Run:

```powershell
& 'C:\Program Files\Git\bin\bash.exe' -n 'ckan-docker-prod/ckan/docker-entrypoint.d/02_setup_prod_config.sh'
```

Expected: exit code 0.

- [ ] **Step 6: Commit tracked config changes**

```powershell
git -c safe.directory='C:/Users/ochot/OneDrive/Počítač/MinEdu/CKAN/ckan-docker' add -- ckan-docker-prod/.env.example ckan-docker-prod/docker-compose.yml ckan-docker-prod/ckan/docker-entrypoint.d/02_setup_prod_config.sh
git -c safe.directory='C:/Users/ochot/OneDrive/Počítač/MinEdu/CKAN/ckan-docker' commit -m "feat: configure DCAT AP SK 3 defaults"
```

---

### Task 3: Normalize RDF Graphs for DCAT-AP-SK 3 Documents

**Files:**
- Modify: `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/dcat_ap_sk.py`

- [ ] **Step 1: Add namespaces and defaults**

At the top of `dcat_ap_sk.py`, change imports to:

```python
import os
from urllib.parse import urlparse

from ckan.plugins import toolkit
from ckanext.dcat.profiles import RDFProfile
from rdflib import BNode, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, FOAF, RDF
```

Add namespaces:

```python
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCATAP = Namespace("http://data.europa.eu/r5r/")
FILETYPE = Namespace("http://publications.europa.eu/resource/authority/file-type/")
FREQ = Namespace("http://publications.europa.eu/resource/authority/frequency/")
LEG = Namespace("https://data.gov.sk/def/ontology/legislation/")
TEXT = Namespace("http://www.iana.org/assignments/media-types/text/")
THEME = Namespace("http://publications.europa.eu/resource/authority/data-theme/")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
```

Extend `DEFAULTS` with:

```python
    "DATAHUB_DCAT_CATALOG_TITLE": "DataHub Open Data",
    "DATAHUB_DCAT_CATALOG_DESCRIPTION": "Katalóg otvorených dát",
    "DATAHUB_DCAT_DEFAULT_LANGUAGE": "sk",
    "DATAHUB_DCAT_DEFAULT_SPATIAL_URI": "https://data.gov.sk/id/nuts1/SK0",
    "DATAHUB_DCAT_DEFAULT_DATASET_TYPE_URI": "https://data.gov.sk/def/dataset-type/1",
```

- [ ] **Step 2: Add URL and language helpers**

Inside `DataHubDCATAPSKProfile`, after `_publisher`, add:

```python
    def _language(self):
        return self._setting("DATAHUB_DCAT_DEFAULT_LANGUAGE")

    def _site_url(self):
        site_url = (
            os.environ.get("CKAN_SITE_URL")
            or os.environ.get("CKAN__SITE_URL")
            or toolkit.config.get("ckan.site_url")
            or ""
        )
        return site_url.rstrip("/")

    def _dataset_name(self, dataset_dict, dataset_ref):
        name = dataset_dict.get("name")
        if name:
            return name

        ref = str(dataset_ref).rstrip("/")
        return ref.rsplit("/", 1)[-1]

    def _dataset_page_uri(self, dataset_dict, dataset_ref):
        return URIRef(f"{self._site_url()}/dataset/{self._dataset_name(dataset_dict, dataset_ref)}")

    def _dataset_document_uri(self, dataset_dict, dataset_ref):
        return URIRef(f"{self._site_url()}/dataset/{self._dataset_name(dataset_dict, dataset_ref)}.ttl")

    def _resource_document_uri(self, dataset_dict, dataset_ref, resource_ref):
        resource_id = str(resource_ref).rstrip("/").rsplit("/", 1)[-1]
        return URIRef(
            f"{self._site_url()}/dataset/"
            f"{self._dataset_name(dataset_dict, dataset_ref)}/resource/{resource_id}"
        )

    def _package_name_from_ref(self, dataset_ref):
        dataset_id = str(dataset_ref).rstrip("/").rsplit("/", 1)[-1]
        try:
            package = toolkit.get_action("package_show")(
                {"ignore_auth": True},
                {"id": dataset_id},
            )
        except Exception:
            return dataset_id

        return package.get("name") or dataset_id

    def _replace_literal(self, subject, predicate, value, lang=None):
        self.g.remove((subject, predicate, None))
        if value:
            self.g.add((subject, predicate, Literal(value, lang=lang)))

    def _first_literal_text(self, subject, predicate):
        for value in self.g.objects(subject, predicate):
            if isinstance(value, Literal):
                text = str(value).strip()
                if text:
                    return text
        return None
```

- [ ] **Step 3: Bind namespaces**

Replace `_bind_namespaces` with:

```python
    def _bind_namespaces(self):
        self.g.bind("dcat", DCAT)
        self.g.bind("dcatap", DCATAP)
        self.g.bind("dct", DCTERMS)
        self.g.bind("filetype", FILETYPE)
        self.g.bind("foaf", FOAF)
        self.g.bind("freq", FREQ)
        self.g.bind("leg", LEG)
        self.g.bind("text", TEXT)
        self.g.bind("theme", THEME)
        self.g.bind("vcard", VCARD)
```

- [ ] **Step 4: Normalize catalog metadata and dataset document links**

Replace `graph_from_catalog` with:

```python
    def graph_from_catalog(self, catalog_dict, catalog_ref):
        self._bind_namespaces()
        self._normalize_publisher(catalog_ref)
        self._normalize_catalog_metadata(catalog_ref)
        self._normalize_catalog_dataset_links(catalog_ref)
```

Add:

```python
    def _normalize_catalog_metadata(self, catalog_ref):
        lang = self._language()
        self._replace_literal(
            catalog_ref,
            DCTERMS.title,
            self._setting("DATAHUB_DCAT_CATALOG_TITLE"),
            lang=lang,
        )
        self._replace_literal(
            catalog_ref,
            DCTERMS.description,
            self._setting("DATAHUB_DCAT_CATALOG_DESCRIPTION"),
            lang=lang,
        )
        self.g.remove((catalog_ref, DCTERMS.language, None))

        homepage = URIRef(self._site_url())
        self.g.remove((catalog_ref, FOAF.homepage, None))
        self.g.add((catalog_ref, FOAF.homepage, homepage))

        self._ensure_contact_point(catalog_ref)

    def _normalize_catalog_dataset_links(self, catalog_ref):
        existing_links = list(self.g.objects(catalog_ref, DCAT.dataset))
        self.g.remove((catalog_ref, DCAT.dataset, None))
        for dataset_link in existing_links:
            dataset_name = self._package_name_from_ref(dataset_link)
            self.g.add(
                (
                    catalog_ref,
                    DCAT.dataset,
                    URIRef(f"{self._site_url()}/dataset/{dataset_name}.ttl"),
                )
            )
```

- [ ] **Step 5: Normalize dataset subject and metadata**

Replace `graph_from_dataset` with:

```python
    def graph_from_dataset(self, dataset_dict, dataset_ref):
        self._bind_namespaces()
        dataset_document_ref = self._dataset_document_uri(dataset_dict, dataset_ref)
        self._move_subject(dataset_ref, dataset_document_ref)
        dataset_ref = dataset_document_ref

        self._normalize_publisher(dataset_ref)
        self._normalize_dataset_text(dataset_dict, dataset_ref)
        self._ensure_keywords(dataset_dict, dataset_ref)
        self._ensure_dataset_defaults(dataset_dict, dataset_ref)
        self._ensure_contact_point(dataset_ref)

        distributions = set(self.g.objects(dataset_ref, DCAT.distribution))
        distributions.update(self.g.subjects(RDF.type, DCAT.Distribution))
        for distribution in distributions:
            normalized_distribution = self._normalize_distribution_ref(
                dataset_dict, dataset_ref, distribution
            )
            self._normalize_distribution(normalized_distribution)
```

Add:

```python
    def _move_subject(self, old_subject, new_subject):
        if old_subject == new_subject:
            return

        for _, predicate, obj in list(self.g.triples((old_subject, None, None))):
            self.g.remove((old_subject, predicate, obj))
            self.g.add((new_subject, predicate, obj))

        for subject, predicate, _ in list(self.g.triples((None, None, old_subject))):
            self.g.remove((subject, predicate, old_subject))
            self.g.add((subject, predicate, new_subject))

    def _normalize_dataset_text(self, dataset_dict, dataset_ref):
        lang = self._language()
        title = dataset_dict.get("title") or self._first_literal_text(dataset_ref, DCTERMS.title)
        description = (
            dataset_dict.get("notes")
            or self._first_literal_text(dataset_ref, DCTERMS.description)
        )
        self._replace_literal(dataset_ref, DCTERMS.title, title, lang=lang)
        self._replace_literal(dataset_ref, DCTERMS.description, description, lang=lang)

    def _ensure_dataset_defaults(self, dataset_dict, dataset_ref):
        if not list(self.g.objects(dataset_ref, DCTERMS.spatial)):
            self.g.add(
                (
                    dataset_ref,
                    DCTERMS.spatial,
                    URIRef(self._setting("DATAHUB_DCAT_DEFAULT_SPATIAL_URI")),
                )
            )

        if not list(self.g.objects(dataset_ref, DCTERMS.type)):
            self.g.add(
                (
                    dataset_ref,
                    DCTERMS.type,
                    URIRef(self._setting("DATAHUB_DCAT_DEFAULT_DATASET_TYPE_URI")),
                )
            )

        landing_page = self._dataset_page_uri(dataset_dict, dataset_ref)
        self.g.remove((dataset_ref, DCAT.landingPage, None))
        self.g.add((dataset_ref, DCAT.landingPage, landing_page))
```

- [ ] **Step 6: Make keywords language-tagged**

Remove the current early return:

```python
        if list(self.g.objects(dataset_ref, DCAT.keyword)):
            return
```

Then replace the final add loop in `_ensure_keywords` with:


```python
        self.g.remove((dataset_ref, DCAT.keyword, None))
        for keyword in keywords:
            self.g.add((dataset_ref, DCAT.keyword, Literal(keyword, lang=self._language())))
```

- [ ] **Step 7: Make contact labels language-tagged**

In `_ensure_contact_point`, change:

```python
self.g.add((contact, VCARD.fn, Literal(contact_name)))
```

to:

```python
self.g.add((contact, VCARD.fn, Literal(contact_name, lang=self._language())))
```

- [ ] **Step 8: Normalize publisher name language**

In `_normalize_publisher`, change:

```python
Literal(self._setting("DATAHUB_DCAT_PUBLISHER_NAME"))
```

to:

```python
Literal(self._setting("DATAHUB_DCAT_PUBLISHER_NAME"), lang=self._language())
```

- [ ] **Step 9: Normalize distribution references and text**

Add this helper:

```python
    def _normalize_distribution_ref(self, dataset_dict, dataset_ref, distribution):
        normalized = self._resource_document_uri(dataset_dict, dataset_ref, distribution)
        self._move_subject(distribution, normalized)
        self.g.remove((dataset_ref, DCAT.distribution, distribution))
        self.g.add((dataset_ref, DCAT.distribution, normalized))
        return normalized
```

At the start of `_normalize_distribution`, after `access_urls = ...`, add:

```python
        lang = self._language()
        title = self._first_literal_text(distribution, DCTERMS.title)
        description = self._first_literal_text(distribution, DCTERMS.description)
        self._replace_literal(distribution, DCTERMS.title, title, lang=lang)
        if description:
            self._replace_literal(distribution, DCTERMS.description, description, lang=lang)
```

Keep the existing CSV format/media normalization and `leg:termsOfUse` replacement.

- [ ] **Step 10: Verify Python syntax**

Run:

```powershell
python -m py_compile 'ckan-docker-prod\ckan\ckanext-datahub\ckanext\datahub\dcat_ap_sk.py'
```

Expected: exit code 0.

If `__pycache__` is created, remove only:

```powershell
$path = Resolve-Path 'ckan-docker-prod\ckan\ckanext-datahub\ckanext\datahub\__pycache__' -ErrorAction SilentlyContinue; if ($path) { Remove-Item -LiteralPath $path.Path -Recurse -Force }
```

- [ ] **Step 11: Commit RDF profile changes**

```powershell
git -c safe.directory='C:/Users/ochot/OneDrive/Počítač/MinEdu/CKAN/ckan-docker' add -- ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/dcat_ap_sk.py
git -c safe.directory='C:/Users/ochot/OneDrive/Počítač/MinEdu/CKAN/ckan-docker' commit -m "feat: normalize DCAT AP SK 3 RDF documents"
```

---

### Task 4: Seed Slovak Demo Metadata

**Files:**
- Modify: `ckan-docker-prod/bin/seed-demo-data`

- [ ] **Step 1: Update demo organization text**

Replace organization description values with:

```bash
description="Publikačná organizácia pre otvorené dáta rezortu školstva."
```

Keep organization name `minedu` and title:

```bash
title="Ministerstvo školstva, výskumu, vývoja a mládeže Slovenskej republiky"
```

- [ ] **Step 2: Update demo dataset values**

In both `package_patch` and `package_create`, replace:

```bash
title="Testovaci zoznam skol"
notes="Synteticky testovaci dataset s 10 skolami na overenie publikovania CSV zdroja a DCAT katalogu."
tag_string=demo,skoly,vzdelavanie
contact_name="DataHub Open Data"
```

with:

```bash
title="Testovací zoznam škôl"
notes="Syntetický testovací dataset s 10 školami na overenie publikovania CSV zdroja a DCAT katalógu."
tag_string=demo,školy,vzdelávanie
contact_name="DataHub Open Data tím"
```

- [ ] **Step 3: Update demo CSV headers and rows**

Replace the CSV heredoc content with:

```csv
nazov_skoly,typ_skoly,obec,okres,kraj
Základná škola Demo 01,základná škola,Bratislava,Bratislava I,Bratislavský
Gymnázium Demo 02,gymnázium,Košice,Košice I,Košický
Stredná odborná škola Demo 03,stredná odborná škola,Žilina,Žilina,Žilinský
Základná škola Demo 04,základná škola,Nitra,Nitra,Nitriansky
Gymnázium Demo 05,gymnázium,Prešov,Prešov,Prešovský
Stredná priemyselná škola Demo 06,stredná odborná škola,Trnava,Trnava,Trnavský
Základná škola Demo 07,základná škola,Banská Bystrica,Banská Bystrica,Banskobystrický
Spojená škola Demo 08,spojená škola,Trenčín,Trenčín,Trenčiansky
Základná škola Demo 09,základná škola,Martin,Martin,Žilinský
Gymnázium Demo 10,gymnázium,Poprad,Poprad,Prešovský
```

- [ ] **Step 4: Update resource metadata in the seed Python**

In the embedded Python, change:

```python
resource_name = "Zoznam skol - demo CSV"
```

to:

```python
resource_name = "Zoznam škôl - demo CSV"
```

Change:

```python
"description": "Synteticky CSV subor s 10 demo skolami.",
```

to:

```python
"description": "Syntetický CSV súbor s 10 demo školami.",
```

Change:

```python
package["tag_string"] = "demo,skoly,vzdelavanie"
```

to:

```python
package["tag_string"] = "demo,školy,vzdelávanie"
```

- [ ] **Step 5: Verify shell syntax**

Run:

```powershell
& 'C:\Program Files\Git\bin\bash.exe' -n 'ckan-docker-prod/bin/seed-demo-data'
```

Expected: exit code 0.

- [ ] **Step 6: Commit seed changes**

```powershell
git -c safe.directory='C:/Users/ochot/OneDrive/Počítač/MinEdu/CKAN/ckan-docker' add -- ckan-docker-prod/bin/seed-demo-data
git -c safe.directory='C:/Users/ochot/OneDrive/Počítač/MinEdu/CKAN/ckan-docker' commit -m "feat: seed Slovak DCAT demo metadata"
```

---

### Task 5: Update Documentation for Catalog and Dataset URLs

**Files:**
- Modify: `ckan-docker-prod/README.md`

- [ ] **Step 1: Update DCAT URL section**

Ensure the README includes:

```markdown
## DCAT-AP-SK 3.0 endpoints

For local testing:

```text
http://localhost:5000/catalog.ttl
http://localhost:5000/dataset/testovaci-zoznam-skol.ttl
```

For slovensko.sk registration, use the public HTTPS catalog URL:

```text
https://your-public-domain.example/catalog.ttl
```

The catalog document links each dataset using `dcat:dataset`. The national catalog will fetch those dataset document URLs and expects a complete `dcat:Dataset` record including its distributions.
```

- [ ] **Step 2: Update profile documentation**

Ensure the README says the default profile chain is:

```text
euro_dcat_ap_3 euro_dcat_ap_scheming datahub_dcat_ap_sk
```

And documents the new env values:

```env
DATAHUB_DCAT_CATALOG_TITLE=DataHub Open Data
DATAHUB_DCAT_CATALOG_DESCRIPTION=Katalóg otvorených dát
DATAHUB_DCAT_DEFAULT_LANGUAGE=sk
DATAHUB_DCAT_DEFAULT_SPATIAL_URI=https://data.gov.sk/id/nuts1/SK0
DATAHUB_DCAT_DEFAULT_DATASET_TYPE_URI=https://data.gov.sk/def/dataset-type/1
```

- [ ] **Step 3: Commit README changes**

```powershell
git -c safe.directory='C:/Users/ochot/OneDrive/Počítač/MinEdu/CKAN/ckan-docker' add -- ckan-docker-prod/README.md
git -c safe.directory='C:/Users/ochot/OneDrive/Počítač/MinEdu/CKAN/ckan-docker' commit -m "docs: document DCAT AP SK 3 endpoints"
```

---

### Task 6: Rebuild, Reseed, and Verify Runtime

**Files:**
- Runtime verification only.

- [ ] **Step 1: Rebuild CKAN**

Run:

```powershell
docker compose up -d --build ckan
```

Working directory:

```text
C:\Users\ochot\OneDrive\Počítač\MinEdu\CKAN\ckan-docker\ckan-docker-prod
```

Expected: CKAN image builds and `ckan-docker-prod-ckan-1` starts.

- [ ] **Step 2: Wait for CKAN health**

Run:

```powershell
$deadline = (Get-Date).AddSeconds(120); do { $status = docker compose ps --format json | ConvertFrom-Json | Where-Object { $_.Service -eq 'ckan' } | Select-Object -ExpandProperty Health -ErrorAction SilentlyContinue; if ($status -eq 'healthy') { 'ckan healthy'; exit 0 }; Start-Sleep -Seconds 3 } while ((Get-Date) -lt $deadline); docker compose ps; exit 1
```

Expected:

```text
ckan healthy
```

- [ ] **Step 3: Reseed demo data**

Run:

```powershell
& 'C:\Program Files\Git\bin\bash.exe' bin/seed-demo-data
```

Expected output includes:

```text
Demo data seeded.
Dataset: http://localhost:5000/dataset/testovaci-zoznam-skol
Catalog: http://localhost:5000/catalog.ttl
```

- [ ] **Step 4: Run production verifier**

Run:

```powershell
& 'C:\Program Files\Git\bin\bash.exe' bin/verify-prod
```

Expected output includes:

```text
DCAT-AP-SK RDF validation passed.
Production smoke check passed.
```

The localhost warning is expected while `CKAN_SITE_URL=http://localhost:5000`.

- [ ] **Step 5: Host-level RDF sanity check**

Run:

```powershell
$catalog = (Invoke-WebRequest -UseBasicParsing 'http://localhost:5000/catalog.ttl').Content
$dataset = (Invoke-WebRequest -UseBasicParsing 'http://localhost:5000/dataset/testovaci-zoznam-skol.ttl').Content
$checks = [ordered]@{
  'catalog links dataset ttl' = $catalog.Contains('/dataset/testovaci-zoznam-skol.ttl')
  'catalog title sk' = $catalog.Contains('"DataHub Open Data"@sk')
  'dataset title sk' = $dataset.Contains('"Testovací zoznam škôl"@sk')
  'dataset spatial' = $dataset.Contains('https://data.gov.sk/id/nuts1/SK0')
  'dataset type' = $dataset.Contains('https://data.gov.sk/def/dataset-type/1')
  'distribution terms' = $dataset.Contains('leg:termsOfUse')
}
$checks.GetEnumerator() | ForEach-Object { "{0}: {1}" -f $_.Key, $_.Value }
if ($checks.Values -contains $false) { exit 1 }
```

Expected: all checks print `True`.

- [ ] **Step 6: Final code review**

Dispatch a final code reviewer subagent with this prompt:

```text
Review the DCAT-AP-SK 3.0 document output implementation in ckan-docker-prod. Do not edit files. Check the approved spec docs/superpowers/specs/2026-06-03-datahub-dcat-ap-sk-3-documents-design.md and implementation plan docs/superpowers/plans/2026-06-03-datahub-dcat-ap-sk-3-documents-implementation.md. Focus on RDF correctness, CKAN profile ordering, env propagation, dataset detail endpoint behavior, non-CSV safety, and verifier quality. Return APPROVED or REJECTED with file/line findings.
```

- [ ] **Step 7: Final status check**

Run:

```powershell
git -c safe.directory='C:/Users/ochot/OneDrive/Počítač/MinEdu/CKAN/ckan-docker' status --short
```

Expected: only known unrelated changes remain, or no changes remain.

---

## Completion Criteria

The implementation is complete only when:

- every task commit exists;
- `bin/verify-prod` passes after rebuild and reseed;
- `/catalog.ttl` links `/dataset/testovaci-zoznam-skol.ttl`;
- `/dataset/testovaci-zoznam-skol.ttl` contains the full `dcat:Dataset` record;
- final subagent review returns `APPROVED`;
- final response reports the local catalog URL and dataset detail URL.
