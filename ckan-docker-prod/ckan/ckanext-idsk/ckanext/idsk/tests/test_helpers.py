from ckanext.idsk.helpers import catalog_ttl_url, dataset_ttl_url


def test_catalog_ttl_url_uses_site_url_without_trailing_slash():
    assert catalog_ttl_url("https://example.gov.sk/") == "https://example.gov.sk/catalog.ttl"


def test_dataset_ttl_url_uses_dataset_name():
    dataset = {"name": "test-dataset"}

    assert dataset_ttl_url("https://example.gov.sk/", dataset) == "https://example.gov.sk/dataset/test-dataset.ttl"
