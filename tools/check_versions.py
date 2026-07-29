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
import contextlib
import json
import re
import sys
from pathlib import Path

SKILL_DIR = ".claude/skills/sdlc-studio"

SEMVER = r"(\d+\.\d+\.\d+)"


def from_package_json(root: Path) -> str | None:
    try:
        v = json.loads((root / "package.json").read_text(encoding="utf-8")).get("version")
    except (OSError, json.JSONDecodeError):
        return None
    if not v:
        return None
    # Normalise a pre-release (`4.0.0-rc.1` -> `4.0.0`) to the SEMVER core, so package.json
    # compares consistently with the other homes (which already extract the core via SEMVER).
    m = re.match(SEMVER, v)
    return m.group(1) if m else v


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


#: The specs declare "the document version tracks the product version" and nothing enforced it:
#: both sat at 4.1.0 after 5.0.0 was cut, and `check_versions` never looked at them.
#: Seeded homes, kept only as a floor for a checkout git cannot enumerate. Coverage is
#: DISCOVERED (see `discover_spec_homes`); this list is what the guard falls back to, never
#: what it is limited to. The four-entry version of it never reached trd.md or tsd.md, so two
#: spec files drifted for as long as anyone cared to look.
SPEC_FILES = ("sdlc-studio/prd.md", "sdlc-studio/trd.md", "sdlc-studio/tsd.md")

#: A directory whose files QUOTE versions rather than declaring one. A bug reporting a version
#: mismatch is evidence, not a home, and holding it to the current version would make filing
#: one impossible.
_NOT_A_HOME = ("/bugs/", "/stories/", "/epics/", "/change-requests/", "/rfcs/", "/retros/",
               "/reviews/", "/handoffs/", "/decisions/", "/tests/", "/archive/")


class DiscoveryFailed(RuntimeError):
    """Raised when the tracked-file listing cannot be taken.

    A guard that cannot see the tree must not report a clean scan of it: a scan over nothing
    passes trivially, and it passes loudest exactly when something is wrong with the checkout.
    """


def tracked_markdown(root: Path) -> list[str]:
    """Every candidate `.md` path, repo-relative.

    Tracked files when git can say, because a tracked listing is the honest definition of "the
    repo" and it excludes build output and scratch files for free. A checkout git cannot
    enumerate - an exported tarball, a vendored copy - falls back to walking the tree, which is
    a wider set but never a narrower one, so the guard degrades toward checking MORE rather
    than toward a clean scan over nothing.

    `DiscoveryFailed` only when both fail, which means the tree itself cannot be read.
    """
    import subprocess  # noqa: PLC0415 - only this path needs it
    with contextlib.suppress(OSError):
        res = subprocess.run(["git", "-C", str(root), "ls-files", "*.md"],
                             capture_output=True, text=True, check=False)
        if res.returncode == 0:
            return [line for line in res.stdout.splitlines() if line.strip()]
    try:
        return [str(p.relative_to(root)) for p in root.rglob("*.md")
                if ".git/" not in str(p.relative_to(root)) and "node_modules/" not in str(p)]
    except OSError as exc:
        raise DiscoveryFailed(f"neither git nor a tree walk could list the repo: {exc}") from exc


def discover_spec_homes(root: Path) -> list[str]:
    """Tracked markdown files that DECLARE a version, so coverage follows the repo.

    A hand-maintained list is a list somebody must remember to extend, and the one this
    replaced had not been extended in two files' worth of drift. Artefact directories are
    excluded: a bug REPORTING a version mismatch quotes a version, and holding it to the
    current one would make the report unfileable.
    """
    homes = []
    for rel in tracked_markdown(root):
        if any(seg in f"/{rel}" for seg in _NOT_A_HOME):
            continue
        if from_spec(root, rel) is None:
            continue
        if _is_superseded(root, rel):
            continue
        homes.append(rel)
    return sorted(set(homes) | {s for s in SPEC_FILES
                                if (root / s).is_file() and not _is_superseded(root, s)})


def _is_superseded(root: Path, rel: str) -> bool:
    """True for a document that records what was true THEN.

    A superseded appendix declaring an old version is history, not drift. Holding it to the
    current version would force a maintainer to falsify the record to make the guard green -
    which is the one thing a truth guard must never demand.
    """
    try:
        head = (root / rel).read_text(encoding="utf-8")[:4000]
    except OSError:
        return False
    m = re.search(r"^>?\s*\*\*Status:?\*\*:?\s*(.+)$", head, re.M)
    return bool(m) and m.group(1).strip().lower().startswith(("superseded", "historical",
                                                              "archived", "retired"))


def from_spec(root: Path, rel: str) -> str | None:
    """The `Version:` a spec declares, in either the plain or the blockquoted form.

    None when the file has no version line at all - which the caller treats as "not one of the
    homes" rather than as a mismatch, so a project whose specs carry no version is not held to
    a rule it never adopted."""
    try:
        head = (root / rel).read_text(encoding="utf-8")[:4000]
    except OSError:
        return None
    m = re.search(rf"^>?\s*\*\*Version:?\*\*:?\s*v?{SEMVER}", head, re.M)
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
    # The specs are held only when they DECLARE a version. Absent is "not a home"; present and
    # different is drift, and it is the drift nothing was looking for. DISCOVERED, so a new
    # home is covered without editing this guard.
    try:
        homes = discover_spec_homes(root)
    except DiscoveryFailed as exc:
        # Never a clean pass over nothing: a scan that could not list its own scope has not
        # checked anything, and reporting success is the loudest possible lie here.
        print(f"VERSIONS: discovery failed, so nothing was scanned - {exc}", file=sys.stderr)
        return 1
    for rel in homes:
        got = from_spec(root, rel)
        if got is not None:
            versions[rel] = got
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
