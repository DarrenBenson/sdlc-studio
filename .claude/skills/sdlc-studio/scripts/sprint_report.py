#!/usr/bin/env python3
"""The sprint report: what a sprint delivered, what it cost, and whether the estimate held.

Almost all of it is COMPOSITION, not new measurement - the retro holds Delivered, the lessons and
the tickets raised; `retro.accuracy` holds the honest estimate-vs-actual and the velocity;
`telemetry` holds model, tokens and per-attempt cost. This module reads those and lays them out as
one end-of-sprint page. Built as a deterministic SCRIPT, so it costs no model tokens - only an agent
writing narrative prose would.

Two honesty rules it will not bend:

  ACTUAL SPEND is a MEASUREMENT: tokens x the configured/estimated model rate, summed over every
  ATTEMPT (rework included), priced offline from the repo's `pricing.*` config. A model with no
  price is UNPRICED - its tokens are still counted, its dollars are not; the report never invents a
  number. No avoided-cost / savings headline: "the cheap model saved X" asks what a model that never
  ran would have cost, which is a model, not a measurement, and this project has been burned by
  exactly that confusion. If a saving is ever shown it is a labelled estimate against a named
  baseline, never summed into a total beside a measured figure.

  RENDERING is switchable (`report.enabled: false` for a token-conscious project); RECORDING is NOT.
  The switch controls only whether the TEXT PAGE is drawn - json data remains available under it
  (`show --format json` returns the composed report either way), and telemetry keeps recording
  regardless, because a report not generated can be generated later, but a measurement not taken
  is gone forever (and turning telemetry off is how the estimator became unfalsifiable the last
  time).
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import run_state, sdlc_md  # noqa: E402
import retro  # noqa: E402


def _flow_summary(root: Path) -> dict | None:
    """The schedule axis beside the cost axis: median cycle time and weekly throughput
    from flow.compute. None (line omitted) when nothing is measurable or flow errors -
    the report never fails on its garnish."""
    try:
        import flow
        rep = flow.compute(root)
        cycles = sorted(u["cycle_days"] for u in rep["units"].values() if "cycle_days" in u)
        w = rep["throughput"]["window"]
        if not cycles or not w:
            return None
        return {"median_cycle_days": round(flow._median(cycles), 1), "weeks": w["weeks"],
                "per_week": round(sum(rep["throughput"]["weekly"].values()) / max(1, w["weeks"]), 1)}
    except Exception as exc:  # noqa: BLE001 - advisory garnish, never breaks the report
        print(f"note: flow summary unavailable ({type(exc).__name__}: {exc})", file=sys.stderr)
        return None


#: How many previous runs the trailing history shows. Enough to read a trend from; short enough
#: that the page stays a page.
MUTATION_HISTORY = 4


def _mutation_row(mut, root: Path, row: dict) -> dict:
    """One series row rendered as cost BESIDE yield.

    Cost is the run's wall-clock. Yield is the artefacts filed against it, never its survivor
    count: a survivor is a hypothesis, and RUN-01KY03GS raised three of which two became bugs -
    counting survivors would have overstated that run by half. `cost_per_finding_s` is derived
    ONLY when both halves are present; otherwise it is None and the note says why, because a
    blank there reads as free and a zero divisor is not an answer."""
    y = mut.run_yield(root, row.get("run_id"))
    elapsed = row.get("elapsed_s")
    filed = y.get("filed") or []
    cost, note = None, None
    if not row.get("evidence"):
        note = "no evidence, so nothing to divide"
    elif not elapsed:
        note = "the run recorded no wall-clock"
    elif not filed:
        note = "nothing was filed from this run, so it has no cost per finding (not a free run)"
    else:
        cost = round(float(elapsed) / len(filed), 1)
    return {"run_id": row.get("run_id"), "at": row.get("at"), "elapsed_s": elapsed,
            "tree": row.get("tree") or {},
            "applied": row.get("applied"), "killed": row.get("killed"),
            "survived": row.get("survived"), "evidence": bool(row.get("evidence")),
            "outcome": row.get("outcome"),
            "no_evidence_reason": row.get("no_evidence_reason"),
            "filed": filed, "yield": len(filed),
            "equivalent": len(y.get("equivalent") or []),
            "cost_per_finding_s": cost, "cost_per_finding_note": note}


def _run_record(root: Path, unit_ids: list[str]) -> dict | None:
    """The run record that delivered THIS sprint, or None.

    The selection rule lives here, ONCE, and both readers share it: `_run_window` wants the
    span, the overhead ratio wants the record's own review rounds and idle gaps, and a second
    copy of "which run was this sprint's" would drift into a second answer. See `_run_window`
    for why closeness rather than overlap decides it.

    Same guard as `_sprint_goal`: a run record counts only when its batch names this sprint's
    units. Where more than one does, the CLOSEST record wins - most of this sprint's units
    covered, then fewest units that are not this sprint's - live or archived alike. Overlap
    alone was not enough: a superset batch ties an exact one, so a foreign run touching every
    unit of this sprint took the window. Trying the live record first regardless was the same defect one level up: a run that
    merely RE-TOUCHES one unit of an old sprint supplied that sprint's window, and an open run
    has no end, so every later project-wide row read as this sprint's again. Ties keep the live
    record, then the newest archived one, because a report is normally read after the close and
    the close archives the run it describes. `ended_at` may be None - an open run has a start
    and no end, and a row after its start still belongs to it."""
    want = {sdlc_md.norm_id(u) for u in unit_ids}
    records = []
    try:
        live = run_state.read(root) or {}
        if live:
            records.append(live)
    except run_state.RunStateError:
        pass                      # the report stays renderable; the close gate owns that failure
    # `archived` skips an unreadable record rather than raising, so there is nothing to catch.
    records.extend(reversed(run_state.archived(root)))
    best = None                   # ((cover, -extraneous), state)
    for state in records:
        batch = {sdlc_md.norm_id(u) for u in (state.get("batch") or [])}
        cover = len(batch & want)
        if not cover:
            continue
        start = telemetry._parse_iso(state.get("started_at"))  # noqa: SLF001 - ONE stamp reader
        if start is None:
            continue              # a run with no start bounds nothing
        # SCORE BY CLOSENESS, NOT OVERLAP. `cover` alone is bounded above by len(want), so ANY
        # run whose batch is a SUPERSET of this sprint's units ties the run that actually
        # delivered them - and with live tried first, an open run touching all of them took the
        # window, which is the defect one round earlier. Worst for a one-unit sprint, where any
        # run touching that unit ties. Breaking the tie on FEWEST extraneous units makes an
        # exact batch beat a superset, and leaves the live-first rule to decide only a genuine
        # tie on both terms.
        score = (cover, -len(batch - want))
        if best is None or score > best[0]:
            best = (score, state)
    return best[1] if best else None


def _run_window(root: Path, unit_ids: list[str]) -> tuple | None:
    """`(started_at, ended_at)` of the run that delivered THIS sprint, or None.

    Derived from `_run_record`, whose docstring holds the selection rule. `ended_at` may be
    None - an open run has a start and no end, and a row after its start still belongs to it.
    """
    state = _run_record(root, unit_ids)
    if state is None:
        return None
    return (telemetry._parse_iso(state.get("started_at")),        # noqa: SLF001 - ONE stamp reader
            telemetry._parse_iso(state.get("ended_at")))          # noqa: SLF001


#: Said when no run record can be joined to this sprint. The series is project-wide, so without
#: a window every row in it belongs to SOME run and none of them provably to this one.
NO_ATTRIBUTION = ("no run state names this sprint's units, so no mutation run can be attributed "
                  "to it")


def _mutation_summary(root: Path, unit_ids: list[str]) -> dict:
    """The mutation gate's cost against its yield, for THIS run and the ones before it.

    The series is PROJECT-WIDE, so the newest row in it is whatever the project last proved -
    not what this sprint proved. It is joined to the run being reported by the run's own
    measured window, and a row outside that window is never this sprint's: a sprint that ran no
    mutation was republishing the previous sprint's cost and yield as its own, unlabelled,
    while the rows beneath it were correctly prefixed `previous run`.

    `current` is None when this run has no row of its own - the step was skipped, refused
    before it could write, or never run. That is NOT a run of zero survivors, and the renderer
    says so rather than printing counts of zero, which would read as a gate that looked and
    found nothing.

    An UNSTAMPED row is a further case and is counted, not folded into those three: it exists and
    carries counts, so saying the step was skipped or killed would be false. It cannot be
    placed in or out of the window either, so it is named and left unattributed."""
    try:
        import mutation
        rows = mutation.series_rows(root)
    except Exception as exc:  # noqa: BLE001 - the report never fails on its evidence being absent
        print(f"note: mutation series unavailable ({type(exc).__name__}: {exc})", file=sys.stderr)
        return {"current": None, "trailing": [], "attribution": None, "unstamped": 0}
    if not rows:
        return {"current": None, "trailing": [], "attribution": None, "unstamped": 0}
    window = _run_window(root, unit_ids)
    if window is None:
        # Nothing can be claimed as this sprint's. The rows are still SHOWN, as the previous
        # runs they are, and the reason no `current` was picked is said out loud.
        return {"current": None, "attribution": NO_ATTRIBUTION, "unstamped": 0,
                "trailing": [_mutation_row(mutation, root, r)
                             for r in reversed(rows[-MUTATION_HISTORY:])]}
    start, end = window
    mine, before = [], []
    unstamped = 0
    for r in rows:
        at = telemetry._parse_iso(r.get("at"))  # noqa: SLF001 - ONE stamp reader
        if at is None:
            unstamped += 1        # an unstamped row cannot be placed in or out of the window
            continue
        if at < start:
            before.append(r)
        elif end is None or at <= end:
            mine.append(r)
        # a row AFTER this run closed belongs to a LATER sprint and is not this report's
    # The trailing history is every EARLIER mutation run, whether it ran inside this sprint (a
    # second pass over the same diff) or in one before it. Both are prior runs of the gate,
    # which is the trend the history exists to show; only `current` is a claim about ownership.
    trailing = (before + mine[:-1]) if mine else before
    # With no row of this run's own, an unstamped row is the REASON, and it is not the same
    # reason as a step that never ran. Said here so the renderer never asserts a skip.
    attribution = None
    if not mine and unstamped:
        attribution = (f"{unstamped} series row(s) carry no timestamp, so they cannot be placed "
                       f"in or out of this run's window")
    return {"current": _mutation_row(mutation, root, mine[-1]) if mine else None,
            "attribution": attribution, "unstamped": unstamped,
            "trailing": [_mutation_row(mutation, root, r)
                         for r in reversed(trailing[-MUTATION_HISTORY:])]}


def _sprint_goal(root: Path, unit_ids: list[str]) -> tuple[str | None, dict | None]:
    """The run state's Sprint Goal + verdict - ONLY when its batch names this sprint's
    units. A run state from a different run says nothing about this report (the same
    stale-confounder guard the elapsed read learned the hard way)."""
    try:
        state = run_state.read(root) or {}
    except run_state.RunStateError:
        return None, None  # the report stays renderable; the close gate owns that failure
    if not state.get("sprint_goal"):
        return None, None
    batch = {sdlc_md.norm_id(u) for u in (state.get("batch") or [])}
    if not batch & {sdlc_md.norm_id(u) for u in unit_ids}:
        return None, None
    return state["sprint_goal"], state.get("sprint_goal_verdict")
import telemetry  # noqa: E402


def _spend(root: Path, unit_ids: list[str]) -> dict:
    """True spend over the batch, summed per ATTEMPT so rework is counted. Returns
    `{tokens, cost, unpriced, priced_units, models}`. `unpriced` names any model no price covered
    (its tokens are still in the token total), so the dollar figure never silently drops spend."""
    actuals = telemetry.latest_actuals(telemetry.read_all(root))
    want = {sdlc_md.norm_id(u) for u in unit_ids}
    tokens, cost, unpriced, measured_units, models = 0, 0.0, [], 0, []
    for uid, rec in actuals.items():
        if sdlc_md.norm_id(uid) not in want:
            continue
        c = telemetry.unit_cost(root, rec)
        if c["tokens"] <= 0:
            continue   # a record with no TOKEN telemetry (interactive) is not a measured spend
        tokens += c["tokens"]
        cost += c["cost"]
        measured_units += 1
        for m in c["unpriced"]:
            if m not in unpriced:
                unpriced.append(m)
        for a in telemetry.attempts_of(rec):
            if a.get("model") and a["model"] not in models:
                models.append(a["model"])
    return {"tokens": tokens, "cost": round(cost, 4), "unpriced": unpriced,
            "measured_units": measured_units, "models": sorted(models)}


def report(root: Path, retro_id: str, *, sprint_tokens: int | None = None,
           elapsed_hours: float | None = None) -> dict:
    """Compose the sprint report from the retro, the accuracy pass, and telemetry. Read-only."""
    acc = retro.accuracy(root, retro_id, sprint_tokens=sprint_tokens, elapsed_hours=elapsed_hours)
    if not acc.get("ok"):
        return {"ok": False, "id": retro_id, "errors": acc.get("errors") or ["retro not found"]}
    unit_ids = [u["id"] for u in acc["units"]]
    val = retro.validate(root, retro_id)  # lessons + dispositioned findings (tickets raised)
    b = acc["batch"]
    goal, goal_verdict = _sprint_goal(Path(root), unit_ids)
    # Composed ONCE and read twice - the overhead block reads the execution and mutation
    # summaries rather than re-deriving them, so the close cannot report one cost here and a
    # different one three lines down.
    mut = _mutation_summary(Path(root), unit_ids)
    execution = _execution_actuals(Path(root), unit_ids)
    overhead = overhead_split(Path(root), unit_ids, execution=execution, mutation=mut)
    out = {
        "ok": True, "id": retro_id, "date": acc.get("date", ""),
        "sprint_goal": goal, "sprint_goal_verdict": goal_verdict,
        "flow": _flow_summary(Path(root)),
        "mutation": mut,
        "execution": execution,
        "overhead": overhead,
        "units": unit_ids,
        "seams": _seam_coverage(Path(root), unit_ids),
        "proof": _proof_coverage(Path(root), unit_ids),
        "delivered_points": b.get("delivered_points"),
        "delegated_signoffs": _delegated_rows(root),
        "spend": _spend(root, unit_ids),
        "sprint_actual_tokens": b.get("sprint_actual_tokens"),
        "velocity": {
            "points_per_elapsed_hour": b.get("points_per_elapsed_hour"),
            "elapsed_hours": b.get("sprint_elapsed_hours"),
            "elapsed_source": b.get("elapsed_source"),
            "points_per_worker_hour": b.get("points_per_worker_hour"),
            "tokens_per_point": b.get("tokens_per_point"),
            "sprint_tokens_per_point": b.get("sprint_tokens_per_point"),
            # The overhead ratio belongs WITH the velocity figures, not in a block of its own:
            # it is the same question (what an hour of this loop buys) and a reader of the
            # velocity record must meet it without knowing to look. Read off the one composed
            # block above, never recomputed, so the two readings cannot disagree.
            "overhead_ratio": overhead["ratio"],
            "overhead_bound": overhead["bound"],
            "overhead_excludes": overhead["unmeasured"],
        },
        "accuracy": {"ratio": b.get("ratio"), "refused": b.get("refused"),
                     "n_measured": acc.get("n_measured"), "models": acc.get("models")},
        "lessons": [ln if isinstance(ln, str) else (ln.get("title") or ln.get("gist") or "")
                    for ln in val.get("lessons", [])],
        "waivers": _waiver_kinds(root),
        "tickets": val.get("filed", []),
        "declined": val.get("declined", []),
    }
    # The compulsory checklist, composed from the same `out` rather than a second pass: a
    # checklist that re-derived the delivered points could disagree with the line above it,
    # and a close cannot be certified by a page that contradicts itself.
    out["checklist"] = checklist(root, retro_id, unit_ids=unit_ids, rep=out)
    return out


def _waiver_kinds(root: Path) -> dict:
    """How many waivers were CHOSEN against how many were forced, kept apart.

    A waiver whose window had already closed when the item fired is a process failure; one
    taken on purpose is a decision. Summing them reports a sprint as having made N decisions
    when some of them were made for it by the clock, and only one of those is worth repeating.

    Unreadable is not empty: an unresolvable log returns None so the renderer can say it could
    not look, rather than printing zeroes that read as nothing to report.
    """
    try:
        import decisions  # noqa: PLC0415 - deferred sibling, as elsewhere in this module
        return decisions.waiver_kind_counts(root)
    except Exception as exc:  # noqa: BLE001 - a report must not die on a log read
        sdlc_md.debug("sprint_report._waiver_kinds", exc)
        return None


def _waiver_lines(rep: dict) -> list[str]:
    counts = rep.get("waivers")
    if counts is None:
        return ["WAIVERS: the decision log could not be read - not zero, unread"]
    if not any(counts.values()):
        return []
    parts = [f"{counts.get('deliberate', 0)} deliberate",
             f"{counts.get('expired', 0)} expired before anyone was asked"]
    if counts.get("unkinded"):
        parts.append(f"{counts['unkinded']} recorded before kinds existed")
    return [f"WAIVERS: {', '.join(parts)}"]


def _spend_line(sp: dict, sprint_tokens: int | None) -> str:
    if not sp["measured_units"]:
        supplied = (f" Sprint total supplied: {sprint_tokens:,} tokens (harness-tracked)."
                    if sprint_tokens else "")
        return ("Cost: no per-unit token telemetry for this batch (interactive sprint)." + supplied
                + " Supply the sprint total with `--tokens N` for a token figure.")
    dollars = f"~${sp['cost']:,.2f} at configured/estimated rates" if sp["cost"] else "no priced models"
    unpriced = (f"; {len(sp['unpriced'])} unpriced model(s) counted in tokens but not dollars: "
                f"{', '.join(sp['unpriced'])}" if sp["unpriced"] else "")
    return (f"Cost (rework included): {sp['tokens']:,} tokens over {sp['measured_units']} unit(s), "
            f"{dollars}{unpriced}. Set `pricing.<model>` in .config.yaml for your contract rate.")


def _mutation_lines(m: dict | None) -> list[str]:
    """The mutation gate's trade, in one place: what it cost against what it produced.

    A gate that cannot show its yield gets cut on a bad day and kept on a good one, so this is
    rendered at the close, where the decision is actually taken. A run with no evidence is NAMED
    - never rendered as a tidy row of zeros, which reads as a gate that looked and found
    nothing rather than one that never looked - and never handed a PREVIOUS run's numbers to
    stand in for the ones it does not have. The trailing history renders either way: those runs
    are the same facts whether or not this sprint proved anything of its own."""
    trailing: list[str] = []
    for prev in (m or {}).get("trailing") or []:
        if not prev["evidence"]:
            trailing.append(f"  previous run {prev['run_id']}: {prev['elapsed_s']}s, no "
                            f"evidence ({prev['no_evidence_reason']}).")
            continue
        pper = (f", {prev['cost_per_finding_s']}s per finding" if prev["cost_per_finding_s"]
                else f", {prev['cost_per_finding_note']}")
        trailing.append(f"  previous run {prev['run_id']}: {prev['elapsed_s']}s, "
                        f"{prev['survived']} survived, yield {prev['yield']}{pper}.")
    if (m or {}).get("unstamped") and (m or {}).get("current"):
        # Named rather than dropped in silence. With no `current` the same fact is the
        # attribution below, so it is said once either way.
        trailing.append(f"  {m['unstamped']} series row(s) carry no timestamp, so they could "
                        f"not be placed in this run's window.")
    if not m or not m.get("current"):
        why = (m or {}).get("attribution")
        return [(f"Mutation gate: no mutation evidence recorded for this run - {why}." if why
                 else "Mutation gate: no mutation evidence recorded for this run (the step was "
                      "skipped, or was killed before it could record anything) - not a run "
                      "that found nothing."), *trailing]
    cur = m["current"]
    if not cur["evidence"]:
        return [f"Mutation gate: no mutation evidence recorded for this run - "
                f"{cur['no_evidence_reason']} ({cur['elapsed_s']}s spent). "
                f"Not a run that found nothing.", *trailing]
    filed = ", ".join(cur["filed"]) if cur["filed"] else "nothing filed"
    per = (f" - {cur['cost_per_finding_s']}s per finding" if cur["cost_per_finding_s"]
           else f" - {cur['cost_per_finding_note']}")
    equiv = f", {cur['equivalent']} equivalent (excluded)" if cur["equivalent"] else ""
    # The tree the counts were measured in, BESIDE them. A survivor measured in a tree another
    # reviewer was cleaning up in is not the same evidence as one measured in a checkout of its
    # own, and the close is exactly where that difference has to be legible: this is the page
    # the reviewer of record signs off from. Silent for a confirmed isolated tree.
    tree = cur.get("tree") or {}
    qualifier = ""
    if tree.get("isolated") is False:
        qualifier = f" MEASURED IN A SHARED TREE: {tree.get('why', '')}"
    elif tree.get("isolated") is None:
        why = tree.get("why") or "no isolation evidence was recorded for this run"
        qualifier = f" TREE UNESTABLISHED: {why}"
    return [f"Mutation gate: {cur['elapsed_s']}s, {cur['applied']} applied, "
            f"{cur['killed']} killed, {cur['survived']} survived{equiv}; "
            f"yield {cur['yield']} filed artefact(s) ({filed}){per}.{qualifier}", *trailing]


#: The ONE mode that ran nothing. Everything else ran something and its seconds count.
#:
#: STATED AS AN EXCLUSION, not as a list of what counts. It was `("full", "selected", "none")`,
#: and US0639 then added a fifth mode - `preflight` - to the ledger without this reader learning
#: of it. Six preflight rows carrying 623.2 measured seconds were reported as "6 execution
#: event(s) ... none carries a duration", while `sprint.close_cost` read the same six rows and
#: reported 623.2s. Two readers of one ledger disagreeing, and the report's sentence was false
#: about the bytes on disk. Worse than silent: `_overhead_ratio` derives delivery by SUBTRACTION,
#: so 600s of measured, attributed gate time was credited to delivery.
#:
#: LL0043 - an enumeration of a rule is a lower bound, not a boundary. An allow-list must be
#: extended by whoever adds a mode; an exclusion is right by default, and the direction it fails
#: in is counting a new mode's real seconds rather than discarding them.
#:
#: `reuse` is excluded because it ran nothing: folding it into the run count would report a
#: saving as a cost, and it is still counted separately so a reader can see a decision was taken.
_REUSE_MODE = "reuse"

#: The ONE spelling of "this was not measured". Declared rather than repeated at each site: an
#: independent seat mutated one of four open-coded copies to `0` and the whole module stayed
#: green, and a zero in a cost column reads as a sprint that cost nothing rather than as one
#: nobody metered. A component added later cannot invent a second spelling by accident.
UNMEASURED = "UNMEASURED"

#: How each cost component reads on the operator's page. A component with no entry still prints,
#: as `<key> <value>` - the renderer must never be the reason a measured figure goes unseen.
_COST_PHRASE = {
    "tokens": lambda v: f"{v} tokens",
    "delivered_points": lambda v: f"over {v} points",
    "elapsed_hours": lambda v: f"{v} elapsed hours",
    "overhead_ratio": lambda v: f"overhead {v}",
}


def _execution_actuals(root: Path, unit_ids: list[str]) -> dict:
    """What test execution actually cost this sprint, beside what the policy declared.

    The ledger is PROJECT-WIDE, so it is joined to this sprint by the run's own measured
    window - the same confounder `_mutation_summary` had to learn, and for the same reason: a
    sprint that ran nothing would otherwise republish the previous sprint's cost as its own.

    `measured` is False whenever nothing can be attributed, and `seconds` is then None. Never
    0: a total of zero reads as a sprint that tested for free, which is precisely the reading
    that let 218 minutes of re-running go unremarked in a retro that said the sprint went well.
    """
    empty = {"measured": False, "full_runs": 0, "selected_runs": 0, "reused_runs": 0,
             "seconds": None, "declared": _declared_policy(root), "runs": 0}
    try:
        import sprint  # noqa: PLC0415 - deferred; the report never pays for the plan graph
        rows = sprint.read_execution_ledger(root)
    except Exception as exc:  # noqa: BLE001 - the report never fails on its evidence
        print(f"note: test-execution ledger unavailable ({type(exc).__name__}: {exc})",
              file=sys.stderr)
        return {**empty, "why": f"the test-execution ledger could not be read ({exc}), so what "
                                f"the suites cost is UNKNOWN, not zero"}
    window = _run_window(Path(root), unit_ids)
    if window is None:
        return {**empty, "why": ("no run state names this sprint's units, so no test-execution "
                                 "row can be attributed to it - the cost is UNKNOWN, not zero")}
    start, end = window
    mine = []
    for r in rows:
        at = telemetry._parse_iso(r.get("at"))  # noqa: SLF001 - ONE stamp reader
        if at is None or at < start:
            continue
        if end is None or at <= end:
            mine.append(r)
    if not mine:
        return {**empty, "why": "no test execution was recorded inside this run's window, so "
                                "what the suites cost is NOT CAPTURED - which is not the same "
                                "as a sprint that ran none, and is not zero"}
    counted = [r for r in mine if str(r.get("mode")) != _REUSE_MODE]
    seconds = [float(r["seconds"]) for r in counted
               if isinstance(r.get("seconds"), (int, float))]
    # DERIVED from the ledger, not enumerated over the modes this file happens to know. The
    # first repair inverted the `seconds` rule to an exclusion and left the three counts beside
    # it as an allow-list, so a preflight-only ledger rendered `0 full run(s), 0 selected - 623s
    # of test time` - a sentence contradicting itself, with the LL0043 note three lines above.
    # An independent seat found that: the lesson had been written down and then not applied to
    # the code beside the one it was written about. `by_mode` names whatever ran, so a mode
    # added later appears in the sentence without anyone remembering to add it.
    by_mode: dict[str, int] = {}
    for r in mine:
        key = str(r.get("mode") or "unrecorded")
        by_mode[key] = by_mode.get(key, 0) + 1
    return {
        "measured": bool(seconds),
        "runs": len(mine),
        "by_mode": by_mode,
        # Derived views of `by_mode`, kept for compatibility with any consuming project reading
        # this dict by field name. A seat checked and there is no non-test reader in this repo,
        # so do not read these as evidence of demand - they are no longer the source of the
        # rendered sentence, which is the property that matters.
        "full_runs": by_mode.get("full", 0),
        "selected_runs": by_mode.get("selected", 0),
        "reused_runs": by_mode.get(_REUSE_MODE, 0),
        "seconds": round(sum(seconds), 1) if seconds else None,
        "declared": _declared_policy(root),
        "why": ("" if seconds else
                f"{len(mine)} execution event(s) are recorded for this run but none carries a "
                f"duration, so the cost is NOT CAPTURED - not zero"),
    }


def _declared_policy(root: Path) -> dict | None:
    """The execution policy the PLAN recorded, or None when it recorded none.

    Read back rather than re-derived: the actuals are judged against what was agreed at plan
    time, never against a config that may have moved since.
    """
    try:
        import sprint  # noqa: PLC0415
        strat = sprint.recorded_test_strategy(root) or {}
    except Exception as exc:  # noqa: BLE001 - the report never fails on a plan read
        sdlc_md.debug("sprint_report._declared_policy", exc)
        return None
    declared = (strat.get("execution") or {}).get("declared")
    return declared if isinstance(declared, dict) and declared else None


def _execution_lines(rep: dict) -> list[str]:
    """The execution block. A sprint that ran the suite fifty times shows it here, beside the
    policy that was supposed to govern how often it would."""
    act = rep.get("execution")
    if not act:
        return []
    declared = act.get("declared")
    against = (" Declared policy: "
               + "; ".join(f"{k.replace('_', ' ')} {str(v).upper()}"
                           for k, v in declared.items()) + "."
               if declared else
               " The plan recorded NO execution policy, so there is nothing to judge these "
               "against.")
    if not act.get("measured"):
        return [f"Test execution: NOT CAPTURED - {act.get('why')}.{against}"]
    # Every row on the ledger is named, so the counts in this sentence sum to `runs` and cannot
    # sit beside a duration they do not account for. `reuse` is annotated rather than dropped:
    # it ran nothing, and a reader has to be able to see that a decision was taken.
    by_mode = act.get("by_mode") or {}
    parts = [f"{n} {mode}" + (" (ran nothing)" if mode == _REUSE_MODE else "")
             for mode, n in sorted(by_mode.items(), key=lambda kv: (-kv[1], kv[0]))]
    ran = ", ".join(parts) if parts else f"{act.get('runs', 0)} run(s)"
    return [f"Test execution: {ran} - {act['seconds']:,.0f}s of test time.{against}"]


# ---------------------------------------------------------------------------
# OVERHEAD AGAINST DELIVERY: the ratio that tests the product's own claim.
# ---------------------------------------------------------------------------
# The close already reports what a sprint delivered and what it cost in tokens. It did not
# report the number an operator actually decides on: how much of the run went on the process
# rather than on the work. On one run that ratio was about 9:1 - roughly 35 minutes of delivery
# against roughly 316 minutes of gate, review and re-running - and it surfaced only because the
# operator said it felt slow and it was then computed by hand.
#
# Two rules it will not bend, and they are the same two the rest of this file lives by:
#
#   EVERY COMPONENT IS READ BACK FROM A RECORD THE RUN WROTE - the test-execution ledger, the
#   mutation series, the review-round stamps, the run's own start and end. Nothing here is
#   estimated at close time. A figure invented at the close is a claim about a sprint, not a
#   measurement of one, and it would be indistinguishable from the hand-computed number this
#   exists to replace.
#
#   AN UNMEASURED COMPONENT READS UNMEASURED, NEVER ZERO, and the ratio names what it excludes.
#   A zero there reports overhead that was never measured as overhead that never happened,
#   which understates the ratio in the one direction that flatters the tool.


def _component_test_execution(ctx: dict) -> dict:
    """Gate time: the test-execution ledger, already joined to this run's window."""
    act = ctx.get("execution") or {}
    seconds = act.get("seconds")
    if act.get("measured") and isinstance(seconds, (int, float)):
        return {"seconds": float(seconds), "measured": True, "bound": "exact",
                "source": "the test-execution ledger", "why": ""}
    return {"seconds": None, "measured": False, "bound": None,
            "source": "the test-execution ledger",
            "why": act.get("why") or "no test-execution row is attributed to this run"}


def _component_mutation(ctx: dict) -> dict:
    """Gate time: the mutation run attributed to this sprint, wall-clock as the series recorded
    it. A refused run still spent its time, so its elapsed still counts as overhead."""
    mut = ctx.get("mutation") or {}
    elapsed = (mut.get("current") or {}).get("elapsed_s")
    if isinstance(elapsed, (int, float)):
        return {"seconds": float(elapsed), "measured": True, "bound": "exact",
                "source": "the mutation series", "why": ""}
    # The REASON is stated once, by the mutation block, and pointed at rather than repeated:
    # the same sentence written by two renderers is how a reader starts counting one fact twice.
    return {"seconds": None, "measured": False, "bound": None,
            "source": "the mutation series",
            "why": "no mutation run is attributed to this run (see the mutation gate line), so "
                   "what that gate cost is NOT CAPTURED, not zero"}


def _component_review(ctx: dict) -> dict:
    """Review and repair: the span the run's own review-round stamps cover.

    A LOWER BOUND, and labelled one. No round records a duration, so the span from the first
    recorded round to the last is the repair time BETWEEN rounds and nothing before the first;
    a run whose rounds were all stamped together at close covers seconds of a review that took
    hours. Fewer than two stamps, or a span of zero, measures nothing at all and says so -
    reporting either as 0s would publish a review that cost nothing.
    """
    state = ctx.get("state") or {}
    rounds = [r for r in (state.get(run_state.REVIEW_ROUNDS) or []) if isinstance(r, dict)]
    # A round that CARRIES a duration is measured directly, and a sum of durations is exact -
    # it counts the review itself, not merely the gaps between the stamps. The stamp-span
    # fallback below stays for rounds recorded before durations existed, and stays labelled a
    # lower bound. Mixed is still a lower bound: the untimed rounds contribute nothing, and
    # counting them as zero is what made review look free while it was the largest cost.
    durations = [d for d in (run_state.round_duration(r) for r in rounds) if d is not None]
    if durations:
        every = len(durations) == len(rounds)
        return {"seconds": float(sum(durations)), "measured": True,
                "bound": "exact" if every else "lower",
                "source": (f"{len(durations)} recorded round duration(s)"
                           + ("" if every else f" of {len(rounds)} round(s); the rest are "
                                               f"UNMEASURED and contribute nothing")),
                "why": ""}
    stamps = sorted(t for t in (telemetry._parse_iso(r.get("recorded_at"))  # noqa: SLF001
                                for r in rounds) if t is not None)
    source = "the recorded review-round stamps"
    if len(stamps) < 2:
        return {"seconds": None, "measured": False, "bound": None, "source": source,
                "why": f"{len(rounds)} review round(s) are recorded and no round carries a "
                       f"duration, so the review and repair time is NOT CAPTURED, not zero"}
    span = (stamps[-1] - stamps[0]).total_seconds()
    if span <= 0:
        return {"seconds": None, "measured": False, "bound": None, "source": source,
                "why": "every recorded round carries the same stamp (they were recorded "
                       "together), so their span measures nothing - not a review that was free"}
    return {"seconds": round(span, 1), "measured": True, "bound": "lower", "source": source,
            "why": "the span between the first and last recorded round, so it bounds the "
                   "review and repair time from below"}


#: The overhead components, defined ONCE as a table of extractors. The sum, the unmeasured
#: list and the rendered breakdown are all derived from this table by iteration, so a component
#: added here reaches all three readers - a hand-typed second list is how one of them silently
#: exempts the component it forgot.
_OVERHEAD_COMPONENTS = (
    ("test execution", _component_test_execution),
    ("mutation", _component_mutation),
    ("review and repair", _component_review),
)


def _overhead_ratio(root: Path, unit_ids: list[str], execution: dict, mutation: dict) -> dict:
    """Overhead time against delivery time for THIS run, from what the run recorded.

    Delivery is what the measured wall-clock has LEFT once the recorded overhead comes out of
    it - the run's own idle-deducted span, never a figure supplied at close. It is therefore an
    upper bound whenever a component is unmeasured, which makes the ratio a lower bound, and
    `bound` says so rather than letting the number read as exact.
    """
    state = _run_record(root, unit_ids)
    blank = {"measured": False, "ratio": None, "delivery_s": None, "overhead_s": None,
             "total_s": None, "components": [], "unmeasured": [], "bound": None}
    if state is None:
        return {**blank, "why": "no run state names this sprint's units, so how long it spent "
                                "on delivery and on overhead is UNKNOWN, not zero"}
    ctx = {"execution": execution, "mutation": mutation, "state": state}
    components = [{"name": name, **fn(ctx)} for name, fn in _OVERHEAD_COMPONENTS]
    measured = [c for c in components if c["measured"]]
    unmeasured = [c["name"] for c in components if not c["measured"]]
    overhead = round(sum(c["seconds"] for c in measured), 1) if measured else None
    span = telemetry.elapsed_excluding_idle(state.get("started_at"), state.get("ended_at"), state)
    total = None if span.get("hours") is None else round(span["hours"] * 3600.0, 1)
    # A ratio is a floor, not an equality, unless every component is measured AND exact. It
    # qualifies a RATIO, so it stays None while there is no ratio to qualify - a bound beside a
    # null figure reads as a claim about a number nobody has.
    bound = ("exact" if not unmeasured and all(c["bound"] == "exact" for c in measured)
             else "lower")
    base = {**blank, "components": components, "unmeasured": unmeasured,
            "overhead_s": overhead, "total_s": total}
    if total is None:
        return {**base, "why": "the run records no closed wall-clock span (it is still open, or "
                               "its stamps do not parse), so delivery time is UNKNOWN, not zero"}
    if overhead is None:
        return {**base, "why": "no overhead component was measured, so the split between "
                               "delivery and overhead is UNKNOWN, not zero"}
    if overhead >= total:
        return {**base, "why": f"the recorded overhead ({overhead:,.0f}s) meets or exceeds the "
                               f"run's measured wall-clock ({total:,.0f}s), so the components "
                               f"overlap or fell outside it and delivery time cannot be derived "
                               f"- it is UNKNOWN, not zero"}
    delivery = round(total - overhead, 1)
    return {**base, "measured": True, "delivery_s": delivery, "bound": bound,
            "ratio": round(overhead / delivery, 1), "why": ""}


def overhead_split(root: Path | str, unit_ids: list[str], *,
                   execution: dict | None = None, mutation: dict | None = None) -> dict:
    """The overhead-against-delivery split for these units, with EVERY component supplied.

    The one way in for anything outside this module. `_overhead_ratio` takes the execution and
    mutation summaries as arguments, and a caller that has neither to hand passed empty dicts -
    which does not fail, it silently blanks two of the three components and returns a smaller
    ratio computed from the third. The velocity record did exactly that, so the file the next
    sprint plans from disagreed with the close report it was copied from, which is the one
    disagreement the shared computation exists to prevent.

    A caller that has already composed a summary passes it, so the close does not read the
    ledger twice and cannot report one cost in two places."""
    root = Path(root)
    ids = list(unit_ids or [])
    execution = _execution_actuals(root, ids) if execution is None else execution
    mutation = _mutation_summary(root, ids) if mutation is None else mutation
    return _overhead_ratio(root, ids, execution, mutation)


def _overhead_component_lines(ov: dict) -> list[str]:
    """One line per component, derived from the same table the sum is - a measured one shows
    its minutes, an unmeasured one shows why it has none."""
    out = []
    for c in ov.get("components") or []:
        if c["measured"]:
            floor = " (a floor)" if c.get("bound") == "lower" else ""
            out.append(f"  {c['name']}: {c['seconds'] / 60:,.0f} min{floor}, from "
                       f"{c['source']}.")
        else:
            out.append(f"  {c['name']}: UNMEASURED - {c['why']}.")
    return out


def _overhead_lines(rep: dict) -> list[str]:
    """The overhead block, drawn with the velocity figures because it is read with them."""
    ov = rep.get("overhead")
    if not ov:
        return []
    if not ov.get("measured"):
        return [f"Overhead vs delivery: UNMEASURED - {ov.get('why')}.",
                *_overhead_component_lines(ov)]
    # DELIVERY IS DERIVED BY SUBTRACTION, so every minute of overhead the instruments failed
    # to attribute is credited to delivery - the ratio flatters the loop exactly in proportion
    # to how poorly it is measured. Saying which components are missing is not the same as
    # saying where their time WENT, and only the second warns a reader that the delivery figure
    # is inflated rather than merely incomplete.
    excludes = (f" It EXCLUDES {', '.join(ov['unmeasured'])}; delivery is derived by "
                f"SUBTRACTION, so that unattributed time is counted as delivery and both the "
                f"ratio and the delivery figure flatter the loop."
                if ov["unmeasured"] else "")
    floor = "at least " if ov.get("bound") == "lower" else ""
    # The ratio said "at least" and the delivery figure beside it said a bare number, so the
    # same sentence carried a qualified claim and an unqualified one about the same arithmetic.
    # Delivery is TOTAL MINUS OVERHEAD: every minute the instruments failed to attribute lands
    # in it, which makes it an upper bound by exactly the amount the ratio is a lower one.
    ceiling = "at most " if ov.get("bound") == "lower" else ""
    return [f"Overhead vs delivery: {floor}{ov['ratio']}:1 - {ov['overhead_s'] / 60:,.0f} min of "
            f"gate, review and repair against {ceiling}{ov['delivery_s'] / 60:,.0f} min of "
            f"delivery, within a measured {ov['total_s'] / 60:,.0f} min run.{excludes}",
            *_overhead_component_lines(ov)]


def _proof_coverage(root: Path, unit_ids: list[str]) -> dict:
    """What the plan's test strategy DEMANDED of this batch against what the delivery produced.

    RUN-01KYJZGZ named six units owing mutation-plus-unit proof; zero mutation runs were
    recorded, and all six reached terminal with both suites green, the gate passed and the
    close run. No lane, gate or close ever compared the two sides, so an obligation voided by a
    reasonable decision - lanes were told not to mutation-test in the working tree, after a
    reviewer doing exactly that silently reverted a shipped repair - removed the strategy's
    central proof with nothing anywhere to notice the trade.
    """
    try:
        import sprint  # noqa: PLC0415 - deferred sibling
        rows = []
        for uid in unit_ids:
            proof = sprint.lane_proof(root, uid)
            if proof.get("available") and proof.get("undischarged"):
                rows.append({"unit": uid,
                             "unmet": [u["obligation"] for u in proof["undischarged"]]})
        return {"available": True, "units": len(unit_ids), "unmet": rows}
    except Exception as exc:  # noqa: BLE001 - a proof read must never break a close report
        sdlc_md.debug("sprint_report._proof_coverage", exc)
        return {"available": False, "units": 0, "unmet": []}


def _proof_lines(rep: dict) -> list[str]:
    """Declared proof against delivered proof. An unmet obligation is NAMED with its unit: a
    count says how much went unproven and not what, and the trade is only reviewable if the
    reader can see which proof was dropped."""
    cov = rep.get("proof") or {}
    if not cov.get("available"):
        return []
    if not cov["unmet"]:
        return [f"Proof: every obligation the test strategy assigned this batch was "
                f"discharged across {cov['units']} unit(s)."]
    out = [f"Proof: {len(cov['unmet'])} of {cov['units']} unit(s) reached terminal with a "
           f"DECLARED obligation nobody discharged. Both suites can be green and the gate can "
           f"pass while this is true - nothing else compares the two sides:"]
    out.extend(f"  {r['unit']}: {', '.join(r['unmet'])}" for r in cov["unmet"])
    return out


def _seam_coverage(root: Path, unit_ids: list[str]) -> dict:
    """Which pairs of this batch shared a surface, and which of those nobody owned.

    Reported at the CLOSE because that is where a batch can still be judged as a batch. A run
    that shipped with unowned seams is not the same as one whose pairs were all accounted for,
    and a report that omits the difference lets the second read like the first."""
    try:
        import refine  # noqa: PLC0415 - deferred sibling
        seams = refine.seam_map(root, unit_ids)
    except Exception as exc:  # noqa: BLE001 - a seam read must never break a close report
        sdlc_md.debug("sprint_report._seam_coverage", exc)
        return {"available": False, "total": 0, "unowned": []}
    return {"available": True, "total": len(seams),
            "unowned": [s for s in seams if not s["owned"]]}


def _seam_lines(rep: dict) -> list[str]:
    """Seam coverage beside the points. An unowned seam is NAMED rather than counted: a number
    tells a reader how many pairs went unaccounted for and not which ones, and the whole value
    of the report is that somebody can go and look."""
    cov = rep.get("seams") or {}
    if not cov.get("available"):
        return []
    if not cov["total"]:
        return ["Seams: no pair in this batch shared a declared file."]
    unowned = cov["unowned"]
    if not unowned:
        return [f"Seams: {cov['total']}, all owned - each pair stated what it must not regress."]
    out = [f"Seams: {cov['total']}, of which {len(unowned)} shipped with NO OWNER - a pair "
           f"nobody was asked about, which is the state every contradicting pair of "
           f"RUN-01KYKVZM was in:"]
    out.extend(f"  {' + '.join(s['units'])} share {', '.join(s['shared'])}" for s in unowned)
    return out


def _delegated_rows(root: Path) -> list[dict]:
    """The delegated-agent sign-off rows, read from `critic` rather than re-derived. One
    definition of "delegated" - a second spelling here is how a writer and its readers stop
    agreeing about what was disclosed."""
    try:
        import critic  # noqa: PLC0415
        return critic.delegated_agent_signoffs(root)
    except Exception as exc:  # noqa: BLE001 - a report must not die on a log read
        sdlc_md.debug("sprint_report._delegated_rows", exc)
        return []


def _delegated_signoff_lines(rep: dict) -> list[str]:
    """The disclosure block. D0059 authorises a subagent in its own context to act as reviewer
    of record and trades independence for DISCLOSURE - so the disclosure has to be somewhere a
    reader meets without knowing to look for it. A count alone is not enough: which units, and
    which delegate, is what lets a reader weigh the verdicts."""
    rows = rep.get("delegated_signoffs") or []
    if not rows:
        return []
    out = [f"Delegated sign-offs: {len(rows)} of this sprint's sign-offs were made by an agent "
           f"under the authoring session's control, not by an independent reviewer."]
    for r in rows[:12]:
        out.append(f"  {r.get('unit', '?')} signed via {r.get('chain', '?')}")
    if len(rows) > 12:
        out.append(f"  (+{len(rows) - 12} more)")
    return out


# --- The compulsory sprint checklist ---------------------------------------------------
#
# A sprint's compulsory items were stated nowhere, so nothing could hold them and the close
# became an interview: what was dropped, what crept in and what is carried were known only to
# whoever ran it. The set below is not a list somebody thought of. It is one row per STAGE of
# the cycle this project actually runs, plus the FIGURES a close re-derives every time.
#
# All but one row is DERIVED. A checklist that asks an agent to retype what the tree already
# holds gets filled in with what the agent REMEMBERS, which is the failure the derived index
# exists to prevent. The exception is the carried known issues: whether an open defect stops
# the ship is a judgement, so it is recorded in the retro and read back here, and its absence
# is reported rather than assumed benign.

#: The waiver subject family, read by `decisions.record_waiver` / `waiver_for`. A close may
#: proceed without one compulsory item, but only on a recorded waiver naming the item and its
#: reason - on the same terms as a conformance waiver, and through the SAME primitive rather
#: than a second one that drifts. Scope tail is the item id: `rule:sprint-checklist:<item>`.
WAIVABLE_RULES = ("rule:sprint-checklist",)
WAIVER_SUBJECT = "rule:sprint-checklist"

#: A STAGE row is exactly one of these three. Evidence that cannot be READ is `not-run`, with
#: the reason in `detail`: this checklist certifies that a stage can be SHOWN to have happened,
#: and an unreadable record shows nothing. That is the conservative direction - the alternative
#: reports a ceremony as held on the strength of a file nobody could open.
RAN, NOT_RUN, WAIVED = "ran", "not-run", "waived"
#: Unsatisfied, and PAST the last command that could still have satisfied it. Reported with the
#: command that should have enforced it, and never held against the close: a gate whose only
#: exit at firing time is a waiver is a receipt rather than a gate.
EXPIRED = "expired"
#: The window that is still open when the checklist runs. Every other window has shut by then,
#: because the checklist is composed BY the close.
CLOSE_WINDOW = "sprint close"
#: A FIGURE row is answered when its value could be derived, unanswered when it could not.
ANSWERED, UNANSWERED = "answered", "unanswered"

STAGE, FIGURE = "stage", "figure"
DERIVED, RECORDED = "derived", "recorded"

#: `sprint` verbs that are NOT a stage of the cycle: the close container itself, and the
#: mechanics a run uses between stages. EVERY OTHER sprint verb must map to a checklist row -
#: which is what makes the drift guard non-circular. Add a ceremony verb tomorrow and the guard
#: fails until it is either given a row or declared here as mechanics; a guard that compared
#: the checklist against a list derived from the checklist would pass by construction.
#: Verbs of the ceremony scripts that are NOT a stage of the cycle - a query, a repair, or the
#: close itself. Keyed by script, because the guard walks every script the rows name and a flat
#: list would exempt `show` everywhere on the strength of one script having it.
#:
#: The direction of failure is deliberate. A ceremony verb missing from a row appears in
#: `uncovered` and the guard fires; a NON-ceremony verb missing from here does the same and
#: somebody adds it. The list can over-report, never under-report - which is the opposite of
#: an enumerated list that silently exempts what it forgot.
NON_CEREMONY_VERBS = {
    # `next` sits with `plan` on the OPENING side of a run, not the closing one: it resolves a
    # queued charter into a batch and opens from it. A close-checklist row would be asking the
    # close to certify something that happened before the run began.
    # `sign` is the close's own last act: the operator's one signature over the report this
    # checklist feeds, recorded on the report page and the run. A checklist row for it could
    # only ever read pending when the page is composed.
    "sprint": ("appetite", "close", "boundary", "report", "checklist", "sign",
               "reopen", "stop", "decision", "batch", "lane", "next", "queue", "call"),
    "critic": ("brief", "caller-check", "correct", "evidence", "repair", "show",
               "signoff", "signoff-brief", "supersede"),
    "handoff": ("show",),
    "lessons": ("add", "carried", "carry", "classes", "list", "propose", "prune", "rank",
                "recall", "repeats", "revalidate", "violated"),
    "retro": ("accuracy", "collate", "dispose", "estimator", "extract", "velocity"),
}

#: The compulsory set. `resolver` is resolved through `globals()` at call time, like the close
#: chain's steps, so a test can patch one row without rebuilding the table. `command` is the
#: shipped command that HOLDS the stage, and the drift guard checks it still resolves.
CHECKLIST = (
    {"id": "reconciled-before-plan", "kind": STAGE, "authority": DERIVED,
     "window": "sprint plan",
     "title": "Index drift zero before the plan", "command": "sprint plan",
     "resolver": "_ck_reconciled"},
    {"id": "goal-seat-reviewed", "kind": STAGE, "authority": DERIVED,
     "window": "sprint plan",
     "title": "Sprint Goal stated and seat-reviewed BEFORE the plan",
     "command": "sprint goal-review", "resolver": "_ck_goal_seat_review"},
    {"id": "batch-groomed", "kind": STAGE, "authority": DERIVED,
     "window": "sprint plan",
     "title": "Batch groomed - nothing ungroomed admitted", "command": "sprint breakdown",
     "resolver": "_ck_batch_groomed"},
    {"id": "run-opened", "kind": STAGE, "authority": DERIVED,
     "window": "sprint plan",
     "title": "Batch approved and the run opened", "command": "sprint plan",
     "resolver": "_ck_run_opened"},
    {"id": "batch-boundary-review", "kind": STAGE, "authority": DERIVED,
     "window": "sprint review-batch",
     "title": "Review at each delivery batch boundary", "command": "sprint review-batch",
     "resolver": "_ck_batch_boundary_review"},
    {"id": "closing-review", "kind": STAGE, "authority": DERIVED,
     "title": "Closing full-diff review", "command": "critic sprint-review",
     "resolver": "_ck_closing_review"},
    {"id": "tick-verification", "kind": STAGE, "authority": DERIVED,
     "title": "Ticked criteria the tree supports", "command": "sprint report",
     "resolver": "_ck_tick_verification"},
    {"id": "goal-judged", "kind": STAGE, "authority": DERIVED,
     "title": "Sprint Goal judged", "command": "sprint goal-verdict",
     "resolver": "_ck_goal_judged"},
    {"id": "retro", "kind": STAGE, "authority": DERIVED,
     "title": "Retro written and structurally complete", "command": "retro validate",
     "resolver": "_ck_retro"},
    {"id": "lessons", "kind": STAGE, "authority": DERIVED,
     "title": "Lessons extracted from the batch", "command": "lessons summary",
     "resolver": "_ck_lessons"},
    # `discharged_by: close` - a compulsory item the CLOSE ITSELF produces, so it is reported
    # like every other row but never held against a close that has not got there yet. A gate
    # whose only exit is the step it blocks is not a gate, it is a deadlock.
    {"id": "handoff", "kind": STAGE, "authority": DERIVED, "discharged_by": "close",
     "title": "Handoff, when the run stopped short of its goal", "command": "handoff generate",
     "resolver": "_ck_handoff"},
    {"id": "planned-vs-delivered", "kind": FIGURE, "authority": DERIVED,
     "title": "Planned against delivered", "command": "sprint report",
     "resolver": "_ck_planned_vs_delivered"},
    {"id": "not-delivered", "kind": FIGURE, "authority": DERIVED,
     "title": "Dropped, held and carried over, each with its reason", "command": "sprint batch",
     "resolver": "_ck_not_delivered"},
    {"id": "scope-creep", "kind": FIGURE, "authority": DERIVED,
     "title": "Scope creep, as a count and a ratio", "command": "sprint report",
     "resolver": "_ck_scope_creep"},
    {"id": "coverage-consistency", "kind": FIGURE, "authority": DERIVED,
     "title": "Coverage computed once, and the two readings agree",
     "command": "sprint report", "resolver": "_ck_coverage_consistency"},
    {"id": "doc-surface", "kind": FIGURE, "authority": DERIVED,
     "title": "Verbs the tooling ships that the documentation does not name",
     "command": "sprint report", "resolver": "_ck_doc_surface"},
    {"id": "mutation-survivors", "kind": FIGURE, "authority": DERIVED,
     "title": "Surviving mutants this run let through, by severity",
     "command": "sprint report", "resolver": "_ck_mutation_survivors"},
    {"id": "review-attribution", "kind": FIGURE, "authority": DERIVED,
     "title": "Who reviewed what, under which seat, over how many lenses",
     "command": "critic record", "resolver": "_ck_review_attribution"},
    {"id": "impediments", "kind": FIGURE, "authority": DERIVED,
     "title": "Blocked units and unresolved operator decisions", "command": "sprint decision",
     "resolver": "_ck_impediments"},
    {"id": "known-issues", "kind": FIGURE, "authority": RECORDED,
     "title": "Known issues carried, each with its stop-ship ruling",
     "command": "retro validate", "resolver": "_ck_known_issues"},
    {"id": "cost", "kind": FIGURE, "authority": DERIVED,
     "title": "Cost, velocity and estimate accuracy", "command": "sprint report",
     "resolver": "_ck_cost"},
)

#: The states that leave a compulsory item OUTSTANDING, and so hold the close.
_OUTSTANDING = (NOT_RUN, UNANSWERED)


def _terminal(root: Path, uid: str) -> tuple[str, bool]:
    """`(status, is_terminal)` for a unit id. `("", False)` when the unit cannot be found -
    unknown is never terminal, because counting an unreadable unit as delivered is the one
    error that inflates every figure above it."""
    found = sdlc_md.find_by_id(root, uid)
    if not found:
        return "", False
    path, type_ = found
    status = (sdlc_md.extract_field(sdlc_md.read_text_safe(path), "Status") or "").strip()
    return status, status in sdlc_md.terminal_statuses(type_)


def _planned_ids(run: dict | None) -> list[str]:
    """The batch as APPROVED, reconstructed from the run's own change ledger.

    `batch` holds the batch as it stands NOW: a drop removes from it and an add appends. So the
    planned set is the current batch, minus everything added during the run, plus everything
    dropped from it - which is the only way a report can put commitment beside actual without
    an operator retyping the plan from memory.
    """
    if not run:
        return []
    ids = [sdlc_md.norm_id(u) for u in (run.get("batch") or [])]
    added, dropped = set(), []
    for change in run.get("batch_changes") or []:
        uid = sdlc_md.norm_id(change.get("id") or "")
        if not uid:
            continue
        if change.get("action") == "add" and not change.get("note"):
            added.add(uid)
        elif change.get("action") == "drop":
            dropped.append(uid)
    # Rebuilt by filtering rather than mutating in place: the confinement roster's write
    # detector is deliberately over-inclusive and cannot tell `list.remove` from `os.remove`,
    # so a read-only module was being censused as a workspace writer.
    kept = [u for u in ids if u not in added]
    return kept + [u for u in dropped if u not in kept]


def _ck_reconciled(ctx: dict) -> tuple:
    rec = (ctx["run"] or {}).get("preplan_reconcile")
    if not isinstance(rec, dict):
        return (NOT_RUN, "no record",
                "the run carries no pre-plan reconcile record, so a drift-free census before "
                "the plan cannot be shown (`sprint plan` records one from v5)")
    drift = rec.get("drift")
    if drift:
        return (RAN, f"{drift} drift item(s)",
                "the plan read a census that had drifted; selection reads file Status, so a "
                "stale index misleads it")
    return (RAN, "drift 0", "")


def _ck_goal_seat_review(ctx: dict) -> tuple:
    # The SPRINT GOAL, not the run's `goal` field - that one holds the pipeline RUNG
    # (plan/design/done), and reviewing the goal-review record against "done" reported every
    # sprint as having had its goal reviewed for a different goal.
    goal = ctx.get("sprint_goal") or (ctx["run"] or {}).get("sprint_goal")
    if not goal:
        return (NOT_RUN, "no goal",
                "the plan recorded no Sprint Goal, so there was nothing for a seat to review; "
                "the batch is judged as a batch")
    try:
        import sprint  # noqa: PLC0415 - deferred, like every sibling read here
        status = sprint.goal_review_status(ctx["root"], goal)
    except Exception as exc:  # noqa: BLE001 - a checklist row never fails the report
        sdlc_md.debug("sprint_report._ck_goal_seat_review", exc)
        return (NOT_RUN, "unreadable", f"the goal-review record could not be read ({exc})")
    if not status.get("reviewed"):
        return (NOT_RUN, "no seat reviewed the goal",
                str(status.get("reason") or "")
                or "a goal no seat judged achievable before the plan is a goal the batch was "
                   "never sized against")
    seats = status.get("seats") or []
    detail = ("objections: " + "; ".join(str(o.get("seat")) for o in status["objections"])
              if status.get("objections") else "")
    return (RAN, f"{len(seats)} seat(s), {status.get('rounds', 0)} round(s)", detail)


def _ck_batch_groomed(ctx: dict) -> tuple:
    plan = ctx.get("plan") or {}
    bd = plan.get("breakdown")
    if not isinstance(bd, dict):
        return (NOT_RUN, "no plan record",
                "the plan record is absent or carries no breakdown, so the grooming gate's "
                "verdict on this batch cannot be shown")
    ungroomed = bd.get("ungroomed") or []
    if ungroomed:
        names = ", ".join(str(u.get("id")) for u in ungroomed[:6])
        return (RAN, f"{len(ungroomed)} ungroomed admitted",
                f"the gate flagged {names} and the batch was planned anyway")
    return (RAN, "0 ungroomed", "")


def _ck_run_opened(ctx: dict) -> tuple:
    run = ctx["run"] or {}
    if not run.get("run_id"):
        return (NOT_RUN, "no run",
                "no run state names this sprint's units, so the batch it was approved with "
                "cannot be recovered - every planned-against-delivered figure below is blind")
    return (RAN, f"{run['run_id']} ({len(run.get('batch') or [])} unit(s))", "")


def _ck_batch_boundary_review(ctx: dict) -> tuple:
    try:
        spans = run_state.batches(ctx["root"])
    except Exception as exc:  # noqa: BLE001
        sdlc_md.debug("sprint_report._ck_batch_boundary_review", exc)
        return (NOT_RUN, "unreadable", f"the batch spans could not be read ({exc})")
    if not spans:
        return (NOT_RUN, "no batch spans",
                "no delivery batch was opened, so every finding this run raised was raised at "
                "the close - which is close work, not sprint work")
    done = [s for s in spans if s.get("reviewed_at")]
    if not done:
        # A span OPENED is not a review HELD. Reporting `ran` here on the strength of the
        # span's existence would certify the ceremony by the act of scheduling it.
        return (NOT_RUN, f"0/{len(spans)} reviewed",
                "delivery batches were opened and none was independently reviewed, so every "
                "finding this run raised was raised at the close")
    if len(done) < len(spans):
        return (RAN, f"{len(done)}/{len(spans)} reviewed",
                f"{len(spans) - len(done)} span(s) closed without an independent pass")
    return (RAN, f"{len(done)}/{len(spans)} reviewed", "")


#: The one verdict that COVERS a unit. Compared against an upper-cased cell, because the
#: ledgers are written by two different recorders and a case-sensitive match against one
#: spelling is how a recorded approval comes to satisfy nothing.
_APPROVE = "APPROVE"


def _verdict_entries(ctx: dict) -> list[tuple]:
    """Every recorded verdict from both ledgers as `(sort_key, verdict, units)`, in order.

    Two ledgers hold this, and the row counts them BOTH: `critic`'s sprint-review rows and the
    run-state review rounds. Reading one and not the other is how a run whose REJECTs were
    written to the ledger this row did not consult reported `none recorded` - the same state a
    genuinely unreviewed run reports, and indistinguishable from it.

    Ordered by the recorded stamp with a stable tiebreak on append order. NOT by date alone:
    `record_verdict` writes a date with no time, so two verdicts recorded in one sitting tie,
    and a date-keyed `max()` would pick either - which turns "the later verdict wins" into a
    coin toss on exactly the case AC3 is about.
    """
    entries: list[tuple] = []
    for i, row in enumerate(ctx.get("sprint_reviews") or []):
        cell = str(row.get("units") or "")
        units = [sdlc_md.norm_id(u) for u in re.split(r"[,;\s]+", cell) if u.strip()]
        entries.append(((str(row.get("date") or ""), 0, i),
                        str(row.get("verdict") or "").strip().upper(), units))
    for i, rnd in enumerate(ctx.get("review_rounds") or []):
        idx = rnd.get("round") if isinstance(rnd.get("round"), int) else i
        entries.append(((str(rnd.get("recorded_at") or ""), 1, idx),
                        str(rnd.get("verdict") or "").strip().upper(),
                        [sdlc_md.norm_id(u) for u in (rnd.get("units") or [])]))
    entries.sort(key=lambda e: e[0])
    return entries


def _coverage(ctx: dict) -> dict | None:
    """THE coverage reading, computed once and cached on the context.

    One question - is this unit covered by an independent pass? - was being answered by three
    computations that could disagree, and did: one close reported `9/9 covered`, `0 covered, 37
    uncovered` and `71 recorded passes` about the same batch. A report that contradicts itself
    is a fact about the report, and the reader has no way to tell which number to believe.

    `sprint.review_coverage` is the canonical one: it is the richest (per-unit verdict,
    adversarial evidence, batch review, each proving independence the same way) and it is
    already what the close chain refuses on. Making the checklist rows read it means the close
    and the page it prints cannot diverge.

    None is not an empty reading. An unresolvable answer must not read as "nothing is covered",
    which would refuse every close for a reason that is really "we could not look".
    """
    if "_coverage" in ctx:
        return ctx["_coverage"]
    try:
        import sprint  # noqa: PLC0415 - deferred sibling, as elsewhere in this module
        out = sprint.review_coverage(ctx["root"], list(ctx.get("units") or []))
    except Exception as exc:  # noqa: BLE001 - a report must not die on a ledger read
        sdlc_md.debug("sprint_report._coverage", exc)
        out = None
    ctx["_coverage"] = out
    return out


def _ck_coverage_consistency(ctx: dict) -> tuple:
    """Do the two readings of coverage agree?

    The shared reading is the authority; `critic.coverage_counts` is the independent one the
    attribution row's breakdown rests on. If they disagree, the report is contradicting itself
    and NOTHING previously noticed - so the disagreement is the finding, named with both
    figures, rather than a silently-picked winner.
    """
    units = list(ctx.get("units") or [])
    if not units:
        return (ANSWERED, "no units", "")
    cov = _coverage(ctx)
    if cov is None:
        return (UNANSWERED, "unreadable",
                "the coverage reading could not be taken, so the two cannot be compared - "
                "which is not the same as their agreeing")
    shared = sum(1 for u in units if (cov.get(u) or {}).get("covered"))
    try:
        import critic  # noqa: PLC0415
        states = critic.coverage_counts(ctx["root"], units)
        other = len(states[critic.COVERAGE_APPROVED]) + len(states[critic.COVERAGE_REPAIRED])
    except Exception as exc:  # noqa: BLE001
        sdlc_md.debug("sprint_report._ck_coverage_consistency", exc)
        return (UNANSWERED, "unreadable", f"the verdict ledger could not be read ({exc})")
    if shared != other:
        return (UNANSWERED, f"{shared} vs {other} of {len(units)}",
                f"two readings of one question disagree: the shared reading says {shared} "
                f"unit(s) covered, the verdict ledger says {other}. A report contradicting "
                f"itself is a fact about the report - decide which lane is wrong before "
                f"believing either figure")
    return (ANSWERED, f"{shared}/{len(units)} covered, both readings agree", "")


def _ck_closing_review(ctx: dict) -> tuple:
    """Does an APPROVE cover EVERY unit in the batch?

    This row counted recorded passes and reported `ran` over four rounds of which three
    rejected. A count cannot see a verdict, and a batch of twelve with one approval is not a
    reviewed batch - so the quantifier is every unit, and the answer is the LAST verdict
    recorded against each, because a REJECT is a verdict on a revision rather than a property
    of the work.
    """
    entries = _verdict_entries(ctx)
    if not entries:
        return (NOT_RUN, "none recorded",
                "no full-diff pass over this batch is recorded; the close certifies that a "
                "review happened, it does not perform one")
    latest: dict[str, str] = {}
    for _key, verdict, units in entries:
        for unit in units:
            latest[unit] = verdict
    units = [sdlc_md.norm_id(u) for u in (ctx.get("units") or [])]
    # WHETHER a unit is covered comes from the shared reading; the verdict fold only says WHY,
    # because `review_coverage` reports a rejection and an absence identically and the operator
    # needs those apart. One computation decides, the other explains - never two deciding.
    cov = _coverage(ctx)
    if cov is None:
        return (NOT_RUN, "coverage unreadable",
                "the coverage reading could not be taken, so this row cannot say whether the "
                "batch was reviewed - which is not the same as its not having been")
    # BOTH, never one. The shared reading is the authority on COVERAGE - that is US0596 - but
    # a recorded non-APPROVE verdict is terminal for the unit, which is US0593, and delegating
    # the whole decision voided it: `review_coverage`'s negative test reads only the per-unit
    # verdict ledger, so an adversarial-evidence row or a stale APPROVE under a later sprint
    # REJECT cleared the row and printed "N unit(s) approved" over a batch nobody had cleared.
    # A delivery review caught it by executing the case; two of US0593's own mutants had gone
    # from killed to surviving in the commit that was supposed to unify the readings.
    open_units = [u for u in units
                  if not (cov.get(u) or {}).get("covered")
                  or (latest.get(u) and latest[u] != _APPROVE)]
    rejected = [u for u in open_units if latest.get(u) and latest[u] != _APPROVE]
    # EVERY open unit lands in one of the two buckets. The residue - uncovered, verdict present,
    # verdict is an APPROVE - matched neither test, so it fell through both and the row reported
    # `ran` over a unit the shared coverage reading calls uncovered. That is the row certifying a
    # review the coverage reading says did not happen, which is the one thing it exists to refuse.
    # An APPROVE recorded against a unit no independent pass covers is not coverage; it is a
    # verdict with nothing behind it.
    rejected_set = set(rejected)
    unreviewed = [u for u in open_units if u not in rejected_set]
    rounds = len(ctx.get("review_rounds") or [])
    if rejected or unreviewed:
        # The VALUE has to say which of the two outstanding states this is. Outstanding because
        # the verdicts were read and did not clear is a different fact from outstanding because
        # nothing was found, and only the first means somebody should go and re-review.
        parts = []
        if rejected:
            parts.append(f"{len(rejected)} unresolved")
        if unreviewed:
            parts.append(f"{len(unreviewed)} unreviewed")
        named = ", ".join(sorted(rejected + unreviewed)[:6])
        return (NOT_RUN, f"{', '.join(parts)} of {len(units)} unit(s) over {rounds} round(s)",
                f"no APPROVE covers: {named} - the row reads each unit's latest verdict, so a "
                f"batch is reviewed only when every unit in it is")
    return (RAN, f"{len(units)} unit(s) approved over {rounds} round(s)", "")


#: A criterion the author ticked. The `[x]` is a human saying "I checked this"; the row below
#: asks whether the tree agrees.
_TICKED_RE = re.compile(r"^\s*[-*]\s+\[[xX]\]\s+(?:\*\*(AC\d+)[^*]*\*\*[:\s]*)?(.*)$")


#: "This tree has no commits", as distinct from `None` - "the diff could not be taken". A row
#: that cannot tell them apart certifies the same way for a repository nobody has committed to
#: and for one it simply failed to read.
NO_HISTORY = "no-history"


def _changed_paths(root: Path, base_ref: str):
    """The paths this run changed, or None when the diff cannot be taken.

    THE SEAM. It is drawn around the SOURCE of the changed set, never around the comparison the
    row makes with it: a fixture that patches the comparison patches away the very thing under
    test, and both of this row's mutants with it.

    None is not an empty set. "The diff could not be taken" and "nothing changed" lead to
    opposite verdicts here - the first means the row cannot judge, the second means every tick
    is contradicted - and collapsing them is how a row comes to certify what it could not check.
    """
    if not str(base_ref or "").strip():
        return None
    try:
        import subprocess  # noqa: PLC0415 - deferred, like every sibling read here
        # VERIFY THE REF FIRST, and pass it after `--`. `f"{base_ref}...HEAD"` builds one argv
        # token from an unvalidated string, so a ref of `--output=<path>` is parsed by git as an
        # OPTION: it writes that file, exits 0, and returns an empty diff - which this row would
        # read as "nothing changed" and report every tick contradicted. A guard that can be
        # turned into a file write by its own input is not a guard.
        ok = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{base_ref}^{{commit}}"],
                            cwd=str(root), capture_output=True, text=True, timeout=30)
        if ok.returncode != 0:
            # WHY the ref did not resolve, asked of GIT and never of the filesystem. `git init`
            # with no commits leaves a `.git` an `exists()` probe calls present while `rev-parse`
            # still fails, so a filesystem answer reports "there is history here" for the one
            # case that has none. NO_HISTORY is a distinct verdict from None: "this tree has no
            # commits" is a fact about the tree, while None is the row admitting it could not
            # look, and collapsing them is how a preview came to say `diff unreadable` about a
            # repository that was simply empty.
            head = subprocess.run(["git", "rev-parse", "--verify", "--quiet", "HEAD"],
                                  cwd=str(root), capture_output=True, text=True, timeout=30)
            return NO_HISTORY if head.returncode != 0 else None
        # `check=True`, so a failing diff raises into the handler below rather than taking a
        # second return path of its own. One way out for every "cannot look", because the branch
        # that had its own `return` was unreachable once the ref is verified first - and an
        # unreachable branch that flips None to an empty set is a hazard nothing can pin.
        out = subprocess.run(["git", "diff", "--name-only", f"{base_ref}...HEAD", "--"],
                             cwd=str(root), capture_output=True, text=True, timeout=60,
                             check=True)
        return {ln.strip() for ln in out.stdout.splitlines() if ln.strip()}
    except Exception as exc:  # noqa: BLE001 - an unreadable diff judges nothing
        sdlc_md.debug("sprint_report._changed_paths", exc)
        return None


#: A story's claim is not a checkbox. `### ACn` headings are stamped `- **Verified:** yes (date)`
#: by `verify_ac.py`; the `- [x]` box is the BUG convention. Reading only the box made this row
#: inert for every story in the corpus - 0 of 651 - including the very unit whose two false
#: ticks are the rationale this row cites.
_VERIFIED_RE = re.compile(r"^\s*[-*]\s+\*\*Verified:\*\*\s*(yes|true)\b", re.I)


def _ticked_criteria(text: str) -> list[str]:
    """The criteria this unit's own body claims are done, named, in BOTH conventions.

    Returns the criterion ids, so a caller reporting them names `AC2` rather than a line index.
    """
    out, heading = [], None
    for line in sdlc_md.criteria_section(text).splitlines():
        h = sdlc_md.AC_HEADING_RE.match(line.strip())
        if h:
            heading = h.group(1)
            continue
        m = _TICKED_RE.match(line)
        if m:
            out.append(m.group(1) or heading or "an unnamed criterion")
            continue
        if heading and _VERIFIED_RE.match(line):
            out.append(heading)
            heading = None
    return out


def _ticks_on_a_design_rung(ctx: dict, rung: str) -> tuple:
    """The tick question a `design` rung actually owes.

    A tick asserts a criterion is MET. A `design` rung's PRODUCT is authored criteria that are
    deliberately RED - every one unticked by definition - so "do the ticks match the diff?"
    cannot be ANSWERED here, only waived. The row therefore held every design close as a
    compulsory unanswered item and printed the waiver command as its own remedy. D0144 waived
    it once; a row whose only exit is a waiver trains the operator to waive.

    So it asks the question this rung DOES owe - that nothing is ticked yet - converting an
    unanswerable item into one that would catch a criterion ticked before the behaviour
    existed, which nothing checks today.

    NEVER BLOCKING where a unit was actually read. `checklist` is not in
    `_DEFERRABLE_CLOSE_STAGES`, so an outstanding row here is a hard refusal with no bounded
    exit - the shape this exists to remove, not to relocate. A tick on a design rung is worth
    SAYING, and refusing it is a job for the rung's own gates rather than this row's.

    SCOPED TO `design`, NOT TO "not `done`", and the distinction is a review finding against the
    first cut of this repair - the SECOND time this repository has made it, after BG0582's
    sibling readers were rejected for exactly it at their own round two. `plan` and `triage` are
    also non-build rungs and their product is NOT grooming: `--goal plan` selects, sequences and
    estimates already-groomed units, so telling such a run that "a plan rung's exit is criteria
    that are authored and still RED" is false, and switching this gate off for it lets an
    unsupported tick ship. That is the filed defect MOVED one rung over rather than closed. Those
    rungs keep exactly the behaviour they already had, which is the bar.
    """
    ticked: list[str] = []
    read = 0
    for uid in (ctx.get("units") or []):
        found = sdlc_md.find_by_id(ctx["root"], uid)
        if not found:
            continue
        read += 1
        ticked.extend(f"{uid} {ac}"
                      for ac in _ticked_criteria(sdlc_md.read_text_safe(found[0])))
    units = len(ctx.get("units") or [])
    if not read:
        # A PASS OVER NOTHING IS NOT A PASS - the same rule the build-rung branch twenty lines
        # below states and obeys. Reporting "every criterion is unticked" having opened zero
        # artefacts is the affirmative-over-an-empty-set shape this row already exists to
        # refuse, and it refuses it identically on either rung. Found by a review of the first
        # cut, which had written the honest rule beside the branch that broke it.
        return (NOT_RUN, "no unit artefact could be read",
                f"none of the {units} unit(s) in the batch resolves to a file, so nothing was "
                f"examined - which is not the same as nothing being ticked")
    if ticked:
        return (RAN, f"{len(ticked)} criterion/criteria ticked on a {rung} rung",
                f"a {rung} rung's exit is criteria that are authored and still RED, so a tick "
                f"here claims a behaviour the rung did not build: {', '.join(ticked[:8])} - "
                f"reported, not blocking, because the rung's own gate is `transition`")
    return (RAN, f"no criteria ticked, which is the {rung} rung's exit",
            f"all {units} unit(s) carry criteria that are unticked, which is what a {rung} rung "
            f"delivers; the tick-versus-diff comparison is the BUILD rung's question and is not "
            f"asked of a run that never targeted it")


def read_root(ctx: dict):
    """The tree a READ-ONLY probe should ask.

    ONE accessor, because the alternative is every probe deciding for itself and one of them
    getting it wrong: `_ck_doc_surface` asked `ctx["root"]` - a scratch holding only
    `sdlc-studio/` under a dry run - and answered `not applicable` where the same row answers
    `ran` outside a preview. That is the degradation this exists to remove, one probe over from
    where it was found.

    Defaults to `root`, so a caller that supplies no read root behaves exactly as before.
    """
    return ctx.get("read_root") or ctx["root"]


def _ck_tick_verification(ctx: dict) -> tuple:
    """Does the tree support what the units say they did?

    A tick is the author asserting a criterion is met. Two units of one run were closed on
    ticks the diff contradicted, and the checklist passed them - because nothing compared the
    claim against the surfaces the unit itself declared.
    """
    # THE RUNG IS READ FIRST, ahead of the base ref and the diff. Both of those branches return
    # NOT_RUN, and the real close resolved this row as `diff unreadable` - so a rung check
    # placed at `not examined` satisfies a fixture and leaves the observed wall standing.
    # The record comes from `ctx["run"]`, which `_run_record` already resolved as the run
    # covering THESE units, so the rung read is the one this sprint was driven to rather than
    # whatever run happens to be open now.
    try:
        import sprint  # noqa: PLC0415 - deferred sibling, as elsewhere in this module
        rung = sprint.run_rung(ctx.get("run") or {})
    except Exception as exc:  # noqa: BLE001 - a report must not die on a state read
        sdlc_md.debug("sprint_report._ck_tick_verification.rung", exc)
        rung = "done"
    if rung == "design":
        return _ticks_on_a_design_rung(ctx, rung)
    base = ""
    try:
        base = run_state.base_ref(ctx["root"])
    except Exception as exc:  # noqa: BLE001
        sdlc_md.debug("sprint_report._ck_tick_verification.base", exc)
    if not str(base).strip():
        # REFUSE on an unrecorded base ref rather than falling back to HEAD. A fallback treats
        # everything as changed, passes every tick, and reproduces the exact defect this row
        # exists to catch - while reporting itself green.
        return (NOT_RUN, "no base ref",
                "the run recorded no base ref, so no diff can be taken and no tick can be "
                "checked against one; this row refuses rather than assuming everything changed")
    changed = _changed_paths(read_root(ctx), base)
    if changed is NO_HISTORY:
        # NAMED, not folded into "unreadable". The remedies are opposite: an unreadable diff is
        # something to investigate, while a tree with no commits is a state to commit out of.
        return (NOT_RUN, "no git history here",
                f"this tree carries no commits, so there is nothing for {base} to diff against - "
                "which is a fact about the tree, not this row failing to read it")
    if changed is None:
        return (NOT_RUN, "diff unreadable",
                f"the diff against {base} could not be taken, so the ticks are unjudged - "
                "which is not the same as supported")
    contradicted, examined = [], 0
    for uid in (ctx.get("units") or []):
        found = sdlc_md.find_by_id(ctx["root"], uid)
        if not found:
            continue
        text = sdlc_md.read_text_safe(found[0])
        ticked = _ticked_criteria(text)
        if not ticked:
            continue
        declared = [a.strip() for a in
                    str(sdlc_md.extract_field(text, "Affects") or "").split(",") if a.strip()]
        if not declared:
            continue
        examined += len(ticked)
        if any(any(c == d or c.startswith(d.rstrip("/") + "/") for c in changed)
               for d in declared):
            continue
        contradicted.extend(f"{uid} {ac}" for ac in ticked)
    if contradicted:
        return (NOT_RUN, f"{len(contradicted)} ticked criterion/criteria unsupported",
                f"ticked while the surfaces the unit declared are unchanged since {base}: "
                f"{', '.join(contradicted[:8])}")
    if not examined:
        # A PASS OVER NOTHING is not a pass. Reporting `ticks supported` having read zero ticks
        # is the affirmative-over-an-empty-set shape the sibling rows refuse by design, and it
        # is how this row read green across a whole batch while understanding one of the two
        # conventions its corpus is written in.
        return (NOT_RUN, "no ticked criteria found",
                f"none of the {len(ctx.get('units') or [])} unit(s) carries a criterion this "
                f"row can read, so nothing was checked - which is not the same as everything "
                f"being supported")
    return (RAN, f"{examined} ticked criterion/criteria supported by the diff since {base}", "")


def _ck_goal_judged(ctx: dict) -> tuple:
    if not ctx.get("sprint_goal"):
        return (NOT_RUN, "no goal to judge",
                "the plan set no goal, so the run is judged as a batch - `goal-verdict` "
                "refuses to invent alignment after the fact")
    gv = ctx.get("goal_verdict")
    if not gv or not gv.get("verdict"):
        return (NOT_RUN, "unjudged",
                "the goal was stated and never judged, which is the state a green unit count "
                "reads as success from")
    return (RAN, str(gv["verdict"]), str(gv.get("note") or ""))


def _ck_retro(ctx: dict) -> tuple:
    val = ctx.get("retro_validate") or {}
    if not val:
        return (NOT_RUN, "no retro", "no retro was resolved for this close")
    # A retro that was never WRITTEN is not a retro that ran badly. `retro.validate` reports a
    # missing file as an error like any other, so the row read RAN - the ceremony reporting
    # itself as performed on the strength of a file that does not exist. `path` is None only in
    # that case, which is the distinction every other row in this table already draws.
    if val.get("path") is None:
        return (NOT_RUN, "no retro file",
                "; ".join(val.get("errors") or ["the retro named for this close was never written"]))
    if val.get("errors"):
        return (RAN, f"{len(val['errors'])} structural error(s)", "; ".join(val["errors"][:3]))
    return (RAN, "complete", "")


def _ck_lessons(ctx: dict) -> tuple:
    lessons = (ctx.get("retro_validate") or {}).get("lessons") or []
    if not lessons:
        return (NOT_RUN, "none recorded",
                "a sprint that recorded no lesson either learned nothing or wrote nothing "
                "down, and only one of those is worth repeating")
    return (RAN, f"{len(lessons)} recorded", "")


def close_report(summary: dict) -> str:
    """What the close TELLS the operator: shipped, carried, cost, findings.

    Being informed is the operator's half of human-in-the-lead. If they are not a step in the
    machine, the machine has to reach them - so the close says what happened rather than
    leaving a file to be discovered.

    An absent figure is NAMED absent, never dropped. A missing line reads as nothing to
    report, and "not attributable" and "nothing happened" are different facts - only one of
    them means somebody should go and look.
    """
    def _listing(items, empty: str) -> str:
        items = [str(i) for i in (items or []) if str(i).strip()]
        return "\n".join(f"    - {i}" for i in items) if items else f"    {empty}"

    cost = summary.get("cost") or {}
    tokens = cost.get("tokens")
    points = cost.get("points")
    if isinstance(tokens, int):
        cost_line = f"    {tokens:,} tokens"
        if isinstance(points, int) and points:
            cost_line += f" over {points} points ({tokens // points:,}/point)"
    else:
        cost_line = "    not attributable - no per-run figure was captured for this close"

    run = summary.get("run_id") or "this run"
    lines = [
        f"CLOSE REPORT - {run}",
        "",
        "  SHIPPED",
        _listing(summary.get("shipped"), "none - this close shipped no units"),
        "",
        "  CARRIED",
        _listing(summary.get("carried"), "none carried"),
        "",
        "  COST",
        cost_line,
        "",
        "  FINDINGS",
        _listing(summary.get("findings"), "none raised by the reviews"),
    ]
    # DEFERRED appears only on a close that deferred something. A section reading "none
    # deferred" on every ordinary close trains the eye past it, and this is the line that
    # matters on the one route where it is ever non-empty - `--file-and-close`, the exit for a
    # close that could not complete cleanly. Deferred is not waived, and the wording says so
    # here as well as in the retro, because the report is what the operator actually reads.
    if deferred := [str(d) for d in (summary.get("deferred") or []) if str(d).strip()]:
        lines += ["", "  DEFERRED (filed, not waived)", _listing(deferred, "")]
    return "\n".join(lines)


def _ck_handoff(ctx: dict) -> tuple:
    run = ctx["run"] or {}
    outcome = str(run.get("outcome") or "")
    if outcome in ("", run_state.RUNNING, run_state.GOAL_REACHED):
        return (RAN, "not owed",
                "a run that reached its goal owes a retro, not a handoff"
                if outcome == run_state.GOAL_REACHED else
                "the run is still open, so no handoff is owed yet")
    if not run.get("handoff"):
        return (NOT_RUN, f"owed ({outcome})",
                "the run stopped short of its goal and left no handoff, so the tail is "
                "scattered across hints, the ledger and the retro")
    return (RAN, str(run["handoff"]), "")


def _ck_planned_vs_delivered(ctx: dict) -> tuple:
    planned = ctx["planned"]
    if not planned:
        return (UNANSWERED, "unknown",
                "no run record names this sprint's units, so what it COMMITTED to cannot be "
                "recovered - only what it happened to finish")
    delivered = [u for u in ctx["units"] if _terminal(ctx["root"], u)[1]]
    pts = ctx.get("delivered_points")
    # PLANNED points too, or the row states commitment in units and actual in points and an
    # operator is left doing the arithmetic the row exists to have done. Summed from the
    # planned units' own artefacts, so it needs no plan-time forecast - an interactive sprint
    # records none, and a figure only some sprints can show is a figure nobody relies on.
    planned_pts = _planned_points(ctx["root"], planned)
    return (ANSWERED,
            f"{len(delivered)}/{len(planned)} unit(s), "
            f"{pts if pts is not None else 'unknown'}/"
            f"{planned_pts if planned_pts is not None else 'unknown'} point(s) delivered", "")


def _planned_points(root: Path, planned: list) -> int | None:
    """Summed `Points` of the PLANNED units, from their artefacts. None when not one resolves -
    an absent total and a genuine zero are different facts, and rendering both as 0 would let a
    sprint whose units all vanished read as one that committed to nothing."""
    total, seen = 0, False
    for uid in planned:
        hit = sdlc_md.find_by_id(root, uid)
        if not hit:
            continue
        seen = True
        pts = sdlc_md.read_points(sdlc_md.read_text_safe(hit[0]))
        if isinstance(pts, int) and pts > 0:
            total += pts
    return total if seen else None


def _ck_not_delivered(ctx: dict) -> tuple:
    run = ctx["run"] or {}
    if not run.get("run_id"):
        return (UNANSWERED, "unknown", "no run record, so no batch-change ledger to read")
    dropped = [c for c in (run.get("batch_changes") or []) if c.get("action") == "drop"]
    dropped_ids = {sdlc_md.norm_id(c.get("id") or "") for c in dropped}
    # HELD is a live state, not a log entry. `deferred_units` is append-only and `decision
    # resolve` never removes from it, so a unit whose decision was answered and which then
    # shipped rendered "held (operator decision pending)" AND counted delivered on the same
    # page. A unit is held only while a decision on it is genuinely outstanding.
    pending = {sdlc_md.norm_id(d.get("unit") or "")
               for d in (run.get("pending_decisions") or []) if not d.get("resolution")}
    held = [sdlc_md.norm_id(u) for u in (run.get("deferred_units") or [])
            if sdlc_md.norm_id(u) in pending and not _terminal(ctx["root"], u)[1]
            and sdlc_md.norm_id(u) not in dropped_ids]
    # Carried is measured against the PLANNED set, not the retro's Batch. Reading the retro
    # made a planned unit that never reached it invisible here, so the row asserted "every
    # planned unit was delivered" while planned-vs-delivered above read 1/2 on the same page.
    seen = {sdlc_md.norm_id(u) for u in ctx["units"]}
    # DISJOINT, or a unit is reported twice under two headings and the counts stop adding up -
    # the shape an independent seat found in the dropped-versus-carried pair. A planned unit
    # the retro never lists is UNACCOUNTED; one it lists but nobody finished is CARRIED.
    # ...and held, or a deferred unit the retro does not list is emitted under BOTH headings and
    # one undelivered unit reads "1 held, 1 UNACCOUNTED". Every bucket here excludes the ones
    # decided before it: dropped wins over held, held over unaccounted, unaccounted over
    # carried. One unit, one heading, or the counts stop meaning anything.
    unaccounted = [u for u in (ctx["planned"] or [])
                   if sdlc_md.norm_id(u) not in seen
                   and sdlc_md.norm_id(u) not in dropped_ids
                   and sdlc_md.norm_id(u) not in held]
    unaccounted_ids = {sdlc_md.norm_id(u) for u in unaccounted}
    carried = [u for u in (ctx["planned"] or ctx["units"])
               if not _terminal(ctx["root"], u)[1]
               and sdlc_md.norm_id(u) not in held
               and sdlc_md.norm_id(u) not in dropped_ids
               and sdlc_md.norm_id(u) not in unaccounted_ids]
    bits = []
    for c in dropped:
        bits.append(f"dropped {c.get('id')}: {c.get('reason') or 'NO REASON RECORDED'}")
    for u in held:
        bits.append(f"held {u} (operator decision pending)")
    for u in carried:
        bits.append(f"carry-over {u} ({_terminal(ctx['root'], u)[0] or 'status unreadable'})")
    for u in unaccounted:
        bits.append(f"UNACCOUNTED {u} (planned, and the retro does not list it)")
    if not bits:
        return (ANSWERED, "none", "every planned unit was delivered")
    more = len(bits) - 12
    return (ANSWERED,
            f"{len(dropped)} dropped, {len(held)} held, {len(carried)} carried over"
            + (f", {len(unaccounted)} UNACCOUNTED" if unaccounted else ""),
            "; ".join(bits[:12]) + (f" (+{more} more)" if more > 0 else ""))


def _ck_scope_creep(ctx: dict) -> tuple:
    planned = ctx["planned"]
    filed = ctx["filed_in_run"]
    if not planned:
        return (UNANSWERED, "unknown",
                "the planned set is unknown, so a ratio against it would be arithmetic on a "
                "number nobody can check")
    ratio = round(len(filed) / len(planned), 2)
    return (ANSWERED, f"{len(filed)} filed against {len(planned)} planned (ratio {ratio})",
            ", ".join(filed[:12]) + (f" (+{len(filed) - 12} more)" if len(filed) > 12 else ""))


#: A round is at least two reviewers on distinct lenses, whatever the diff size, because the
#: defects a lone reviewer misses are the ones that reviewer's one lens does not point at.
MIN_LENSES = 2


def _ck_doc_surface(ctx: dict) -> tuple:
    """How many enumerated verbs carry no invocable form in the hand-written documentation.

    DERIVED by calling the measurement, never a number typed into a report - a figure written
    down is one that stops being true the day after. It is the same call the gate lane makes,
    so the two cannot disagree.
    """
    import doc_coverage  # noqa: PLC0415 - the ONE applicability reader, shared with the gate lane
    if not doc_coverage.is_skill_repo(str(read_root(ctx))):
        return (NOT_RUN, "not applicable",
                "the verb surface is the skill's own documentation, which this project does not "
                "have - the row is undefined here rather than unmeasurable")
    try:
        import command_audit  # noqa: PLC0415
        r = command_audit.verb_coverage(str(read_root(ctx)))
    except Exception as exc:  # noqa: BLE001 - a report must not die on a measurement
        return (NOT_RUN, "unreadable",
                f"the verb surface could not be measured ({type(exc).__name__}: {exc})")
    return (RAN, f"{r['documented']} of {r['verbs']} verb(s) documented ({r['ratio']}%), "
                 f"{r['undocumented']} not",
            "a verb with no invocable form in the documentation is one a reader cannot find as "
            "something they could type - reported, never blocking")


def _ck_mutation_survivors(ctx: dict) -> tuple:
    """The survivors this run FILED rather than blocked on, counted by severity.

    THIS RUN's, scoped by the run id stamped on each filed artefact, and derived by reading
    those artefacts rather than a tally the filer kept alongside them.
    A tally is what a hurried implementation writes and it is invisible to any fixture whose
    artefacts all arrive through the filer - so the count would be right for exactly as long as
    nothing else ever wrote one.

    This row exists because reporting rather than blocking is a trade the operator only gets to
    make if the thing traded away is visible. A survivor filed and never counted is a survivor
    silently dropped, which is the outcome blocking was rejected to avoid, not the one chosen.
    """
    root = Path(ctx["root"])
    bugs = root / "sdlc-studio" / "bugs"
    if not bugs.is_dir():
        return (NOT_RUN, "no backlog", "there is no bugs directory to count from")
    # SCOPED TO THIS RUN. The first cut globbed every survivor bug ever filed, so the row's own
    # title - and the criterion, and the changelog - claimed a scope the resolver did not have,
    # and the number only ever grew. The run id is stamped on the artefact at filing.
    run_id = ((ctx.get("run") or {}).get("run_id") or "").strip()
    if not run_id:
        return (NOT_RUN, "no run", "no run is recorded, so survivors cannot be scoped to one")
    counts: dict = {}
    orphans: list = []
    for f in sorted(bugs.rglob("BG*.md")):
        try:
            body = f.read_text(encoding="utf-8")
        except OSError:
            continue
        if not (sdlc_md.extract_field(body, "Mutation-survivor") or "").strip():
            continue
        stamped = (sdlc_md.extract_field(body, "Mutation-survivor-run") or "").strip()
        sev = (sdlc_md.extract_field(body, "Severity") or "unstated").strip() or "unstated"
        if stamped == run_id:
            counts[sev] = counts.get(sev, 0) + 1
        elif stamped in ("", "none"):
            # Filed with no run open, so no close will ever claim it. Reported rather than
            # dropped: a survivor nobody counts is the silent loss this row exists to prevent,
            # and scoping to a run must not become a new way of losing one.
            orphans.append(sev)
    total = sum(counts.values())
    unattributed = (f"; {len(orphans)} filed with no run open, counted by no close"
                    if orphans else "")
    if not total:
        return (RAN, f"0 survivors filed{unattributed}",
                "a survivor filed outside a run is counted by nobody" if orphans else "")
    order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    split = ", ".join(f"{sev} {n}" for sev, n in
                      sorted(counts.items(), key=lambda kv: (order.get(kv[0], 9), kv[0])))
    return (RAN, f"{total} survivor(s) filed - {split}{unattributed}",
            "these are mutants a repair let through, filed rather than blocked on. Fix them "
            "or decide to live with them, but decide")


def _ck_review_attribution(ctx: dict) -> tuple:
    units = ctx["units"]
    if not units:
        return (UNANSWERED, "no units", "the batch named no units")
    try:
        import critic  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001
        sdlc_md.debug("sprint_report._ck_review_attribution", exc)
        return (UNANSWERED, "unreadable", f"the verdict log could not be read ({exc})")
    def _lens(who: str) -> str:
        """The LENS a reviewer looks through: their seat, or - failing that - themselves.

        A lens is a point of view, and two reviewers sharing seat `qa` bring one. Counting
        distinct NAMES reported them as two and let a single-lens round escape the
        under-covered mark, contradicting this row's own title, `MIN_LENSES`, and the shipped
        doctrine. The fallback matters as much: a reviewer with no declared seat is not
        interchangeable with another seat-less reviewer, so they count separately rather than
        collapsing into one anonymous lens.
        """
        seat = critic.seat_for(ctx["root"], who) if who else None
        return f"seat:{seat}" if seat else f"who:{who}"

    # THREE states, not two. `verdict_for` alone cannot tell "rejected and repaired" from
    # "nobody looked", and one number cannot carry three states: the figure this replaces said
    # "28 of 44 covered by no independent review" when 18 of those 28 carried a REJECT whose
    # every finding had been repaired in-run. Wrong by 18 out of 19, and wrong in the direction
    # that hides the one real gap inside a crowd of false ones.
    states = critic.coverage_counts(ctx["root"], units)
    covered, rejected, uncovered, reviewers = [], [], [], set()
    # UNCOVERED comes from the shared reading, not from a second walk of the verdict ledger.
    # This row and the closing-review row above were each deciding the same question their own
    # way, which is how one close reported three different answers to it.
    shared = _coverage(ctx) or {}
    by_lane = []
    for uid in units:
        v = critic.verdict_for(ctx["root"], uid)
        # A unit with a VERDICT falls through to the covered/rejected split below - the shared
        # reading marks a rejection as not-covered, and short-circuiting here lost the
        # rejected-versus-never-opened distinction this row exists to draw. What the shared
        # reading decides is the NO-VERDICT case: covered by another lane, or covered by nothing.
        if not (shared.get(uid) or {}).get("covered") and not v:
            uncovered.append(uid)
            continue
        if not v:
            # Covered, by a lane that carries no per-unit verdict. Counted and NAMED as that
            # rather than folded into `covered` beside the verdicted ones: the first attempt did
            # fold it, and the row then printed "2 unreviewed" next to "US0001 by adversarial
            # evidence" because its figures come from a counter with no evidence lane. A row
            # that contradicts itself in one line is the thing this unit exists to remove.
            by_lane.append(f"{uid} by {(shared.get(uid) or {}).get('by') or 'an independent pass'}")
            continue
        who = (v.get("reviewer") or "").strip()
        reviewers.add(who)
        seat = critic.seat_for(ctx["root"], who) if who else None
        label = f"{uid} by {who or 'unnamed'} ({seat or 'NO DECLARED SEAT'})"
        (covered if str(v.get("verdict") or "").strip().upper() == "APPROVE"
         else rejected).append(label)
    # The reviewers of the batch as a whole count too: a full-diff pass covers every unit at
    # once, so counting only per-unit rows would report a two-lens round as one-lens.
    reviewers |= {str(r.get("reviewer") or "").strip()
                  for r in ctx["sprint_reviews"] + ctx["review_rounds"]}
    lenses = len({_lens(r) for r in reviewers if r})
    under = lenses < MIN_LENSES
    repaired = states[critic.COVERAGE_REPAIRED]
    # The uncovered bucket holds two DIFFERENT facts and the operator needs both: a rejection
    # nobody has answered, and a unit nobody has opened. Calling the first "unreviewed" would be
    # the same collapse this row exists to undo, one level down - it WAS reviewed, and rejected.
    # `never` excludes anything the SHARED reading covered by a non-verdict lane. Without that,
    # the row printed "UNREVIEWED US0001" beside "US0001 by adversarial evidence" - contradicting
    # itself in one line, which is the failure this unit exists to remove. The rejected/unopened
    # split is untouched: those are the two facts the bucket has to keep apart.
    lane_ids = {s.split(" by ")[0] for s in by_lane}
    unanswered = [u for u in states[critic.COVERAGE_UNREVIEWED]
                  if critic.verdict_for(ctx["root"], u)]
    never = [u for u in states[critic.COVERAGE_UNREVIEWED]
             if not critic.verdict_for(ctx["root"], u) and u not in lane_ids]
    value = (f"{len(states[critic.COVERAGE_APPROVED])} approved, {len(repaired)} repaired, "
             f"{len(unanswered)} rejected, {len(never)} unreviewed"
             + (f", {len(by_lane)} by a non-verdict lane" if by_lane else "")
             + f"; {lenses} lens(es)"
             + (" - UNDER-COVERED" if under else ""))
    # The unreviewed units are NAMED, never only counted: the failure being repaired is one real
    # gap hidden inside a crowd of false ones, so a count alone leaves the operator to find it.
    shown = ([f"UNREVIEWED {u}" for u in never]
             + covered[:6] + by_lane[:6] + [f"REJECTED {r}" for r in rejected[:6]])
    dropped_from_view = (len(covered) - len(covered[:6])) + (len(rejected) - len(rejected[:6]))
    detail = "; ".join(shown) + (f" (+{dropped_from_view} more)" if dropped_from_view else "")
    if under:
        detail = (f"a round under {MIN_LENSES} distinct reviewers is recorded as under-covered: "
                  f"one lens does not point at what it does not point at. " + detail)
    return (ANSWERED, value, detail)


def _ck_impediments(ctx: dict) -> tuple:
    run = ctx["run"]
    if run is None:
        return (UNANSWERED, "unreadable",
                "no run record could be read, so whether anything was blocked is unknown - "
                "which is not the same as nothing having been blocked")
    pending = [d for d in (run.get("pending_decisions") or []) if not d.get("resolution")]
    blocked = []
    for uid in ctx["units"]:
        status = _terminal(ctx["root"], uid)[0]
        if status.strip().lower() == "blocked":
            blocked.append(uid)
    if not pending and not blocked:
        return (ANSWERED, "none", "nothing blocked and no operator question outstanding")
    # The BLOCKER, read through the same convention the blocker sweep uses. "Blocked" on its
    # own tells an operator that something stopped and not what to go and unstick, and a
    # blocked unit RECORDING no blocker is a different and worse fact - it is an impediment
    # nobody can act on, so it is named rather than rendered identically to a known one.
    def _blocker(uid: str) -> str:
        try:
            import blocker_sweep  # noqa: PLC0415
            found = sdlc_md.find_by_id(ctx["root"], uid)   # (path, type), not a bare path
            path = found[0] if found else None
            refs = blocker_sweep._referents(sdlc_md.read_text_safe(path)) if path else []
        except Exception as exc:  # noqa: BLE001 - a report must not die on one unreadable unit
            sdlc_md.debug("sprint_report._ck_impediments", exc)
            return f"blocked {uid} (blocker UNREADABLE)"
        return (f"blocked {uid} by {', '.join(refs)}" if refs
                else f"blocked {uid} with NO RECORDED BLOCKER - nothing says what to unstick")

    bits = [_blocker(u) for u in blocked]
    bits += [f"open question on {d.get('unit')}: {d.get('question')}" for d in pending]
    dropped_from_view = max(len(bits) - 12, 0)
    return (ANSWERED, f"{len(blocked)} blocked, {len(pending)} open question(s)",
            "; ".join(bits[:12])
            + (f" (+{dropped_from_view} more)" if dropped_from_view else ""))


def _ck_known_issues(ctx: dict) -> tuple:
    rows = ctx["carried_issues"]
    open_findings = ctx["open_filed_in_run"]
    # BLINDNESS FIRST. Either source coming back None means the scan could not run, and a scan
    # that saw nothing must never render as a workspace with nothing to see. The impediments
    # row draws exactly this distinction on the same page; this one used to contradict it.
    if rows is None or open_findings is None:
        why = ("the retro's carried-issues table could not be read" if rows is None
               else "the run record carries no start time, so no finding could be dated to "
                    "this run")
        return (UNANSWERED, "unreadable",
                f"{why} - so whether this sprint leaves an open finding is UNKNOWN, which is "
                f"not the same as leaving none")
    ruled = {r["id"] for r in rows if r["ok"]}
    unruled = [u for u in open_findings if u not in ruled]
    # The same join the gate applies. Reporting every stop-ship row while the gate discharges
    # some of them printed "2 STOP-SHIP" beside a close that proceeded over one - the operator
    # reads this row, not the gate's dict.
    stop = [r["id"] for r in rows
            if r["ok"] and r["ruling"] == "stop-ship" and not r.get("terminal")]
    discharged = [r["id"] for r in rows
                  if r["ok"] and r["ruling"] == "stop-ship" and r.get("terminal")]
    broken = [f"{r['id'] or '(no id)'}: {r['why']}" for r in rows if not r["ok"]]
    undatable = ctx.get("undatable_findings") or []
    if not rows and not open_findings:
        if undatable:
            # "None carried" is a claim about everything, and this scan could not judge these.
            # Saying it anyway is how a visible over-count becomes a silent clean sheet.
            return (UNANSWERED, f"none carried, but {len(undatable)} finding(s) undatable",
                    f"the window could not judge {', '.join(undatable[:12])}"
                    + (f" (+{len(undatable) - 12} more)" if len(undatable) > 12 else "")
                    + " - each carries a `Raised-in-batch` stamp recording no moment and no "
                      "`Created` to fall back on, so whether this sprint left them open is "
                      "UNKNOWN, which is not the same as leaving none")
        return (ANSWERED, "none carried",
                "the scan ran and this sprint left no finding open - a scan that could NOT "
                "run reports unreadable above, so this row means what it says")
    if unruled or broken:
        bits = [f"UNRULED {u}" for u in unruled] + broken
        return (UNANSWERED, f"{len(unruled)} unruled, {len(broken)} malformed row(s)",
                "; ".join(bits[:12]) + " - an open finding nobody ruled on is not a carried "
                "issue, it is one nobody looked at")
    detail = "; ".join(f"{r['id']} {r['ruling']} by {r['by']}" for r in rows[:12])
    if discharged:
        # Named, because a ruling that stopped holding is a fact the signer is entitled to -
        # silently dropping it from the count is how a hold disappears with nobody told.
        detail += (f" - DISCHARGED (their findings reached a terminal status): "
                   f"{', '.join(discharged)}")
    return (ANSWERED, f"{len(rows)} ruled" + (f", {len(stop)} STOP-SHIP" if stop else "")
            + (f", {len(discharged)} discharged" if discharged else ""), detail)


def _ck_cost(ctx: dict) -> tuple:
    spend = ctx.get("spend") or {}
    if not spend.get("measured_units") and not ctx.get("sprint_actual_tokens"):
        return (UNANSWERED, "unattributed",
                "no per-unit telemetry and no harness-tracked sprint total, so what this "
                "sprint cost is not attributable - which is not zero")
    return (ANSWERED, f"{spend.get('tokens', 0):,} token(s) over "
                      f"{spend.get('measured_units', 0)} measured unit(s)", "")


#: An ISO-8601 timestamp anywhere in a `Raised-in-batch` stamp. Anchored on the SHAPE of a date
#: rather than on position: the stamp is a bare timestamp when a batch claimed the finding and
#: prose when none did, so position says nothing and only the shape is reliable.
_STAMP_TS_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?")


def _stamp_timestamp(stamp: str) -> str:
    """The moment a `Raised-in-batch` stamp records, or `""` when it records none.

    `""` is the honest answer for a prose stamp, and the caller treats it exactly as it treats an
    empty field - undatable, therefore outside every window. Taking the last token instead read
    the word `batch` as a date.
    """
    m = _STAMP_TS_RE.search(stamp or "")
    return m.group(0) if m else ""


#: A date, or a full timestamp, at the START of a `Created` value.
_CREATED_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)?")


def _created_date(text: str) -> str:
    """The `Created` field, the fallback when a `Raised-in-batch` stamp carries no timestamp.

    `file_finding` wrote `none open - raised outside a delivery batch` for a finding raised
    with no batch open, and until it appended the moment of filing that stamp recorded none -
    but the artefact still does, to the day, in `Created`. Reading it is what keeps a
    prose-stamped finding attributable instead of invisible, and `sprint.py`'s reader of the
    same field already resolves it this way.
    """
    value = (sdlc_md.extract_field(text, "Created") or "").strip()
    # Guarded BY SHAPE, exactly as `_stamp_timestamp` is. `Created: TBD` sorts after every ISO
    # date, so an unguarded read would attribute it to any open run - and it would not appear in
    # the undatable set either, so nothing would disclose it. That is this bug's own arithmetic
    # moved one layer over.
    m = _CREATED_DATE_RE.match(value)
    return m.group(0) if m else ""


def _as_utc(stamp: str) -> str:
    """`stamp`, marked UTC when it carries no offset of its own. Every writer here stamps UTC, and
    a moment read without an offset cannot be compared with one read with it."""
    at = _at(stamp)
    return _iso(at.replace(tzinfo=timezone.utc)) if at is not None and at.tzinfo is None else stamp


def _undatable_findings(root: Path, *, open_only: bool = True) -> list[str]:
    """Findings whose `Raised-in-batch` stamp carries no timestamp, by artefact id.

    Reported rather than silently skipped: a finding excluded without trace is the same defect as
    one attributed wrongly, one direction over. The close names these so a reader can see what the
    window could not judge.

    Scoped to NON-TERMINAL findings by default, and the scoping is the difference between a
    disclosure and noise. This corpus holds 45 of them once both sources are read; naming every
    artefact that merely lacks a stamp would tell a reader nothing they can act on, while these are
    exactly the set a stop-ship question could be asked about.
    """
    out = []
    for type_ in ("bug", "cr"):
        for path in sdlc_md.artifact_files(type_, Path(root)):
            uid = sdlc_md.norm_id(sdlc_md.extract_record_id(path.stem) or "")
            if not uid:
                continue
            text = sdlc_md.read_text_safe(path)
            stamp = (sdlc_md.extract_field(text, "Raised-in-batch") or "").strip()
            # Undatable means a stamp EXISTS and neither it nor `Created` carries a moment. An
            # artefact with no stamp at all is not an undatable stamp - it predates the mechanism
            # that writes one, and `_open_findings` skips it for the same reason. The two readers
            # must apply the same rule or the row would disclose a set the scan never considered.
            if not stamp or _stamp_timestamp(stamp) or _created_date(text):
                continue
            if open_only:
                status = (sdlc_md.extract_field(text, "Status") or "").strip()
                if status in sdlc_md.terminal_statuses(type_):
                    continue
            out.append(uid)
    return sorted(out)


def _open_findings(root: Path, run: dict | None) -> tuple[list[str], list[str]]:
    """`(filed during the run, of those the ones still open)`, by artefact id.

    Joined on the `Raised-in-batch` stamp `file_finding` writes, so a finding counts against
    the run that produced it rather than against whatever happened to be open when someone
    last edited the file.
    """
    if not run or not run.get("started_at"):
        # None, not []. An empty result and a scan that could not run are different facts, and
        # returning [] for both let the known-issues row render ANSWERED "none carried" over a
        # workspace with open findings on disk - a gate reporting green over something it never
        # looked at, which is the one thing the checklist exists to stop.
        return None, None
    started, ended = run.get("started_at"), run.get("ended_at")
    filed, still_open = [], []
    for type_ in ("bug", "cr"):
        for path in sdlc_md.artifact_files(type_, Path(root)):
            uid = sdlc_md.norm_id(sdlc_md.extract_record_id(path.stem) or "")
            if not uid:
                continue
            text = sdlc_md.read_text_safe(path)
            stamp = (sdlc_md.extract_field(text, "Raised-in-batch") or "").strip()
            # A stamp naming no batch still carries the moment it was raised, and a raise
            # inside the window is this run's whether or not a batch span claimed it. But the
            # moment has to be PARSED, not taken as the last whitespace-separated token: the
            # stamp `file_finding` writes outside a batch ends in the word `batch`, and a word
            # sorts after every ISO timestamp, so with an OPEN run - `ended` None, which is the
            # state a close runs in - it passed both comparisons and the finding was attributed
            # to whichever run happened to be open. One run filed two findings and its close
            # demanded stop-ship rulings for 81.
            if not stamp:
                # No stamp AT ALL predates the mechanism that writes one: nothing ever claimed
                # this finding for a run, and counting it would attribute the whole historical
                # backlog to whichever run is open - 558 of them here, 402 of which carry no
                # `Created` either. Only a stamp that EXISTS
                # but records no moment is the case this bug is about.
                continue
            when = _stamp_timestamp(stamp) or _created_date(text)
            if not when:
                # Undatable: no timestamp in the stamp and no `Created` to fall back on.
                # NOT attributed - attributing them handed the close 47 findings to rule on that
                # no run had touched. But not silently dropped either: `_undatable_findings`
                # collects them and the known-issues row reads it, so the close can never
                # certify "none carried" over a set it was unable to judge. Excluding them with
                # nothing said is what made a visible over-count into a silent under-count.
                continue
            # Compare at the granularity the value HAS. A date-only `Created` can only be judged
            # to the day, but a stamp carrying a real moment must be compared in full: truncating
            # both sides for every input gave a 4h22m run 45 findings raised elsewhere that day,
            # and made two different runs each claim the same eleven. 15 days in this corpus
            # carry more than one run, so the loss is live rather than theoretical.
            # A moment is placed in the half-open `[start, end)` the DORA figures use: with the
            # end inclusive, a finding stamped in the page's own generation second entered the
            # re-derivation and not the page, so `check` read INVALID on a page nobody touched.
            if len(when) == 10:
                if when < started[:10] or (ended and when > ended[:10]):
                    continue
            elif not _in_window(_as_utc(when), _at(_as_utc(started)), _at(_as_utc(ended or ""))):
                continue
            filed.append(uid)
            status = (sdlc_md.extract_field(text, "Status") or "").strip()
            if status not in sdlc_md.terminal_statuses(type_):
                still_open.append(uid)
    return sorted(filed), sorted(still_open)


def checklist(root: Path | str, retro_id: str, *, unit_ids: list[str] | None = None,
              rep: dict | None = None, read_root: Path | str | None = None) -> dict:
    """The compulsory checklist for a sprint, one row per item. Read-only.

    Every row carries `state`, and only `state` decides whether the close may proceed: a row is
    OUTSTANDING when it is `not-run` or `unanswered` and no waiver names it. A resolver that
    raises is reported as outstanding with the exception in `detail` - a checklist row that
    fails open is a row that certifies the thing it could not check.
    """
    root = Path(root)
    rep = rep if rep is not None else report(root, retro_id)
    units = unit_ids if unit_ids is not None else list(rep.get("units") or [])
    run = _run_record(root, units)
    try:
        import critic  # noqa: PLC0415
        sprint_reviews, review_rounds = critic.sprint_reviews(root), run_state.review_rounds(root)
    except Exception as exc:  # noqa: BLE001 - a report must not die on a log read
        sdlc_md.debug("sprint_report.checklist.reviews", exc)
        sprint_reviews, review_rounds = [], []
    filed, still_open = _open_findings(root, run)
    ctx = {
        # `read_root` is the tree a READ-ONLY probe should ask, and it differs from `root` in
        # exactly one caller: `close_dry_run`, whose `root` is a scratch copy holding only
        # `sdlc-studio/`. A probe reading `.git`, `.claude/skills/`, `tools/` or `changelog.d/`
        # from that copy finds nothing and degrades to a softer verdict than the close it
        # previews. Carrying the real tree separately keeps every write confined to the scratch
        # - a symlinked `.git` was tried first and let `git add` reach the real object database.
        # Defaults to `root`, so every other caller is unchanged.
        "root": root, "read_root": Path(read_root) if read_root else root,
        "retro_id": retro_id, "units": units, "run": run,
        "planned": _planned_ids(run),
        "plan": sdlc_md.read_json(Path(root) / "sdlc-studio" / ".local" / "sprint-plan.json", {}),
        "sprint_goal": rep.get("sprint_goal"), "goal_verdict": rep.get("sprint_goal_verdict"),
        "delivered_points": rep.get("delivered_points"), "spend": rep.get("spend"),
        "sprint_actual_tokens": rep.get("sprint_actual_tokens"),
        "sprint_reviews": sprint_reviews, "review_rounds": review_rounds,
        "filed_in_run": filed, "open_filed_in_run": still_open,
        "carried_issues": _carried_issues(root, retro_id),
        # Named in the checklist so the close can SAY what its window could not
        # judge. An uncalled derivation is a claim nobody can read.
        "undatable_findings": _undatable_findings(Path(root)),
        "retro_validate": _retro_validate(root, retro_id),
    }
    rows = []
    for item in CHECKLIST:
        rows.append({**{k: v for k, v in item.items() if k != "resolver"},
                     **_resolve_item(item, ctx)})
    unmet = [r for r in rows if r["state"] in _OUTSTANDING]
    return {"ok": True, "id": retro_id, "items": rows,
            "expired": [r["id"] for r in rows if r["state"] == EXPIRED],
            "outstanding": [r["id"] for r in unmet if not r.get("discharged_by")],
            "pending_in_close": [r["id"] for r in unmet if r.get("discharged_by") == "close"],
            **_known_issue_rulings(ctx)}


def _known_issue_rulings(ctx: dict) -> dict:
    """The carried stop-ship rulings, split by whether each still holds.

    A finding ruled stop-ship is ANSWERED - the answer is that it stops the ship. It is carried
    separately because a ruling that changes nothing is a note, and the ruling that matters most
    is the one that must be able to stop something.

    Each ruling is re-judged against its finding's CURRENT status, which is the whole of BG0730.
    A finding that has reached a terminal status has had its ruling answered by the work, so it
    is DISCHARGED rather than blocking forever - before this, a ruling outlived its finding and
    blocked every later close with hand-editing a retro the only escape. A finding that cannot be
    read at all still BLOCKS: an id resolving to nothing is a typo or a deletion, and in neither
    case has anybody discharged anything, so releasing it silently would turn a typo into a
    released hold.
    """
    rows = [i for i in (ctx["carried_issues"] or [])
            if i["ok"] and i["ruling"] == retro.STOP_SHIP]
    return {
        "stop_ship": [i["id"] for i in rows if not i.get("terminal")],
        "stop_ship_discharged": [i["id"] for i in rows if i.get("terminal")],
        "stop_ship_unreadable": [i["id"] for i in rows if i.get("unreadable")],
    }


def _window(item: dict) -> str:
    """The last command by which this item could still have been satisfied.

    Defaults to the close: a row that declares no earlier window is one the close itself owns,
    which is the safe direction - the alternative would quietly stop gating anything nobody had
    got round to labelling.
    """
    return str(item.get("window") or CLOSE_WINDOW)


def _expired(item: dict) -> bool:
    """Has this item's window already shut by the time the checklist runs?

    The checklist is composed BY the close, so every window that is not the close's own has
    passed. Nothing else needs to be inspected - a row whose enforcer was `sprint plan` cannot
    be satisfied at a close where the batch has already been delivered.
    """
    return _window(item) != CLOSE_WINDOW


def _resolve_item(item: dict, ctx: dict) -> dict:
    """One row's state, value and detail. A waiver overrides whatever the resolver found, and
    is recorded on the row, so closing without an item and forgetting it are different events
    in the record. An exception is OUTSTANDING, never silently benign."""
    waiver = _waiver_for(ctx["root"], item["id"])
    resolver = globals().get(item["resolver"])
    try:
        state, value, detail = resolver(ctx)
    except Exception as exc:  # noqa: BLE001 - one bad row must not cost the other seventeen
        sdlc_md.debug(f"sprint_report.{item['resolver']}", exc)
        state = NOT_RUN if item["kind"] == STAGE else UNANSWERED
        value, detail = "unresolved", f"{type(exc).__name__}: {exc}"
    if waiver and state in _OUTSTANDING:
        return {"state": WAIVED, "value": value, "detail": detail, "waiver": waiver}
    if state in _OUTSTANDING and _expired(item):
        # REPORTED, not held. The item cannot be satisfied here - its enforcer ran long ago -
        # so refusing the close leaves a waiver as the only exit, and a gate whose only exit is
        # a waiver is a receipt. The command that SHOULD have enforced it goes in the detail,
        # because the actionable fact is where to put the gate, not that it is missing now.
        return {"state": EXPIRED, "value": value, "waiver": None,
                "detail": (f"{detail} - past its window: `{_window(item)}` is the last command "
                           f"that could still have satisfied this, and it has already run"
                           ).strip(" -")}
    return {"state": state, "value": value, "detail": detail, "waiver": None}


def _waiver_for(root: Path, item_id: str) -> str | None:
    try:
        import decisions  # noqa: PLC0415
        return decisions.waiver_for(root, f"{WAIVER_SUBJECT}:{item_id}")
    except Exception as exc:  # noqa: BLE001 - an unreadable log waives nothing
        sdlc_md.debug("sprint_report._waiver_for", exc)
        return None


def _carried_issues(root: Path, retro_id: str) -> list[dict]:
    try:
        path = retro.find_retro(root, retro_id)
        # A retro that cannot be LOCATED is blindness, not an empty table: `find_retro` answers
        # None rather than raising, so returning [] here dressed "we could not look" as "there
        # was nothing to see" one layer above the exception handler.
        # `root` is what lets each row be joined to its artefact's CURRENT status. Without it
        # a stop-ship ruling could never be discharged, so a ruling on a finding that had since
        # been Fixed blocked every later close with hand-editing a retro the only escape.
        return retro.carried_issues(sdlc_md.read_text_safe(path), root=root) if path else None
    except Exception as exc:  # noqa: BLE001
        sdlc_md.debug("sprint_report._carried_issues", exc)
        return None  # unreadable, NOT empty - the caller must be able to tell them apart


def _retro_validate(root: Path, retro_id: str) -> dict:
    try:
        return retro.validate(root, retro_id)
    except Exception as exc:  # noqa: BLE001
        sdlc_md.debug("sprint_report._retro_validate", exc)
        return {}


#: Returned by the verb lookup for a script that ships but exposes no `build_parser()`, so its
#: verbs cannot be enumerated without running it. Distinct from "no such script", because an
#: absence is not an answer: one is a broken row, the other is a row the guard cannot judge,
#: and reporting the second as the first would fail a green tree over the checker's own reach.
UNVERIFIABLE = "unverifiable"


def scope_tail_error(scope: str) -> str | None:
    """Why `scope` names no checklist item, or None when it names one.

    The CONSUMER's own check, published so `decisions.record_waiver` can refuse a waiver that
    covers nothing rather than re-deriving the grammar here - a second reading of it would be a
    copy that drifts, and the copy that drifts is the one that accepts what the consumer
    rejects. Without it `rule:sprint-checklist:not-a-real-item` recorded clean and was read by
    nothing, so the close stayed blocked by an item the log said had been waived: exactly the
    defect the conformance scope check was written for, in the next rule along.
    """
    scope = (scope or "").strip()
    known = [item["id"] for item in CHECKLIST]
    if not scope:
        return (f"a {WAIVER_SUBJECT} waiver must name the item it covers "
                f"({', '.join(known)})")
    if scope not in known:
        return (f"{scope!r} is not a checklist item, so a waiver of it would cover nothing - "
                f"known items: {', '.join(known)}")
    return None


def cycle_drift() -> dict:
    """`{unresolved, uncovered, unverifiable}` - how the checklist and the cycle come apart.

    `unresolved`: a checklist row whose holding command no longer resolves to a shipped script
    and verb, so the row certifies a ceremony that has been renamed or removed.
    `uncovered`: a `sprint` verb that is neither a checklist row's command nor declared
    mechanics, so a stage was added to the cycle and the checklist grew no row for it.
    `unverifiable`: a row whose script ships but publishes no parser to enumerate - reported
    with its reason, never counted as either green or broken.

    The `uncovered` half is what makes this a drift guard rather than a tautology: it is
    derived from the SHIPPED CLI, not from the checklist, so the two can genuinely disagree.

    All THREE buckets are the guard. `unverifiable` was non-empty on the shipped tree and
    asserted by nothing, so two rows were certified unchecked while a caller reading the first
    two saw green; `uncovered` walked `sprint` alone while six rows hold a stage in `critic`,
    `retro`, `lessons` or `handoff`. Both are closed, and the verifier asserts all three.
    """
    scripts = Path(__file__).resolve().parent
    unresolved, unverifiable, verbs_by_script = [], [], {}

    def verbs(script: str):
        if script in verbs_by_script:
            return verbs_by_script[script]
        found = None
        if (scripts / f"{script}.py").is_file():
            found = UNVERIFIABLE
            try:
                mod = importlib.import_module(script)
                if hasattr(mod, "build_parser"):
                    found = set()
                    for action in mod.build_parser()._actions:   # noqa: SLF001 - argparse's own
                        if isinstance(action, argparse._SubParsersAction):  # noqa: SLF001
                            found |= set(action.choices or {})
            except Exception as exc:  # noqa: BLE001 - an unimportable script resolves nothing
                sdlc_md.debug(f"sprint_report.cycle_drift.{script}", exc)
                found = None
        verbs_by_script[script] = found
        return found

    covered: dict[str, set] = {}
    # WINDOWS are checked on the same terms as commands. A row's window names the last command
    # that could still have satisfied it, and a window naming a verb nothing exposes is the same
    # inert-mechanism defect as a command that does - but it was outside this walk entirely, so
    # a window of `sprint totally-not-a-verb` passed every test in the file.
    for item in CHECKLIST:
        win_script, _, win_verb = _window(item).partition(" ")
        if not verbs(win_script):
            unresolved.append(f"{item['id']}: window `{_window(item)}` names no shipped script")
        elif win_verb and win_verb not in verbs(win_script):
            unresolved.append(f"{item['id']}: window `{_window(item)}` names no verb of "
                              f"{win_script}.py")
    for item in CHECKLIST:
        script, _, verb = item["command"].partition(" ")
        if verb:
            covered.setdefault(script, set()).add(verb)
        known = verbs(script)
        if known is None:
            unresolved.append(f"{item['id']}: `{item['command']}` names no shipped script")
        elif known == UNVERIFIABLE:
            unverifiable.append(f"{item['id']}: {script}.py ships but publishes no "
                                f"build_parser(), so `{item['command']}` cannot be checked")
        elif verb and verb not in known:
            unresolved.append(f"{item['id']}: `{item['command']}` names no verb of {script}.py")
    # EVERY script the rows name, not `sprint` alone. Six of the rows hold a stage in `critic`,
    # `retro`, `lessons` or `handoff`, and walking only `sprint` meant a ceremony added to any
    # of those grew no row and nothing said so.
    uncovered = []
    for script in sorted({item["command"].partition(" ")[0] for item in CHECKLIST}):
        known = verbs(script)
        if not isinstance(known, set):
            continue                     # unresolved or unverifiable, already reported above
        extra = known - covered.get(script, set()) - set(NON_CEREMONY_VERBS.get(script, ()))
        uncovered += [f"{script} {v}" for v in sorted(extra)]
    return {"unresolved": unresolved, "uncovered": uncovered, "unverifiable": unverifiable}


def render_checklist(ck: dict) -> str:
    """The checklist as the report's own section. One line per item, state first, because the
    column a reader scans is the one that says whether something happened."""
    lines = ["", "## Sprint checklist", ""]
    for row in ck["items"]:
        mark = {RAN: "ran", ANSWERED: "ok", WAIVED: "WAIVED", EXPIRED: "EXPIRED",
                NOT_RUN: "NOT RUN", UNANSWERED: "UNANSWERED"}[row["state"]]
        line = f"[{mark}] {row['title']}: {row['value']}"
        if row.get("waiver"):
            line += f" (waived by {row['waiver']})"
        lines.append(line)
        if row["detail"]:
            lines.append(f"      {row['detail']}")
    if ck["outstanding"]:
        lines += ["", f"{len(ck['outstanding'])} compulsory item(s) OUTSTANDING: "
                      f"{', '.join(ck['outstanding'])}. The close refuses until each is "
                      f"answered or waived on the record (`decisions.py waive --subject "
                      f"{WAIVER_SUBJECT}:<item> --rationale '<why>'`)."]
    if ck.get("expired"):
        lines += ["", f"{len(ck['expired'])} item(s) PAST THEIR WINDOW, reported and not held: "
                      + "; ".join(f"{r['id']} (enforce at `{_window(r)}`)"
                                  for r in ck["items"] if r["state"] == EXPIRED)
                      + ". Each names the command that should have enforced it - the fix is to "
                        "gate it there, not to waive it here."]
    if ck.get("stop_ship"):
        lines += ["", f"{len(ck['stop_ship'])} carried finding(s) ruled STOP-SHIP: "
                      f"{', '.join(ck['stop_ship'])}. The close refuses: a ruling that cannot "
                      f"stop anything is a note."]
    if ck.get("stop_ship_discharged"):
        lines += ["", f"{len(ck['stop_ship_discharged'])} carried STOP-SHIP ruling(s) "
                      f"DISCHARGED: {', '.join(ck['stop_ship_discharged'])}. Their findings "
                      f"reached a terminal status, so the ruling has been answered by the work "
                      f"rather than by anybody standing it down."]
    if ck.get("stop_ship_unreadable"):
        lines += ["", f"{len(ck['stop_ship_unreadable'])} carried STOP-SHIP ruling(s) name an "
                      f"artefact that cannot be read: "
                      f"{', '.join(ck['stop_ship_unreadable'])}. These still refuse - an id "
                      f"resolving to nothing is a typo or a deletion, and neither discharges "
                      f"anything."]
    if ck.get("pending_in_close"):
        lines += ["", f"{len(ck['pending_in_close'])} item(s) this close will discharge "
                      f"itself: {', '.join(ck['pending_in_close'])}. Reported, not held - a "
                      f"gate whose only exit is the step it blocks is a deadlock."]
    return "\n".join(lines)


def operator_summary(root: Path, retro_id: str, rep: dict | None = None) -> dict:
    """The decision-grade page an operator LEADS from, derived entirely from the record.

    Human-in-the-lead rather than human-in-the-loop: the seats judge at their speed, and the
    operator reads what happened and reverses what they disagree with, at theirs. That only
    works if the summary is a READ of the ledgers - what shipped, what was rejected, what is
    carried and where it is filed, what it cost - and never prose the signing party composes
    about its own decision. A seat writing its own summary is a seat marking its own homework,
    and the operator would be leading from an account with a stake in the answer.

    So every field here comes from `report`, the verdict log and the findings scan. There is NO
    parameter through which anybody's free text reaches this page, which is the property the
    test pins by varying a verdict's `issues` and asserting the summary does not move.

    A component with no record reads UNMEASURED. Omitting it would let a run that measured
    nothing read as a run that cost nothing.
    """
    rep = rep if rep is not None else report(root, retro_id)
    if not rep.get("ok"):
        return {"ok": False, "id": retro_id, "errors": rep.get("errors") or []}
    root = Path(root)
    units = list(rep.get("units") or [])
    run = _run_record(root, units)
    filed, still_open = _open_findings(root, run)
    import critic  # noqa: PLC0415 - deferred, like the report's other ledger reads

    shipped, rejected, reversal = [], [], []
    for uid in units:
        v = critic.verdict_for(root, uid)
        verdict = str((v or {}).get("verdict") or "").upper()
        if verdict == critic.REJECT:
            rejected.append({"unit": uid, "state": critic.repair_state(root, uid)["state"]})
            # A REJECT that was repaired is the single likeliest thing an operator would rule
            # differently: somebody said this was wrong, and somebody else then said the repair
            # answered it. Naming it is what makes leading a bounded act.
            reversal.append({"unit": uid, "why": "rejected, then repaired - the repair was "
                                                 "judged to answer the finding"})
        elif verdict == critic.APPROVE:
            shipped.append({"unit": uid})

    cost = _sprint_cost_line(rep)
    return {
        "ok": True, "id": retro_id, "run_id": (run or {}).get("run_id"),
        "sprint_goal": rep.get("sprint_goal"),
        "goal_verdict": (rep.get("sprint_goal_verdict") or {}).get("verdict"),
        "shipped": shipped,
        "rejected": rejected,
        # CARRIED, with the id it was filed under. "Some findings were carried" is not something
        # an operator can act on; a list of ids is.
        "carried": list(still_open or []),
        "filed": list(filed or []),
        "cost": cost,
        "reversal_candidates": reversal,
    }


def _sprint_cost_line(rep: dict) -> dict:
    """What the sprint cost, or a STATED absence for each component that was not measured.

    EVERY component states its absence, and the test asserts that over `.keys()` rather than
    over a list of field names. An independent seat found this criterion met for two of its four
    components: `tokens` fell back to zero under mutation and `delivered_points` had no absent
    branch at all, so the shipped page rendered `over None points`. The negative test named two
    fields and the positive control only exercises values that are present, so neither could see
    it - LL0013, in a test written to catch this very class one round earlier.

    Nought delivered points is an ANSWER, not an absence: a run whose units all sat at Review
    accepted nothing, and saying UNMEASURED there would hide a real and unwelcome number behind
    a word that means nobody looked. Nought tokens or nought hours cannot be true of a sprint
    that ran, so for those the two collapse.
    """
    vel = rep.get("velocity") or {}
    ov = rep.get("overhead") or {}
    points = rep.get("delivered_points")
    return {
        "tokens": rep.get("sprint_actual_tokens") or UNMEASURED,
        "delivered_points": points if isinstance(points, (int, float)) else UNMEASURED,
        "elapsed_hours": vel.get("elapsed_hours") or UNMEASURED,
        "overhead_ratio": ov.get("ratio") if ov.get("measured") else UNMEASURED,
    }


def render_operator_summary(s: dict) -> str:
    """The summary as a page. Every line is a read; nothing here is composed about anybody."""
    if not s.get("ok"):
        return f"operator summary unavailable: {'; '.join(s.get('errors') or ['unknown'])}"
    lines = [f"# Operator summary - {s['id']}" + (f" ({s['run_id']})" if s.get("run_id") else ""),
             "", f"Sprint goal: {s.get('sprint_goal') or 'none recorded'}",
             f"Goal verdict: {s.get('goal_verdict') or 'unjudged'}", ""]
    lines.append(f"Shipped ({len(s['shipped'])}): " + (", ".join(
        r["unit"] for r in s["shipped"]) or "none"))
    lines.append(f"Rejected ({len(s['rejected'])}): " + (", ".join(
        f"{r['unit']} [{r['state']}]" for r in s["rejected"]) or "none"))
    lines.append(f"Carried, still open: " + (", ".join(s["carried"]) or "none"))
    # FILED was computed, returned and never printed, while the verb's own --help and the
    # changelog both promised "what is carried and where it is filed". A finding raised and
    # closed inside the run reached the dict and never the page - the derivation was right and
    # the operator could not see it, which is the state `critic brief --tier` was in for a whole
    # sprint. Found by an independent seat reading the renderer against the help text.
    lines.append(f"Filed this run: " + (", ".join(s.get("filed") or []) or "none"))
    # DERIVED from the cost line's own keys, so a component added to `_sprint_cost_line`
    # reaches the page. A seat proved the completeness claim true of the dict and false of the
    # page: the derivation asserted over `.keys()` while the renderer hand-enumerated four field
    # names, so a fifth component was computed correctly and silently never printed. An unknown
    # key renders as `<key> <value>` rather than vanishing.
    c = s["cost"]
    lines.append("Cost: " + ", ".join(_COST_PHRASE.get(k, lambda v, k=k: f"{k} {v}")(v)
                                      for k, v in c.items()))
    lines += ["", "What to overturn if you disagree:"]
    lines += [f"  - {r['unit']}: {r['why']}" for r in s["reversal_candidates"]] or ["  - nothing"]
    return "\n".join(lines)


def render(rep: dict) -> str:
    if not rep.get("ok"):
        return f"sprint report {rep['id']}: unavailable ({'; '.join(rep.get('errors', []))})"
    v = rep["velocity"]
    lines = [f"# Sprint report - {rep['id']} ({rep['date']})", ""]
    if rep.get("sprint_goal"):
        gv = rep.get("sprint_goal_verdict")
        judged = (f"{gv['verdict']}" + (f" - {gv['note']}" if gv.get("note") else "")
                  if gv else "not judged (record with `sprint goal-verdict`)")
        lines.append(f"Sprint Goal: {rep['sprint_goal']} [{judged}]")
        for c in (gv or {}).get("clauses") or []:
            # Per clause, because a goal reached in two parts of three is a real outcome and
            # one word cannot express it. Printed under the goal it belongs to, so a reader
            # meets the detail without knowing to look for it.
            lines.append(f"  clause: {c.get('clause', '')} -> {c.get('verdict') or 'not judged'}")
    if not rep["units"]:
        # BG0362: an unreadable Batch line yielded no units and the report then stated the
        # sprint delivered nothing. Zero units is an empty MEASUREMENT presented as a finding -
        # the two readings call for opposite responses (fix the retro, versus explain a sprint
        # that shipped nothing), and the report must not pick the alarming one by default.
        lines.append("Delivered: the Batch field named no unit ids, so what this sprint "
                     "delivered is UNREADABLE, not zero. Name the units individually in the "
                     "retro's `> **Batch:**` field, then re-run.")
    else:
        lines.append(f"Delivered: {len(rep['units'])} unit(s), "
                     f"{rep['delivered_points']} points.")
    lines.extend(_seam_lines(rep))
    lines.extend(_proof_lines(rep))
    # A GREEN UNIT COUNT IS NOT A GOAL. Every unit reaching terminal while the goal was not
    # achieved is the most misreadable state a close can be in - the numbers all look like
    # success - so it is stated in the headline rather than left to be inferred from a verdict
    # printed above it. Silence here is what let a run report completion it had not earned.
    if rep.get("sprint_goal"):
        verdict = ((rep.get("sprint_goal_verdict") or {}).get("verdict") or "").strip().lower()
        if verdict and verdict not in ("achieved", "reached", "met"):
            lines.append(f"  ... and the goal was {verdict}: every unit reached a terminal "
                         f"status, which is not the same as the sprint having done what it "
                         f"set out to do.")
    lines.extend(_delegated_signoff_lines(rep))
    lines.append(_spend_line(rep["spend"], rep.get("sprint_actual_tokens")))
    if v["points_per_elapsed_hour"]:
        lines.append(f"Velocity: {v['points_per_elapsed_hour']} points/elapsed-hour "
                     f"({v['elapsed_hours']}h, {v['elapsed_source']}, ceremony included) - "
                     f"descriptive, never a target.")
    else:
        lines.append("Velocity (points/elapsed-hour): UNMEASURED - supply `--elapsed-hours H`.")
    if v["sprint_tokens_per_point"]:
        lines.append(f"Tokens/point: {v['sprint_tokens_per_point']:,} (sprint total over delivered "
                     f"points, harness-tracked).")
    elif v["tokens_per_point"]:
        lines.append(f"Tokens/point: {v['tokens_per_point']:,} (over rated units).")
    lines.extend(_overhead_lines(rep))
    acc = rep["accuracy"]
    if acc["refused"]:
        lines.append(f"Estimate vs actual: {acc['refused']}")
    elif acc["ratio"]:
        lines.append(f"Estimate vs actual: {acc['ratio']}x (>1 = over-forecast), over "
                     f"{acc['n_measured']} measured unit(s).")
    if acc["models"]:
        lines.append(f"Models: {', '.join(acc['models'])}.")
    lines.extend(_mutation_lines(rep.get("mutation")))
    lines.extend(_execution_lines(rep))
    lines.extend(_waiver_lines(rep))
    if rep.get("checklist"):
        # The checklist IS the report, not a second document beside it. Two close-time
        # documents that both claim to record the run is the drift this repo keeps filing bugs
        # about, so the compulsory set is rendered here rather than in an artefact of its own.
        lines.append(render_checklist(rep["checklist"]))
    lines.append(f"Tickets raised: {', '.join(rep['tickets']) if rep['tickets'] else 'none'}.")
    lines.append(f"Lessons: {len(rep['lessons'])} recorded.")
    fl = rep.get("flow")
    if fl:
        lines.append(f"Flow (schedule axis - measured, feeds no gate): median cycle "
                     f"{fl['median_cycle_days']}d, throughput ~{fl['per_week']}/week "
                     f"over {fl['weeks']} week(s).")
    return "\n".join(lines)


def rendering_enabled(root: Path) -> bool:
    """Whether the report PAGE is drawn. The page only: with it off, json data remains available
    (`show --format json` still returns the whole composed report) and measurement is never gated -
    telemetry keeps recording. A page is a rendering choice; the data and the measurement are not."""
    import config
    val = config.get(root, "report.enabled", True)
    return not (val is False or str(val).strip().lower() in ("false", "0", "no", "off"))


def cmd_show(args: argparse.Namespace) -> int:
    root = Path(args.root)
    # Page versus data: the switch withholds the TEXT PAGE only. `--format json` is exempt by
    # design - json data remains available so a tool or a later read still gets the composed
    # report - and measurement is never gated either way.
    if not rendering_enabled(root) and args.format != "json":
        print("sprint report: text page rendering disabled (report.enabled=false); json data "
              "remains available via `--format json`. Telemetry is unaffected - measurement "
              "keeps recording; re-enable to draw the page.")
        return 0
    rep = report(root, args.id, sprint_tokens=args.tokens, elapsed_hours=args.elapsed_hours)
    print(json.dumps(rep, indent=2) if args.format == "json" else render(rep))
    return 0 if rep.get("ok") else 1


def cmd_operator_summary(args: argparse.Namespace) -> int:
    s = operator_summary(Path(args.root), args.id)
    print(json.dumps(s, indent=2) if args.format == "json" else render_operator_summary(s))
    return 0 if s.get("ok") else 1


def cmd_checklist(args: argparse.Namespace) -> int:
    """The compulsory checklist alone, without the cost and velocity page around it.

    Exits non-zero while any compulsory item is outstanding, so the same command answers "is
    this sprint closeable" for a reader and for the close chain - one authority, not two.
    """
    root = Path(args.root)
    ck = checklist(root, args.id)
    print(json.dumps(ck, indent=2) if args.format == "json" else render_checklist(ck))
    return 1 if (ck["outstanding"] or ck["stop_ship"]) else 0



# =============================================================================================
# THE REPORT OF RECORD
#
# A second, separate artefact from the close report above it: that one is the operator's
# terminal page at the moment of the close; this one is the FILEABLE document a run leaves
# behind - JSON of record, a committed Markdown twin, and an HTML rendering generated on
# demand and never written into the tree (D2a).
#
# Two rules hold the whole thing up, and everything below is machinery for them:
#
#   EVERY FIGURE CARRIES ITS SOURCE. A leaf figure is `{"value", "source"}` and a build whose
#   deriver produced no source REFUSES, naming the figure and its section. Without that the
#   Provenance section's claim - that a disputed number can be re-derived rather than argued -
#   reads as satisfied while being false.
#
#   A SECTION WITH NO DATA SAYS SO BY NAME. `NOT MEASURED` with the reason and the source it
#   could not read, never `0`, `-`, `None` or an empty cell. Separating a measured zero from a
#   measurement nobody took is the one distinction this report exists to preserve.
# =============================================================================================

#: What an unmeasured figure or section READS. A word, in the output, not an absence.
NOT_MEASURED = "NOT MEASURED"
#: What a per-unit token actual reads, under the run-level attribution ruling: the meter is
#: cumulative per session and interleaved work cannot be split between units honestly, so the
#: split is named UNMEASURED rather than divided up.
UNMEASURED = "UNMEASURED"

#: D2a: the JSON is of record, the Markdown twin is committed, the HTML is generated on demand.
D2A = ("D2a: the JSON is the artefact of record and the Markdown twin is committed beside it; "
       "the HTML is generated on demand and never written into the tree, because a "
       "three-hundred-line generated page churns in git on every re-prepare")

REPORTS_REL = "sdlc-studio/reports"


class ReportError(RuntimeError):
    """A report that cannot be built or rendered honestly. Every message names what is missing
    and where, because the caller's next move is to go and look at it."""


def fig(key: str, value, source: str, reason: str | None = None, **extra) -> dict:
    """ONE figure: a value and the source it can be re-derived from.

    Every leaf in the report passes through here, so `source` is never optional by accident.
    A figure that is not measured carries `NOT_MEASURED` as its value, a `reason`, and the
    source it CONSULTED - the reader has to be able to go and look at the thing that had no
    answer, not merely be told there was none.
    """
    out = {"key": key, "value": value, "source": source}
    if reason is not None:
        out["reason"] = reason
    out.update(extra)
    return out


def unmeasured(key: str, source: str, reason: str, **extra) -> dict:
    return fig(key, NOT_MEASURED, source, reason=reason, **extra)


def _section(key: str, title: str, figures: dict | None = None, rows: list | None = None,
             not_measured: dict | None = None) -> dict:
    return {"key": key, "title": title, "figures": figures or {},
            "rows": rows or [], "not_measured": not_measured}


#: Figures the digest does NOT cover, and why. These are the run's own LIFECYCLE - set by the
#: act of closing and sealing rather than derived from the delivered work - so including them
#: would mean the signature changed the fingerprint it had just recorded, and every sealed run
#: would read INVALIDATED from the moment it was signed. Exactly the reason `fingerprint` already
#: excludes the signature block and the generation timestamp. A unit's delivered state is read
#: from the gate PREPARE recorded rather than its status for the same reason: the seal moves
#: statuses.
OUTSIDE_THE_DIGEST = (("goal", "ended_at"), ("goal", "duration_hours"))
#: Whole sections the digest does not cover. The lessons appendix reads the class store, which
#: every later close moves; in the digest, the next run's close would invalidate this signed
#: page. The page still shows the store as the close left it, from the JSON of record. The lane
#: yield reads a per-clone log whose refusals are classed by commits that land later, so it
#: moves for the same reason.
SECTIONS_OUTSIDE_THE_DIGEST = ("lessons", "lane_yield")


def in_the_digest(section: str, key: str) -> bool:
    """Is this figure one the signature is over? One predicate, so what is COMPARED on
    revalidation and what is SIGNED can never be two different sets."""
    return (section not in SECTIONS_OUTSIDE_THE_DIGEST
            and (section, key.split("[", 1)[0]) not in OUTSIDE_THE_DIGEST)


def leaf_figures(report: dict):
    """Every `(section key, figure key, figure)` in the report's figure set, IN ORDER.

    The order is the fingerprint's input, so it is the section list's order, then each
    section's figures in insertion order, then its rows and per-unit rows. A `not_measured`
    marker is a figure too: a section that stops being measured has moved, and a fingerprint that could not see
    that would certify a report whose facts had gone.
    """
    for sec in report.get("sections") or []:
        nm = sec.get("not_measured")
        if nm:
            yield sec["key"], "not_measured", nm
        for key, f in (sec.get("figures") or {}).items():
            yield sec["key"], key, f
        for rows in ("rows", "unit_rows"):
            for i, row in enumerate(sec.get(rows) or []):
                for key, f in row.items():
                    yield sec["key"], f"{key}[{i}]", f


def fingerprint(report: dict) -> str:
    """A digest of the ordered FIGURE SET - not of the JSON file.

    The signature block and the generation timestamp are excluded deliberately. Fingerprinting
    the whole file would mean that signing a report changes the fingerprint the signature just
    recorded, so every sealed run would read INVALIDATED from the moment it was signed.
    """
    payload = [[section, key, f.get("value")] for section, key, f in leaf_figures(report)
               if in_the_digest(section, key)]
    blob = json.dumps(payload, sort_keys=False, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


# --- reading the run's artefacts -------------------------------------------------------------

def _rel(root: Path, path: Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(Path(root).resolve()))
    except ValueError:
        return str(path)


def _run_state_for(root: Path, run_id: str | None) -> tuple[dict, str]:
    """The run record this report describes, and the relative path it was read from."""
    rel = _rel(root, run_state.path(root))
    try:
        live = run_state.read(root) or {}
    except run_state.RunStateError as exc:
        raise ReportError(f"the run record at {rel} could not be read: {exc}") from exc
    if not run_id or sdlc_md.norm_id(str(live.get("run_id") or "")) == sdlc_md.norm_id(run_id):
        if live.get("run_id"):
            return live, rel
    for archived in run_state.archived(root):
        if str(archived.get("run_id") or "") == run_id:
            return archived, _rel(root, run_state.archive_path(root, run_id))
    raise ReportError(f"no run record names {run_id or 'a run'} - looked in {rel} and the "
                      f"run archive beside it")


def _retro_for_run(root: Path, state: dict) -> str:
    """The retro whose Batch names this run's units. The report is keyed by retro because the
    retro is the artefact a close produces; the run record is what it is checked against."""
    want = {sdlc_md.norm_id(u) for u in (state.get("batch") or [])}
    best = None
    for p in sorted((root / "sdlc-studio" / "retros").glob("*.md")):
        if p.name == "_index.md":
            continue
        text = sdlc_md.read_text_safe(p)
        batch = {sdlc_md.norm_id(u.strip())
                 for u in (sdlc_md.extract_field(text, "Batch") or "").split(",") if u.strip()}
        cover = len(batch & want)
        if cover and (best is None or cover > best[0]):
            best = (cover, sdlc_md.any_record_id(p.stem))
    if best is None:
        raise ReportError(f"no retro under sdlc-studio/retros/ names any unit of "
                          f"{state.get('run_id')}'s batch")
    return best[1]


def _table_rows(text: str, header: str) -> list[list[str]]:
    """Every data row of the first table whose header row carries `header` (case-folded).

    Routed through `sdlc_md.iter_tables`, the ONE structural boundary rule every table parser
    in this project shares - a hand-rolled scan re-imports the tallied-into-the-wrong-table
    defect class, and a fenced example table would be read as real rows.
    """
    want = header.lower()
    for table in sdlc_md.iter_tables(text):
        cells = table.get("header") or []
        if want in " | ".join(cells).lower():
            return [[c.strip() for c in row] for _line, row in table.get("rows") or []]
    return []


def _verdict_rows(root: Path, units=None) -> tuple[list[list[str]], str]:
    """The delivery verdict ledger's rows for THIS run's units, and the file they came from.
    Every verdict is a delivery verdict: a historical plan-review ledger is never read.

    The ledgers are PROJECT-WIDE and append-only: read whole they carry a year of other runs'
    verdicts. Unscoped, this repository's own report read 185 rejected units out of a batch of
    23 and printed a rework rate of 804% - measured, not imagined, on the first run against the
    real tree. `units` is the run's batch; None keeps every row, for a caller that wants the
    whole file and says so.
    """
    p = root / "sdlc-studio" / "reviews" / "critic-verdicts.md"
    rel = _rel(root, p)
    if not p.is_file():
        return [], rel
    rows = _table_rows(sdlc_md.read_text_safe(p), "Unit | Verdict")
    if units is None:
        return rows, rel
    want = {sdlc_md.norm_id(u) for u in units}
    return [r for r in rows if r and sdlc_md.norm_id(r[0]) in want], rel


# --- the forge, and the git history behind it ------------------------------------------------

#: Where a `gh run list --json ...` answer is cached for this run. The report reads the cache
#: when it is there and asks the forge when it is not, so a report can be rebuilt offline from
#: the same data it was first built from - which is what makes re-derivation a check rather
#: than a second network call with a different answer.
CI_RUNS_REL = "sdlc-studio/.local/ci-runs.json"
_CI_FIELDS = "databaseId,event,conclusion,headBranch,headSha,workflowName,createdAt,updatedAt"


def _ci_runs(root: Path) -> tuple[list[dict], str]:
    """Every CI run this clone can see, and the source they were read from."""
    cached = root / CI_RUNS_REL
    if cached.is_file():
        try:
            rows = json.loads(cached.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            rows = []
        return ([r for r in rows if isinstance(r, dict)], CI_RUNS_REL)
    if shutil.which("gh") is None:
        return [], "gh run list"
    try:
        proc = subprocess.run(["gh", "run", "list", "--limit", "100", "--json", _CI_FIELDS],
                              capture_output=True, text=True, cwd=str(root), timeout=30)
        rows = json.loads(proc.stdout or "[]") if proc.returncode == 0 else []
    except (OSError, ValueError, subprocess.SubprocessError):
        rows = []
    rows = [r for r in rows if isinstance(r, dict)]
    # WRITE THE CACHE. Nothing wrote it, so every read went to the live forge - and a forge
    # answer is time-varying and page-truncated, which makes the guardrail and all four DORA
    # keys move on a tree nobody touched. A report is supposed to re-derive from the same data
    # it was first built from; without this it re-derives from a second network call with a
    # different answer, which is the thing the fragment claims is avoided. Best-effort: a clone
    # that cannot write its own `.local/` still gets its figures, just not the stability.
    if rows:
        try:
            cached.parent.mkdir(parents=True, exist_ok=True)
            cached.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
        except OSError as exc:
            sdlc_md.debug("sprint_report.ci_runs.cache", exc)
    return (rows, "gh run list")


def _at(value) -> "datetime | None":
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None


def _in_window(stamp, start, end) -> bool:
    """Is `stamp` inside the run window `[start, end)`?

    HALF-OPEN. The end is the page's generation instant (or the run's end, when that came
    first), and both it and every commit or CI stamp are read to the second. Anything stamped
    in the end's own second is therefore at or after the moment the page was derived - the
    commit that files the page, the CI run its push triggers - and with the end inclusive it
    entered the re-derivation alone, so `check` read INVALID on a page nobody touched.
    Excluding that second at derivation and re-derivation alike keeps the two the same.
    """
    at = _at(stamp)
    if at is None or start is None:
        return False
    return at >= start and (end is None or at < end)


def _git_commits(root: Path, start, end) -> list[tuple[str, "datetime"]]:
    """`(sha, committed at)` for every commit inside the run's window, oldest first."""
    try:
        proc = subprocess.run(["git", "log", "--format=%H%x09%cI"], capture_output=True,
                              text=True, cwd=str(root), timeout=30)
    except (OSError, subprocess.SubprocessError):
        return []
    if proc.returncode != 0:
        return []
    out = []
    for line in (proc.stdout or "").splitlines():
        sha, _, stamp = line.partition("\t")
        if _in_window(stamp, start, end):
            out.append((sha, _at(stamp)))
    return sorted(out, key=lambda r: r[1])


def _hms(seconds: float) -> str:
    total = int(seconds)
    return f"{total // 3600}h {total % 3600 // 60}m"


#: A deployment in THIS project, stated rather than assumed. The report prints the sentence
#: beside every DORA figure, because a figure whose definition is unstated cannot be compared
#: with anyone else's - and an unmeasured key printed as 0% against an elite band of 0-15%
#: reads as the best possible result.
DEPLOY_MAPPING = ("a push to main IS the deployment in this trunk-based repository: there is no "
                  "separate deploy step, and CI on that commit is what decides whether the "
                  "change stood up")
_NO_FORGE = "no forge run data"


def _dora_rows(root: Path, start, end) -> list[dict]:
    """The four keys, each with its value, this project's mapping, the elite band and a source.

    Deployment frequency and change failure rate count PUSH-TRIGGERED runs alone. Counting
    every run in the window would let a `workflow_dispatch` or a schedule stand as a
    deployment, which is not a change reaching the trunk, and the rate it produces is a
    different number about a different thing.
    """
    runs, ci_source = _ci_runs(root)
    windowed = [r for r in runs if _in_window(r.get("createdAt"), start, end)]
    pushes = [r for r in windowed if str(r.get("event") or "") == "push"]
    failed = [r for r in pushes if str(r.get("conclusion") or "").lower() not in ("success", "")]
    ids = "/".join(str(r.get("databaseId")) for r in pushes)

    def forge(detail: str) -> str:
        return f"forge runs {ids} - {detail}" if ids else f"forge runs (none readable); {detail}"

    rows: list[dict] = []
    if pushes:
        rows.append({"dora_key": fig("dora_key", "Deployment frequency", ci_source),
                     "dora_value": fig("dora_value", len(pushes), ci_source),
                     "dora_mapping": fig("dora_mapping", DEPLOY_MAPPING, ci_source),
                     "dora_band": fig("dora_band", "on demand", ci_source),
                     "dora_source": fig("dora_source", forge(
                         f"{len(pushes)} push-triggered run(s) on main in the run window"),
                         ci_source)})
    else:
        commits = _git_commits(root, start, end)
        mapping = (DEPLOY_MAPPING + "; with no forge run data a deployment is counted as a "
                                    "commit on main inside the run window")
        if commits:
            rows.append({"dora_key": fig("dora_key", "Deployment frequency", "git log"),
                         "dora_value": fig("dora_value", len(commits), "git log"),
                         "dora_mapping": fig("dora_mapping", mapping, "git log"),
                         "dora_band": fig("dora_band", "on demand", "git log"),
                         "dora_source": fig("dora_source",
                                            f"git history - {len(commits)} commit(s) on main "
                                            f"inside the run window", "git log")})
        else:
            rows.append({"dora_key": fig("dora_key", "Deployment frequency", "git log"),
                         "dora_value": unmeasured("dora_value", "git log", _NO_FORGE),
                         "dora_mapping": fig("dora_mapping", mapping, "git log"),
                         "dora_band": fig("dora_band", "on demand", "git log"),
                         "dora_source": fig("dora_source", "git history - no commit inside the "
                                                           "run window", "git log")})

    lead_map = ("the span from the run's first commit on main to its last - per-commit lead "
                "time is not derived, because the work is committed locally and pushed in "
                "batches")
    commits = _git_commits(root, start, end)
    if len(commits) >= 2:
        span = _hms((commits[-1][1] - commits[0][1]).total_seconds())
        rows.append({"dora_key": fig("dora_key", "Lead time for changes", "git log"),
                     "dora_value": fig("dora_value", span, "git log"),
                     "dora_mapping": fig("dora_mapping", lead_map, "git log"),
                     "dora_band": fig("dora_band", "under a day", "git log"),
                     "dora_source": fig("dora_source", f"git history - first to last of "
                                                       f"{len(commits)} commit(s)", "git log")})
    elif len(pushes) >= 2:
        first, last = _at(pushes[0].get("createdAt")), _at(pushes[-1].get("createdAt"))
        rows.append({"dora_key": fig("dora_key", "Lead time for changes", ci_source),
                     "dora_value": fig("dora_value", _hms((last - first).total_seconds()),
                                       ci_source),
                     "dora_mapping": fig("dora_mapping", lead_map, ci_source),
                     "dora_band": fig("dora_band", "under a day", ci_source),
                     "dora_source": fig("dora_source",
                                        forge("first to last push-triggered run"), ci_source)})
    else:
        rows.append({"dora_key": fig("dora_key", "Lead time for changes", ci_source),
                     "dora_value": unmeasured("dora_value", ci_source, _NO_FORGE),
                     "dora_mapping": fig("dora_mapping", lead_map, ci_source),
                     "dora_band": fig("dora_band", "under a day", ci_source),
                     "dora_source": fig("dora_source", "no commit and no push-triggered run "
                                                       "inside the run window", ci_source)})

    cfr_map = (DEPLOY_MAPPING + "; the rate is the share of push-triggered CI runs on main "
                                "that did not conclude success")
    if pushes:
        pct = f"{round(100 * len(failed) / len(pushes))}%"
        shas = "/".join(str(r.get("headSha") or "?") for r in failed) or "none"
        rows.append({"dora_key": fig("dora_key", "Change failure rate", ci_source),
                     "dora_value": fig("dora_value", pct, ci_source),
                     "dora_mapping": fig("dora_mapping", cfr_map, ci_source),
                     "dora_band": fig("dora_band", "0-15%", ci_source),
                     "dora_source": fig("dora_source", forge(
                         f"{len(pushes)} deployment(s); {len(failed)} failed on {shas}"),
                         ci_source)})
    else:
        rows.append({"dora_key": fig("dora_key", "Change failure rate", ci_source),
                     "dora_value": unmeasured("dora_value", ci_source, _NO_FORGE),
                     "dora_mapping": fig("dora_mapping", cfr_map, ci_source),
                     "dora_band": fig("dora_band", "0-15%", ci_source),
                     "dora_source": fig("dora_source", "no push-triggered CI run is readable "
                                                       "for this run window", ci_source)})

    restore_map = ("the span from a push-triggered run concluding failure on main to the next "
                   "push-triggered run concluding success")
    restored = None
    for i, run in enumerate(pushes):
        if run in failed:
            for later in pushes[i + 1:]:
                if str(later.get("conclusion") or "").lower() == "success":
                    red, green = _at(run.get("updatedAt")), _at(later.get("updatedAt"))
                    if red and green:
                        restored = (_hms((green - red).total_seconds()), run, later)
                    break
            break
    if restored:
        span, red, green = restored
        rows.append({"dora_key": fig("dora_key", "Time to restore", ci_source),
                     "dora_value": fig("dora_value", span, ci_source),
                     "dora_mapping": fig("dora_mapping", restore_map, ci_source),
                     "dora_band": fig("dora_band", "under an hour", ci_source),
                     "dora_source": fig("dora_source",
                                        f"forge runs {red.get('databaseId')}/"
                                        f"{green.get('databaseId')} - red then green on main",
                                        ci_source)})
    elif pushes and not failed:
        rows.append({"dora_key": fig("dora_key", "Time to restore", ci_source),
                     "dora_value": fig("dora_value", "no restore needed", ci_source),
                     "dora_mapping": fig("dora_mapping", restore_map, ci_source),
                     "dora_band": fig("dora_band", "under an hour", ci_source),
                     "dora_source": fig("dora_source", forge("no push-triggered run on main "
                                                            "concluded failure"), ci_source)})
    else:
        rows.append({"dora_key": fig("dora_key", "Time to restore", ci_source),
                     "dora_value": unmeasured("dora_value", ci_source, _NO_FORGE),
                     "dora_mapping": fig("dora_mapping", restore_map, ci_source),
                     "dora_band": fig("dora_band", "under an hour", ci_source),
                     "dora_source": fig("dora_source", "no push-triggered CI run is readable "
                                                       "for this run window", ci_source)})
    return rows


# --- building the report ----------------------------------------------------------------------
#
# ONE PAGE, THREE QUESTIONS. The front page is the goal, then how accurate the estimates were,
# whether the run delivered to plan and which known issues it hands over, then the sign line.
# Tokens by model, DORA, calibration, rulings and waivers are appendix. The run state carries
# the plan snapshot, the per-unit actuals, the close's own known-issue gaps and the rulings; each
# is read where it is present and reads NOT MEASURED where it is not, never 0.

#: The report schema. A page filed under another schema cannot be re-derived by this builder,
#: and `revalidate` says so rather than reporting every figure as moved.
SCHEMA = 2
#: The front page, in order, and the appendix beneath it.
FRONT_PAGE = ("goal", "estimates", "delivered", "known_issues", "signoff")
APPENDIX = ("cost", "dora", "calibration", "rulings", "waivers", "lane_yield", "lessons")


def _num(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _review_rounds(root: Path, uid: str, ledger: list[list[str]], found: bool,
                   state: dict | None = None) -> int | None:
    """A unit's delivery review rounds: `critic.review_rounds` where it exists, else the unit's
    rows in the verdict ledger, one row per recorded round. None when there is no ledger to
    count: no ledger is not zero rounds, whichever route would have counted them."""
    if not found:
        return None
    try:
        import critic  # noqa: PLC0415 - deferred sibling, as elsewhere in this module
        counter = getattr(critic, "review_rounds", None)
        if callable(counter):
            return int(counter(root, uid, state=state))
    except Exception as exc:  # noqa: BLE001 - fall back to the ledger rather than fail the page
        sdlc_md.debug("sprint_report._review_rounds", exc)
    return sum(1 for r in ledger if r and sdlc_md.norm_id(r[0]) == uid)


def _unit_ledger(root: Path, state: dict, state_rel: str) -> list[dict]:
    """One entry per unit the run planned, added or dropped: plan order, then added order.

    Planned points come from the plan snapshot, never the unit file: a unit resized from 3 to 8
    after approval was planned at 3, and reading the file erases the very error this page shows.
    Delivered means the terminal gate PREPARE recorded, when it recorded one - the seal moves
    statuses, so reading a status would change the page the signature froze - else a terminal
    status on disk.
    """
    snap = {sdlc_md.norm_id(k): v
            for k, v in ((state.get("plan_snapshot") or {}).get("units") or {}).items()
            if isinstance(v, dict)}
    actuals = {sdlc_md.norm_id(k): v for k, v in (state.get("unit_actuals") or {}).items()
               if isinstance(v, dict)}
    changes = {sdlc_md.norm_id(c.get("id") or ""): c for c in state.get("batch_changes") or []
               if isinstance(c, dict) and c.get("id") and not c.get("note")
               and c.get("action") in ("drop", "add")}
    planned = ([u for u, v in snap.items() if not v.get("added")] if snap
               else _planned_ids(state))
    added = [u for u, v in snap.items() if v.get("added")] + \
        [u for u, c in changes.items() if c.get("action") == "add"]
    order = list(dict.fromkeys(planned + added
                               + [sdlc_md.norm_id(u) for u in state.get("batch") or []]))
    gate_clear = state.get("report_gate_clear")
    cleared = {sdlc_md.norm_id(u) for u in gate_clear or []}
    ledger, ledger_rel = _verdict_rows(root, order)
    ledger_found = (root / ledger_rel).is_file()
    out = []
    for uid in order:
        found = sdlc_md.find_by_id(root, uid)
        path = Path(found[0]) if found else None
        change = changes.get(uid) or {}
        dropped = change.get("action") == "drop"
        delivered = (False if dropped else uid in cleared if gate_clear is not None
                     else _terminal(root, uid)[1])
        plan, act = snap.get(uid) or {}, actuals.get(uid) or {}
        out.append({
            "id": uid, "rel": _rel(root, path) if path else state_rel,
            "planned": uid in planned, "added": uid not in planned and uid in added,
            "dropped": dropped, "reason": (change.get("reason") or "").strip(),
            "delivered": delivered, "carried": not dropped and not delivered,
            "points": sdlc_md.read_points(sdlc_md.read_text_safe(path)) if path else None,
            "planned_points": plan.get("planned_points"),
            "forecast_minutes": plan.get("forecast_minutes"),
            "forecast_tokens": plan.get("forecast_tokens"),
            "minutes": act.get("minutes"), "tokens": act.get("tokens"),
            "in_plan": bool(plan), "measured": bool(act),
            "rounds": _review_rounds(root, uid, ledger, ledger_found, state),
            "rounds_rel": ledger_rel})
    return out


def _paired(units: list[dict], fkey: str, akey: str) -> tuple:
    """`(forecast, actual, basis)` summed like for like: over the units carrying both halves,
    or - when none does - each half over the units carrying it, so one missing half still
    shows the other."""
    both = [u for u in units if _num(u[fkey]) and _num(u[akey])]
    if both:
        return (sum(u[fkey] for u in both), sum(u[akey] for u in both),
                f"{len(both)} of {len(units)} delivered unit(s)")
    fs = [u[fkey] for u in units if _num(u[fkey])]
    acts = [u[akey] for u in units if _num(u[akey])]
    return (sum(fs) if fs else None, sum(acts) if acts else None,
            f"{len(units)} delivered unit(s)")


def _estimate_row(measure: str, forecast, actual, basis: str, src: str,
                  why_forecast: str, why_actual: str) -> dict:
    if _num(forecast) and isinstance(forecast, float):
        forecast = round(forecast, 1)
    if _num(actual) and isinstance(actual, float):
        actual = round(actual, 1)
    ok = _num(forecast) and _num(actual) and forecast
    return {
        "est_measure": fig("est_measure", measure, src),
        "est_forecast": (fig("est_forecast", forecast, src) if _num(forecast)
                         else unmeasured("est_forecast", src, why_forecast)),
        "est_actual": (fig("est_actual", actual, src) if _num(actual)
                       else unmeasured("est_actual", src, why_actual)),
        "est_ratio": (fig("est_ratio", f"{round(actual / forecast, 2)}x", src) if ok
                      else unmeasured("est_ratio", src, "needs both a forecast and an actual")),
        "est_basis": fig("est_basis", basis, src)}


def _estimates_section(state: dict, state_rel: str, ledger: list[dict], run_tokens,
                       span_minutes) -> dict:
    """Forecast, actual and actual over forecast. Points over the units the run delivered;
    minutes and tokens over the WHOLE run - its span and its meter - because units open at the
    same time share their hours and tokens, so the per-unit figures beneath overlap and summing
    them over-counts the run."""
    delivered = [u for u in ledger if u["delivered"]]
    no_plan = "no plan snapshot is recorded"
    f, a, basis = _paired(delivered, "planned_points", "points")
    rows = [_estimate_row(
        "Points", f, a, basis, state_rel,
        no_plan if not any(u["in_plan"] for u in ledger) else
        "no delivered unit" if not delivered else "no delivered unit is in the plan snapshot",
        "no delivered unit carries Points" if delivered else "no delivered unit")]
    live = [u for u in ledger if not u["dropped"]]

    def forecast(key):
        vals = [u[key] for u in live if _num(u[key])]
        return (sum(vals) if vals else None,
                f"the whole run: forecast over {len(vals)} of {len(live)} unit(s) planned or "
                f"added and not dropped")
    f, over = forecast("forecast_minutes")
    rows.append(_estimate_row("Minutes", f, span_minutes,
                              f"{over}; forecast is active work minutes per point, actual is the run's "
                              "wall-clock span, start to end, so waiting counts", state_rel,
                              no_plan if not any(u["in_plan"] for u in ledger) else
                              "the plan recorded no minute forecast for any unit",
                              "the run records no start time"))
    f, over = forecast("forecast_tokens")
    if f is None:
        legacy = state.get("token_forecast", state.get("forecast_tokens"))
        f = legacy if _num(legacy) else None
        if f is not None:
            over = "the whole run: the plan's run-level token forecast"
    tokens = run_tokens.get("tokens")
    # Delegated agents' reported totals are real spend the main-thread meter cannot see: a run
    # that fans its work out would otherwise read a fraction of its cost.
    delegated = run_state.delegated_total(state)
    agents = len([r for r in (state.get(run_state.DELEGATED) or []) if isinstance(r, dict)])
    basis = f"{over}; actual is the run meter, a lower bound"
    if tokens and delegated:
        basis = (f"{over}; actual is the main-thread meter plus {agents} delegated agent(s)' "
                 f"reported totals, split in the appendix")
        tokens += delegated
    rows.append(_estimate_row(
        "Tokens", f, tokens or None, basis,
        state_rel, "no token forecast is recorded",
        run_tokens.get("reason") or ("the run meter read no spend between its readings"
                                     if tokens == 0 else "no token actual was recorded")))

    def cell(key, value, why):
        if _num(value):
            return fig(key, round(value, 1) if isinstance(value, float) else value, state_rel)
        return unmeasured(key, state_rel, why)
    unit_rows = [{"unit_id": fig("unit_id", u["id"], u["rel"]),
                  "eu_forecast_minutes": cell("eu_forecast_minutes", u["forecast_minutes"],
                                              "not in the plan"),
                  "eu_minutes": cell("eu_minutes", u["minutes"], "not recorded"),
                  "eu_forecast_tokens": cell("eu_forecast_tokens", u["forecast_tokens"],
                                             "not in the plan"),
                  "eu_tokens": cell("eu_tokens", u["tokens"], "not recorded")}
                 for u in ledger if not u["dropped"] and (u["in_plan"] or u["measured"])]
    if not any(_num(u[k]) for u in ledger for k in ("forecast_minutes", "minutes",
                                                    "forecast_tokens", "tokens")):
        unit_rows = []   # nothing measured per unit: a row of NOT MEASURED each says nothing
    sec = _section("estimates", "Estimates", rows=rows)
    sec["unit_rows"] = unit_rows
    return sec


def _delivered_section(root: Path, state_rel: str, ledger: list[dict]) -> dict:
    """What the plan committed to against what of it was delivered, at PLANNED size, with the
    units added mid-run counted beside the plan and never inside it: two of four planned units
    plus one added is not three delivered against four."""
    snapped = any(u["in_plan"] for u in ledger)

    def at_plan_size(key: str, units: list[dict]) -> dict:
        missing = [u["id"] for u in units if not _num(u["planned_points"])]
        if not units:
            return fig(key, 0, state_rel)
        if not snapped:
            return unmeasured(key, state_rel, "no plan snapshot is recorded, so the planned "
                                              "size is unknown")
        if missing:
            return unmeasured(key, state_rel, f"not in the plan snapshot: {', '.join(missing)}")
        return fig(key, sum(u["planned_points"] for u in units), state_rel)
    planned = [u for u in ledger if u["planned"]]
    added = [u for u in ledger if u["added"]]
    groups = {"planned": planned, "plan_delivered": [u for u in planned if u["delivered"]],
              "added_delivered": [u for u in added if u["delivered"]],
              "dropped": [u for u in ledger if u["dropped"]],
              "carried": [u for u in ledger if u["carried"]]}
    figures = {}
    for name, units in groups.items():
        figures[f"{name}_units"] = fig(f"{name}_units", len(units), state_rel)
        pkey = "added_points" if name == "added_delivered" else f"{name}_points"
        figures[pkey] = at_plan_size(pkey, units)
    figures["added_units"] = fig("added_units", len(added), state_rel)
    delivered = [u for u in ledger if u["delivered"]]
    unsized = [u["id"] for u in delivered if not _num(u["points"])]
    figures["points_delivered"] = (
        unmeasured("points_delivered", state_rel, "no unit was delivered") if not delivered else
        unmeasured("points_delivered", state_rel, f"{len(unsized)} delivered unit(s) carry no "
                                                  f"Points: {', '.join(unsized)}") if unsized
        else fig("points_delivered", sum(u["points"] for u in delivered),
                 ", ".join(u["rel"] for u in delivered)))
    rows = []
    for u in ledger:
        why = u["reason"] or "no reason recorded"
        done = "delivered" if u["delivered"] else "carried, not delivered"
        outcome = (f"dropped - {why}" if u["dropped"] else
                   f"added - {why}; {done}" if u["added"] else
                   f"carried - {why}" if u["carried"] else done)
        rows.append({
            "unit_id": fig("unit_id", u["id"], u["rel"]),
            "unit_planned_points": (fig("unit_planned_points", u["planned_points"], state_rel)
                                    if _num(u["planned_points"]) else
                                    unmeasured("unit_planned_points", state_rel,
                                               "not in the plan snapshot" if any(
                                                   v["in_plan"] for v in ledger)
                                               else "no plan snapshot")),
            "unit_points": (fig("unit_points", u["points"], u["rel"]) if _num(u["points"])
                            else unmeasured("unit_points", u["rel"], "no Points on the unit")),
            "unit_outcome": fig("unit_outcome", outcome, state_rel),
            "unit_rounds": (fig("unit_rounds", u["rounds"], u["rounds_rel"])
                            if u["rounds"] is not None else
                            unmeasured("unit_rounds", u["rounds_rel"],
                                       f"no verdict ledger at {u['rounds_rel']}"))})
    return _section("delivered", "Delivered to plan", figures, rows)


def _priority_rank(priority: str) -> int:
    """Most severe first, in `critic`'s tiers, so a change request's P0-P4 ranks beside a bug's
    severity: P0 with Critical, P1 with High, P2 with Medium, P3 with Low. Anything else,
    P4 included, sorts after Low."""
    import critic  # noqa: PLC0415 - deferred sibling, as elsewhere in this module
    word = critic._normalise_priority(priority)
    return next((rank for rank, tier in enumerate(critic.PRIORITY_TIERS) if word in tier),
                len(critic.PRIORITY_TIERS))


def _finding_row(root: Path, uid: str) -> tuple[int, dict]:
    found = sdlc_md.find_by_id(root, uid)
    path = Path(found[0]) if found else None
    text = sdlc_md.read_text_safe(path) if path else ""
    rel = _rel(root, path) if path else "sdlc-studio/bugs"
    priority = (sdlc_md.extract_field(text, "Severity")
                or sdlc_md.extract_field(text, "Priority") or "").strip()
    head = re.search(r"(?m)^#\s+[^:\n]+:\s*(.+)$", text)
    rank = _priority_rank(priority)
    return rank, {"issue_id": fig("issue_id", uid, rel),
                  "issue_priority": (fig("issue_priority", priority, rel) if priority else
                                     unmeasured("issue_priority", rel, "no priority recorded")),
                  "issue_detail": fig("issue_detail",
                                      head.group(1).strip() if head else uid, rel)}


def _known_issues_section(root: Path, state: dict, state_rel: str, ledger: list[dict],
                          start: str | None, end: str | None) -> dict:
    """STOP-SHIP rulings the close recorded, first and marked, so the signer cannot miss one;
    then open findings raised inside the run's window, most severe first; then the other gaps
    the close recorded; then the units carried undelivered."""
    _filed, still_open = _open_findings(root, {"started_at": start, "ended_at": end})
    ranked = sorted((_finding_row(root, uid) for uid in still_open or []),
                    key=lambda pair: (pair[0], pair[1]["issue_id"]["value"]))
    gaps = state.get("close_known_issues")
    gap_rows = [({"issue_id": fig("issue_id", str(gap.get("source") or "close"), state_rel),
                  "issue_priority": fig("issue_priority",
                                        "STOP-SHIP" if gap.get("stop_ship") else "close gap",
                                        state_rel),
                  "issue_detail": fig("issue_detail",
                                      str(gap.get("detail") or "no detail recorded"),
                                      state_rel)}, bool(gap.get("stop_ship")))
                for gap in gaps or [] if isinstance(gap, dict)]
    rows = ([row for row, stop in gap_rows if stop] + [row for _rank, row in ranked]
            + [row for row, stop in gap_rows if not stop])
    carried = [u for u in ledger if not u["dropped"] and not u["delivered"]]
    for u in carried:
        rows.append({"issue_id": fig("issue_id", u["id"], u["rel"]),
                     "issue_priority": fig("issue_priority", "carried unit", state_rel),
                     "issue_detail": fig("issue_detail",
                                         f"{'added' if u['added'] else 'planned'} and not "
                                         f"delivered by this run", state_rel)})
    scan = (unmeasured("findings_scan", state_rel,
                       "the run records no start time, so no finding can be placed in it")
            if still_open is None else
            fig("findings_scan", f"{len(still_open)} open finding(s) raised in the run, "
                                 + (f"{len(gaps)} close gap(s)" if isinstance(gaps, list)
                                    else "close gaps not recorded")
                                 + f", {len(carried)} carried unit(s)", state_rel))
    return _section("known_issues", "Known issues handed over", {"findings_scan": scan}, rows)


def _model_of(stamps: list[dict]) -> str:
    models = sorted({str(s["model"]) for s in stamps if s.get("model")})
    return (models[0] if len(models) == 1 else
            run_state.SESSION_MODEL_MIXED if models else retro.MODEL_UNRECORDED)


def _cost_section(state: dict, state_rel: str, total: dict) -> dict:
    """Tokens by model, from the meter stamps, and the delegated spend beside them."""
    delegated = run_state.delegated_total(state)
    figures = {"tokens_delegated": (
        fig("tokens_delegated", delegated, state_rel) if delegated else
        unmeasured("tokens_delegated", state_rel,
                   "no delegated agent supplied a total, which is not the same fact as no "
                   "work having been delegated"))}
    if total.get("tokens") is None:
        return _section("cost", "Tokens by model", figures, not_measured=unmeasured(
            "cost", state_rel, total.get("reason") or "the session meter could not be read"))
    stamps = [s for s in (state.get(run_state.TOKEN_STAMPS) or []) if isinstance(s, dict)]
    sessions: dict[str, list[dict]] = {}
    for s in stamps:
        sessions.setdefault(str(s.get("source")), []).append(s)
    by_model: dict[str, list[dict]] = {}
    for rows in sessions.values():
        by_model.setdefault(_model_of(rows), []).extend(rows)
    rows = []
    for model, model_stamps in sorted(by_model.items()):
        # Each model's total goes through the same summing rule as the run's own total, so the
        # rows add up to it.
        sub = run_state.run_token_total({**state, run_state.TOKEN_STAMPS: model_stamps})
        if sub.get("tokens"):
            rows.append({"model_name": fig("model_name", model, state_rel),
                         "model_tokens": fig("model_tokens", sub["tokens"], state_rel)})
    if not rows:
        rows = [{"model_name": fig("model_name", total.get("model") or retro.MODEL_UNRECORDED,
                                   state_rel),
                 "model_tokens": fig("model_tokens", total["tokens"], state_rel)}]
    uncovered = total.get("uncovered") or []
    coverage = f"{total['session_count']} session(s)" + (
        f"; {len(uncovered)} session(s) wrote to the run with no closing stamp and are NOT in "
        f"this total: {', '.join(uncovered)}" if uncovered else "")
    figures.update({
        "tokens_total": fig("tokens_total", total["tokens"] + delegated, state_rel),
        "token_coverage": fig("token_coverage", coverage, state_rel),
        "token_shape": fig("token_shape", f"read from {total['shape']}", state_rel)})
    return _section("cost", "Tokens by model", figures, rows)


def _calibration_section(state: dict, state_rel: str) -> dict:
    """The rates the plan was estimated from, and where each came from."""
    rates = (state.get("plan_snapshot") or {}).get("rates") or {}
    figures = {}
    for key, name in (("tokens_per_point", "cal_tokens"), ("minutes_per_point", "cal_minutes")):
        rate = rates.get(key) if isinstance(rates.get(key), dict) else {}
        figures[f"{name}_per_point"] = (
            fig(f"{name}_per_point", rate["value"], state_rel) if _num(rate.get("value")) else
            unmeasured(f"{name}_per_point", state_rel, "the plan snapshot records no rate"))
        figures[f"{name}_source"] = fig(f"{name}_source",
                                        str(rate.get("source") or "none recorded"), state_rel)
    return _section("calibration", "Calibration", figures)


def _rulings_section(state: dict, state_rel: str) -> dict:
    """How many questions a persona seat settled, and how many reached the operator."""
    recs = state.get("rulings")
    if not isinstance(recs, list):
        return _section("rulings", "Rulings", not_measured=unmeasured(
            "rulings", state_rel, "the run records no rulings"))
    recs = [r for r in recs if isinstance(r, dict)]
    return _section("rulings", "Rulings", {
        "persona_rulings": fig("persona_rulings",
                               sum(1 for r in recs if r.get("by") == "persona"), state_rel),
        "cited_rulings": fig("cited_rulings",
                             sum(1 for r in recs if r.get("kind") == "cited"), state_rel),
        "operator_rulings": fig("operator_rulings",
                                sum(1 for r in recs if r.get("by") == "operator"), state_rel)})


def _dora_section(root: Path, start, end) -> dict:
    rows = _dora_rows(root, start, end)
    if all(r["dora_value"]["value"] == NOT_MEASURED for r in rows):
        return _section("dora", "DORA", not_measured=unmeasured(
            "dora", _ci_runs(root)[1],
            f"{_NO_FORGE} and no commit on main inside the run window"))
    return _section("dora", "DORA", rows=rows)


def _iso(moment) -> str | None:
    return moment.isoformat().replace("+00:00", "Z") if moment else None


def build_report(root, retro_id: str, as_of: str | None = None,
                 window_end: str | None = None, run_id: str | None = None) -> dict:
    """The report of record for `retro_id`'s run: every figure derived, every figure sourced.

    Read-only. Raises `ReportError` when the run cannot be reported honestly - no sprint goal
    recorded, no run record, a figure whose deriver produced no source. `run_id` names an
    archived run to re-derive; unset, the live run is reported.

    THE WINDOW IS CLOSED AND CARRIED. `ended_at` is None until the seal and written by it, so
    an open run is bounded at the page's generation time, and the resolved end is recorded on
    the report and replayed on every re-derivation - otherwise signing would widen the window,
    move the figures and invalidate the page it had just signed.
    """
    root = Path(root)
    state, state_rel = _run_state_for(root, run_id)
    generated_at = as_of or sdlc_md.now_iso8601()
    start = _at(state.get("started_at"))
    end = (_at(window_end) if window_end else
           (_at(state.get("ended_at")) or _at(generated_at)))
    goal = state.get("sprint_goal") or state.get("goal")
    if not goal or not str(goal).strip():
        raise ReportError(
            f"{state.get('run_id')} records no sprint goal in {state_rel}, and a report cannot "
            f"invent what the run aimed at - nothing was written")

    verdict = state.get("sprint_goal_verdict") or {}
    if isinstance(verdict, str):
        verdict = {"verdict": verdict, "note": ""}
    duration = round((end - start).total_seconds() / 3600, 1) if start and end else None
    goal_figs = {
        "sprint_goal": fig("sprint_goal", goal, state_rel),
        # Never defaulted to `achieved`: the run would then judge itself.
        "goal_verdict": (fig("goal_verdict", f"Judged {verdict['verdict']}", state_rel)
                         if verdict.get("verdict") else
                         unmeasured("goal_verdict", state_rel,
                                    "no goal verdict recorded on this run")),
        "goal_verdict_note": fig("goal_verdict_note",
                                 (verdict.get("note") or "no note recorded")
                                 if verdict.get("verdict") else "", state_rel),
        "run_id": fig("run_id", state.get("run_id"), state_rel),
        "started_at": fig("started_at", state.get("started_at"), state_rel),
        "ended_at": fig("ended_at", state.get("ended_at") or "open", state_rel),
        # The unit travels with the figure, so an unmeasured duration is never mis-suffixed.
        "duration_hours": (fig("duration_hours", f"{duration}h", state_rel) if duration else
                           unmeasured("duration_hours", state_rel,
                                      "the run record carries no end time")),
        "verified_sha": fig("verified_sha", state.get("verified_sha") or state.get("base_ref")
                            or "none recorded", state_rel),
    }

    current = None
    if not (state.get(run_state.TOKEN_STAMPS) or []) and state.get(run_state.TOKEN_BASELINE):
        # The LEGACY single baseline needs a closing reading of the same meter, so the
        # transcript is read here and nowhere else.
        current = run_state.session_tokens(root)
    tokens = run_state.run_token_total(state, current)
    ledger = _unit_ledger(root, state, state_rel)
    sections = [
        _section("goal", "Goal", goal_figs),
        _estimates_section(state, state_rel, ledger, tokens,
                           round((end - start).total_seconds() / 60, 1) if start and end
                           else None),
        _delivered_section(root, state_rel, ledger),
        _known_issues_section(root, state, state_rel, ledger,
                              state.get("started_at"), _iso(end)),
        _signoff_section(state_rel),
        _cost_section(state, state_rel, tokens),
        _dora_section(root, start, end),
        _calibration_section(state, state_rel),
        _rulings_section(state, state_rel),
        # Bounded at both ends by the run's own window, like DORA, so a decision taken before
        # or after the run cannot move a signed page.
        _waivers_section(root, _iso(end), _iso(start)),
        _lane_yield_section(root, state, start, end),
        _lessons_section(root, state.get("run_id")),
    ]
    # Absent, not NOT MEASURED, where no refusal log exists: its only writer is this repository's
    # own commit hooks, so in a consuming project the section could never fill.
    sections = [s for s in sections if s is not None]
    report = {"schema": SCHEMA, "report_id": None, "run_id": state.get("run_id"),
              "retro_id": sdlc_md.norm_id(retro_id), "generated_at": generated_at,
              # An envelope field, never a figure: in the digest, recording the bound would
              # change the fingerprint it protects.
              "window_end": _iso(end), "signature": None, "sections": sections}
    _refuse_sourceless(report, root)
    report["fingerprint"] = fingerprint(report)
    return report


#: Sources that are NOT paths and cannot be resolved as one - a command whose output was read,
#: or a forge query. Declared, so "it resolves" has one meaning and a deriver cannot invent a
#: third kind of source that quietly satisfies the check by being neither.
#: Where a workspace path starts. A source under one of these names a place in the tree,
#: whether or not the file has been written yet.
WORKSPACE_PREFIXES = ("sdlc-studio/", ".claude/", "tools/", "docs/", "changelog.d/")

NON_PATH_SOURCES = ("gh run list", "git log", "git history", "the session transcript",
                    "forge run", "forge runs", "the harness meter", "no forge")


def _source_resolves(root: Path, src: str) -> bool:
    """Does this source name somewhere a reader can actually go?

    A non-empty string was the whole test, so a deriver could answer `derived` for every figure
    and the Provenance section would read as satisfied while being true of nothing - the exact
    mutant AC1 names, and it survived.

    The rule is DELIBERATELY not "the file exists". A ledger a run has not written to yet is
    the honest source of a figure derived from its absence - `rework_rate` reads the critic
    verdict ledger, and a run with no rejections has no such file - so requiring existence
    would refuse a report over the very absence it is reporting. What is required is that the
    source names a place: a path inside the workspace, or one of the declared non-path sources.
    `derived` is neither, and that is what this catches.
    """
    for part in str(src).split(", "):
        part = part.strip()
        if not part:
            continue
        if any(part.startswith(n) for n in NON_PATH_SOURCES):
            continue
        if (root / part).exists():
            continue
        if any(part.startswith(pre) for pre in WORKSPACE_PREFIXES):
            continue                 # a place in the workspace, written to or not yet
        if part.endswith(".jsonl"):
            # A SESSION TRANSCRIPT. It is a real place and the only place a meter reading can
            # come from, but it lives outside the workspace (the harness owns it) and a run
            # closed from another machine cannot expect to find it. Naming it is honest; going
            # to it is the reader's problem, not this report's.
            continue
        return False
    return True


def _refuse_sourceless(report: dict, root: Path | None = None) -> None:
    """A figure whose deriver produced no source REFUSES the whole build.

    Defaulting the missing source to a word like `derived` would let every figure carry one and
    none of them be re-derivable, so the Provenance section's whole claim would read as
    satisfied while being false. The refusal names the figure's key and its section, because
    the reader's next move is to go and fix that deriver.
    """
    for section, key, f in leaf_figures(report):
        if not isinstance(f, dict) or "value" not in f:
            raise ReportError(f"{section}.{key} is not a figure: it carries no value")
        src = f.get("source")
        if not isinstance(src, str) or not src.strip():
            raise ReportError(
                f"the figure {key!r} in the {section!r} section carries no source, so it cannot "
                f"be re-derived - a figure with no source is a defect in this report, not a "
                f"fact, and nothing was written")
        if root is not None and not _source_resolves(root, src):
            raise ReportError(
                f"the figure {key!r} in the {section!r} section names the source {src!r}, which "
                f"resolves to nothing under {root} - a source a reader cannot go to is not a "
                f"source, and nothing was written")


def _waivers_in_force(root: Path | str, window_end: str | None,
                      window_start: str | None = None) -> tuple[list[dict], list[str]]:
    """The ACCEPTED waivers dated at or before `window_end`, as report rows.

    RPT0002 was SIGNED with two waivers in force - one standing `review.line_coverage` down from
    block to report for that seal, one waiving a checklist row - and named neither, so the
    operator signed without being told which gate was not holding.

    A waiver is an ordinary decision row whose decision cell is the canonical token
    `waiver: <subject>`, which is why it can be recognised at all; a row that merely MENTIONS a
    waiver is prose and is not one. Only `accepted` rows count: a superseded waiver did not hold,
    and reporting it would tell the signer a gate stood down that did not.

    Bounded at BOTH ends by the run's own window, the same bounds the DORA figures use. The upper
    bound stops a decision taken after the page was derived from moving it - BG0718 is the scar,
    where signing widened a window and invalidated the page one second later. The lower bound is
    what makes the section a disclosure rather than an archive: without it this repository returns
    67 rows, almost all one-shot per-story waivers discharged months ago, and the one that matters
    lands around row 60. A section that buries what it exists to surface has disclosed nothing.

    A missing bound is FAIL-CLOSED. An unbounded read would return every waiver ever recorded and
    call them all in force, which is the direction a signer must never be shown.

    A waiver that records its MOMENT is placed by instant, in the half-open `[start, end)` the
    DORA figures use. By date alone, one recorded later on the page's own day entered
    the re-derivation and not the page, so `check` read INVALID; and the cell held the local date
    while the window is stored in UTC, so near midnight a waiver inside the window fell a day
    outside it. A date-only row keeps the date rule, so a page already signed re-derives as filed.
    """
    try:
        import decisions as dec  # noqa: PLC0415 - deferred, like the chain's sibling imports
    except Exception as exc:  # noqa: BLE001 - a report must not die on a log read
        sdlc_md.debug("sprint_report._waivers_in_force", exc)
        return [], []   # the shape the caller unpacks - a bare [] made this guard the death
    hi, lo = (window_end or "")[:10], (window_start or "")[:10]
    start, end = _at(window_start), _at(window_end)
    rel = "sdlc-studio/decisions.md"
    out, undated = [], []
    for rec in dec.list_decisions(Path(root)):
        if rec["status"] != "accepted":
            continue
        decision = (rec["decision"] or "").strip()
        if not decision.lower().startswith(dec.WAIVER_PREFIX):
            continue
        cell = (rec["date"] or "").strip()
        when = cell[:10]
        if not hi or not lo:
            continue      # fail-closed: an unbounded read would call every waiver ever in force
        if not when:
            # A waiver whose Date cell is blank or unreadable cannot be placed in any window.
            # Dropping it silently is the defect BG0715 built `_undatable_findings` to avoid.
            undated.append(rec["id"])
            continue
        moment = _at(cell)       # a date-only cell parses naive: the legacy date rule
        if moment is not None and moment.tzinfo is not None:
            when = cell
            if not _in_window(cell, start, end):
                continue
        elif when > hi or when < lo:
            continue
        # `fig()` rows, not raw strings. Every consumer of a section's rows - `leaf_figures`,
        # `fingerprint`, `render_context` - reads `{"value","source"}`, so
        # raw strings made `build` exit 1 with an AttributeError on any tree holding a waiver.
        out.append({"waiver_id": fig("waiver_id", rec["id"], rel),
                    "waiver_subject": fig("waiver_subject",
                                          decision[len(dec.WAIVER_PREFIX):].strip(), rel),
                    "waiver_reason": fig("waiver_reason", (rec["rationale"] or "").strip(), rel),
                    "waiver_date": fig("waiver_date", when, rel)})
    return out, undated


def _waivers_section(root: Path | str, window_end: str | None,
                     window_start: str | None = None) -> dict:
    """The waivers section, ALWAYS present. An absent section reads as "not checked", and the
    whole point is that the signer can tell that apart from "nothing stood down"."""
    rel = "sdlc-studio/decisions.md"
    if not window_end or not window_start:
        # A read that could not be BOUNDED is not a clean sheet. Emitting the affirmative note
        # here made a refused read indistinguishable from a log that was read and found nothing -
        # on a page carrying a signature, which is this bug's own failure mode one layer over.
        return _section("waivers", "Waivers in force",
                        not_measured=unmeasured(
                            "waivers", rel,
                            "the run record carries no usable window, so the waivers in force "
                            "could not be bounded - which is NOT the same as none standing down"))
    rows, undated = _waivers_in_force(root, window_end, window_start)
    note = ("no gate stood down for this seal - the log was read and carries no accepted waiver "
            "dated inside this report's window" if not rows else
            f"{len(rows)} gate(s) were not holding when this page was derived")
    if undated:
        # Named rather than dropped, the standard BG0715 set in this same run: an item the window
        # cannot judge is disclosed, never silently excluded.
        note += (f" - and {len(undated)} accepted waiver(s) carry no readable date, so whether "
                 f"they were in force is UNKNOWN: {', '.join(undated)}")
    # The note is a FIGURE, not a loose key. A key no consumer reads reaches no template and no
    # digest, so "the log was read and found nothing" existed only inside the in-memory object -
    # which is the same defect as not deriving it at all.
    return _section("waivers", "Waivers in force",
                    figures={"waivers_note": fig("waivers_note", note, "sdlc-studio/decisions.md"),
                             "waivers_count": fig("waivers_count", len(rows),
                                                  "sdlc-studio/decisions.md")},
                    rows=rows)


def _lessons_section(root: Path, run_id: str | None) -> dict:
    """Each live lesson class, with its hits this run and in total, from the class store. Kept
    out of the digest (SECTIONS_OUTSIDE_THE_DIGEST): later closes move the store."""
    import lessons  # noqa: PLC0415 - deferred sibling, as elsewhere in this module
    rel = lessons.STORE_FILE
    try:
        live = [r for r in lessons.load_store(root) if r.get("state") in lessons.LIVE_STATES]
    except (OSError, ValueError) as exc:
        return _section("lessons", "Lessons", not_measured=unmeasured(
            "lessons", rel, f"the lesson store could not be read: {exc}"))
    rows = [{"lesson_id": fig("lesson_id", r["id"], rel),
             "lesson_class": fig("lesson_class", r.get("class") or "", rel),
             "lesson_state": fig("lesson_state", r["state"] + (f" ({r['cr']})" if r.get("cr")
                                                               else ""), rel),
             "lesson_hits_run": fig("lesson_hits_run", sum(
                 1 for h in r.get("hits") or () if h.get("run") == run_id), rel),
             "lesson_hits_total": fig("lesson_hits_total", len(r.get("hits") or ()), rel)}
            for r in live]
    note = (f"{len(rows)} lesson class(es) in force at this close." if rows else
            f"No lesson class is in force: {rel} holds no active or graduating class.")
    return _section("lessons", "Lessons", {"lessons_note": fig("lessons_note", note, rel)}, rows)


#: One line per refusing commit lane, appended by the commit hooks:
#: `{lane, ts, staged, blobs}`, `blobs` mapping each staged path to its blob.
REFUSALS_REL = "sdlc-studio/.local/refusals.jsonl"
#: Runs a lane is judged over before it is listed for deletion: this one and the two before it.
YIELD_RUNS = 3


def is_paperwork(path: str) -> bool:
    """An artefact, baseline, index, changelog fragment or doc: a change that fixes no code."""
    name = path.rsplit("/", 1)[-1]
    return (path.startswith(("sdlc-studio/", "changelog.d/", "docs/"))
            or name.endswith(".md") or "baseline" in name)


def _aware(value) -> "datetime | None":
    """A stamp with its zone, or None. A stamp with no zone cannot be placed against a run
    window - comparing it raises - so it is read as unparseable."""
    at = _at(value)
    return at if at is not None and at.tzinfo is not None else None


def _commits_after(root: Path, since) -> "list[tuple[datetime, dict[str, str]]] | str":
    """`(committed at, {path: new blob})` for every commit with a path, committed at or after
    `since`, oldest first, from one `git log`; or the reason git could not be read. `git log`
    itself is newest first, so two commits stamped in the same whole second arrive with the
    later one first: reversed before the (stable) sort, so a same-second tie keeps the OLDER
    commit first, matching classify_refusals's `>=` join to the earliest same-second retry."""
    try:
        proc = subprocess.run(
            ["git", "log", f"--since={since.isoformat()}", "--format=%x01%cI", "--raw",
             "--no-abbrev", "--no-renames"],
            capture_output=True, text=True, cwd=str(root), timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        return f"git log could not run: {exc}"
    if proc.returncode != 0:
        return f"git log failed: {(proc.stderr or '').strip()[:200] or proc.returncode}"
    out = []
    for block in (proc.stdout or "").split("\x01")[1:]:
        stamp, *lines = [ln for ln in block.splitlines() if ln.strip()]
        # `:<old mode> <new mode> <old blob> <new blob> <status>\t<path>`
        blobs = {ln.split("\t", 1)[1]: ln.split()[3] for ln in lines
                 if ln.startswith(":") and "\t" in ln}
        if blobs and _aware(stamp):
            out.append((_aware(stamp), blobs))
    return sorted(reversed(out), key=lambda c: c[0])


def classify_refusals(root: Path, refusals: list[dict]) -> "list[str] | str":
    """Each refusal's class, by the first commit after it: `catch` when that commit changes a
    path that is not paperwork to content other than the refused commit staged (its `blobs`),
    `paperwork` when it does not - a retry carrying the refused code unchanged caught nothing -
    and `pending` when no commit has followed yet. Or the reason the history could not be read.
    Every refusal's `ts` must carry a zone.

    "After" includes the refusal's own second: git stamps a commit when it starts, before its
    hooks run, so a retry landing in that second carries it. Known limit: both stamps are whole
    seconds, so a commit that landed in that second but before the refusal is read as its
    retry."""
    stamps = [_aware(r["ts"]) for r in refusals]
    if not stamps:
        return []
    commits = _commits_after(root, min(stamps))
    if isinstance(commits, str):
        return commits
    out = []
    for rec, at in zip(refusals, stamps):
        nxt = next((blobs for when, blobs in commits if when >= at), None)
        refused = rec.get("blobs") if isinstance(rec.get("blobs"), dict) else {}
        out.append("pending" if nxt is None else
                   "catch" if any(not is_paperwork(p) and blob != refused.get(p)
                                  for p, blob in nxt.items()) else "paperwork")
    return out


def _yield_windows(root: Path, state: dict, start, end) -> list[tuple]:
    """`(start, end)` for this run and up to the two archived runs before it, newest first. An
    archived run with no end is bounded by the start of the run after it."""
    windows = [(start, end)]
    prior = sorted(((_aware(r.get("started_at")), _aware(r.get("ended_at")))
                    for r in run_state.archived(root)
                    if r.get("run_id") != state.get("run_id") and _aware(r.get("started_at"))
                    and _aware(r.get("started_at")) < start), key=lambda w: w[0])
    for s, e in reversed(prior):
        if len(windows) == YIELD_RUNS:
            break
        windows.append((s, e or windows[-1][0]))
    return windows


def _lane_yield_section(root: Path, state: dict, start, end) -> dict | None:
    """Per commit lane: this run's refusals, candidate catches and paperwork, and whether the
    lane refused across the last three runs without one candidate catch. A MEASURE, never a
    gate: a lane is listed for deletion here and nothing refuses, files or exits on it, and no
    fault in the log or the history can raise out of the close - it reads NOT MEASURED instead.
    None when there is no log, so a clone without the hooks shows no section at all. Outside
    the digest (SECTIONS_OUTSIDE_THE_DIGEST): the log is per clone and a refusal's class moves
    when the next commit lands."""
    path = root / REFUSALS_REL
    if not path.is_file():
        return None
    src = f"{REFUSALS_REL}, git log"

    def unread(why: str) -> dict:
        return _section("lane_yield", "Lane yield",
                        not_measured=unmeasured("lane_yield", REFUSALS_REL, why))
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return unread(f"the refusal log could not be read: {exc}")
    if start is None or start.tzinfo is None:
        return unread("the run records no start time with a zone, so no refusal can be placed "
                      "in it")
    end = end if end is not None and end.tzinfo is not None else None
    logged, bad = [], 0
    for line in filter(str.strip, text.splitlines()):
        try:
            rec = json.loads(line)
        except ValueError:
            rec = None
        if isinstance(rec, dict) and rec.get("lane") and _aware(rec.get("ts")):
            logged.append(rec)
        else:
            bad += 1
    windows = _yield_windows(root, state, start, end)
    logged = [r for r in logged if any(_in_window(r["ts"], s, e) for s, e in windows)]
    classes = classify_refusals(root, logged)
    if isinstance(classes, str):
        return unread(f"the refusals could not be joined to the commits after them: {classes}")
    tally: dict[str, dict] = {}
    for rec, cls in zip(logged, classes):
        t = tally.setdefault(str(rec["lane"]), {"run": [], "all": []})
        t["all"].append(cls)
        if _in_window(rec["ts"], *windows[0]):
            t["run"].append(cls)
    rows = []
    for lane, t in sorted(tally.items()):
        caught, paper = t["all"].count("catch"), t["all"].count("paperwork")
        verdict = (f"too few runs: {len(windows)} of {YIELD_RUNS} recorded"
                   if len(windows) < YIELD_RUNS else
                   f"delete candidate: {len(t['all'])} refusal(s) over {YIELD_RUNS} runs and no "
                   f"candidate catch" if paper and not caught else
                   f"{caught} candidate catch(es) over {YIELD_RUNS} runs")
        rows.append({"yield_lane": fig("yield_lane", lane, src),
                     "yield_refusals": fig("yield_refusals", len(t["run"]), src),
                     "yield_catches": fig("yield_catches", t["run"].count("catch"), src),
                     "yield_paperwork": fig("yield_paperwork", t["run"].count("paperwork"), src),
                     "yield_verdict": fig("yield_verdict", verdict, src)})
    note = (f"{sum(len(t['run']) for t in tally.values())} refusal(s) in this run. A refusal "
            f"is a candidate catch when the next commit changed code or a test from what was "
            f"refused, paperwork when it changed only artefacts, baselines, indexes or docs, and "
            f"pending until a commit follows it."
            + (f" {bad} unparseable line(s) in the log were skipped." if bad else ""))
    return _section("lane_yield", "Lane yield", {"lane_yield_note": fig("lane_yield_note",
                                                                        note, src)}, rows)


def _signoff_section(state_rel: str) -> dict:
    """The block a signature LANDS in. Unsigned it says so; it is never blanked, because an
    empty cell reads as a signature nobody can find rather than one nobody has given."""
    return _section("signoff", "Sign-off", {
        "principal": fig("principal", "not yet signed", state_rel),
        "signed_at": fig("signed_at", "not yet signed", state_rel),
        # The fingerprint is what makes a signature point at ONE version of one page, so it is
        # part of the block that records the signature rather than a footnote under it. Its
        # value is filled from `report["signature"]` at render time, never from the figure set:
        # a figure holding the digest OF the figure set could not be computed before itself.
        "signed_fingerprint": fig("signed_fingerprint", "not yet signed", state_rel),
    })


# --- the template engine ------------------------------------------------------------------
#
# The LAYOUT comes from the shipped template, never from format strings in this module. Build
# the Markdown here and the template becomes documentation, and the two drift on the first
# change to either.

_TOKEN = re.compile(r"\{\{([a-z0-9_]+)\}\}")
_BLOCK = re.compile(r"[ \t]*<!--\s*(repeat|when|unless):\s*([a-z0-9_]+)\s*-->[ \t]*\n?"
                    r"|[ \t]*<!--\s*end\s*-->[ \t]*\n?")


def _parse_blocks(template: str) -> list:
    """`[str | (kind, name, [children])]` - the template as a tree of literals and blocks."""
    stack: list[list] = [[]]
    kinds: list[tuple[str, str]] = []
    pos = 0
    for m in _BLOCK.finditer(template):
        if m.start() > pos:
            stack[-1].append(template[pos:m.start()])
        pos = m.end()
        if m.group(1):
            kinds.append((m.group(1), m.group(2)))
            stack.append([])
        else:
            if not kinds:
                raise ReportError("the template closes a block that was never opened")
            kind, name = kinds.pop()
            children = stack.pop()
            stack[-1].append((kind, name, children))
    if kinds:
        raise ReportError(f"the template leaves the block {kinds[-1][1]!r} unclosed")
    if pos < len(template):
        stack[-1].append(template[pos:])
    return stack[0]


def _fill(text: str, scope: dict, seen: set) -> str:
    def sub(m):
        name = m.group(1)
        if name not in scope:
            seen.add(name)
            return m.group(0)
        value = scope[name]
        return "" if value is None else str(value)
    return _TOKEN.sub(sub, text)


def _emit(nodes: list, scope: dict, rows: dict, flags: dict, seen: set) -> str:
    out = []
    for node in nodes:
        if isinstance(node, str):
            out.append(_fill(node, scope, seen))
            continue
        kind, name, children = node
        if kind == "when" and not flags.get(name):
            continue
        if kind == "unless" and flags.get(name):
            continue
        if kind in ("when", "unless"):
            out.append(_emit(children, scope, rows, flags, seen))
            continue
        for row in rows.get(name) or []:
            out.append(_emit(children, {**scope, **row}, rows, flags, seen))
    return "".join(out)


def _cell(f: dict):
    """How one figure reads on the page: NOT MEASURED carries its reason, and a large count
    carries thousands separators."""
    value = f.get("value")
    if value == NOT_MEASURED and f.get("reason"):
        return f"{NOT_MEASURED} - {f['reason']}"
    return f"{value:,}" if isinstance(value, int) and abs(value) >= 10000 else value


def render_context(report: dict, revalidation: dict | None = None) -> tuple[dict, dict, dict]:
    """`(scalars, row lists, flags)` - what the templates are filled from.

    Tokens are FLAT across sections on purpose: the report's sections group figures by their
    provenance, and the page groups them by what a reader wants next to what. Tying the two
    together would make a layout change a schema change.
    """
    scope: dict = {}
    rows: dict = {}
    flags: dict = {}
    for sec in report.get("sections") or []:
        nm = sec.get("not_measured")
        # A section a page was filed without renders nothing, so a later section is additive.
        flags[f"{sec['key']}_present"] = True
        flags[f"{sec['key']}_measured"] = nm is None
        if nm is not None:
            scope[f"{sec['key']}_reason"] = f"{nm.get('reason')} (consulted {nm.get('source')})"
        for key, f in (sec.get("figures") or {}).items():
            scope[key] = _cell(f)
        flags[f"{sec['key']}_rows"] = bool(sec.get("rows"))
        flags[f"{sec['key']}_units"] = bool(sec.get("unit_rows"))
        for field, name in (("rows", _ROW_LISTS.get(sec["key"], sec["key"])),
                            ("unit_rows", f"{sec['key']}_units")):
            rows[name] = [{k: _cell(f) for k, f in row.items()} for row in sec.get(field) or []]
    scope["report_fingerprint"] = report.get("fingerprint") or "unsigned"
    sig = report.get("signature") or {}
    if sig.get("principal"):
        scope["principal"] = sig["principal"]
        scope["signed_at"] = sig.get("signed_at") or "not recorded"
        scope["signed_fingerprint"] = sig.get("fingerprint") or "not recorded"
    rows["invalidation"] = []
    if revalidation is not None and not revalidation.get("valid"):
        rows["invalidation"] = [{
            "signed_fingerprint": revalidation.get("signed_fingerprint"),
            "current_fingerprint": revalidation.get("fingerprint"),
            "moved_figures": ", ".join(dict.fromkeys(
                (revalidation.get("moved") or [])
                + [e["figure"] for e in revalidation.get("edited") or []]))
            or "an unnamed figure"}]
    return scope, rows, flags


#: Section key -> the row-list name the templates repeat over. Named here rather than in the
#: templates so a section can be renamed without editing two files.
_ROW_LISTS = {"estimates": "estimates", "delivered": "plan_units", "known_issues": "issues",
              "cost": "models", "dora": "dora", "waivers": "waivers", "lessons": "lessons",
              "lane_yield": "lane_yield"}


def _render(report: dict, template: str, revalidation: dict | None) -> str:
    scope, rows, flags = render_context(report, revalidation)
    seen: set = set()
    out = _emit(_parse_blocks(template), scope, rows, flags, seen)
    if seen:
        # A token no figure answers REFUSES rather than being left in the page or silently
        # emptied: a page carrying `{{unit_count}}` is a defect a reader sees, and a page
        # carrying a blank where a figure should be is one nobody sees.
        raise ReportError(
            f"the template names {len(seen)} placeholder(s) this report has no figure for: "
            f"{', '.join(sorted(seen))} - nothing was rendered")
    return out


def template_path(name: str) -> Path:
    return Path(__file__).resolve().parent.parent / "templates" / name


#: The Markdown twin's template, under `templates/`.
MD_TEMPLATE = "core/sprint-report.md"


def render_markdown(report: dict, template: str | None = None,
                    revalidation: dict | None = None) -> str:
    """The committed twin, from `templates/core/sprint-report.md`."""
    if template is None:
        template = template_path(MD_TEMPLATE).read_text(encoding="utf-8")
    out = _render(report, template, revalidation)
    # A repeat block that emits NOTHING - the invalidation banner on a valid report is the
    # ordinary case - leaves its surrounding blank line behind, and two blank lines in a row
    # fail this project's own markdownlint (MD012). The twin is COMMITTED, so a page the repo
    # refuses to accept is a page the close cannot land. Normalised here rather than by
    # tightening every block's whitespace in the template, where the next block added would
    # have to remember the rule.
    # One blank line at most anywhere, and exactly one newline at the end: an empty repeat block
    # at the foot of the page otherwise leaves a trailing blank markdownlint refuses (MD012).
    return re.sub(r"\n{3,}", "\n\n", out).rstrip("\n") + "\n"


def render_html(report: dict, template: str | None = None,
                revalidation: dict | None = None) -> str:
    """The page, from `templates/reports/sprint-report.html`. Generated on demand and never
    written into the tree (D2a)."""
    if template is None:
        template = template_path("reports/sprint-report.html").read_text(encoding="utf-8")
    return _render(report, template, revalidation)


# --- filing, reading and re-deriving -----------------------------------------------------------

def report_dir(root) -> Path:
    return Path(root) / REPORTS_REL


def _unsigned_report_for(root: Path, run_id: str | None) -> str | None:
    """The id of the unsigned report already filed for `run_id`, or None."""
    if not run_id:
        return None
    for p in sorted(report_dir(root).glob("RPT*.json"), reverse=True):
        try:
            stored = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if stored.get("run_id") == run_id and not (stored.get("signature") or {}).get("principal"):
            return p.stem
    return None


def file_report(root, report: dict) -> str:
    """Write the JSON of record and the Markdown twin. Returns the report id.

    ONE REPORT PER RUN. Re-filing a run whose unsigned report is already filed rewrites that
    report in place under its own id; re-running a close used to mint a new id every time. A
    signed report is a record and is never overwritten, so only a run with no unsigned report
    is allocated an id, through the shared allocator. No HTML is written.
    """
    root = Path(root)
    rid = _unsigned_report_for(root, report.get("run_id"))
    if rid is None:
        import next_id  # noqa: PLC0415 - sibling script, imported where it is used
        rid = f"RPT{next_id.allocate_number('report', root, remote=False):04d}"
    report = {**report, "report_id": rid}
    report["fingerprint"] = report.get("fingerprint") or fingerprint(report)
    write_report(root, report)
    return rid


def write_report(root, report: dict) -> Path:
    """Write a report's JSON of record and re-render its Markdown twin. Returns the JSON path.

    Both, always. The twin is a RENDERING of the JSON, so writing one without the other is how
    a page and the record it claims to show come to disagree - which is the failure the whole
    fingerprint exists to detect, and it should not be this module that causes it. Used by
    `file_report` when the page is first derived, and by the seal when a signature lands on it.
    """
    root = Path(root)
    rid = sdlc_md.norm_id(report.get("report_id") or "")
    if not rid:
        raise ReportError("a report cannot be written without its id")
    d = report_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{rid}.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md = _twin_path(root, {**report, "report_id": rid})
    md.write_text(render_markdown(report), encoding="utf-8")
    _sync_report_index(root, d, rid, md, report)
    return path


def _twin_path(root, report: dict) -> Path:
    """Where a report's Markdown twin is filed: one name, for the writer and the check."""
    stem = sdlc_md.slug(f"sprint report {report.get('run_id') or ''}")[:60].strip("-")
    return report_dir(root) / f"{report['report_id']}-{stem or 'sprint-report'}.md"


#: The index a filed report has to leave behind. `report` is a registered artefact type, so
#: `reconcile detect` requires this file the moment the first RPT exists - and reports it as
#: drift `apply` cannot clear, because there is nothing to sync rows INTO. Writing the JSON and
#: the twin and stopping therefore ended the first close of every project in a pre-commit gate
#: refusing the very commit the close had just told the operator to make.
_REPORT_INDEX_HEAD = """# Report Index

**Last Updated:** {updated}

Sprint reports of record, one per run that reached a close. Each is a JSON record derived from
the run's own artefacts with a Markdown twin rendered from it, and a fingerprint over the
ordered figure set - so a reader can tell whether a signed page still describes the tree.
Filed by `sprint close` and sealed by `sprint sign`; never hand-authored, and re-derived rather
than edited when a figure moves.

| ID | Run | Generated | Fingerprint | Signed |
| --- | --- | --- | --- | --- |
"""


def _sync_report_index(root: Path, d: Path, rid: str, md: Path, report: dict) -> None:
    """Add or replace this report's row, keeping every other row already there.

    Re-filing a report REPLACES its own row rather than appending a second: PREPARE is
    rerunnable by contract, so a run that prepares three times must leave one row, not three.
    """
    idx = d / "_index.md"
    head = report.get("header") or {}

    def val(key):
        f = head.get(key) if isinstance(head, dict) else None
        v = f.get("value") if isinstance(f, dict) else None
        return str(v) if v not in (None, "") else "-"

    sig = report.get("signature") or {}
    row = (f"| [{rid}]({md.name}) | {report.get('run_id') or val('run_id')} | "
           f"{report.get('generated_at') or '-'} | {report.get('fingerprint') or '-'} | "
           f"{(sig.get('principal') if isinstance(sig, dict) else None) or 'unsigned'} |")
    if idx.is_file():
        kept = [ln for ln in idx.read_text(encoding="utf-8").splitlines()
                if not (ln.startswith("| [") and f"[{rid}]" in ln)]
        text = "\n".join(kept).rstrip("\n") + "\n" + row + "\n"
    else:
        text = _REPORT_INDEX_HEAD.format(updated=str(report.get("generated_at") or "")[:10]
                                         or "-") + row + "\n"
    # Atomically, like every other index write in this skill: a reader must never see a
    # half-written index, and `test_concurrency` refuses any `_index.md` write that bypasses it.
    sdlc_md.atomic_write(idx, text)


def read_report(root, report_id: str) -> dict:
    p = report_dir(root) / f"{sdlc_md.norm_id(report_id)}.json"
    if not p.is_file():
        raise ReportError(f"no report of record at {_rel(Path(root), p)}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ReportError(f"{_rel(Path(root), p)} could not be read: {exc}") from exc


def _legacy_window_end(root, stored: dict) -> str | None:
    """The bound a stored page was DERIVED under, for a page that records none.

    Pages filed before the bound was carried have to have it inferred, and the two cases are
    not the same: a page derived while its run was still open was bounded at its own generation
    time, and one derived after the run ended was bounded at `ended_at`. Falling back to the
    generation time for both leaves the second re-deriving over a WIDER window than it was
    written under, so a commit landing between the run's end and the page enters only the
    re-derivation and an untouched page reads INVALID - which is the defect this whole repair
    is about, surviving in exactly the pages the fallback exists to protect. An independent
    plan review found it there.

    Which case a page belongs to is readable from the two timestamps: a run that ended BEFORE
    the page was generated had already ended when it was derived. A run that ended after - the
    ordinary shape, because the seal comes after the page - was open at the time, whatever
    `ended_at` says now. So the earlier of the two is the bound, and a page that records its
    own `window_end` never reaches here at all.
    """
    gen = stored.get("generated_at")
    if stored.get("window_end"):
        return stored["window_end"]
    state, _rel = _run_state_for(Path(root), stored.get("run_id"))
    ended, g = _at(state.get("ended_at")), _at(gen)
    if ended and g and ended < g:
        return state["ended_at"]
    return gen


def revalidate(root, report_id: str) -> dict:
    """Is this report still true of the tree? Decided by RE-DERIVING it, never by counting
    writes since the signature.

    A tracked write newer than the signature marks every sealed report stale on the next
    unrelated commit, so the marker stops carrying information within a day; a write to a batch
    unit's declared files invalidates on a changelog fragment that moves no figure. Re-derivation
    is the only reading that is itself re-derivable, which is the property the whole report
    rests on. READ-ONLY: nothing on disk is touched.
    """
    stored = read_report(root, report_id)
    if stored.get("schema") != SCHEMA:
        # A page of another shape re-derives to different sections, so every figure would read
        # as moved. Said as what it is instead; the page and its signature stand as filed.
        raise ReportError(f"{stored.get('report_id') or report_id} was filed under report "
                          f"schema {stored.get('schema')} and this builder derives schema "
                          f"{SCHEMA}, so it cannot be re-derived - the page stands as filed")
    # RE-DERIVED OVER THE SAME WINDOW AND THE SAME RUN. Passing the stored generation time is
    # what makes this a comparison of the tree against the page, rather than of one window
    # against a wider one: without it every commit made after the report - including the commit
    # that files it - entered the fresh figures and nothing else had to change for INVALIDATED
    # to appear. The run is the page's own, archived once the next run opens.
    fresh = build_report(root, stored.get("retro_id"), as_of=stored.get("generated_at"),
                         window_end=_legacy_window_end(root, stored),
                         run_id=stored.get("run_id"))
    was = {f"{s}.{k}": f.get("value") for s, k, f in leaf_figures(stored)
           if in_the_digest(s, k)}
    now = {f"{s}.{k}": f.get("value") for s, k, f in leaf_figures(fresh)
           if in_the_digest(s, k)}
    changes = []
    for name in sorted(set(was) | set(now)):
        if was.get(name) != now.get(name):
            changes.append({"figure": name, "key": name.split(".", 1)[1],
                            "signed": was.get(name), "current": now.get(name)})
    signed = stored.get("fingerprint")
    current = fresh["fingerprint"]
    # THE FILED PAGE IS CHECKED AGAINST ITSELF TOO. Re-deriving the tree says nothing about a
    # page edited by hand while the tree still re-derives the original, so the filed figures
    # are digested the way the fingerprint was, and the twin is compared with its own rendering.
    digest = fingerprint(stored)
    edited = []
    if digest != signed:
        edited = [{"page": "json", "figure": c["figure"],
                   "detail": f"filed {c['signed']!r}, the tree re-derives {c['current']!r}"}
                  for c in changes] or [
            {"page": "json", "figure": "an unnamed figure",
             "detail": f"the filed figures digest to {digest}, not the {signed} recorded"}]
    edited += _lifecycle_edits(root, stored, fresh)
    twin_edits, twin_note = _twin_check(root, {**stored, "report_id": sdlc_md.norm_id(
        stored.get("report_id") or report_id)})
    edited += twin_edits
    return {"valid": signed == current and not edited,
            "report_id": stored.get("report_id") or report_id,
            "signed_fingerprint": signed, "fingerprint": current, "page_fingerprint": digest,
            "moved": [c["key"] for c in changes], "changes": changes, "edited": edited,
            "twin_note": twin_note, "signature": stored.get("signature"),
            "archived": _run_state_for(Path(root), stored.get("run_id"))[1]
            != _rel(root, run_state.path(root))}


def _lifecycle_edits(root, stored: dict, fresh: dict) -> list[dict]:
    """The figures OUTSIDE_THE_DIGEST, checked against the run record instead of signed.

    The seal writes the run's end after the page, so neither figure is in the digest, but each
    was still fixed when the page was generated. The end is the run record's `ended_at`, or
    `open` when the run had not ended by the page's generation time; the duration runs to the
    window the page carries, which the re-derivation replays.
    """
    state, _state_rel = _run_state_for(Path(root), stored.get("run_id"))
    ended, generated = _at(state.get("ended_at")), _at(stored.get("generated_at"))
    derived = {f"{s}.{k}": f.get("value") for s, k, f in leaf_figures(fresh)
               if not in_the_digest(s, k)}
    filed = {f"{s}.{k}": f.get("value") for s, k, f in leaf_figures(stored)
             if not in_the_digest(s, k)}
    edits = []
    for name in sorted(set(derived) | set(filed)):
        allowed = {derived.get(name)}
        if name == "goal.ended_at" and (ended is None or generated is None or ended >= generated):
            allowed.add("open")
        if filed.get(name) not in allowed:
            edits.append({"page": "json", "figure": name,
                          "detail": f"filed {filed.get(name)!r}, the run record gives "
                                    f"{' or '.join(sorted(repr(a) for a in allowed))}"})
    return edits


#: What a figure reads while it is probed for the Markdown lines it fills.
_PROBE = "\ufffcprobe\ufffc"


#: What a twin difference inside no figure's text is named: the template owns that wording.
_NO_FIGURE = "wording no figure fills"


def _lines(text: str) -> list[str]:
    """A page's lines, trailing blank lines dropped: an editor's extra newline is not an edit."""
    lines = text.splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def _twin_check(root, stored: dict) -> tuple[list[dict], str | None]:
    """Where the filed Markdown twin is not what its JSON renders to, and a note when the twin
    could not be compared.

    A twin rendered under an earlier template differs from today's rendering in wording no
    figure fills, and that is not an edit. So a twin that differs is also rendered under each
    template the repository held at the commits that wrote the page, and a match under any of
    them is a match; a mismatch is named against the closest. Without that history, a
    difference only in wording no figure fills is noted as not comparable. A differing figure
    is an edit either way.
    """
    twin = _twin_path(root, stored)
    if not twin.is_file():
        return [{"page": "markdown", "figure": "the Markdown twin",
                 "detail": f"no twin is filed at {_rel(Path(root), twin)}"}], None
    have = _lines(twin.read_text(encoding="utf-8"))
    current = template_path(MD_TEMPLATE).read_text(encoding="utf-8")
    edits = _twin_edits(stored, have, current)
    if not edits:
        return [], None
    history = [tpl for tpl in _filed_templates(Path(root), [
        twin, report_dir(root) / f"{stored['report_id']}.json"]) if tpl != current]
    for tpl in history:
        found = _twin_edits(stored, have, tpl)
        if not found:
            return [], None
        if len(found) <= len(edits):
            edits = found
    if not history and all(e["figure"] == _NO_FIGURE for e in edits):
        return [], ("the twin differs from today's template only in wording no figure fills, "
                    "and no commit holds the template it was rendered with - not comparable")
    return edits, None


def _filed_templates(root: Path, page: list[Path]) -> list[str]:
    """The twin's template as each commit that wrote the page held it, newest first; empty
    when git, those commits or the template at them cannot be read."""
    def git(*args: str) -> str | None:
        try:
            proc = subprocess.run(["git", *args], cwd=str(root), capture_output=True,
                                  text=True, encoding="utf-8", timeout=30)
        except (OSError, subprocess.SubprocessError):
            return None
        return proc.stdout if proc.returncode == 0 else None

    top = (git("rev-parse", "--show-toplevel") or "").strip()
    if not top:
        return []
    try:
        rel = template_path(MD_TEMPLATE).resolve().relative_to(Path(top).resolve())
    except ValueError:
        return []
    shas = (git("log", "--format=%H", "--", *map(str, page)) or "").split()
    texts = (git("show", f"{sha}:{rel.as_posix()}") for sha in shas)
    return list(dict.fromkeys(text for text in texts if text is not None))


def _differing(a: list[str], b: list[str]):
    """`(i1, i2, j1, j2)` for every block where the line lists `a` and `b` differ."""
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag != "equal":
            yield i1, i2, j1, j2


def _spans(line: str, probed: str) -> list[tuple[int, int]]:
    """Where in `line` a figure renders, from the same line rendered with the figure probed.

    Only the figure differs between the two, so each marker stands where the figure's text
    does and the text is as much longer or shorter than the marker as the lines differ. When
    that cannot be read off - the probe moved more than the one line - the whole line is the
    figure's.
    """
    hits = probed.count(_PROBE)
    width, spare = divmod(len(line) - len(probed), hits) if hits else (0, 1)
    width += len(_PROBE)
    if spare or width < 0:
        return [(0, len(line))]
    spans, at = [], probed.find(_PROBE)
    for n in range(hits):
        start = at - n * (len(_PROBE) - width)
        spans.append((start, start + width))
        at = probed.find(_PROBE, at + len(_PROBE))
    return spans


def _twin_edits(stored: dict, have: list[str], template: str) -> list[dict]:
    """The twin's lines that differ from `template`'s rendering of the FILED JSON, by figure.

    The whole twin is compared, so the signature row `sprint sign` writes through the same
    renderer is on both sides and never reads as an edit. A difference is attributed by
    probing: each figure in turn renders as a marker, which places its text on a line of the
    rendering, and a figure is named when the twin's characters differ inside its text. A
    difference inside no figure's text is the template's own wording.
    """
    want = _lines(render_markdown(stored, template))
    blocks = list(_differing(want, have))
    if not blocks:
        return []
    sig = stored.get("signature") if isinstance(stored.get("signature"), dict) else {}
    probes = ([(f"{s}.{k}", f, "value") for s, k, f in leaf_figures(stored)]
              + [("fingerprint", stored, "fingerprint")]
              + [(f"signature.{k}", sig, k) for k in ("principal", "signed_at", "fingerprint")
                 if k in sig])
    filled: dict[int, list[tuple[str, int, int]]] = {}
    for name, holder, field in probes:
        old = holder.get(field)
        holder[field] = _PROBE
        try:
            probe = _lines(render_markdown(stored, template))
        finally:
            holder[field] = old
        for i1, i2, j1, j2 in _differing(want, probe):
            paired = i2 - i1 == j2 - j1
            for n, i in enumerate(range(i1, min(max(i2, i1 + 1), len(want)))):
                for a, b in (_spans(want[i], probe[j1 + n]) if paired
                             else [(0, len(want[i]))]):
                    filled.setdefault(i, []).append((name, a, b))
    edits = []
    for i1, i2, j1, j2 in blocks:
        was, now = "\n".join(want[i1:i2]), "\n".join(have[j1:j2])
        changed = [(c1, c2) for tag, c1, c2, _d1, _d2 in difflib.SequenceMatcher(
            None, was, now, autojunk=False).get_opcodes() if tag != "equal"]
        names, offset = [], 0
        for i in range(i1, i2):
            for name, a, b in filled.get(i, []):
                s, e = offset + a, offset + b
                if any(s <= c1 <= e if c1 == c2 else (c1 < e and c2 > s) or s == e == c1
                       for c1, c2 in changed):
                    names.append(name)
            offset += len(want[i]) + 1
        shown = (" / ".join(have[j1:j2]) or "nothing", " / ".join(want[i1:i2]) or "nothing")
        edits += [{"page": "markdown", "figure": name,
                   "detail": f"the twin reads {shown[0]!r} where its JSON renders {shown[1]!r}"}
                  for name in list(dict.fromkeys(names)) or [_NO_FIGURE]]
    return edits


def report_status(root) -> dict | None:
    """The newest report of record and whether it is still valid, or None when there is none.

    Lives here rather than in the renderer so `status` can say it too: an operator who reads
    `status` and never opens the report would otherwise be told nothing, which is the state
    this check exists to end. Never raises and never writes.
    """
    d = report_dir(root)
    if not d.is_dir():
        return None
    files = sorted(d.glob("RPT*.json"))
    if not files:
        return None
    rid = files[-1].stem
    try:
        state = revalidate(root, rid)
    except (ReportError, OSError, ValueError) as exc:
        return {"report_id": rid, "valid": None, "reason": f"{type(exc).__name__}: {exc}"}
    return state


def status_line(state: dict | None) -> str | None:
    """The one line `status` prints about the report of record."""
    if not state:
        return None
    rid = state.get("report_id")
    if state.get("valid") is None:
        return f"Report:       {rid} could not be re-derived ({state.get('reason')})"
    sig = state.get("signature") or {}
    if state.get("valid"):
        if sig.get("principal"):
            return (f"Report:       {rid} signed by {sig['principal']} on "
                    f"{sig.get('signed_at')}")
        return f"Report:       {rid} built and not yet signed"
    if state.get("edited"):
        named = ", ".join(dict.fromkeys(e["figure"] for e in state["edited"]))
        return (f"Report:       {rid} INVALID - the filed page was edited ({named}); restore it "
                f"from version control, or `sprint_report.py check --report {rid}` for detail")
    moved = ", ".join(state.get("moved") or []) or "an unnamed figure"
    return (f"Report:       {rid} INVALIDATED - re-deriving it now moves {moved}; "
            f"{_refile_remedy(state)}")


# --- the verbs ---------------------------------------------------------------------------------

def _filed_by_close_only(state: dict, retro_id: str, archived: bool = False) -> str:
    """Why `build --write` files nothing: a report of record is filed ONLY by `sprint close`.

    The close takes the closing token stamp and records each unit's gate verdict before it
    derives the page, and holds the page behind its checks; a report filed here skipped all
    three and read Tokens 0. An open run is re-filed by re-running the close. A sealed run's
    report is the close's record, so it too is refused: a new page needs the run reopened, and
    an archived run cannot be reopened at all.
    """
    run_id, outcome = state.get("run_id"), state.get("outcome")
    close = f"`sprint.py close --retro {retro_id}`"
    if outcome == run_state.RUNNING:
        return (f"refused: {run_id} is open, and a report of record is filed only by the close, "
                f"which stamps the tokens and records the gate verdicts first - run {close}. "
                f"Without --write, build previews the page and files nothing")
    record = ("a signed record" if (state.get("signature") or {}).get("principal")
              else "the close's record")
    return (f"refused: {run_id} is sealed ({outcome}) and its report is {record} - "
            + (_LIVE_ONLY if archived else
               f"`sprint.py reopen --reason ...` then {close} to file a new one"))


#: An archived run is no longer the live one, so neither `reopen` nor the close can reach it.
_LIVE_ONLY = "a page re-files only while its run is live, and this run is archived"


def _refile_remedy(state: dict) -> str:
    """The route that re-files an invalidated report: the close, after a reopen once signed,
    and none once its run is archived."""
    if state.get("archived"):
        return _LIVE_ONLY
    if (state.get("signature") or {}).get("principal"):
        return "reopen the run with `sprint.py reopen --reason ...`, then re-run `sprint.py close`"
    return "re-run `sprint.py close`, which re-files it under the same id"


def cmd_build(args: argparse.Namespace) -> int:
    root = Path(args.root)
    try:
        state, state_rel = _run_state_for(root, getattr(args, "run", None))
        if args.write:
            archived = state_rel != _rel(root, run_state.path(root))
            print(f"error: {_filed_by_close_only(state, args.id or 'RETROxxxx', archived)}",
                  file=sys.stderr)
            return 2
        report = build_report(root, args.id or _retro_for_run(root, state))
    except ReportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(report))
    return 0


def _filed_twin(root: Path, report: dict, asked: str, to: str) -> str:
    """A page filed under another report schema, as it was filed: its Markdown twin under a
    one-line note. This builder cannot re-derive it, so it has no HTML render."""
    rid = sdlc_md.norm_id(report.get("report_id") or asked)
    why = (f"{rid} was filed under report schema {report.get('schema')} and cannot be "
           f"re-derived by this builder (schema {SCHEMA})")
    twins = sorted(report_dir(root).glob(f"{rid}-*.md"))
    if to == "html":
        raise ReportError(f"{why}, so it has no HTML render - `render --report {rid}` prints "
                          f"its filed Markdown")
    if not twins:
        raise ReportError(f"{why}, and no filed Markdown twin was found beside it")
    return (f"> {why}; this is the page as it was filed.\n\n"
            + twins[0].read_text(encoding="utf-8"))


def cmd_render(args: argparse.Namespace) -> int:
    root = Path(args.root)
    try:
        report = read_report(root, args.report)
        if args.out:
            out = Path(args.out).resolve()
            if report_dir(root).resolve() in out.parents or out.parent == report_dir(root).resolve():
                print(f"error: {out} is inside {REPORTS_REL}/, and {D2A}", file=sys.stderr)
                return 2
        if report.get("schema") != SCHEMA:
            page = _filed_twin(root, report, args.report, args.to)
        else:
            state = revalidate(root, args.report)
            page = (render_html(report, revalidation=state) if args.to == "html"
                    else render_markdown(report, revalidation=state))
    except ReportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        return 0
    print(page)
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    try:
        state = revalidate(Path(args.root), args.report)
    except ReportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    rid = state["report_id"]
    if state["valid"]:
        print(f"VALID: {rid} re-derives to the fingerprint it records ({state['fingerprint']})")
        if state.get("twin_note"):
            print(f"  note: {state['twin_note']}")
        return 0
    if state["edited"]:
        print(f"INVALID: {rid} as filed is not the page that was written - edited:")
        for e in state["edited"]:
            print(f"  {e['page']} {e['figure']}: {e['detail']}")
        print("restore the filed page from version control - a report is re-derived, never "
              "edited")
        if state["signed_fingerprint"] == state["fingerprint"]:
            return 1
    print(f"INVALIDATED: {rid} records fingerprint {state['signed_fingerprint']}; re-deriving "
          f"it from the tree now yields {state['fingerprint']}")
    for change in state["changes"]:
        print(f"  {change['key']}: signed {change['signed']!r}, now {change['current']!r}")
    print(f"to re-file it, {_refile_remedy(state)}")
    return 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="The end-of-sprint report: delivered, cost, velocity.")
    p.add_argument("--root", default=".")
    sub = p.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("operator-summary",
                       help="The decision-grade page an operator leads from: what shipped, "
                            "what was rejected, what is carried and where it is filed, what it "
                            "cost, and what to overturn. Derived from the record - no party to "
                            "the decision writes a word of it.")
    o.add_argument("--id", required=True, metavar="RETROxxxx")
    o.add_argument("--format", choices=["text", "json"], default="text")
    o.set_defaults(func=cmd_operator_summary)
    c = sub.add_parser("checklist",
                       help="The compulsory sprint checklist: one row per stage of the cycle "
                            "plus the figures a close re-derives. Non-zero while any item is "
                            "outstanding.")
    c.add_argument("--id", required=True, metavar="RETROxxxx")
    c.add_argument("--format", choices=["text", "json"], default="text")
    c.set_defaults(func=cmd_checklist)
    s = sub.add_parser("show", help="Compose and print the sprint report for a retro.")
    s.add_argument("--id", required=True, metavar="RETROxxxx")
    s.add_argument("--tokens", type=int, default=None, help="sprint actual token total (interactive)")
    s.add_argument("--elapsed-hours", dest="elapsed_hours", type=float, default=None,
                   help="sprint elapsed hours for the primary velocity (interactive)")
    s.add_argument("--format", choices=["text", "json"], default="text")
    s.set_defaults(func=cmd_show)
    b = sub.add_parser("build", help="Build the REPORT OF RECORD for a run: every figure "
                                     "derived from the run's own artefacts and carrying its "
                                     "source. Exits 2 on a figure with no source.")
    b.add_argument("--run", default=None, metavar="RUN-...", help="the run to report on")
    b.add_argument("--id", default=None, metavar="RETROxxxx", help="the run's retro")
    # `text` and `json`, defaulting to `text`, like every other `--format` in the family.
    # `text` here IS the Markdown rendering - it is what a reader reads.
    b.add_argument("--format", choices=["text", "json"], default="text")
    b.add_argument("--write", action="store_true",
                   help="refused: a report of record is filed only by `sprint.py close`, "
                        "which names the command to run")
    b.set_defaults(func=cmd_build)
    r = sub.add_parser("render", help="Render a filed report. The HTML is generated on demand "
                                      "and never written into the tree (D2a).")
    r.add_argument("--report", required=True, metavar="RPTxxxx")
    # NOT `--format`: this chooses which RENDERING to produce, and `--format` is spelled one
    # way family-wide (`text`/`json`, defaulting to `text`). Borrowing the name for a
    # different question is what makes an agent probe --help for a switch it already knows.
    r.add_argument("--to", choices=["markdown", "html"], default="markdown",
                   help="which rendering to produce")
    r.add_argument("--out", default=None, help="write to this path instead of stdout")
    r.set_defaults(func=cmd_render)
    k = sub.add_parser("check", help="Is a filed report still true of the tree? Re-derives it "
                                     "and names every figure that moved. Non-zero when it has.")
    k.add_argument("--report", required=True, metavar="RPTxxxx")
    k.set_defaults(func=cmd_check)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Resolve the root ONCE and write it back, so every verb below anchors on the tree the
    # run belongs to. The family default `.` means "work it out from here", not "the cwd
    # is the project": otherwise a run from a subdirectory acts on a stray tree and exits 0.
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


# EVERY ROSTER ENTRY RESOLVES, CHECKED AT IMPORT. Placed at the END of the module rather
# than beside the roster, because the resolvers are defined below it - run there, this check
# refuses the module's own first entry. An entry naming a resolver this module does
# not define fails only when the close reaches that item - minutes into a close, on the one run
# that needed it - and an entry naming an attribute that exists but is not CALLABLE fails the
# same way, one line later. Both are typos, both are cheap to find here, and neither is
# something a reader of the roster can see by looking at it.
for _item in CHECKLIST:
    _name = _item.get("resolver") or ""
    _fn = globals().get(_name)
    if _fn is None:
        raise RuntimeError(
            f"checklist item {_item.get('id')!r} names resolver {_name!r}, which this module "
            f"does not define - the close would fail on that item and nowhere earlier")
    if not callable(_fn):
        raise RuntimeError(
            f"checklist item {_item.get('id')!r} names resolver {_name!r}, which exists but is "
            f"not callable - an attribute that merely EXISTS satisfies a presence test and "
            f"still cannot resolve the item")
del _item, _name, _fn

if __name__ == "__main__":
    raise SystemExit(main())
