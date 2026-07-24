#!/usr/bin/env python3
"""Substitute an immutable Data@Spark image into rendered overlays."""

from __future__ import annotations

import re
import sys
from pathlib import Path

IMAGE_RE = re.compile(r"^.+@sha256:[0-9a-f]{64}$")


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        raise SystemExit(
            "usage: substitute_ckan_image.py IMAGE_REF RENDERED_YAML..."
        )

    image_ref = argv[1]
    if not IMAGE_RE.match(image_ref):
        raise SystemExit(f"CKAN image is not immutable: {image_ref}")

    source_ref = "docker.io/ckan/ckan-base:2.11.5"
    for path_str in argv[2:]:
        path = Path(path_str)
        text = path.read_text(encoding="utf-8")
        if text.count(source_ref) != 3:
            raise SystemExit(
                f"{path}: expected exactly 3 CKAN image references to promote"
            )
        path.write_text(text.replace(source_ref, image_ref), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
