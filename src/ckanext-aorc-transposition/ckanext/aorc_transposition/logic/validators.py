import ckan.plugins.toolkit as tk


def aorc_transposition_required(value):
    if not value or value is tk.missing:
        raise tk.Invalid(tk._("Required"))
    return value


def get_validators():
    return {
        "aorc_transposition_required": aorc_transposition_required,
    }
