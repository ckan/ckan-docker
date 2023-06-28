import ckan.plugins.toolkit as tk


def aorc_composite_required(value):
    if not value or value is tk.missing:
        raise tk.Invalid(tk._("Required"))
    return value


def get_validators():
    return {
        "aorc_composite_required": aorc_composite_required,
    }
