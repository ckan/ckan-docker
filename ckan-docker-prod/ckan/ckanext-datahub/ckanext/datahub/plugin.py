import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from flask import Blueprint
from ckanext.dcat.interfaces import IDCATURIGenerator
from ckanext.dcat.processors import RDFSerializer


class DataHubBrandingPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(IDCATURIGenerator)

    def update_config(self, config):
        toolkit.add_template_directory(config, "templates")
        self._disable_hydra_pagination()

    def get_blueprint(self):
        blueprint = Blueprint("datahub_rdf_headers", __name__)

        @blueprint.after_app_request
        def add_utf8_charset(response):
            if response.mimetype == "text/turtle":
                response.headers["Content-Type"] = "text/turtle; charset=utf-8"
            return response

        return blueprint

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

    def _disable_hydra_pagination(self):
        if getattr(RDFSerializer, "_datahub_hydra_disabled", False):
            return

        # ckanext-dcat emits Hydra pagination with literal URLs; LKOD document harvesting does not need it.
        def skip_pagination_triples(serializer, paging_info):
            return None

        RDFSerializer._add_pagination_triples = skip_pagination_triples
        RDFSerializer._datahub_hydra_disabled = True
