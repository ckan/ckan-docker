# encoding=utf-8
from __future__ import annotations

import fnmatch
import json
import logging
from collections import OrderedDict
from os import path
import re
import yaml

import ckan.logic as logic
import ckan.model as model
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import _
from ckan.lib.helpers import _url_with_params
from ckan.lib.helpers import helper_functions as h
from ckan.lib.helpers import url_for

LOGGER = logging.getLogger(__name__)


invest_keywords = []
topic_keywords = []

with open(path.join(path.dirname(__file__), 'topic_keywords.json'), 'r') as f:
    topic_keywords = json.load(f)

with open(path.join(path.dirname(__file__), 'invest_keywords.json'), 'r') as f:
    invest_keywords = json.load(f)


shown_extensions = [
    'csv',
    'geojson',
    'tif',
    'shp',
    'txt',
    'yml',
]


def get_resource_type_facet_label(resource_type_facet):
    return get_resource_type_label(resource_type_facet['name'])


def get_resource_type_label(resource_type):
    labels = {
        'csv': 'CSV',
        'geojson': 'GeoJSON',
        'tif': 'GeoTIFF',
        'shp': 'Shapefile',
        'txt': 'Text',
        'yml': 'YML',
    }
    return labels.get(resource_type, resource_type)


def get_resource_type_label_short(resource):
    labels = {
        'csv': 'CSV',
        'geojson': 'GEOJSON',
        'tif': 'TIF',
        'shp': 'SHP',
        'txt': 'TXT',
        'yml': 'YML',
    }
    return labels.get(resource_type, resource_type)


def get_ext(resource_url):
    return resource_url.split('.')[-1]


def get_filename(resource_url):
    return resource_url.split('/')[-1].split('.')[0]


def get_resource_type_icon_slug(resource_url):
    return get_ext(resource_url)


def get_invest_models():
    models = invest_keywords['InVEST_Models']

    highlighted = [
        'Sediment Delivery Ratio',
        'Annual Water Yield',
        'Nutrient Delivery Ratio',
        'Seasonal Water Yield',
    ]

    def update_model(model):
        url = _url_with_params(
            url_for('dataset.search'),
            params=[('invest_model', model['model'])],
        )
        name = model['model']
        return {
            'slug': name.replace(' ', '-').lower(),
            'name': name,
            'keywords': model['keywords'],
            'highlighted': name in highlighted,
            'url': url,
        }
    models = sorted([update_model(m) for m in models],
                    key=lambda data: data['name'])
    return models


def get_all_search_facets():
    facets: dict[str, str] = OrderedDict()

    default_facet_titles = {
        u'tags': _(u'Tags'),
        u'vocab_place': _(u'Places'),
        u'res_format': _(u'Formats'),
        u'license_id': _(u'Licenses'),
    }

    for facet in h.facets():
        if facet in default_facet_titles:
            facets[facet] = default_facet_titles[facet]
        else:
            facets[facet] = facet
    for plugin in plugins.PluginImplementations(plugins.IFacets):
        facets = plugin.dataset_facets(facets, 'dataset')

    # Perform an empty search to get all facets
    context = {}
    data_dict = {
        u'q': '',
        u'facet.field': list(facets.keys()),
    }
    LOGGER.debug(f"Searching with data dict {data_dict}")
    query = logic.get_action(u'package_search')(context, data_dict)

    return query['search_facets']


def get_topic_keywords():
    topics = topic_keywords['Topics']

    def update_topic(topic):
        url = _url_with_params(
            url_for('dataset.search'),
            params=[('topic', topic['topic'])],
        )
        return {
            'slug': topic['topic'].replace(' ', '-').lower(),
            'name': topic['topic'],
            'keywords': topic['keywords'],
            'url': url,
        }
    topics = [update_topic(t) for t in topics if t['topic'] != 'Plants']
    return topics


def show_resource(resource_url):
    return get_ext(resource_url) in shown_extensions


def show_icon(resource_url):
    return get_ext(resource_url) in shown_extensions


def parse_json(json_str):
    try:
        return json.loads(json_str)
    except (ValueError, TypeError):
        LOGGER.exception("Could not load string as JSON: %s", json_str)
        return []


def get_collection_tags(context):
    vocab_tags = toolkit.get_action('tag_list')(
        context, {'vocabulary_id': 'collection'})
    return [{'value': tag, 'label': tag} for tag in vocab_tags]


def get_place_tags(context):
    vocab_tags = toolkit.get_action('tag_list')(
        context, {'vocabulary_id': 'place'})
    return [{'value': tag, 'label': tag} for tag in vocab_tags]


def get_collection_name(collection_name):
    dataset = toolkit.get_action('package_show')(
        {}, {'id': collection_name})
    return dataset.get('title', '')


def get_collection_name_url(collection_tags):
    tag_collection_map = {}
    for tag in collection_tags:
        results = toolkit.get_action('package_search')(
            {},
            {
                "fq": f'extras_collection:"{tag}"',
                "q": "type:collection",
                "fl": "title, name",
            }
        )
        if results['count'] > 0:
            tag_collection_map[tag] = results['results']
        else:
            tag_collection_map[tag] = None
    return tag_collection_map


def collection_lulc_biotable(pkg):
    if not pkg['collection']:
        return (False, False)

    tags = [tag['name'] for tag in pkg['tags']]
    if 'LULC' in tags:
        return (True, False)
    if 'BIOPHYSICAL TABLE' in tags:
        return (False, True)
    return (False, False)


def collection_has_datasets(collection_tag):
    results = toolkit.get_action('package_search')(
        {},
        {
            "fq": f'extras_collection:"{collection_tag}"',
            "q": "type:dataset",
            "fl": "title",
        }
    )
    if results['count'] > 0:
        return True
    return False


def _load_download_rules_for(pkg):
    """Try to get dataset-specific rules (first by title, then name)

    Looks in dataset_configs folder for a file named after the dataset.

    Args:
        pkg (dict): CKAN package dictionary of metadata

    Returns:
        dict of parsed rules configuration or an empty dict if no
        per-dataset config exists or loading fails.

    """
    rules_dir = path.join(
        path.dirname(__file__), 'public', 'dataset_configs'
    )
    if not path.isdir(rules_dir):
        LOGGER.debug(f"dataset_configs not found at: {rules_dir}")

    potential_config_path = path.join(rules_dir, f"{pkg.get('title')}.yml")
    try:
        if path.exists(potential_config_path):
            with open(potential_config_path, 'r') as f:
                data = yaml.safe_load(f) or {}
                LOGGER.info(f"Loaded rules for: {potential_config_path}")
                return data
    except Exception:
        LOGGER.exception(f"Failed loading rules from {potential_config_path}")

    return {}


def _apply_rule_list(rule_list, base, ext, url):
    """Evaluate first-match-wins

    Args:
        rule_list (list[dict]): list of rules read from config if config yaml
            for the datapackage exists, otherwise will be empty list. List will
            contain dictionaries of rules like:
            {'match': {'path_glob': 'some_path'},
             'allow': True, 'reason': 'some reason'}
        base (str): basename of source (file or folder), e.g., 'foo.tif'
            or 'my_dir'
        ext (str): file extension (e.g., '.tif') (could be empty if directory)
        url (str): original download url to where source file lives. Will
            be empty if source is a directory and url inferred via
            ``get_directory_url``.

    Returns:
        dict: {'allowed': bool, 'reason': str} or None

    """
    for rule in rule_list:
        m = (rule.get('match') or {})
        if _match_rule(m, base, ext, url):
            return {'allowed': bool(rule.get('allow', True)),
                    'reason': rule.get('reason', ''),
                    'url': url}
    return None


def _match_rule(m, base, ext, url):
    """Check whether a single rule's match clause applies.

    ``m`` can have any of these keys:
      - ``path_glob``: fnmatch pattern tested against ``base`` (used
            for directory names or simple file patterns).
      - ``name_regex``: Python regex tested against ``base``. Note that
            invalid regex patterns are treated as non-matches (return False)
      - ``ext_any``: list of extensions (with dots) that must contain ``ext``.

    Args:
        m (dict): Match clause from a rule (may be empty).
        base (str): Basename of the source (file or directory).
        ext (str): File extension including dot, or empty for directories.
        url (str): URL to download file

    Returns:
        bool: ``True`` if the rule matches; ``False`` otherwise.

    """
    pg = m.get('path_glob')
    if pg:
        if not url and not fnmatch.fnmatch(base, pg):
            return False
        elif url and not fnmatch.fnmatch(url, pg):
            return False
    rx = m.get('name_regex')
    if rx:
        try:
            if not re.search(rx, base):
                return False
        except re.error:
            return False

    ex = m.get('ext_any')
    if ex and ext.lower() not in [e.lower() for e in ex]:
        return False
    return True


def get_directory_url(node, target_name):
    """Infer a folder ZIP URL from a directory node in the sources tree.

    If ``node`` (or any of its descendants) is a directory whose ``name``
    equals ``target_name``, we try to infer a `.zip` URL by:
      1) taking the first child's ``url``,
      2) stripping the final path segment (child filename),
      3) appending `.zip`.

    This ultimately allows us to click the "Download" icon for a folder and
    have it point to a pre-zipped archive published at the same path.

    Args:
        node (dict): Source tree node, e.g. the object passed from the Jinja
            template (must include ``type``, ``name``, optional ``children``).
        target_name (str): Basename of directory to find (not full path).

    Returns:
        Inferred ZIP URL if derivable; otherwise ``None``.
    """
    if node["type"] == "directory":
        if node["name"] == target_name:
            # infer URL from first child's URL
            for child in node.get("children", []):
                if "url" in child:
                    # Drop the filename and change dir path to zip path
                    return "/".join(child["url"].split("/")[:-1])+".zip"

        # recurse into children
        for child in node.get("children", []):
            result = get_directory_url(child, target_name)
            if result:
                return result
    return None


def get_file_downloadability(pkg, source):
    """
    Check if a 'source' (file/dir in sources_list.html) is downloadable.

    Loads per-dataset rules for pkg via `_load_download_rules_for`
    and evaluates them with `_apply_rule_list`. If a folder is allowed,
    this will also attempt to populate `url` with an inferred folder
    ZIP URL via `get_directory_url`. If no per-dataset config is found,
    uses ``defaults.allow`` (evaluates to `True` when absent).

    Args:
        pkg (dict): CKAN package dictionary
        source (dict | object): source node (as passed from Jinja template).
            Should have keys/attributes `name`, `url`, and `type`.

    Returns:
        dict: {'allowed': bool, 'reason': '...'} which specified whether and
            why an item can be downloaded and if so, what url to use.

    """
    rules = _load_download_rules_for(pkg) or {}

    try:
        allowed_default = bool(rules['defaults']['allow'])
    except KeyError:
        # When `allow` not in `rules['defaults']`
        allowed_default = True
    except TypeError:
        # When `rules['defaults'] = False` (this is not preferred setup)
        allowed_default = bool(rules['defaults'])

    # Extract fields to match on
    if isinstance(source, dict):
        name = source.get('name')
        url = source.get('url')
        filetype = source.get('type')
    else:
        raise Exception('Invalid configuration; source is not a dict')

    ext = path.splitext(name)[1].lower()
    base = path.basename(name)

    verdict = _apply_rule_list((rules.get('rules') or []), base, ext, url)
    if verdict is not None:
        if verdict['allowed'] and filetype == 'directory':
            verdict['url'] = get_directory_url(source, name)
        return verdict

    return {'allowed': allowed_default, 'reason': 'default', 'url': url}


def get_download_url(resource_url):
    if resource_url.lower().endswith('.shp'):
        return '.'.join([resource_url.rsplit('.', 1)[0], 'zip'])
    return resource_url


def get_helpers():
    return {
        'natcap_get_ext': get_ext,
        'natcap_get_filename': get_filename,
        'natcap_get_resource_type_icon_slug': get_resource_type_icon_slug,
        'natcap_get_resource_type_facet_label': get_resource_type_facet_label,
        'natcap_get_resource_type_label': get_resource_type_label,
        'natcap_get_topic_keywords': get_topic_keywords,
        'natcap_get_invest_models': get_invest_models,
        'natcap_get_all_search_facets': get_all_search_facets,
        'natcap_show_icon': show_icon,
        'natcap_show_resource': show_resource,
        'natcap_parse_json': parse_json,
        'natcap_get_file_downloadability': get_file_downloadability,
        'natcap_get_download_url': get_download_url,
        'natcap_get_collection_name': get_collection_name,
        'natcap_get_collection_name_url': get_collection_name_url,
        'natcap_collection_lulc_biotable': collection_lulc_biotable,
        'natcap_collection_has_datasets': collection_has_datasets,
        # helpers for ckanext-scheming:
        'natcap_get_place_tags': get_place_tags,
        'natcap_get_collection_tags': get_collection_tags,
    }
