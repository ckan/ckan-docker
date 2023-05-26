[![Tests](https://git.fhgr.ch/resto/ckanext-nadit/badges/main/pipeline.svg)](https://git.fhgr.ch/resto/ckanext-nadit/)

# ckanext-nadit

A custom CKAN data harvester for the NADIT project.

## Usage

Firstly, make sure that you have created at least one Organization.

(1) Access the plugin through the `/harvest` URL on your server. For example, if you are running a development server it is likely to be http://ckan:5000/harvest/

(2) Click **Add harvest source**, and fill out the form as follows:

- URL: the CKAN site we are harvesting. Example: https://ckan.opendata.swiss
- Title: a short descriptive tag for this harvester. Example: `BFS - Tourism`
- Description: your notes on this workflow, key contacts, etc.
- Source type: "NADIT plugin for CKAN"
- Update frequency: set to anything other than Manual to automate harvests
- Organization: choose from one of the CKAN orgs
- Configuration: this is an optional bit of JSON to filter the harvester, as you may not want to mirror the entire CKAN instance. Example: 

```
{
"organizations_filter_include": ["openglam"],
"groups_filter_include": ["culture", "tourism"],
"force_all": true
}
```

Multiple organizations or groups can be included in this way.

### Further references

See Harvesting chapter in the [Opendata.swiss Handbook](https://handbook.opendata.swiss/de/content/publizieren/publikationsvarianten/harvesting.html#harvesting-einrichten) (German only) and docs for [ckanext-harvest](https://github.com/ckan/ckanext-harvest#the-ckan-harvester).

_TODO: in the future, we can add a link next to "Add Dataset", or to the Administer CKAN page._

## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible? |
|-----------------|-------------|
| 2.8 and earlier | not tested  |
| 2.9             | yes         |
| 2.10            | yes         |

## Installation with Docker

We are developing this plugin using the convenient 
[ckan-docker](https://github.com/datalets/ckan-docker) 
build system, with installation as follows:

(1) Clone the folder in the `src` folder at the CKAN root. 

The full path might be `/opt/docker/ckan/src/ckanext-nadit`

(2) Add the project to your plugins list.

`CKAN__PLUGINS="envvars image_view... harvest nadit nadit_ckan_harvester"`

(3) Install plugin dependencies. 

(Should be done automatically by CKAN's build scripts)

(4) Make sure the default [CKAN Harvester](https://github.com/ckan/ckanext-harvest#ckanext-harvest---remote-harvesting-extension) is set up correctly.

(Making sure that `gather_consumer` and `fetch_consumer` processes are set up to run automatically, such as with [this supervisord script](https://github.com/datalets/ckan-docker/blob/766accecf7538ad6344620c75a526325723d0695/ckan/setup/consumers.conf))

(5) Create your first harvester by navigating to https://yourckansite.tld/harvest, select the "Nadit plugin for CKAN" Option and enter an appropriate URL. In the case of opendata.swiss this is https://ckan.opendata.swiss/

**Tips:**

- To see status reports: `tail -f /var/log/*.log`
- To refresh a running server: `./start_ckan_development.sh`

## Installation as source

To install ckanext-nadit in your local Python environment:

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

```
    git clone https://github.com/datalets/ckanext-nadit.git
    cd ckanext-nadit
    pip install -e .
	pip install -r requirements.txt
```

3. Add `nadit` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`). For example, the full 
   configuration we use is:

   `CKAN__PLUGINS="envvars image_view text_view recline_view datastore datapusher dcat dcat_rdf_harvester dcat_json_harvester dcat_json_interface structured_data harvest nadit nadit_ckan_harvester"`

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

   `sudo service apache2 reload`

5. Ensure that harvester jobs are running (e.g. in your supervisord)
   ```
   ckan --config=/srv/app/ckan.ini harvester gather-consumer &
   ckan --config=/srv/app/ckan.ini harvester fetch-consumer
   ```

## Plugin config settings

None at present.

**TODO:** Document any optional config settings here. For example:

	# The minimum number of hours to wait before re-checking a resource
	# (optional, default: 24).
	ckanext.nadit.some_setting = some_default_value


## Developer references

- https://docs.ckan.org/en/2.10/extensions/index.html
- https://github.com/ckan/ckanext-harvest#the-ckan-harvester
- https://www.polaz.net/how-to-develop-a-plugin-for-ckan-part-1/

## Developer installation

To install ckanext-nadit for development, activate your CKAN virtualenv and
do:

    git clone https://github.com/datalets/ckanext-nadit.git
    cd ckanext-nadit
    python setup.py develop
    pip install -r dev-requirements.txt


## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini


## Releasing a new version of ckanext-nadit

If ckanext-nadit should be available on PyPI you can follow these steps to publish a new version:

1. Update the version number in the `setup.py` file. See [PEP 440](http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers) for how to choose version numbers.

2. Make sure you have the latest version of necessary packages:

    pip install --upgrade setuptools wheel twine

3. Create a source and binary distributions of the new version:

       python setup.py sdist bdist_wheel && twine check dist/*

   Fix any errors you get.

4. Upload the source distribution to PyPI:

       twine upload dist/*

5. Commit any outstanding changes:

       git commit -a
       git push

6. Tag the new release of the project on GitHub with the version number from
   the `setup.py` file. For example if the version number in `setup.py` is
   0.0.1 then do:

       git tag 0.0.1
       git push --tags

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
