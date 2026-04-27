#!/usr/bin/env python3
"""Local pre-commit hook: block accidental commits of personal PII.

Allowed in GIS data files (GeoJSON, CSV, Shapefile, etc.) since those are
public datasets, but blocked in source code, docs, and config.
"""

import re
import sys

SKIP_PATHS = {
    "scripts/check_pii.py",
    "LICENSE",
    "LICENSE.txt",
    "LICENSE.md",
}

BLOCKLIST = [
    (re.compile(r"82\s+Grand(?:\s+St(?:reet)?)?\.?", re.IGNORECASE), "address"),
    (re.compile(r"Emma\s+Dalton", re.IGNORECASE), "name"),
    (re.compile(r"Cristos\s+Lianides(?:[-\s]Chin)?", re.IGNORECASE), "name"),
    (re.compile(r"Lianides(?:[-\s]Chin)?", re.IGNORECASE), "name"),
]


def main() -> int:
    fail = False
    for path in sys.argv[1:]:
        # Skip metadata / legal files that legitimately contain names
        if re.search(r"LICEN[CS]E(-?\w+)?\.(md|txt|rst)?$", path, re.I):
            continue
        if path in SKIP_PATHS:
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception:
            continue
        for pattern, kind in BLOCKLIST:
            for match in pattern.finditer(content):
                line_no = content[: match.start()].count("\n") + 1
                print(f"ERROR: {kind!r} PII detected in {path}:{line_no}")
                snippet = match.group(0).replace("\n", " ")
                print(f'       "{snippet}"')
                print(
                    "       If this is intentional (e.g., inside a public data file), "
                    "exclude the file with `exclude:` in .pre-commit-config.yaml"
                )
                fail = True
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
