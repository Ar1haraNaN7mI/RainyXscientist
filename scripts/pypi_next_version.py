#!/usr/bin/env python3
"""Resolve next PyPI-safe version and optionally write pyproject.toml (patch bump if taken)."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
VERSION_RE = re.compile(r'^version\s*=\s*"([^"]+)"', re.MULTILINE)


def _get_project_name(text: str) -> str:
    in_project = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "[project]":
            in_project = True
            continue
        if in_project and stripped.startswith("["):
            break
        if in_project and stripped.startswith("name"):
            m = re.match(r'^\s*name\s*=\s*"([^"]+)"\s*$', line)
            if m:
                return m.group(1)
    raise SystemExit("Could not read [project] name from pyproject.toml")


def _get_version(text: str) -> str:
    m = VERSION_RE.search(text)
    if not m:
        raise SystemExit("Could not read version in pyproject.toml")
    return m.group(1).strip()


def _bump_patch(ver: str) -> str:
    parts = ver.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise SystemExit(
            f"version must be semantic MAJOR.MINOR.PATCH (digits), got: {ver!r}"
        )
    major, minor, patch = (int(x) for x in parts)
    return f"{major}.{minor}.{patch + 1}"


def _fetch_pypi_releases(pypi_name: str) -> set[str]:
    url = f"https://pypi.org/pypi/{pypi_name}/json"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Rxscientist-pypi_next_version/1.0 (release script)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return set()
        raise
    return set((data or {}).get("releases") or {})


def _resolve_next(
    pypi_releases: set[str],
    start: str,
) -> str:
    ver = start
    while ver in pypi_releases:
        ver = _bump_patch(ver)
    return ver


def _write_version(text: str, new_ver: str) -> str:
    if _get_version(text) == new_ver:
        return text
    out, n = VERSION_RE.subn(f'version = "{new_ver}"', text, count=1)
    if n != 1:
        raise SystemExit("Failed to update version in pyproject.toml")
    return out


def main() -> int:
    write = "--write" in sys.argv
    raw = PYPROJECT.read_text(encoding="utf-8")
    pypi_name = _get_project_name(raw)
    current = _get_version(raw)
    releases = _fetch_pypi_releases(pypi_name)
    nxt = _resolve_next(releases, current)
    if write and nxt != current:
        PYPROJECT.write_text(_write_version(raw, nxt), encoding="utf-8", newline="\n")
    gho = os.environ.get("GITHUB_OUTPUT", "")
    if "--github-output" in sys.argv and gho:
        with open(gho, "a", encoding="utf-8") as f:
            f.write(f"version={nxt}\n")
            f.write(f"previous_version={current}\n")
            f.write(f"bump_needed={str(nxt != current).lower()}\n")
    if write:
        print(f"version={nxt} (wrote: {nxt != current})")
    else:
        print(nxt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
