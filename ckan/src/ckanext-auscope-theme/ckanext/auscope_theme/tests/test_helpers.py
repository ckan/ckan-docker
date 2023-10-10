"""Tests for helpers.py."""

import ckanext.auscope_theme.helpers as helpers


def test_auscope_theme_hello():
    assert helpers.auscope_theme_hello() == "Hello, auscope_theme!"
