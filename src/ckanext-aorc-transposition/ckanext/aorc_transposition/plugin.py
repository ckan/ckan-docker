from __future__ import annotations

from json import loads
import os
from re import compile, search
import sys
from typing import Any

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.config.middleware import CKANConfig
from ckan.types import Schema
from flask import make_response
from flask.blueprints import Blueprint
from rdflib import DCAT, DCTERMS, FOAF, PROV, RDF, RDFS, XSD, BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection

sys.path.append("/srv/app/src_extensions")

from utils.aorc_handler import AORCDatasetClass, AORCHandler


class TranspositionHandler(AORCHandler):
    def __init__(
        self,
        class_name: AORCDatasetClass = AORCDatasetClass.TRANSPOSITION,
        new_template: str = "",
        read_template: str = "package/transposition_read.html",
        edit_template: str = "package/transposition_edit.html",
        resource_form_template: str = "package/snippets/transposition_resource_form.html",
    ) -> None:
        super().__init__(class_name, new_template, read_template, edit_template, resource_form_template)
        self._validate_class()
        self.fields_simple = [
            *self.common_fields_simple,
            "transposition_region_name",
            "transposition_region_wkt",
            "watershed_region_name",
            "watershed_region_wkt",
            "max_precipitation_point_wkt",
            "image",
            "cell_count",
            "mean_precipitation",
            "max_precipitation",
            "min_precipitation",
            "sum_precipitation",
        ]
        self.fields_dt = [*self.common_fields_dt, *self.time_period_fields_dt]
        self.fields_list = self.common_fields_list
        self.fields_json = ["composite_normalized_datasets"]
        self.ignore_missing_fields = ["normalized_mean_precipitation", "max_precipitation_point_name"]
        self.additional_resource_fields = self.additional_resource_common_fields

    def _validate_class(self):
        if self.class_name != AORCDatasetClass.TRANSPOSITION:
            raise ValueError(f"Handler created for incorrect AORC class: {self.class_name}")

    def validate_name(self, dataset_type: str):
        clean_dataset = dataset_type.replace("_", ":")
        if clean_dataset != self.class_name.value:
            raise ValueError(f"Handler used for dataset with class {dataset_type}, not {self.class_name.value}")


class AorcTranspositionPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    AORC = Namespace("https://raw.githubusercontent.com/Dewberry/blobfish/v0.9/semantics/rdf/aorc.ttl")
    SCHEMA = Namespace("https://schema.org")
    LOCN = Namespace("http://www.w3.org/ns/locn#")
    GEO = Namespace("http://www.opengis.net/ont/geosparql#")

    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.handler = TranspositionHandler()
        self.base_url = os.environ["CKAN_SITE_URL"]
        self.catalog_fn = "catalog.ttl"
        self.catalog_endpoint = f"{self.base_url}/aorc_TranspositionDataset/{self.catalog_fn}"

    @staticmethod
    def _create_image_rights_statement(image_uri: str) -> Literal | None:
        pattern = compile(r"^s3:\/\/")
        if search(pattern, image_uri):
            return Literal(
                "This image is a resource held within an s3 bucket. In order to access the image, you must have read access to the parent s3 bucket.",
                datatype=XSD.string,
            )
        return

    def _bind_to_namespaces(self, g: Graph) -> None:
        g.bind("aorc", self.AORC)
        g.bind("schema", self.SCHEMA, replace=True)
        g.bind("geo", self.GEO)
        g.bind("locn", self.LOCN)
        g.bind("dct", DCTERMS)
        g.bind("dcat", DCAT)
        g.bind("foaf", FOAF)
        g.bind("prov", PROV)
        g.bind("xsd", XSD)
        g.bind("rdf", RDF)
        g.bind("rdfs", RDFS)

    def _handle_resources(self, resources: list[dict], dataset_uri: URIRef, g: Graph):
        for resource in resources:
            resource_uri = URIRef(f"{str(dataset_uri)}/resource/{resource['id']}")
            g.add((resource_uri, RDF.type, DCAT.Distribution))

            download_url_literal = Literal(resource["url"], datatype=XSD.string)
            g.add((resource_uri, DCAT.downloadURL, download_url_literal))

            access_rights_b_node = BNode()
            access_rights_literal = Literal(resource["access_rights"], datatype=XSD.string)
            g.add((access_rights_b_node, RDF.type, DCTERMS.RightsStatement))
            g.add((access_rights_b_node, RDFS.label, access_rights_literal))
            g.add((resource_uri, DCTERMS.accessRights, access_rights_b_node))

            file_format_uri = URIRef(resource["format"])
            g.add((resource_uri, DCTERMS.FileFormat, file_format_uri))

            compress_format_uri = URIRef(resource["compress_format"])
            g.add((resource_uri, DCAT.compressFormat, compress_format_uri))

    def _parse_composite_datasets(self, g: Graph, transposition_dataset_uri: URIRef, composite_datasets_str: str):
        composite_datasets_dict = loads(composite_datasets_str)
        for composite_dataset_url, normalization_data_download_url in composite_datasets_dict.items():
            composite_dataset_uri = URIRef(composite_dataset_url)
            g.add((composite_dataset_uri, RDF.type, self.AORC.CompositeDataset))
            g.add((transposition_dataset_uri, DCTERMS.source, composite_dataset_uri))
            if normalization_data_download_url:
                normalization_dataset_b_node = BNode()
                normalization_data_download_url_literal = Literal(normalization_data_download_url, datatype=XSD.anyURI)
                g.add((normalization_dataset_b_node, RDF.type, DCAT.Dataset))
                g.add((normalization_dataset_b_node, DCAT.downloadURL, normalization_data_download_url_literal))
                g.add((composite_dataset_uri, self.AORC.normalizedBy, normalization_dataset_b_node))

    def _parse_transposition_dataset(self, g: Graph, dataset: dict) -> URIRef:
        transposition_dataset_uri = URIRef(f"{self.base_url}/aorc_TranspositionDataset/{dataset['url']}")
        g.add((transposition_dataset_uri, RDF.type, self.AORC.TranspositionDataset))

        docker_process_b_node = BNode()
        g.add((docker_process_b_node, RDF.type, self.AORC.DockerProcess))
        g.add((transposition_dataset_uri, PROV.wasGeneratedBy, docker_process_b_node))

        if dataset.get("docker_file"):
            docker_container_node = URIRef(dataset["docker_file"])
        else:
            docker_container_node = BNode()
        g.add((docker_container_node, RDF.type, self.AORC.DockerContainer))
        g.add((docker_process_b_node, PROV.used, docker_container_node))

        command_list = dataset["command_list"].split(" ")
        command_list_b_node = BNode()
        command_list_collection = Collection(g, command_list_b_node)
        for command in command_list:
            command_literal = Literal(command, datatype=XSD.string)
            command_list_collection.append(command_literal)
        g.add((docker_process_b_node, PROV.wasStartedBy, command_list_b_node))

        self._parse_composite_datasets(g, transposition_dataset_uri, dataset["composite_normalized_datasets"])

        docker_compose_uri = URIRef(dataset["compose_file"])
        g.add((docker_compose_uri, RDF.type, self.AORC.DockerCompose))
        g.add((docker_container_node, PROV.wasStartedBy, docker_compose_uri))

        commit_hash_literal = Literal(dataset["commit_hash"], datatype=XSD.string)
        github_url = Literal(dataset["git_repo"], datatype=XSD.string)
        g.add((docker_compose_uri, self.SCHEMA.sha256, commit_hash_literal))
        g.add((docker_compose_uri, self.SCHEMA.codeRepository, github_url))

        docker_image_uri = URIRef(dataset["docker_image"])
        g.add((docker_image_uri, RDF.type, self.AORC.DockerImage))
        g.add((docker_compose_uri, DCTERMS.source, docker_image_uri))

        digest_hash_literal = Literal(dataset["digest_hash"], datatype=XSD.string)
        docker_hub_url = Literal(dataset["docker_repo"], datatype=XSD.string)
        g.add((docker_image_uri, self.SCHEMA.sha256, digest_hash_literal))
        g.add((docker_image_uri, self.SCHEMA.codeRepository, docker_hub_url))

        watershed_b_node = BNode()
        watershed_name_literal = Literal(dataset["watershed_region_name"])
        g.add((watershed_b_node, RDF.type, DCTERMS.Location))
        g.add((watershed_b_node, self.LOCN.geographicName, watershed_name_literal))
        g.add((transposition_dataset_uri, self.AORC.watershedRegion, watershed_b_node))

        watershed_geom_b_node = BNode()
        watershed_geom_wkt_literal = Literal(dataset["watershed_region_wkt"], datatype=self.GEO.wktLiteral)
        g.add((watershed_geom_b_node, RDF.type, self.LOCN.Geometry))
        g.add((watershed_geom_b_node, self.GEO.asWKT, watershed_geom_wkt_literal))
        g.add((watershed_b_node, self.LOCN.geometry, watershed_geom_b_node))

        transposition_b_node = BNode()
        transposition_name_literal = Literal(dataset["transposition_region_name"])
        g.add((transposition_b_node, RDF.type, DCTERMS.Location))
        g.add((transposition_b_node, self.LOCN.geographicName, transposition_name_literal))
        g.add((transposition_dataset_uri, self.AORC.transpositionRegion, transposition_b_node))

        transposition_geom_b_node = BNode()
        transposition_geom_wkt_literal = Literal(dataset["transposition_region_wkt"], datatype=self.GEO.wktLiteral)
        g.add((transposition_geom_b_node, RDF.type, self.LOCN.Geometry))
        g.add((transposition_geom_b_node, self.GEO.asWKT, transposition_geom_wkt_literal))
        g.add((transposition_b_node, self.LOCN.geometry, transposition_geom_b_node))

        max_precip_b_node = BNode()
        g.add((max_precip_b_node, RDF.type, DCTERMS.Location))
        g.add((transposition_dataset_uri, self.AORC.maxPrecipitationPoint, max_precip_b_node))

        if dataset.get("max_precipitation_point_name"):
            max_precip_name_literal = Literal(dataset["max_precipitation_point_name"])
            g.add((transposition_b_node, self.LOCN.geographicName, max_precip_name_literal))

        max_precip_geom_b_node = BNode()
        max_precip_geom_wkt_literal = Literal(dataset["max_precipitation_point_wkt"], datatype=self.GEO.wktLiteral)
        g.add((max_precip_geom_b_node, RDF.type, self.LOCN.Geometry))
        g.add((max_precip_geom_b_node, self.GEO.asWKT, max_precip_geom_wkt_literal))
        g.add((max_precip_b_node, self.LOCN.geometry, max_precip_geom_b_node))

        period_of_time_b_node = BNode()
        start_literal = Literal(dataset["start_time"], datatype=XSD.dateTime)
        end_literal = Literal(dataset["end_time"], datatype=XSD.dateTime)
        g.add((period_of_time_b_node, RDF.type, DCTERMS.PeriodOfTime))
        g.add((period_of_time_b_node, DCAT.startDate, start_literal))
        g.add((period_of_time_b_node, DCAT.endDate, end_literal))
        g.add((transposition_dataset_uri, DCTERMS.temporal, period_of_time_b_node))

        image_uri = URIRef(dataset["image"])
        g.add((image_uri, RDF.type, FOAF.Image))
        g.add((transposition_dataset_uri, FOAF.depiction, image_uri))

        access_rights_literal = self._create_image_rights_statement(dataset["image"])
        if access_rights_literal:
            access_rights_b_node = BNode()
            g.add((access_rights_b_node, RDF.type, DCTERMS.RightsStatement))
            g.add((access_rights_b_node, RDFS.label, access_rights_literal))
            g.add((image_uri, DCTERMS.accessRights, access_rights_b_node))

        spatial_resolution_literal = Literal(dataset["spatial_resolution"], datatype=XSD.numeric)
        g.add((transposition_dataset_uri, DCAT.spatialResolutionInMeters, spatial_resolution_literal))

        last_modification = Literal(dataset["last_modified"], datatype=XSD.dateTime)
        g.add((transposition_dataset_uri, DCTERMS.modified, last_modification))

        cell_count_literal = Literal(dataset["cell_count"], datatype=XSD.integer)
        g.add((transposition_dataset_uri, self.AORC.cellCount, cell_count_literal))

        mean_precipitation_literal = Literal(dataset["mean_precipitation"], datatype=XSD.float)
        g.add((transposition_dataset_uri, self.AORC.meanPrecipitation, mean_precipitation_literal))

        max_precipitation_literal = Literal(dataset["max_precipitation"], datatype=XSD.float)
        g.add((transposition_dataset_uri, self.AORC.maxPrecipitation, max_precipitation_literal))

        min_precipitation_literal = Literal(dataset["min_precipitation"], datatype=XSD.float)
        g.add((transposition_dataset_uri, self.AORC.minPrecipitation, min_precipitation_literal))

        sum_precipitation_literal = Literal(dataset["sum_precipitation"], datatype=XSD.float)
        g.add((transposition_dataset_uri, self.AORC.sumPrecipitation, sum_precipitation_literal))

        if dataset.get("normalized_mean_precipitation"):
            normalized_mean_precipitation_literal = Literal(
                dataset["normalized_mean_precipitation"], datatype=XSD.float
            )
            g.add(
                (
                    transposition_dataset_uri,
                    self.AORC.normalizedMeanPrecipitation,
                    normalized_mean_precipitation_literal,
                )
            )

        return transposition_dataset_uri

    def _handle_ckan_transposition_data(self, results: dict[str, list[dict]]) -> Graph:
        g = Graph()
        self._bind_to_namespaces(g)

        catalog_uri = URIRef(self.catalog_endpoint)
        g.add((catalog_uri, RDF.type, DCAT.Catalog))

        for dataset in results.get("results", []):
            mirror_dataset_uri = self._parse_transposition_dataset(g, dataset)
            g.add((catalog_uri, DCAT.dataset, mirror_dataset_uri))
        return g

    def update_config(self, config_: CKANConfig):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "aorc_transposition")

    def create_package_schema(self):
        schema: Schema = super(AorcTranspositionPlugin, self).create_package_schema()
        return self.handler.modify_schema(schema)

    def update_package_schema(self):
        schema: Schema = super(AorcTranspositionPlugin, self).update_package_schema()
        return self.handler.modify_schema(schema)

    def show_package_schema(self) -> Schema:
        schema: Schema = super(AorcTranspositionPlugin, self).show_package_schema()
        return self.handler.show_schema(schema)

    def is_fallback(self) -> bool:
        return False

    def package_types(self) -> list[str]:
        return ["aorc_TranspositionDataset"]

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
            data_dict={"fq": "type:aorc_TranspositionDataset", "rows": 1000}  # Adjust the number of rows as needed
        )
        catalog_ttl = self._handle_ckan_transposition_data(result).serialize(format="ttl")
        # Change to flask.Response class to manually set content type / mime type
        resp = make_response(catalog_ttl, {"Content-Type": "text/plain; charset=utf-8"})
        return resp

    def view_dataset_ttl(self, package_type: str, _id: str):
        self.handler.validate_name(package_type)
        result = toolkit.get_action("package_show")(data_dict={"id": _id})
        g = Graph()
        self._bind_to_namespaces(g)
        self._parse_transposition_dataset(g, result)
        dataset_ttl = g.serialize(format="ttl")
        resp = make_response(dataset_ttl, {"Content-Type": "text/plain; charset=utf-8"})
        return resp
