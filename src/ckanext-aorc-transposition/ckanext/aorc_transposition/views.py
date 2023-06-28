from flask import Blueprint


aorc_transposition = Blueprint(
    "aorc_transposition", __name__)


def page():
    return "Hello, aorc_transposition!"


aorc_transposition.add_url_rule(
    "/aorc_transposition/page", view_func=page)


def get_blueprints():
    return [aorc_transposition]
