from setuptools import setup, find_packages

setup(
    name='ckanext-idsk',
    version='0.1',
    packages=find_packages(),
    entry_points='''
        [ckan.plugins]
        idsk_theme=ckanext.idsk.plugin:IDSKThemePlugin
    ''',
)