from __future__ import annotations

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
from ckan.config.middleware import CKANConfig
from ckan.types import Schema


class ExampleNewExtensionPlugin(plugins.SingletonPlugin, tk.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)

    def _modify_package_schema(self, schema: Schema) -> Schema:
        schema.update({"custom_text": [tk.get_validator("ignore_missing"), tk.get_converter("convert_to_extras")]})
        return schema

    def create_package_schema(self):
        schema: Schema = super(ExampleNewExtensionPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema: Schema = super(ExampleNewExtensionPlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def show_package_schema(self) -> Schema:
        schema: Schema = super(ExampleNewExtensionPlugin, self).show_package_schema()
        schema.update({"custom_text": [tk.get_converter("convert_from_extras"), tk.get_validator("ignore_missing")]})
        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self) -> list[str]:
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []

    def update_config(self, config: CKANConfig):
        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        tk.add_template_directory(config, "templates")
