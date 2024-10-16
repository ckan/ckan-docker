<!--
SPDX-FileCopyrightText: 2024 PNED G.I.E.

SPDX-License-Identifier: CC-BY-4.0
-->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [v1.3.3] - 2024-10-16

### Fixed
* fix(language): Set fallback language to English when Dutch for example is not available

## [v1.3.2] - 2024-10-14

### Changed
* docs: clean up Keycloak section from README by @hcvdwerf in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/141

## [v1.3.1] - 2024-10-11

### Added
* feat(language): add Dutch facet translations to translations table by @Markus92 in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/129

### Changed
* chore(deps): update aquasecurity/trivy-action action to v0.26.0 by @LNDS-Sysadmins in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/128
* chore(deps): update redis docker tag to v7 by @LNDS-Sysadmins in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/134
* chore(deps): update aquasecurity/trivy-action action to v0.27.0 by @LNDS-Sysadmins in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/140

### Fixed
* fix: bugfix on harvesters by @brunopacheco1 in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/131
* fix: reduce cron job for harvesting to every 15min by @brunopacheco1 in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/139

## [v1.3.0] - 2024-10-07

## Changed
* chore(deps): update ckan/ckan-base docker tag to v2.10.5 by @LNDS-Sysadmins in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/115
* chore(deps): update ckan/ckan-dev docker tag to v2.10.5 by @LNDS-Sysadmins in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/116
* feat(scheming): set up GDI presets (for datetime scheming) by @Markus92 in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/119
* chore(deps): update postgres docker tag to v17 by @LNDS-Sysadmins in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/124
* feat: Upgrade to DCAT AP 3 by @hcvdwerf in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/125
* chore(deps): update aquasecurity/trivy-action action to v0.25.0 by @LNDS-Sysadmins in https://
github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/127

### Removed
* feat(auth): remove Keycloak integration from CKAN and user portal by @hcvdwerf in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/121


### Fixed
* fix: user permissions error causes oidc plugin to error by @Markus92 in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/114

### Security
* chore(deps): remove vulnerable packages by @brunopacheco1 in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/126

## [v1.2.2] - 2024-05-12

### Added
* Vulnscan by @sehaartuc in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/76
* feat: renovate integration by @sehaartuc in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/77

### Changed
* chore(deps): update fsfe/reuse-action action to v4 - autoclosed by @LNDS-Sysadmins in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/83
* chore(deps): update docker/build-push-action action to v6 by @LNDS-Sysadmins in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/82
* chore(deps): update docker/login-action digest to 0d4c9c5 by @LNDS-Sysadmins in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/79
* chore(deps): update docker/metadata-action digest to a64d048 by @LNDS-Sysadmins in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/80
* chore(deps): update oss-review-toolkit/ort-ci-github-action digest to 81698a9 by @LNDS-Sysadmins in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/81
* chore(deps): update postgres docker tag to v16 by @LNDS-Sysadmins in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/84
* chore(deps): update azure/webapps-deploy digest to 5c1d76e by @LNDS-Sysadmins in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/78
* chore: setup default user permissions by @brunopacheco1 in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/109
* chore: change from Catalogues to Organizations by @nolliia in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/110
* chore: merge RUN commands by @brunopacheco1 in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/111
* Update fairdatapoint extension  by @hcvdwerf in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/113

### Fixed
* fix: Set compatibility_mode to false to map correctly publisher close… by @hcvdwerf in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/74

## [v1.2.1] - 2024-06-12

### Changed

- chore: change versions of fairdatapoint harvester and gdi extensions by @a-nayden in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/66
- chore: update vocabulary by @a-nayden in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/68
- chore: update fairdatapoint by @hcvdwerf in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/69

### Fixed

- fix(cron): Run harvester cron job in background (run and clean up log… by @hcvdwerf in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/71
- fix(csv): resolve "extra data after last expected column" error by @hcvdwerf in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/70

## [v1.2.0] - 2024-05-19

### Changed

chore: change versions of fairdatapoint harvester and gdi extensions

## [v1.1.3] - 2024-05-19

### Fixed

- fix: fix harvester issues

## [v1.1.2] - 2024-05-12

### Changed

- chore: preload CKAN term translation by @brunopacheco1 in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/56
- chore: remove keycloak from localhost by @brunopacheco1 in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/58
- chore(deps): bump 2.10 version to 2.10.4 by @hcvdwerf in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/57
- chore: update gdi-userportal reference by @a-nayden in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/60
- chore: add more labels by @brunopacheco1 in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/62

### Fixed

- fix(azure-deployment): Trigger repull on new CKAN version by updating… by @hcvdwerf in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/52
- fix: point to fairdatapoint extension tag by @a-nayden in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/54
- fix: #51 bug report by @hcvdwerf in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/55
- fix: set up profiles to fix parsing from file bug by @a-nayden in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/59
- fix: update gdi-userportal reference by @a-nayden in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/61
- enable multilingual plugins; pre-populate ckan db with labels by @a-nayden in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/53
- fix: update fairdatapoint harvester reference by @a-nayden in https://github.com/GenomicDataInfrastructure/gdi-userportal-ckan-docker/pull/63

## [v1.1.1] - 2024-03-01

### Added

- chore: #15 add REUSE headers by @brunopacheco1 in #44
- feat(harvester): Configure automatic CRON job for CKAN Harvester #25 by @hcvdwerf in #45

### Fixed

- fix: Re-add ckanext scheming extension from Civity to solved harvester issues
- fix(theme-fetcher): handle empty iterable in theme reduction process #36 by @hcvdwerf in #48

## [v1.0.0] - 2024-01-30

### Added

- ckanext-scheming v3.0.0.
- ckanext-dcat v1.5.1.
- ckanext-harvest v1.5.6.
- ckanext-gdi-userportal v1.0.0.
- ckanext-oidc-pkce v0.3.1.
- minimal default scheming for GDI User Portal.

### Removed

- Unused datastore dependencies.

### Fixed

- Replaced all non-GDI extension locations by their original ones.
