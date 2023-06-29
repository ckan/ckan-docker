import datetime
import requests
from urllib.parse import quote
import logging


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
    list_fields = ["command_list"]
    for l in list_fields:
        mirror_data[l] = ["command_1", "command_2", "command_3"]
    json_fields = ["source_dataset"]
    for j in json_fields:
        mirror_data[j] = {"id": 1}
    add_dataset(api_key, base_url, dataset_id, **mirror_data)


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
    dataset_id = "dataset_demo"
    # add_dataset(api_key, base_url, dataset_id, title="Demo Dataset", type="dataset")
    # add_mirror_dataset(api_key, base_url, dataset_id)
    show_package(base_url, dataset_id)
