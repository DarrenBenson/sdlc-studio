#!/usr/bin/env python3
"""flow - deterministic flow metrics: cycle time, throughput, work-item age.

The zero-token schedule instrument (the cost instrument is points x a measured
tokens-per-point rate - a different axis, see reference-sprint.md). Everything
here is computed from data the workspace already keeps: `Created:` dates in
artefact headers, status transitions in git history (fallback: the revision
history table), and the status vocabulary in `lib.sdlc_md`.

Honesty contract (LL0008): a unit whose dates cannot be resolved is NAMED in
the report as unmeasurable with the reason - never guessed, never silently
skipped. Throughput and cycle time count only DELIVERED terminal statuses
(Done / Fixed / Closed); a Superseded or Rejected unit was not delivered and
pollutes both metrics. Advisory only: nothing here feeds a gate.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from lib import sdlc_md
except ImportError:  # pragma: no cover - flat install layout
    import sdlc_md  # type: ignore

# Delivered = the unit shipped. Other terminal states (Superseded, Rejected,
# Won't Fix/Implement, Duplicate) close the unit without delivering it.
DELIVERED_STATUS = {
    "story": {"Done"},
    "bug": {"Fixed", "Closed"},
}

_REV_ROW = re.compile(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|", re.M)


def cycle_days(created: dt.date, done: dt.date) -> int:
    """Whole days from creation to delivery (same-day delivery = 0)."""
    return (done - created).days


def _revision_dates(text: str) -> list[dt.date]:
    """Dates of the Revision History table rows, in row order.

    Scoped to the section (a date elsewhere in prose - a deadline, a quote -
    must not win; a max() over the whole file is defeated by any future date).
    """
    m = re.search(r"^## Revision History\b.*", text, re.M)
    if not m:
        return []
    section = text[m.start():]
    nxt = re.search(r"^## ", section[len(m.group(0)):], re.M)
    if nxt:
        section = section[: len(m.group(0)) + nxt.start()]
    out = []
    for raw in _REV_ROW.findall(section):
        try:
            out.append(dt.date.fromisoformat(raw))
        except ValueError:
            continue
    return out


def terminal_date(root: Path, path: Path, type_: str, status: str,
                  allow_revision_fallback: bool = True):
    """When `path` reached `status`: `(datetime, source)` or `(None, None)`.

    git history is the precise source (the newest commit that changed the
    occurrence count of the status line). Fallback: the LAST revision-history
    row's date (day precision) - sound for a TERMINAL status (the last row IS
    the close), wrong for a transient one like Blocked (a post-block edit
    masquerades as the transition), so those callers pass
    allow_revision_fallback=False and get an honest (None, None) instead.
    """
    rel = path.resolve().relative_to(Path(root).resolve())
    # -G on the anchored HEADER line, not -S on the bare literal: a pickaxe over the
    # occurrence count is poisoned by a later body-prose mention of the same string
    # (the newest such edit would masquerade as the transition, source "git").
    pattern = r"^> \*\*Status:\*\* " + re.escape(status) + r"$"
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "-G", pattern, "--", str(rel)],
            cwd=root, capture_output=True, text=True, timeout=30)
        stamp = out.stdout.strip().splitlines()[0] if out.stdout.strip() else ""
        if out.returncode == 0 and stamp:
            return dt.datetime.fromisoformat(stamp), "git"
    except (OSError, subprocess.TimeoutExpired, ValueError):
        pass
    if allow_revision_fallback:
        text = sdlc_md.read_text_safe(path)
        rows = _revision_dates(text)
        if rows:
            return dt.datetime.combine(rows[-1], dt.time(12, 0)), "revision"
    return None, None


def commit_author_times(root: Path) -> list[dt.datetime] | None:
    """Every commit's author time, newest first - or None when git is unreadable.
    One call; callers bucket in Python (git's --since/--until filter on COMMITTER
    date, a trap for histories with backdated author times). Times are compared as
    naive wall-clock (offsets stripped) against naive ledger stamps - a bounded
    <=1-day skew on a days-scale metric across mixed-offset histories.

    Refuses (None) when `root` is not itself a git work-tree root: git walks UP from
    cwd, so a non-repo workspace would silently read the ENCLOSING repo's history -
    wrong-repo lead times presented as real."""
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=root,
                             capture_output=True, text=True, timeout=30)
        if top.returncode != 0 or not top.stdout.strip():
            return None
        if Path(top.stdout.strip()).resolve() != Path(root).resolve():
            return None
        out = subprocess.run(["git", "log", "--format=%aI"], cwd=root,
                             capture_output=True, text=True, timeout=30)
        if out.returncode != 0:
            return None
        return [dt.datetime.fromisoformat(s).replace(tzinfo=None)
                for s in out.stdout.split()]
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return None


def lead_times(root: Path, event_times: list[dt.datetime]) -> list[float] | None:
    """Lead-time-for-changes samples in days: for each event (sorted), every commit
    authored since the previous event and at-or-before it contributes
    `event - commit`. None = no readable git history (the caller names it)."""
    commits = commit_author_times(Path(root))
    if commits is None:
        return None
    leads: list[float] = []
    prev = None
    for when in sorted(event_times):
        for c in commits:
            if c <= when and (prev is None or c > prev):
                leads.append((when - c).total_seconds() / 86400)
        prev = when
    return leads


def weekly_throughput(dates) -> dict[str, int]:
    """Delivered-date counts keyed by ISO week (`2026-W28`)."""
    weekly: dict[str, int] = {}
    for d in dates:
        y, w, _ = d.isocalendar()
        weekly[f"{y}-W{w:02d}"] = weekly.get(f"{y}-W{w:02d}", 0) + 1
    return dict(sorted(weekly.items()))


def compute(root, types=("story", "bug"), today: dt.date | None = None) -> dict:
    """The flow report: per-unit metrics, named unmeasurables, weekly throughput."""
    root = Path(root)
    today = today or dt.date.today()
    units: dict[str, dict] = {}
    unmeasurable: dict[str, str] = {}
    delivered_dates: list[dt.date] = []

    for type_ in types:
        for path, text in sdlc_md.iter_artifact_files(type_, root):
            rec = sdlc_md.extract_record_id(path.stem)
            if not rec:
                continue
            rec = sdlc_md.norm_id(rec)
            if text is None:
                text = sdlc_md.read_text_safe(path)
                if not text:
                    unmeasurable[rec] = "unreadable file"
                    units[rec] = {"type": type_, "status": ""}
                    continue
            status = sdlc_md.extract_field(text, "Status") or ""
            created_raw = sdlc_md.extract_field(text, "Created") or sdlc_md.extract_field(text, "Date")
            created = None
            if created_raw:
                try:
                    created = dt.date.fromisoformat(created_raw.strip()[:10])
                except ValueError:
                    created = None
            unit: dict = {"type": type_, "status": status}
            if status in DELIVERED_STATUS.get(type_, set()):
                when, source = terminal_date(root, path, type_, status)
                if when is None or created is None:
                    why = "no Created date" if created is None else "no resolvable delivery date (no git history, no revision row)"
                    unmeasurable[rec] = why
                    units[rec] = unit
                    continue
                unit["cycle_days"] = cycle_days(created, when.date())
                unit["cycle_source"] = source
                unit["delivered"] = when.date().isoformat()
                delivered_dates.append(when.date())
            elif sdlc_md.is_terminal_status(type_, status):
                unit["closed_undelivered"] = True  # Superseded etc: no flow metric
            else:
                if created is None:
                    unmeasurable[rec] = "no Created date"
                    units[rec] = unit
                    continue
                unit["age_days"] = (today - created).days
                if status == "Blocked":
                    # blocked-age, distinct from total age: how long has it been STUCK
                    when, source = terminal_date(root, path, type_, "Blocked",
                                                 allow_revision_fallback=False)
                    if when is not None:
                        unit["blocked_days"] = (today - when.date()).days
                        unit["blocked_source"] = source
                    else:
                        unit["blocked_age"] = ("unmeasurable (no resolvable Blocked "
                                               "transition in git or revision history)")
            units[rec] = unit

    window = {}
    if delivered_dates:
        def _monday(d: dt.date) -> dt.date:
            return d - dt.timedelta(days=d.isocalendar()[2] - 1)
        weeks = (_monday(max(delivered_dates)) - _monday(min(delivered_dates))).days // 7 + 1
        window = {"from": min(delivered_dates).isoformat(),
                  "to": max(delivered_dates).isoformat(),
                  "weeks": weeks}
    return {
        "units": units,
        "unmeasurable": unmeasurable,
        "throughput": {"weekly": weekly_throughput(delivered_dates), "window": window},
    }


def ageing_report(root, *, today: dt.date | None = None) -> dict | None:
    """The ageing flags status surfaces: None when `flow.ageing_days` is unset (the
    feature is opt-in - a gate appearing on a live workflow uninvited breaks it).
    Cheap by design: ages need no git (today - Created); blocked-age is read only for
    Blocked units (few). Returns {"days", "flagged": [(id, status, age)],
    "blocked": [(id, blocked_days_or_None, age)]}."""
    days = sdlc_md.project_override(root, "flow.ageing_days", None)
    if not days:
        return None
    days = int(days)
    root = Path(root)
    today = today or dt.date.today()
    flagged: list[tuple[str, str, int]] = []
    blocked: list[tuple[str, int | None, int]] = []
    for type_ in ("story", "bug"):
        for path, text in sdlc_md.iter_artifact_files(type_, root):
            if text is None:
                continue
            status = sdlc_md.extract_field(text, "Status") or ""
            if sdlc_md.is_terminal_status(type_, status):
                continue
            rec = sdlc_md.extract_record_id(path.stem)
            created_raw = sdlc_md.extract_field(text, "Created") or sdlc_md.extract_field(text, "Date")
            if not (rec and created_raw):
                continue
            try:
                age = (today - dt.date.fromisoformat(created_raw.strip()[:10])).days
            except ValueError:
                continue
            rec = sdlc_md.norm_id(rec)
            if status == "Blocked":
                when, _src = terminal_date(root, path, type_, "Blocked",
                                           allow_revision_fallback=False)
                blocked.append((rec, (today - when.date()).days if when else None, age))
            elif status == "In Progress" and age > days:
                flagged.append((rec, status, age))
    return {"days": days, "flagged": flagged, "blocked": blocked}


def _render(report: dict) -> str:
    units = report["units"]
    lines = []
    cycles = sorted((u["cycle_days"], rid) for rid, u in units.items() if "cycle_days" in u)
    if cycles:
        vals = [c for c, _ in cycles]
        n = len(vals)
        mid = vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2
        lines.append(f"cycle time: {n} delivered unit(s), median {mid:g}d, "
                     f"range {vals[0]}-{vals[-1]}d")
    weekly = report["throughput"]["weekly"]
    if weekly:
        w = report["throughput"]["window"]
        rate = sum(weekly.values()) / max(1, w.get("weeks", 1))
        lines.append(f"throughput: {sum(weekly.values())} delivered over {w['from']}..{w['to']} "
                     f"(~{rate:.1f}/week)")
        for wk, n in weekly.items():
            lines.append(f"  {wk}: {n}")
    ages = sorted(((u["age_days"], rid, u["status"]) for rid, u in units.items()
                   if "age_days" in u), reverse=True)
    if ages:
        lines.append(f"work-item age: {len(ages)} non-terminal unit(s), oldest first:")
        for age, rid, status in ages[:15]:
            b = units[rid].get("blocked_days")
            lines.append(f"  {rid} ({status}): {age}d"
                         + (f" (blocked {b}d)" if b is not None else ""))
        if len(ages) > 15:
            lines.append(f"  (+{len(ages) - 15} more)")
    if report["unmeasurable"]:
        lines.append(f"unmeasurable ({len(report['unmeasurable'])}) - named, not guessed:")
        for rid, why in sorted(report["unmeasurable"].items()):
            lines.append(f"  {rid}: {why}")
    if not lines:
        lines.append("no units found to measure")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="flow", description="Deterministic flow metrics: cycle time, throughput, "
        "work-item age - the zero-token schedule instrument. Advisory; never a gate.")
    sdlc_md.add_global_root(ap)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compute", help="Compute the flow report for stories + bugs.")
    c.add_argument("--type", default="story,bug",
                   help="comma-separated unit types (default: story,bug)")
    sdlc_md.add_format_arg(c)
    args = ap.parse_args(argv)
    types = tuple(t.strip() for t in args.type.split(",") if t.strip())
    report = compute(Path(args.root), types=types)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(_render(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
