import requests
import logging


def add_data(api_key: str, base_url: str, dataset_id: str, **kwargs) -> int:
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
    dataset_id = "mirror_dataset_demo"
    add_data(api_key, base_url, dataset_id, title="Demo Mirror Dataset", type="aorc:MirrorDataset")
    show_package(base_url, dataset_id)
