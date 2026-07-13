#!/usr/bin/env python3
"""SDLC Studio critic-verdict record.

The independent non-author critic judges each unit's diff against the
AC intent. Its verdict used to be ephemeral, so nothing could confirm the critic
actually ran. Here it is a committed, append-only record
(`sdlc-studio/reviews/critic-verdicts.md`), so the conformance gate can require it:
"the critic ran" becomes a deterministic, auditable signal - the cheap part of
the deferred Stop-Hook, with no harness dependency.

Each verdict now stamps both the reviewer and the author (the authoring seat /
delegation id that produced the diff and tests). The conformance gate hard-fails any
unit whose reviewer id equals its author id, or that has no recorded author - a
self-review never clears the Done gate. This independence floor holds for generic
workers too, not only persona-framed ones. Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

APPROVE, REJECT = "APPROVE", "REJECT"
# Visible grandfather marker for units closed before the independence gate existed
# (under the prior risk-scaled policy that permitted light-tier self-review). Stamped
# once by the migration; never produced by the sprint loop. See is_pre_gate.
PRE_GATE = "pre-gate"
# Two verdict phases, each in its own log so a plan-review verdict never satisfies the
# delivery critique gate (and vice versa): `delivery` is the post-implementation critic the
# conformance `critiqued` stage reads; `plan-review` is the pre-implementation AC-vs-spec
# check. Same schema, same independence rule, distinct files.
PHASES = ("delivery", "plan-review")
_FILE = {"delivery": "critic-verdicts.md", "plan-review": "plan-review-verdicts.md"}
# Delivery header is byte-identical to the original (a freshly created delivery log must not
# change); plan-review has its own title/prose. Both share the row schema.
_TABLE = ("| Unit | Verdict | Reviewer | Author | Date | Issues |\n"
          "| --- | --- | --- | --- | --- | --- |\n")
_HEADERS = {
    "delivery": (
        "# Critic Verdicts\n\n"
        "> Append-only. The independent non-author critic's verdict per unit.\n"
        "> APPROVE = ready; REJECT = repair before Done. Latest row per unit wins.\n"
        "> Reviewer must differ from Author - a self-review never clears the Done gate.\n\n"
        + _TABLE),
    "plan-review": (
        "# Plan-Review Verdicts\n\n"
        "> Append-only. The independent non-author plan reviewer's verdict per unit -\n"
        "> the pre-implementation AC-vs-spec check (US0090). Latest row per unit wins.\n"
        "> Reviewer must differ from the plan author - a self-review never clears the gate.\n\n"
        + _TABLE),
}


def _header(phase: str) -> str:
    return _HEADERS[phase]


HEADER = _HEADERS["delivery"]
_COLS = ("unit", "verdict", "reviewer", "author", "date", "issues")


def verdicts_path(repo_root: Path | str, phase: str = "delivery") -> Path:
    return Path(repo_root) / "sdlc-studio" / "reviews" / _FILE[phase]


def _clean(value: str) -> str:
    # Escape `_` so an underscored identifier (e.g. `_read`, `_index_row`) in free-text notes
    # cannot pair across words into markdown emphasis and trip markdownlint MD037.
    return value.replace("|", "/").replace("\n", " ").strip().replace("_", r"\_")


def record_verdict(repo_root: Path | str, unit: str, verdict: str,
                   reviewer: str = "independent-critic", author: str = "",
                   issues: str = "", phase: str = "delivery") -> Path:
    """Append a critic verdict for a unit (creating the table if absent).

    `author` is the authoring seat / delegation instance id that produced the diff
    and tests. It is recorded alongside the reviewer so the conformance gate can prove
    reviewer != author - independence you cannot verify is independence you do not have.
    `phase` routes the verdict to its own log (delivery vs plan-review) so neither
    satisfies the other's gate.
    """
    if phase not in PHASES:
        raise ValueError(f"unknown critic phase {phase!r} - expected one of {PHASES}")
    path = verdicts_path(repo_root, phase)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(_header(phase), encoding="utf-8")
    row = (f"| {sdlc_md.norm_id(unit)} | {verdict.upper()} | {_clean(reviewer)} | "
           f"{_clean(author) or '-'} | "
           f"{sdlc_md.now_date()} | {_clean(issues) or '-'} |\n")
    with path.open("a", encoding="utf-8") as fh:  # append-only
        fh.write(row)
    return path


def read_verdicts(repo_root: Path | str, phase: str = "delivery") -> list[dict]:
    """All recorded verdicts for `phase`, in order, as
    {unit, verdict, reviewer, author, date, issues}.

    Reads both the current 6-column rows and any legacy 5-column rows (no Author) that
    pre-date the independence gate; a legacy row's author is the empty string.
    """
    path = verdicts_path(repo_root, phase)
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = sdlc_md.table_cells(line)  # escaped-pipe-aware
        if not cells or cells[0] in ("Unit",):
            continue
        if len(cells) == 6:
            out.append(dict(zip(_COLS, cells)))
        elif len(cells) == 5:  # legacy: Unit, Verdict, Reviewer, Date, Issues
            legacy = dict(zip(("unit", "verdict", "reviewer", "date", "issues"), cells))
            legacy["author"] = ""
            out.append(legacy)
    return out


def verdict_for(repo_root: Path | str, unit: str, phase: str = "delivery"):
    """The latest recorded verdict for a unit in `phase`, or None. Defaults to the
    delivery log, so the conformance `critiqued` gate is unaffected by plan-review rows."""
    target = sdlc_md.norm_id(unit)
    latest = None
    for v in read_verdicts(repo_root, phase):
        if sdlc_md.norm_id(v["unit"]) == target:
            latest = v
    return latest


def _id(value: str) -> str:
    """Normalise an author/reviewer id for comparison: case-folded, stripped, with the
    markdown escaping that `_clean` adds on write removed, so `Dani\\_Okafor` and
    `dani_okafor` compare equal. The empty-cell placeholder `-` normalises to empty,
    so a missing author is treated as no author, not a real id."""
    out = (value or "").replace("\\_", "_").strip()
    return "" if out == "-" else out.casefold()


def is_independent(verdict: dict | None) -> bool:
    """True when a verdict was authored and reviewed by distinct identities.

    Independence is the floor, not a persona feature: it holds for generic workers too.
    A verdict with no recorded author, or whose reviewer id equals its author id
    (a self-review), is NOT independent and must not clear the Done gate. The
    grandfather marker PRE_GATE is not real independence either - it is handled
    separately by is_pre_gate, so this stays a truthful test.
    """
    if not verdict:
        return False
    author = _id(verdict.get("author", ""))
    reviewer = _id(verdict.get("reviewer", ""))
    if author == PRE_GATE:
        return False
    return bool(author) and reviewer != author


def is_pre_gate(verdict: dict | None) -> bool:
    """True for a unit closed BEFORE the independence gate, under the prior
    risk-scaled policy (which permitted light-tier self-review). Marked by the
    visible PRE_GATE author sentinel from the one-time migration - auditable in the
    ledger, and never producible by the sprint loop (which stamps a real delegation
    id). These are grandfathered as conformant; the gate applies to all work closed
    after it."""
    return bool(verdict) and _id(verdict.get("author", "")) == PRE_GATE


def _declared_reviewers(repo_root: Path | str) -> list[tuple[str, str]]:
    """(role, card person-name) pairs declared under personas/seats and
    personas/amigos - the reviewers the project actually has."""
    import re as _re
    out: list[tuple[str, str]] = []
    role_re = _re.compile(r"<!--\s*role:\s*([a-z][a-z0-9-]*)\s*-->", _re.I)
    name_re = _re.compile(r"^#\s+([^-\n]+)", _re.M)
    for sub in ("seats", "amigos"):
        d = Path(repo_root) / "sdlc-studio" / "personas" / sub
        if not d.is_dir():
            continue
        for card in sorted(d.glob("*.md")):
            try:
                text = card.read_text(encoding="utf-8")
            except OSError:
                continue
            rm = role_re.search(text)
            nm = name_re.search(text)
            if rm:
                out.append((rm.group(1).lower(),
                            (nm.group(1).strip() if nm else card.stem)))
    return out


def _seat_drift_warning(repo_root: Path | str, reviewer: str) -> str | None:
    """Advisory when the reviewer names no declared seat - the persona lens
    drifting out of the critic loop must be visible, never silent. Silent on
    projects that declare no personas (headless consumers still work)."""
    import re as _re
    declared = _declared_reviewers(repo_root)
    if not declared:
        return None
    # whole-word matching only: 'production' must not claim the product seat,
    # while any token of the seat holder's name ('sam') is a seat claim
    words = set(_re.findall(r"[a-z0-9]+", reviewer.lower()))
    for role, name in declared:
        if role in words:
            return None
        if any(tok in words for tok in _re.findall(r"[a-z0-9]+", name.lower())):
            return None
    opts = ", ".join(f"{name} (role: {role})" for role, name in declared)
    return (f"reviewer '{reviewer}' matches no declared seat - the critic "
            f"should run as a review seat's render (declared: {opts}); see "
            f"reference-workflow-personas.md")


def cmd_record(args: argparse.Namespace) -> int:
    path = record_verdict(args.root, args.unit, args.verdict, args.reviewer,
                          args.author, args.issues, args.phase)
    note = "" if _id(args.author) != _id(args.reviewer) else "  (WARNING: self-review - blocked at the gate)"
    print(f"recorded {sdlc_md.norm_id(args.unit)} {args.verdict.upper()} "
          f"[{args.phase}] -> {path}{note}")
    drift = _seat_drift_warning(args.root, args.reviewer)
    if drift:
        print(f"WARNING: {drift}", file=sys.stderr)
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    if getattr(args, "format", "text") == "json":
        if args.unit:
            print(json.dumps({"unit": args.unit, "verdict": verdict_for(
                args.root, args.unit, args.phase)}, indent=2))
        else:
            print(json.dumps(read_verdicts(args.root, args.phase), indent=2))
        return 0
    if args.unit:
        v = verdict_for(args.root, args.unit, args.phase)
        print(v if v else f"no verdict for {args.unit}")
    else:
        for v in read_verdicts(args.root, args.phase):
            print(f"{v['unit']} {v['verdict']} ({v['date']})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio critic-verdict record.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record", help="Record a critic verdict for a unit.")
    r.add_argument("--unit", required=True)
    r.add_argument("--verdict", required=True, choices=("approve", "reject", "APPROVE", "REJECT"))
    r.add_argument("--reviewer", default="independent-critic")
    r.add_argument("--author", required=True,
                   help="Authoring seat / delegation id that produced the diff (must differ from --reviewer).")
    r.add_argument("--issues", default="")
    r.add_argument("--phase", choices=PHASES, default="delivery",
                   help="delivery (default, the conformance critique gate) or plan-review "
                        "(the pre-implementation AC-vs-spec check); each has its own log")
    r.add_argument("--root", default=".")
    r.set_defaults(func=cmd_record)
    s = sub.add_parser("show", help="Show the latest verdict for a unit (or all).")
    s.add_argument("--unit", default=None)
    s.add_argument("--phase", choices=PHASES, default="delivery")
    s.add_argument("--root", default=".")
    sdlc_md.add_format_arg(s)
    s.set_defaults(func=cmd_show)
    sdlc_md.add_global_root(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
