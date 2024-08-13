#!/bin/bash

# SPDX-FileCopyrightText: 2024 PNED G.I.E.
#
# SPDX-License-Identifier: AGPL-3.0-only

# Update the config file with each extension config-options
echo "[ckan.auth] Setting up config-options"
ckan config-tool $CKAN_INI -s app:main \
    "ckan.auth.create_user_via_api = False"\
    "ckan.auth.create_user_via_web = False"\
    "ckan.auth.user_create_groups = False"\
    "ckan.auth.user_create_organizations = False"\
    "ckan.auth.user_delete_groups = False"\
    "ckan.auth.user_delete_organizations = False"\
    "ckan.auth.anon_create_dataset = False"\
    "ckan.auth.create_unowned_dataset = False"\
    "ckan.auth.create_dataset_if_not_in_organization = False"\
    "ckan.auth.roles_that_cascade_to_sub_groups = admin"\
    "ckan.auth.public_user_details = False"\
    "ckan.auth.public_activity_stream_detail = False"\
    "ckan.auth.allow_dataset_collaborators = False"\
    "ckan.auth.allow_admin_collaborators = False"\
    "ckan.auth.allow_collaborators_to_change_owner_org = False"\
    "ckan.auth.create_default_api_keys = False"\
    "ckan.auth.reveal_private_datasets = False"\
    "ckan.auth.enable_cookie_auth_in_api = False"\
    "ckan.auth.route_after_login = home.index"\
    "ckan.user_reset_landing_page = home.index"\
    "ckan.upload.user.types = image"\
    "ckan.upload.user.mimetypes = image/png image/jpeg"\
    "ckan.upload.group.types = image text/svg"\
    "ckan.upload.group.mimetypes = image/png text/svg image/svg+xml"
