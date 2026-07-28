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
import json
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
    return {
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
        "tickets": val.get("filed", []),
        "declined": val.get("declined", []),
    }


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
    return [f"Mutation gate: {cur['elapsed_s']}s, {cur['applied']} applied, "
            f"{cur['killed']} killed, {cur['survived']} survived{equiv}; "
            f"yield {cur['yield']} filed artefact(s) ({filed}){per}.", *trailing]


#: Modes that count as having RUN something. `reuse` ran nothing and is counted apart: folding
#: it into the full-run count would report a saving as a cost, and dropping it would hide that
#: a decision was taken at all.
_RAN_MODES = ("full", "selected", "none")


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
    counted = [r for r in mine if str(r.get("mode")) in _RAN_MODES]
    seconds = [float(r["seconds"]) for r in counted
               if isinstance(r.get("seconds"), (int, float))]
    return {
        "measured": bool(seconds),
        "runs": len(mine),
        "full_runs": sum(1 for r in mine if r.get("mode") == "full"),
        "selected_runs": sum(1 for r in mine if r.get("mode") == "selected"),
        "reused_runs": sum(1 for r in mine if r.get("mode") == "reuse"),
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
    reused = f", {act['reused_runs']} reused (ran nothing)" if act.get("reused_runs") else ""
    return [f"Test execution: {act['full_runs']} full run(s), {act['selected_runs']} "
            f"selected{reused} - {act['seconds']:,.0f}s of test time.{against}"]


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
    return [f"Overhead vs delivery: {floor}{ov['ratio']}:1 - {ov['overhead_s'] / 60:,.0f} min of "
            f"gate, review and repair against {ov['delivery_s'] / 60:,.0f} min of delivery, "
            f"within a measured {ov['total_s'] / 60:,.0f} min run.{excludes}",
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


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="The end-of-sprint report: delivered, cost, velocity.")
    p.add_argument("--root", default=".")
    sub = p.add_subparsers(dest="cmd", required=True)
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
