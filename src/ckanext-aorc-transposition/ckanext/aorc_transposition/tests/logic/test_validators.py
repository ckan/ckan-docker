"""Tests for validators.py."""

import pytest

import ckan.plugins.toolkit as tk

from ckanext.aorc_transposition.logic import validators


def test_aorc_transposition_reauired_with_valid_value():
    assert validators.aorc_transposition_required("value") == "value"


def test_aorc_transposition_reauired_with_invalid_value():
    with pytest.raises(tk.Invalid):
        validators.aorc_transposition_required(None)
