import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.idsk import cli


class IDSKThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IClick)

    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')

    def get_helpers(self):
        return {}

    def get_commands(self):
        return cli.get_commands()
