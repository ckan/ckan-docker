"""Tests for helpers.py."""

import ckanext.aorc_composite.helpers as helpers


def test_aorc_composite_hello():
    assert helpers.aorc_composite_hello() == "Hello, aorc_composite!"
