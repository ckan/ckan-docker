"""Tests for validators.py."""

import pytest

import ckan.plugins.toolkit as tk

from ckanext.aorc_mirror.logic import validators


def test_aorc_mirror_reauired_with_valid_value():
    assert validators.aorc_mirror_required("value") == "value"


def test_aorc_mirror_reauired_with_invalid_value():
    with pytest.raises(tk.Invalid):
        validators.aorc_mirror_required(None)
