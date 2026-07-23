#!/usr/bin/env python3
"""Validate that rendered Kubernetes workloads carry the restricted profile."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

EXPECTED_UIDS = {
    "postgres": 70,
    "redis": 999,
    "solr": 8983,
    "datapusher": 92,
    "ckan": 503,
    "initialize": 503,
    "reindex": 503,
    "wait-for-initialization": 70,
}


def fail(message: str) -> None:
    raise SystemExit(message)


def check_container(container: dict, doc_name: str, kind: str) -> None:
    name = container.get("name")
    security = container.get("securityContext") or {}
    expected_uid = EXPECTED_UIDS.get(name)
    if expected_uid is None:
        fail(f"{doc_name}: {kind} {name} has no reviewed runAsUser")

    required = [
        ("allowPrivilegeEscalation", False),
        ("runAsNonRoot", True),
    ]
    for field, expected in required:
        if security.get(field) is not expected:
            fail(f"{doc_name}: {kind} {name} missing {field}={expected}")

    capabilities = security.get("capabilities") or {}
    if capabilities.get("drop") != ["ALL"]:
        fail(f"{doc_name}: {kind} {name} missing capabilities.drop=[ALL]")

    if security.get("runAsUser") != expected_uid:
        fail(f"{doc_name}: {kind} {name} missing runAsUser={expected_uid}")


def check_doc(doc: dict, source: Path) -> None:
    kind = doc.get("kind")
    metadata = doc.get("metadata") or {}
    spec = doc.get("spec") or {}
    name = metadata.get("name", "<unnamed>")
    doc_name = f"{source.name}:{kind}/{name}"

    template = None
    if kind in {"Deployment", "StatefulSet", "Job"}:
        template = (spec.get("template") or {}).get("spec") or {}
    if template is None:
        return

    pod_security = template.get("securityContext") or {}
    seccomp = pod_security.get("seccompProfile") or {}
    if seccomp.get("type") != "RuntimeDefault":
        fail(f"{doc_name}: pod spec missing seccompProfile.type=RuntimeDefault")

    for container in template.get("containers") or []:
        check_container(container, doc_name, "container")
    for container in template.get("initContainers") or []:
        check_container(container, doc_name, "initContainer")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        fail("usage: validate_restricted_profile.py RENDERED_YAML...")

    for path_str in argv[1:]:
        path = Path(path_str)
        result = subprocess.run(
            [
                "kubectl",
                "create",
                "--dry-run=client",
                "-f",
                str(path),
                "-o",
                "json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        decoder = json.JSONDecoder()
        offset = 0
        while offset < len(result.stdout):
            doc, offset = decoder.raw_decode(result.stdout, offset)
            check_doc(doc, path)
            while offset < len(result.stdout) and result.stdout[offset].isspace():
                offset += 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
