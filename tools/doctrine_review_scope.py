#!/usr/bin/env python3
"""The shipped doctrine must state the review SCOPE rule, not only the review ceremony.

A skill-development CI tool (lives in tools/).

A consuming project installs `reference-doctrine.md` and inherits whatever it says. Rule 18
told it WHERE the adversarial review runs; until rule 19 nothing told it what that review may
look at or what may block it. Without the bound, a review of a five-point unit becomes an audit
of the repository, and the gate stops being passable by any correct increment - which is not
strictness but a review that has stopped discriminating.

The check is SCOPED to the numbered rules section on purpose. A whole-file substring search is
satisfied by any occurrence of the words, including a Revision History row that merely describes
this change being made: a guard its own changelog entry can satisfy goes green the moment
somebody writes about the work instead of doing it (BG0457).

Usage:
    python3 tools/doctrine_review_scope.py [--root DIR]

Exits non-zero when the doctrine's rules do not state the scope rule.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DOCTRINE_REL = ".claude/skills/sdlc-studio/reference-doctrine.md"

#: The claims the rule must actually make, each probed separately - a passage that mentions
#: scope without saying what may BLOCK leaves the expensive half unstated.
CLAIMS: tuple[tuple[str, re.Pattern], ...] = (
    ("affects", re.compile(r"`?Affects`?", re.IGNORECASE)),
    ("base ref", re.compile(r"base ref", re.IGNORECASE)),
    ("regression", re.compile(r"regression", re.IGNORECASE)),
    ("pre-existing", re.compile(r"pre-existing", re.IGNORECASE)),
    ("does not block", re.compile(r"does not (?:block|hold)", re.IGNORECASE)),
)


def rules_section(text: str) -> str:
    """The numbered rules only - never the whole file. See the module docstring."""
    start = text.find("## The rules")
    if start < 0:
        return ""
    end = text.find("\n## ", start + 1)
    return text[start:end if end > 0 else len(text)]


def missing_claims(text: str) -> list[str]:
    """The scope-rule claims the doctrine's rules section does not make."""
    section = rules_section(text)
    if not section:
        return ["a `## The rules` section to state them in"]
    return [name for name, pattern in CLAIMS if not pattern.search(section)]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args(argv)
    path = Path(args.root) / DOCTRINE_REL
    if not path.exists():
        print(f"no doctrine at {path} - nothing to check", file=sys.stderr)
        return 0
    missing = missing_claims(path.read_text(encoding="utf-8"))
    if missing:
        print(f"{DOCTRINE_REL}: the rules never state {', '.join(missing)} - a consuming "
              f"project inherits the review ceremony without the bound on what it may judge",
              file=sys.stderr)
        return 1
    print("The doctrine states the review scope rule.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
