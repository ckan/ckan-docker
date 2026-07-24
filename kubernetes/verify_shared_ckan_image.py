#!/usr/bin/env python3
"""Verify both rendered overlays resolve to the same immutable CKAN image."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

IMAGE_RE = re.compile(r"^.+@sha256:[0-9a-f]{64}$")
CKAN_CONTAINERS = {"ckan", "initialize", "reindex"}


def fail(message: str) -> None:
    raise SystemExit(message)


def image_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    with path.open("r", encoding="utf-8") as handle:
        for doc in yaml.safe_load_all(handle):
            if not doc:
                continue
            template = (doc.get("spec") or {}).get("template") or {}
            pod_spec = template.get("spec") or {}
            for container in pod_spec.get("containers") or []:
                name = container.get("name")
                if name in CKAN_CONTAINERS:
                    if name in values:
                        fail(f"{path}: duplicate CKAN container {name}")
                    values[name] = container.get("image") or ""
    return values


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        fail("usage: verify_shared_ckan_image.py INT_RENDERED_YAML PROD_RENDERED_YAML")

    int_images = image_values(Path(argv[1]))
    prod_images = image_values(Path(argv[2]))

    if set(int_images) != CKAN_CONTAINERS:
        fail(f"{argv[1]}: CKAN workload set is incomplete: {sorted(int_images)}")
    if set(prod_images) != CKAN_CONTAINERS:
        fail(f"{argv[2]}: CKAN workload set is incomplete: {sorted(prod_images)}")

    int_refs = set(int_images.values())
    prod_refs = set(prod_images.values())
    if len(int_refs) != 1:
        fail(f"{argv[1]}: CKAN images are not identical: {sorted(int_refs)}")
    if len(prod_refs) != 1:
        fail(f"{argv[2]}: CKAN images are not identical: {sorted(prod_refs)}")

    int_ref = next(iter(int_refs))
    prod_ref = next(iter(prod_refs))
    if int_ref != prod_ref:
        fail(
            "rendered overlays do not share the same CKAN image: "
            f"{int_ref} != {prod_ref}"
        )

    if not IMAGE_RE.match(int_ref):
        fail(f"rendered CKAN image is not immutable: {int_ref}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
