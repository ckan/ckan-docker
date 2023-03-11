# coding=utf-8
import ckan.plugins as plugins
# import ckan.plugins.toolkit as toolkit


class NaditPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        pass



