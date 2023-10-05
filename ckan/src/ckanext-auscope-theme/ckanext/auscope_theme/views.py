from flask import Blueprint


auscope_theme = Blueprint(
    "auscope_theme", __name__)


def page():
    return "Hello, auscope_theme!"


auscope_theme.add_url_rule(
    "/auscope_theme/page", view_func=page)


def get_blueprints():
    return [auscope_theme]
