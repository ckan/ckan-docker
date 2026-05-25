from ckanext.idsk.organization import (
    DEFAULT_CONTEXT_USER,
    default_action_context,
    default_organization_payload,
)


def test_default_organization_payload_uses_config_values():
    config = {
        "ckanext.idsk.default_organization": "minedu",
        "ckanext.idsk.default_organization_title": "Ministerstvo školstva",
        "ckanext.idsk.default_organization_description": "Open data provider",
    }

    payload = default_organization_payload(config)

    assert payload == {
        "name": "minedu",
        "title": "Ministerstvo školstva",
        "description": "Open data provider",
        "state": "active",
    }


def test_default_organization_payload_uses_stable_defaults():
    payload = default_organization_payload({})

    assert payload["name"] == "minedu"
    assert payload["title"] == "Ministerstvo školstva"
    assert payload["state"] == "active"


def test_default_action_context_uses_sysadmin_user():
    context = default_action_context()

    assert context == {"user": DEFAULT_CONTEXT_USER}
