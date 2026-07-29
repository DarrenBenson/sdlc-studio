#!/usr/bin/env python3
"""Hold the TSD's per-script test contract to the scripts tree, in BOTH directions.

A skill-development CI tool (lives in tools/).

The TSD said "Every script has a matching `test_<script>.py`" and, separately, that every
script and shared-library module has a dedicated test module. Neither was true - three modules
have none - and the document itself admitted, two hundred lines away, that "no sweep enumerates
the scripts and fails a build on a module that arrives without a test". This is that sweep.

Both directions matter equally. A module the sweep finds untested and the list omits is coverage
nobody declared. A module the list names that has since GAINED a dedicated test is a stale
exemption, and a stale exemption is how a real gap hides next to a fake one.

The exception list is parsed from the TSD's own fenced block, so the document is the declaration
and this tool is only the reader - there is no second copy of the set to drift.

Usage:
    python3 tools/check_script_tests.py [--root DIR]

Exits non-zero on any disagreement, on a denied absolute claim, or on a directory it cannot read.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILL_DIR = ".claude/skills/sdlc-studio"
SCRIPTS_REL = f"{SKILL_DIR}/scripts"
TSD_REL = "sdlc-studio/tsd.md"

#: Absolute phrasings the tree contradicts. Applied to a LOCATED passage, never to the whole
#: file: a whole-file search cannot say which passage is wrong, and a passage that has been
#: renamed away would silently match nothing and report clean.
DENIED = (
    "Every script has a matching",
    "every script and every\nshared-library module has a dedicated test module",
)

#: passage name -> (heading that opens it, regex that closes it)
PASSAGES = {
    "Script tier": ("**Script tier - test-driven, executable.**", r"^---\s*$"),
    "coverage aspiration": ("The 80% floor is the **hard gate**", r"^\s*```"),
}


class Unreadable(RuntimeError):
    """A directory or document the sweep needs and cannot read.

    Never degrades to an empty result: a sweep over nothing reports zero exceptions, which
    reads exactly like a clean tree and is the failure this tool exists to remove.
    """


def untested_modules(root: Path) -> list[str]:
    """Modules with no `tests/test_<name>.py` partner, as the TSD names them.

    Top level and `lib/` both, because a `scripts/*.py`-shaped glob silently drops the shared
    library - the exemption-by-omission that would lose `lib/tiers` without anyone deciding to.
    """
    scripts = root / SCRIPTS_REL
    tests = scripts / "tests"
    if not scripts.is_dir():
        raise Unreadable(f"{SCRIPTS_REL} is not a readable directory - nothing was swept")
    if not tests.is_dir():
        raise Unreadable(f"{SCRIPTS_REL}/tests is not a readable directory - nothing was swept")
    have = {p.name for p in tests.glob("test_*.py")}
    missing: list[str] = []
    for path in sorted(scripts.glob("*.py")):
        if f"test_{path.stem}.py" not in have:
            missing.append(path.stem)
    for path in sorted((scripts / "lib").glob("*.py")):
        if path.name == "__init__.py":
            continue
        if f"test_{path.stem}.py" not in have:
            missing.append(f"lib/{path.stem}")
    return missing


def declared_exceptions(root: Path) -> list[str]:
    """The indirect-only set the TSD declares, from its own fenced block under the coverage map.

    The document is the declaration; this is only the reader. A second copy of the set living
    in this file would be one more thing to drift.
    """
    tsd = root / TSD_REL
    if not tsd.is_file():
        raise Unreadable(f"{TSD_REL} is not readable - the declared set cannot be parsed")
    text = tsd.read_text(encoding="utf-8")
    i = text.find("#### Unit coverage map")
    if i == -1:
        raise Unreadable("no '#### Unit coverage map' heading in the TSD - the passage was "
                         "renamed, and a guard must not compare an empty set")
    m = re.search(r"```text\n(.*?)```", text[i:], re.S)
    if not m:
        raise Unreadable("the Unit coverage map declares no fenced exception list")
    return [line.strip() for line in m.group(1).splitlines() if line.strip()]


def denied_claims(root: Path) -> list[str]:
    """Absolute claims found inside their own located passage."""
    tsd = root / TSD_REL
    if not tsd.is_file():
        raise Unreadable(f"{TSD_REL} is not readable")
    text = tsd.read_text(encoding="utf-8")
    out: list[str] = []
    for name, (start, end) in PASSAGES.items():
        i = text.find(start)
        if i == -1:
            raise Unreadable(f"could not locate the {name!r} passage - it was renamed, and a "
                             f"denylist that matches nothing reports clean")
        rest = text[i + len(start):]
        m = re.search(end, rest, re.M)
        block = rest[:m.start()] if m else rest
        for phrase in DENIED:
            if phrase in block:
                out.append(f"{name}: {phrase.splitlines()[0]!r} is contradicted by the tree")
    return out


def check(root: Path) -> list[str]:
    """Every disagreement, in both directions, plus any denied claim."""
    swept = set(untested_modules(root))
    declared = set(declared_exceptions(root))
    errors = []
    for module in sorted(swept - declared):
        errors.append(f"{module} has no dedicated test module and the TSD's exception list does "
                      f"not name it - undeclared coverage gap")
    for module in sorted(declared - swept):
        errors.append(f"{module} is listed as indirect-only but now HAS a dedicated test module - "
                      f"a stale exemption hides a real gap beside it")
    errors.extend(denied_claims(root))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repo root")
    args = parser.parse_args(argv)
    try:
        errors = check(Path(args.root))
    except Unreadable as exc:
        print(f"SCRIPT-TESTS: {exc}", file=sys.stderr)
        return 1
    for err in errors:
        print(f"SCRIPT-TESTS: {err}", file=sys.stderr)
    if errors:
        return 1
    swept = untested_modules(Path(args.root))
    print(f"The TSD's per-script test contract agrees with the tree "
          f"({len(swept)} declared indirect-only: {', '.join(swept) or 'none'}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
