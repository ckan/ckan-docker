from __future__ import annotations

from enum import Enum
from typing import Any, cast

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.config.middleware import CKANConfig
from ckan.types import Schema


class AORCDatasetClass(Enum):
    MIRROR = "aorc:MirrorDataset"
    COMPOSITE = "aorc:CompositeDataset"
    TRANSPOSITION = "aorc:TranspositionDataset"


class AORCHandler:
    def __init__(
        self, class_name: AORCDatasetClass, read_template: str, edit_template: str, resource_template: str
    ) -> None:
        self.class_name = class_name
        self.read_template = read_template
        self.edit_template = edit_template
        self.resource_template = resource_template
        self.common_fields_simple = [
            "spatial_resolution",
            "temporal_resolution",
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
        self.rfc_fields_simple = ["rfc_alias", "rfc_full_name", "rfc_wkt"]
        self.additional_resource_common_fields = ["compress_format", "access_rights"]
        self.fields_simple = self.fields_dt = self.fields_list = self.fields_json = self.additional_resource_fields = []

    def update_schema(self, schema: Schema) -> Schema:
        for simple_field in self.fields_simple:
            schema.update(
                {simple_field: [toolkit.get_validator("not_empty"), toolkit.get_converter("convert_to_extras")]}
            )
        for dt_field in self.fields_dt:
            schema.update({dt_field: [toolkit.get_validator("isodate"), toolkit.get_converter("convert_to_extras")]})
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
                {json_field: [toolkit.get_validator("json_object"), toolkit.get_converter("convert_to_extras")]}
            )
        resource_schema = cast(Schema, schema["resources"])
        for additional_field in self.additional_resource_fields:
            resource_schema.update(
                {additional_field: [toolkit.get_validator("not_empty"), toolkit.get_converter("convert_to_extras")]}
            )

    def show_schema(self, schema: Schema) -> Schema:
        for simple_field in self.fields_simple:
            schema.update(
                {simple_field: [toolkit.get_converter("convert_from_extras"), toolkit.get_validator("not_empty")]}
            )
        for dt_field in self.fields_dt:
            schema.update({dt_field: [toolkit.get_converter("convert_from_extras"), toolkit.get_validator("isodate")]})
        for list_field in self.fields_list:
            schema.update(
                {list_field: [toolkit.get_converter("convert_from_extras"), toolkit.get_validator("list_of_strings")]}
            )
        for json_field in self.fields_json:
            schema.update(
                {json_field: [toolkit.get_converter("convert_from_extras"), toolkit.get_validator("json_object")]}
            )
        resource_schema = cast(Schema, schema["resources"])
        for additonal_field in self.additional_resource_fields:
            resource_schema.update(
                {additonal_field: [toolkit.get_converter("convert_from_extras"), toolkit.get_validator("not_empty")]}
            )


class MirrorHandler(AORCHandler):
    def __init__(
        self,
        class_name: AORCDatasetClass = AORCDatasetClass.MIRROR,
        read_template: str = "package/mirror_read.html",
        edit_template: str = "package/mirror_edit.html",
        resource_template: str = "package/aorc_resource.html",
    ) -> None:
        super().__init__(class_name, read_template, edit_template, resource_template)
        self._validate_name()
        self.fields_simple = [*self.common_fields_list, *self.rfc_fields_simple]
        self.fields_dt = [*self.common_fields_dt, *self.time_period_fields_dt]
        self.fields_list = self.common_fields_list
        self.fields_json = ["source_dataset"]
        self.additional_resource_fields = self.additional_resource_common_fields

    def _validate_name(self):
        if self.class_name != AORCDatasetClass.MIRROR:
            raise ValueError(f"Mirror handler created for incorrect AORC class: {AORCDatasetClass}")


class AorcMirrorPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._possible_dataset_class = AORCDatasetClass
        self.handler = None

    def update_config(self, config_: CKANConfig):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "aorc_mirror")

    def update_package_schema(self):
        schema: Schema = super(AorcMirrorPlugin, self).update_package_schema()
        if not self.handler:
            return schema
        return self.handler.update_schema(schema)

    def show_package_schema(self) -> Schema:
        schema: Schema = super(AorcMirrorPlugin, self).show_package_schema()
        if not self.handler:
            return schema
        return self.handler.show_schema(schema)

    def is_fallback(self) -> bool:
        return False

    def package_types(self) -> list[str]:
        # package_types = [i.name for i in self._possible_dataset_class]
        package_types = ["aorc:MirrorDataset"]
        return package_types

    def edit_template(self, package_type: str) -> str:
        if not self.handler:
            default_edit_template = super(AorcMirrorPlugin, self).edit_template()
            if package_type == AORCDatasetClass.MIRROR.value:
                self.handler = MirrorHandler()
                return self.handler.edit_template
            return default_edit_template
        return self.handler.edit_template

    def read_template(self, package_type: str) -> str:
        if not self.handler:
            default_read_template = super(AorcMirrorPlugin, self).read_template()
            if package_type == AORCDatasetClass.MIRROR.value:
                self.handler = MirrorHandler()
                return self.handler.read_template
            return default_read_template
        return self.handler.read_template
