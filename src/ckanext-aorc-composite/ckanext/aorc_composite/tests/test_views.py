"""Tests for views.py."""

import pytest

import ckanext.aorc_composite.validators as validators


import ckan.plugins.toolkit as tk


@pytest.mark.ckan_config("ckan.plugins", "aorc_composite")
@pytest.mark.usefixtures("with_plugins")
def test_aorc_composite_blueprint(app, reset_db):
    resp = app.get(tk.h.url_for("aorc_composite.page"))
    assert resp.status_code == 200
    assert resp.body == "Hello, aorc_composite!"
