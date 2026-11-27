#!/usr/bin/env python3
"""Trace a bug that escaped to production back to the unit and the review that let it through.

`trace --bug BGxxxx` reads the bug's `Shipped-in` release and the files its fix touches (its
`Affects`), lists the units that release shipped, and proposes those that share a file with the
fix, most shared files first, each with the verdict the review ledger recorded for it and the
seat that gave it. It writes nothing. `--confirm UNIT` records one proposal on the bug, as
`Escaped-via` and `Escaped-verdict`, and refuses a unit that is not among the proposals.

The units a release shipped are the story and bug ids owned by the commits the release's tag
holds and the previous tag does not: the ids a commit's subject names and no `Mentions:` trailer
names (a mentioned id owns none of the commit's files), and the ids its `Refs:` trailers name.
Without a release on the bug, or with one that tags no unit, nothing is proposed: a guess from
the bug's prose would point somewhere nobody can check. Verdicts are read through `critic`'s
public readers, the one authority on the ledger.

`to-class --bug BGxxxx --class NAME --rule ... --behaviour ...` turns a confirmed escape's
written Root Cause into a failure class in the lessons store, through `lessons.class_add`:
injected at build and review, citing the bug and its `Escaped-via` unit as evidence and carrying
the bug's Affects as the files it applies to. A bug not escaped, not confirmed, or whose Root
Cause is unwritten, and a class the store already holds, are refused with nothing written.

`failure-rate [--since D] [--until D] [--settle-days N]` derives change failure rate: the
releases with at least one linked incident divided by the releases counted, from the release
records `release_cut.py changelog-cut` writes. An incident is an issue whose Root Cause section is
written, linked to a release through each escaped bug it was triaged into (the issue's
`Decomposed-into`, or a bug naming it as `Parent`) and that bug's `Shipped-in`. The window is the
`WINDOW_DAYS` days ending on `--until` (today by default), both days included. A release younger
than `SETTLE_DAYS` days (`--settle-days`) at the earlier of the window's end and today is pending,
counted neither way even when an incident already names it. No release record in the window,
every release pending, or no incident recorded reads not measured, never 0%. It writes nothing.

Verbs are subcommands, so a further step of the escape record adds a parser beside these.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import critic  # noqa: E402
import engagement_floor  # noqa: E402
import lessons  # noqa: E402

#: The artefact types a release ships as units, and so the only ones a trace proposes.
UNIT_TYPES = ("story", "bug")
_UNIT_ID_RE = re.compile(r"(?<![A-Za-z0-9])(?:US|BG)-?\d{4,}(?![0-9])", re.I)
#: The record separator between commit messages in the log a release is read from.
_MSG_SEP = "\x1e"
#: The days a change failure rate counts by default, ending on the window's end date.
WINDOW_DAYS = 90
#: The days a release is held as pending before it counts, so an incident can be linked first.
SETTLE_DAYS = 14
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


class TraceRefused(Exception):
    """A trace that cannot be made or recorded; the CLI exits 2 with its message."""


class RateRefused(Exception):
    """A change failure rate that cannot be read; the CLI exits 2 with its message."""


def _git(root: Path, *args: str) -> str | None:
    """A read-only git command's output, run from `root`; None when git or the command fails."""
    try:
        proc = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True,
                              encoding="utf-8", timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout if proc.returncode == 0 else None


def release_tag(root: Path | str, name: str) -> str | None:
    """The git tag a release name means, which is the only thing a trace can read: `name` itself
    when it tags a commit here, else the same name with its leading `v` dropped or added, so
    the spelling a CHANGELOG.md heading uses (`6.4.0`) finds the tag behind it (`v6.4.0`).
    None when neither spelling tags a commit.

    The one resolver: `file_finding.check_escape` stores the `Shipped-in` it returns, and
    `release_units` reads through it, so filing cannot accept a release the trace refuses."""
    name = (name or "").strip()
    if not name:
        return None
    other = name[1:] if name[0] in "vV" else f"v{name}"
    for candidate in (name, other):
        if _git(Path(root), "rev-parse", "-q", "--verify",
                f"refs/tags/{candidate}^{{commit}}") is not None:
            return candidate
    return None


def _owned_ids(message: str) -> list[str]:
    """The unit ids one commit message owns, in the order named: those its subject line names
    that no `Mentions:` trailer names, then those its `Refs:` trailers name (an id both name is
    listed twice, and `release_units` keeps the first). The trailers are read in the grammar
    `engagement_floor` defines for them; an id the body's prose names outside a trailer is not
    owned."""
    def ids(line_re: re.Pattern[str]) -> list[str]:
        return [i for m in line_re.finditer(message) for i in _UNIT_ID_RE.findall(m.group(1))]
    mentioned = {sdlc_md.norm_id(i) for i in ids(engagement_floor._MENTIONS_LINE_RE)}
    subject = message.strip().split("\n", 1)[0]
    return ([i for i in _UNIT_ID_RE.findall(subject) if sdlc_md.norm_id(i) not in mentioned]
            + ids(engagement_floor._REFS_LINE_RE))


def release_units(root: Path, release: str) -> list[str]:
    """The story and bug ids on disk that the commits of `release` own (`_owned_ids`), in
    first-seen order.

    `release` is resolved to its tag by `release_tag`, so either spelling of a tagged version
    is read. The commits are those the tag holds and the tag before it does not (every commit it
    holds when it is the first tag). Raises `TraceRefused` when neither spelling is a tag here."""
    tag = release_tag(root, release)
    if tag is None:
        raise TraceRefused(f"release {release} is not a git tag in this project, in either "
                           f"spelling, so the units it shipped cannot be read - nothing is "
                           f"proposed")
    prev = (_git(root, "describe", "--tags", "--abbrev=0", f"{tag}^") or "").strip()
    span = f"{prev}..{tag}" if prev else tag
    seen: list[str] = []
    log = _git(root, "log", f"--format=%B{_MSG_SEP}", span) or ""
    for found in (i for message in log.split(_MSG_SEP) for i in _owned_ids(message)):
        hit = sdlc_md.find_by_id(root, found)
        if not hit or hit[1] not in UNIT_TYPES:
            continue
        uid = sdlc_md.extract_record_id(hit[0].stem) or found.upper()
        if uid not in seen:
            seen.append(uid)
    return seen


def _verdict(root: Path, unit: str) -> dict | None:
    """The ledger row that let `unit` through - its latest APPROVE, else its latest row - as
    {verdict, reviewer, seat, round}, or None when no review of it is recorded."""
    rows = critic.unit_review_rounds(root, unit)
    approves = [r for r in rows if str(r.get("verdict") or "").upper().startswith("APPROVE")]
    row = (approves or rows or [None])[-1]
    if row is None:
        return None
    reviewer = str(row.get("reviewer") or "").strip()
    return {"verdict": str(row.get("verdict") or "").strip(), "reviewer": reviewer,
            "seat": critic.verdict_seat(root, reviewer), "round": row.get("round")}


def describe_verdict(v: dict | None) -> str:
    """One line for a proposal's verdict, the same words `--confirm` stamps on the bug."""
    if not v:
        return "none recorded"
    rnd = f"round {v['round']} " if v.get("round") else ""
    return f"{rnd}{v['verdict']} by {v['reviewer']}, seat {v['seat']}"


def trace(root: Path | str, bug: str) -> dict:
    """The proposal for one escaped bug: {bug, release, fix_files, proposals}, each proposal
    {unit, shared, verdict}, most shared files first. Raises `TraceRefused` naming what is
    missing when the bug, its release, its files or the release's units cannot be read."""
    root = Path(root)
    hit = sdlc_md.find_by_id(root, bug)
    if not hit or hit[1] != "bug":
        raise TraceRefused(f"{bug} names no bug on disk")
    path = hit[0]
    text = sdlc_md.read_text_safe(path) or ""
    bid = sdlc_md.extract_record_id(path.stem) or bug
    release = (sdlc_md.extract_field(text, "Shipped-in") or "").strip()
    if not release:
        raise TraceRefused(f"{bid} records no Shipped-in release, so there is no release to "
                           f"trace - file it with --shipped-in; nothing is proposed")
    fix_files = sdlc_md.affects_files(text)
    if not fix_files:
        raise TraceRefused(f"{bid} names no Affects, so no file ties the fix to a unit - "
                           f"nothing is proposed")
    units = [u for u in release_units(root, release) if sdlc_md.norm_id(u) != sdlc_md.norm_id(bid)]
    if not units:
        raise TraceRefused(f"release {release} tags no unit: none of its commits names a "
                           f"story or bug on disk - nothing is proposed")
    proposals = []
    for unit in units:
        found = sdlc_md.find_by_id(root, unit)
        shared = sorted(set(sdlc_md.affects_files(sdlc_md.read_text_safe(found[0]) or ""))
                        & set(fix_files))
        if shared:
            proposals.append({"unit": unit, "shared": shared, "verdict": _verdict(root, unit)})
    proposals.sort(key=lambda p: (-len(p["shared"]), p["unit"]))
    return {"bug": bid, "path": str(path), "release": release, "fix_files": fix_files,
            "units": units, "proposals": proposals}


def _set_line(lines: list[str], field: str, value: str, after: str) -> list[str]:
    """`lines` with the `> **field:**` line set to `value`: replaced where present, else
    inserted after the `> **after:**` line, else after the last line of the header block."""
    new = f"> **{field}:** {value}"
    for i, ln in enumerate(lines):
        if ln.startswith(f"> **{field}:**"):
            return lines[:i] + [new] + lines[i + 1:]
    anchor = next((i for i, ln in enumerate(lines) if ln.startswith(f"> **{after}:**")), None)
    if anchor is None:
        heads = [i for i, ln in enumerate(lines) if ln.startswith("> **")]
        anchor = heads[-1] if heads else 0
    return lines[:anchor + 1] + [new] + lines[anchor + 1:]


def confirm(root: Path | str, bug: str, unit: str) -> dict:
    """Record `unit` as the one that let `bug` through: set `Escaped-via` and stamp the verdict
    row as `Escaped-verdict`. Refuses, writing nothing, a unit that is not a proposal."""
    result = trace(root, bug)
    pick = next((p for p in result["proposals"]
                 if sdlc_md.norm_id(p["unit"]) == sdlc_md.norm_id(unit)), None)
    if pick is None:
        if any(sdlc_md.norm_id(u) == sdlc_md.norm_id(unit) for u in result["units"]):
            why = (f"shares no file with the fix ({', '.join(result['fix_files'])})")
        else:
            why = f"is not a unit release {result['release']} shipped"
        raise TraceRefused(f"{unit} {why}, so it cannot have let {result['bug']} through - "
                           f"refused, nothing written")
    path = Path(result["path"])
    text = path.read_text(encoding="utf-8")
    lines = _set_line(text.splitlines(), "Escaped-via", pick["unit"], "Shipped-in")
    lines = _set_line(lines, "Escaped-verdict", describe_verdict(pick["verdict"]), "Escaped-via")
    sdlc_md.atomic_write(path, "\n".join(lines) + ("\n" if text.endswith("\n") else ""))
    return {**result, "confirmed": pick}


def to_class(root: Path | str, bug: str, name: str, rule: str, behaviour: str) -> dict:
    """Record a confirmed escape's root cause as a failure class and return its row.

    The bug must be escaped (`Escaped: yes`), confirmed (an `Escaped-via` unit) and have a
    written Root Cause. The row goes through `lessons.class_add`, the function `lessons.py
    class-add` runs, injected at build and review, its `evidence` the bug and the unit, its
    `files` the bug's Affects paths and its source `escape:<bug>`. Raises `TraceRefused`,
    writing nothing, for any other bug or for a class the store already holds."""
    # Deferred sibling: its gate is the one reader of an unwritten Root Cause.
    import transition  # noqa: PLC0415
    root = Path(root)
    hit = sdlc_md.find_by_id(root, bug)
    if not hit or hit[1] != "bug":
        raise TraceRefused(f"{bug} names no bug on disk")
    text = sdlc_md.read_text_safe(hit[0]) or ""
    bid = sdlc_md.extract_record_id(hit[0].stem) or bug
    if (sdlc_md.extract_field(text, "Escaped") or "").strip().lower() != "yes":
        raise TraceRefused(f"{bid} is not escaped (no `Escaped: yes`), so it reached no "
                           f"production and carries no escape to learn from - nothing written")
    via = (sdlc_md.extract_field(text, "Escaped-via") or "").strip()
    if not via:
        raise TraceRefused(f"{bid} records no Escaped-via, so no unit is confirmed as the one "
                           f"that let it through - run escape.py trace --bug {bid} --confirm "
                           f"UNIT first; nothing written")
    unwritten = transition._escaped_root_cause_gate(text, "made a failure class")
    if unwritten:
        raise TraceRefused(f"{bid}: {unwritten}; nothing written")
    try:
        return lessons.class_add(root, name, rule, behaviour, ("build", "review"),
                                 f"escape:{bid}", files=sdlc_md.affects_files(text),
                                 evidence=[bid, via])
    except (OSError, ValueError) as exc:
        raise TraceRefused(f"{exc}; nothing written") from exc


def _date(value, what: str) -> date:
    """`value` as a date when it is a `YYYY-MM-DD` string naming a real day, else `RateRefused`
    naming `what`. The pattern is checked first, so a compact `20260105` is refused on every
    Python, not only on those whose `fromisoformat` rejects it."""
    if isinstance(value, str) and _DATE_RE.fullmatch(value):
        try:
            return date.fromisoformat(value)
        except ValueError:
            pass
    raise RateRefused(f"{what} is not a date YYYY-MM-DD: {value!r}")


def _bare(version: str) -> str:
    """A release name with one leading `v` or `V` dropped, so `v1.1.0` and `1.1.0` are one."""
    return version[1:] if version[:1] in ("v", "V") else version


def _root_cause_written(text: str) -> bool:
    """True when an issue's Root Cause section is written, judged by the one reader of an
    unwritten section, the escaped-bug gate. The gate is asked with `Escaped: yes` set first,
    so the issue's own fields cannot excuse it from the test."""
    import transition  # noqa: PLC0415 - deferred sibling, as `to_class` reads it
    return transition._escaped_root_cause_gate("> **Escaped:** yes\n" + text, "counted") is None


def _release_dates(root: Path) -> dict[str, tuple[str, date]]:
    """{bare version: (version as recorded, date)} from the release record file, empty when it
    is absent. Raises `RateRefused` naming the line for a line `release_cut` cannot read, a
    record whose `date` is not `YYYY-MM-DD`, and a release recorded on two lines."""
    import release_cut  # noqa: PLC0415 - deferred sibling: the reader of the record it writes
    try:
        text, records = release_cut._release_records(root)
    except ValueError as exc:
        raise RateRefused(str(exc)) from exc
    lines = [n for n, line in enumerate(text.splitlines(), 1) if line.strip()]
    out: dict[str, tuple[str, date]] = {}
    first: dict[str, int] = {}
    for n, rec in zip(lines, records):
        when = _date(rec.get("date"), f"{release_cut.RELEASES_REL} line {n}'s date")
        key = _bare(rec["version"])
        if key in out:
            raise RateRefused(f"{release_cut.RELEASES_REL} lines {first[key]} and {n} both "
                              f"record release {key}; keep one")
        out[key], first[key] = (rec["version"], when), n
    return out


def _incident_links(root: Path) -> tuple[set[str], dict[str, tuple[str, list[str]]]]:
    """(the incident ids, {bug id: (Shipped-in, [incident ids])}) for each escaped bug with a
    `Shipped-in` that an incident is linked to: named in the issue's `Decomposed-into`, or
    naming the issue as its `Parent`."""
    incidents: dict[str, str] = {}
    children: dict[str, set[str]] = {}
    for path, text in sdlc_md.iter_artifact_files("issue", root):
        text = text or ""
        if not _root_cause_written(text):
            continue
        iid = sdlc_md.extract_record_id(path.stem)
        incidents[sdlc_md.norm_id(iid)] = iid
        children[sdlc_md.norm_id(iid)] = {sdlc_md.norm_id(b) for b in sdlc_md.decomposed_ids(text)}
    links: dict[str, tuple[str, list[str]]] = {}
    for path, text in sdlc_md.iter_artifact_files("bug", root):
        text = text or ""
        bid = sdlc_md.extract_record_id(path.stem)
        shipped = sdlc_md.extract_field(text, "Shipped-in")
        if (sdlc_md.extract_field(text, "Escaped") or "").lower() != "yes" or not shipped:
            continue
        parents = {sdlc_md.norm_id(p) for p in sdlc_md.parent_refs(text)}
        named = [incidents[k] for k in incidents
                 if k in parents or sdlc_md.norm_id(bid) in children[k]]
        if named:
            links[bid] = (shipped, named)
    return set(incidents.values()), links


def _percent(failed: int, counted: int) -> int | float:
    """The rate as a whole number when exact, else rounded to one decimal."""
    if (100 * failed) % counted == 0:
        return 100 * failed // counted
    return round(100 * failed / counted, 1)


def failure_rate(root: Path | str, since: str | None = None, until: str | None = None,
                 settle_days: int = SETTLE_DAYS) -> dict:
    """Change failure rate over a window: the releases with at least one linked incident divided
    by the releases counted. The one calculation, which `failure-rate` prints.

    The window runs from `since` to `until`, both included, as `YYYY-MM-DD`: `until` defaults
    to today (UTC, the clock the release cut dates its records by), `since` to the
    `WINDOW_DAYS` days ending on `until`. A release dated in it is pending while it is younger
    than `settle_days` at the earlier of `until` and today, and is then neither counted nor
    failed, even when an incident already names it. Returns {rate_percent, counted, failed:
    [{release, incidents, bugs}], pending, unrecorded: [{bug, shipped_in, incidents}], since,
    until, settle_days, not_measured}. `rate_percent` is None and `not_measured` gives the
    reason when the window holds no release record, every release in it is pending, or no
    incident is recorded, checked in that order. `unrecorded` names the linked bugs whose
    release no record holds, which move no figure. Raises `RateRefused` for a date that does not
    parse, `since` after `until`, a negative `settle_days`, or a record file it cannot read."""
    root = Path(root)
    today = date.fromisoformat(sdlc_md.now_date())
    end = _date(until, "--until") if until is not None else today
    start = (_date(since, "--since") if since is not None
             else end - timedelta(days=WINDOW_DAYS - 1))
    if start > end:
        raise RateRefused(f"--since {start} is after --until {end}")
    if settle_days < 0:
        raise RateRefused(f"--settle-days must be 0 or more, not {settle_days}")
    releases = _release_dates(root)
    as_of = min(end, today)
    in_window = sorted((when, version) for version, when in releases.values()
                       if start <= when <= end)
    counted = [v for when, v in in_window if (as_of - when).days >= settle_days]
    pending = [v for when, v in in_window if (as_of - when).days < settle_days]
    incidents, links = _incident_links(root)
    by_release: dict[str, tuple[set[str], set[str]]] = {}
    unrecorded = []
    for bid, (shipped, named) in links.items():
        if _bare(shipped) not in releases:
            unrecorded.append({"bug": bid, "shipped_in": shipped, "incidents": named})
            continue
        hit = by_release.setdefault(releases[_bare(shipped)][0], (set(), set()))
        hit[0].update(named)
        hit[1].add(bid)
    failed = [{"release": v, "incidents": sorted(by_release[v][0]),
               "bugs": sorted(by_release[v][1])} for v in counted if v in by_release]
    if not in_window:
        reason = ("no release record in the window: a release is recorded when `release_cut.py "
                  "changelog-cut` cuts it, so one cut before that record existed has none")
    elif not counted:
        reason = (f"every release in the window is still inside the {settle_days}-day settling "
                  f"period: {', '.join(pending)}")
    elif not incidents:
        reason = ("no incident recorded: an incident is an issue whose `## Root Cause` section "
                  "is written, triaged into the escaped bugs it caused")
    else:
        reason = None
    return {"rate_percent": None if reason else _percent(len(failed), len(counted)),
            "counted": counted, "failed": failed, "pending": pending, "unrecorded": unrecorded,
            "since": start.isoformat(), "until": end.isoformat(), "settle_days": settle_days,
            "not_measured": reason}


def _plural(noun: str, items: list[str]) -> str:
    return f"{noun}{'' if len(items) == 1 else 's'} {', '.join(items)}"


def cmd_failure_rate(args: argparse.Namespace) -> int:
    try:
        result = failure_rate(args.root, args.since, args.until, args.settle_days)
    except RateRefused as exc:
        print(f"escape failure-rate refused: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(result, indent=2))
        return 0
    if result["not_measured"]:
        print(f"change failure rate not measured: {result['not_measured']}")
    else:
        print(f"change failure rate {result['rate_percent']}% ({len(result['failed'])} of "
              f"{len(result['counted'])} releases)")
    period = f"{result['settle_days']}-day settling period"
    print(f"window: {result['since']} to {result['until']} (both days included), {period}")
    if result["not_measured"]:
        return 0
    print(f"counted: {', '.join(result['counted'])}")
    print("failed: " + ("; ".join(
        f"{f['release']} ({_plural('incident', f['incidents'])}; {_plural('bug', f['bugs'])})"
        for f in result["failed"]) or "none"))
    print("pending: " + (f"{', '.join(result['pending'])} (inside the {period})"
                         if result["pending"] else "none"))
    for u in result["unrecorded"]:
        print(f"linked to an unrecorded release: {u['bug']} names {u['shipped_in']} "
              f"({_plural('incident', u['incidents'])}); it moves no figure: record the release "
              f"or correct the bug's Shipped-in")
    return 0


def cmd_to_class(args: argparse.Namespace) -> int:
    try:
        row = to_class(args.root, args.bug, args.class_name, args.rule, args.behaviour)
    except TraceRefused as exc:
        print(f"escape to-class refused: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(row, indent=2))
        return 0
    files = ", ".join(row.get("files") or ()) or "no files"
    print(f"recorded {row['id']} {row['class']} [{', '.join(row['inject'])}] in "
          f"{lessons.STORE_FILE}, from {', '.join(row.get('evidence') or ())}; applies to {files}")
    return 0


def cmd_trace(args: argparse.Namespace) -> int:
    try:
        result = (confirm(args.root, args.bug, args.confirm) if args.confirm
                  else trace(args.root, args.bug))
    except TraceRefused as exc:
        print(f"escape trace refused: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(result, indent=2))
        return 0
    if result.get("confirmed"):
        pick = result["confirmed"]
        print(f"recorded {pick['unit']} as Escaped-via on {result['bug']}; Escaped-verdict: "
              f"{describe_verdict(pick['verdict'])}")
        return 0
    print(f"{result['bug']} shipped in {result['release']}; the fix touches "
          f"{', '.join(result['fix_files'])}")
    if not result["proposals"]:
        print(f"no unit {result['release']} shipped shares a file with the fix")
        return 0
    print("proposed, most shared files first:")
    for p in result["proposals"]:
        print(f"  {p['unit']}  shares {', '.join(p['shared'])}  verdict "
              f"{describe_verdict(p['verdict'])}")
    print(f"record one with: escape.py trace --bug {result['bug']} --confirm "
          f"{result['proposals'][0]['unit']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Trace an escaped bug to the unit and review that "
                                            "let it through.")
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("trace", help="propose the units of the bug's release that share a file "
                                     "with its fix, each with its recorded verdict and seat")
    t.add_argument("--bug", required=True, help="the escaped bug, carrying Shipped-in and Affects")
    t.add_argument("--confirm", metavar="UNIT",
                   help="record this proposed unit as Escaped-via, with its verdict as "
                        "Escaped-verdict; a unit that is not proposed is refused")
    t.add_argument("--root", default=".")
    t.add_argument("--format", choices=("text", "json"), default="text")
    t.set_defaults(func=cmd_trace)
    c = sub.add_parser("to-class", help="record a confirmed escape's root cause as a failure "
                                        "class in the lessons store, carrying the bug's Affects")
    c.add_argument("--bug", required=True,
                   help="the escaped bug, carrying Escaped-via and a written Root Cause")
    c.add_argument("--class", dest="class_name", required=True, metavar="NAME",
                   help="the class's short name; refused when the store already holds it")
    c.add_argument("--rule", required=True, help="what the class is and the rule it breaks")
    c.add_argument("--behaviour", required=True, help="what to do differently")
    c.add_argument("--root", default=".")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_to_class)
    r = sub.add_parser("failure-rate", help="change failure rate: releases with a linked incident "
                                            "over the releases counted, or not measured")
    r.add_argument("--since", metavar="YYYY-MM-DD",
                   help=f"the window's first day (default: the {WINDOW_DAYS} days ending on "
                        f"--until, both days included)")
    r.add_argument("--until", metavar="YYYY-MM-DD",
                   help="the window's last day (default: today, UTC)")
    r.add_argument("--settle-days", type=int, default=SETTLE_DAYS, metavar="N",
                   help=f"days a release is held as pending before it counts (default: "
                        f"{SETTLE_DAYS})")
    r.add_argument("--root", default=".")
    r.add_argument("--format", choices=("text", "json"), default="text",
                   help="text or json; the rate prints as a whole number when exact, else to "
                        "one decimal")
    r.set_defaults(func=cmd_failure_rate)
    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
