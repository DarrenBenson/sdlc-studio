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
import importlib
import json
import re
import sys
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
    overhead = _overhead_ratio(Path(root), unit_ids, execution, mut)
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
        qualifier = (f" TREE UNESTABLISHED: {tree.get('why') or 'no isolation evidence was '
                     'recorded for this run'}")
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
    "sprint": ("appetite", "close", "boundary", "report", "checklist", "preflight",
               "reopen", "stop", "decision", "batch", "lane", "next", "queue", "call"),
    "critic": ("brief", "caller-check", "correct", "evidence", "repair", "show",
               "signoff-brief", "supersede"),
    "handoff": ("show",),
    "lessons": ("add", "carried", "carry", "list", "propose", "prune", "rank",
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
    # like every other row but never held against a close that has not got there yet. Without
    # this the chain refuses on the sign-off it is about to fan out and no close can ever pass:
    # a gate whose only exit is the step it blocks is not a gate, it is a deadlock. Reject,
    # fix, RE-REQUEST is the loop a human sprint runs; a gate must leave the re-request
    # reachable.
    {"id": "signoff", "kind": STAGE, "authority": DERIVED, "discharged_by": "close",
     "title": "Reviewer-of-record sign-off", "command": "critic signoff",
     "resolver": "_ck_signoff"},
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
    rejected = [u for u in units if latest.get(u) and latest[u] != _APPROVE]
    unreviewed = [u for u in units if not latest.get(u)]
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


def _changed_paths(root: Path, base_ref: str) -> set | None:
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
        out = subprocess.run(["git", "diff", "--name-only", f"{base_ref}...HEAD"],
                             cwd=str(root), capture_output=True, text=True, timeout=60)
        if out.returncode != 0:
            return None
        return {ln.strip() for ln in out.stdout.splitlines() if ln.strip()}
    except Exception as exc:  # noqa: BLE001 - an unreadable diff judges nothing
        sdlc_md.debug("sprint_report._changed_paths", exc)
        return None


def _ticked_criteria(text: str) -> list[str]:
    """The criteria this unit's own body claims are done, named."""
    out = []
    for i, line in enumerate(sdlc_md.criteria_section(text).splitlines(), 1):
        m = _TICKED_RE.match(line)
        if m:
            out.append(m.group(1) or f"criterion {i}")
    return out


def _ck_tick_verification(ctx: dict) -> tuple:
    """Does the tree support what the units say they did?

    A tick is the author asserting a criterion is met. Two units of one run were closed on
    ticks the diff contradicted, and the checklist passed them - because nothing compared the
    claim against the surfaces the unit itself declared.
    """
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
    changed = _changed_paths(ctx["root"], base)
    if changed is None:
        return (NOT_RUN, "diff unreadable",
                f"the diff against {base} could not be taken, so the ticks are unjudged - "
                "which is not the same as supported")
    contradicted = []
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
        if any(any(c == d or c.startswith(d.rstrip("/") + "/") for c in changed)
               for d in declared):
            continue
        contradicted.extend(f"{uid} {ac}" for ac in ticked)
    if contradicted:
        return (NOT_RUN, f"{len(contradicted)} ticked criterion/criteria unsupported",
                f"ticked while the surfaces the unit declared are unchanged since {base}: "
                f"{', '.join(contradicted[:8])}")
    return (RAN, f"ticks supported by the diff since {base}", "")


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


def _ck_signoff(ctx: dict) -> tuple:
    units = ctx["units"]
    if not units:
        return (NOT_RUN, "no units", "the batch named no units, so there is nothing to sign off")
    try:
        import critic  # noqa: PLC0415
        signed = [u for u in units if critic.signoff_for(ctx["root"], u)]
    except Exception as exc:  # noqa: BLE001
        sdlc_md.debug("sprint_report._ck_signoff", exc)
        return (NOT_RUN, "unreadable", f"the sign-off log could not be read ({exc})")
    if not signed:
        return (NOT_RUN, f"0/{len(units)}",
                "no reviewer of record has signed any unit of this batch")
    # SPLIT, never a single total. Who accepted a unit - a human principal or an amigo panel -
    # is exactly the fact a reader comes to this row for, and a combined count hides it behind
    # a number that looks complete either way.
    panel = [u for u in signed
             if critic.is_panel_signoff(critic.signoff_for(ctx["root"], u))]
    operator = len(signed) - len(panel)
    split = f" ({len(panel)} panel, {operator} operator)" if panel else ""
    return (RAN, f"{len(signed)}/{len(units)}{split}",
            "" if len(signed) == len(units) else
            f"{len(units) - len(signed)} unit(s) hold at Review until a sign-off lands")


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
    for uid in units:
        v = critic.verdict_for(ctx["root"], uid)
        if not v:
            uncovered.append(uid)
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
    unanswered = [u for u in states[critic.COVERAGE_UNREVIEWED]
                  if critic.verdict_for(ctx["root"], u)]
    never = [u for u in states[critic.COVERAGE_UNREVIEWED]
             if not critic.verdict_for(ctx["root"], u)]
    value = (f"{len(states[critic.COVERAGE_APPROVED])} approved, {len(repaired)} repaired, "
             f"{len(unanswered)} rejected, {len(never)} unreviewed; {lenses} lens(es)"
             + (" - UNDER-COVERED" if under else ""))
    # The unreviewed units are NAMED, never only counted: the failure being repaired is one real
    # gap hidden inside a crowd of false ones, so a count alone leaves the operator to find it.
    shown = ([f"UNREVIEWED {u}" for u in never]
             + covered[:6] + [f"REJECTED {r}" for r in rejected[:6]])
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
    stop = [r["id"] for r in rows if r["ok"] and r["ruling"] == "stop-ship"]
    broken = [f"{r['id'] or '(no id)'}: {r['why']}" for r in rows if not r["ok"]]
    if not rows and not open_findings:
        return (ANSWERED, "none carried",
                "the scan ran and this sprint left no finding open - a scan that could NOT "
                "run reports unreadable above, so this row means what it says")
    if unruled or broken:
        bits = [f"UNRULED {u}" for u in unruled] + broken
        return (UNANSWERED, f"{len(unruled)} unruled, {len(broken)} malformed row(s)",
                "; ".join(bits[:12]) + " - an open finding nobody ruled on is not a carried "
                "issue, it is one nobody looked at")
    return (ANSWERED, f"{len(rows)} ruled" + (f", {len(stop)} STOP-SHIP" if stop else ""),
            "; ".join(f"{r['id']} {r['ruling']} by {r['by']}" for r in rows[:12]))


def _ck_cost(ctx: dict) -> tuple:
    spend = ctx.get("spend") or {}
    if not spend.get("measured_units") and not ctx.get("sprint_actual_tokens"):
        return (UNANSWERED, "unattributed",
                "no per-unit telemetry and no harness-tracked sprint total, so what this "
                "sprint cost is not attributable - which is not zero")
    return (ANSWERED, f"{spend.get('tokens', 0):,} token(s) over "
                      f"{spend.get('measured_units', 0)} measured unit(s)", "")


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
            # inside the window is this run's whether or not a batch span claimed it.
            when = stamp.split()[-1] if stamp else ""
            if not when or when < started or (ended and when > ended):
                continue
            filed.append(uid)
            status = (sdlc_md.extract_field(text, "Status") or "").strip()
            if status not in sdlc_md.terminal_statuses(type_):
                still_open.append(uid)
    return sorted(filed), sorted(still_open)


def checklist(root: Path | str, retro_id: str, *, unit_ids: list[str] | None = None,
              rep: dict | None = None) -> dict:
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
        "root": root, "retro_id": retro_id, "units": units, "run": run,
        "planned": _planned_ids(run),
        "plan": sdlc_md.read_json(Path(root) / "sdlc-studio" / ".local" / "sprint-plan.json", {}),
        "sprint_goal": rep.get("sprint_goal"), "goal_verdict": rep.get("sprint_goal_verdict"),
        "delivered_points": rep.get("delivered_points"), "spend": rep.get("spend"),
        "sprint_actual_tokens": rep.get("sprint_actual_tokens"),
        "sprint_reviews": sprint_reviews, "review_rounds": review_rounds,
        "filed_in_run": filed, "open_filed_in_run": still_open,
        "carried_issues": _carried_issues(root, retro_id),
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
            # A finding ruled stop-ship is ANSWERED - the answer is that it stops the ship. It
            # is carried separately because a ruling that changes nothing is a note, and the
            # ruling that matters most is the one that must be able to stop something.
            "stop_ship": [i["id"] for i in (ctx["carried_issues"] or [])
                          if i["ok"] and i["ruling"] == retro.STOP_SHIP]}


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
        return retro.carried_issues(sdlc_md.read_text_safe(path)) if path else None
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

    So every field here comes from `report`, the sign-off log, the verdict log and the findings
    scan. There is NO parameter through which anybody's free text reaches this page, which is
    the property the test pins by varying a verdict's `issues` and asserting the summary does
    not move.

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
        signoff = critic.signoff_for(root, uid)
        # ASKED of critic, never re-derived here. A second copy of "what counts as a seat"
        # would drift from the first, and this reader is where the answer becomes visible to
        # the operator - the one place a wrong answer is acted on.
        capacity = (critic.CAPACITY_SEAT if critic.signed_by_seat(signoff)
                    else str((signoff or {}).get("capacity") or "").strip())
        if capacity in critic.CAPACITY_ABSENT:
            capacity = "unrecorded"
        verdict = str((v or {}).get("verdict") or "").upper()
        if verdict == critic.REJECT:
            rejected.append({"unit": uid, "state": critic.repair_state(root, uid)["state"]})
            # A REJECT that was repaired is the single likeliest thing an operator would rule
            # differently: somebody said this was wrong, and somebody else then said the repair
            # answered it. Naming it is what makes leading a bounded act.
            reversal.append({"unit": uid, "why": "rejected, then repaired - the repair was "
                                                 "judged to answer the finding"})
        elif verdict == critic.APPROVE:
            shipped.append({"unit": uid, "signed_by": capacity})
        if critic.signed_by_seat(signoff):
            reversal.append({"unit": uid, "why": "signed off by a SEAT, not a person"})

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
        f"{r['unit']} [signed: {r['signed_by']}]" for r in s["shipped"]) or "none"))
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
