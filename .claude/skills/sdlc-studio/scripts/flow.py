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
import random
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


MC_MIN_WEEKS = 4
MC_SIMS = 10_000
MC_WEEK_CAP = 520  # simulation horizon; a percentile AT the cap is refused, never reported
# Day is the calendar floor and the DEFAULT bucket: on an agent-speed project the median
# cycle time is 0 days and sprints are sessions measured in hours, so a week bucket
# quantises the schedule answer to uselessness. The ISO-week bucket stays available via
# --bucket week or `flow.forecast_bucket: week` for slow-moving projects.
MC_MIN_DAYS = 7
MC_DAY_CAP = MC_WEEK_CAP * 7
MC_MIN_SPRINTS = 3
MC_SPRINT_CAP = 200
_BUCKETS = {"day": (MC_MIN_DAYS, MC_DAY_CAP, 1),          # (min history, horizon, days/step)
            "week": (MC_MIN_WEEKS, MC_WEEK_CAP, 7)}


def _median(vals: list) -> float:
    n = len(vals)
    return vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2


def _mc_ranks(samples: list[int], n_units: int, *, seed: int, sims: int,
              cap: int, period: str = "period") -> tuple | dict:
    """The shared Monte Carlo engine: sample measured per-period throughput with
    replacement until the batch is covered, `sims` times. Returns the rank function,
    or the refusal dict when a guard fires (all-zero, non-positive, horizon). The
    guards hold in EVERY bucket - a bucket without them is silent optimism."""
    if n_units <= 0:
        return {"refused": f"a batch of {n_units} unit(s) is not forecastable"}
    if not any(samples):
        return {"refused": "throughput history is all zero - nothing has been delivered "
                           "in the window, so no completion date is honest"}
    rng = random.Random(seed)
    needed: list[int] = []
    for _ in range(sims):
        done = 0
        periods = 0
        while done < n_units and periods < cap:
            done += rng.choice(samples)
            periods += 1
        needed.append(periods)
    needed.sort()

    def rank(p: float) -> int:
        return needed[min(len(needed) - 1, int(len(needed) * p))]
    if rank(0.95) >= cap:
        return {"refused": f"at the measured throughput the batch does not complete "
                           f"within the simulation horizon ({cap} {period}s) at 95% "
                           f"confidence - a capped date would be a truncation, not a forecast"}
    return (rank,)


def mc_bucket_forecast(samples: list[int], n_units: int, *, bucket: str = "week",
                       seed: int = 0, sims: int = MC_SIMS,
                       min_history: int | None = None,
                       today: dt.date | None = None) -> dict:
    """Probabilistic completion forecast over a calendar bucket (day or week):
    50/85/95% completion dates at the bucket's precision. Seeded and reproducible
    by construction. Refuses - never guesses - under the bucket's minimum history,
    on an all-zero history, on a non-positive batch, and at the horizon."""
    today = today or dt.date.today()
    min_hist, cap, step_days = _BUCKETS[bucket]
    if min_history is not None:
        min_hist = min_history
    if len(samples) < min_hist and n_units > 0:
        return {"refused": f"only {len(samples)} {bucket}(s) of throughput history - "
                           f"minimum {min_hist}; a forecast from less is a guess"}
    got = _mc_ranks(samples, n_units, seed=seed, sims=sims, cap=cap, period=bucket)
    if isinstance(got, dict):
        return got
    rank = got[0]
    return {"bucket": bucket, "units": n_units, "sims": sims, "seed": seed,
            f"history_{bucket}s": len(samples),
            "confidence": {p: (today + dt.timedelta(days=rank(float(p) / 100) * step_days))
                           .isoformat() for p in ("50", "85", "95")}}


def monte_carlo_forecast(weekly_samples: list[int], n_units: int, *,
                         seed: int = 0, sims: int = MC_SIMS,
                         min_weeks: int = MC_MIN_WEEKS,
                         today: dt.date | None = None) -> dict:
    """The ISO-week forecast (the original instrument, kept as the `week` bucket):
    see mc_bucket_forecast for the engine and its guards."""
    out = mc_bucket_forecast(weekly_samples, n_units, bucket="week", seed=seed,
                             sims=sims, min_history=min_weeks, today=today)
    if "refused" in out:
        return out
    out.pop("bucket")  # the original shape, unchanged for existing readers
    return out


def day_samples(dates: list[dt.date]) -> list[int]:
    """Per-day delivered counts across the delivered window, ZERO days included -
    dropping them is silent optimism."""
    if not dates:
        return []
    counts: dict[dt.date, int] = {}
    for d in dates:
        counts[d] = counts.get(d, 0) + 1
    day = min(dates)
    out: list[int] = []
    while day <= max(dates):
        out.append(counts.get(day, 0))
        day += dt.timedelta(days=1)
    return out


def sprint_forecast(root, n_units: int, *, seed: int = 0, sims: int = MC_SIMS) -> dict:
    """The sprint-session denominator - the primary read on an agent-speed project:
    sample measured per-sprint delivered units from the velocity history and report
    sprints-to-complete, plus hours at the measured elapsed-hours-per-sprint median.
    Refuses under MC_MIN_SPRINTS of history (named); unmeasured elapsed hours are
    named unmeasured, never zeroed."""
    import retro  # noqa: PLC0415 - sibling; deferred so `compute` never pays for it
    rows = retro.velocity_history(root)
    samples = [r["measured"] if r.get("measured") is not None else r.get("units")
               for r in rows]
    samples = [int(s) for s in samples if s is not None]
    if len(samples) < MC_MIN_SPRINTS:
        return {"refused": f"only {len(samples)} sprint(s) of velocity history - "
                           f"minimum {MC_MIN_SPRINTS}; a forecast from less is a guess"}
    got = _mc_ranks(samples, n_units, seed=seed, sims=sims, cap=MC_SPRINT_CAP,
                    period="sprint")
    if isinstance(got, dict):
        return got
    rank = got[0]
    sprints = {p: rank(float(p) / 100) for p in ("50", "85", "95")}
    walls = sorted(float(r["wall_time_s"]) for r in rows
                   if r.get("wall_time_s") is not None)
    out = {"bucket": "sprint", "units": n_units, "sims": sims, "seed": seed,
           "history_sprints": len(samples), "confidence_sprints": sprints}
    if walls:
        median_h = _median(walls) / 3600
        out["median_sprint_hours"] = median_h
        out["confidence_hours"] = {p: k * median_h for p, k in sprints.items()}
    else:
        out["median_sprint_hours"] = None
        out["confidence_hours"] = None
        out["note"] = ("elapsed hours unmeasured - no sprint in the history recorded a "
                       "wall time, so sprints-to-complete is the whole honest answer")
    return out


def resolve_bucket(flag: str | None, root) -> str:
    """The forecast bucket: an explicit flag wins, then `flow.forecast_bucket` in
    .config.yaml, then the day default. An unknown config value is refused loudly -
    silently falling through to another bucket would be a guess dressed as config."""
    if flag:
        return flag
    got = str(sdlc_md.project_override(root, "flow.forecast_bucket", "day") or "day")
    if got not in ("day", "week", "sprint"):
        raise ValueError(f"flow.forecast_bucket is {got!r} - expected day, week or sprint")
    return got


def forecast(root, n_units: int, *, seed: int = 0,
             today: dt.date | None = None, bucket: str = "week") -> dict:
    """Workspace glue: measured throughput in the requested bucket (every period in
    the delivered window, zeros included) -> the seeded Monte Carlo engine."""
    if bucket == "sprint":
        return sprint_forecast(root, n_units, seed=seed)
    report = compute(root, today=today)
    window = report["throughput"]["window"]
    if not window:
        return {"refused": "no delivered units at all - there is no throughput to sample"}
    if bucket == "day":
        dates = sorted(dt.date.fromisoformat(u["delivered"])
                       for u in report["units"].values() if "delivered" in u)
        return mc_bucket_forecast(day_samples(dates), n_units, bucket="day",
                                  seed=seed, today=today)
    weekly = report["throughput"]["weekly"]
    start = dt.date.fromisoformat(window["from"])
    end = dt.date.fromisoformat(window["to"])
    samples: list[int] = []
    monday = start - dt.timedelta(days=start.isocalendar()[2] - 1)
    while monday <= end:
        y, w, _ = monday.isocalendar()
        samples.append(weekly.get(f"{y}-W{w:02d}", 0))
        monday += dt.timedelta(days=7)
    return monte_carlo_forecast(samples, n_units, seed=seed, today=today)


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
        lines.append(f"cycle time: {len(vals)} delivered unit(s), median {_median(vals):g}d, "
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
    f = sub.add_parser("forecast", help="Seeded Monte Carlo completion forecast for N "
                                        "units from measured throughput. Buckets: day "
                                        "(default - the agent-speed calendar floor), "
                                        "week (ISO weeks), sprint (sessions from the "
                                        "velocity history, with measured hours).")
    f.add_argument("--units", type=int, required=True,
                   help="how many delivery units the batch holds")
    f.add_argument("--seed", type=int, default=0,
                   help="simulation seed (default 0 - reproducible by design)")
    f.add_argument("--bucket", choices=("day", "week", "sprint"), default=None,
                   help="throughput denominator (default: flow.forecast_bucket config, "
                        "else day)")
    sdlc_md.add_format_arg(f)
    args = ap.parse_args(argv)
    if args.cmd == "forecast":
        bucket = resolve_bucket(args.bucket, Path(args.root))
        result = forecast(Path(args.root), args.units, seed=args.seed, bucket=bucket)
        if args.format == "json":
            print(json.dumps(result, indent=2))
        elif "refused" in result:
            print(f"forecast refused: {result['refused']}")
        elif bucket == "sprint":
            s = result["confidence_sprints"]
            line = (f"forecast for {result['units']} unit(s) over "
                    f"{result['history_sprints']} measured sprint(s) "
                    f"({result['sims']} sims, seed {result['seed']}):\n"
                    f"  50% within {s['50']}   85% within {s['85']}   "
                    f"95% within {s['95']} sprint-session(s)")
            if result["median_sprint_hours"] is not None:
                h = result["confidence_hours"]
                line += (f"\n  ~{h['50']:.1f}h / {h['85']:.1f}h / {h['95']:.1f}h at the "
                         f"measured {result['median_sprint_hours']:.1f}h-per-sprint median")
            else:
                line += f"\n  {result['note']}"
            print(line)
        else:
            c50, c85, c95 = (result["confidence"][k] for k in ("50", "85", "95"))
            history = result.get("history_days", result.get("history_weeks"))
            print(f"forecast for {result['units']} unit(s) over {history} "
                  f"measured {bucket}(s) ({result['sims']} sims, seed {result['seed']}):\n"
                  f"  50% by {c50}   85% by {c85}   95% by {c95}\n"
                  f"  probabilistic schedule read - the cost instrument (points x rate) "
                  f"is a different axis; neither feeds a gate")
        return 0
    types = tuple(t.strip() for t in args.type.split(",") if t.strip())
    report = compute(Path(args.root), types=types)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(_render(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
