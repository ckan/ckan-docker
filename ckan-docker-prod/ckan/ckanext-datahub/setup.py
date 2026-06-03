from setuptools import find_namespace_packages, setup

setup(
    name="ckanext-datahub",
    version="0.1.0",
    packages=find_namespace_packages(include=["ckanext.*"]),
    include_package_data=True,
    package_data={
        "ckanext.datahub": [
            "templates/*.html",
            "templates/**/*.html",
        ],
    },
    entry_points="""
        [ckan.plugins]
        datahub_branding=ckanext.datahub.plugin:DataHubBrandingPlugin

        [ckan.rdf.profiles]
        datahub_dcat_ap_sk=ckanext.datahub.dcat_ap_sk:DataHubDCATAPSKProfile
    """,
)
