from __future__ import annotations

import datetime
import os
from enum import Enum
import json
import re
from typing import cast

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.types import Schema
from flask import Response, make_response
from flask.blueprints import Blueprint
from psycopg2.extensions import register_adapter
from psycopg2.extras import Json
from rdflib import DCAT, DCTERMS, FOAF, ORG, PROV, RDF, RDFS, SKOS, XSD, BNode, Graph, Literal, URIRef
from rdflib.collection import Collection
from rdflib.namespace import DefinedNamespace, Namespace

# Constants
SCHEMA = Namespace("https://schema.org")
LOCN = Namespace("http://www.w3.org/ns/locn#")
GEO = Namespace("http://www.opengis.net/ont/geosparql#")


class AORC(DefinedNamespace):
    # Classes
    CommandList: URIRef
    CompositeDataset: URIRef
    DockerCompose: URIRef
    DockerContainer: URIRef
    DockerImage: URIRef
    DockerProcess: URIRef
    MirrorDataset: URIRef
    RFC: URIRef
    SourceDataset: URIRef
    TranspositionDataset: URIRef

    # Object Properties
    hasRFC: URIRef
    maxPrecipitationPoint: URIRef
    normalizedBy: URIRef
    transpositionRegion: URIRef
    watershedRegion: URIRef

    # Data Properties
    cellCount: URIRef
    maxPrecipitation: URIRef
    meanPrecipitation: URIRef
    normalizedMeanPrecipitation: URIRef
    sumPrecipitation: URIRef

    _NS = Namespace("https://raw.githubusercontent.com/Dewberry/blobfish/v0.9/semantics/rdf/aorc.ttl#")


def datetime_to_string(dt: datetime.datetime) -> str:
    return dt.isoformat()


def reformat_command_list(command_list: str) -> str:
    commands = command_list[1:-1].split(",")
    command_string = " ".join(commands)
    return command_string


class BaseHandler:
    def __init__(self) -> None:
        self.simple_fields = []
        self.datetime_fields = []
        self.list_fields = []
        self.json_fields = []
        self.additional_resource_fields = []
        self.ignore_missing_fields = []

    def _register_dict_handler(self) -> None:
        register_adapter(dict, Json)

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

    def handle_resources(self, resources: list[dict], dataset_uri: URIRef, dataset_url: str, g: Graph) -> None:
        for resource in resources:
            resource_uri = URIRef(f"{dataset_url}/resource/{resource['id']}")
            g.add((resource_uri, RDF.type, DCAT.Distribution))
            g.add((dataset_uri, DCAT.distribution, resource_uri))

            download_url_literal = Literal(resource["url"], datatype=XSD.anyURI)
            g.add((resource_uri, DCAT.downloadURL, download_url_literal))

            access_rights_b_node = BNode()
            access_rights_literal = Literal(resource["access_rights"], datatype=XSD.string)
            g.add((access_rights_b_node, RDF.type, DCTERMS.RightsStatement))
            g.add((access_rights_b_node, RDFS.label, access_rights_literal))
            g.add((resource_uri, DCTERMS.accessRights, access_rights_b_node))

            file_format_uri = URIRef(resource["format"])
            g.add((resource_uri, DCTERMS.FileFormat, file_format_uri))

    def _modify_simple_fields(self, schema: Schema) -> Schema:
        for simple_field in self.simple_fields:
            schema.update(
                {
                    simple_field: [
                        toolkit.get_validator("not_empty"),
                        toolkit.get_converter("convert_to_extras"),
                    ]
                }
            )
        return schema

    def _show_simple_fields(self, schema: Schema) -> Schema:
        for simple_field in self.simple_fields:
            schema.update(
                {
                    simple_field: [
                        toolkit.get_converter("convert_from_extras"),
                        toolkit.get_validator("not_empty"),
                    ]
                }
            )
        return schema

    def _modify_datetime_fields(self, schema: Schema) -> Schema:
        for datetime_field in self.datetime_fields:
            schema.update(
                {
                    datetime_field: [
                        toolkit.get_validator("isodate"),
                        datetime_to_string,
                        toolkit.get_converter("convert_to_extras"),
                    ]
                }
            )
        return schema

    def _show_datetime_fields(self, schema: Schema) -> Schema:
        for datetime_field in self.datetime_fields:
            schema.update(
                {
                    datetime_field: [
                        toolkit.get_converter("convert_from_extras"),
                        toolkit.get_validator("isodate"),
                        datetime_to_string,
                    ]
                }
            )
        return schema

    def _modify_list_fields(self, schema: Schema) -> Schema:
        for list_field in self.list_fields:
            schema.update(
                {
                    list_field: [
                        toolkit.get_validator("not_empty"),
                        toolkit.get_converter("as_list"),
                        toolkit.get_converter("convert_to_extras"),
                    ]
                }
            )
        return schema

    def _show_list_fields(self, schema: Schema) -> Schema:
        for list_field in self.list_fields:
            schema.update(
                {
                    list_field: [
                        toolkit.get_converter("convert_from_extras"),
                        toolkit.get_validator("list_of_strings"),
                        reformat_command_list,
                    ]
                }
            )
        return schema

    def _modify_json_fields(self, schema: Schema) -> Schema:
        for json_field in self.json_fields:
            schema.update(
                {
                    json_field: [
                        toolkit.get_converter("convert_to_json_if_string"),
                        toolkit.get_validator("json_object"),
                        toolkit.get_converter("convert_to_extras"),
                    ]
                }
            )
        return schema

    def _show_json_fields(self, schema: Schema) -> Schema:
        for json_field in self.json_fields:
            schema.update(
                {
                    json_field: [
                        toolkit.get_converter("convert_from_extras"),
                        toolkit.get_validator("json_object"),
                    ]
                }
            )
        return schema

    def _modify_ignore_missing_fields(self, schema: Schema) -> Schema:
        for ignore_missing_field in self.ignore_missing_fields:
            schema.update(
                {
                    ignore_missing_field: [
                        toolkit.get_validator("ignore_missing"),
                        toolkit.get_converter("convert_to_extras"),
                    ]
                }
            )
        return schema

    def _show_ignore_missing_fields(self, schema: Schema) -> Schema:
        for ignore_missing_field in self.ignore_missing_fields:
            schema.update(
                {
                    ignore_missing_field: [
                        toolkit.get_converter("convert_from_extras"),
                        toolkit.get_validator("ignore_missing"),
                    ]
                }
            )
        return schema

    def _modify_additional_resource_fields(self, schema: Schema) -> Schema:
        resource_schema = cast(Schema, schema["resources"])
        for additional_field in self.additional_resource_fields:
            resource_schema.update(
                {
                    additional_field: [
                        toolkit.get_validator("not_empty"),
                        toolkit.get_converter("convert_to_extras"),
                    ]
                }
            )
        schema["resources"] = resource_schema
        return schema

    def _show_additional_resource_fields(self, schema: Schema) -> Schema:
        resource_schema = cast(Schema, schema["resources"])
        for additonal_field in self.additional_resource_fields:
            resource_schema.update(
                {
                    additonal_field: [
                        toolkit.get_converter("convert_from_extras"),
                        toolkit.get_validator("not_empty"),
                    ]
                }
            )
        schema["resources"] = resource_schema
        return schema

    def _parse_dataset(self, g: Graph, dataset: dict) -> URIRef:
        raise NotImplementedError("Placeholder function for inheritance")

    def _handle_ckan_data(self, results: list[dict]) -> Graph:
        g = Graph()
        self._bind_to_namespaces(g)

        catalog_uri = URIRef(self.catalog_endpoint)
        g.add((catalog_uri, RDF.type, DCAT.Catalog))

        for dataset in results:
            dataset_uri = self._parse_dataset(g, dataset)
            g.add((catalog_uri, DCAT.dataset, dataset_uri))
        return g

    def create_catalog_ttl(self, results: list[dict]) -> str:
        g = self._handle_ckan_data(results)
        ttl = g.serialize(format="ttl")
        return ttl

    def create_dataset_ttl(self, result: dict) -> str:
        g = Graph()
        self._bind_to_namespaces(g)
        self._parse_dataset(g, result)
        ttl = g.serialize(format="ttl")
        return ttl

    def modify_schema(self, schema: Schema) -> Schema:
        schema = self._modify_simple_fields(schema)
        schema = self._modify_datetime_fields(schema)
        schema = self._modify_list_fields(schema)
        schema = self._modify_json_fields(schema)
        schema = self._modify_ignore_missing_fields(schema)
        schema = self._modify_additional_resource_fields(schema)
        return schema

    def show_schema(self, schema: Schema) -> Schema:
        schema = self._show_simple_fields(schema)
        schema = self._show_datetime_fields(schema)
        schema = self._show_list_fields(schema)
        schema = self._show_json_fields(schema)
        schema = self._show_ignore_missing_fields(schema)
        schema = self._show_additional_resource_fields(schema)
        return schema


class MirrorHandler(BaseHandler):
    def __init__(self) -> None:
        super().__init__()
        self.simple_fields = [
            "docker_file",
            "compose_file",
            "docker_image",
            "git_repo",
            "docker_repo",
            "commit_hash",
            "digest_hash",
            "temporal_resolution",
            "spatial_resolution",
            "rfc_alias",
            "rfc_full_name",
            "rfc_parent_organization",
            "rfc_wkt",
            "source_dataset",
        ]
        self.datetime_fields = ["last_modified", "start_time", "end_time"]
        self.list_fields = ["command_list"]
        self.additional_resource_fields = ["access_rights", "compress_format"]
        self.base_url = os.environ["CKAN_SITE_URL"]
        self.catalog_fn = "catalog.ttl"
        self.catalog_endpoint = f"{self.base_url}/aorc_MirrorDataset/{self.catalog_fn}"

    def __add_source_dataset(
        self, g: Graph, ttl_str: str, target_node: URIRef, rfc_alias_literal: Literal, start_date_literal: Literal
    ) -> None:
        g.parse(data=ttl_str, format="ttl")

        query = """
            SELECT ?node
            WHERE {
                ?node a aorc:SourceDataset .
                ?node dct:temporal ?t .
                ?node aorc:hasRFC ?rfc .
                ?t dcat:startDate ?sd .
                ?rfc skos:altLabel ?alias .
            }
            """
        source_results = g.query(
            query,
            initNs={"aorc": AORC, "dcat": DCAT, "dct": DCTERMS},
            initBindings={"sd": start_date_literal, "alias": rfc_alias_literal},
        )
        if len(source_results) > 1:
            raise ValueError(
                f"Expected one match source dataset, found at least one more for {rfc_alias_literal} and {start_date_literal}"
            )
        elif len(source_results) == 0:
            raise ValueError(
                f"Expected one match source dataset, found zero for {rfc_alias_literal} and {start_date_literal}"
            )
        for row in source_results:
            g.add((target_node, DCTERMS.source, row.node))
            return

    def _parse_dataset(self, g: Graph, dataset: dict) -> URIRef:
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

        self.__add_source_dataset(g, dataset["source_dataset"], mirror_dataset_uri, rfc_alias_literal, start_literal)

        self.handle_resources(
            dataset["resources"], mirror_dataset_uri, f"{self.base_url}/aorc_MirrorDataset/{dataset['url'].lower()}", g
        )

        return mirror_dataset_uri


class CompositeHandler(BaseHandler):
    def __init__(self) -> None:
        super().__init__()
        self.simple_fields = [
            "docker_file",
            "compose_file",
            "docker_image",
            "git_repo",
            "docker_repo",
            "commit_hash",
            "digest_hash",
            "spatial_resolution",
            "location_name",
            "location_wkt",
        ]
        self.datetime_fields = ["last_modified", "start_time", "end_time"]
        self.list_fields = ["command_list", "mirror_datasets"]
        self.additional_resource_fields = ["access_rights"]
        self.base_url = os.environ["CKAN_SITE_URL"]
        self.catalog_fn = "catalog.ttl"
        self.catalog_endpoint = f"{self.base_url}/aorc_CompositeDataset/{self.catalog_fn}"

    def _parse_dataset(self, g: Graph, dataset: dict) -> URIRef:
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

        self.handle_resources(
            dataset["resources"],
            composite_dataset_uri,
            f"{self.base_url}/aorc_CompositeDataset/{dataset['url'].lower()}",
            g,
        )

        return composite_dataset_uri


class TranspositionHandler(BaseHandler):
    def __init__(self) -> None:
        super().__init__()
        self.simple_fields = [
            "docker_file",
            "compose_file",
            "docker_image",
            "git_repo",
            "docker_repo",
            "commit_hash",
            "digest_hash",
            "spatial_resolution",
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
        self.datetime_fields = ["last_modified", "start_time", "end_time"]
        self.list_fields = ["command_list"]
        self.json_fields = ["composite_normalized_datasets"]
        self.ignore_missing_fields = ["normalized_mean_precipitation", "max_precipitation_point_name"]
        self.additional_resource_fields = ["access_rights"]
        self.base_url = os.environ["CKAN_SITE_URL"]
        self.catalog_fn = "catalog.ttl"
        self.catalog_endpoint = f"{self.base_url}/aorc_TranspositionDataset/{self.catalog_fn}"

    @staticmethod
    def _create_image_rights_statement(image_uri: str) -> Literal | None:
        pattern = re.compile(r"^s3:\/\/")
        if re.search(pattern, image_uri):
            return Literal(
                "This image is a resource held within an s3 bucket. In order to access the image, you must have read access to the parent s3 bucket.",
                datatype=XSD.string,
            )
        return

    def _bind_to_namespaces(self, g: Graph) -> None:
        super()._bind_to_namespaces(g)
        g.bind("foaf", FOAF)

    def __parse_composite_dataset(self, g: Graph, transposition_dataset_uri: URIRef, composite_datasets_str: str):
        composite_datasets_dict = json.loads(composite_datasets_str)
        for composite_dataset_url, normalization_data_download_url in composite_datasets_dict.items():
            composite_dataset_uri = URIRef(composite_dataset_url)
            g.add((composite_dataset_uri, RDF.type, AORC.CompositeDataset))
            g.add((transposition_dataset_uri, DCTERMS.source, composite_dataset_uri))
            if normalization_data_download_url:
                normalization_dataset_b_node = BNode()
                normalization_data_download_url_literal = Literal(normalization_data_download_url, datatype=XSD.anyURI)
                g.add((normalization_dataset_b_node, RDF.type, DCAT.Dataset))
                g.add((normalization_dataset_b_node, DCAT.downloadURL, normalization_data_download_url_literal))
                g.add((composite_dataset_uri, AORC.normalizedBy, normalization_dataset_b_node))

    def _parse_dataset(self, g: Graph, dataset: dict) -> URIRef:
        transposition_dataset_uri = URIRef(f"{self.base_url}/aorc_TranspositionDataset/{dataset['url']}")
        g.add((transposition_dataset_uri, RDF.type, AORC.TranspositionDataset))

        docker_process_b_node = BNode()
        g.add((docker_process_b_node, RDF.type, AORC.DockerProcess))
        g.add((transposition_dataset_uri, PROV.wasGeneratedBy, docker_process_b_node))

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

        self.__parse_composite_dataset(g, transposition_dataset_uri, dataset["composite_normalized_datasets"])

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

        watershed_b_node = BNode()
        watershed_name_literal = Literal(dataset["watershed_region_name"])
        g.add((watershed_b_node, RDF.type, DCTERMS.Location))
        g.add((watershed_b_node, LOCN.geographicName, watershed_name_literal))
        g.add((transposition_dataset_uri, AORC.watershedRegion, watershed_b_node))

        watershed_geom_b_node = BNode()
        watershed_geom_wkt_literal = Literal(dataset["watershed_region_wkt"], datatype=GEO.wktLiteral)
        g.add((watershed_geom_b_node, RDF.type, LOCN.Geometry))
        g.add((watershed_geom_b_node, GEO.asWKT, watershed_geom_wkt_literal))
        g.add((watershed_b_node, LOCN.geometry, watershed_geom_b_node))

        transposition_b_node = BNode()
        transposition_name_literal = Literal(dataset["transposition_region_name"])
        g.add((transposition_b_node, RDF.type, DCTERMS.Location))
        g.add((transposition_b_node, LOCN.geographicName, transposition_name_literal))
        g.add((transposition_dataset_uri, AORC.transpositionRegion, transposition_b_node))

        transposition_geom_b_node = BNode()
        transposition_geom_wkt_literal = Literal(dataset["transposition_region_wkt"], datatype=GEO.wktLiteral)
        g.add((transposition_geom_b_node, RDF.type, LOCN.Geometry))
        g.add((transposition_geom_b_node, GEO.asWKT, transposition_geom_wkt_literal))
        g.add((transposition_b_node, LOCN.geometry, transposition_geom_b_node))

        max_precip_b_node = BNode()
        g.add((max_precip_b_node, RDF.type, DCTERMS.Location))
        g.add((transposition_dataset_uri, AORC.maxPrecipitationPoint, max_precip_b_node))

        if dataset.get("max_precipitation_point_name"):
            max_precip_name_literal = Literal(dataset["max_precipitation_point_name"])
            g.add((transposition_b_node, LOCN.geographicName, max_precip_name_literal))

        max_precip_geom_b_node = BNode()
        max_precip_geom_wkt_literal = Literal(dataset["max_precipitation_point_wkt"], datatype=GEO.wktLiteral)
        g.add((max_precip_geom_b_node, RDF.type, LOCN.Geometry))
        g.add((max_precip_geom_b_node, GEO.asWKT, max_precip_geom_wkt_literal))
        g.add((max_precip_b_node, LOCN.geometry, max_precip_geom_b_node))

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
        g.add((transposition_dataset_uri, AORC.cellCount, cell_count_literal))

        mean_precipitation_literal = Literal(dataset["mean_precipitation"], datatype=XSD.float)
        g.add((transposition_dataset_uri, AORC.meanPrecipitation, mean_precipitation_literal))

        max_precipitation_literal = Literal(dataset["max_precipitation"], datatype=XSD.float)
        g.add((transposition_dataset_uri, AORC.maxPrecipitation, max_precipitation_literal))

        min_precipitation_literal = Literal(dataset["min_precipitation"], datatype=XSD.float)
        g.add((transposition_dataset_uri, AORC.minPrecipitation, min_precipitation_literal))

        sum_precipitation_literal = Literal(dataset["sum_precipitation"], datatype=XSD.float)
        g.add((transposition_dataset_uri, AORC.sumPrecipitation, sum_precipitation_literal))

        if dataset.get("normalized_mean_precipitation"):
            normalized_mean_precipitation_literal = Literal(
                dataset["normalized_mean_precipitation"], datatype=XSD.float
            )
            g.add(
                (
                    transposition_dataset_uri,
                    AORC.normalizedMeanPrecipitation,
                    normalized_mean_precipitation_literal,
                )
            )

        self.handle_resources(
            dataset["resources"],
            transposition_dataset_uri,
            f"{self.base_url}/aorc_TranspositionDataset/{dataset['url'].lower()}",
            g,
        )

        return transposition_dataset_uri


class DatasetHandler(Enum):
    MIRROR = "aorc:MirrorDataset"
    COMPOSITE = "aorc:CompositeDataset"
    TRANSPOSITION = "aorc:TranspositionDataset"

    @property
    def sanitized_value(self) -> str:
        return self.value.replace(":", "_")


class AORCPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "aorc")

    @staticmethod
    def __match_datahandler(sanitized_package_type: str) -> DatasetHandler:
        for p in DatasetHandler:
            if p.sanitized_value == sanitized_package_type:
                return p
        raise ValueError(
            f"Expected input type defined in class DatasetHandler, got unexpected value {sanitized_package_type}"
        )

    def __detect_type(self) -> DatasetHandler:
        package_type_sanitized = toolkit.request.view_args.get("package_type")
        matched_package_type = self.__match_datahandler(package_type_sanitized)
        return matched_package_type

    def __define_handler(self, package_type: DatasetHandler) -> None:
        if package_type == DatasetHandler.MIRROR:
            self.handler = MirrorHandler()
        elif package_type == DatasetHandler.COMPOSITE:
            self.handler = CompositeHandler()
        else:
            self.handler = TranspositionHandler()

    def update_package_schema(self) -> Schema:
        package_type = self.__detect_type()
        self.__define_handler(package_type)
        schema: Schema = super(AORCPlugin, self).update_package_schema()
        return self.handler.modify_schema(schema)

    def show_package_schema(self) -> Schema:
        package_type = self.__detect_type()
        self.__define_handler(package_type)
        schema: Schema = super(AORCPlugin, self).show_package_schema()
        return self.handler.show_schema(schema)

    def is_fallback(self) -> bool:
        return False

    def package_types(self) -> list[str]:
        return [p.sanitized_value for p in DatasetHandler]

    def edit_template(self, package_type: str) -> str:
        matched_package_type = self.__match_datahandler(package_type)
        if matched_package_type == DatasetHandler.MIRROR:
            return "package/mirror_edit.html"
        elif matched_package_type == DatasetHandler.COMPOSITE:
            return "package/composite_edit.html"
        else:
            return "package/transposition_edit.html"

    def read_template(self, package_type: str) -> str:
        matched_package_type = self.__match_datahandler(package_type)
        if matched_package_type == DatasetHandler.MIRROR:
            return "package/mirror_read.html"
        elif matched_package_type == DatasetHandler.COMPOSITE:
            return "package/composite_read.html"
        else:
            return "package/transposition_read.html"

    def resource_form(self, package_type: str) -> str:
        matched_package_type = self.__match_datahandler(package_type)
        if matched_package_type == DatasetHandler.MIRROR:
            return "package/snippets/mirror_resource_form.html"
        elif matched_package_type == DatasetHandler.COMPOSITE:
            return "package/snippets/composite_resource_form.html"
        else:
            return "package/snippets/transposition_resource_form.html"

    def prepare_dataset_blueprint(self, package_type: str, blueprint: Blueprint) -> Blueprint:
        matched_package_type = self.__match_datahandler(package_type)
        self.__define_handler(matched_package_type)
        blueprint.add_url_rule(f"/{self.handler.catalog_fn}", view_func=self.view_catalog_ttl)
        blueprint.add_url_rule(f"/<_id>.ttl", view_func=self.view_dataset_ttl)
        return blueprint

    @staticmethod
    def __get_package_count(package_type: str) -> int:
        result = toolkit.get_action("package_search")(
            data_dict={"fq": f"type:{package_type}", "rows": 1}  # Adjust the number of rows as needed
        )
        return result.get("count", 0)

    def view_catalog_ttl(self, package_type: str, limit: int = None, step: int = 100) -> Response:
        matched_package_type = self.__match_datahandler(package_type)
        self.__define_handler(matched_package_type)
        result_list = []
        current_offset = 0
        if limit == None:
            limit = self.__get_package_count(package_type)
        while current_offset < limit:
            result = toolkit.get_action("package_search")(
                data_dict={
                    "fq": f"type:{package_type}",
                    "rows": step,
                    "start": current_offset,
                }  # Adjust the number of rows as needed
            )
            current_offset += step
            result_list.extend(result.get("results", []))
        catalog_ttl = self.handler.create_catalog_ttl(result_list)
        # Change to flask.Response class to manually set content type / mime type
        resp = make_response(catalog_ttl, {"Content-Type": "text/plain; charset=utf-8"})
        return resp

    def view_dataset_ttl(self, package_type: str, _id: str) -> Response:
        matched_package_type = self.__match_datahandler(package_type)
        self.__define_handler(matched_package_type)
        result = toolkit.get_action("package_show")(data_dict={"id": _id})
        dataset_ttl = self.handler.create_dataset_ttl(result)
        resp = make_response(dataset_ttl, {"Content-Type": "text/plain; charset=utf-8"})
        return resp
