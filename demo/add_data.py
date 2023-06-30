import datetime
import requests
from urllib.parse import quote
import logging


def add_transposition_dataset(api_key: str, base_url: str, dataset_id: str) -> int:
    transposition_data = {
        "title": dataset_id.capitalize(),
        "type": "aorc_TranspositionDataset",
        "url": quote(dataset_id),
    }
    simple_fields = [
        "spatial_resolution",
        "docker_file",
        "compose_file",
        "docker_image",
        "git_repo",
        "docker_repo",
        "commit_hash",
        "digest_hash",
        "transposition_region_name",
        "transposition_region_wkt",
        "watershed_region_name",
        "watershed_region_wkt",
        "max_precipitation_point_name",
        "max_precipitation_point_wkt",
        "image",
        "cell_count",
        "mean_precipitation",
        "max_precipitation",
        "min_precipitation",
        "sum_precipitation",
        "normalized_mean_precipitation",
    ]
    for simple in simple_fields:
        transposition_data[simple] = "test"
    dt_fields = ["last_modified", "start_time", "end_time"]
    for dt in dt_fields:
        transposition_data[dt] = datetime.datetime.today().isoformat()
    transposition_data["composite_normalized_datasets"] = {
        "https://example.org/aorc_CompositeDataset/dataset_1": None,
        "https://example.org/aorc_CompositeDataset/dataset_2": "https://example.org/atlas14_data/dataset_2",
        "https://example.org/aorc_CompositeDataset/dataset_3": None,
    }
    transposition_data["command_list"] = [
        "command_1",
        "command_2",
        "command_3",
    ]
    return add_dataset(api_key, base_url, dataset_id, **transposition_data)


def add_composite_dataset(api_key: str, base_url: str, dataset_id: str) -> int:
    composite_data = {"title": dataset_id.capitalize(), "type": "aorc_CompositeDataset", "url": quote(dataset_id)}
    simple_fields = [
        "spatial_resolution",
        "docker_file",
        "compose_file",
        "docker_image",
        "git_repo",
        "docker_repo",
        "commit_hash",
        "digest_hash",
        "location_name",
        "location_wkt",
    ]
    for simple in simple_fields:
        composite_data[simple] = "test"
    dt_fields = ["last_modified", "start_time", "end_time"]
    for dt in dt_fields:
        composite_data[dt] = datetime.datetime.today().isoformat()
    composite_data["mirror_datasets"] = [
        "https://example.org/aorc_MirrorDataset/dataset_1",
        "https://example.org/aorc_MirrorDataset/dataset_2",
        "https://example.org/aorc_MirrorDataset/dataset_3",
    ]
    composite_data["command_list"] = [
        "command_1",
        "command_2",
        "command_3",
    ]
    return add_dataset(api_key, base_url, dataset_id, **composite_data)


def add_mirror_dataset(api_key: str, base_url: str, dataset_id: str) -> int:
    mirror_data = {"title": dataset_id.capitalize(), "type": "aorc_MirrorDataset", "url": quote(dataset_id)}
    simple_fields = [
        "spatial_resolution",
        "docker_file",
        "compose_file",
        "docker_image",
        "git_repo",
        "docker_repo",
        "commit_hash",
        "digest_hash",
        "temporal_resolution",
        "rfc_alias",
        "rfc_full_name",
        "rfc_parent_organization",
        "rfc_wkt",
    ]
    for simple in simple_fields:
        mirror_data[simple] = "test"
    dt_fields = ["last_modified", "start_time", "end_time"]
    for dt in dt_fields:
        mirror_data[dt] = datetime.datetime.today().isoformat()
    mirror_data["command_list"] = ["command_1", "command_2", "command_3"]
    json_fields = ["source_dataset"]
    for j in json_fields:
        mirror_data[j] = {"id": 1}
    return add_dataset(api_key, base_url, dataset_id, **mirror_data)


def add_dataset(api_key: str, base_url: str, dataset_id: str, **kwargs) -> int:
    url = f"{base_url}/api/3/action/package_create"
    headers = {"Authorization": api_key, "Content-Type": "application/json"}
    data = {
        "name": dataset_id,
        "owner_org": "aorc",
        "title": "your_dataset_title_here",
        "notes": "your_dataset_description_here",
        "private": False,
    }
    data.update(kwargs)
    response = requests.post(url, headers=headers, json=data)
    logging.info(response.json())
    return response.status_code


def delete_data(api_key: str, base_url: str, dataset_id: str) -> int:
    url = f"{base_url}/api/3/action/package_delete?id={dataset_id}"
    headers = {"Authorization": api_key}
    response = requests.post(url, headers=headers)
    logging.info(response.json())
    return response.status_code


def list_packages(base_url: str) -> list:
    url = f"{base_url}/api/3/action/package_list"
    response = requests.get(url)
    logging.info(response.json())
    return []


def show_package(base_url: str, dataset_id: str) -> dict:
    url = f"{base_url}/api/3/action/package_show?id={dataset_id}"
    response = requests.get(url)
    logging.info(response.json())
    return response.status_code


if __name__ == "__main__":
    logging.basicConfig(handlers=[logging.StreamHandler()], level=logging.INFO)
    api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJDalRlaUVtTWc5TlRsR1g0SWNudDlaNGxGMWxTUWcxRW1Ta3l0aTVVMW5nIiwiaWF0IjoxNjg3ODk2NzI3fQ.7dzvPq9BXAnVmA9_82SFQ9nwuz7qSdqjYrZRe5BZlSY"
    base_url = "http://localhost:5000/"
    dataset_id = "transposition_dataset_demo"
    # add_dataset(api_key, base_url, dataset_id, title="Demo Dataset", type="dataset")
    # add_mirror_dataset(api_key, base_url, dataset_id)
    # add_composite_dataset(api_key, base_url, dataset_id)
    add_transposition_dataset(api_key, base_url, dataset_id)
    show_package(base_url, dataset_id)
