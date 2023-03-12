[![Tests](https://github.com/datalets/ckanext-nadit/workflows/Tests/badge.svg?branch=main)](https://github.com/datalets/ckanext-nadit/actions)

# ckanext-nadit

**TODO:** Put a description of your extension here:  What does it do? What features does it have? Consider including some screenshots or embedding a video!

`tail -f /var/log/*.log`

## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible? |
|-----------------|-------------|
| 2.8 and earlier | not tested  |
| 2.9             | yes         |
| 2.10            | yes         |


## Installation

To install ckanext-nadit:

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone https://github.com/datalets/ckanext-nadit.git
    cd ckanext-nadit
    pip install -e .
	pip install -r requirements.txt

3. Add `nadit` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     sudo service apache2 reload

5. If harvesters are not running

     ckan --config=/srv/app/ckan.ini harvester gather-consumer &
     ckan --config=/srv/app/ckan.ini harvester fetch-consumer

## Config settings

None at present

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
