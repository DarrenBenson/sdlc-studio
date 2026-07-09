#!/usr/bin/env python3
"""Deterministic documentation-coverage check.

The `documented` half of the sprint Definition of Done. Enforces the discoverability
floor so docs cannot drift (the gap the self-audit found - pvd/gate/skill-update shipped
without a help-catalogue entry):
  - every command in SKILL.md's Type Reference has a help/help.md catalogue entry  (HARD)
  - every scripts/*.py (non-test, non-lib) has a reference-scripts.md entry          (HARD)
  - CHANGELOG [Unreleased] is non-empty when there is undocumented release work      (soft warn)

Skill-development check: it inspects the SKILL itself, so for a CONSUMING project (no
SKILL.md under the root) it is a no-op (ok, N/A). Wired into the gate (blocking) and the
conformance `documented` stage. Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_SKILL_REL = Path(".claude") / "skills" / "sdlc-studio"
_NON_SCRIPTS = {"__init__"}


def _skill_dir(repo_root: Path) -> Path | None:
    d = Path(repo_root) / _SKILL_REL
    return d if (d / "SKILL.md").exists() else None


def _type_ref_commands(skill_dir: Path) -> list[str]:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    if "## Type Reference" not in text:
        return []
    sec = text.split("## Type Reference", 1)[1].split("## Full Reference")[0]
    return [m.group(1) for m in re.finditer(r"^\| `([^`]+)`", sec, re.M)]


def _scripts(skill_dir: Path) -> list[str]:
    sd = skill_dir / "scripts"
    return sorted(p.stem for p in sd.glob("*.py")
                  if p.stem not in _NON_SCRIPTS and not p.stem.startswith("test"))


def _changelog_unreleased_empty(repo_root: Path) -> bool | None:
    p = Path(repo_root) / "CHANGELOG.md"
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return None  # no changelog -> not applicable
    if "## [Unreleased]" not in text:
        return None
    after = text.split("## [Unreleased]", 1)[1]
    section = re.split(r"\n## \[", after, maxsplit=1)[0]  # up to the next release header
    return section.strip() == ""


def check(repo_root: Path | str = ".") -> dict:
    skill_dir = _skill_dir(Path(repo_root))
    if skill_dir is None:  # not the skill repo - nothing to check
        return {"findings": [], "ok": True, "applicable": False}
    help_text = (skill_dir / "help" / "help.md").read_text(encoding="utf-8")
    # The script catalogue is a lean index (reference-scripts.md) plus grouped detail pages
    # (reference-scripts-*.md); a script's `### ` entry may live in any of them, so union them.
    refscripts = "\n".join(
        p.read_text(encoding="utf-8")
        for p in sorted(skill_dir.glob("reference-scripts*.md")))
    findings = []
    for cmd in _type_ref_commands(skill_dir):
        # Must be an actual catalogue entry (`/sdlc-studio <cmd>`), not a coincidental
        # backtick mention in prose (which would falsely mark it documented).
        if not re.search(rf"/sdlc-studio {re.escape(cmd)}\b", help_text):
            findings.append({"kind": "command-uncatalogued", "name": cmd, "blocking": True,
                             "detail": f"command `{cmd}` is in the Type Reference but not in help/help.md"})
    for s in _scripts(skill_dir):
        if f"### `{s}.py`" not in refscripts:
            findings.append({"kind": "script-undocumented", "name": s, "blocking": True,
                             "detail": f"scripts/{s}.py has no reference-scripts.md entry"})
    if _changelog_unreleased_empty(Path(repo_root)) is True:
        findings.append({"kind": "changelog-empty", "name": "CHANGELOG", "blocking": False,
                         "detail": "CHANGELOG [Unreleased] is empty - add an entry for the release work (LL0004)"})
    return {"findings": findings, "ok": not any(f["blocking"] for f in findings), "applicable": True}


def cmd_check(args: argparse.Namespace) -> int:
    r = check(args.root)
    if args.format == "json":
        print(json.dumps(r, indent=2))
    elif not r["applicable"]:
        print("doc-coverage: N/A (no SKILL.md under root)")
    else:
        for f in r["findings"]:
            print(f"  [{'FAIL' if f['blocking'] else 'warn'}] {f['detail']}")
        print(f"doc-coverage: {'PASS' if r['ok'] else 'FAIL'}")
    return 0 if r["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Documentation-coverage check.")
    p.add_argument("--root", default=".")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.set_defaults(func=cmd_check)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        args = build_parser().parse_args()
        sys.exit(args.func(args))
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
