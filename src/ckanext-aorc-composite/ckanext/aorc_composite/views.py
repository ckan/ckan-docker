from flask import Blueprint


aorc_composite = Blueprint(
    "aorc_composite", __name__)


def page():
    return "Hello, aorc_composite!"


aorc_composite.add_url_rule(
    "/aorc_composite/page", view_func=page)


def get_blueprints():
    return [aorc_composite]
