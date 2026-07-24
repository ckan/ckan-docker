#!/usr/bin/env python3
"""Prove direct multipart object upload followed by CKAN registration.

Run this inside the CKAN service container. The dataset always remains private
so access, integrity, and DataPusher results can be checked before publication.
"""

from __future__ import annotations

import hashlib
import os
import re
import sys
import uuid
from pathlib import Path

import boto3
import requests
from boto3.s3.transfer import TransferConfig


def required(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if not value:
        raise SystemExit(f"{name} is required")
    return value


def action(site_url: str, token: str, name: str, payload: dict) -> dict:
    response = requests.post(
        f"{site_url.rstrip('/')}/api/3/action/{name}",
        headers={"Authorization": token},
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    body = response.json()
    if not body.get("success"):
        raise RuntimeError(f"{name} failed: {body}")
    return body["result"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} FILE")
    source = Path(sys.argv[1]).resolve()
    if not source.is_file():
        raise SystemExit(f"not a file: {source}")

    site_url = required("CKAN_INTERNAL_URL", "http://ckan:5000")
    token = required("CKAN_API_TOKEN")
    endpoint = required("CKANEXT__S3FILESTORE__HOST_NAME", "http://minio:9000")
    access_key = required("CKANEXT__S3FILESTORE__AWS_ACCESS_KEY_ID")
    secret_key = required("CKANEXT__S3FILESTORE__AWS_SECRET_ACCESS_KEY")
    bucket = required("CKANEXT__S3FILESTORE__AWS_BUCKET_NAME")
    region = required("CKANEXT__S3FILESTORE__REGION_NAME", "us-east-1")

    suffix = uuid.uuid4().hex[:10]
    owner_org = os.environ.get("CKAN_TEST_OWNER_ORG")
    if not owner_org:
        organization = action(
            site_url,
            token,
            "organization_create",
            {
                "name": f"minio-spike-{suffix}",
                "title": f"MinIO spike {suffix}",
            },
        )
        owner_org = organization["id"]
    package = action(
        site_url,
        token,
        "package_create",
        {
            "name": f"minio-direct-upload-{suffix}",
            "title": f"MinIO direct-upload proof {suffix}",
            "notes": "Ephemeral private dataset created by the MinIO spike.",
            "private": True,
            "owner_org": owner_org,
        },
    )

    # Generate the CKAN resource UUID client-side so the deterministic object
    # key is known before resource_create. A placeholder resource would trigger
    # DataPusher before its URL can be patched to the uploaded object.
    resource_id = str(uuid.uuid4())
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", source.name)
    object_key = f"resources/{resource_id}/{safe_name}"

    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
        config=boto3.session.Config(
            signature_version="s3v4", s3={"addressing_style": "path"}
        ),
    )
    transfer = TransferConfig(
        multipart_threshold=16 * 1024 * 1024,
        multipart_chunksize=16 * 1024 * 1024,
        max_concurrency=4,
    )
    client.upload_file(str(source), bucket, object_key, Config=transfer)

    try:
        result = action(
            site_url,
            token,
            "resource_create",
            {
                "id": resource_id,
                "package_id": package["id"],
                "name": source.name,
                "url": source.name,
                "url_type": "upload",
                "format": source.suffix.lstrip(".").upper(),
                "size": source.stat().st_size,
                "hash": sha256(source),
            },
        )
    except Exception:
        client.delete_object(Bucket=bucket, Key=object_key)
        raise
    print(f"registered private resource: {result.get('url')}")

    print(f"dataset remains private: {package['name']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
