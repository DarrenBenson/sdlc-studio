#!/usr/bin/env python3
"""Check that the skill version is consistent across its authoritative homes.

A skill-development CI tool (lives in tools/). Extracts the version by
structure from exactly five places - never by repo-wide grep, so
incidental version mentions in prose are ignored:

1. package.json                          -> "version"
2. templates/version.yaml                -> skill_version
3. SKILL.md frontmatter                  -> metadata.version
4. README.md                             -> first "**Version:** X.Y.Z" or "version X.Y.Z" match in the head
5. CHANGELOG.md                          -> topmost released "## [X.Y.Z]" heading
                                            (an [Unreleased] section above it is fine)

The CHANGELOG check is advisory between releases (the topmost released
heading lags until the release PR) unless --strict is passed, when it
must match too.

Usage:
    python3 tools/check_versions.py [--root DIR] [--strict]

Exits non-zero on any mismatch or unparseable location.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_DIR = ".claude/skills/sdlc-studio"

SEMVER = r"(\d+\.\d+\.\d+)"


def from_package_json(root: Path) -> str | None:
    try:
        return json.loads((root / "package.json").read_text(encoding="utf-8")).get("version")
    except (OSError, json.JSONDecodeError):
        return None


def from_version_yaml(root: Path) -> str | None:
    path = root / SKILL_DIR / "templates" / "version.yaml"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(rf'^skill_version:\s*"?{SEMVER}"?', text, re.M)
    return m.group(1) if m else None


def from_skill_md(root: Path) -> str | None:
    path = root / SKILL_DIR / "SKILL.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    # frontmatter block only
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    m = re.search(rf'^\s+version:\s*"?{SEMVER}"?', parts[1], re.M)
    return m.group(1) if m else None


def from_readme(root: Path) -> str | None:
    try:
        head = (root / "README.md").read_text(encoding="utf-8")[:4000]
    except OSError:
        return None
    m = re.search(rf"\*\*Version:?\*\*:?\s*v?{SEMVER}", head) or \
        re.search(rf"[Vv]ersion\s+v?{SEMVER}", head) or \
        re.search(rf"\bv{SEMVER}\b", head)
    return m.group(1) if m else None


def from_changelog(root: Path) -> str | None:
    try:
        text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(rf"^## \[{SEMVER}\]", text, re.M)
    return m.group(1) if m else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repo root")
    parser.add_argument("--strict", action="store_true",
                        help="CHANGELOG topmost release must match too (release gate)")
    args = parser.parse_args(argv)
    root = Path(args.root)

    versions = {
        "package.json": from_package_json(root),
        "templates/version.yaml skill_version": from_version_yaml(root),
        "SKILL.md metadata.version": from_skill_md(root),
        "README.md": from_readme(root),
    }
    changelog = from_changelog(root)

    errors = [f"{name}: version not found" for name, v in versions.items() if v is None]
    found = {v for v in versions.values() if v is not None}
    if len(found) > 1:
        detail = ", ".join(f"{name}={v}" for name, v in versions.items())
        errors.append(f"version mismatch: {detail}")

    if args.strict:
        if changelog is None:
            errors.append("CHANGELOG.md: no released [x.y.z] heading found")
        elif found and changelog not in found:
            errors.append(f"CHANGELOG.md topmost release {changelog} != {sorted(found)[0]}")

    for err in errors:
        print(f"VERSIONS: {err}", file=sys.stderr)
    if not errors:
        v = sorted(found)[0] if found else "unknown"
        note = "" if args.strict else f" (CHANGELOG topmost release: {changelog or 'none'}, advisory)"
        print(f"Version {v} consistent across authoritative locations.{note}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
