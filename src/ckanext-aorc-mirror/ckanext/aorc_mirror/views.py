from flask import Blueprint


aorc_mirror = Blueprint(
    "aorc_mirror", __name__)


def page():
    return "Hello, aorc_mirror!"


aorc_mirror.add_url_rule(
    "/aorc_mirror/page", view_func=page)


def get_blueprints():
    return [aorc_mirror]
