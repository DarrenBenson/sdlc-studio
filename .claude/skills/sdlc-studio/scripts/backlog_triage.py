#!/usr/bin/env python3
"""Backlog triage: is this backlog worth planning FROM?

Breakdown asks whether a single unit can be planned (Affects + a size). Triage asks the
backlog-level question that had no home: are these items DISTINCT, correctly sized, current, and
still wanted? One day of dogfooding produced three duplicate pairs in a backlog of eleven, all
caught by a human looking rather than by tooling - a duplicate inflates the backlog, double-counts
every status report, and splits one change's acceptance criteria across two artefacts so neither
is complete alone.

The lenses, deterministic and each stating what it compares:

  DUPLICATE/SUBSUMED  (report) - two open artefacts whose Affects overlap AND whose title+summary
                      are similar: likely one unit filed twice. Names the candidate; never
                      auto-refuses, because a genuine near-miss is common and only the author can
                      tell them apart. SUBSUMED is the strong form: one's Affects is a subset of
                      the other's, so the smaller is likely absorbed by the larger.
  OVERSIZED           (BLOCK) - a delivery unit sized above the point at which estimation is
                      reliable. Estimator consistency collapses above ~5x a reference unit, so an
                      oversized unit is not an estimation failure, it is a TRIAGE failure whose
                      answer is to split it. Blocks at points > 8 (the refuse ceiling); reports at
                      exactly 8 (at the ceiling - consider decomposing).
  STALE               (report) - open, untouched for months, nothing depends on it: ask whether it
                      is still wanted before planning around it.
  ORPHANED DEPENDENCY (report) - `Depends on:` names an artefact that is terminal or absent, so the
                      dependency is already resolved or was mis-recorded.

Judgement lenses REPORT (the human decides); the mechanical OVERSIZED lens BLOCKS. Every lens logs
what it examined and dropped, so a silent truncation never reads as a clean backlog. Pure stdlib;
skill/consuming-project neutral - it reads only the artefacts.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

# The plannable backlog: delivery units and the discovery requests that feed them. Terminal
# artefacts are excluded - triage is about what a plan would be built FROM.
TRIAGE_TYPES = ("epic", "story", "bug", "cr", "rfc", "issue")

# Above this many points a delivery unit cannot be sized reliably; the refuse ceiling.
OVERSIZE_BLOCK = 8

_STOP = frozenset(
    "the a an and or of to for in on at is are be it this that with into from as by "
    "no not but so if then when what which who whose their its our your they we you".split())
_ID_RE = re.compile(r"\b((?:US|BG|EP|CR|RFC|IS|PL|TS|WF)-?\d{3,})\b", re.I)


def _summary(text: str) -> str:
    """The artefact's own description: the `## Summary` section if present, else the first
    non-frontmatter paragraph. Used (with the title) for similarity - the words the author chose
    to describe the change."""
    m = re.search(r"(?ms)^##\s+Summary\s*\n(.+?)(?=^\#|\Z)", text)
    if m:
        return m.group(1)
    body = re.sub(r"(?ms)^#.*?\n", "", text, count=1)  # drop the H1
    body = re.sub(r"(?m)^>.*$", "", body)               # drop frontmatter quote-lines
    for para in body.split("\n\n"):
        if para.strip():
            return para
    return ""


_ID_TOKEN_RE = re.compile(r"^(?:us|bg|ep|cr|rfc|is|pl|ts|wf)\d{3,}$")


def _tokens(*parts: str) -> set[str]:
    words = re.findall(r"[a-z0-9_]+", " ".join(parts).lower())
    # Drop an artefact's OWN id token (it leaks in from the `US0001:` H1 prefix): two duplicates
    # carry different ids, and counting them would drive similar wording apart.
    return {w for w in words
            if w not in _STOP and len(w) > 2 and not _ID_TOKEN_RE.match(w)}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _affect_key(root: Path, p: str) -> str:
    """One file, one key - however the path was written (mirrors the planner's clustering key), so
    a path spelled from the repo root and the same file spelled from the skill dir are one file."""
    r = sdlc_md.resolve_affects(root, p)
    if r is not None:
        try:
            return str(Path(r).relative_to(root))
        except ValueError:
            return str(r)
    return re.sub(r"^\./", "", p.strip())


def _depends(text: str) -> set[str]:
    raw = sdlc_md.extract_field(text, "Depends on") or sdlc_md.extract_field(text, "Depends-on")
    if not raw:
        return set()
    return {sdlc_md.norm_id(m.group(1)) for m in _ID_RE.finditer(raw)}


_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def _last_date(text: str, *, today: str | None = None) -> str | None:
    """The most recent date the artefact carries - from its metadata fields (`Date:`/`Created:`/
    `Updated:`) and its `## Revision History` table - as YYYY-MM-DD. Used for staleness; None when
    the artefact records no date to judge by.

    It reads only those regions, and clamps to `today`, so a future deadline or a date mentioned in
    prose (`finish by 2026-12-31`) cannot masquerade as a last-touched date and suppress the lens."""
    dates: list[str] = []
    for field in ("Date", "Created", "Updated"):
        v = sdlc_md.extract_field(text, field)
        if v:
            dates += _DATE_RE.findall(v)
    hist = re.search(r"(?ms)^##\s+Revision History\s*\n(.+?)(?=^\#|\Z)", text)
    if hist:
        dates += _DATE_RE.findall(hist.group(1))
    if today:
        dates = [d for d in dates if d <= today]  # a future date is not a last-touched date
    return max(dates) if dates else None


def _days_between(earlier: str, later: str) -> int | None:
    from datetime import date
    try:
        y1, m1, d1 = (int(x) for x in earlier.split("-"))
        y2, m2, d2 = (int(x) for x in later.split("-"))
        return (date(y2, m2, d2) - date(y1, m1, d1)).days
    except (ValueError, TypeError):
        return None


def _scan(root: Path, *, today: str | None = None) -> tuple[list[dict], dict[str, str], int]:
    """One guarded pass over EVERY artefact. Returns (backlog, states, skipped):

    - `backlog` - the non-terminal triage-type units, with the fields the lenses read.
    - `states` - `{norm_id: "open" | "terminal"}` across ALL artefact types (so the orphaned lens
      can tell a resolved (terminal) dependency from an absent (mistyped/unmet) one, and does not
      false-flag a live dependency on a test-spec, plan or workflow the backlog scan omits).
    - `skipped` - files that could not be read (a half-written or non-UTF-8 artefact). Counted, not
      swallowed, so a drop never reads as a clean backlog.
    """
    backlog: list[dict] = []
    states: dict[str, str] = {}
    skipped = 0
    for type_ in sdlc_md.ARTIFACT_TYPES:
        vocab = sdlc_md.status_vocab(type_, root)
        triage_type = type_ in TRIAGE_TYPES
        for p in sdlc_md.artifact_files(type_, root):
            cid = sdlc_md.extract_record_id(p.stem)
            if not cid:
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                skipped += 1  # a file we could not read is a gap we NAME, never a clean pass
                continue
            status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab)
            terminal = bool(status and sdlc_md.is_terminal_status(type_, status))
            states[sdlc_md.norm_id(cid)] = "terminal" if terminal else "open"
            if terminal or not triage_type:
                continue
            title = sdlc_md.extract_h1_title(text) or ""
            affects = {_affect_key(root, a) for a in sdlc_md.affects_files(text)}
            backlog.append({
                "id": cid, "type": type_, "status": status or "?",
                "affects": {a for a in affects if a},
                "tokens": _tokens(title, _summary(text)),
                "points": sdlc_md.read_points(text), "size": sdlc_md.read_size(text),
                "depends": _depends(text), "date": _last_date(text, today=today),
            })
    return backlog, states, skipped


def load_backlog(root: Path) -> list[dict]:
    """Every non-terminal triage-type artefact, with the fields the lenses read (the backlog half
    of `_scan`)."""
    return _scan(root)[0]


def _duplicate_findings(backlog: list[dict], *, sim: float = 0.5) -> list[dict]:
    """Pairs whose Affects overlap AND whose words are similar: likely one unit filed twice.
    SUBSUMED when one's Affects is a subset of the other's (the smaller is likely absorbed)."""
    out: list[dict] = []
    for i, a in enumerate(backlog):
        for b in backlog[i + 1:]:
            shared = a["affects"] & b["affects"]
            if not shared:
                continue
            j = _jaccard(a["tokens"], b["tokens"])
            if j < sim:
                continue
            # SUBSUMED is the strong form: one's files are a PROPER subset of the other's, so the
            # smaller is likely absorbed. Equal file sets are a plain duplicate, not a subsumption.
            subsumed = (a["affects"] < b["affects"]) or (b["affects"] < a["affects"])
            lens = "subsumed" if subsumed else "duplicate"
            out.append({
                "lens": lens, "severity": "report", "units": sorted([a["id"], b["id"]]),
                "detail": (f"{a['id']} and {b['id']} share {sorted(shared)} and are "
                           f"{int(j * 100)}% similar in wording - likely "
                           f"{'one subsumes the other' if subsumed else 'the same change filed twice'}; "
                           f"merge or supersede one, or confirm they are distinct")})
    return out


def _oversized_findings(backlog: list[dict]) -> list[dict]:
    """A unit sized above the reliable-estimation ceiling: a triage failure, split it. Any unit
    carrying Points is judged (a delivery unit, or a legacy CR that carries points), matching the
    plan's breakdown gate - a pointed container above the ceiling is over-sized wherever it lives."""
    out: list[dict] = []
    for u in backlog:
        if u["points"] is None:
            continue
        if u["points"] > OVERSIZE_BLOCK:
            out.append({"lens": "oversized", "severity": "block", "units": [u["id"]],
                        "detail": (f"{u['id']} is {u['points']} points, above the {OVERSIZE_BLOCK}-point "
                                   f"ceiling nobody can size reliably - decompose it before planning")})
        elif u["points"] == OVERSIZE_BLOCK:
            out.append({"lens": "oversized", "severity": "report", "units": [u["id"]],
                        "detail": (f"{u['id']} is at the {OVERSIZE_BLOCK}-point ceiling - consider "
                                   f"decomposing; estimation reliability falls off here")})
    return out


def _stale_findings(backlog: list[dict], *, today: str, stale_days: int = 90) -> list[dict]:
    """Open, untouched for months, and nothing open depends on it: ask if it is still wanted."""
    depended_on = {d for u in backlog for d in u["depends"]}
    out: list[dict] = []
    for u in backlog:
        if not u["date"] or sdlc_md.norm_id(u["id"]) in depended_on:
            continue
        age = _days_between(u["date"], today)
        if age is not None and age >= stale_days:
            out.append({"lens": "stale", "severity": "report", "units": [u["id"]],
                        "detail": (f"{u['id']} last touched {u['date']} ({age}d ago), nothing depends "
                                   f"on it - confirm it is still wanted before planning around it")})
    return out


def _orphaned_findings(backlog: list[dict], states: dict[str, str]) -> list[dict]:
    """A `Depends on:` that names a TERMINAL artefact (already resolved) or an ABSENT one (mistyped
    or unmet). Distinguished, because the fix differs: a resolved dependency's line can be cleared,
    but an absent one is a broken reference to check. Resolved against ALL artefact types, so a live
    dependency on an open test-spec, plan or workflow (outside the triage-type backlog) is not
    false-flagged."""
    out: list[dict] = []
    for u in backlog:
        for dep in sorted(u["depends"]):
            state = states.get(dep)
            if state == "open":
                continue  # a live, unresolved dependency - correct as recorded
            if state == "terminal":
                detail = (f"{u['id']} depends on {dep}, which is terminal - the dependency is "
                          f"already resolved; clear the `Depends on:` line")
            else:  # absent from every type: a mistyped id or a reference to something never filed
                detail = (f"{u['id']} depends on {dep}, which does not exist in this project - a "
                          f"mistyped id or an unmet reference; fix or remove the `Depends on:` line")
            out.append({"lens": "orphaned-dependency", "severity": "report",
                        "units": [u["id"]], "detail": detail})
    return out


def triage(root: Path, *, today: str | None = None, stale_days: int = 90) -> dict:
    """Run every lens over the backlog. Returns findings (block + report) and a scanned count, so a
    caller (plan, status) can surface them and a drop is never silent."""
    today = today or sdlc_md.now_date()
    backlog, states, skipped = _scan(root, today=today)
    findings = (_duplicate_findings(backlog) + _oversized_findings(backlog)
                + _stale_findings(backlog, today=today, stale_days=stale_days)
                + _orphaned_findings(backlog, states))
    blocking = [f for f in findings if f["severity"] == "block"]
    return {"scanned": len(backlog), "skipped": skipped, "findings": findings,
            "blocking": blocking, "blocked": bool(blocking)}


def render(report: dict) -> str:
    n = len(report["findings"])
    skipped = report.get("skipped", 0)
    unread = f"; {skipped} file(s) unreadable - could not be checked" if skipped else ""
    if not n:
        return f"backlog triage: clean ({report['scanned']} open artefact(s) scanned{unread})"
    lines = [f"backlog triage: {n} finding(s) over {report['scanned']} open artefact(s) "
             f"({len(report['blocking'])} blocking{unread}):"]
    order = {"oversized": 0, "subsumed": 1, "duplicate": 2, "stale": 3, "orphaned-dependency": 4}
    for f in sorted(report["findings"], key=lambda x: (order.get(x["lens"], 9), x["units"])):
        mark = "BLOCK" if f["severity"] == "block" else "note "
        lines.append(f"  [{mark}] {f['lens']}: {f['detail']}")
    return "\n".join(lines)


def cmd_check(args: argparse.Namespace) -> int:
    report = triage(Path(args.root), stale_days=args.stale_days)
    if args.format == "json":
        print(json.dumps(report, indent=2, default=sorted))
    else:
        print(render(report))
    return 1 if report["blocked"] else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Backlog triage: is this backlog worth planning from?")
    p.add_argument("--root", default=".", help="Repo root (default: .)")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Run the triage lenses over the backlog (non-zero if any lens blocks).")
    c.add_argument("--stale-days", type=int, default=90, help="Age (days) at which an untouched item is stale")
    c.add_argument("--format", choices=["text", "json"], default="text")
    c.set_defaults(func=cmd_check)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
