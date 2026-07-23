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
from lib import run_state, sdlc_md  # noqa: E402

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
    _write_verdict_row(path, row)
    return path


def _write_verdict_row(path: Path, row: str) -> None:
    """Add a verdict row, keeping the table one contiguous block.

    With no supersession section present this is a plain O_APPEND write, byte-identical to
    what it has always done. Once records have been added below the table, the row goes in
    after the last table line instead, so the table does not acquire a paragraph in the
    middle of it. Nothing already written is removed or altered either way.
    """
    text = path.read_text(encoding="utf-8")
    if SUPERSEDE_HEADING not in text:
        with path.open("a", encoding="utf-8") as fh:  # append-only
            fh.write(row)
        return
    lines = text.splitlines(keepends=True)
    table = [i for i, line in enumerate(lines) if line.lstrip().startswith("|")]
    if not table:
        with path.open("a", encoding="utf-8") as fh:
            fh.write(row)
        return
    last = table[-1]
    if not lines[last].endswith("\n"):
        lines[last] += "\n"
    lines.insert(last + 1, row)
    path.write_text("".join(lines), encoding="utf-8")


def read_verdicts(repo_root: Path | str, phase: str = "delivery") -> list[dict]:
    """All recorded verdicts for `phase`, in order, as
    {unit, verdict, reviewer, author, date, issues} plus the supersession annotation
    {superseded, superseded_reason, superseded_by, superseded_at}.

    Reads both the current 6-column rows and any legacy 5-column rows (no Author) that
    pre-date the independence gate; a legacy row's author is the empty string. A retired
    row is still returned, marked - dropping it would lose the record that it happened,
    which is the reason the log is append-only in the first place.
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
    return _annotate_superseded(out, read_supersessions(repo_root, phase))


def verdict_for(repo_root: Path | str, unit: str, phase: str = "delivery"):
    """The latest LIVE recorded verdict for a unit in `phase`, or None. Defaults to the
    delivery log, so the conformance `critiqued` gate is unaffected by plan-review rows.

    A superseded row is skipped: it records an event that a named authoriser has ruled did
    not happen, so acting on it would be acting on a known-false fact. A unit whose only row
    is superseded therefore has NO verdict, which is different from having an approval.
    """
    target = sdlc_md.norm_id(unit)
    latest = None
    for v in read_verdicts(repo_root, phase):
        if sdlc_md.norm_id(v["unit"]) == target and not v.get("superseded"):
            latest = v
    return latest


# --- Supersession (a verdict row retired by addition) ----------------------------------
# A verdict row can record an event that did not happen - a reviewer mis-entered, a verdict
# filed against the wrong unit. The log's authority comes from nobody editing it, so the
# correction is made by ADDING a record that retires the row, never by deleting the row or
# widening it with another column (the row parser reads 6 or 5 cells and warns on anything
# else, so a 7th column would turn every row into a torn-write warning). The record is
# written below the table as prose for the same reason: a pipe-delimited erratum would be
# read as a malformed verdict.
SUPERSEDE_HEADING = "## Supersessions"
_SUPERSEDE_INTRO = (
    "\n" + SUPERSEDE_HEADING + "\n\n"
    "> Appended, never edited in place. Each record retires one verdict row above: the row\n"
    "> stays in the table and every reader marks it superseded, so the log is corrected by\n"
    "> addition. Prose, not a table - the row parser reads every pipe-delimited line here.\n\n")
#: Record fields, in write order. Also the parse boundary: a value runs to the next of these
#: keys, so a reason containing punctuation (or a semicolon-separated agent id) stays whole.
_SUPERSEDE_KEYS = ("unit", "row-date", "row-verdict", "row-reviewer", "row-author",
                   "authorised-by", "reason", "recorded")
_SUPERSEDE_COLS = ("unit", "row_date", "row_verdict", "row_reviewer", "row_author",
                   "authorised_by", "reason", "recorded")
_SUPERSEDE_PREFIX = "SUPERSEDED "


def _supersede_value(value: str, escape: bool = True) -> str:
    """One field of a supersession record: single-line, pipe-free (so no reader mistakes it
    for a table row), and with any embedded ` key=` sequence defused to ` key:` so free prose
    cannot forge a field boundary. `escape` off for a value copied from a table cell, which
    already carries the markdown escaping `_clean` applies - doubling it would store a value
    that no longer reads back as what the row says."""
    out = _clean(value) if escape else value.replace("|", "/").replace("\n", " ").strip()
    for key in _SUPERSEDE_KEYS:
        out = out.replace(f" {key}=", f" {key}:")
    return " ".join(out.split())


def _supersede_field(body: str, key: str) -> str:
    boundary = "|".join(re.escape(k) for k in _SUPERSEDE_KEYS)
    m = re.search(rf"(?:^|\s){re.escape(key)}=(.*?)(?=\s(?:{boundary})=|$)", body)
    return m.group(1).strip().replace("\\_", "_") if m else ""


def read_supersessions(repo_root: Path | str, phase: str = "delivery") -> list[dict]:
    """Every supersession record in `phase`'s log, in order, as
    {unit, row_date, row_verdict, row_reviewer, row_author, authorised_by, reason, recorded}."""
    path = verdicts_path(repo_root, phase)
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith(_SUPERSEDE_PREFIX):
            continue
        body = stripped[len(_SUPERSEDE_PREFIX):]
        out.append({col: _supersede_field(body, key)
                    for col, key in zip(_SUPERSEDE_COLS, _SUPERSEDE_KEYS)})
    return out


def _matches_supersession(row: dict, rec: dict) -> bool:
    return (sdlc_md.norm_id(row.get("unit", "")) == sdlc_md.norm_id(rec.get("unit", ""))
            and row.get("date", "") == rec.get("row_date", "")
            and (row.get("verdict", "") or "").upper() == (rec.get("row_verdict", "") or "").upper()
            and _id(row.get("reviewer", "")) == _id(rec.get("row_reviewer", "")))


def _annotate_superseded(rows: list[dict], records: list[dict]) -> list[dict]:
    """Mark each row a supersession record retires. Every row carries the four keys, so a
    reader never has to tell 'live' from 'field absent'."""
    for row in rows:
        rec = next((r for r in records if _matches_supersession(row, r)), None)
        row["superseded"] = rec is not None
        row["superseded_reason"] = rec["reason"] if rec else ""
        row["superseded_by"] = rec["authorised_by"] if rec else ""
        row["superseded_at"] = rec["recorded"] if rec else ""
    return rows


def is_superseded(verdict: dict | None) -> bool:
    """True when a verdict row has been retired by a recorded supersession."""
    return bool(verdict) and bool(verdict.get("superseded"))


def record_supersession(repo_root: Path | str, unit: str, date: str, reason: str,
                        authorised_by: str, reviewer: str | None = None,
                        verdict: str | None = None, phase: str = "delivery") -> Path:
    """Retire one verdict row by appending a supersession record naming it.

    The row is identified by unit and date, narrowed with `reviewer` and `verdict` when a
    unit carries more than one row that day. Refusals, all loud and all writing nothing:

    - no row matches, or more than one does - a correction pointing at nothing (or at an
      unspecified one of several) is a false erratum;
    - no authoriser, or an authoriser who is the row's own AUTHOR - the party that wrote the
      wrong row cannot retire it on its own say-so. The row's REVIEWER is not refused: a row
      that names the wrong reviewer is precisely the case this exists for, and the person
      wrongly named is usually the one who can rule that the pass never ran;
    - no reason.
    """
    if phase not in PHASES:
        raise ValueError(f"unknown critic phase {phase!r} - expected one of {PHASES}")
    if not (reason or "").strip():
        raise ValueError("a supersession needs a --reason - retiring a recorded event "
                         "without stating why is the quiet rewrite this log exists to prevent")
    if not (authorised_by or "").strip():
        raise ValueError("a supersession needs --authorised-by naming who authorised it - "
                         "an unauthorised correction to an append-only log is a hand edit "
                         "with extra steps")
    target, want_date = sdlc_md.norm_id(unit), (date or "").strip()
    candidates = [v for v in read_verdicts(repo_root, phase)
                  if sdlc_md.norm_id(v["unit"]) == target and v["date"] == want_date]
    if reviewer:
        candidates = [v for v in candidates if _id(v["reviewer"]) == _id(reviewer)]
    if verdict:
        candidates = [v for v in candidates if v["verdict"].upper() == verdict.upper()]
    if not candidates:
        dates = sorted({v["date"] for v in read_verdicts(repo_root, phase)
                        if sdlc_md.norm_id(v["unit"]) == target})
        seen = f"rows dated {', '.join(dates)}" if dates else "no rows at all"
        raise ValueError(f"no {phase} verdict row for {target} dated {want_date!r} "
                         f"(that unit has {seen}) - a supersession that points at nothing "
                         f"is a false erratum; nothing written")
    if len(candidates) > 1:
        raise ValueError(
            f"{len(candidates)} {phase} verdict rows match {target} dated {want_date} - "
            f"narrow it with --reviewer and/or --verdict; retiring an unspecified one of "
            f"several is not a correction")
    row = candidates[0]
    if _id(authorised_by) == _id(row["author"]):
        raise ValueError(
            f"authoriser {authorised_by!r} is the row's own author - the party that wrote "
            f"the row cannot authorise retiring it; name an authoriser outside it")
    path = verdicts_path(repo_root, phase)
    record = _SUPERSEDE_PREFIX + " ".join(
        f"{key}={value}" for key, value in zip(_SUPERSEDE_KEYS, (
            sdlc_md.norm_id(row["unit"]), row["date"], row["verdict"].upper(),
            _supersede_value(row["reviewer"], escape=False),
            _supersede_value(row["author"] or "-", escape=False),
            _supersede_value(authorised_by), _supersede_value(reason), sdlc_md.now_date())))
    text = path.read_text(encoding="utf-8")
    with path.open("a", encoding="utf-8") as fh:  # append-only, below the table
        if SUPERSEDE_HEADING not in text:
            fh.write(_SUPERSEDE_INTRO)
        else:
            fh.write("\n")
        fh.write(record + "\n")
    return path


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
    """The table's DATA rows. The markdown header is identified by matching the whole cell
    tuple against the declared column names, not by a first-column literal: the previous
    check knew only `Unit`, so a table led by any other column (the sprint-review table's
    `Base`) returned its own header as data. Matching every column generalises to each table
    this serves and cannot lapse when the next one is added."""
    if not path.exists():
        return []
    header = tuple(c.strip().lower() for c in cols)
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = sdlc_md.table_cells(line)  # escaped-pipe-aware
        if not cells or len(cells) != len(cols):
            continue
        if tuple(c.strip().lower() for c in cells) == header:
            continue
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
    """Every reviewer id recorded on the unit's evidence, verdict, and sprint-level-review rows.
    A delegate or principal drawn from this set is a reviewer signing off its own review (or the
    author's proxy), and is refused: the reviewer-of-record must differ from BOTH the author and
    the adversarial reviewer, per-unit or sprint-scope alike.

    A SUPERSEDED verdict row contributes nothing: an authorised record says the review it names
    never happened, so treating its reviewer as one of the author's own would strand the unit on
    the strength of a fact that has been ruled untrue."""
    target = sdlc_md.norm_id(unit)
    ids: set[str] = set()
    for r in _read_rows(evidence_path(repo_root), _EVIDENCE_COLS):
        if sdlc_md.norm_id(r["unit"]) == target:
            ids.add(_id(r["reviewer"]))
    for phase in PHASES:  # BOTH verdict phases - a plan-review seat is still the author's spawn
        for v in read_verdicts(repo_root, phase):
            if sdlc_md.norm_id(v["unit"]) == target and not v.get("superseded"):
                ids.add(_id(v["reviewer"]))
    for sr in sprint_reviews(repo_root):  # a sprint-level review covering this unit
        if target in _covered_ids(sr):
            ids.add(_id(sr["reviewer"]))
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
                         verdict: str, findings: str, base: str = "",
                         tokens: int | None = run_state.UNMEASURED,
                         repaired: list[dict] | None = None) -> Path:
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
    written = _append_row(sprint_review_path(repo_root), _SPRINT_HEADER,
                          (_clean(base) or "-", _clean(reviewer), _clean(author), v,
                           sdlc_md.now_date(), _clean(" ".join(ids)), _clean(findings)))
    # The review IS the round. Recorded after the row is written, so a run-state failure can
    # never cost us the evidence; and skipped entirely when no run is open, which leaves the
    # review recorded and nothing counted against a run that has no identity to count against.
    run_state.record_review_round(repo_root, verdict=v, units=ids, reviewer=_clean(reviewer),
                                  tokens=tokens, repaired=repaired)
    return written


def sprint_reviews(repo_root: Path | str) -> list[dict]:
    return _read_rows(sprint_review_path(repo_root), _SPRINT_COLS)


# The shipped ceiling on close-review rounds. Three is the point past which this project's own
# history stops paying: RUN-01KXVYGR ran five, and rounds 2, 3 and 4 each had a MAJOR created
# by the previous round's repair. It is a stop-and-ask, never a hard refusal - the operator can
# buy another round, but must do it deliberately and on the record.
DEFAULT_REVIEW_CEILING = 3


def review_ceiling(repo_root: Path | str) -> int:
    """The configured round ceiling (`review.max_rounds`), or the shipped default.

    Read through `project_override`, which degrades fully: a missing config, absent PyYAML or
    malformed YAML all fall back to the default rather than breaking a close. A non-integer or
    non-positive setting is ignored the same way - a ceiling of 0 would refuse the FIRST round
    and make the close unrunnable."""
    raw = sdlc_md.project_override(repo_root, "review.max_rounds", DEFAULT_REVIEW_CEILING)
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return DEFAULT_REVIEW_CEILING
    return value if value > 0 else DEFAULT_REVIEW_CEILING


# How a round-N finding relates to round N-1's repair. The distinction is the whole point:
# a FRESH finding says the review is still earning its cost, a REPAIR_REGRESSION says the
# repair loop is manufacturing the defects the review is being paid to catch, and those two
# call for opposite responses. UNCLASSIFIED is neither, and is never quietly folded into
# FRESH - a regression hidden inside the fresh count is the failure this exists to prevent.
FRESH = "fresh"
REPAIR_REGRESSION = "repair-regression"
UNCLASSIFIED = "unclassified"


def _spans(entry: dict) -> list[tuple[int, int]]:
    """The (start, end) line spans of one repaired-file entry, malformed pairs dropped."""
    out = []
    for pair in entry.get("lines") or []:
        try:
            start, end = int(pair[0]), int(pair[1])
        except (TypeError, ValueError, IndexError):
            continue
        out.append((start, end) if start <= end else (end, start))
    return out


def classify_finding(repo_root: Path | str, file: str | None = None,
                     line: int | None = None) -> dict:
    """Classify a finding against the PREVIOUS round's repair surface.

    Compared against the latest recorded round only. An earlier round's surface has already
    been re-reviewed by the round after it, so a finding there now is a fresh miss rather
    than a defect the last repair created.

    Matching is file AND line, not file alone: single files here run to thousands of lines,
    and a file-level match would classify nearly every finding as a regression, which would
    make the signal useless in exactly the case it exists for."""
    rounds = run_state.review_rounds(repo_root)
    if not rounds:
        return {"class": FRESH, "round": None, "file": file, "line": line,
                "reason": "no prior round: there is no repair surface to regress against"}
    if not file or line is None:
        return {"class": UNCLASSIFIED, "round": None, "file": file, "line": line,
                "reason": "the finding has no parseable file and line, so it cannot be placed "
                          "inside or outside the previous round's repair surface"}
    try:
        line = int(line)
    except (TypeError, ValueError):
        return {"class": UNCLASSIFIED, "round": None, "file": file, "line": line,
                "reason": f"the finding's line {line!r} is not a number"}
    last = rounds[-1]
    target = Path(str(file)).name
    for entry in last.get("repaired") or []:
        if not isinstance(entry, dict) or Path(str(entry.get("file", ""))).name != target:
            continue
        for start, end in _spans(entry):
            if start <= line <= end:
                return {"class": REPAIR_REGRESSION, "round": last.get("round"),
                        "file": file, "line": line,
                        "reason": f"{target}:{line} lies in the surface round "
                                  f"{last.get('round')}'s repair touched ({start}-{end})"}
    return {"class": FRESH, "round": last.get("round"), "file": file, "line": line,
            "reason": f"{target}:{line} lies outside round {last.get('round')}'s repair surface"}


# What must never reach a reviewer's brief, because it predicts a conclusion rather than
# describing the work: the prior verdict words, severity labels that pre-grade what will be
# found, a round number (which says "others already rejected this"), and any sentence asserting
# what the reviewer is about to conclude. Checked mechanically, so a future edit that
# reintroduces priming fails the suite rather than relying on a reader noticing.
_PRIMING = (
    (re.compile(r"\b(REJECT|APPROVE)\b"), "a prior verdict word"),
    (re.compile(r"\b(MAJOR|MINOR|BLOCKING)\b"), "a severity label that pre-grades the finding"),
    (re.compile(r"(?i)\bround\s*\d+\b"), "a round number"),
    (re.compile(r"(?i)the pattern will continue|you will find|expect to find|"
                r"as in the previous round"), "an asserted conclusion"),
)

# A probe is a thing the reviewer must RE-EXECUTE: a test path or node, or a file:line the
# prior round mutated. These are facts, and they must survive into a re-review - the round-2
# APPROVE this project trusts was earned by a reviewer re-running exactly these. What must not
# survive is the prose around them.
_PROBE = re.compile(r"(?:[\w./-]+\.(?:py|sh|ts|js|go|md)(?::\d+)?"
                    r"(?:::[\w:]+)?|\b(?:pytest|jest|vitest|go test)\s+[\w./:-]+)")


def neutrality_violations(text: str) -> list[str]:
    """Every priming class present in `text`. Empty means the brief is neutral.

    The RETURN CONTRACT is excluded before checking. It necessarily contains both verdict words
    and the BLOCKING label, because it is the reply format the reviewer must follow - offering
    the vocabulary as a required choice is not priming, and stripping it to satisfy this check
    would break the contract. Priming is a prior verdict ASSERTED, which is what remains once
    the contract is removed.

    Mechanical by design: a reviewer's impression of neutrality is exactly the judgement this
    exists to remove from the loop."""
    body = (text or "").replace(_RETURN_CONTRACT, "")
    return [why for rx, why in _PRIMING if rx.search(body)]


def extract_probes(prior_verdict_text: str) -> list[str]:
    """The probes a prior verdict named, as a bare list of things to re-execute.

    Refuses loudly when none can be extracted. A re-review that silently dropped the
    re-execution demand would approve against a brief WEAKER than the one it replaced, which
    is worse than the priming this strips - so absence is an error, never an empty list."""
    found, seen = [], set()
    for m in _PROBE.finditer(prior_verdict_text or ""):
        probe = m.group(0)
        if probe not in seen:
            seen.add(probe)
            found.append(probe)
    if not found:
        raise ValueError(
            "no probe could be extracted from the prior verdict - a re-review must carry the "
            "checks to re-execute, and one that drops them silently is weaker than the review "
            "it replaces. Name the tests and file:line mutants in the verdict, or run a fresh "
            "review rather than a re-review.")
    return found


def neutral_brief(repo_root: Path | str, unit: str, seat: str, tier: str = "full",
                  prior: str | None = None, round_number: int | None = None) -> str:
    """The reviewer's brief, carrying the diff and risk surface but none of the framing that
    predicts a conclusion.

    `round_number` is accepted and deliberately NOT rendered: callers hold it, and silently
    ignoring an argument would be worse than refusing one - this way the caller cannot leak it
    by passing it. When `prior` is given, the probes it named travel as a neutral checklist;
    the verdict prose, severity labels and conclusions around them do not."""
    base = brief(repo_root, unit, seat, tier)
    if prior is None:
        return base
    probes = extract_probes(prior)          # raises rather than dropping the demand
    listed = "\n".join(f"  - {p}" for p in probes)
    return (f"{base}\n\n--- CHECKS TO RE-EXECUTE ---\n\n"
            f"Before concluding, re-execute each of the following and record what you observed. "
            f"Re-apply each named mutant and confirm its killing test fails; re-run each named "
            f"test. Confirm the tree is byte-identical afterwards.\n\n{listed}\n")


def round_cost_report(repo_root: Path | str) -> str:
    """What the close review has cost so far, per round and cumulatively.

    An unmeasured round is NAMED and the total is marked PARTIAL rather than the round being
    summed as zero: a total that quietly absorbs an unmeasured round reads cheaper than the
    run actually was, and this number exists to be weighed against buying another round. A
    measured zero is a different fact from an unmeasured round and reads differently."""
    rounds = run_state.review_rounds(repo_root)
    if not rounds:
        return "no review rounds recorded for this run - no cost to report"
    lines, total, unmeasured = [], 0, 0
    for r in rounds:
        tokens = r.get("tokens", run_state.UNMEASURED)
        if tokens is run_state.UNMEASURED or tokens is None:
            unmeasured += 1
            lines.append(f"  round {r.get('round')}: unmeasured ({r.get('verdict', '?')})")
        else:
            total += int(tokens)
            lines.append(f"  round {r.get('round')}: {int(tokens):,} tokens "
                         f"({r.get('verdict', '?')})")
    if unmeasured:
        tail = (f"  total: {total:,} tokens across {len(rounds) - unmeasured} of "
                f"{len(rounds)} round(s) - PARTIAL, {unmeasured} unmeasured and never "
                f"counted as zero")
    else:
        tail = f"  total: {total:,} tokens across {len(rounds)} round(s)"
    return "\n".join([*lines, tail])


def next_round_offer(repo_root: Path | str, ceiling: int | None = None) -> str:
    """The text put in front of the operator when another round is on the table: what the
    rounds so far cost, how many there have been, and the ceiling they are counting towards.
    'Is the next round worth buying' is then a question asked against a number."""
    limit = review_ceiling(repo_root) if ceiling is None else ceiling
    count = run_state.review_round_count(repo_root)
    return (f"review rounds so far: {count} of a ceiling of {limit}\n"
            f"{round_cost_report(repo_root)}")


# The three ways out of a self-feeding repair loop. Another patch round is deliberately NOT
# among them: on a repair regression the patching is the cause, so offering more of it is the
# one response the evidence rules out. Escalating is a decision someone makes, which is the
# whole point - a round nobody chose is how a loop runs to five.
ESCALATIONS = ("revert", "redesign", "accept-and-file")


def escalation_for(repo_root: Path | str, finding: dict) -> dict:
    """The escalation brief for a repair-regression finding: three named options, each with
    the consequence of taking it, and the round and files that triggered it named so the
    choice is not blind.

    Refuses a finding that is not a repair regression - escalating a fresh finding would spend
    the circuit breaker on the case the review is supposed to handle normally."""
    if (finding or {}).get("class") != REPAIR_REGRESSION:
        raise ValueError(
            f"escalation is for a {REPAIR_REGRESSION} finding; this one is "
            f"{(finding or {}).get('class', 'missing')!r}. A fresh finding is repaired, not "
            f"escalated - the loop is still earning its cost.")
    rounds = run_state.review_rounds(repo_root)
    last = rounds[-1] if rounds else {}
    files = ", ".join(sorted({str(e.get("file")) for e in (last.get("repaired") or [])
                              if isinstance(e, dict) and e.get("file")})) or "(none recorded)"
    rnd = finding.get("round")
    return {
        "finding": finding,
        "round": rnd,
        "options": [
            {"label": "revert",
             "consequence": f"undo round {rnd}'s repair, returning {files} to its state before "
                            f"that round, and re-review from there. The defect the repair "
                            f"targeted comes back and is re-decided with the regression known."},
            {"label": "redesign",
             "consequence": "stop patching this surface and rework the approach. Costs the most "
                            "now and is the only option that addresses a repair loop whose "
                            "successive fixes keep colliding in the same place."},
            {"label": "accept-and-file",
             "consequence": "accept the current state, file the finding as its own tracked "
                            "artefact linked to this run, and close. The defect is recorded "
                            "rather than fixed, and the run closes honestly with it outstanding."},
        ],
    }


def record_escalation(repo_root: Path | str, choice: str, finding: dict, **fields) -> dict:
    """Record the operator's escalation choice against the run, with the regression that
    triggered it. For `accept-and-file`, mints a real linked artefact through the shared filer
    and reports its id - never a prose note claiming something was filed."""
    if choice not in ESCALATIONS:
        raise ValueError(f"unknown escalation {choice!r} - expected one of "
                         f"{', '.join(ESCALATIONS)}")
    filed = None
    if choice == "accept-and-file":
        import file_finding  # noqa: PLC0415 - optional at import time, required only here
        res = file_finding.file_finding(repo_root, "bug", fields.pop("title"), fields)
        filed = res["id"]
    entry = {"choice": choice, "round": finding.get("round"), "finding": finding,
             "filed": filed, "recorded_at": sdlc_md.now_iso8601()}

    def _append(state: dict) -> dict:
        existing = state.get("escalations")
        state["escalations"] = ([e for e in existing if isinstance(e, dict)]
                                if isinstance(existing, list) else []) + [entry]
        return state

    run_state._mutate(repo_root, _append)  # noqa: SLF001 - the module's own mutation path
    return entry


def defer_escalation(repo_root: Path | str, unit: str, finding: dict) -> dict:
    """The autonomous path: record the escalation as a pending operator decision and leave it
    unresolved. It never selects an option - a circuit breaker that picks its own answer is
    not a circuit breaker. Reuses the deferred-decision queue rather than adding a second
    pending-decision mechanism, so the close asks this alongside everything else, once."""
    brief = escalation_for(repo_root, finding)
    entry = {"unit": sdlc_md.norm_id(unit) or unit,
             "question": f"round {brief['round']}'s repair created this finding "
                         f"({finding.get('reason', '')}). Patching again is what produced it - "
                         f"how should the loop exit?",
             "options": brief["options"], "recommend": None,
             "deferred_at": sdlc_md.now_iso8601(), "resolution": None}

    def _append(state: dict) -> dict:
        pending = state.get("pending_decisions")
        state["pending_decisions"] = ([p for p in pending if isinstance(p, dict)]
                                      if isinstance(pending, list) else []) + [entry]
        return state

    run_state._mutate(repo_root, _append)  # noqa: SLF001
    return entry


def review_round_guard(repo_root: Path | str, ceiling: int | None = None,
                       override: bool = False) -> int:
    """Refuse a further close-review round once `ceiling` rounds are recorded, unless the
    operator overrides explicitly. Returns the rounds recorded so far.

    The refusal names the count, the ceiling and the override, because a gate whose remedy is
    not in its message sends the reader round a loop with no exit. An override is RECORDED, so
    the retro can read that the ceiling was passed and at which round."""
    limit = review_ceiling(repo_root) if ceiling is None else ceiling
    count = run_state.review_round_count(repo_root)
    if count < limit:
        return count
    if not override:
        raise ValueError(
            f"the close review has recorded {count} round(s), reaching the ceiling of {limit} "
            f"(review.max_rounds). This project's rounds past three have historically found "
            f"defects its own repairs created, not fresh ones - check the repair-regression "
            f"report before buying another. To proceed deliberately, re-run with the override.")
    run_state.record_ceiling_override(repo_root, at_round=count, ceiling=limit)
    return count


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
                marker += _superseded_suffix(v)  # a retired row is shown, and shown retired
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


#: The explicit token for a repair that executed NO plan - the repair-plan gate is off, or a
#: repair was made without one. Recorded so a reader can tell a planned repair from an
#: unplanned one, and so an ABSENT field (which reads as missing data) is never mistaken for a
#: planned repair whose id was dropped (US0314).
REPAIR_UNPLANNED = "repair:unplanned"


def repair_provenance(plan_id: str | None) -> str:
    """The provenance token a repair records, for the `issues` field of its delivery verdict
    or its review-round entry. A named plan yields `repair:plan=<id>`; the absence of one
    yields REPAIR_UNPLANNED, explicitly, never the empty string - an empty field reads as
    missing data and a reader cannot tell it apart from a planned repair whose id was lost."""
    pid = " ".join(str(plan_id or "").split())
    return f"repair:plan={pid}" if pid else REPAIR_UNPLANNED


def repair_plan_of(issues: str | None) -> str | None:
    """The plan id a recorded repair executed, or None when it was recorded unplanned. Reads
    the token `repair_provenance` wrote. Distinguishes 'unplanned, on the record' (returns
    None but REPAIR_UNPLANNED was present) from 'no provenance recorded at all'."""
    import re as _re
    m = _re.search(r"repair:plan=(\S+)", str(issues or ""))
    return m.group(1) if m else None


def is_planned_repair(issues: str | None) -> bool:
    """True only when a repair recorded a named plan. An unplanned repair - even one honestly
    marked REPAIR_UNPLANNED - is not a planned repair, and a repair with no provenance token
    at all is not one either."""
    return repair_plan_of(issues) is not None


# EP0113: the carry-forward review policy lives in its own module; re-exported here so the
# review-policy discipline is reachable through the critic surface the tests and gate use.
try:
    import carry_forward as _carry_forward  # noqa: E402
    review_policy = _carry_forward.review_policy
    validate_carried = _carry_forward.validate_carried
    reject_carries_forward = _carry_forward.reject_carries_forward
    is_narrative_downgrade = _carry_forward.is_narrative_downgrade
    REVIEW_POLICIES = _carry_forward.POLICIES
    PolicyError = _carry_forward.PolicyError
except ImportError:  # pragma: no cover - partial install
    _carry_forward = None


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


# --- Standing review-brief practices ---------------------------------------------------
# The three practices that produced this project's highest-value findings, each a STANDING
# instruction carried in every reviewer brief with the reason it exists beside it. All three
# were improvised mid-sprint rather than drawn from anything shipped, so they depended on
# whoever wrote the brief remembering them - the party the review exists to check. Woven into
# every brief so they no longer do. `missing_practices` proves both halves are present: a
# practice named without its reason is the half a fresh reviewer drops first.
_REVIEW_PRACTICES_BLOCK = """--- STANDING REVIEW PRACTICES (each with the reason it exists) ---

On a REPAIR review, rule each previous finding CLOSED, OVER-CLAIMED or MOVED - a general
'review the repair' answer blurs the three into one impression, and a MOVED defect is one that
survived, not one that closed.

Mutate the author's TESTS, not only the code: a shape list drawn from the families where two
implementations agree by construction passes every mutant while proving nothing, and reading
the code never finds that.

When a mutant SURVIVES, re-test its branch in ISOLATION before drawing any conclusion from it:
a sibling guard masked a survivor three separate times in one sprint, and each time the truth
appeared only when the branch was exercised alone - a survivor is evidence about the harness,
not about the test."""

# Each practice: (name, instruction-regex, reason-regex). Both must be present in a brief for
# the practice to count as carried; the reason clause is the half worth keeping. Searched over
# the whitespace-normalised brief, and `[^.]*` keeps each match inside one sentence so an
# instruction in one place and a reason in another do not pair by accident.
_BRIEF_PRACTICES = (
    ("per-item repair verdict",
     r"rule each previous finding[^.]*CLOSED[^.]*OVER-CLAIMED[^.]*MOVED",
     r"blurs?[^.]*into one impression"),
    ("mutate the author's tests",
     r"mutate the author'?s TESTS[^.]*not only the code",
     r"agree by construction"),
    ("isolation re-test of a survivor",
     r"re-test[^.]*in ISOLATION[^.]*before drawing any conclusion",
     r"sibling guard[^.]*masked"),
)

# The four prose surfaces the claim-inventory first pass must cover. A pass that omits one
# exempts it, and a Resolution is the artefact no test can fail - the cheapest thing in the
# diff to check and the likeliest to be wrong.
CLAIM_SURFACES = ("Resolutions", "docstrings", "comments", "CHANGELOG")
_CLAIM_INVENTORY_BLOCK = """--- CLAIM INVENTORY (run this FIRST, before the logic review) ---

Before reading the logic, enumerate every assertion the diff's prose makes across all four
surfaces - Resolutions, docstrings, comments and CHANGELOG entries - and mark each TRUE, FALSE
or UNVERIFIABLE against the code. A Resolution is the one artefact no test can fail, so it is
the cheapest thing here to check and the likeliest to be wrong. A claim no command can settle
is UNVERIFIABLE, reported as such and counted on trust, never assumed TRUE."""


def _normalise_brief(text: str) -> str:
    """Collapse whitespace so a practice or surface wrapped across brief lines still matches."""
    return re.sub(r"\s+", " ", (text or "")).strip()


def missing_practices(brief_text: str) -> list[str]:
    """The standing review practices a brief fails to carry, by name. Empty means all three are
    present with their reasons. A practice whose instruction is present but whose reason clause
    is not still counts as missing - the reason is what survives into a fresh reviewer's head."""
    body = _normalise_brief(brief_text)
    absent = []
    for name, instruction, reason in _BRIEF_PRACTICES:
        if not (re.search(instruction, body, re.I) and re.search(reason, body, re.I)):
            absent.append(name)
    return absent


def assert_brief_practices(brief_text: str) -> None:
    """Refuse a brief missing any of the three standing practices, naming which. A brief that
    omits one leaves it to whoever wrote the brief to remember, which is how all three were
    improvised rather than shipped - so it is refused, never issued."""
    absent = missing_practices(brief_text)
    if absent:
        raise ValueError(
            "reviewer brief is missing standing practice(s): " + "; ".join(absent)
            + " - each of per-item repair verdict, mutating the author's TESTS, and isolation "
              "re-testing of a survivor is a standing instruction; a brief that omits one is "
              "refused, not issued")


def missing_claim_surfaces(brief_text: str) -> list[str]:
    """The prose surfaces the claim-inventory pass fails to name, so removing one is detectable.
    All four (Resolutions, docstrings, comments, CHANGELOG) must be named or the omitted one is
    exempted from the pass."""
    body = _normalise_brief(brief_text)
    return [s for s in CLAIM_SURFACES if not re.search(re.escape(s), body, re.I)]


def assert_brief_claim_pass(brief_text: str) -> None:
    """Refuse a brief whose claim-inventory pass omits any of the four prose surfaces or the
    TRUE/FALSE/UNVERIFIABLE vocabulary. A pass that omits a surface silently exempts it."""
    absent = missing_claim_surfaces(brief_text)
    if absent:
        raise ValueError(f"claim-inventory pass omits prose surface(s): {', '.join(absent)} - "
                         f"all four ({', '.join(CLAIM_SURFACES)}) must be enumerated or the "
                         f"omitted one is exempt; refused")
    body = _normalise_brief(brief_text)
    for word in ("TRUE", "FALSE", "UNVERIFIABLE"):
        if not re.search(rf"\b{word}\b", body):
            raise ValueError(f"claim-inventory pass never names the {word} ruling - each claim "
                             f"is marked TRUE, FALSE or UNVERIFIABLE; refused")


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

{_CLAIM_INVENTORY_BLOCK}

{_REVIEW_PRACTICES_BLOCK}

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


# --- Per-item repair verdict -----------------------------------------------------------
# A repair review rules each previous finding individually, so an aggregate 'the repair is
# fine' can never cover findings the reviewer was shown as a set but never item by item.
REPAIR_RULINGS = ("CLOSED", "OVER-CLAIMED", "MOVED")


def enumerate_repair_findings(prior_findings: list[str]) -> str:
    """Render the previous round's findings as a per-item checklist for a repair review, each
    demanding its own CLOSED / OVER-CLAIMED / MOVED ruling. Refuses an empty list - a repair
    review with nothing to rule on is not a repair review, and an aggregate answer about a set
    never shown item by item is exactly what enumerating them forbids."""
    items = [str(f).strip() for f in (prior_findings or []) if str(f).strip()]
    if not items:
        raise ValueError("a repair review needs the previous round's findings to enumerate - "
                         "with none listed the reviewer answers in aggregate; refused")
    lines = ["--- PER-ITEM REPAIR VERDICT (rule EACH previous finding below) ---", "",
             "Rule each of the previous round's findings individually as CLOSED, OVER-CLAIMED "
             "or MOVED. A general 'the repair is fine' answer is not accepted - every finding "
             "carries its own ruling, and MOVED means the defect survived, not that it closed.",
             ""]
    for i, finding in enumerate(items, 1):
        lines.append(f"{i}. {finding}")
        lines.append("   ruling: ( CLOSED | OVER-CLAIMED | MOVED )")
    return "\n".join(lines)


def validate_repair_verdict(prior_findings: list[str], rulings: dict) -> bool:
    """Refuse a repair-round verdict unless EVERY previous finding carries a ruling in
    {CLOSED, OVER-CLAIMED, MOVED}. Raises ValueError naming the first unruled finding, or a
    ruling outside the vocabulary. An unruled finding is never resolved in the repair's favour -
    that is the aggregate answer this exists to refuse."""
    seen = {str(k): str(v).strip().upper() for k, v in (rulings or {}).items()}
    for finding in prior_findings:
        key = str(finding)
        ruling = seen.get(key, "")
        if not ruling:
            raise ValueError(f"finding not ruled: {key!r} - each previous finding carries its "
                             f"own CLOSED/OVER-CLAIMED/MOVED ruling; an unruled finding is "
                             f"refused, never taken as closed")
        if ruling not in REPAIR_RULINGS:
            raise ValueError(f"finding {key!r} has ruling {ruling!r} outside {REPAIR_RULINGS}")
    return True


def repair_open_findings(rulings: dict) -> list[str]:
    """The findings still OPEN after a repair round: everything not CLOSED. A MOVED defect
    survived - it moved, it did not close - and an OVER-CLAIMED repair claimed more than it did;
    counting either as closed is how a repair masks the defect beside it."""
    return [str(f) for f, r in (rulings or {}).items() if str(r).strip().upper() != "CLOSED"]


# --- Claim inventory (prose assertions ruled TRUE / FALSE / UNVERIFIABLE) ---------------
# The first pass of a review: enumerate every assertion the diff's prose makes and rule each,
# before the logic review. A claim silently ruled TRUE because nothing contradicted it is the
# failure this surfaces, so UNVERIFIABLE is its own category and an absent ruling is refused.
CLAIM_RULINGS = ("TRUE", "FALSE", "UNVERIFIABLE")


def validate_claim_inventory(claims: list[str], rulings: dict) -> bool:
    """Refuse a claim inventory unless every enumerated claim carries a ruling in
    {TRUE, FALSE, UNVERIFIABLE}. Raises ValueError naming the first unruled claim, or a ruling
    outside the vocabulary. An absent ruling is refused, never defaulted to TRUE."""
    seen = {str(k): str(v).strip().upper() for k, v in (rulings or {}).items()}
    for claim in claims:
        key = str(claim)
        ruling = seen.get(key, "")
        if not ruling:
            raise ValueError(f"claim not ruled: {key!r} - every enumerated assertion carries a "
                             f"TRUE/FALSE/UNVERIFIABLE ruling; an unruled claim is refused, "
                             f"never assumed true")
        if ruling not in CLAIM_RULINGS:
            raise ValueError(f"claim {key!r} has ruling {ruling!r} outside {CLAIM_RULINGS}")
    return True


def summarise_claim_pass(rulings) -> dict:
    """The claim pass summarised. Counts per category, how many claims rest on TRUST
    (UNVERIFIABLE), how many were actually CHECKED against the code (TRUE or FALSE), and whether
    the pass is VERIFIED. A pass is verified only when at least one claim was settled; a pass
    whose every ruling is UNVERIFIABLE checked nothing, and must not read the same as one that
    looked and found nothing wrong. Accepts a rulings dict or a bare iterable of rulings."""
    values = rulings.values() if isinstance(rulings, dict) else (rulings or [])
    counts = {r: 0 for r in CLAIM_RULINGS}
    for v in values:
        u = str(v).strip().upper()
        if u in counts:
            counts[u] += 1
    checked = counts["TRUE"] + counts["FALSE"]
    on_trust = counts["UNVERIFIABLE"]
    return {"true": counts["TRUE"], "false": counts["FALSE"],
            "unverifiable": on_trust, "on_trust": on_trust,
            "checked": checked, "total": checked + on_trust,
            "verified": checked > 0}


def render_claim_pass(rulings) -> str:
    """One line describing the claim pass, in which a checked round and an all-on-trust round
    read differently. An all-UNVERIFIABLE pass renders NOT VERIFIED - nothing was settled - so
    it cannot be mistaken for a clean pass that looked and found nothing."""
    s = summarise_claim_pass(rulings)
    if s["total"] == 0:
        return "claim pass: no assertions enumerated"
    if not s["verified"]:
        return (f"claim pass: NOT VERIFIED - all {s['total']} claim(s) UNVERIFIABLE, nothing "
                f"settled against the code; this round checked nothing")
    trust = f", {s['on_trust']} on trust (UNVERIFIABLE)" if s["on_trust"] else ""
    return (f"claim pass: {s['checked']} of {s['total']} checked "
            f"(TRUE {s['true']}, FALSE {s['false']}){trust}")


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
    import file_finding  # noqa: PLC0415 - the shared prose-fields loader, as elsewhere
    try:
        fields = file_finding.resolve_prose_fields(
            getattr(args, "fields_file", None), {"note": args.note}, allowed=("note",))
    except ValueError as exc:
        print(f"signoff refused: {exc}", file=sys.stderr)
        return 2
    try:
        path = record_signoff(args.root, args.unit, args.principal, args.author,
                              delegate=args.delegate, boundary=args.boundary,
                              note=fields.get("note", ""))
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
            print(f"{v['unit']} {v['verdict']} ({v['date']}){_superseded_suffix(v)}")
    return 0


def _superseded_suffix(verdict: dict) -> str:
    """How a retired row reads in the listing: still shown, with why and on whose authority,
    so a reader sees both that it was recorded and that it no longer counts."""
    if not verdict.get("superseded"):
        return ""
    return (f"  SUPERSEDED {verdict.get('superseded_at', '')}: "
            f"{verdict.get('superseded_reason', '')} "
            f"(authorised by {verdict.get('superseded_by', '')})")


def cmd_supersede(args: argparse.Namespace) -> int:
    try:
        path = record_supersession(args.root, args.unit, args.date, args.reason,
                                   args.authorised_by, reviewer=args.reviewer,
                                   verdict=args.verdict, phase=args.phase)
    except (OSError, ValueError) as exc:
        print(f"supersede refused: {exc}", file=sys.stderr)
        return 2
    print(f"superseded the {args.phase} verdict row for {sdlc_md.norm_id(args.unit)} "
          f"dated {args.date} -> {path}")
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
    so.add_argument("--fields-file", dest="fields_file", metavar="FIELDS.json",
                    help="read the sign-off note from a JSON object ({\"note\": \"...\"}) instead "
                         "of --note, so prose carrying shell metacharacters is stored verbatim "
                         "rather than interpreted by the shell")
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
    sp = sub.add_parser("supersede", aliases=["correct"],
                        help="Retire a verdict row that records an event which did not "
                             "happen, by appending a supersession record naming the row, "
                             "the reason and the authoriser. The row itself stays.")
    sp.add_argument("--unit", required=True)
    sp.add_argument("--date", required=True, help="the retired row's Date cell")
    sp.add_argument("--reason", required=True, help="why the row records something untrue")
    sp.add_argument("--authorised-by", dest="authorised_by", required=True,
                    help="who authorised the correction - never the row's own author")
    sp.add_argument("--reviewer", default=None,
                    help="narrow the match when the unit has several rows that date")
    sp.add_argument("--verdict", default=None, help="narrow the match by the row's verdict")
    sp.add_argument("--phase", choices=PHASES, default="delivery")
    sp.add_argument("--root", default=".")
    sp.set_defaults(func=cmd_supersede)
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
