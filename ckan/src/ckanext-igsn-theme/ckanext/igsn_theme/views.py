from flask import Blueprint


igsn_theme = Blueprint(
    "igsn_theme", __name__)


def page():
    return "Hello, igsn_theme!"


igsn_theme.add_url_rule(
    "/igsn_theme/page", view_func=page)


def get_blueprints():
    return [igsn_theme]
