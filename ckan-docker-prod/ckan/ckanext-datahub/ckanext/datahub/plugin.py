import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class DataHubBrandingPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    def update_config(self, config):
        toolkit.add_template_directory(config, "templates")
