from __future__ import annotations

import sys
from typing import Any

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.config.middleware import CKANConfig
from ckan.types import Schema

sys.path.append("/srv/app/src_extensions")

from utils.aorc_handler import AORCDatasetClass, AORCHandler


class CompositeHandler(AORCHandler):
    def __init__(
        self,
        class_name: AORCDatasetClass = AORCDatasetClass.COMPOSITE,
        read_template: str = "package/composite_read.html",
        edit_template: str = "package/composite_edit.html",
        resource_form_template: str = "package/snippets/composite_resource_form.html",
    ) -> None:
        super().__init__(class_name, read_template, edit_template, resource_form_template)
        self._validate_class()
        self.fields_simple = [*self.common_fields_simple, *self.location_fields_simple]
        self.fields_dt = [*self.common_fields_dt, *self.time_period_fields_dt]
        self.fields_list = [*self.common_fields_list, "mirror_datasets"]
        self.additional_resource_fields = self.additional_resource_common_fields

    def _validate_class(self):
        if self.class_name != AORCDatasetClass.COMPOSITE:
            raise ValueError(f"Handler created for incorrect AORC class: {self.class_name}")

    def validate_name(self, dataset_type: str):
        if dataset_type != self.class_name.value:
            raise ValueError(f"Handler used for dataseet with class {dataset_type}, not {self.class_name.value}")


class AorcCompositePlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.handler = CompositeHandler()

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
        return ["aorc:CompositeDataset"]

    def edit_template(self, package_type: str) -> str:
        self.handler.validate_name(package_type)
        return self.handler.edit_template

    def read_template(self, package_type: str) -> str:
        self.handler.validate_name(package_type)
        return self.handler.read_template

    def resource_form(self, package_type: str) -> str:
        self.handler.validate_name(package_type)
        return self.handler.resource_form_template
