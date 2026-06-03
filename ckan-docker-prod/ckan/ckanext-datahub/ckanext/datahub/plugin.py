import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.dcat.interfaces import IDCATURIGenerator


class DataHubBrandingPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(IDCATURIGenerator)

    def update_config(self, config):
        toolkit.add_template_directory(config, "templates")

    def catalog_uri(self, default_uri):
        return default_uri

    def dataset_uri(self, dataset_dict, default_uri):
        name = dataset_dict.get("name")
        if not name:
            return default_uri

        return f"{self._site_url(default_uri)}/dataset/{name}.ttl"

    def resource_uri(self, resource_dict, default_uri):
        return default_uri

    def publisher_uri(self, dataset_dict, default_uri):
        return default_uri

    def _site_url(self, default_uri):
        site_url = (
            toolkit.config.get("ckan.site_url")
            or toolkit.config.get("ckanext.dcat.base_uri")
        )

        if not site_url and "/dataset/" in default_uri:
            site_url = default_uri.rsplit("/dataset/", 1)[0]

        return (site_url or default_uri).rstrip("/")
