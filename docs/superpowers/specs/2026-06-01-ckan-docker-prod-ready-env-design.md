# CKAN Docker Production Ready Environment Design

Date: 2026-06-01

## Goal

Make `ckan-docker-prod` usable as a ready-to-run production deployment bundle by adding a local generated `.env` file with strong secrets and a localhost site URL for the current pre-domain phase.

The bundle should be transferable to a server and start with:

```bash
docker compose up -d --build
```

The deployment is still not ready for national LKOD registration until the localhost URL is replaced with a final public HTTPS domain.

## Chosen Approach

Generate real secrets into `ckan-docker-prod/.env` and keep that file uncommitted.

The root `.gitignore` already ignores `.env`, so `ckan-docker-prod/.env` is ignored by Git. This is the correct place for generated production secrets. The repository will continue to track only `.env.example`, scripts, documentation, and compose files.

Do not commit generated secrets to Git.

## Generated Values

Create `ckan-docker-prod/.env` from `ckan-docker-prod/.env.example` and replace all placeholder values.

Generate strong random values for:

- `POSTGRES_PASSWORD`
- `CKAN_DB_PASSWORD`
- `DATASTORE_READONLY_PASSWORD`
- `CKAN___BEAKER__SESSION__SECRET`
- `CKAN___API_TOKEN__JWT__ENCODE__SECRET`
- `CKAN___API_TOKEN__JWT__DECODE__SECRET`
- `CKAN_SYSADMIN_PASSWORD`
- `CKAN_SMTP_USER`
- `CKAN_SMTP_PASSWORD`

The CKAN database passwords must also be reflected inside:

- `CKAN_SQLALCHEMY_URL`
- `CKAN_DATASTORE_WRITE_URL`
- `CKAN_DATASTORE_READ_URL`

The API token encode/decode secrets can use the same generated value, keeping the required `string:` prefix in both settings.

## Localhost URL

Set the current site URL values to:

```dotenv
CKAN_SITE_URL=http://localhost:5000
CKAN__SITE_URL=http://localhost:5000
```

This makes the bundle startable before a public domain exists. It is valid for local/server smoke testing behind a localhost-bound reverse proxy target.

Before registering the catalog with the Slovak open data flow, replace both values with the public HTTPS URL, for example:

```dotenv
CKAN_SITE_URL=https://opendata.example.sk
CKAN__SITE_URL=https://opendata.example.sk
```

## Template And Documentation Updates

Update `ckan-docker-prod/.env.example` so the temporary default URL is also `http://localhost:5000`, with comments that it must be changed before LKOD registration.

Update `ckan-docker-prod/README.md` so it no longer implies the operator must generate every secret manually. It should say:

- `.env` is included locally for this prepared bundle.
- `.env.example` remains the tracked template.
- generated secrets are not committed.
- copy or preserve `.env` when moving the deployment bundle to the server.
- change `CKAN_SITE_URL` and `CKAN__SITE_URL` to the final public HTTPS URL before LKOD registration.

Update `ckan-docker-prod/bin/verify-prod` so it warns when `ckan.site_url` is either:

- `https://CHANGE-ME.example.sk`
- `http://localhost:5000`

The warning should not fail the smoke check. The stack must remain testable before a public domain exists.

## Security Notes

Do not print the generated secrets in final assistant messages. Tell the operator that they are stored in `ckan-docker-prod/.env`.

If this bundle is later committed to a remote repository, confirm that `ckan-docker-prod/.env` is still ignored and not staged.

If the generated `.env` is copied to a real server, treat it as a production secret file and restrict file permissions according to the server operating system.

## Acceptance Criteria

- `ckan-docker-prod/.env` exists locally and is ignored by Git.
- `.env` contains no `CHANGE_ME` values.
- `.env` uses `http://localhost:5000` for both CKAN site URL settings.
- database connection URLs contain the generated database passwords.
- `.env.example` documents localhost as the temporary pre-domain default.
- `README.md` explains that the local `.env` is ready to run but must be updated with public HTTPS before LKOD registration.
- `bin/verify-prod` warns on localhost URL without failing.
- Git status does not show `ckan-docker-prod/.env` as staged, modified, or untracked.
