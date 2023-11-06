"""Tests for views.py."""

import pytest

import ckanext.igsn_theme.validators as validators


import ckan.plugins.toolkit as tk


@pytest.mark.ckan_config("ckan.plugins", "igsn_theme")
@pytest.mark.usefixtures("with_plugins")
def test_igsn_theme_blueprint(app, reset_db):
    resp = app.get(tk.h.url_for("igsn_theme.page"))
    assert resp.status_code == 200
    assert resp.body == "Hello, igsn_theme!"
