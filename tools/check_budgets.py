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
import re
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
    # Crossed the 600 un-allowlisted budget when US0658's generated Reading Guide landed:
    # both sat in the 620s already, and a guide is worth roughly 15 lines on a file an agent
    # would otherwise read whole. Allowlisted deliberately at their measured size rather than
    # splitting a reference to fit a generator, which would be the tail wagging the dog.
    "reference-consult.md": 634,
    "reference-prd.md": 660,
    "reference-epic.md": 1102,
    "reference-story.md": 1091,
    "reference-code.md": 974,
    "reference-outputs.md": 869,  # +RFC0012 index-archival + slice-read conventions (CR0041)
    "reference-decisions.md": 812,
    "reference-test-best-practices.md": 788,  # +assertion-integrity + mutation-check section (CR0131)
    "reference-config.md": 695,  # +repair-plan gate keys (EP0106): a new opt-in config surface
    "reference-review.md": 819,  # +closing-review brief (EP0108/EP0109) +supersession boundary rule
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
    "reference-sprint.md": 855,  # +the compulsory checklist as loop step 9 (EP0192): the one place
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
                                 # +the close's fixed point as a guardrail (US0616/CR0527): the
                                 # rule that a finding surfaced during a close is filed and
                                 # deferred, and the command that refuses otherwise. A rule with
                                 # no gate behind it is a known-weak rule, so the statement ships
                                 # beside the gate rather than instead of it

# Recorded by `check_budgets.py --record`: reference-epic.md 1052 -> 1119; reference-story.md 1037 -> 1108; reference-code.md 911 -> 975; reference-outputs.md 781 -> 870; reference-decisions.md 724 -> 813; reference-test-best-practices.md 706 -> 789; reference-config.md 640 -> 696; reference-review.md 755 -> 820; reference-sprint.md 827 -> 856
# Recorded by `check_budgets.py --record`: reference-consult.md 635 -> 634; reference-prd.md 661 -> 660; reference-epic.md 1119 -> 1118; reference-story.md 1108 -> 1107; reference-code.md 975 -> 974; reference-outputs.md 870 -> 869; reference-decisions.md 813 -> 812; reference-test-best-practices.md 789 -> 788; reference-config.md 696 -> 695; reference-review.md 820 -> 819; reference-sprint.md 856 -> 855
# Recorded by `check_budgets.py --record`: reference-epic.md 1118 -> 1102; reference-story.md 1107 -> 1091
}


# ---------------------------------------------------------------- record / drift (US0657)

#: Trees with no line budget. REPORTED, never gated: a hard ceiling set on day one over a tree
#: nobody has been pruning fails on day one and is waived on day two, and a waived gate is worse
#: than a reported number because it looks like a gate. Counted over `*.md` only - `templates/`
#: is 7,412 lines over all files, and a total whose filter is unstated is one nobody can
#: reproduce.
UNBUDGETED_TREES = ("help", "best-practices", "templates")


def _measure(skill):
    """`{filename: line count}` for every reference, plus SKILL.md."""
    out = {}
    for path in sorted(skill.glob("reference-*.md")):
        out[path.name] = len(path.read_text(encoding="utf-8").splitlines())
    return out


STAMP_PREFIX = "# Recorded by `check_budgets.py --record`:"
#: How many `--record` runs the in-source history keeps. The trail is for a reader deciding
#: whether a ceiling moved recently, not an archive - git already holds every one of them.
HISTORY_KEEP = 5


def _allowlist_span(text: str, path) -> tuple[int, int]:
    """`(first, last)` line indices of the `ALLOWLIST` literal, or a NAMED failure.

    `next(...)` over a generator raises a bare `StopIteration` if the constant is ever renamed,
    which reaches the caller as a traceback with no sentence in it. A rewriter that has lost its
    anchor must say which anchor and in which file.
    """
    try:
        open_at = text.index("ALLOWLIST = {")
        close_at = text.index("\n}", open_at)
    except ValueError:
        raise SystemExit(
            f"check_budgets: no `ALLOWLIST = {{` ... `\\n}}` literal in {path} - `--record` "
            f"rewrites that block and will not guess at a replacement anchor") from None
    return text[:open_at].count("\n"), text[:close_at].count("\n")


def record_ceilings(root) -> list[str]:
    """Rewrite ALLOWLIST ceiling integers to the measured sizes. Returns what moved.

    Only the INTEGER is rewritten, per line, by a regex over the literal. Every pre-existing
    reason comment survives byte-identically and a new provenance line is APPENDED beneath the
    block - never edited into. That is the criterion rather than a nicety: the reasons CONTAIN
    their numbers (`Raised 705 -> 755`), so a tool that preserved them while moving the ceiling
    would leave an argument that is false about the ceiling it justifies. The history
    accumulates; nothing already written is rewritten.
    """
    skill = Path(root) / SKILL_DIR
    sizes = _measure(skill)
    src_path = Path(__file__)
    whole = src_path.read_text(encoding="utf-8")
    lines = whole.splitlines(keepends=True)
    # SCOPED TO THE ALLOWLIST LITERAL. Run line-wise over the whole source, the pattern rewrites
    # any ceiling-shaped line anywhere - including one inside a docstring, demonstrated in
    # review. This is a tool whose job is rewriting its own source, so the blast radius is the
    # thing to bound. `guide_justification_faults` below already scopes the same way.
    first, last = _allowlist_span(whole, src_path)
    moved: list[str] = []
    for i, line in enumerate(lines):
        if not (first <= i <= last):
            continue
        m = re.match(r'^(\s*)"([^"]+\.md)":\s*(\d+),(.*)$', line)
        if not m:
            continue
        indent, name, old, tail = m.group(1), m.group(2), int(m.group(3)), m.group(4)
        new = sizes.get(name)
        if new is None or new == old:
            continue
        lines[i] = f'{indent}"{name}": {new},{tail}\n'
        moved.append(f"{name} {old} -> {new}")
    if moved:
        # BOUNDED, and BENEATH the block it describes. An unbounded history above the allowlist
        # pushes the literal further down the file on every run, and the reader hits the audit
        # trail before the thing being audited. `HISTORY_KEEP` runs are kept; git holds the rest.
        stamp = "# Recorded by `check_budgets.py --record`: " + "; ".join(moved) + "\n"
        kept = [ln for ln in lines if ln.startswith(STAMP_PREFIX)]
        lines = [ln for ln in lines if not ln.startswith(STAMP_PREFIX)]
        history = (kept + [stamp])[-HISTORY_KEEP:]
        first, last = _allowlist_span("".join(lines), src_path)
        lines[last + 1:last + 1] = ["\n"] + history
        src_path.write_text("".join(lines), encoding="utf-8")
    return moved


def drift(root) -> list[tuple[str, int, int, float]]:
    """`(name, lines, ceiling, percent over)` for every file inside the +5% tolerance.

    The SET, not the worst offender: a report naming one member passes a single-member
    assertion while hiding the rest.
    """
    skill = Path(root) / SKILL_DIR
    out = []
    for name, n in _measure(skill).items():
        ceiling = ALLOWLIST.get(name)
        if ceiling is None or n <= ceiling:
            continue
        if n <= ceiling * CEILING_TOLERANCE:
            out.append((name, n, ceiling, round((n - ceiling) * 100.0 / ceiling, 2)))
    return sorted(out)


def tree_totals(root) -> dict:
    """`{tree: markdown line count}` - reported, with no threshold anywhere."""
    skill = Path(root) / SKILL_DIR
    out = {}
    for tree in UNBUDGETED_TREES:
        d = skill / tree
        out[tree] = sum(len(p.read_text(encoding="utf-8", errors="replace").splitlines())
                        for p in d.rglob("*.md")) if d.is_dir() else 0
    return out


def guide_justification_faults(root) -> list[str]:
    """Ceilings whose justification names a Reading Guide over a file that has none.

    The premise is fixed by MAKING IT TRUE - the guides are generated - rather than by deleting
    a sentence that is right about what the file needs.
    """
    skill = Path(root) / SKILL_DIR
    src = Path(__file__).read_text(encoding="utf-8")
    block = src[src.index("ALLOWLIST = {"):src.index("\n}", src.index("ALLOWLIST = {"))]
    faults = []
    current = None
    for line in block.splitlines():
        m = re.search(r'"([^"]+\.md)":', line)
        if m:
            current = m.group(1)
        if current and re.search(r"reading guide", line, re.I):
            target = skill / current
            if target.is_file() and "Reading Guide" not in target.read_text(encoding="utf-8"):
                faults.append(current)
    return sorted(set(faults))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repo root")
    parser.add_argument("--record", action="store_true",
                        help="rewrite ceiling INTEGERS to the measured sizes, preserving every "
                             "reason comment byte-identically and appending the provenance")
    parser.add_argument("--drift", action="store_true",
                        help="name every file inside the +5%% tolerance, and exit 0 - a file one "
                             "line from failing is worth seeing before it fails")
    args = parser.parse_args(argv)
    skill = Path(args.root) / SKILL_DIR

    if args.record:
        moved = record_ceilings(args.root)
        print(f"budgets: recorded {len(moved)} ceiling(s)"
              + (" - " + "; ".join(moved) if moved else " - nothing moved"))
        return 0

    if args.drift:
        band = drift(args.root)
        for name, n, ceiling, pct in band:
            print(f"  {name}: {n} lines, ceiling {ceiling}, {pct}% over - inside the +5% "
                  f"tolerance")
        print(f"budgets: {len(band)} file(s) inside the tolerance")
        for tree, total in tree_totals(args.root).items():
            print(f"  {tree}/: {total} markdown line(s) - REPORTED, no threshold")
        return 0

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

    for name in guide_justification_faults(args.root):
        errors.append(f"{name}: its ceiling justification names a Reading Guide and the file "
                      f"has none - generate it with `docgen.py reading-guides`, or the "
                      f"argument for the ceiling is false about the file it justifies")

    for err in errors:
        print(f"BUDGET: {err}", file=sys.stderr)
    if not errors:
        print("All files within line budgets.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
