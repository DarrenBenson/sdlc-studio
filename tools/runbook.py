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
REQUIRED_STEPS = ("Orient", "Groom and plan", "Deliver a unit", "Review a unit", "Close", "Release")

#: A command cell: `script.py verb ...` or `tools/thing.sh ...`, inside backticks.
#:
#: `[a-z_]+` cannot match a HYPHEN, so every hyphenated script was silently exempt - including
#: `run-suite.sh` and `forward-port.sh`, which the guard then reported "all resolving" having
#: never looked at. An enumeration exempts whatever its pattern forgot (LL0013), and a
#: character class is an enumeration.
_CMD = re.compile(r"`((?:tools/)?[a-z][a-z_-]*\.(?:py|sh))(?:\s+([a-z][a-z-]*))?[^`]*`")


def commands(text: str) -> list[tuple[str, str]]:
    """Every (script, subcommand) pair the runbook names, subcommand possibly empty."""
    return [(m.group(1), m.group(2) or "") for m in _CMD.finditer(text)]


def _resolve(root: Path, script: str) -> Path | None:
    for c in (root / script, root / SKILL_REL / script):
        if c.is_file():
            return c
    return None


def missing(root: Path, text: str) -> list[str]:
    """Scripts the runbook names that do not exist on the shipped surface."""
    return sorted({s for s, _v in commands(text) if _resolve(root, s) is None})


def missing_verbs(root: Path, text: str) -> list[str]:
    """Named `script verb` pairs whose VERB the script does not offer.

    Subcommand rot is the commoner kind: scripts are renamed rarely, verbs often, and a runbook
    naming `status.py points` after that verb is renamed sends an agent to a command that exits
    2. The first version bound the verb and discarded it, so it checked the half that hardly
    ever moves. Read from the script's own `--help`, so the answer comes from the shipped
    surface rather than a second list that would itself go stale.
    """
    out = []
    for script, verb in commands(text):
        if not verb:
            continue
        path = _resolve(root, script)
        if path is None or path.suffix != ".py":
            continue                      # a missing script is `missing`'s finding, not this one
        try:
            help_text = subprocess.run(
                [sys.executable, str(path), "--help"], capture_output=True, text=True,
                timeout=30, cwd=str(root)).stdout
        except (OSError, subprocess.SubprocessError):
            continue                      # unrunnable is not evidence the verb is gone
        # argparse prints its subcommands in the `{a,b,c}` choices block. Absent block means the
        # script takes no subcommands at all, in which case a named verb is itself the rot.
        blocks = re.findall(r"\{([a-z][a-z0-9,_-]*)\}", help_text)
        offered = {v for b in blocks for v in b.split(",")}
        if offered and verb not in offered:
            out.append(f"{script} {verb}")
    return sorted(set(out))


def missing_steps(text: str) -> list[str]:
    return [s for s in REQUIRED_STEPS if s.lower() not in text.lower()]


def out_of_order_steps(text: str) -> list[str]:
    """The required steps that appear out of sequence.

    The runbook's whole claim is that it is ordered BY STEP - that is what distinguishes it from
    the script catalogue. A membership test cannot see order, so the sections could be reversed
    entirely and the guard still passed.
    """
    low = text.lower()
    seen = [(low.find(s.lower()), s) for s in REQUIRED_STEPS if s.lower() in low]
    ordered = [s for _, s in sorted(seen)]
    expected = [s for s in REQUIRED_STEPS if s in ordered]
    return [] if ordered == expected else expected


def steps_without_a_command(text: str) -> list[str]:
    """Required steps whose own section names no command.

    Asserted per SECTION, not as a total over the document: a global count is satisfied by one
    rich step carrying the tally for an empty one, which is the case that matters - the empty
    step is the one an agent answers from memory.
    """
    low, out = text.lower(), []
    marks = sorted((low.find(s.lower()), s) for s in REQUIRED_STEPS if s.lower() in low)
    for i, (pos, step) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        if not commands(text[pos:end]):
            out.append(step)
    return out


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
    rotted_verbs = missing_verbs(root, text)
    disordered = out_of_order_steps(text)
    commandless = steps_without_a_command(text)
    if gone:
        print(f"{RUNBOOK_REL}: names {len(gone)} command(s) that do not exist: "
              f"{', '.join(gone)} - a runbook that has rotted sends an agent to a renamed "
              f"tool, which is when they stop trusting it", file=sys.stderr)
    if steps:
        print(f"{RUNBOOK_REL}: no section for {', '.join(steps)} - a step with no entry is one "
              f"an agent answers from memory", file=sys.stderr)
    if rotted_verbs:
        print(f"{RUNBOOK_REL}: names {len(rotted_verbs)} subcommand(s) the script no longer "
              f"offers: {', '.join(rotted_verbs)} - a verb rename is the commonest rot, and it "
              f"sends an agent to a command that exits 2", file=sys.stderr)
    if disordered:
        print(f"{RUNBOOK_REL}: the steps are not in sprint order (expected "
              f"{' -> '.join(disordered)}) - ordering BY STEP is what distinguishes this from "
              f"the script catalogue", file=sys.stderr)
    if commandless:
        print(f"{RUNBOOK_REL}: {', '.join(commandless)} name(s) no command - a step with no "
              f"command is the one an agent answers from memory", file=sys.stderr)
    if gone or steps or rotted_verbs or disordered or commandless:
        return 1
    print(f"runbook: {len(set(commands(text)))} command(s) across "
          f"{len(REQUIRED_STEPS)} steps, all resolving.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
