from setuptools import find_packages, setup

setup(
    name="ckanext-idsk",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "ckanext.idsk": [
            "schemas/*.yaml",
            "templates/**/*.html",
            "public/**/*",
        ],
    },
    entry_points="""
        [ckan.plugins]
        idsk_theme=ckanext.idsk.plugin:IDSKThemePlugin
    """,
)
