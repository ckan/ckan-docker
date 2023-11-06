"""Tests for validators.py."""

import pytest

import ckan.plugins.toolkit as tk

from ckanext.igsn_theme.logic import validators


def test_igsn_theme_reauired_with_valid_value():
    assert validators.igsn_theme_required("value") == "value"


def test_igsn_theme_reauired_with_invalid_value():
    with pytest.raises(tk.Invalid):
        validators.igsn_theme_required(None)
