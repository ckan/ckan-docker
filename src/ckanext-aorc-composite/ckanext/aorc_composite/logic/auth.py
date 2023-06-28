import ckan.plugins.toolkit as tk


@tk.auth_allow_anonymous_access
def aorc_composite_get_sum(context, data_dict):
    return {"success": True}


def get_auth_functions():
    return {
        "aorc_composite_get_sum": aorc_composite_get_sum,
    }
