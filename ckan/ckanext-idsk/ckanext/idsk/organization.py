import ckan.plugins.toolkit as toolkit


DEFAULT_ORG_NAME = "minedu"
DEFAULT_ORG_TITLE = "Ministerstvo školstva"
DEFAULT_ORG_DESCRIPTION = "Predvolený poskytovateľ otvorených dát pre tento portál."
DEFAULT_CONTEXT_USER = "ckan_admin"


def default_organization_payload(config):
    return {
        "name": config.get("ckanext.idsk.default_organization", DEFAULT_ORG_NAME),
        "title": config.get("ckanext.idsk.default_organization_title", DEFAULT_ORG_TITLE),
        "description": config.get(
            "ckanext.idsk.default_organization_description",
            DEFAULT_ORG_DESCRIPTION,
        ),
        "state": "active",
    }


def default_action_context():
    return {"user": DEFAULT_CONTEXT_USER}


def ensure_default_organization(context=None, config=None):
    context = context or default_action_context()
    config = config or toolkit.config
    payload = default_organization_payload(config)

    try:
        return toolkit.get_action("organization_show")(context, {"id": payload["name"]})
    except toolkit.ObjectNotFound:
        return toolkit.get_action("organization_create")(context, payload)
