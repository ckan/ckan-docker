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
from rdflib import DCAT, DCTERMS, ORG, PROV, RDF, RDFS, SKOS, XSD, BNode, Graph, Literal, URIRef
from rdflib.collection import Collection

sys.path.append("/srv/app/src_extensions")

from utils import AORCDatasetClass, AORCHandler, AORC
from utils.constants import GEO, LOCN, SCHEMA


class MirrorHandler(AORCHandler):
    def __init__(
        self,
        class_name: AORCDatasetClass = AORCDatasetClass.MIRROR,
        new_template: str = "package/mirror_new.html",
        read_template: str = "package/mirror_read.html",
        edit_template: str = "package/mirror_edit.html",
        resource_form_template: str = "package/snippets/mirror_resource_form.html",
    ) -> None:
        super().__init__(class_name, new_template, read_template, edit_template, resource_form_template)
        self._validate_class()
        self.fields_simple = [
            *self.common_fields_simple,
            *self.time_resolution_duration_fields_simple,
            *self.rfc_fields_simple,
            "source_dataset",
        ]
        self.fields_dt = [*self.common_fields_dt, *self.time_period_fields_dt]
        self.fields_list = self.common_fields_list
        self.additional_resource_fields = self.additional_resource_common_fields

    def _validate_class(self):
        if self.class_name != AORCDatasetClass.MIRROR:
            raise ValueError(f"Handler created for incorrect AORC class: {self.class_name}")

    def validate_name(self, dataset_type: str):
        clean_dataset = dataset_type.replace("_", ":")
        if clean_dataset != self.class_name.value:
            raise ValueError(f"Handler used for dataset with class {dataset_type}, not {self.class_name.value}")


class AorcMirrorPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        self.handler = MirrorHandler()
        self.base_url = os.environ["CKAN_SITE_URL"]
        self.catalog_fn = "catalog.ttl"
        self.catalog_endpoint = f"{self.base_url}/aorc_MirrorDataset/{self.catalog_fn}"

    def _bind_to_namespaces(self, g: Graph) -> None:
        g.bind("aorc", AORC)
        g.bind("schema", SCHEMA, replace=True)
        g.bind("geo", GEO)
        g.bind("locn", LOCN, replace=True)
        g.bind("dct", DCTERMS)
        g.bind("dcat", DCAT)
        g.bind("prov", PROV)
        g.bind("skos", SKOS)
        g.bind("org", ORG)
        g.bind("xsd", XSD)
        g.bind("rdf", RDF)
        g.bind("rdfs", RDFS)

    def _add_source_dataset(
        self, g: Graph, ttl_str: str, target_node: URIRef, rfc_alias_literal: Literal, start_date_literal: Literal
    ):
        g.parse(data=ttl_str, format="ttl")

        query = """
            SELECT ?node ?sd ?alias
            WHERE {
                ?node a aorc:SourceDataset .
                ?node dct:temporal ?t .
                ?node aorc:hasRFC ?rfc .
                ?t dcat:startDate ?sd .
                ?rfc skos:altLabel ?alias .
            }
            """
        source_results = g.query(query)
        node = None
        for row in source_results:
            bnode, start_date, alias = row
            if start_date == start_date_literal and alias == rfc_alias_literal:
                if node != None:
                    raise ValueError(
                        f"Expected only one match source dataset, found at least one more for {rfc_alias_literal} and {start_date_literal}"
                    )
                node = bnode
        g.add((target_node, DCTERMS.source, node))

    def _parse_mirror_dataset(self, g: Graph, dataset: dict) -> URIRef:
        mirror_dataset_uri = URIRef(f"{self.base_url}/aorc_MirrorDataset/{dataset['url']}")
        g.add((mirror_dataset_uri, RDF.type, AORC.MirrorDataset))

        docker_process_b_node = BNode()
        g.add((docker_process_b_node, RDF.type, AORC.DockerProcess))
        g.add((mirror_dataset_uri, PROV.wasGeneratedBy, docker_process_b_node))

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

        rfc_b_node = BNode()
        rfc_alias_literal = Literal(dataset["rfc_alias"], datatype=XSD.string)
        rfc_name_literal = Literal(dataset["rfc_full_name"], datatype=XSD.string)
        g.add((rfc_b_node, SKOS.altLabel, rfc_alias_literal))
        g.add((rfc_b_node, SKOS.prefLabel, rfc_name_literal))
        g.add((rfc_b_node, RDF.type, AORC.RFC))
        g.add((mirror_dataset_uri, AORC.hasRFC, rfc_b_node))

        rfc_geom_b_node = BNode()
        rfc_geom_wkt_literal = Literal(dataset["rfc_wkt"], datatype=GEO.wktLiteral)
        g.add((rfc_geom_b_node, RDF.type, LOCN.Geometry))
        g.add((rfc_b_node, LOCN.geometry, rfc_geom_b_node))
        g.add((rfc_geom_b_node, GEO.asWKT, rfc_geom_wkt_literal))

        rfc_org_uri = URIRef(dataset["rfc_parent_organization"])
        g.add((rfc_b_node, ORG.unitOf, rfc_org_uri))

        period_of_time_b_node = BNode()
        start_literal = Literal(dataset["start_time"], datatype=XSD.dateTime)
        end_literal = Literal(dataset["end_time"], datatype=XSD.dateTime)
        g.add((period_of_time_b_node, RDF.type, DCTERMS.PeriodOfTime))
        g.add((period_of_time_b_node, DCAT.startDate, start_literal))
        g.add((period_of_time_b_node, DCAT.endDate, end_literal))
        g.add((mirror_dataset_uri, DCTERMS.temporal, period_of_time_b_node))

        spatial_resolution_literal = Literal(dataset["spatial_resolution"], datatype=XSD.numeric)
        g.add((mirror_dataset_uri, DCAT.spatialResolutionInMeters, spatial_resolution_literal))

        last_modification = Literal(dataset["last_modified"], datatype=XSD.dateTime)
        g.add((mirror_dataset_uri, DCTERMS.modified, last_modification))

        temporal_resolution_literal = Literal(dataset["temporal_resolution"], datatype=XSD.duration)
        g.add((mirror_dataset_uri, DCAT.temporalResolution, temporal_resolution_literal))

        self._add_source_dataset(g, dataset["source_dataset"], mirror_dataset_uri, rfc_alias_literal, start_literal)

        self.handler.handle_resources(
            dataset["resources"], mirror_dataset_uri, f"{self.base_url}/aorc_MirrorDataset/{dataset['url'].lower()}", g
        )

        return mirror_dataset_uri

    def _handle_ckan_mirror_data(self, results: dict[str, list[dict]]) -> Graph:
        g = Graph()
        self._bind_to_namespaces(g)

        catalog_uri = URIRef(self.catalog_endpoint)
        g.add((catalog_uri, RDF.type, DCAT.Catalog))

        for dataset in results.get("results", []):
            mirror_dataset_uri = self._parse_mirror_dataset(g, dataset)
            g.add((catalog_uri, DCAT.dataset, mirror_dataset_uri))
        return g

    def update_config(self, config_: CKANConfig):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "aorc_mirror")

    def create_package_schema(self):
        schema: Schema = super(AorcMirrorPlugin, self).create_package_schema()
        return self.handler.modify_schema(schema)

    def update_package_schema(self):
        schema: Schema = super(AorcMirrorPlugin, self).update_package_schema()
        return self.handler.modify_schema(schema)

    def show_package_schema(self) -> Schema:
        schema: Schema = super(AorcMirrorPlugin, self).show_package_schema()
        return self.handler.show_schema(schema)

    def is_fallback(self) -> bool:
        return False

    def package_types(self) -> list[str]:
        return ["aorc_MirrorDataset"]

    def new_template(self, package_type: str) -> str:
        self.handler.validate_name(package_type)
        return self.handler.new_template

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
        blueprint.add_url_rule(f"{self.catalog_fn}", view_func=self.view_catalog_ttl)
        blueprint.add_url_rule(f"<_id>.ttl", view_func=self.view_dataset_ttl)
        return blueprint

    def view_catalog_ttl(self, package_type: str):
        self.handler.validate_name(package_type)
        result = toolkit.get_action("package_search")(
            data_dict={"fq": f"type:{package_type}", "rows": 1000}  # Adjust the number of rows as needed
        )
        catalog_ttl = self._handle_ckan_mirror_data(result).serialize(format="ttl")
        # Change to flask.Response class to manually set content type / mime type
        resp = make_response(catalog_ttl, {"Content-Type": "text/plain; charset=utf-8"})
        return resp

    def view_dataset_ttl(self, package_type: str, _id: str):
        self.handler.validate_name(package_type)
        result = toolkit.get_action("package_show")(data_dict={"id": _id})
        g = Graph()
        self._bind_to_namespaces(g)
        self._parse_mirror_dataset(g, result)
        dataset_ttl = g.serialize(format="ttl")
        resp = make_response(dataset_ttl, {"Content-Type": "text/plain; charset=utf-8"})
        return resp
