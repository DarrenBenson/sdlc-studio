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
from lib import run_state  # noqa: E402  (the run's own vocabulary for open vs finished)

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

# THE OTHER HALF OF A CLOSE: the velocity row.
#
# The coverage rule above asks one question - does some retro's `Batch` name this unit - and
# nothing asked whether the accuracy and velocity write ran at all. So `accuracy --write`
# shipped and sprint after sprint still closed with no row in the velocity record, which means
# the tokens-per-point rate every plan quotes was never re-measured against them.
#
# The demand is for the ROW, never for a token total. A row with a blank Actual and a recorded
# reason is a COMPLETE close: it states that the sprint's cost was not recoverable, which is a
# fact the record holds. No row at all states nothing, and is indistinguishable from the write
# having been skipped.
#
# Scoped by the same grandfather doctrine the unit half obeys: only a retro DATED on or after
# the baseline stamp can owe a row. Without that, adopting the check hands a project a tail of
# historical retros no close can ever clear.
VELOCITY_FILE = "sdlc-studio/retros/VELOCITY.md"
#: The recorded escape: `> **Velocity-override:** <why this retro can have no row>`. It travels
#: with the record rather than in a command flag, so the reason is auditable afterwards - and a
#: BARE marker with no reason is not an override, by the same rule the retro's own `declined:`
#: disposition obeys.
#:
#: Read with its OWN line-anchored pattern rather than `sdlc_md.extract_field`, which falls
#: through an empty value to the next non-blank line: an override left blank would then be
#: "reasoned" by whatever prose followed it, which is the bare dodge dressed as a reason.
VELOCITY_OVERRIDE_RE = re.compile(r"(?mi)^>?\s*\*\*Velocity-override:\*\*[ \t]*(.*)$")

#: THE RECORDED EXCEPTION for a repair that genuinely could not be deferred:
#: `> **Close-repair-override:** BG0123 - <why this could not wait>`, one line per unit.
#:
#: It travels with the retro rather than in a command flag, on the same reasoning as the
#: velocity override beside it: an escape nobody can read afterwards is a silent pass. And by
#: the same rule, a BARE marker is not an override - an exception has to cost a sentence, or it
#: becomes the routine the rule was written against.
#:
#: PER UNIT, because one exception must not license the next. The unit id is required: an
#: override naming nothing would forgive every close-time repair in the run at once, which is
#: the blanket exemption this is specifically not.
CLOSE_REPAIR_OVERRIDE_RE = re.compile(
    r"(?mi)^>?\s*\*\*Close-repair-override:\*\*[ \t]*(.*)$")


def close_repair_overrides(root: Path) -> dict:
    """`{unit_id: reason}` for every reasoned close-repair override across the retros.

    A line naming no unit, or naming one with no reason after it, contributes nothing - it is
    the bare dodge dressed as a reason, and it is dropped rather than honoured.
    """
    out: dict = {}
    retros_dir = Path(root) / "sdlc-studio" / "retros"
    if not retros_dir.is_dir():
        return out
    for p in sorted(retros_dir.glob("RETRO*.md")):
        for m in CLOSE_REPAIR_OVERRIDE_RE.finditer(sdlc_md.read_text_safe(p)):
            raw = " ".join(retro.PLACEHOLDER_RE.sub("", m.group(1)).split())
            hit = sdlc_md.ID_SEARCH_RE.search(raw)
            if not hit:
                continue
            reason = raw[hit.end():].lstrip(" -:\u2013").strip()
            if reason:
                out[sdlc_md.norm_id(hit.group(0))] = reason
    return out


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


def velocity_owed(root: Path, stamped: str) -> dict:
    """Which retros dated on or after `stamped` have no row in the velocity record.

    `{"owed": [(retro_id, date)], "overrides": [(retro_id, reason)], "undated": [retro_id]}`.

    THREE outcomes, and each is reported rather than assumed:

    * OWED - dated on or after the stamp, no row, no recorded override. The accuracy write did
      not run, and nothing else in this project would ever say so.
    * OVERRIDDEN - the retro records why it can have no row. Named, with its reason, because an
      escape nobody can read afterwards is a silent pass.
    * UNDATED - the retro carries no `Date`, so it cannot be placed either side of the stamp.
      Not demanded (guessing would rebuild the unclearable tail the baseline exists to prevent)
      and not hidden either.

    The rows are read with `retro.velocity_history`, so this asks the same question of the file
    that the planner does: a row the reader cannot parse is a row that is not there.
    """
    retros_dir = root / "sdlc-studio" / "retros"
    if not retros_dir.is_dir():
        return {"owed": [], "overrides": [], "undated": []}
    have = {r["id"] for r in retro.velocity_history(root)}
    owed_rows: list[tuple[str, str]] = []
    overrides: list[tuple[str, str]] = []
    undated: list[str] = []
    for p in sorted(retros_dir.glob("RETRO*.md")):
        # `retro._STEM_ID_RE`, not the general artefact matcher: a RETRO id is a meta id the
        # latter does not recognise, and this must resolve a filename the same way `find_retro`
        # does or the two halves of the close would disagree about which files exist.
        m = retro._STEM_ID_RE.match(p.stem)
        if not m:
            continue
        rid = sdlc_md.norm_id(m.group(1))
        if rid in have:
            continue
        text = sdlc_md.read_text_safe(p)
        m = retro.DATE_RE.search(text)
        date = (m.group(1).strip() if m else "")
        if date and date < stamped:
            continue                       # grandfathered: adoption creates no debt
        mo = VELOCITY_OVERRIDE_RE.search(text)
        why = " ".join(retro.PLACEHOLDER_RE.sub("", mo.group(1)).split()) if mo else ""
        if why:
            overrides.append((rid, why))
        elif not date:
            undated.append(rid)
        else:
            owed_rows.append((rid, date))
    return {"owed": sorted(owed_rows), "overrides": sorted(overrides), "undated": sorted(undated)}


#: Where a terminal close is timestamped. `transition.py` appends one row per unit reaching a
#: terminal status, into a file named for the DAY it happened - so the date a unit closed is on
#: disk already, in the filename, and nobody has to declare it.
_ACTUALS_GLOB = "sdlc-studio/retros/evidence/actuals-*.jsonl"
_ACTUALS_DATE_RE = re.compile(r"actuals-(\d{4}-\d{2}-\d{2})\.jsonl$")


def terminal_dates(root: Path) -> dict:
    """`{unit_id: earliest date it was recorded terminal}`, from the close telemetry.

    DERIVED, never declared. A flag somebody must remember to pass records the honest case and
    misses the careless one, and the careless one is the whole population this ledger exists for.

    Earliest rather than latest: a unit reopened and re-closed owes its account from the first
    close, and taking the later date would let a re-close move a unit out of the owed set.
    """
    out: dict = {}
    for p in sorted(Path(root).glob(_ACTUALS_GLOB)):
        m = _ACTUALS_DATE_RE.search(p.name)
        if not m:
            continue
        day = m.group(1)
        for line in sdlc_md.read_text_safe(p).splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                uid = sdlc_md.norm_id(str(json.loads(line).get("id") or ""))
            except (ValueError, TypeError):
                continue           # a malformed row is not a date, and must not become one
            if uid and (uid not in out or day < out[uid]):
                out[uid] = day
    return out


def close_time_repairs(root: Path, uncovered: list) -> tuple[list, list]:
    """Split `uncovered` into `(close_time_repairs, unaccounted)`.

    A CLOSE-TIME REPAIR is a unit that reached terminal AFTER the most recent retro was written,
    while the run that retro closed was itself already closed. Those are the units a close
    produced about itself: found during the ceremony, fixed, and therefore unaccounted by the
    account written moments earlier. The ledger then re-opened, and the operator's reading was
    that the sprint was never being closed - it was, repeatedly, and each close was undone by
    the next repair.

    "Fixed after the account was written" and "nobody accounted for this" are different facts
    and must not read the same. Both are still REPORTED - the split is about wording and
    countability, not about forgiving anything.

    The two conditions are both load-bearing. Without the date test every uncovered unit would
    be excused; without the run-closed test, ordinary delivery in the NEXT sprint would be
    excused too, because it also postdates the last retro. When a run is open, work reaching
    terminal is that run's batch and owes that run's account - which is the ordinary case.
    """
    repairs, unaccounted = [], []
    latest = _latest_retro_date(root)
    closed = _last_run_is_closed(root)
    dates = terminal_dates(root) if (latest and closed) else {}
    for cid, t in uncovered:
        when = dates.get(sdlc_md.norm_id(cid), "")
        (repairs if (when and latest and when >= latest) else unaccounted).append((cid, t))
    return sorted(repairs), sorted(unaccounted)


def _latest_retro_date(root: Path) -> str:
    """The most recent `> **Date:**` across the retros, or "" when none is dated."""
    best = ""
    retros_dir = Path(root) / "sdlc-studio" / "retros"
    if not retros_dir.is_dir():
        return ""
    for p in sorted(retros_dir.glob("RETRO*.md")):
        m = retro.DATE_RE.search(sdlc_md.read_text_safe(p))
        date = (m.group(1).strip() if m else "")
        if date > best:
            best = date
    return best


def _last_run_is_closed(root: Path) -> bool:
    """Whether the recorded run has FINISHED - an outcome that is not `running`.

    `outcome` is `"running"` while a run is live, so a truthiness test reads an open run as a
    closed one and excuses that run's ordinary delivery as close-time repair. Caught on this
    repository's own tree: the four units delivered into an OPEN run were all reported as
    repairs made during a close that had not started.

    Read defensively: an unreadable or absent run state answers False, so the split degrades to
    calling everything unaccounted. That is the direction that over-reports rather than
    under-reports, and this ledger's whole value is that it does not quietly say "none owed".
    """
    p = Path(root) / "sdlc-studio" / ".local" / "run-state.json"
    try:
        outcome = str((json.loads(p.read_text(encoding="utf-8")) or {}).get("outcome") or "")
    except (OSError, ValueError, TypeError):
        return False
    return bool(outcome) and outcome != run_state.RUNNING


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
            # DELIVERED-terminal only. The terminal set mixes two different things: `Done`
            # and `Fixed` are reached by building, `Won't Fix` / `Superseded` / `Duplicate`
            # by ruling. A close-down accounts for what a sprint DELIVERED, so a unit nobody
            # built can owe no retro - and an advisory no correct action can discharge is one
            # an operator learns to scroll past, which is fatal for the surface that exists
            # so a skipped close is SEEN. Recognised by wording in `sdlc_md`, shared with the
            # transition verb's criteria floor, not by a list of statuses kept here.
            if status and sdlc_md.is_delivered_terminal(type_, status):
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
    # The scan is wrapped so an UNREADABLE tree can be told from an empty one. Every read below
    # degrades quietly by design - one bad artefact must not abort the walk - and the tag guard
    # was reading that silence as "nothing is owed". The swallow stays; the witness is new.
    with sdlc_md.degradation_log():
        covered = covered_ids(root)
        terminal, known = scan_delivery(root)  # one tree scan, reused by every epic below
        degraded = sdlc_md.degradations()
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
                "close_time_repairs": [], "unaccounted": [],
                "grandfathered": 0, "covered": len(covered), "terminal": len(terminal),
                "dead_breakdown_ids": dead_ids, "unreadable": degraded,
                **_no_velocity_demand()}
    if baseline is None:
        # No stamp, so no date to scope the velocity demand to. Reporting every retro on disk
        # would be the unclearable tail again; the baseline nudge below stands on its own.
        return {"baselined": False, "corrupt": False, "owed": sorted(uncovered),
                "close_time_repairs": [], "unaccounted": sorted(uncovered),
                "grandfathered": 0, "covered": len(covered), "terminal": len(terminal),
                "dead_breakdown_ids": dead_ids, "unreadable": degraded,
                **_no_velocity_demand()}
    forgiven = {sdlc_md.norm_id(x) for x in baseline["grandfathered"]}
    owed_units = [(cid, t) for (cid, t) in uncovered if sdlc_md.norm_id(cid) not in forgiven]
    # The split the ledger could not make: a unit fixed DURING a close is not a unit nobody
    # accounted for. Both stay in `owed` - nothing is forgiven here - but they are named
    # separately, because an advisory that reports a run which did account for itself is one
    # people learn to step over.
    repairs, unaccounted = close_time_repairs(root, owed_units)
    # An override is per unit and reasoned. Recorded ones are split out so the exception is
    # COUNTABLE rather than routine - CR0527 asks for visible, not for forgiven, and an
    # exception nobody can count is indistinguishable from the inline repair the rule forbids.
    overrides = close_repair_overrides(root)
    overridden = [(cid, t) for cid, t in repairs if sdlc_md.norm_id(cid) in overrides]
    repairs = [(cid, t) for cid, t in repairs if sdlc_md.norm_id(cid) not in overrides]
    vel = velocity_owed(root, str(baseline.get("stamped") or ""))
    return {"baselined": True, "corrupt": False, "owed": sorted(owed_units),
            "close_time_repairs": repairs, "unaccounted": unaccounted,
            "close_repair_overrides": sorted(
                (cid, t, overrides[sdlc_md.norm_id(cid)]) for cid, t in overridden),
            "grandfathered": len(uncovered) - len(owed_units),
            "covered": len(covered), "terminal": len(terminal),
            "dead_breakdown_ids": dead_ids, "unreadable": degraded,
            # The close's OTHER half: a retro whose accuracy and velocity write never ran.
            "velocity_owed": vel["owed"], "velocity_overrides": vel["overrides"],
            "velocity_undated": vel["undated"]}


def _no_velocity_demand() -> dict:
    """The velocity fields on a report that cannot make the demand (unbaselined, or corrupt).
    Present and empty rather than absent: a consumer that has to test for the key would read a
    missing one as 'nothing owed' on exactly the reports that can judge nothing at all."""
    return {"velocity_owed": [], "velocity_overrides": [], "velocity_undated": []}


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


def blocking(report: dict) -> dict:
    """The ONE answer the headline and the exit code are both derived from.

    `owed` is every uncovered terminal unit, including the ones a close-time repair or a
    recorded override fully accounts for. The exit code has always been computed from
    `unaccounted` instead - correctly - while the headline was computed from `owed`. Two
    readers of one question, so on a fully-overridden set the first line announced a debt and
    named the command to discharge it, and the process exited 0. A gate reading the
    exit code was right; every human and agent reading the headline was told the opposite.

    Derived here rather than restated at each site, so the two cannot drift apart again
    (LL0042). `unaccounted` is defaulted from `owed` for the unbaselined and corrupt reports,
    which do not carry the split.
    """
    return {"units": report.get("unaccounted", report.get("owed") or []),
            "velocity": report.get("velocity_owed") or [],
            "corrupt": bool(report.get("corrupt"))}


def is_owed(report: dict) -> bool:
    """True when something genuinely holds the close. The exit code IS this predicate."""
    block = blocking(report)
    return bool(block["corrupt"]
                or (report.get("baselined") and (block["units"] or block["velocity"])))


def render(report: dict) -> str:
    n = len(report["owed"])
    # What actually holds the close, as opposed to what merely reached terminal. Every branch
    # below that makes a CLAIM reads this; the listing lines still read `owed`, because naming
    # the accounted-for units is the point of reporting them.
    n_block = len(blocking(report)["units"])
    if report.get("corrupt"):
        return (f"close owed: BASELINE CORRUPT - {report.get('error', BASELINE_FILE)}. "
                f"The close-down cannot be judged and is BLOCKED until the file is repaired "
                f"(restore it from git, or fix the JSON). Do NOT run `close_owed baseline`: "
                f"re-stamping would forgive the very units that owe a close.")
    if not report["baselined"]:
        head = (f"close owed: UNBASELINED - {n} uncovered terminal unit(s). "
                f"Run `close_owed baseline` to grandfather the existing tail, "
                f"then only later work can owe a close.")
    elif n_block == 0 and report.get("velocity_owed"):
        # The unit half is clean and the close is still unfinished. Saying "none" here and
        # listing the missing rows two lines below would be one report contradicting itself.
        head = (f"close owed: {len(report['velocity_owed'])} retro(s) closed without their "
                f"velocity row - the delivery units are all accounted for, the accuracy write "
                f"is not.")
    elif n_block == 0 and n:
        # Terminal since the baseline, and every one of them accounted for by a close-time
        # repair or a recorded override. Nothing is owed, so nothing here may say a close is -
        # and no discharge command is named, because there is no ledger left to discharge and
        # running a retro over a batch that does not exist is work that cannot honestly be done.
        # The units are still named below: visible and countable is the whole point of an
        # override, and silence would be indistinguishable from the inline repair the rule
        # forbids.
        head = (f"close owed: none. {n} unit(s) reached terminal since the baseline and every "
                f"one is accounted for - named below with the reason each carries. "
                f"{report['covered']} unit(s) accounted for by retros; "
                f"{report['grandfathered']} grandfathered.")
    elif n_block == 0:
        head = (f"close owed: none. {report['covered']} unit(s) accounted for by retros; "
                f"{report['grandfathered']} grandfathered.")
    else:
        head = (f"close owed: {n_block} delivery unit(s) reached terminal since the baseline "
                f"with no retro accounting for them - a sprint close is owed "
                f"(run the retro, then `gate --require-retro RETROxxxx`).")
    lines = [head]
    # The two states named apart. "Fixed after the account was written" and "nobody accounted
    # for this" are different facts, and a ledger that reports a run which DID account for
    # itself is one people learn to step over. Only printed when the split found something, so
    # an ordinary owed close reads exactly as before.
    if repairs := report.get("close_time_repairs") or []:
        lines.append(f"  {len(repairs)} of these is a CLOSE-TIME REPAIR - terminal after the "
                     f"retro was written, so the account it postdates could not name it: "
                     + ", ".join(cid for cid, _ in repairs))
        lines.append("    Amend that retro's Batch, or - if the repair genuinely could not "
                     "wait - record `> **Close-repair-override:** <UNIT> - <why>` in the retro. "
                     "The rule is that a finding surfaced during a close is FILED and deferred.")
    # Counted and NAMED, with the reason. An override nobody sees is indistinguishable from the
    # inline repair the rule forbids, so it is reported on every run rather than filed away.
    if ov := report.get("close_repair_overrides") or []:
        lines.append(f"  {len(ov)} close-time repair(s) carry a recorded override:")
        lines += [f"    {cid} ({t}) - {why}" for cid, t, why in ov]
    if n and (not report["baselined"] or n <= 40):
        lines.append("  " + ", ".join(f"{cid} ({t})" for cid, t in report["owed"]))
    elif n:
        shown = report["owed"][:40]
        lines.append("  " + ", ".join(f"{cid} ({t})" for cid, t in shown) + f", +{n - 40} more")
    vel = report.get("velocity_owed") or []
    if vel:
        lines.append(f"  {len(vel)} retro(s) closed with no row in {VELOCITY_FILE} - the "
                     f"accuracy and velocity write did not run, so the tokens-per-point rate "
                     f"the plans quote has never been measured against them. Record it: "
                     f"`retro.py accuracy --id RETROxxxx --write` (a sprint whose cost is not "
                     f"recoverable still writes a row, with a blank Actual and the reason):")
        lines.append("  " + ", ".join(f"{rid} ({date})" for rid, date in vel[:20])
                     + (f", +{len(vel) - 20} more" if len(vel) > 20 else ""))
    for rid, why in report.get("velocity_overrides") or []:
        lines.append(f"  velocity override: {rid} records no row on purpose - {why}")
    undated = report.get("velocity_undated") or []
    if undated:
        lines.append(f"  advisory: {len(undated)} retro(s) with no row carry no Date either, so "
                     f"the baseline cannot place them and no row is demanded of them: "
                     f"{', '.join(undated[:20])}")
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
    # Non-zero when a close is genuinely owed (baselined AND unaccounted units exist, or a retro
    # closed without its velocity row) OR when the baseline is corrupt - so a gate or hook can
    # branch on the exit code. An unbaselined project is a soft state (exit 0); a corrupt
    # baseline is a loud blocking failure, never a silent pass.
    #
    # A CLOSE-TIME REPAIR is reported and does not hold the exit code. CR0527 asks for it to be
    # visible and countable, which the report above does; gating on it would re-create the
    # unconvergeable close from the other side - the ceremony would refuse precisely because the
    # close had done its job carefully. What holds the gate is work nobody accounted for.
    # `is_owed` is the shared predicate `render` composes its headline from, so the line the
    # reader sees and the code a gate branches on cannot disagree.
    return 1 if is_owed(report) else 0


def cmd_baseline(args: argparse.Namespace) -> int:
    import file_finding  # noqa: PLC0415 - the shared prose-fields loader, as elsewhere
    try:
        fields = file_finding.resolve_prose_fields(
            getattr(args, "fields_file", None), {"note": args.note}, allowed=("note",))
    except ValueError as exc:
        print(f"baseline refused: {exc}", file=sys.stderr)
        return 2
    data = stamp_baseline(Path(args.root), date=args.date, note=fields.get("note"))
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
    b.add_argument("--fields-file", dest="fields_file", metavar="FIELDS.json",
                   help="read the baseline note from a JSON object ({\"note\": \"...\"}) instead "
                        "of --note, so prose carrying shell metacharacters is stored verbatim "
                        "rather than interpreted by the shell")
    b.set_defaults(func=cmd_baseline)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Resolve the root ONCE and write it back, so every verb below anchors on the tree the
    # run belongs to. The family default `.` means "work it out from here", not "the cwd
    # is the project": otherwise a run from a subdirectory acts on a stray tree and exits 0.
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
