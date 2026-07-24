#!/usr/bin/env python3
"""Static and live-render validation for the ckanext-s3filestore MinIO spike.

Runs without a real cloud account. Always performs static checks against the
rendered/raw Compose and Dockerfile contract. If a Compose provider is
available on PATH, also renders the merged config and re-checks against it.

Usage: python3 data-at-spark/minio-spike/validate.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SPIKE_DIR = Path(__file__).resolve().parent
DATA_AT_SPARK_DIR = SPIKE_DIR.parent

EXPECTED_S3FILESTORE_COMMIT = "e972ae3c36489dcfc716f75063ac64c13cde1146"
EXPECTED_S3FILESTORE_REPO = "github.com/keitaroinc/ckanext-s3filestore"

COMPOSE_FILES = [
    REPO_ROOT / "docker-compose.yml",
    DATA_AT_SPARK_DIR / "compose.yml",
    SPIKE_DIR / "compose.yml",
]

failures: list[str] = []
warnings: list[str] = []


def fail(message: str) -> None:
    failures.append(message)


def warn(message: str) -> None:
    warnings.append(message)


def check_dockerfile_pin() -> None:
    dockerfile = (DATA_AT_SPARK_DIR / "Dockerfile").read_text()
    if EXPECTED_S3FILESTORE_REPO not in dockerfile:
        fail(f"data-at-spark/Dockerfile does not reference {EXPECTED_S3FILESTORE_REPO}")
    if f"CKANEXT_S3FILESTORE_COMMIT={EXPECTED_S3FILESTORE_COMMIT}" not in dockerfile:
        fail(
            "data-at-spark/Dockerfile ARG default does not pin the exact "
            f"validated commit {EXPECTED_S3FILESTORE_COMMIT}"
        )
    if "@${CKANEXT_S3FILESTORE_COMMIT}" not in dockerfile:
        fail("data-at-spark/Dockerfile does not install s3filestore pinned to the ARG commit")


def check_compose_arg_default() -> None:
    compose = (DATA_AT_SPARK_DIR / "compose.yml").read_text()
    if EXPECTED_S3FILESTORE_COMMIT not in compose:
        fail("data-at-spark/compose.yml build-arg default does not match the pinned commit")


def check_no_committed_secrets() -> None:
    # No committed .env files (only .env.example) anywhere ckanext-s3filestore
    # config is introduced, and no Kubernetes Secret manifests in this phase.
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "data-at-spark/.env",
         "data-at-spark/minio-spike/.env"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        fail("a real .env file is tracked; only .env.example files may be committed")

    for path in [SPIKE_DIR / "compose.yml"]:
        text = path.read_text(errors="ignore")
        if "kind: Secret" in text:
            fail(f"{path.relative_to(REPO_ROOT)} commits a Kubernetes Secret manifest")


def check_spike_env_example() -> None:
    env_example = (SPIKE_DIR / ".env.example").read_text()
    required_keys = [
        "MINIO_ROOT_USER",
        "MINIO_ROOT_PASSWORD",
        "MINIO_BUCKET_NAME",
        "MINIO_REGION",
        "DATA_AT_SPARK_CKAN_PLUGINS_WITH_S3FILESTORE",
    ]
    for key in required_keys:
        if key not in env_example:
            fail(f"data-at-spark/minio-spike/.env.example missing {key}")
    if "s3filestore" not in env_example:
        fail("data-at-spark/minio-spike/.env.example plugin list does not include s3filestore")


def load_spike_compose_raw() -> dict:
    return yaml.safe_load((SPIKE_DIR / "compose.yml").read_text())


def check_raw_spike_compose() -> None:
    doc = load_spike_compose_raw()
    services = doc.get("services", {})

    for name in ("minio", "minio-init", "ckan"):
        if name not in services:
            fail(f"data-at-spark/minio-spike/compose.yml missing service {name!r}")
    if failures:
        return

    ckan_env = services["ckan"].get("environment", {})
    if ckan_env.get("CKANEXT__S3FILESTORE__ACL") != "private":
        fail("ckan.CKANEXT__S3FILESTORE__ACL must be 'private'")
    if ckan_env.get("CKANEXT__S3FILESTORE__ADDRESSING_STYLE") != "path":
        fail("ckan.CKANEXT__S3FILESTORE__ADDRESSING_STYLE must be 'path' for MinIO")
    host_name = ckan_env.get("CKANEXT__S3FILESTORE__HOST_NAME", "")
    if "minio" not in host_name:
        fail("ckan.CKANEXT__S3FILESTORE__HOST_NAME must point at the local minio service")
    if "CKANEXT__S3FILESTORE__AWS_USE_SSL" in ckan_env:
        fail("ckan config contains unsupported AWS_USE_SSL; endpoint scheme controls TLS")

    depends_on = services["ckan"].get("depends_on", {})
    if "minio-init" not in depends_on:
        fail("ckan service must depend_on minio-init so the bucket exists before boot")
    elif depends_on["minio-init"].get("condition") != "service_completed_successfully":
        fail("ckan's dependency on minio-init must wait for service_completed_successfully")

    minio_init_env = services["minio-init"].get("environment", {})
    if "MINIO_BUCKET_NAME" not in minio_init_env:
        fail("minio-init service must receive MINIO_BUCKET_NAME to create the bucket deterministically")


def check_init_script() -> None:
    script = (SPIKE_DIR / "init-bucket.sh").read_text()
    if "mc mb" not in script:
        fail("init-bucket.sh does not create the bucket (mc mb)")
    if "mc anonymous set none" not in script:
        fail("init-bucket.sh does not enforce a private/no-anonymous bucket policy")


def check_direct_upload_harness() -> None:
    harness = (SPIKE_DIR / "direct_upload.py").read_text()
    required_fragments = [
        "TransferConfig",
        "upload_file(",
        "resources/{resource_id}/{safe_name}",
        '"url_type": "upload"',
        '"resource_create"',
    ]
    for fragment in required_fragments:
        if fragment not in harness:
            fail(f"direct_upload.py missing required flow fragment: {fragment}")


def check_live_render() -> None:
    compose_bin = shutil.which("podman")
    if compose_bin is None:
        warn("podman not found on PATH; skipped live `compose config` render")
        return

    args = ["podman", "compose"]
    args += ["--env-file", str(REPO_ROOT / ".env.example")]
    for compose_file in COMPOSE_FILES:
        args += ["-f", str(compose_file)]
    args += ["config"]

    try:
        result = subprocess.run(
            args, cwd=REPO_ROOT, capture_output=True, text=True, timeout=60
        )
    except Exception as exc:  # noqa: BLE001 - expose a failed local validation
        fail(f"live `podman compose config` render errored: {exc}")
        return

    if result.returncode != 0:
        fail(f"live `podman compose config` render failed: {result.stderr.strip()[:500]}")
        return

    rendered = yaml.safe_load(result.stdout)
    ckan_build_args = (
        rendered.get("services", {}).get("ckan", {}).get("build", {}).get("args", {})
    )
    if isinstance(ckan_build_args, list):
        ckan_build_args = dict(
            item.split("=", 1) for item in ckan_build_args if "=" in item
        )
    pinned = ckan_build_args.get("CKANEXT_S3FILESTORE_COMMIT")
    if pinned != EXPECTED_S3FILESTORE_COMMIT:
        fail(
            "rendered ckan build arg CKANEXT_S3FILESTORE_COMMIT="
            f"{pinned!r}, expected {EXPECTED_S3FILESTORE_COMMIT!r}"
        )


def main() -> int:
    check_dockerfile_pin()
    check_compose_arg_default()
    check_no_committed_secrets()
    check_spike_env_example()
    check_raw_spike_compose()
    check_init_script()
    check_direct_upload_harness()
    check_live_render()

    for message in warnings:
        print(f"WARN: {message}")
    if failures:
        for message in failures:
            print(f"FAIL: {message}")
        print(f"\n{len(failures)} check(s) failed.")
        return 1

    print("All static checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
