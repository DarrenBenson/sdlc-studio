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

Verbs are subcommands, so a further step of the escape record adds a parser beside these.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
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


class TraceRefused(Exception):
    """A trace that cannot be made or recorded; the CLI exits 2 with its message."""


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
    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
