import ckan.plugins.toolkit as tk


def auscope_theme_required(value):
    if not value or value is tk.missing:
        raise tk.Invalid(tk._("Required"))
    return value


def get_validators():
    return {
        "auscope_theme_required": auscope_theme_required,
    }
