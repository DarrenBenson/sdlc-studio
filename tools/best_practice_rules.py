#!/usr/bin/env python3
"""The shipped testing practice must state the ENTRY-POINT rule.

A skill-development CI tool (lives in tools/).

A criterion describing a COMMAND, verified only through the library, passes forever while the
command does nothing. US0577 shipped `brief_fingerprint` that way: a green acceptance test
computing it in-process, and no command that called it at all. Three of five findings in that
batch were the same shape, and it cost a second review round.

The check is SCOPED to the practice's own section. A whole-file search is satisfied by a
Revision History row describing this change being made - a guard its own paperwork turns green
(BG0457).

Usage:
    python3 tools/best_practice_rules.py [--root DIR]

Exits non-zero when the practice does not state the rule.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PRACTICE_REL = ".claude/skills/sdlc-studio/best-practices/testing.md"
SECTION_HEADING = "## Name the ENTRY POINT"

#: Probed separately: a passage mentioning entry points without saying what to DO when they
#: differ from the claim leaves out the half that changes behaviour.
CLAIMS: tuple[tuple[str, re.Pattern], ...] = (
    ("entry point", re.compile(r"entry point", re.IGNORECASE)),
    ("the command against the library",
     re.compile(r"library.*command|command.*library", re.IGNORECASE | re.DOTALL)),
    ("name it before writing",
     re.compile(r"before writing the test|write it down before", re.IGNORECASE)),
)


def section(text: str) -> str:
    """The practice's own entry-point section - never the whole file. See the module docstring."""
    start = text.find(SECTION_HEADING)
    if start < 0:
        return ""
    end = text.find("\n## ", start + 1)
    return text[start:end if end > 0 else len(text)]


def missing_claims(text: str) -> list[str]:
    body = section(text)
    if not body:
        return [f"a `{SECTION_HEADING}` section to state them in"]
    return [name for name, pattern in CLAIMS if not pattern.search(body)]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args(argv)
    path = Path(args.root) / PRACTICE_REL
    if not path.exists():
        print(f"no testing practice at {path} - nothing to check", file=sys.stderr)
        return 0
    missing = missing_claims(path.read_text(encoding="utf-8"))
    if missing:
        print(f"{PRACTICE_REL}: the entry-point rule never states {', '.join(missing)} - a "
              f"criterion about a command, verified through the library, passes while the "
              f"command does nothing", file=sys.stderr)
        return 1
    print("The testing practice states the entry-point rule.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
