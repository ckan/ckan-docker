from __future__ import annotations

import os
import sys
from typing import Any

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.config.middleware import CKANConfig
from ckan.types import Schema
from flask import make_response
from flask.blueprints import Blueprint
from rdflib import DCAT, DCTERMS, PROV, RDF, RDFS, XSD, BNode, Graph, Literal, URIRef
from rdflib.collection import Collection

sys.path.append("/srv/app/src_extensions")

from utils import AORCDatasetClass, AORCHandler, AORC
from utils.constants import GEO, LOCN, SCHEMA


class CompositeHandler(AORCHandler):
    def __init__(
        self,
        class_name: AORCDatasetClass = AORCDatasetClass.COMPOSITE,
        new_template: str = "",
        read_template: str = "package/composite_read.html",
        edit_template: str = "package/composite_edit.html",
        resource_form_template: str = "package/snippets/composite_resource_form.html",
    ) -> None:
        super().__init__(class_name, new_template, read_template, edit_template, resource_form_template)
        self._validate_class()
        self.fields_simple = [*self.common_fields_simple, *self.location_fields_simple]
        self.fields_dt = [*self.common_fields_dt, *self.time_period_fields_dt]
        self.fields_list = [*self.common_fields_list, "mirror_datasets"]
        self.additional_resource_fields = self.additional_resource_common_fields

    def _validate_class(self):
        if self.class_name != AORCDatasetClass.COMPOSITE:
            raise ValueError(f"Handler created for incorrect AORC class: {self.class_name}")

    def validate_name(self, dataset_type: str):
        clean_dataset = dataset_type.replace("_", ":")
        if clean_dataset != self.class_name.value:
            raise ValueError(f"Handler used for dataset with class {dataset_type}, not {self.class_name.value}")


class AorcCompositePlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.handler = CompositeHandler()
        self.base_url = os.environ["CKAN_SITE_URL"]
        self.catalog_fn = "catalog.ttl"
        self.catalog_endpoint = f"{self.base_url}/aorc_CompositeDataset/{self.catalog_fn}"

    def _bind_to_namespaces(self, g: Graph) -> None:
        g.bind("aorc", AORC)
        g.bind("schema", SCHEMA, replace=True)
        g.bind("geo", GEO)
        g.bind("locn", LOCN)
        g.bind("dct", DCTERMS)
        g.bind("dcat", DCAT)
        g.bind("prov", PROV)
        g.bind("xsd", XSD)
        g.bind("rdf", RDF)
        g.bind("rdfs", RDFS)

    def _parse_composite_dataset(self, g: Graph, dataset: dict) -> URIRef:
        composite_dataset_uri = URIRef(f"{self.base_url}/aorc_CompositeDataset/{dataset['url']}")
        g.add((composite_dataset_uri, RDF.type, AORC.CompositeDataset))

        docker_process_b_node = BNode()
        g.add((docker_process_b_node, RDF.type, AORC.DockerProcess))
        g.add((composite_dataset_uri, PROV.wasGeneratedBy, docker_process_b_node))

        if dataset.get("docker_file"):
            docker_container_node = URIRef(dataset["docker_file"])
        else:
            docker_container_node = BNode()
        g.add((docker_container_node, RDF.type, AORC.DockerContainer))
        g.add((docker_process_b_node, PROV.used, docker_container_node))

        command_list = dataset["command_list"].split(" ")
        command_list_b_node = BNode()
        command_list_collection = Collection(g, command_list_b_node)
        for command in command_list:
            command_literal = Literal(command, datatype=XSD.string)
            command_list_collection.append(command_literal)
        g.add((docker_process_b_node, PROV.wasStartedBy, command_list_b_node))

        mirror_dataset_url_list = dataset["mirror_datasets"].split(" ")
        for mirror_dataset_url in mirror_dataset_url_list:
            mirror_dataset_uri = URIRef(mirror_dataset_url)
            g.add((mirror_dataset_uri, RDF.type, AORC.MirrorDataset))
            g.add((composite_dataset_uri, DCTERMS.source, mirror_dataset_uri))

        docker_compose_uri = URIRef(dataset["compose_file"])
        g.add((docker_compose_uri, RDF.type, AORC.DockerCompose))
        g.add((docker_container_node, PROV.wasStartedBy, docker_compose_uri))

        commit_hash_literal = Literal(dataset["commit_hash"], datatype=XSD.string)
        github_url = Literal(dataset["git_repo"], datatype=XSD.string)
        g.add((docker_compose_uri, SCHEMA.sha256, commit_hash_literal))
        g.add((docker_compose_uri, SCHEMA.codeRepository, github_url))

        docker_image_uri = URIRef(dataset["docker_image"])
        g.add((docker_image_uri, RDF.type, AORC.DockerImage))
        g.add((docker_compose_uri, DCTERMS.source, docker_image_uri))

        digest_hash_literal = Literal(dataset["digest_hash"], datatype=XSD.string)
        docker_hub_url = Literal(dataset["docker_repo"], datatype=XSD.string)
        g.add((docker_image_uri, SCHEMA.sha256, digest_hash_literal))
        g.add((docker_image_uri, SCHEMA.codeRepository, docker_hub_url))

        location_b_node = BNode()
        location_name_literal = Literal(dataset["location_name"], datatype=XSD.string)
        g.add((location_b_node, RDF.type, DCTERMS.Location))
        g.add((location_b_node, LOCN.geographicName, location_name_literal))
        g.add((composite_dataset_uri, DCTERMS.spatial, location_b_node))

        location_geom_b_node = BNode()
        location_geom_wkt_literal = Literal(dataset["location_wkt"], datatype=GEO.wktLiteral)
        g.add((location_geom_b_node, RDF.type, LOCN.Geometry))
        g.add((location_geom_b_node, GEO.asWKT, location_geom_wkt_literal))
        g.add((location_b_node, LOCN.geometry, location_geom_b_node))

        period_of_time_b_node = BNode()
        start_literal = Literal(dataset["start_time"], datatype=XSD.dateTime)
        end_literal = Literal(dataset["end_time"], datatype=XSD.dateTime)
        g.add((period_of_time_b_node, RDF.type, DCTERMS.PeriodOfTime))
        g.add((period_of_time_b_node, DCAT.startDate, start_literal))
        g.add((period_of_time_b_node, DCAT.endDate, end_literal))
        g.add((composite_dataset_uri, DCTERMS.temporal, period_of_time_b_node))

        spatial_resolution_literal = Literal(dataset["spatial_resolution"], datatype=XSD.numeric)
        g.add((composite_dataset_uri, DCAT.spatialResolutionInMeters, spatial_resolution_literal))

        last_modification = Literal(dataset["last_modified"], datatype=XSD.dateTime)
        g.add((composite_dataset_uri, DCTERMS.modified, last_modification))

        self.handler.handle_resources(dataset["resources"], composite_dataset_uri, g)

        return composite_dataset_uri

    def _handle_ckan_composite_data(self, results: dict[str, list[dict]]) -> Graph:
        g = Graph()
        self._bind_to_namespaces(g)

        catalog_uri = URIRef(self.catalog_endpoint)
        g.add((catalog_uri, RDF.type, DCAT.Catalog))

        for dataset in results.get("results", []):
            mirror_dataset_uri = self._parse_composite_dataset(g, dataset)
            g.add((catalog_uri, DCAT.dataset, mirror_dataset_uri))
        return g

    def update_config(self, config_: CKANConfig):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "aorc_composite")

    def create_package_schema(self):
        schema: Schema = super(AorcCompositePlugin, self).create_package_schema()
        return self.handler.modify_schema(schema)

    def update_package_schema(self):
        schema: Schema = super(AorcCompositePlugin, self).update_package_schema()
        return self.handler.modify_schema(schema)

    def show_package_schema(self) -> Schema:
        schema: Schema = super(AorcCompositePlugin, self).show_package_schema()
        return self.handler.show_schema(schema)

    def is_fallback(self) -> bool:
        return False

    def package_types(self) -> list[str]:
        return ["aorc_CompositeDataset"]

    def edit_template(self, package_type: str) -> str:
        self.handler.validate_name(package_type)
        return self.handler.edit_template

    def read_template(self, package_type: str) -> str:
        self.handler.validate_name(package_type)
        return self.handler.read_template

    def resource_form(self, package_type: str) -> str:
        self.handler.validate_name(package_type)
        return self.handler.resource_form_template

    def prepare_dataset_blueprint(self, package_type: str, blueprint: Blueprint) -> Blueprint:
        self.handler.validate_name(package_type)
        blueprint.add_url_rule(f"/{self.catalog_fn}", view_func=self.view_catalog_ttl)
        blueprint.add_url_rule(f"/<_id>.ttl", view_func=self.view_dataset_ttl)
        return blueprint

    def view_catalog_ttl(self, package_type: str):
        self.handler.validate_name(package_type)
        result = toolkit.get_action("package_search")(
            data_dict={"fq": f"type:{package_type}", "rows": 1000}  # Adjust the number of rows as needed
        )
        catalog_ttl = self._handle_ckan_composite_data(result).serialize(format="ttl")
        # Change to flask.Response class to manually set content type / mime type
        resp = make_response(catalog_ttl, {"Content-Type": "text/plain; charset=utf-8"})
        return resp

    def view_dataset_ttl(self, package_type: str, _id: str):
        self.handler.validate_name(package_type)
        result = toolkit.get_action("package_show")(data_dict={"id": _id})
        g = Graph()
        self._bind_to_namespaces(g)
        self._parse_composite_dataset(g, result)
        dataset_ttl = g.serialize(format="ttl")
        resp = make_response(dataset_ttl, {"Content-Type": "text/plain; charset=utf-8"})
        return resp
