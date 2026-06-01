# CKAN Docker Production Ready Environment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate a local ignored `ckan-docker-prod/.env` with strong secrets and update the production bundle docs/template/checks for a localhost pre-domain setup.

**Architecture:** Keep generated secrets outside Git in `ckan-docker-prod/.env`; keep tracked files limited to `.env.example`, README, and smoke checks. Use `http://localhost:5000` as the current site URL until a real HTTPS domain exists, while preserving warnings before LKOD registration.

**Tech Stack:** PowerShell secret generation, Docker Compose env files, CKAN envvars, Bash smoke script.

---

## File Structure

- Modify `ckan-docker-prod/.env.example`: change the temporary default URL to `http://localhost:5000` and update comments.
- Create ignored `ckan-docker-prod/.env`: generated ready-to-run production env with no `CHANGE_ME` values.
- Modify `ckan-docker-prod/bin/verify-prod`: warn on localhost URL and `CHANGE-ME` URL without failing.
- Modify `ckan-docker-prod/README.md`: document the included local `.env`, server transfer, and final HTTPS URL requirement.

Do not stage or commit `ckan-docker-prod/.env`.

---

### Task 1: Update The Tracked Production Template

**Files:**
- Modify: `ckan-docker-prod/.env.example`
- Modify: `ckan-docker-prod/README.md`
- Modify: `ckan-docker-prod/bin/verify-prod`

- [ ] **Step 1: Update localhost template URL**

In `ckan-docker-prod/.env.example`, replace:

```dotenv
# Site identity. Replace both URL values with the final public HTTPS URL before LKOD registration.
```

with:

```dotenv
# Site identity. localhost is usable for pre-domain smoke tests.
# Replace both URL values with the final public HTTPS URL before LKOD registration.
```

Replace:

```dotenv
CKAN_SITE_URL=https://CHANGE-ME.example.sk
CKAN__SITE_URL=https://CHANGE-ME.example.sk
```

with:

```dotenv
CKAN_SITE_URL=http://localhost:5000
CKAN__SITE_URL=http://localhost:5000
```

- [ ] **Step 2: Update verify script URL warning**

In `ckan-docker-prod/bin/verify-prod`, replace:

```bash
if [ "$site_url" = "https://CHANGE-ME.example.sk" ]; then
  echo "Warning: CKAN_SITE_URL still uses the example value. Do not register LKOD until this is the final public HTTPS URL." >&2
fi
```

with:

```bash
if [ "$site_url" = "https://CHANGE-ME.example.sk" ] || [ "$site_url" = "http://localhost:5000" ]; then
  echo "Warning: CKAN_SITE_URL is not a final public HTTPS URL. Do not register LKOD until this is updated." >&2
fi
```

- [ ] **Step 3: Update README setup guidance**

In `ckan-docker-prod/README.md`, replace the `## First Setup` section through the sentence:

```markdown
Do not register the LKOD catalog while `CKAN_SITE_URL` is `https://CHANGE-ME.example.sk`.
```

with:

```markdown
## First Setup

This prepared local bundle includes an ignored `.env` file with generated secrets. Keep that file with the deployment package when copying `ckan-docker-prod` to a server.

The tracked `.env.example` file remains a template only.

Before exposing the portal publicly:

- Keep `.env` out of Git.
- Check `CKAN_SYSADMIN_EMAIL`.
- Set SMTP values if password reset or mail notifications are required.
- Replace `CKAN_SITE_URL` and `CKAN__SITE_URL` with the final public HTTPS URL.

The current local default is:

```text
http://localhost:5000
```

Do not register the LKOD catalog while `CKAN_SITE_URL` is `http://localhost:5000`.
```

- [ ] **Step 4: Verify tracked file edits**

Run:

```powershell
Select-String -Path .\ckan-docker-prod\.env.example -Pattern "CKAN_SITE_URL=http://localhost:5000|CKAN__SITE_URL=http://localhost:5000"
Select-String -Path .\ckan-docker-prod\bin\verify-prod -Pattern "not a final public HTTPS URL"
Select-String -Path .\ckan-docker-prod\README.md -Pattern "ignored `.env` file|http://localhost:5000|final public HTTPS URL"
```

Expected: all three commands print matching lines.

- [ ] **Step 5: Commit tracked updates**

Run:

```bash
git add ckan-docker-prod/.env.example ckan-docker-prod/bin/verify-prod ckan-docker-prod/README.md
git commit -m "config: prepare production bundle for localhost startup"
```

Expected: commit succeeds and does not include `ckan-docker-prod/.env`.

---

### Task 2: Generate The Ignored Ready-To-Run Environment File

**Files:**
- Create: `ckan-docker-prod/.env` ignored by Git

- [ ] **Step 1: Generate `.env` with strong random values**

Run this PowerShell script from the repository root:

```powershell
function New-Secret {
  param([int]$Bytes = 36)
  $bytes = New-Object byte[] $Bytes
  [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
  return [Convert]::ToBase64String($bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_')
}

$envPath = '.\ckan-docker-prod\.env'
$postgresPassword = New-Secret
$ckanDbPassword = New-Secret
$datastorePassword = New-Secret
$sessionSecret = New-Secret 48
$apiTokenSecret = New-Secret 48
$adminPassword = New-Secret
$smtpUser = "smtp_" + (New-Secret 18)
$smtpPassword = New-Secret

$content = Get-Content .\ckan-docker-prod\.env.example -Raw
$content = $content.Replace('https://CHANGE-ME.example.sk', 'http://localhost:5000')
$content = $content.Replace('CHANGE_ME_POSTGRES_PASSWORD', $postgresPassword)
$content = $content.Replace('CHANGE_ME_CKAN_DB_PASSWORD', $ckanDbPassword)
$content = $content.Replace('CHANGE_ME_DATASTORE_PASSWORD', $datastorePassword)
$content = $content.Replace('CHANGE_ME_SESSION_SECRET', $sessionSecret)
$content = $content.Replace('CHANGE_ME_API_TOKEN_SECRET', $apiTokenSecret)
$content = $content.Replace('CHANGE_ME_ADMIN_PASSWORD', $adminPassword)
$content = $content.Replace('CHANGE_ME_SMTP_USER', $smtpUser)
$content = $content.Replace('CHANGE_ME_SMTP_PASSWORD', $smtpPassword)
Set-Content -Path $envPath -Value $content -Encoding UTF8
```

Expected: PowerShell exits with code 0 and `ckan-docker-prod/.env` exists.

- [ ] **Step 2: Verify `.env` contains no placeholders**

Run:

```powershell
Select-String -Path .\ckan-docker-prod\.env -Pattern "CHANGE_ME|CHANGE-ME"
```

Expected: command prints no matches.

- [ ] **Step 3: Verify localhost URLs and database URL password propagation**

Run:

```powershell
$envLines = Get-Content .\ckan-docker-prod\.env
$values = @{}
foreach ($line in $envLines) {
  if ($line -match '^\s*#' -or $line -notmatch '=') { continue }
  $key, $value = $line.Split('=', 2)
  $values[$key] = $value
}
($values['CKAN_SITE_URL'] -eq 'http://localhost:5000')
($values['CKAN__SITE_URL'] -eq 'http://localhost:5000')
($values['CKAN_SQLALCHEMY_URL'] -like "*$($values['CKAN_DB_PASSWORD'])*")
($values['CKAN_DATASTORE_WRITE_URL'] -like "*$($values['CKAN_DB_PASSWORD'])*")
($values['CKAN_DATASTORE_READ_URL'] -like "*$($values['DATASTORE_READONLY_PASSWORD'])*")
```

Expected output:

```text
True
True
True
True
True
```

- [ ] **Step 4: Verify `.env` is ignored by Git**

Run:

```bash
git check-ignore -v ckan-docker-prod/.env
git status --short -- ckan-docker-prod/.env
```

Expected: first command reports `.gitignore`; second command prints no status line for `ckan-docker-prod/.env`.

---

### Task 3: Validate Compose With The Generated Environment

**Files:**
- Verify: `ckan-docker-prod/.env`
- Verify: `ckan-docker-prod/docker-compose.yml`
- Verify: `ckan-docker-prod/docker-compose.proxy.yml`

- [ ] **Step 1: Render base compose with generated `.env`**

Run:

```powershell
docker compose --env-file .\ckan-docker-prod\.env -f .\ckan-docker-prod\docker-compose.yml config
```

Expected: command exits with code 0 and rendered YAML includes services `ckan`, `db`, `solr`, `redis`, and `datapusher`.

- [ ] **Step 2: Render proxy compose with generated `.env`**

Run:

```powershell
docker compose --env-file .\ckan-docker-prod\.env -f .\ckan-docker-prod\docker-compose.yml -f .\ckan-docker-prod\docker-compose.proxy.yml config
```

Expected: command exits with code 0 and rendered YAML includes external network `reverse-proxy`.

- [ ] **Step 3: Confirm final Git status does not expose `.env`**

Run:

```bash
git status --short
git status --short -- ckan-docker-prod/.env
```

Expected: existing unrelated root changes may remain, but there is no line for `ckan-docker-prod/.env`.

