# DataHub Header And Homepage Branding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the remaining visible CKAN branding in the production homepage header and intro with `Open Data` while keeping the default CKAN layout.

**Architecture:** Extend the existing `ckanext-datahub` production-only extension with two focused template overrides. Use `ckan_extends` for `header.html` so only the logo block changes, and copy the small promoted homepage snippet to replace its default CKAN fallback text. Extend the production smoke check to fail if the old CKAN header/homepage text returns.

**Tech Stack:** CKAN 2.11, Jinja2 CKAN templates, `ckanext-datahub`, Docker Compose, Bash smoke checks.

---

## File Structure

- Modify `ckan-docker-prod/bin/verify-prod`: add checks for `Open Data`, `Vitajte v Open Data`, and absence of the old CKAN intro/logo markers.
- Create `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/templates/header.html`: CKAN template extension overriding only `header_logo`.
- Create `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/templates/home/snippets/promoted.html`: homepage promoted snippet with DataHub/Open Data intro fallback text.
- Modify `ckan-docker-prod/ckan/ckanext-datahub/setup.py`: include nested template paths in package data.

### Task 1: Add Header And Homepage Regression Checks

**Files:**
- Modify: `ckan-docker-prod/bin/verify-prod`

- [ ] **Step 1: Update the homepage checks**

In `ckan-docker-prod/bin/verify-prod`, replace the current homepage check block:

```bash
home_html="$(docker compose exec -T ckan wget -qO- http://localhost:5000)"
printf '%s' "$home_html" | grep -q "DataHub Open Data"
if printf '%s' "$home_html" | grep -Eq "Powered by CKAN|CKAN API|CKAN Association|ckan-footer-logo"; then
  echo "Visible CKAN branding is still present on the homepage." >&2
  exit 1
fi
```

with:

```bash
home_html="$(docker compose exec -T ckan wget -qO- http://localhost:5000)"
printf '%s' "$home_html" | grep -q "DataHub Open Data"
printf '%s' "$home_html" | grep -q "Open Data"
printf '%s' "$home_html" | grep -q "Vitajte v Open Data"
if printf '%s' "$home_html" | grep -Eq "Vitajte v CKAN|Welcome to CKAN|This is a nice introductory paragraph about CKAN|/base/images/ckan-logo.png|ckan-footer-logo|Powered by CKAN|CKAN API|CKAN Association"; then
  echo "Visible CKAN branding is still present on the homepage." >&2
  exit 1
fi
```

- [ ] **Step 2: Run the smoke check and verify the expected failure**

Run from `ckan-docker-prod`:

```bash
bash bin/verify-prod
```

Expected: FAIL because `Vitajte v Open Data` is not rendered yet and the header still uses the default CKAN logo.

### Task 2: Add Header And Homepage Template Overrides

**Files:**
- Create: `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/templates/header.html`
- Create: `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/templates/home/snippets/promoted.html`
- Modify: `ckan-docker-prod/ckan/ckanext-datahub/setup.py`

- [ ] **Step 1: Create the focused header override**

Create `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/templates/header.html`:

```html
{% ckan_extends %}

{% block header_logo %}
  <h1>
    <a href="{{ h.url_for('home.index') }}">Open Data</a>
  </h1>
{% endblock %}
```

- [ ] **Step 2: Create the homepage promoted snippet override**

Create `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/templates/home/snippets/promoted.html`:

```html
{% set intro = g.site_intro_text %}

<div class="module-promotion card box">
  <div>
    {% if intro %}
      {{ h.render_markdown(intro) }}
    {% else %}
      <h1 class="page-heading">{{ _("Vitajte v Open Data") }}</h1>
      <p>
        {{ _("Katalog otvorenych dat Ministerstva skolstva. Najdete tu datasety a datove zdroje publikovane pre verejne pouzitie.") }}
      </p>
    {% endif %}
  </div>

  {% block home_image %}
    <section class="featured media-overlay hidden-xs">
      <h2 class="media-heading">{% block home_image_caption %}{{ _("Toto je vybrana sekcia") }}{% endblock %}</h2>
      {% block home_image_content %}
        <a class="media-image" href="#">
          <img class="img-fluid" src="{{ h.url_for_static('/base/images/placeholder-420x220.png') }}" alt="Placeholder" />
        </a>
      {% endblock %}
    </section>
  {% endblock %}
</div>
```

- [ ] **Step 3: Include nested templates in the extension package**

In `ckan-docker-prod/ckan/ckanext-datahub/setup.py`, replace:

```python
        "ckanext.datahub": [
            "templates/*.html",
        ],
```

with:

```python
        "ckanext.datahub": [
            "templates/*.html",
            "templates/**/*.html",
        ],
```

- [ ] **Step 4: Rebuild and restart the production stack**

Run from `ckan-docker-prod`:

```bash
docker compose up -d --build
```

Expected: image rebuilds, CKAN restarts, services reach running or healthy state.

- [ ] **Step 5: Run the smoke check**

Run:

```bash
bash bin/verify-prod
```

Expected: PASS with `Production smoke check passed.`

- [ ] **Step 6: Verify the homepage text directly**

Run:

```powershell
$homepageHtml = (Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:5000').Content
if ($homepageHtml -notmatch 'Open Data') { throw 'Header brand is missing Open Data' }
if ($homepageHtml -notmatch 'Vitajte v Open Data') { throw 'Homepage intro is missing Vitajte v Open Data' }
if ($homepageHtml -match 'Vitajte v CKAN|Welcome to CKAN|This is a nice introductory paragraph about CKAN|/base/images/ckan-logo.png') { throw 'Old CKAN branding is still visible' }
Write-Output 'Header and homepage branding OK'
```

Expected: `Header and homepage branding OK`.

- [ ] **Step 7: Verify catalog and demo seed still work**

Run from `ckan-docker-prod`:

```bash
bash bin/seed-demo-data
```

Then run:

```powershell
$catalog = (Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:5000/catalog.ttl').Content
if ($catalog -notmatch 'dcat:Catalog') { throw 'Catalog RDF missing dcat:Catalog' }
if ($catalog -notmatch 'Testovaci zoznam skol') { throw 'Catalog does not include demo dataset title' }
Write-Output 'Catalog RDF OK'
```

Expected:

```text
Demo data seeded.
Organization: http://localhost:5000/organization/minedu
Dataset: http://localhost:5000/dataset/testovaci-zoznam-skol
Catalog: http://localhost:5000/catalog.ttl
Catalog RDF OK
```

- [ ] **Step 8: Commit the implementation**

```bash
git add ckan-docker-prod/bin/verify-prod ckan-docker-prod/ckan/ckanext-datahub/setup.py ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/templates/header.html ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/templates/home/snippets/promoted.html
git commit -m "feat: replace CKAN header and homepage branding"
```

## Final Verification

Run from `ckan-docker-prod`:

```bash
docker compose ps
bash bin/verify-prod
bash bin/seed-demo-data
```

Run from the repository root or `ckan-docker-prod`:

```powershell
$homepageHtml = (Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:5000').Content
if ($homepageHtml -notmatch 'Open Data') { throw 'Header brand is missing Open Data' }
if ($homepageHtml -notmatch 'Vitajte v Open Data') { throw 'Homepage intro is missing Vitajte v Open Data' }
if ($homepageHtml -match 'Vitajte v CKAN|Welcome to CKAN|This is a nice introductory paragraph about CKAN|/base/images/ckan-logo.png|Powered by CKAN|CKAN API|CKAN Association|ckan-footer-logo') { throw 'Old CKAN branding is still visible' }
$catalog = (Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:5000/catalog.ttl').Content
if ($catalog -notmatch 'dcat:Catalog') { throw 'Catalog RDF missing dcat:Catalog' }
if ($catalog -notmatch 'Testovaci zoznam skol') { throw 'Catalog does not include demo dataset title' }
Write-Output 'Final branding and catalog verification OK'
```

Expected:

- Docker services are running or healthy.
- `verify-prod` passes.
- `seed-demo-data` passes.
- Homepage shows `Open Data`.
- Homepage shows `Vitajte v Open Data`.
- Homepage does not show the old CKAN logo or CKAN intro text.
- Catalog still exposes the demo dataset.
