#!/usr/bin/env python3
"""Detect an owed sprint close-down: delivery units that reached a terminal state but that
no retro's `Batch` has ever accounted for.

The close-down (retro + lesson extraction + close gate) is mandated but, until now, only ran
when an agent voluntarily invoked `gate --require-retro`. Nothing DETECTED a skipped close, so
under delivery pressure the ceremony silently lapsed and the lessons stopped compounding. This
is the thing a gate can interrogate: a deterministic answer to "is a close owed right now?".

The rule. A delivery unit (epic / story / bug) that is terminal (Done / Fixed / ...) is COVERED
when some retro's `> **Batch:**` field names it - that retro is the close that accounted for it.
An uncovered terminal unit is a candidate for "close owed".

The grandfather baseline. A project that adopts this after many sprints carries a large tail of
historically-closed units that predate story-level retro batches (this repo had 283 at adoption).
Treating that tail as "owed" would block forever with no signal, so the feature BASELINES: `close_owed
baseline` snapshots the exact SET of ids terminal at adoption into a committed
`.close-owed-baseline.json`. From then on, only a unit that reaches terminal LATER (one not in that
set) can owe a close. A set, not a per-prefix id cutoff: a highest-id cutoff would silently forgive
any unit in flight at adoption that closes later - the false "none owed" this exists to kill - and
breaks entirely on non-numeric (ULID / schema-v3) ids. The pre-existing debt is recorded and
acknowledged, not hidden, and not enforced retroactively. Until a baseline is stamped the detector
reports every uncovered unit and nudges you to stamp one - it never invents a cutoff.

Skill/consuming-project neutral, pure stdlib. Read-only except `baseline`, which writes the one
snapshot file.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import retro  # noqa: E402  (sibling - for the `Batch` field pattern, so both read the same line)

# The delivery backlog: the units a sprint sets out to complete and a retro accounts for.
# Discovery artefacts (RFC/CR/Issue) reach terminal by derivation from these, so they are not
# themselves a "close owed" trigger - closing the delivery work is what a retro records.
DELIVERY_TYPES = ("epic", "story", "bug")

# Id prefixes coverage can be earned by. Outside a parenthetical, any delivery unit; INSIDE one,
# only a leaf. See `batch_covered_ids`.
DELIVERY_PREFIXES = ("EP", "US", "BG")
LEAF_PREFIXES = ("US", "BG")

_PARENTHETICAL_RE = re.compile(r"\(([^)]*)\)")

BASELINE_FILE = "sdlc-studio/.close-owed-baseline.json"


def batch_covered_ids(text: str) -> set[str]:
    """The unit ids a retro's `Batch` line accounts for, parentheticals included.

    Deliberately NOT `retro.batch_ids`. That parses the same line for `retro accuracy`, which
    asks a different question - which units carry a plan-time forecast - and so strips every
    `(...)` as provenance (`(absorbing CR0139)`, `(EP0075-EP0077, from RFC0044)`). Read as
    coverage, that strip made a Batch of `BG0219, EP0090 (US0276)` - the natural way to write a
    story delivered under its epic - leave US0276 reported as owed by the very retro naming it.
    A false alarm costs what a miss costs: the line gets reworded to silence the detector, and a
    detector people work around has stopped detecting.

    Matching uses `sdlc_md.ID_SEARCH_RE`, the canonical unanchored id matcher the rest of the
    codebase shares, rather than a third private regex. It carries the boundary rules already
    paid for: a leading letter is not an id (`SUS0001`), the digit run is `\\d{4,}` so a
    five-digit id is claimed WHOLE instead of a four-digit prefix being credited to a different
    real unit, and a v3 ULID id is matched at all.

    Widening stops at the smallest set that answers the bug. Only a LEAF unit (story or bug)
    earns coverage from inside a parenthetical, because that is what a parenthetical reports as
    delivered; an epic there is provenance - which epic decomposed the batch - and crediting it
    would forgive an epic no close had derived. Outside the parentheses the flat list credits
    any delivery unit, as before.
    """
    m = retro.BATCH_RE.search(text)
    if not m:
        return set()
    line = retro.PLACEHOLDER_RE.sub("", m.group(1))
    flat = _PARENTHETICAL_RE.sub(" ", line)
    inner = " ".join(_PARENTHETICAL_RE.findall(line))
    out: set[str] = set()
    for chunk, allowed in ((flat, DELIVERY_PREFIXES), (inner, LEAF_PREFIXES)):
        for hit in sdlc_md.ID_SEARCH_RE.finditer(chunk):
            rid = sdlc_md.norm_id(hit.group(0))
            if rid.startswith(allowed):
                out.add(rid)
    return out


def covered_ids(root: Path) -> set[str]:
    """Every unit id named in any retro's `Batch` - the set of closes already accounted for."""
    covered: set[str] = set()
    retros_dir = root / "sdlc-studio" / "retros"
    if not retros_dir.is_dir():
        return covered
    for p in sorted(retros_dir.glob("RETRO*.md")):
        # a bad retro must not crash the scan
        covered |= batch_covered_ids(sdlc_md.read_text_safe(p))
    return covered


def scan_delivery(root: Path) -> tuple[list[tuple[str, str]], set[str]]:
    """One pass over the delivery tree: `(terminal units as (id, type), every delivery id)`.

    Both answers come from the same walk because reading the tree is the whole cost. Taking
    them separately doubled the detector's runtime on a repo this size for an identical
    result.
    """
    out: list[tuple[str, str]] = []
    ids: set[str] = set()
    for type_ in DELIVERY_TYPES:
        vocab = sdlc_md.status_vocab(type_, root)
        for p in sdlc_md.artifact_files(type_, root):
            cid = sdlc_md.extract_record_id(p.stem)
            if not cid:
                continue
            ids.add(sdlc_md.norm_id(cid))
            status = sdlc_md.canonical_status(
                sdlc_md.extract_field(sdlc_md.read_text_safe(p), "Status"), vocab)
            if status and sdlc_md.is_terminal_status(type_, status):
                out.append((cid, type_))
    return out, ids


def terminal_delivery_units(root: Path) -> list[tuple[str, str]]:
    """Every terminal delivery unit as `(id, type)` - the population a close accounts for."""
    return scan_delivery(root)[0]


def _breakdown_child_ids(root: Path, cid: str, known: set[str]) -> tuple[set[str], set[str]]:
    """`(coverable, dead)` child ids for an epic.

    BOTH id sets are read, because the two answers to "what is a child" can differ: the
    derivation that closed this epic reads its DECLARED Story Breakdown, while `children_of`
    reads whatever names the epic as a parent. An id in one but not the other would otherwise
    be invisible, forgiving the epic off a strict subset of the children its own closure was
    derived from.

    A DEAD id is one a retro can never account for: no backing file (split, renamed, deleted),
    or a non-delivery artefact - a CR or an RFC is a discovery item, and a `Batch` names
    delivery units. Demanding coverage of one asks for something no close can supply, so the
    epic is owed a close forever and every close leaves it owed. Dead ids are therefore
    excluded from the demand and returned separately to be REPORTED: the id is still a real
    defect in the breakdown, and forgiving it silently would trade a false debt for a hidden
    fault.
    """
    import reconcile  # noqa: PLC0415 - lazy, like the chain's other sibling imports
    found = sdlc_md.find_by_id(root, cid)     # one full-tree scan, not one per branch
    declared = (reconcile.declared_breakdown_ids(sdlc_md.read_text_safe(found[0]))
                if found else [])
    coverable = {sdlc_md.norm_id(c) for c, *_ in sdlc_md.children_of(root, cid)}
    dead: set[str] = set()
    for raw in declared:
        norm = sdlc_md.norm_id(raw)
        if norm in coverable:
            continue                          # already a resolved child; nothing to check
        if norm in known:
            coverable.add(norm)
        else:
            dead.add(norm)                    # no file at all, or a CR/RFC/Issue
    return coverable, dead


class BaselineCorrupt(Exception):
    """The baseline file is present but unreadable or mis-shaped - a loud BLOCKING state, never
    'allow' and never a re-stamp. A corrupt-vs-absent conflation would let one merge-conflict
    marker in the committed snapshot silently disarm the whole close-down, and the unbaselined
    path then invites `close_owed baseline`, which would grandfather exactly the units that owe a
    close. Repair the file (restore it from git, or fix the JSON) - do not re-stamp it."""


def load_baseline(root: Path) -> dict | None:
    """The stamped grandfather set, or None when the project has not baselined yet.

    A present-but-corrupt file (truncated, merge-conflict markers, a JSON array, a dict whose
    `grandfathered` is not a list of ids) is NOT None: it raises BaselineCorrupt, so a damaged
    snapshot is a distinct blocking state rather than indistinguishable from 'never baselined'.
    """
    fp = root / BASELINE_FILE
    if not fp.exists():
        return None
    try:
        data = json.loads(fp.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise BaselineCorrupt(f"{BASELINE_FILE} is present but unparseable ({exc})") from exc
    if not isinstance(data, dict):
        raise BaselineCorrupt(f"{BASELINE_FILE} is not a JSON object (found {type(data).__name__})")
    gf = data.get("grandfathered")
    if not isinstance(gf, list) or any(not isinstance(x, str) for x in gf):
        raise BaselineCorrupt(f"{BASELINE_FILE} has no valid 'grandfathered' list of ids")
    return data


def owed(root: Path) -> dict:
    """The deterministic close-owed report.

    `baselined` is False when no baseline is stamped: then `owed` lists every uncovered terminal
    unit and the caller must stamp a baseline before the signal means anything. When baselined,
    `owed` is the uncovered units NOT in the grandfathered set - the work closed since adoption
    that no retro has accounted for. `grandfathered` counts the uncovered units the baseline
    forgives.

    The baseline is the exact SET of ids terminal at adoption, not a per-prefix id cutoff. A
    highest-id cutoff silently forgives any unit that was in flight (a lower id, non-terminal) at
    adoption and closes later - the precise false "none owed" this feature exists to kill - and
    breaks entirely on non-numeric (ULID / schema-v3) ids. Membership in a set has neither hole.
    """
    covered = covered_ids(root)
    terminal, known = scan_delivery(root)     # one tree scan, reused by every epic below
    uncovered: list[tuple[str, str]] = []
    dead_ids: list[list[str]] = []
    for cid, t in terminal:
        if sdlc_md.norm_id(cid) in covered:
            continue
        # ONLY an epic inherits coverage from its children. An epic does not reach terminal by
        # being worked; it is DERIVED terminal once every child is terminal, and that derivation
        # runs in the close tail AFTER the retro is written - so an epic is never named in a
        # `Batch`, and requiring it to be named made every clean close manufacture close-owed
        # debt for the epics it had just derived, debt no further close could clear. The retro
        # that accounted for the children is the close that accounted for the epic.
        #
        # Recording the epics in the `Batch` instead was the obvious alternative and is wrong:
        # `retro accuracy` sums points across the batch and an epic's Derived Point Total is the
        # sum of its stories, so it would double-count every sprint's velocity.
        #
        # A story or bug can carry children too (a story naming a parent epic is the same shape
        # inverted), so this guard is load-bearing and stays owed on its own account.
        if t != "epic":
            uncovered.append((cid, t))
            continue
        # ONE call per epic: both answers come out of the same walk, and asking twice was
        # measurably slower for an identical result.
        child_ids, dead = _breakdown_child_ids(root, cid, known)
        # A CHILDLESS epic inherits nothing - there is no derivation to inherit from - and an
        # epic with one unaccounted child stays owed. Without both, the relaxation would be a
        # blanket exemption for epics, a vacuous pass.
        if not child_ids or not all(c in covered for c in child_ids):
            uncovered.append((cid, t))
            continue
        # Forgiven through its children. Report the dead ids ONLY here - an epic whose
        # coverage did not depend on the relaxation is unaffected by them, and this repo
        # carries 33 historical CR-in-breakdown declarations on epics the baseline already
        # forgives. Reporting those would put a permanent 33-line advisory on every run to
        # describe records that change no answer, which is the skim-past failure BG0210 was
        # filed for, in advisory form.
        for bad in sorted(dead):
            dead_ids.append([cid, bad])
    dead_ids.sort()
    try:
        baseline = load_baseline(root)
    except BaselineCorrupt as exc:
        # A present-but-corrupt baseline is a loud blocking state: never 'allow', never a
        # re-stamp nudge. The enforcement halves must fail closed and direct a repair.
        return {"baselined": False, "corrupt": True, "error": str(exc), "owed": [],
                "grandfathered": 0, "covered": len(covered), "terminal": len(terminal),
                "dead_breakdown_ids": dead_ids}
    if baseline is None:
        return {"baselined": False, "corrupt": False, "owed": sorted(uncovered),
                "grandfathered": 0, "covered": len(covered), "terminal": len(terminal),
                "dead_breakdown_ids": dead_ids}
    forgiven = {sdlc_md.norm_id(x) for x in baseline["grandfathered"]}
    owed_units = [(cid, t) for (cid, t) in uncovered if sdlc_md.norm_id(cid) not in forgiven]
    return {"baselined": True, "corrupt": False, "owed": sorted(owed_units),
            "grandfathered": len(uncovered) - len(owed_units),
            "covered": len(covered), "terminal": len(terminal),
            "dead_breakdown_ids": dead_ids}


def stamp_baseline(root: Path, date: str | None = None, note: str | None = None,
                   exclude: set[str] | None = None) -> dict:
    """Snapshot the SET of ids terminal at adoption as the grandfather set, and write it.

    Every unit terminal at this instant is forgiven forever; only units that reach terminal LATER
    (or an already-terminal unit not in the set) can owe a close. `exclude` drops ids from the
    snapshot - used when adoption predates work already closed in the same session, so that work
    is still held to a close rather than grandfathered by the act of stamping.
    """
    drop = {sdlc_md.norm_id(x) for x in (exclude or set())}
    grandfathered = sorted({sdlc_md.norm_id(cid) for cid, _t in terminal_delivery_units(root)}
                           - drop)
    data = {
        "grandfathered": grandfathered,
        "stamped": date or sdlc_md.now_date(),
        "note": note or "Ids terminal at adoption; only later closes can owe a retro.",
    }
    (root / BASELINE_FILE).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def render(report: dict) -> str:
    n = len(report["owed"])
    if report.get("corrupt"):
        return (f"close owed: BASELINE CORRUPT - {report.get('error', BASELINE_FILE)}. "
                f"The close-down cannot be judged and is BLOCKED until the file is repaired "
                f"(restore it from git, or fix the JSON). Do NOT run `close_owed baseline`: "
                f"re-stamping would forgive the very units that owe a close.")
    if not report["baselined"]:
        head = (f"close owed: UNBASELINED - {n} uncovered terminal unit(s). "
                f"Run `close_owed baseline` to grandfather the existing tail, "
                f"then only later work can owe a close.")
    elif n == 0:
        head = (f"close owed: none. {report['covered']} unit(s) accounted for by retros; "
                f"{report['grandfathered']} grandfathered.")
    else:
        head = (f"close owed: {n} delivery unit(s) reached terminal since the baseline with no "
                f"retro accounting for them - a sprint close is owed "
                f"(run the retro, then `gate --require-retro RETROxxxx`).")
    lines = [head]
    if n and (not report["baselined"] or n <= 40):
        lines.append("  " + ", ".join(f"{cid} ({t})" for cid, t in report["owed"]))
    elif n:
        shown = report["owed"][:40]
        lines.append("  " + ", ".join(f"{cid} ({t})" for cid, t in shown) + f", +{n - 40} more")
    dead = report.get("dead_breakdown_ids") or []
    if dead:
        # Advisory, never blocking: the epic is forgiven above precisely because no close can
        # satisfy this demand, so failing on it would restore the unclearable debt by another
        # name. It is surfaced because a breakdown naming an id that does not resolve to a
        # delivery unit is a real defect - fix the breakdown, or retire the id.
        lines.append(f"  advisory: {len(dead)} declared breakdown id(s) resolve to no delivery "
                     f"unit, so no retro can ever account for them - they are excluded from the "
                     f"coverage demand rather than owed forever. Fix the epic's Story Breakdown:")
        lines.append("  " + ", ".join(f"{epic} declares {bad}" for epic, bad in dead[:20])
                     + (f", +{len(dead) - 20} more" if len(dead) > 20 else ""))
    return "\n".join(lines)


def cmd_detect(args: argparse.Namespace) -> int:
    report = owed(Path(args.root))
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(render(report))
    # Non-zero when a close is genuinely owed (baselined AND owed units exist) OR when the baseline
    # is corrupt - so a gate or hook can branch on the exit code. An unbaselined project is a soft
    # state (exit 0); a corrupt baseline is a loud blocking failure, never a silent pass.
    return 1 if (report.get("corrupt") or (report["baselined"] and report["owed"])) else 0


def cmd_baseline(args: argparse.Namespace) -> int:
    data = stamp_baseline(Path(args.root), date=args.date, note=args.note)
    n = len(data["grandfathered"])
    print(f"baseline stamped ({data['stamped']}): grandfathered {n} unit(s) terminal at adoption. "
          f"Only later closes can owe a retro. Wrote {BASELINE_FILE}.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Detect an owed sprint close-down.")
    p.add_argument("--root", default=".", help="Repo root (default: .)")
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("detect", help="Report delivery units that owe a close (non-zero if any).")
    d.add_argument("--format", choices=["text", "json"], default="text")
    d.set_defaults(func=cmd_detect)
    b = sub.add_parser("baseline", help="Grandfather the set terminal at adoption; only later closes can owe.")
    b.add_argument("--date", help="Stamp date (default: today)")
    b.add_argument("--note", help="Override the baseline note")
    b.set_defaults(func=cmd_baseline)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
