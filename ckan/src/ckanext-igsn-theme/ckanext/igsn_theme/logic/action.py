import ckan.plugins.toolkit as tk
import ckanext.igsn_theme.logic.schema as schema


@tk.side_effect_free
def igsn_theme_get_sum(context, data_dict):
    tk.check_access(
        "igsn_theme_get_sum", context, data_dict)
    data, errors = tk.navl_validate(
        data_dict, schema.igsn_theme_get_sum(), context)

    if errors:
        raise tk.ValidationError(errors)

    return {
        "left": data["left"],
        "right": data["right"],
        "sum": data["left"] + data["right"]
    }


def get_actions():
    return {
        'igsn_theme_get_sum': auscope_theme_get_sum,
    }
