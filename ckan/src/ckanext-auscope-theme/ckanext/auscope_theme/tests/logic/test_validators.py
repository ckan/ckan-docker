"""Tests for validators.py."""

import pytest

import ckan.plugins.toolkit as tk

from ckanext.auscope_theme.logic import validators


def test_auscope_theme_reauired_with_valid_value():
    assert validators.auscope_theme_required("value") == "value"


def test_auscope_theme_reauired_with_invalid_value():
    with pytest.raises(tk.Invalid):
        validators.auscope_theme_required(None)
