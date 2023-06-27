"""Tests for helpers.py."""

import ckanext.aorc_mirror.helpers as helpers


def test_aorc_mirror_hello():
    assert helpers.aorc_mirror_hello() == "Hello, aorc_mirror!"
