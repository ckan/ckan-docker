# DataHub Header And Homepage Branding Design

## Context

The production deployment in `ckan-docker-prod` uses the default CKAN layout with a small `ckanext-datahub` extension. The extension already removes visible CKAN footer branding and sets the site title to `DataHub Open Data`.

The current homepage still shows default CKAN branding in two visible places:

- the top header logo/text renders `ckan`
- the homepage intro renders `Vitajte v CKAN`

The user wants both changed while keeping the default CKAN layout and without re-enabling the IDSK theme.

## Decisions

- The top header brand text must be `Open Data`.
- The homepage intro heading must be `Vitajte v Open Data`.
- The homepage intro paragraph must describe the open data catalog, not CKAN.
- The default CKAN navigation, search, colors, cards, and layout stay unchanged.
- The IDSK theme stays disabled.
- The existing `ckanext-datahub` extension remains the branding boundary.

## Template Scope

The default CKAN templates were checked in the running CKAN 2.11 container. The relevant paths are:

- `header.html`
- `home/snippets/promoted.html`

The implementation should add overrides for these two templates under:

- `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/templates/header.html`
- `ckan-docker-prod/ckan/ckanext-datahub/ckanext/datahub/templates/home/snippets/promoted.html`

## Header Behavior

The header override should preserve the default CKAN header structure, account masthead, navigation, search form, and responsive behavior. Only the `header_logo` block should change.

The logo area should render a text link:

```text
Open Data
```

It should link to the homepage and use the existing CKAN masthead styles so the page keeps the default CKAN look.

## Homepage Intro Behavior

The homepage promoted snippet should preserve the default card/module structure and featured image area. The default CKAN fallback text should be replaced with:

```text
Vitajte v Open Data
```

and a short catalog-oriented paragraph such as:

```text
Katalog otvorenych dat Ministerstva skolstva. Najdete tu datasety a datove zdroje publikovane pre verejne pouzitie.
```

ASCII text is used because the production env and current tracked files already use ASCII-normalized Slovak text in several places.

If `g.site_intro_text` is configured in CKAN, the snippet can continue to render that configured text. The custom fallback should apply when no intro text is configured.

## Verification

After implementation:

- Rebuild and restart the production CKAN stack.
- Run `bash bin/verify-prod`.
- Verify `http://localhost:5000` contains `Open Data`.
- Verify `http://localhost:5000` contains `Vitajte v Open Data`.
- Verify `http://localhost:5000` does not contain visible `Vitajte v CKAN`.
- Verify `http://localhost:5000` does not contain visible `ckan-footer-logo`, `Powered by CKAN`, `CKAN API`, or `CKAN Association`.
- Verify `/catalog.ttl` still returns a DCAT catalog.
- Verify `bin/seed-demo-data` still works and the demo dataset remains in the catalog.

## Out Of Scope

- Replacing the full homepage layout.
- Changing colors, typography, or navigation labels beyond the requested header brand.
- Re-enabling IDSK or adding IDSK assets.
- Changing dataset, organization, or DCAT behavior.
