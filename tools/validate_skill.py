#!/usr/bin/env python3
"""Validate SKILL.md frontmatter against the Agent Skills open standard.

A skill-development CI tool (lives in tools/, not the runtime scripts/
directory). Implements the agentskills.io specification subset this repo
cares about - https://agentskills.io/specification - plus the additive
fields Claude Code defines. Swap to an official validator (skills-ref)
by changing the lint:skill entry in package.json if one becomes a
sensible dependency; this stays stdlib-only by repo doctrine.

Checks:
- frontmatter block present and parseable (flat keys + one-level maps)
- name: present, 1-64 chars, ^[a-z0-9]+(-[a-z0-9]+)*$, matches directory
- description: present, 1-1024 chars
- only known fields (spec fields + Claude Code additive allowlist)
- metadata.version: semver (X.Y.Z, with an optional pre-release like -rc.1) when present

Usage:
    python3 tools/validate_skill.py [--root DIR]

Exits non-zero on any violation.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_ROOT = ".claude/skills/sdlc-studio"

# The spec's closed field set - the skills-ref reference validator rejects
# anything else ("Unexpected fields in frontmatter"), so we enforce exactly
# that. Tool-specific extras belong under metadata:.
KNOWN_FIELDS = {"name", "description", "license", "compatibility", "metadata",
                "allowed-tools"}

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")  # X.Y.Z with an optional pre-release (rc.1)


def parse_frontmatter(text: str) -> dict[str, object] | None:
    """Parse the leading YAML frontmatter block.

    Handles the flat subset this skill uses: `key: value` lines plus
    one-level nested maps (e.g. metadata:). Returns None when no
    frontmatter block exists.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fields: dict[str, object] = {}
    current_map: dict[str, str] | None = None
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indented = line.startswith((" ", "\t"))
        if indented and current_map is not None:
            key, _, value = line.strip().partition(":")
            current_map[key.strip()] = value.strip().strip("\"'")
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip().strip("\"'")
        if value:
            fields[key] = value
            current_map = None
        else:
            current_map = {}
            fields[key] = current_map
    return None  # unterminated block


def validate(root: Path) -> list[str]:
    """Return a list of violations for the skill at root."""
    errors: list[str] = []
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        return [f"missing {skill_md}"]

    fields = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    if fields is None:
        return [f"{skill_md}: no parseable frontmatter block"]

    name = fields.get("name")
    if not isinstance(name, str) or not name:
        errors.append("name: missing")
    else:
        if not 1 <= len(name) <= 64:
            errors.append(f"name: length {len(name)} outside 1-64")
        if not NAME_RE.match(name):
            errors.append(f"name: '{name}' fails ^[a-z0-9]+(-[a-z0-9]+)*$")
        if name != root.resolve().name:
            errors.append(f"name: '{name}' does not match directory '{root.resolve().name}'")

    description = fields.get("description")
    if not isinstance(description, str) or not description:
        errors.append("description: missing")
    elif len(description) > 1024:
        errors.append(f"description: {len(description)} chars exceeds 1024")

    for key in fields:
        if key not in KNOWN_FIELDS:
            errors.append(f"unknown frontmatter field: {key}")

    metadata = fields.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict):
            errors.append("metadata: not a map")
        else:
            version = metadata.get("version")
            if version is not None and not SEMVER_RE.match(version):
                errors.append(f"metadata.version: '{version}' is not X.Y.Z semver")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=DEFAULT_ROOT, help="skill directory")
    args = parser.parse_args(argv)

    errors = validate(Path(args.root))
    for err in errors:
        print(f"SKILL: {err}", file=sys.stderr)
    if not errors:
        print("SKILL.md frontmatter conforms to the Agent Skills spec subset.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
