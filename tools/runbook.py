#!/usr/bin/env python3
"""The sprint toolchain runbook must name commands that exist.

A skill-development CI tool (lives in tools/).

A runbook that has rotted is worse than none: it sends an agent to a command that was renamed,
which is the moment they stop trusting it and go back to hand-rolling. So every command the
runbook names is resolved against the shipped surface, and a name that no longer resolves
fails.

Usage:
    python3 tools/runbook.py [--root DIR]

Exits non-zero when the runbook names a script or subcommand that does not exist.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

RUNBOOK_REL = ".claude/skills/sdlc-studio/reference-sprint-toolchain.md"
SKILL_REL = ".claude/skills/sdlc-studio/scripts"

#: The steps a sprint actually has. Named here so a runbook that quietly drops one fails,
#: rather than passing because everything it happens to mention still resolves.
REQUIRED_STEPS = ("Orient", "Groom and plan", "Deliver a unit", "Review a unit", "Close")

#: A command cell: `script.py verb ...` or `tools/thing.sh ...`, inside backticks.
_CMD = re.compile(r"`((?:tools/)?[a-z_]+\.(?:py|sh))(?:\s+([a-z][a-z-]*))?[^`]*`")


def commands(text: str) -> list[tuple[str, str]]:
    """Every (script, subcommand) pair the runbook names, subcommand possibly empty."""
    return [(m.group(1), m.group(2) or "") for m in _CMD.finditer(text)]


def missing(root: Path, text: str) -> list[str]:
    """Scripts the runbook names that do not exist on the shipped surface."""
    out = []
    for script, _verb in commands(text):
        candidates = [root / script, root / SKILL_REL / script]
        if not any(c.is_file() for c in candidates):
            out.append(script)
    return sorted(set(out))


def missing_steps(text: str) -> list[str]:
    return [s for s in REQUIRED_STEPS if s.lower() not in text.lower()]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args(argv)
    root = Path(args.root)
    path = root / RUNBOOK_REL
    if not path.exists():
        print(f"no runbook at {RUNBOOK_REL} - the toolchain has no step-ordered entry point",
              file=sys.stderr)
        return 1
    text = path.read_text(encoding="utf-8")
    gone = missing(root, text)
    steps = missing_steps(text)
    if gone:
        print(f"{RUNBOOK_REL}: names {len(gone)} command(s) that do not exist: "
              f"{', '.join(gone)} - a runbook that has rotted sends an agent to a renamed "
              f"tool, which is when they stop trusting it", file=sys.stderr)
    if steps:
        print(f"{RUNBOOK_REL}: no section for {', '.join(steps)} - a step with no entry is one "
              f"an agent answers from memory", file=sys.stderr)
    if gone or steps:
        return 1
    print(f"runbook: {len(set(commands(text)))} command(s) across "
          f"{len(REQUIRED_STEPS)} steps, all resolving.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
