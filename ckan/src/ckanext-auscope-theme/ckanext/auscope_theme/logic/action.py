import ckan.plugins.toolkit as tk
import ckanext.auscope_theme.logic.schema as schema


@tk.side_effect_free
def auscope_theme_get_sum(context, data_dict):
    tk.check_access(
        "auscope_theme_get_sum", context, data_dict)
    data, errors = tk.navl_validate(
        data_dict, schema.auscope_theme_get_sum(), context)

    if errors:
        raise tk.ValidationError(errors)

    return {
        "left": data["left"],
        "right": data["right"],
        "sum": data["left"] + data["right"]
    }


def get_actions():
    return {
        'auscope_theme_get_sum': auscope_theme_get_sum,
    }
