import datetime
from enum import Enum
from typing import cast
import psycopg2

import ckan.plugins.toolkit as toolkit
from ckan.types import Schema


class AORCDatasetClass(Enum):
    MIRROR = "aorc:MirrorDataset"
    COMPOSITE = "aorc:CompositeDataset"
    TRANSPOSITION = "aorc:TranspositionDataset"


def datetime_to_string(dt: datetime.datetime) -> str:
    return dt.isoformat()


class AORCHandler:
    def __init__(
        self,
        class_name: AORCDatasetClass,
        new_template: str,
        read_template: str,
        edit_template: str,
        resource_form_template: str,
    ) -> None:
        self._register_dict_handler()
        self.class_name = class_name
        self.new_template = new_template
        self.read_template = read_template
        self.edit_template = edit_template
        self.resource_form_template = resource_form_template
        self.common_fields_simple = [
            "spatial_resolution",
            "docker_file",
            "compose_file",
            "docker_image",
            "git_repo",
            "docker_repo",
            "commit_hash",
            "digest_hash",
        ]
        self.common_fields_dt = ["last_modified"]
        self.common_fields_list = ["command_list"]
        self.time_period_fields_dt = ["start_time", "end_time"]
        self.time_resolution_duration_fields_simple = ["temporal_resolution"]
        self.rfc_fields_simple = ["rfc_alias", "rfc_full_name", "rfc_parent_organization", "rfc_wkt"]
        self.additional_resource_common_fields = ["compress_format", "access_rights"]
        self.location_fields_simple = ["location_name", "location_wkt"]
        self.fields_simple = self.fields_dt = self.fields_list = self.fields_json = self.additional_resource_fields = []
        self.fields_ignore_missing = []

    def _register_dict_handler(self) -> None:
        psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)

    def modify_schema(self, schema: Schema) -> Schema:
        for simple_field in self.fields_simple:
            schema.update(
                {
                    simple_field: [
                        toolkit.get_validator("not_empty"),
                        toolkit.get_converter("convert_to_extras"),
                    ]
                }
            )
        for dt_field in self.fields_dt:
            schema.update(
                {
                    dt_field: [
                        toolkit.get_validator("isodate"),
                        datetime_to_string,
                        toolkit.get_converter("convert_to_extras"),
                    ]
                }
            )
        for list_field in self.fields_list:
            schema.update(
                {
                    list_field: [
                        toolkit.get_validator("not_empty"),
                        toolkit.get_converter("as_list"),
                        toolkit.get_converter("convert_to_extras"),
                    ]
                }
            )
        for json_field in self.fields_json:
            schema.update(
                {
                    json_field: [
                        toolkit.get_converter("convert_to_json_if_string"),
                        toolkit.get_validator("json_object"),
                        toolkit.get_converter("convert_to_extras"),
                    ]
                }
            )
        for ignore_missing_field in self.fields_ignore_missing:
            schema.update(
                {
                    ignore_missing_field: [
                        toolkit.get_validator("ignore_missing"),
                        toolkit.get_converter("convert_to_extras"),
                    ]
                }
            )
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
        return schema

    def show_schema(self, schema: Schema) -> Schema:
        for simple_field in self.fields_simple:
            schema.update(
                {
                    simple_field: [
                        toolkit.get_converter("convert_from_extras"),
                        toolkit.get_validator("not_empty"),
                    ]
                }
            )
        for dt_field in self.fields_dt:
            schema.update(
                {
                    dt_field: [
                        toolkit.get_converter("convert_from_extras"),
                        toolkit.get_validator("isodate"),
                        datetime_to_string,
                    ]
                }
            )
        for list_field in self.fields_list:
            schema.update(
                {
                    list_field: [
                        toolkit.get_converter("convert_from_extras"),
                        toolkit.get_validator("list_of_strings"),
                        toolkit.get_converter("convert_to_json_if_string"),
                    ]
                }
            )
        for json_field in self.fields_json:
            schema.update(
                {
                    json_field: [
                        toolkit.get_converter("convert_from_extras"),
                        toolkit.get_validator("json_object"),
                    ]
                }
            )
        for ignore_missing_field in self.fields_ignore_missing:
            schema.update(
                {
                    ignore_missing_field: [
                        toolkit.get_converter("convert_from_extras"),
                        toolkit.get_validator("ignore_missing"),
                    ]
                }
            )
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
        return schema
