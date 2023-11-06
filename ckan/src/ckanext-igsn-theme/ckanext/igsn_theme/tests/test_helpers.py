"""Tests for helpers.py."""

import ckanext.igsn_theme.helpers as helpers


def test_igsn_theme_hello():
    assert helpers.igsn_theme_hello() == "Hello, igsn_theme!"
