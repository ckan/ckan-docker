import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.obis_theme.helpers import dataset_type_class


class ObisThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "obis_theme")

    def get_helpers(self):
        return {
            'dataset_type_class': dataset_type_class
        }

    
