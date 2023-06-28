import ckan.plugins.toolkit as tk
import ckanext.aorc_composite.logic.schema as schema


@tk.side_effect_free
def aorc_composite_get_sum(context, data_dict):
    tk.check_access(
        "aorc_composite_get_sum", context, data_dict)
    data, errors = tk.navl_validate(
        data_dict, schema.aorc_composite_get_sum(), context)

    if errors:
        raise tk.ValidationError(errors)

    return {
        "left": data["left"],
        "right": data["right"],
        "sum": data["left"] + data["right"]
    }


def get_actions():
    return {
        'aorc_composite_get_sum': aorc_composite_get_sum,
    }
