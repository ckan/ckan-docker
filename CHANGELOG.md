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


## [v1.1.1] - 2024-03-01

### Added
- chore: #15 add REUSE headers by @brunopacheco1 in #44
- feat(harvester): Configure automatic CRON job for CKAN Harvester #25 by @hcvdwerf in #45

### Fixed
- fix: Re-add ckanext scheming  extension from Civity to solved harvester issues
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
