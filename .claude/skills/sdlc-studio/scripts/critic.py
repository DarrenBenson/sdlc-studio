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
import re
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
        else:
            # A row that is neither current (6 cols) nor legacy (5) - a torn write from a
            # crash mid-append. Surface it: silently dropping a verdict is a false "no
            # verdict" signal at the gate. Report and skip, never swallow.
            print(f"warning: malformed row in {path} ({len(cells)} cells, expected 6 or 5), "
                  f"skipped: {' | '.join(cells)[:100]}", file=sys.stderr)
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


# --- Two-role review gate ------------------------------------------------------------
# The seat subagent's adversarial pass is EVIDENCE (findings, reviewer seat, author) in
# its own log; the reviewer-of-record SIGN-OFF is a separate record whose principal the
# author does not control - the operator by default, or a named delegate in a separate
# trust boundary, with the delegation chain recorded. Neither substitutes for the other.
_EVIDENCE_FILE = "critic-evidence.md"
_SIGNOFF_FILE = "signoff-record.md"
_EVIDENCE_HEADER = (
    "# Critic Evidence\n\n"
    "> Append-only. The adversarial reviewer's pass per unit - findings, reviewer seat,\n"
    "> author. Evidence is INPUT to the sign-off, never the sign-off itself.\n\n"
    "| Unit | Reviewer | Author | Date | Findings |\n"
    "| --- | --- | --- | --- | --- |\n")
_SIGNOFF_HEADER = (
    "# Reviewer-of-Record Sign-offs\n\n"
    "> Append-only. The independent principal's sign-off per unit. The principal is\n"
    "> never the author nor an authoring-session subagent; a delegated sign-off\n"
    "> records the chain (delegator -> delegate, trust boundary named).\n\n"
    "| Unit | Principal | Chain | Author | Date | Note |\n"
    "| --- | --- | --- | --- | --- | --- |\n")
_EVIDENCE_COLS = ("unit", "reviewer", "author", "date", "findings")
_SIGNOFF_COLS = ("unit", "principal", "chain", "author", "date", "note")


def evidence_path(repo_root: Path | str) -> Path:
    return Path(repo_root) / "sdlc-studio" / "reviews" / _EVIDENCE_FILE


def signoff_path(repo_root: Path | str) -> Path:
    return Path(repo_root) / "sdlc-studio" / "reviews" / _SIGNOFF_FILE


def _append_row(path: Path, header: str, cells: tuple[str, ...]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(header, encoding="utf-8")
    with path.open("a", encoding="utf-8") as fh:  # append-only
        fh.write("| " + " | ".join(cells) + " |\n")
    return path


def _read_rows(path: Path, cols: tuple[str, ...]) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = sdlc_md.table_cells(line)  # escaped-pipe-aware
        if not cells or cells[0] in ("Unit",):
            continue
        if len(cells) == len(cols):
            out.append(dict(zip(cols, cells)))
    return out


def _latest_for(rows: list[dict], unit: str):
    target = sdlc_md.norm_id(unit)
    latest = None
    for r in rows:
        if sdlc_md.norm_id(r["unit"]) == target:
            latest = r
    return latest


def record_evidence(repo_root: Path | str, unit: str, reviewer: str, author: str,
                    findings: str) -> Path:
    """Append the adversarial pass as evidence. Findings must have substance -
    an empty evidence row would certify a pass that cannot be shown to have run."""
    if not (findings or "").strip():
        raise ValueError("evidence needs findings text - an empty adversarial pass "
                         "is not evidence (record what was probed, even 'none blocking')")
    if not (reviewer or "").strip() or not (author or "").strip():
        raise ValueError("evidence needs both --reviewer (the seat) and --author")
    return _append_row(evidence_path(repo_root), _EVIDENCE_HEADER,
                       (sdlc_md.norm_id(unit), _clean(reviewer), _clean(author),
                        sdlc_md.now_date(), _clean(findings)))


def evidence_for(repo_root: Path | str, unit: str):
    """The latest evidence row for a unit, or None."""
    return _latest_for(_read_rows(evidence_path(repo_root), _EVIDENCE_COLS), unit)


def _session_reviewer_ids(repo_root: Path | str, unit: str) -> set[str]:
    """Every reviewer id recorded on the unit's evidence and verdict rows - the
    authoring session's subagents. A delegate or principal drawn from this set is
    the author signing via a proxy it controls, and is refused."""
    ids: set[str] = set()
    for r in _read_rows(evidence_path(repo_root), _EVIDENCE_COLS):
        if sdlc_md.norm_id(r["unit"]) == sdlc_md.norm_id(unit):
            ids.add(_id(r["reviewer"]))
    for phase in PHASES:  # BOTH verdict phases - a plan-review seat is still the author's spawn
        for v in read_verdicts(repo_root, phase):
            if sdlc_md.norm_id(v["unit"]) == sdlc_md.norm_id(unit):
                ids.add(_id(v["reviewer"]))
    ids.discard("")
    return ids


def record_signoff(repo_root: Path | str, unit: str, principal: str, author: str,
                   delegate: str | None = None, boundary: str | None = None,
                   note: str = "") -> Path:
    """Append the reviewer-of-record sign-off for a unit.

    Direct form: `principal` (the operator by default) signs; chain is `-`.
    Delegated form: `delegate` signs on the principal's behalf - `boundary` (the
    separate trust boundary it runs in) is mandatory and the chain is recorded.
    Refusals, all loud: a principal or delegate equal to the author; a delegate
    (or effective principal) that matches any reviewer id already recorded on the
    unit's evidence/verdict rows - those are the authoring session's own subagents.
    """
    if not (principal or "").strip():
        raise ValueError("sign-off needs a --principal (the reviewer of record)")
    if not (author or "").strip():
        raise ValueError("sign-off needs the --author it is independent of")
    session_ids = _session_reviewer_ids(repo_root, unit)
    chain = "-"
    effective = principal
    if delegate is not None:
        if not (boundary or "").strip():
            raise ValueError("a delegated sign-off needs --boundary - the separate "
                             "trust boundary the delegate runs in (another session, "
                             "CI, another human)")
        if _id(delegate) == _id(author):
            raise ValueError(f"delegate {delegate!r} is the author - refused")
        if _id(delegate) in session_ids:
            raise ValueError(
                f"delegate {delegate!r} is an authoring-session subagent (it is a "
                "recorded reviewer on this unit's evidence/verdict rows) - a delegate "
                "the author controls hollows out the self-approval guard; refused")
        chain = f"{principal} -> {delegate} (boundary: {boundary})"
        effective = delegate
    if _id(effective) == _id(author):
        raise ValueError(f"principal {effective!r} is the author - a self-sign-off "
                         "never clears the gate")
    if _id(effective) in session_ids:
        raise ValueError(
            f"principal {effective!r} is an authoring-session subagent (a recorded "
            "reviewer on this unit) - the reviewer of record must sit outside the "
            "author's control; refused")
    return _append_row(signoff_path(repo_root), _SIGNOFF_HEADER,
                       (sdlc_md.norm_id(unit), _clean(effective), _clean(chain),
                        _clean(author), sdlc_md.now_date(), _clean(note) or "-"))


def signoff_for(repo_root: Path | str, unit: str):
    """The latest sign-off row for a unit, or None."""
    return _latest_for(_read_rows(signoff_path(repo_root), _SIGNOFF_COLS), unit)


def is_independent_signoff(repo_root: Path | str, unit: str, signoff: dict | None) -> bool:
    """Backstop re-check of a recorded sign-off (record_signoff refuses at write time,
    but a hand-appended row walks round the tool): the principal must be non-empty,
    differ from the recorded author, and not be an authoring-session reviewer id."""
    if not signoff:
        return False
    principal = _id(signoff.get("principal", ""))
    author = _id(signoff.get("author", ""))
    if not principal or not author or principal == author:
        return False
    return principal not in _session_reviewer_ids(repo_root, unit)


# --- Sprint-level review (one full-diff pass covers a batch) ---------------------------
# The closing adversarial pass reads the WHOLE sprint diff at once, so recording it per unit is
# false precision - it is one judgement over one range. Recorded here as evidence keyed to the
# units it covers, so the per-unit `critiqued` gate reads it as coverage for a unit that had no
# individual verdict. Coverage NEVER overrides a per-unit REJECT: a rejected unit still repairs
# per unit (a later per-unit APPROVE), because the sprint pass judged the range, not that fix.
_SPRINT_FILE = "sprint-review-record.md"
_SPRINT_HEADER = (
    "# Sprint-level Reviews\n\n"
    "> Append-only. One adversarial full-diff review covering a batch of units at close -\n"
    "> verdict, reviewer, author, and the units covered. It is coverage for the per-unit\n"
    "> critiqued gate; a per-unit REJECT still repairs per unit.\n\n"
    "| Base | Reviewer | Author | Verdict | Date | Units | Findings |\n"
    "| --- | --- | --- | --- | --- | --- | --- |\n")
_SPRINT_COLS = ("base", "reviewer", "author", "verdict", "date", "units", "findings")


def sprint_review_path(repo_root: Path | str) -> Path:
    return Path(repo_root) / "sdlc-studio" / "reviews" / _SPRINT_FILE


def record_sprint_review(repo_root: Path | str, units: list[str], reviewer: str, author: str,
                         verdict: str, findings: str, base: str = "") -> Path:
    """Record one sprint-level adversarial full-diff review over `units`.

    Independence is PROVEN, not assumed: reviewer and author are both required and must differ.
    Findings must have substance - an empty adversarial pass is not evidence. The verdict is
    APPROVE or REJECT; a REJECT is recorded (the range was reviewed and rejected) but never clears
    a unit's gate."""
    v = (verdict or "").upper()
    if v not in (APPROVE, REJECT):
        raise ValueError(f"sprint review verdict must be {APPROVE} or {REJECT}, got {verdict!r}")
    if not (reviewer or "").strip() or not (author or "").strip():
        raise ValueError("a sprint review needs both --reviewer and --author - independence is proven")
    if _id(reviewer) == _id(author):
        raise ValueError(f"reviewer {reviewer!r} == author - a sprint-level self-review never "
                         "clears the critiqued gate")
    if not (findings or "").strip():
        raise ValueError("a sprint review needs findings text - an empty adversarial pass is "
                         "not evidence (record what was probed, even 'none blocking')")
    ids = [sdlc_md.norm_id(u) for u in units if sdlc_md.norm_id(u)]
    if not ids:
        raise ValueError("a sprint review must name the units it covers")
    return _append_row(sprint_review_path(repo_root), _SPRINT_HEADER,
                       (_clean(base) or "-", _clean(reviewer), _clean(author), v,
                        sdlc_md.now_date(), _clean(" ".join(ids)), _clean(findings)))


def sprint_reviews(repo_root: Path | str) -> list[dict]:
    return _read_rows(sprint_review_path(repo_root), _SPRINT_COLS)


def _covered_ids(row: dict) -> set[str]:
    return {sdlc_md.norm_id(u) for u in re.split(r"[,\s]+", row.get("units", "")) if u.strip()}


def sprint_review_for(repo_root: Path | str, unit: str):
    """The latest sprint-level review whose covered-units list includes `unit`, or None."""
    target = sdlc_md.norm_id(unit)
    latest = None
    for r in sprint_reviews(repo_root):
        if target in _covered_ids(r):
            latest = r
    return latest


def sprint_covers_independently(repo_root: Path | str, unit: str, review: dict | None) -> bool:
    """True when a sprint-level review is a valid INDEPENDENT APPROVE covering `unit`: an APPROVE
    whose reviewer and author are both recorded and distinct. This is the evidence half of the
    two-role gate satisfied at sprint scope - the per-unit sign-off is still required separately."""
    if not review or (review.get("verdict") or "").upper() != APPROVE:
        return False
    reviewer, author = _id(review.get("reviewer", "")), _id(review.get("author", ""))
    return bool(reviewer) and bool(author) and reviewer != author


def signoff_brief(repo_root: Path | str, units: list[str], gate_note: str | None = None,
                  cost_note: str | None = None) -> str:
    """The sign-off request with the decision brief inline - per-unit deliveries,
    each unit's verdict + REJECT history, the adversarial evidence, and the gate/cost
    evidence - so the principal judges content, not counts. Absent evidence is named
    absent, never invented. Refuses an unknown unit loudly."""
    root = Path(repo_root)
    lines = ["# Reviewer-of-record sign-off request", "",
             "You are asked to sign off the units below as the independent principal.",
             "The brief is composed from the committed records - judge it, then reply.", ""]
    for unit in units:
        found = sdlc_md.find_by_id(root, unit)
        if not found:
            raise ValueError(f"no artefact with id {unit!r} - the brief only covers real units")
        path, _type = found
        text = sdlc_md.read_text_safe(path)
        uid = sdlc_md.norm_id(sdlc_md.extract_record_id(path.stem) or unit)
        title = sdlc_md.extract_h1_title(text) or uid
        points = sdlc_md.extract_field(text, "Points") or "?"
        status = sdlc_md.extract_field(text, "Status") or "?"
        lines.append(f"## {uid} ({points} pts, {status}) - {title}")
        history = [v for v in read_verdicts(root)
                   if sdlc_md.norm_id(v["unit"]) == uid]
        # A sprint-level review covering this unit is coverage, not an absence: the brief reads it
        # as such rather than reporting the unit unreviewed, so the principal sees what the one
        # full-diff pass judged instead of a false "(no verdict)" for every unit it covered.
        sprint_rev = sprint_review_for(root, uid)
        covered = sprint_covers_independently(root, uid, sprint_rev)
        if history:
            for v in history:
                marker = f"- verdict {v['verdict']} by {v['reviewer']} ({v['date']})"
                if v["verdict"] != APPROVE or (v.get("issues") or "-") != "-":
                    marker += f": {v['issues']}"
                lines.append(marker)
        elif covered:
            lines.append(f"- covered by sprint-level review ({sprint_rev['verdict']}) by "
                         f"{sprint_rev['reviewer']} ({sprint_rev['date']}) - no per-unit verdict needed")
        else:
            lines.append("- (no critic verdict recorded)")
        ev = evidence_for(root, uid)
        if ev:
            lines.append(f"- evidence: adversarial pass by {ev['reviewer']} "
                         f"({ev['date']}): {ev['findings']}")
        elif covered:
            lines.append(f"- evidence: sprint-level full-diff pass by {sprint_rev['reviewer']} "
                         f"({sprint_rev['date']}): {sprint_rev['findings']}")
        else:
            lines.append("- (no adversarial evidence recorded)")
        lines.append("")
    lines.append("## Gate evidence")
    lines.append(gate_note or "(not provided - run gate.py and pass --gate-note)")
    lines.append("")
    lines.append("## Cost evidence")
    lines.append(cost_note or "(not provided - pass --cost-note with forecast vs measured)")
    lines.append("")
    lines.append("## Your paths")
    lines.append("- APPROVE: record with `critic.py signoff --unit <id> --principal "
                 "\"<you>\" --author <author-id>` per unit")
    lines.append("- HOLD: name what must change; nothing is recorded")
    lines.append("- DELEGATE: name a principal in a separate trust boundary: "
                 "`critic.py signoff ... --delegate <name> --boundary <where>` - "
                 "the chain is recorded; the authoring session's subagents are refused")
    return "\n".join(lines)


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


_RETURN_CONTRACT = """Return EXACTLY (raw data, no wrapper):
VERDICT: APPROVE or REJECT
ISSUES: <semicolon-separated findings with file:line evidence, or 'none'>
BLOCKING: <the subset that must be fixed before Done, or 'none'>"""


def brief(repo_root: Path | str, unit: str, seat: str, tier: str = "full") -> str:
    """The seat-review prompt, assembled deterministically.

    The judgement stays with the seat; this is only the scaffolding every review
    needs - charter, unit ACs, diff scope, tier, and the exact return contract -
    so no reviewer starts from a hand-typed, drift-prone brief. Refuses an
    unknown unit or seat loudly."""
    root = Path(repo_root)
    found = sdlc_md.find_by_id(root, unit)
    if not found:
        raise ValueError(f"no artefact with id {unit!r} - brief needs a real unit")
    path, _type = found
    text = sdlc_md.read_text_safe(path)
    seats_dir = root / "sdlc-studio" / "personas" / "seats"
    card = seats_dir / f"{seat}.md"
    if not card.is_file():
        available = ", ".join(sorted(p.stem for p in seats_dir.glob("*.md"))) or "none"
        raise ValueError(f"no seat card at {card} - available seats: {available}")
    m = re.search(r"^## Acceptance Criteria\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    acs = (m.group(1).strip() if m else "(no Acceptance Criteria section - judge the diff "
                                        "against the unit's stated intent)")
    affects = sdlc_md.affects_files(text)
    scope = (", ".join(affects) if affects
             else "(no Affects declared - derive the scope from git status)")
    depth = ("Full adversarial pass: try to make each test FAIL (mutations), probe "
             "boundaries and silent-failure paths, verify claims by EXECUTION, not reading."
             if tier == "full" else
             "Lighter independent pass (mechanical/doc-tier unit): check the change does "
             "what its ACs say and nothing else; run the named suite once.")
    unit_id = sdlc_md.norm_id(sdlc_md.extract_record_id(path.stem) or unit)
    title = sdlc_md.extract_h1_title(text) or unit_id
    return f"""You are the {seat} review seat. Read and adopt the charter at
{card} (the review render). You did NOT author this diff; your job is
independent judgement of it against the ACs below - they are law, your stance never
overrides them.

Repo root: {root.resolve()}

Unit under review: {unit_id} - {title}
Artefact: {path}

Diff scope (the unit's declared Affects - inspect with git diff/status on these paths):
{scope}

Acceptance criteria (canonical - judge against THESE, not a paraphrase):
{acs}

Review depth: {depth}

{_RETURN_CONTRACT}"""


def rejoinder_brief(repo_root: Path | str, unit: str, seat: str,
                    prior_verdict_text: str, tier: str = "full") -> str:
    """The re-review brief after a REJECT's repairs: the prior VERDICT/ISSUES/BLOCKING
    quoted verbatim, the diff scope refreshed (via the standard brief), the structural
    demand to RE-EXECUTE the previously named probes and mutants, and the same return
    contract. A malformed prior-verdict block is refused loudly - a rejoinder against
    a verdict that cannot be parsed would re-review against a paraphrase. Validation
    is well-formedness only: an APPROVE prior verdict is accepted too (a legitimate
    post-approval re-review), not just the REJECT-repair loop this exists for."""
    parse_verdict_block(prior_verdict_text)  # validation only; ValueError on malformed
    base = brief(repo_root, unit, seat, tier)
    return f"""{base}

--- RE-REVIEW (rejoinder) ---

This is a RE-REVIEW after repairs to your prior verdict. Your prior verdict, verbatim:

{prior_verdict_text.strip()}

The author's repairs summary (if any) accompanies this brief separately. It is a CLAIM,
not evidence: before you may approve, RE-EXECUTE the probes and mutants your prior
verdict named - re-apply each mutant and watch its killing test FAIL, re-run each live
probe - and confirm the tree is byte-identical after your mutations. A repair whose
killing test cannot fail is vacuous; two such tests have shipped before.

Then return the SAME contract as before:

{_RETURN_CONTRACT}"""


_VERDICT_LINE = re.compile(r"^\s*VERDICT:\s*(\S+)\s*$", re.M | re.I)
_BLOCK_TOKENS = ("VERDICT", "ISSUES", "BLOCKING")


def _block_field(text: str, token: str) -> str:
    """The token's content: from `TOKEN:` to the next KNOWN token line or EOF.
    Case-insensitive both ways, and bounded only by the contract's own tokens -
    a wrapped continuation line starting `NOTE:` (or any other ALL-CAPS word)
    belongs to the field, not to a phantom next one."""
    boundary = "|".join(_BLOCK_TOKENS)
    m = re.search(rf"^\s*{token}:\s*(.*?)(?=^\s*(?:{boundary}):\s|\Z)",
                  text, re.M | re.S | re.I)
    return m.group(1).strip() if m else ""


def parse_verdict_block(text: str) -> tuple[str, str]:
    """(verdict, issues) from a returned VERDICT/ISSUES/BLOCKING block.

    Refuses (ValueError) a missing VERDICT line, a value outside APPROVE/REJECT,
    or MORE THAN ONE verdict line - an ambiguous block must never be recorded as
    a clean approval. An echoed copy of the return contract ("VERDICT: APPROVE or
    REJECT") never matches the single-token verdict line; ISSUES/BLOCKING are read
    from AFTER the verdict line, so an echo above it cannot leak placeholder text
    into the record."""
    matches = list(_VERDICT_LINE.finditer(text))
    if not matches:
        raise ValueError("no 'VERDICT:' line found in the block - the reviewer must "
                         "return the VERDICT/ISSUES/BLOCKING contract")
    if len(matches) > 1:
        raise ValueError(f"{len(matches)} VERDICT lines found - an ambiguous block is "
                         "refused, never resolved in the author's favour")
    m = matches[0]
    verdict = m.group(1).strip().upper()
    if verdict not in ("APPROVE", "REJECT"):
        raise ValueError(f"unknown verdict {verdict!r} - APPROVE or REJECT only")
    after = text[m.end():]
    issues = _block_field(after, "ISSUES")
    blocking = _block_field(after, "BLOCKING")
    if blocking and blocking.lower() != "none":
        issues = (issues + "; " if issues else "") + f"BLOCKING: {blocking}"
    return verdict, issues


def cmd_brief(args: argparse.Namespace) -> int:
    try:
        if getattr(args, "rejoinder", None):
            src = args.rejoinder
            prior = (sys.stdin.read() if src == "-"
                     else Path(src).read_text(encoding="utf-8"))
            print(rejoinder_brief(args.root, args.unit, args.seat, prior, args.tier))
        else:
            print(brief(args.root, args.unit, args.seat, args.tier))
    except (OSError, ValueError) as exc:
        print(f"brief refused: {exc}", file=sys.stderr)
        return 2
    return 0


def cmd_record(args: argparse.Namespace) -> int:
    if getattr(args, "from_verdict", None):
        if args.verdict or args.issues:
            print("record refused: --from-verdict and an explicit --verdict/--issues are "
                  "mutually exclusive - one source of truth per record", file=sys.stderr)
            return 2
        src = args.from_verdict
        try:
            raw = (sys.stdin.read() if src == "-"
                   else Path(src).read_text(encoding="utf-8"))
            verdict, issues = parse_verdict_block(raw)
        except (OSError, ValueError) as exc:
            print(f"record refused: {exc}", file=sys.stderr)
            return 2
        args.verdict, args.issues = verdict, issues
    elif not args.verdict:
        print("record refused: give --verdict, or --from-verdict FILE|- with the "
              "reviewer's returned block", file=sys.stderr)
        return 2
    path = record_verdict(args.root, args.unit, args.verdict, args.reviewer,
                          args.author, args.issues, args.phase)
    note = "" if _id(args.author) != _id(args.reviewer) else "  (WARNING: self-review - blocked at the gate)"
    print(f"recorded {sdlc_md.norm_id(args.unit)} {args.verdict.upper()} "
          f"[{args.phase}] -> {path}{note}")
    drift = _seat_drift_warning(args.root, args.reviewer)
    if drift:
        print(f"WARNING: {drift}", file=sys.stderr)
    return 0


def cmd_evidence(args: argparse.Namespace) -> int:
    findings = args.findings
    if getattr(args, "from_verdict", None):
        if findings:
            print("evidence refused: --from-verdict and --findings are mutually "
                  "exclusive - one source of truth per record", file=sys.stderr)
            return 2
        src = args.from_verdict
        try:
            raw = (sys.stdin.read() if src == "-"
                   else Path(src).read_text(encoding="utf-8"))
            verdict, issues = parse_verdict_block(raw)
        except (OSError, ValueError) as exc:
            print(f"evidence refused: {exc}", file=sys.stderr)
            return 2
        findings = f"{verdict}: {issues or 'none'}"
    try:
        path = record_evidence(args.root, args.unit, args.reviewer, args.author, findings or "")
    except ValueError as exc:
        print(f"evidence refused: {exc}", file=sys.stderr)
        return 2
    print(f"evidence recorded for {sdlc_md.norm_id(args.unit)} -> {path}")
    return 0


def cmd_signoff(args: argparse.Namespace) -> int:
    try:
        path = record_signoff(args.root, args.unit, args.principal, args.author,
                              delegate=args.delegate, boundary=args.boundary,
                              note=args.note)
    except ValueError as exc:
        print(f"signoff refused: {exc}", file=sys.stderr)
        return 2
    print(f"sign-off recorded for {sdlc_md.norm_id(args.unit)} -> {path}")
    return 0


def cmd_sprint_review(args: argparse.Namespace) -> int:
    units = [u.strip() for u in args.units.split(",") if u.strip()]
    findings = args.findings
    if getattr(args, "from_verdict", None):
        if findings:
            print("sprint-review refused: --from-verdict and --findings are mutually exclusive",
                  file=sys.stderr)
            return 2
        try:
            raw = sys.stdin.read() if args.from_verdict == "-" else Path(args.from_verdict).read_text("utf-8")
            v, issues = parse_verdict_block(raw)
        except (OSError, ValueError) as exc:
            print(f"sprint-review refused: {exc}", file=sys.stderr)
            return 2
        findings = f"{v}: {issues or 'none'}"
        args.verdict = args.verdict or v
    try:
        path = record_sprint_review(args.root, units, args.reviewer, args.author,
                                    args.verdict or "", findings or "", base=args.base or "")
    except ValueError as exc:
        print(f"sprint-review refused: {exc}", file=sys.stderr)
        return 2
    print(f"sprint-level review recorded ({args.verdict}) over {len(units)} unit(s) -> {path}")
    return 0


def cmd_signoff_brief(args: argparse.Namespace) -> int:
    units = [u.strip() for u in args.units.split(",") if u.strip()]
    if not units:
        print("signoff-brief refused: --units needs at least one unit id", file=sys.stderr)
        return 2
    try:
        print(signoff_brief(args.root, units, gate_note=args.gate_note,
                            cost_note=args.cost_note))
    except ValueError as exc:
        print(f"signoff-brief refused: {exc}", file=sys.stderr)
        return 2
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
    r.add_argument("--verdict", choices=("approve", "reject", "APPROVE", "REJECT"),
                   help="the verdict; or use --from-verdict to parse the reviewer's block")
    r.add_argument("--from-verdict", dest="from_verdict", metavar="FILE|-",
                   help="parse VERDICT/ISSUES/BLOCKING from a file (or stdin with -), refusing a malformed block")
    r.add_argument("--reviewer", default="independent-critic")
    r.add_argument("--author", required=True,
                   help="Authoring seat / delegation id that produced the diff (must differ from --reviewer).")
    r.add_argument("--issues", default="")
    r.add_argument("--phase", choices=PHASES, default="delivery",
                   help="delivery (default, the conformance critique gate) or plan-review "
                        "(the pre-implementation AC-vs-spec check); each has its own log")
    r.add_argument("--root", default=".")
    r.set_defaults(func=cmd_record)
    b = sub.add_parser("brief", help="Print the assembled seat-review prompt for a unit "
                                     "(charter + ACs + scope + return contract).")
    b.add_argument("--unit", required=True)
    b.add_argument("--seat", required=True, help="a card under sdlc-studio/personas/seats/")
    b.add_argument("--tier", choices=("full", "light"), default="full")
    b.add_argument("--rejoinder", metavar="FILE|-", default=None,
                   help="emit the RE-REVIEW brief from the prior verdict file (or stdin "
                        "with -): prior verdict quoted verbatim, re-execute-your-probes "
                        "demand, same return contract; a malformed block is refused")
    b.add_argument("--root", default=".")
    b.set_defaults(func=cmd_brief)
    e = sub.add_parser("evidence", help="Record the adversarial pass as evidence "
                                        "(findings, reviewer seat, author) - distinct from the verdict.")
    e.add_argument("--unit", required=True)
    e.add_argument("--reviewer", required=True, help="the seat that ran the adversarial pass")
    e.add_argument("--author", required=True)
    e.add_argument("--findings", default="",
                   help="what was probed and found; or use --from-verdict")
    e.add_argument("--from-verdict", dest="from_verdict", metavar="FILE|-",
                   help="record the returned VERDICT/ISSUES/BLOCKING block as the findings")
    e.add_argument("--root", default=".")
    e.set_defaults(func=cmd_evidence)
    so = sub.add_parser("signoff", help="Record the reviewer-of-record sign-off "
                                        "(independent principal; optional named delegate with chain).")
    so.add_argument("--unit", required=True)
    so.add_argument("--principal", required=True,
                    help="the reviewer of record (the operator by default)")
    so.add_argument("--author", required=True)
    so.add_argument("--delegate", default=None,
                    help="a named delegate signing on the principal's behalf")
    so.add_argument("--boundary", default=None,
                    help="the delegate's separate trust boundary (required with --delegate)")
    so.add_argument("--note", default="")
    so.add_argument("--root", default=".")
    so.set_defaults(func=cmd_signoff)
    sr = sub.add_parser("sprint-review", help="Record one adversarial full-diff review covering "
                                              "a batch of units - coverage for the per-unit "
                                              "critiqued gate.")
    sr.add_argument("--units", required=True, help="comma-separated unit ids the review covers")
    sr.add_argument("--reviewer", required=True, help="the independent reviewer (the QA seat)")
    sr.add_argument("--author", required=True, help="the author the review is independent of")
    sr.add_argument("--verdict", default=None, choices=("APPROVE", "REJECT"),
                    help="the review verdict (or read from --from-verdict's block)")
    sr.add_argument("--findings", default=None, help="what the adversarial pass probed")
    sr.add_argument("--from-verdict", dest="from_verdict", default=None,
                    help="read the VERDICT/ISSUES block from a file (or - for stdin)")
    sr.add_argument("--base", default=None, help="the diff base ref the review covered (advisory)")
    sr.add_argument("--root", default=".")
    sr.set_defaults(func=cmd_sprint_review)
    sb = sub.add_parser("signoff-brief", help="Print the sign-off request with the "
                                              "decision brief inline (deliveries, verdict history, evidence).")
    sb.add_argument("--units", required=True, help="comma-separated unit ids")
    sb.add_argument("--gate-note", dest="gate_note", default=None)
    sb.add_argument("--cost-note", dest="cost_note", default=None)
    sb.add_argument("--root", default=".")
    sb.set_defaults(func=cmd_signoff_brief)
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
