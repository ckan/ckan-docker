import ckan.plugins.toolkit as toolkit


def _site_url(site_url=None):
    return (site_url or toolkit.config.get("ckan.site_url", "")).rstrip("/")


def catalog_ttl_url(site_url=None):
    return f"{_site_url(site_url)}/catalog.ttl"


def dataset_ttl_url(site_url_or_dataset=None, dataset=None):
    if dataset is None:
        dataset = site_url_or_dataset
        site_url = None
    else:
        site_url = site_url_or_dataset
    return f"{_site_url(site_url)}/dataset/{dataset['name']}.ttl"
