#!/usr/bin/env python3
"""Enforce line budgets on the skill's always-loaded and reference files.

A skill-development CI tool (lives in tools/). The Agent Skills guidance
caps SKILL.md at 500 lines; reference files are progressively loaded but
past ~600 lines partial reads start missing content, so growth beyond
that needs deliberate sign-off here rather than accretion.

Rules:
- SKILL.md must stay under 500 lines (hard).
- Any reference-*.md over 600 lines must appear in ALLOWLIST (hard),
  recorded with its ceiling; an allowlisted file may not exceed its
  ceiling by more than 5% (hard) - shrink it or consciously raise the
  ceiling in this file.

Usage:
    python3 tools/check_budgets.py [--root DIR]

Exits non-zero on any violation.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SKILL_DIR = ".claude/skills/sdlc-studio"
SKILL_MD_BUDGET = 500
REFERENCE_BUDGET = 600
CEILING_TOLERANCE = 1.05

# Files allowed over REFERENCE_BUDGET, with the line count recorded when
# they were allowlisted (v2.0.0). Raising a ceiling is a deliberate,
# reviewed act - do it here, with a reason in the commit message.
ALLOWLIST = {
    "reference-epic.md": 1052,
    "reference-story.md": 1037,
    "reference-code.md": 911,
    "reference-outputs.md": 781,  # +RFC0012 index-archival + slice-read conventions (CR0041)
    "reference-decisions.md": 724,
    "reference-test-best-practices.md": 706,  # +assertion-integrity + mutation-check section (CR0131)
    "reference-config.md": 640,  # +repair-plan gate keys (EP0106): a new opt-in config surface
    "reference-review.md": 755,  # +closing-review brief (EP0108/EP0109) +supersession boundary rule
                                 # first pass and the standing adversarial practices;
                                 # +the verdict-log supersession section (EP0133/US0374/US0375):
                                 # the correction path and what a retired row does to each gate.
                                 # Raised 705 -> 755 for US0504/US0505: where a delegated reviewer
                                 # mutates (isolated checkout, never the author's tree - a reviewer
                                 # reverted a shipped repair mutating a live one) and the standing
                                 # practice that a behaviour-changing repair carries a test. Both
                                 # are doctrine nothing executes, so the reference IS the artefact
    # 797: +the in-flight controls section (US0473). Raised DELIBERATELY, in the same commit
    # as the prose it admits, and set to the file's actual length rather than a round number
    # with headroom - a ceiling with slack in it is one that stops noticing growth.
    "reference-sprint.md": 796,  # +the compulsory checklist as loop step 9 (EP0192): the one place
                                 # the whole cycle is stated as a checkable set. Raised 724 -> 740
                                 # deliberately - the file was AT its +5% tolerance, so the step
                                 # could not land without saying so here.
                                 # +EP0130/0146/0150-0155 sprint-engine, +report-only lane partition/export
                                 # +the amend/material goal-review and seat-brief notes (EP0152/0153)
                                 # (Sprint 1 of the three-sprint run). FLAGGED for a structural
                                 # split: it is the largest reference and grows with the engine;
                                 # its Reading Guide anchors partial reads, so a split is safe.
                                 # +deferred operator decisions and the bounded close exit
                                 # (CR0369/CR0371), +the fixed per-sprint forecast term (CR0391)
                                 # - loop steps, not accretion; the file has a Reading Guide, so
                                 # partial reads stay anchored
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repo root")
    args = parser.parse_args(argv)
    skill = Path(args.root) / SKILL_DIR

    errors: list[str] = []

    skill_md = skill / "SKILL.md"
    n = len(skill_md.read_text(encoding="utf-8").splitlines())
    if n >= SKILL_MD_BUDGET:
        errors.append(f"SKILL.md: {n} lines >= {SKILL_MD_BUDGET} budget")

    for path in sorted(skill.glob("reference-*.md")):
        n = len(path.read_text(encoding="utf-8").splitlines())
        ceiling = ALLOWLIST.get(path.name)
        if ceiling is None:
            if n > REFERENCE_BUDGET:
                errors.append(
                    f"{path.name}: {n} lines > {REFERENCE_BUDGET} budget "
                    f"(not allowlisted - split it, or allowlist deliberately)")
        elif n > ceiling * CEILING_TOLERANCE:
            errors.append(
                f"{path.name}: {n} lines > allowlisted ceiling {ceiling} +5% "
                f"({int(ceiling * CEILING_TOLERANCE)}) - shrink it or raise the ceiling deliberately")

    for err in errors:
        print(f"BUDGET: {err}", file=sys.stderr)
    if not errors:
        print("All files within line budgets.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
