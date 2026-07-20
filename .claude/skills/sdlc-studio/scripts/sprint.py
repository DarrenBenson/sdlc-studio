#!/usr/bin/env python3
"""SDLC Studio sprint - batch selection and ordering.

`sprint plan` selects a batch of work by query (open bugs, proposed CRs, ready
stories) and orders it, so the operator sees the triage plan before the run starts.
Ordering is by priority/severity (Critical first); dependency-topological; and WSJF
(`--order wsjf`): **Cost of Delay divided by Points**, both on the modified Fibonacci scale.
CoD falls out of the declared Priority, so WSJF runs on any groomed backlog - it needs NO seat
scores, which is why it can now actually run. When the review seats HAVE scored a unit, their
value + time-criticality + risk-reduction replaces the derived CoD; the denominator is always
the unit's `Points`, because there is only one size vocabulary.

Under WSJF, priority is deliberately NOT the dominant axis: a job worth less but four times
cheaper does go first, and that is the whole economic content of WSJF. `--order priority` is
there for anyone who wants strict priority bands instead.

THE GATE REFUSES A UNIT ABOVE 8 POINTS (`sprint.points_split_above` to move the ceiling). Above
it the estimate is not worth having, and the answer is to DECOMPOSE - a triage decision, not an
estimation one. See the forecast block below for the measurement that demands it.

The forecast is sum(points) x a tokens-per-point rate MEASURED from this project's own evidence.
It carries the BATCH HISTORY (what sprints actually cost) beside it, and it names the evidence
the rate came from, so nobody has to take the number on trust.

The plan then SIZES the batch against the sprint's CAPACITY (`capacity.*`: tokens, wall-clock
minutes, units) and says whether it fits - at plan time, while the operator can still cut it,
rather than mid-run when the breaker halts the sprint. The same capacity resolves the run
APPETITE that `loop_guard budget` later breaks on, so the plan-time ceiling and the run-time
ceiling are ONE number and cannot disagree. Over budget is a WARNING, never a refusal: a script
cannot observe token spend, and the token model is a hypothesis, not a measurement.

The plan also EMITS the still-valid lessons digest (`lessons.plan_digest`): the lessons the
last sprints paid for arrive inside the plan the agent reads at sprint start, rather than as a
prose instruction to open a file that an agent under effort pressure skips. Read-only;
pure stdlib (lessons, telemetry and route are sibling helpers).
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import run_state, sdlc_md  # noqa: E402
import config  # noqa: E402  (sibling - routing block for tier enrichment)
import lessons  # noqa: E402  (sibling - the still-valid lessons digest carried in the plan)
import reconcile  # noqa: E402  (sibling - reconcile before plan)
import telemetry  # noqa: E402  (sibling - the forecast log the plan records its prediction in)
import blocker_sweep  # noqa: E402  (sibling - blocker sweep before plan)

PRIORITY_FIELD = {"bug": "Severity", "cr": "Priority", "story": "Priority"}
# One weight scale across types (documented in reference-sprint.md): bug Severity and
# CR/story Priority - including the P1-P4 form - map onto the same rank, so a merged
# bugs + CRs tranche orders on a single documented axis instead of two vocabularies.
PRIORITY_WEIGHT = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3,
                   "P1": 0, "P2": 1, "P3": 2, "P4": 3}

# ---------------------------------------------------------------------------
# COST OF DELAY: the WSJF numerator, derived from Priority, on the Fibonacci scale
# ---------------------------------------------------------------------------
# WSJF = Cost of Delay / Job Size, and this project already records both halves. The size is
# `Points` (the scale lives in lib/sdlc_md - one definition, read by everyone). The value half
# is the declared Priority/Severity, which is exactly what a Cost of Delay is: how much it
# costs to NOT do this yet.
#
# The old WSJF needed the review seats to have scored value, time-criticality and risk-reduction
# into `.local/wsjf-inputs.json` first. They almost never had, so WSJF almost never ran - and a
# signal that scores r = +0.03 against measured cost was quietly doing the ordering instead.
# A ranking that only works after a ceremony nobody performs is a ranking that does not work.
# This one runs on any groomed backlog.
#
# ONE RUNG PER BAND, on the same modified Fibonacci scale the points use. Each band is therefore
# worth about 1.6x the one below - the golden ratio the scale is built on - so a unit has to be
# more than ~1.6x bigger to lose a band of priority. That is the intended economics of WSJF and
# not an accident of the mapping: a 3-point High DOES outrank an 8-point Critical, because you
# can finish it and still start the Critical sooner than the Critical would have finished. An
# operator who wants strict priority bands has `--order priority`, which is what it is for.
COST_OF_DELAY = {"Critical": 13, "High": 8, "Medium": 5, "Low": 3,
                 "P1": 13, "P2": 8, "P3": 5, "P4": 3}
#: An unknown, blank or absent Priority ranks Medium - the same neutral rank `_weight` gives it.
#: A half-filled template field must plan, never crash the planner, and never rank itself first.
DEFAULT_COST_OF_DELAY = COST_OF_DELAY["Medium"]

# ---------------------------------------------------------------------------
# THE FORECAST: sum(points) x a MEASURED tokens-per-point rate. No base term.
# ---------------------------------------------------------------------------
# For the first time this number rests on a signal that predicts. A blind re-estimation
# recovered 21 delivered units AS FILED, stripped the declared size, and had three independent
# estimators size them in modified Fibonacci with no access to the outcomes:
#
#     Points (median of 3)    r = +0.68 pooled, +0.78 on units of 8 or below, and POSITIVE
#                             within every one of the four sprints
#     declared Effort (S/M/L) r = +0.35    retired: a second size vocabulary, and worse
#     max_cognitive           r = +0.03    dead, and it was ordering the batch
#
# A POINT IS A STABLE UNIT OF COST FROM 2 TO 8, and it BREAKS ABOVE THAT. Measured tokens per
# point, by band: 2-pt 22,370 | 3-pt 26,153 | 5-pt 27,396 | 8-pt 25,171 | 13-pt 14,144. The 13s
# are systematically OVER-estimated - 1.9x cheaper per point than every band below - and all
# three estimators returned them with LOW confidence and the words "should be split", unprompted.
# That is why the gate refuses above 8 (`points_split_above`): the ceiling is not a ceremony, it
# is the boundary of the region where the model is known to work.
#
# NO BASE TERM, DELIBERATELY. A least-squares fit adds one (8,043) and does WORSE: 11/19 units
# inside the 0.75x-1.25x band, 9/19 leave-one-out, against 12/19 for the flat rate with NO
# fitting at all. The simple model won on the evidence and it is not re-complicated here.
#
# THE RATE IS MEASURED, NOT FITTED, and it is re-measured from the project's own evidence every
# time a plan is built (`tokens_per_point`): the points a plan RECORDED, against the tokens the
# work actually cost. The seed below is the starting rate for a project with no evidence of its
# own yet, and the plan always says which of the two it is quoting.
POINTS_RATE_SEED = 25_000
POINTS_RATE_SEED_BASIS = (
    "the shipped default from a blind re-estimation of 21 delivered units, recovered as filed "
    "and sized in modified Fibonacci by three independent estimators with no access to the "
    "outcomes; 19 had measured actuals. A point measured 22,370-27,396 tokens across the 2-, "
    "3-, 5- and 8-point bands (~25,000, flat). No base term: fitting one does worse than not "
    "fitting at all. Your project's own evidence replaces this the moment it has enough")
#: Units of the project's OWN evidence before its measured rate replaces the seed. A rate
#: re-fitted to one or two units is fitting noise - a fit to one or two sprints has burned this
#: estimator before, and a wild single unit would drag the rate for the whole next sprint.
RATE_MIN_UNITS = 5

# ---------------------------------------------------------------------------
# What the rate was measured FROM - so a ratio can never be quoted as evidence for a model
# against the very data that produced it.
# ---------------------------------------------------------------------------
# A model's fit against its own training data is TRAINING ERROR. It lands near 1.0x by
# construction and it cannot be wrong, which is precisely why it reassures: an earlier estimator
# was quoted at 1.09x in-sample while it was running at 0.55x on live work.
#
# The sprints whose actuals the rate was read from are NAMED here, and every accuracy figure the
# planner quotes to an operator excludes them. Only a forecast made by the estimator in force, on
# a sprint that was NOT in the measurement, is evidence.
#
# CHANGE THIS IN THE SAME COMMIT THAT CHANGES THE RATE. It is declared per SPRINT, not per unit:
# the blind re-estimation read these four sprints' actuals, and naming a unit list this rate was
# never fitted to unit-by-unit would be inventing a precision the measurement does not have.
CALIBRATION_FIT_RETROS = ("RETRO0024", "RETRO0025", "RETRO0026", "RETRO0027")

# How a recorded sprint stands in relation to the estimator IN FORCE.
SAMPLE_IN = "in-sample"            # its actuals are the training data - training error, not evidence
SAMPLE_OUT = "out-of-sample"       # forecast by the constants in force, on data they never saw
SAMPLE_STALE = "stale-constants"   # forecast by a DIFFERENT estimator - judges that one, not this one
SAMPLE_MIXED = "mixed-constants"   # the batch was forecast by more than one estimator
SAMPLE_NONE = "unforecast"         # no plan-time forecast was recorded - it predicted nothing


def tokens_per_point(repo_root: Path | str | None = None) -> dict:
    """The tokens-per-point rate IN FORCE, MEASURED from this project's own evidence.

    The join is the closed loop: the points a plan RECORDED at plan time (the forecast log,
    first-record-wins, so hindsight cannot rewrite it) against the tokens the work ACTUALLY cost
    (the actuals log). Total tokens over total points - not the mean of the per-unit ratios,
    which would over-weight the small units.

    Below `RATE_MIN_UNITS` the project's own measurement is noise, and the seed stands: a rate
    re-fitted to one unit is exactly the mistake that produced two bad recalibrations. The count
    is REPORTED either way, so a reader can see how close the project is to owning its own rate.

    Fail-safe: unreadable evidence yields the seed, never an exception - a project must be able
    to plan before it has measured anything.
    """
    seed = {"rate": POINTS_RATE_SEED, "source": "seed", "units": 0, "points": 0, "tokens": 0,
            "ids": [], "min_units": RATE_MIN_UNITS, "basis": POINTS_RATE_SEED_BASIS}
    if repo_root is None:
        return seed
    try:
        forecasts = telemetry.forecasts(repo_root)
        actuals = telemetry.actuals(repo_root)
    except Exception as exc:  # noqa: BLE001 - no evidence must never break planning
        sdlc_md.debug("sprint.tokens_per_point", exc)
        return seed
    points = tokens = 0
    ids: list[str] = []
    for uid, fc in sorted(forecasts.items()):
        pts = fc.get("points")
        actual = (actuals.get(uid) or {}).get("tokens")
        if not isinstance(pts, int) or isinstance(pts, bool) or pts <= 0:
            continue
        if not isinstance(actual, (int, float)) or isinstance(actual, bool) or actual <= 0:
            continue
        points += pts
        tokens += int(actual)
        ids.append(uid)
    seed["units"], seed["points"], seed["tokens"], seed["ids"] = len(ids), points, tokens, ids
    if len(ids) < RATE_MIN_UNITS or not points:
        return seed          # counted, named, and NOT yet trusted
    return {"rate": int(round(tokens / points)), "source": "measured", "units": len(ids),
            "points": points, "tokens": tokens, "ids": ids, "min_units": RATE_MIN_UNITS,
            "basis": (f"measured from this project's evidence: {len(ids)} delivered unit(s), "
                      f"{points} point(s) forecast at plan time, {tokens:,} tokens actually "
                      f"spent (sdlc-studio/retros/evidence/)")}


def forecast_constants(repo_root: Path | str | None = None) -> dict:
    """The estimator, as a record. Stamped on every forecast at plan time so a later reader can
    tell WHICH model produced a number, instead of assuming it was this one.

    A row forecast by the OLD estimator (a flat per-unit rate scaled by a dead complexity axis)
    carries different keys entirely, so `sample_class` reads it as what it is: evidence about a
    different model, and not about this one.
    """
    return {"TOKENS_PER_POINT": tokens_per_point(repo_root)["rate"]}


# ---------------------------------------------------------------------------
# WHO estimated a unit, and under WHAT COMPULSION.
# ---------------------------------------------------------------------------
# The loop recorded a forecast and an actual, and never who made the size call. So it could tell
# an operator what estimation is like IN GENERAL - a population average from a study of other
# people - and could not tell them whether THEIR judgement was any good. Those are different
# questions, and only the second one is actionable. Low engagement and low capability produce an
# identical correlation in a population study, and the study cannot separate them; a per-person
# figure against measured actuals can.
#
# So the plan RECORDS the estimator, and the accuracy report is segmented by them. Feedback on
# your own past calls is the one intervention known to improve human estimation, and here it
# costs a field.
#
# It is NEVER INFERRED. With no `Estimated-by:` on the artefact and no project default, the
# estimate belongs to nobody - which is a fact, not a gap to be filled by guessing from whoever
# happened to file the ticket. Attributing a bad call to a person who did not make it is worse
# than attributing it to no one.
ESTIMATOR_UNATTRIBUTED = "unattributed"


def estimator_of(repo_root: Path | str, text: str) -> str:
    """WHO made the size call on this unit: the artefact's `Estimated-by:`, else the project's
    declared default, else `unattributed`."""
    raw = sdlc_md.extract_field(text, "Estimated-by")
    if raw and raw.strip() and raw.strip() not in ("-", "--"):
        name = (sdlc_md.parse_authorship_value(raw) or {}).get("name") or raw
        name = str(name).strip().strip("*_`")
        if name and not name.startswith("{{"):
            return name
    default = config.get(repo_root, "estimator.default", None)
    default = str(default or "").strip()
    return default or ESTIMATOR_UNATTRIBUTED


# Was an Effort COMPULSORY when it was written, or freely given? The coercion hazard turns on
# this, and it is only answerable if the answer is RECORDED: a compulsory estimate from someone
# who does not want to estimate is a careless estimate, and a careless number is worse than none.
EFFORT_GATE_COMPULSORY = "compulsory"  # the grooming gate refuses a unit with no size
EFFORT_GATE_VOLUNTARY = "voluntary"    # `sprint.breakdown: judgement` - the size is freely given
EFFORT_GATE_UNKNOWN = "unknown"        # recorded before the planner stamped the era


def effort_gate(repo_root: Path | str) -> str:
    """The compulsion in force RIGHT NOW, stamped on every forecast the plan records.

    Read from the grooming gate itself (`breakdown_mode`), not from a second copy of the rule:
    when the gate blocks an unsized unit, an Effort is compulsory, by definition."""
    return (EFFORT_GATE_COMPULSORY if breakdown_mode(repo_root) == "enforce"
            else EFFORT_GATE_VOLUNTARY)


def effort_gate_era(repo_root: Path | str, unit_id: str, stamped: str | None) -> str:
    """The era an Effort was recorded in. The STAMP on the forecast record wins - it was
    observed at the moment the plan read the field.

    For evidence recorded BEFORE the planner stamped the era, a project may DECLARE the
    boundary, per id prefix, in its own config:

        estimator:
          compulsory_after:
            BG: 136        # every bug filed after BG0136 had to carry an Effort

    A declaration, in the project's config, that a human can be held to - not an inference from
    a timestamp. A commit date is when the work was COMMITTED, not when the size was written,
    and guessing the era from one would put units on the wrong side of the very split the
    comparison exists to make. With neither a stamp nor a declaration the era is UNKNOWN, and an
    unknown-era unit is reported as its own cohort rather than quietly filed on one side.
    """
    if stamped in (EFFORT_GATE_COMPULSORY, EFFORT_GATE_VOLUNTARY):
        return stamped
    cutoffs = config.get(repo_root, "estimator.compulsory_after", None)
    if not isinstance(cutoffs, dict) or not cutoffs:
        return EFFORT_GATE_UNKNOWN
    uid = sdlc_md.norm_id(str(unit_id or ""))
    m = re.match(r"([A-Za-z]+)", uid)
    num = sdlc_md.id_number(uid)
    if not m or num is None:
        return EFFORT_GATE_UNKNOWN
    cut = {str(k).upper(): v for k, v in cutoffs.items()}.get(m.group(1).upper())
    try:
        cut = sdlc_md.parse_cutoff(cut)
    except Exception:  # noqa: BLE001 - a malformed cutoff declares nothing; it never guesses
        return EFFORT_GATE_UNKNOWN
    if cut is None:
        return EFFORT_GATE_UNKNOWN
    return EFFORT_GATE_COMPULSORY if num > cut else EFFORT_GATE_VOLUNTARY


def sample_class(retro_id: str | None, constants: dict | None,
                 repo_root: Path | str | None = None) -> str:
    """Is this recorded sprint evidence about the estimator in force, or is it its own fit?

    Derived at READ time from two facts the row carries - which sprint it is, and which
    constants produced its forecast - never from a label frozen when the row was written. A
    re-measurement that adds a sprint to the training set therefore reclassifies that sprint's
    row immediately, instead of leaving it quoted as validation for a model it helped fit.
    """
    rid = (retro_id or "").strip().upper()
    if constants == SAMPLE_MIXED:
        return SAMPLE_MIXED
    if not isinstance(constants, dict) or not constants:
        return SAMPLE_NONE
    try:
        same = all(int(constants.get(k, -1)) == v
                   for k, v in forecast_constants(repo_root).items())
    except (TypeError, ValueError):
        return SAMPLE_NONE
    # IN-SAMPLE (training error) requires BOTH that this sprint's actuals are in the current fit
    # AND that the constants which MADE its forecast are the current ones. A row forecast by an
    # OLDER estimator, whose actuals were LATER folded into the current fit, is a GENUINE
    # out-of-sample falsification of the estimator that made it - not training error.
    # Gating the fit-membership check on `same` is what stops a recalibration from relabelling the
    # very falsifications that justified it: RETRO0025/0026 (forecast by the retired base/tpc
    # estimator) judge THAT estimator, so they read stale-constants, never in-sample.
    if same:
        in_fit = bool(rid) and rid in {r.upper() for r in CALIBRATION_FIT_RETROS}
        return SAMPLE_IN if in_fit else SAMPLE_OUT
    return SAMPLE_STALE


# ---------------------------------------------------------------------------
# Sprint capacity: ONE operator-set budget, TWO consumers.
# ---------------------------------------------------------------------------
# The plan-time question ("does this batch fit?") and the run-time circuit breaker
# ("stop, the appetite is spent") were two numbers that could disagree: an operator could plan a
# 12-unit batch and then watch the breaker halt it at 8, mid-sprint. They are now one number.
# `capacity.*` is the source; the appetite is RESOLVED ONCE, here, at plan time, and stamped on
# the run state - which is exactly what `loop_guard budget` reads back at each unit boundary. So
# the ceiling the plan checked the batch against IS the ceiling that stops the run.
#
# PROVISIONAL. These defaults are round numbers over one measured sprint (6 units, 384,278
# tokens actual, RETRO0024), not a calibration. `retro.velocity_history` accumulates a row per
# sprint; once it has CALIBRATION_MIN_SPRINTS rows a human re-reads the trend and decides
# whether the numbers have earned a change. NOTHING here re-fits anything automatically - a fit
# to one or two sprints would fit noise.
DEFAULT_CAPACITY = {"tokens": 500_000, "minutes": 240, "units": 8}

# The honest error band on the token forecast, and it is WIDE on purpose.
#
# Points predict cost well (r = +0.68), but "well" is not "tightly": the held-out batch ratios in
# the blind re-estimation were 0.98x, 1.47x, 0.84x and 0.82x, and one sprint in four fell outside
# 0.75x-1.25x. +/-50% is the floor that spread implies; observed out-of-sample ratios in the
# velocity history WIDEN it and never narrow it, because one sprint agreeing with the model is not
# evidence the model is tight.
FORECAST_BAND = 0.50

# Sprints of recorded velocity before the history is worth recalibrating the constants against.
# Below this the plan says so, and changes nothing.
CALIBRATION_MIN_SPRINTS = 5


def capacity(repo_root: Path | str) -> dict:
    """The configured per-sprint capacity: tokens, wall-clock minutes, unit count.

    0 on an axis means that axis is unbounded (the pre-capacity behaviour). A malformed value
    degrades to the shipped default rather than crashing the planner."""
    out: dict = {}
    for axis, default in DEFAULT_CAPACITY.items():
        try:
            out[axis] = max(0, int(config.get(repo_root, f"capacity.{axis}", default)))
        except (TypeError, ValueError):
            out[axis] = default
    return out


def resolve_appetite(repo_root: Path | str, cli_minutes: float | None = None,
                     cli_units: int | None = None) -> dict:
    """The run appetite in force, resolved ONCE - at plan time, from the capacity budget.

    Per axis, most specific first: the CLI flag, then an explicitly configured `appetite.*`
    (non-zero; the pre-capacity key, still honoured), then the sprint capacity. The resolved
    pair is what the plan checks the batch against AND what `sprint plan --write` stamps on the
    run state for `loop_guard budget` to break on. One number, two consumers.
    """
    cap = capacity(repo_root)

    def pick(flag, axis: str) -> tuple:
        if flag is not None:
            return flag, f"--appetite-{axis}"
        legacy = config.get(repo_root, f"appetite.{axis}", 0) or 0
        if legacy:
            return legacy, f"config appetite.{axis}"
        return cap[axis], f"config capacity.{axis}"

    minutes, m_src = pick(cli_minutes, "minutes")
    units, u_src = pick(cli_units, "units")
    return {"minutes": float(minutes or 0), "units": int(units or 0),
            "minutes_source": m_src, "units_source": u_src}


def calibration(repo_root: Path | str) -> dict:
    """What the velocity history says about the forecast the plan is about to quote -
    OUT-OF-SAMPLE, and nothing else.

    A row whose actuals the constants in force were fitted to is training error. Quoting it as
    the estimator's observed accuracy is how the planner came to reassure the operator with
    1.09x while the estimator was actually running at 0.55x on live work. So an in-sample row
    is counted, named, and EXCLUDED - from the reported ratio and from the band.

    REPORTS, never re-fits. `low`/`high` are multipliers on the point forecast that bound the
    plausible actual: FORECAST_BAND is the floor, and any observed OUT-OF-SAMPLE estimate/actual
    ratio widens them (an actual of estimate/ratio). A history that agrees with the model does
    not shrink the band - agreeing once is not evidence of precision.
    """
    rows: list[dict] = []
    try:
        import retro  # noqa: PLC0415 - deferred: the planner must not pay for the retro import graph
        rows = retro.velocity_history(repo_root)
    except Exception as exc:  # noqa: BLE001 - no history must never break planning
        sdlc_md.debug("sprint.calibration", exc)
    by_class: dict[str, list[dict]] = {}
    for r in rows:
        by_class.setdefault(sample_class(r.get("id"), r.get("constants"), repo_root),
                            []).append(r)
    evidence = [r for r in by_class.get(SAMPLE_OUT, [])
                if isinstance(r.get("ratio"), (int, float)) and r["ratio"] > 0]
    ratios = [float(r["ratio"]) for r in evidence]
    low, high = 1.0 - FORECAST_BAND, 1.0 + FORECAST_BAND
    if ratios:
        low = min(low, 1.0 / max(ratios))
        high = max(high, 1.0 / min(ratios))
    excluded = {k: len(v) for k, v in by_class.items() if k != SAMPLE_OUT}
    return {"sprints": len(evidence), "ratios": ratios,
            "low": round(low, 2), "high": round(high, 2),
            "in_sample": len(by_class.get(SAMPLE_IN, [])),
            "unforecast": len(by_class.get(SAMPLE_NONE, [])),
            "stale_constants": len(by_class.get(SAMPLE_STALE, [])),
            "excluded": excluded,
            "recalibrate_after": CALIBRATION_MIN_SPRINTS,
            "enough_history": len(evidence) >= CALIBRATION_MIN_SPRINTS,
            "note": "out-of-sample rows only. A row whose actuals the constants were fitted to "
                    "is training error and is excluded: it lands near 1.0x by construction. "
                    "Nothing is re-fitted automatically"}


def _unit_wall_minutes(cal_rows: list[dict]) -> float | None:
    """Mean per-unit SUBAGENT wall time from the velocity history, in minutes, or None.

    A lower bound on a run, never a forecast of it: the history records the time the workers
    spent, not the elapsed clock of the run around them (orchestration, reviews, operator
    STOPs). It is reported as a floor so nobody reads it as the answer."""
    total_s = sum(r["wall_time_s"] for r in cal_rows
                  if isinstance(r.get("wall_time_s"), (int, float)))
    units = sum(r["measured"] for r in cal_rows if isinstance(r.get("measured"), (int, float)))
    if not total_s or not units:
        return None
    return round(total_s / units / 60.0, 1)


def capacity_report(repo_root: Path | str, batch: list[dict], forecast: dict | None,
                    appetite: dict) -> dict:
    """Does this batch fit the sprint's capacity? Answered AT PLAN TIME, as a WARNING.

    Never a gate. A script cannot observe token spend (see telemetry.py), so a token ceiling
    would depend on the actor self-reporting the budget meant to constrain it; and the forecast
    itself is mis-calibrated out-of-sample by ~30%. Refusing to plan on a number that soft would
    be false authority. The real breaker is wall-clock/unit-count, and it fires on the SAME
    appetite reported here.
    """
    root = Path(repo_root)
    cap = capacity(root)
    cal = calibration(root)
    tokens = int((forecast or {}).get("tokens") or 0)
    units = len(batch)
    token_budget = cap["tokens"]
    unit_budget = appetite["units"]        # the number the run breaker will actually stop on
    minute_budget = appetite["minutes"]    # ditto

    over: list[str] = []
    if token_budget and tokens > token_budget:
        over.append("tokens")
    if unit_budget and units > unit_budget:
        over.append("units")
    low, high = int(tokens * cal["low"]), int(tokens * cal["high"])
    return {
        "budget": {"tokens": token_budget, "minutes": minute_budget, "units": unit_budget},
        "forecast": {"tokens": tokens, "low": low, "high": high},
        "units": units,
        "over": over,
        "over_budget": bool(over),
        # under budget on the point estimate, but the top of the honest band is not
        "tokens_may_exceed": bool(token_budget and "tokens" not in over and high > token_budget),
        "appetite": appetite,
        "calibration": cal,
        "unit_wall_minutes_floor": _unit_wall_minutes(_velocity_rows(root)),
        "advisory": True,
        "basis": "a WARNING, never a gate - a script cannot observe token spend, and the "
                 "forecast is a hypothesis. The run breaker is wall-clock/unit-count, on the "
                 "same appetite reported here",
    }


def _velocity_rows(repo_root: Path | str) -> list[dict]:
    """The raw velocity rows (fail-safe: [] when there is no history or retro cannot load)."""
    try:
        import retro  # noqa: PLC0415
        return retro.velocity_history(repo_root)
    except Exception as exc:  # noqa: BLE001
        sdlc_md.debug("sprint._velocity_rows", exc)
        return []


def _weight(pri: str) -> int:
    """Shared cross-type rank of a Severity/Priority value (case-tolerant; decorations
    like `High (gate)` use the leading token). Unknown, blank, or absent values rank
    Medium - a half-filled template field must plan, never crash the planner."""
    toks = (pri or "").strip().split()
    if not toks:
        return 2
    tok = toks[0].rstrip(":,;")
    key = tok.upper() if re.fullmatch(r"[Pp]\d", tok) else tok.title()
    return PRIORITY_WEIGHT.get(key, 2)


def _affects_files(text: str) -> list[str]:
    """File paths a unit declares it will touch (delegates to the shared parser in
    lib/sdlc_md so the planner and the routing estimator count the same files)."""
    return sdlc_md.affects_files(text)


def _resolve(root: Path, p: str) -> Path | None:
    """Resolve an Affects path (delegates to the shared resolver in lib/sdlc_md)."""
    return sdlc_md.resolve_affects(root, p)


def _dep_ids(value: str) -> set:
    """The leading artifact-ID tokens of a `Depends on` field, normalised.

    Stops at the first non-ID word, so prose like "see US0001 for background" or
    "supersedes US0001" does not become a hard ordering dependency. Handles
    comma/space-separated lists and a trailing parenthetical (`US0003 (note)`).
    """
    ids: set = set()
    for tok in re.split(r"[,\s]+", value.strip()):
        if not tok:
            continue
        m = sdlc_md.ID_RE.match(tok)  # anchored at the start of the token
        if not m:
            break  # first non-ID token ends the dependency list
        ids.add(sdlc_md.norm_id(m.group(0)))
    return ids


def _rank_key(it: dict):
    """Tiebreak order among ready units: highest WSJF first, else priority, then id.

    THE COMPLEXITY TIE-BREAK IS GONE. It used to sit here, between priority and id, so
    the running order within a priority band was decided by `max_cognitive` - a number measured
    at r = +0.03 against actual cost, under a docstring vouching that "the smaller blast-radius
    job goes first". It measured how complicated the FILE was, never how big the JOB was.
    Shortest-job-first is a sound heuristic; it just needs a size signal that is real, and it now
    has one - so it does the work up in the WSJF denominator, where a size signal belongs.

    With no WSJF (priority order, or a unit the grooming opt-out let through unsized) the order
    falls to id: arbitrary, and honestly so. Arbitrary beats meaningful-looking and arbitrary.
    Shared by topo order + waves.
    """
    w = _weight(it["priority"])
    if "wsjf" in it:
        return (-it["wsjf"], w, it["id"])
    return (w, it["id"])


def _build_dag(items: list[dict], deps: dict[str, set]) -> tuple[dict, dict, dict]:
    """(by_id, adjacency dep->dependents, indegree) over the in-batch dependency graph."""
    by_id = {sdlc_md.norm_id(it["id"]): it for it in items}
    adj: dict[str, set] = {k: set() for k in by_id}
    indeg: dict[str, int] = {k: 0 for k in by_id}
    for k in by_id:
        for dep in deps.get(k, ()):
            if dep in by_id and dep != k and k not in adj[dep]:
                adj[dep].add(k)        # dep must come before k
                indeg[k] += 1
    return by_id, adj, indeg


def _topo_waves(items: list[dict], deps: dict[str, set]) -> list[list[dict]]:
    """Dependency LEVELS: wave 0 = units with no in-batch deps; wave n+1 = units all of
    whose in-batch deps sit in waves <= n. Units in one wave are independent (parallelisable),
    ordered within the wave by `_rank_key`. Raises ValueError naming a dependency cycle."""
    by_id, adj, indeg = _build_dag(items, deps)
    waves: list[list[dict]] = []
    placed = 0
    current = sorted([k for k in by_id if indeg[k] == 0], key=lambda k: _rank_key(by_id[k]))
    while current:
        waves.append([by_id[k] for k in current])
        placed += len(current)
        nxt: list[str] = []
        for k in current:
            for m in adj[k]:
                indeg[m] -= 1
                if indeg[m] == 0:
                    nxt.append(m)
        current = sorted(nxt, key=lambda k: _rank_key(by_id[k]))
    if placed != len(by_id):
        raise ValueError("dependency cycle among: "
                         + ", ".join(sorted(k for k in by_id if indeg[k] > 0)))
    return waves


def _topo_order(items: list[dict], deps: dict[str, set]) -> list[dict]:
    """Dependency-topological order - a unit follows its in-batch deps - with
    priority/severity (then id) as the tiebreak among ready units. A dependency on
    a unit outside the batch is ignored here (the tranche audit reports it as
    unmet-deps). Raises ValueError naming the units in a dependency cycle.
    """
    by_id, adj, indeg = _build_dag(items, deps)

    def rank(k: str):
        return _rank_key(by_id[k])

    ready = sorted([k for k in by_id if indeg[k] == 0], key=rank)
    order: list[dict] = []
    while ready:
        k = ready.pop(0)
        order.append(by_id[k])
        for m in adj[k]:
            indeg[m] -= 1
            if indeg[m] == 0:
                ready.append(m)
        ready.sort(key=rank)
    if len(order) != len(by_id):
        raise ValueError("dependency cycle among: " + ", ".join(sorted(k for k in by_id if indeg[k] > 0)))
    return order


def cost_of_delay(priority: str) -> int:
    """The WSJF numerator for a declared Priority/Severity, on the Fibonacci scale.

    Case-tolerant, and tolerant of a decorated value (`High (gate)`) exactly as `_weight` is -
    the two read the same field and must never disagree about what it says. An unknown, blank or
    absent value is Medium: a half-filled template field must plan, and it must not rank itself
    first by accident.
    """
    toks = (priority or "").strip().split()
    if not toks:
        return DEFAULT_COST_OF_DELAY
    tok = toks[0].rstrip(":,;")
    key = tok.upper() if re.fullmatch(r"[Pp]\d", tok) else tok.title()
    return COST_OF_DELAY.get(key, DEFAULT_COST_OF_DELAY)


def wsjf_score(cod: float, points: float) -> float:
    """WSJF = Cost of Delay / Points. Points >= 1 (the scale has no zero, and a zero
    denominator would make the cheapest possible job out of a unit nobody sized)."""
    return round(cod / max(points, 1), 3)


def _seat_cost_of_delay(inp: dict) -> float:
    """The seats' Cost of Delay: value + time-criticality + risk-reduction, the classic
    three-part CoD. Missing parts score 0 - a component the seats did not discuss adds
    nothing, and must not be imputed."""
    return sum(float(inp.get(k, 0) or 0)
               for k in ("value", "time_criticality", "risk_reduction"))


def _wsjf_inputs(root: Path) -> dict:
    """Per-unit value/time-criticality/risk-reduction the review seats scored, written
    to `sdlc-studio/.local/wsjf-inputs.json` by the model after the PO/Eng/QA consult. Keyed by
    normalised id.

    An OPTIONAL override of the CoD the planner derives from Priority, and nothing more: absent
    (the normal case) the WSJF still runs, because Priority is always there. The seats do NOT
    supply a size - `Points` is the one size vocabulary, and a second one is what this change
    removed."""
    raw = sdlc_md.read_json(root / "sdlc-studio" / ".local" / "wsjf-inputs.json", {})
    return {sdlc_md.norm_id(k): v for k, v in raw.items()} if isinstance(raw, dict) else {}


def _collect(root: Path, kind: str, status: str,
             epic_filter: set | None) -> tuple[list[dict], dict[str, set]]:
    """One kind+status query: (items, in-batch dependency map)."""
    vocab = sdlc_md.status_vocab(kind, root)
    # canonicalise the user-supplied status arg so a lowercase '--crs proposed' (the
    # documented form) matches the title-case vocab token, instead of silently selecting nothing.
    target = sdlc_md.canonical_status(status, vocab) or status
    if vocab and target not in vocab:
        raise ValueError(
            f"status '{status}' is not a {kind} status; valid: {', '.join(vocab)}")
    out: list[dict] = []
    deps: dict[str, set] = {}
    for path in sdlc_md.artifact_files(kind, root):
        text = path.read_text(encoding="utf-8")
        st = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab) or "Unknown"
        if st != target:
            continue
        if epic_filter is not None:  # scope to the named epic(s)
            ef = sdlc_md.extract_field(text, "Epic") or ""
            m = sdlc_md.ID_SEARCH_RE.search(ef)
            if not (m and sdlc_md.norm_id(m.group(0)) in epic_filter):
                continue
        out.append(_unit(kind, path, text, st, deps))
    return out, deps


def _unit(kind: str, path: Path, text: str, st: str, deps: dict[str, set]) -> dict:
    pri = sdlc_md.extract_field(text, PRIORITY_FIELD.get(kind, "Priority")) or "Medium"
    rid = sdlc_md.extract_record_id(path.stem) or path.stem
    dval = sdlc_md.extract_field(text, "Depends on") or sdlc_md.extract_field(text, "Depends On") or ""
    deps[sdlc_md.norm_id(rid)] = _dep_ids(dval)
    return {"id": rid, "type": kind, "status": st, "priority": pri, "path": str(path)}


def _worklist_units(root: Path, worklist: str) -> tuple[list[dict], dict[str, set]]:
    """The documented tranche-file batch source: one unit id per line (markdown
    bullets and `#` comment/heading lines are tolerated). Every id must resolve to
    an artifact on disk - a silent skip would ship a smaller tranche than approved."""
    lines = Path(worklist).read_text(encoding="utf-8").splitlines()
    wanted: list[str] = []
    for ln in lines:
        ln = ln.strip().lstrip("-*").strip()
        if not ln or ln.startswith("#"):
            continue
        m = sdlc_md.ID_SEARCH_RE.search(ln)
        if m:
            wanted.append(sdlc_md.norm_id(m.group(0)))
    wanted = list(dict.fromkeys(wanted))  # a repeated id is one unit, in every order mode
    by_id: dict[str, tuple[Path, str]] = {}
    for kind in sdlc_md.ARTIFACT_TYPES:
        for path in sdlc_md.artifact_files(kind, root):
            rec = sdlc_md.extract_record_id(path.stem)
            if rec and sdlc_md.norm_id(rec) in set(wanted):
                by_id[sdlc_md.norm_id(rec)] = (path, kind)
    missing = [w for w in wanted if w not in by_id]
    if missing:
        raise ValueError(f"worklist ids not found on disk: {', '.join(missing)}")
    out: list[dict] = []
    deps: dict[str, set] = {}
    for w in wanted:
        path, kind = by_id[w]
        text = path.read_text(encoding="utf-8")
        st = sdlc_md.canonical_status(
            sdlc_md.extract_field(text, "Status"),
            sdlc_md.status_vocab(kind, root)) or "Unknown"
        out.append(_unit(kind, path, text, st, deps))
    return out, deps


def _enrich_routing(root: Path, out: list[dict]) -> None:
    """Per-unit routing enrichment, for EVERY order mode: `difficulty` is
    always stamped (advisory info); `tier` + `model` only when `routing.enabled` in
    the project config. Fail-safe per unit: an estimator exception degrades that unit
    to no routing fields - routing must never break planning."""
    try:
        import route  # sibling - deferred so a broken estimator can't break import
        routing = config.get(root, "routing", None) or {}
    except Exception:  # noqa: BLE001
        return
    enabled = bool(routing.get("enabled"))
    for it in out:
        try:
            est = route.estimate(root, Path(it["path"]))
            it["difficulty"] = {"score": est["difficulty_score"],
                                 "band": est["difficulty_band"],
                                 "confidence": est["confidence"]}
            if enabled:
                picked = route.pick(root, Path(it["path"]), role="author",
                                    routing=routing)
                it["tier"] = picked["tier"]
                it["model"] = picked["model"]
        except Exception:  # noqa: BLE001 - degrade this unit, keep planning
            continue


def _order_batch(root: Path, out: list[dict], deps: dict[str, set], order: str,
                 skip_personas: bool) -> list[dict]:
    """WSJF enrichment + dependency-topological ordering over one (possibly mixed) batch.

    WSJF = Cost of Delay / Points, and it needs NOTHING but the artefact: the CoD falls out of
    the declared Priority, and the Points are on the unit (the grooming gate refuses a batch
    where they are not). Seat scores, when they exist, replace the derived CoD - they never
    replace the size, because there is one size vocabulary and the seats do not speak a second.

    A unit with NO points scores no WSJF and falls to priority order. That is only reachable
    through the recorded `sprint.breakdown: judgement` opt-out - and it is the honest outcome:
    a unit nobody sized cannot be ranked by size.
    """
    _enrich_routing(root, out)  # difficulty always; tier/model when routing.enabled
    if order == "wsjf":
        seat_inputs = {} if skip_personas else _wsjf_inputs(root)
        for it in out:
            text = Path(it["path"]).read_text(encoding="utf-8")
            points = sdlc_md.read_points(text)
            if points is None:
                continue                       # unsized: no WSJF, and nothing is invented
            it["points"] = points
            inp = seat_inputs.get(sdlc_md.norm_id(it["id"]))
            if inp:
                it["value"] = inp.get("value", 0)
                it["time_criticality"] = inp.get("time_criticality", 0)
                it["risk_reduction"] = inp.get("risk_reduction", 0)
                it["cod"] = _seat_cost_of_delay(inp)
                it["cod_source"] = "seats"
            else:
                it["cod"] = cost_of_delay(it["priority"])
                it["cod_source"] = "priority"
            it["wsjf"] = wsjf_score(it["cod"], points)
    if order in ("priority", "wsjf"):
        out = _topo_order(out, deps)
    return out


def select_batches(repo_root: Path | str, queries: list[tuple[str, str]],
                   order: str = "priority", skip_personas: bool = False,
                   epics: set[str] | None = None) -> list[dict]:
    """The union of one or more kind+status queries as ONE merged, ordered batch -
    a mixed bugs + CRs tranche is first-class, and a cross-type `Depends on` edge
    (CR depends on BG) orders and waves like any other."""
    root = Path(repo_root)
    epic_filter = {sdlc_md.norm_id(e) for e in epics} if epics else None
    out: list[dict] = []
    deps: dict[str, set] = {}
    for kind, status in queries:
        items, d = _collect(root, kind, status, epic_filter if kind == "story" else None)
        out.extend(items)
        deps.update(d)
    return _order_batch(root, out, deps, order, skip_personas)


def select_batch(repo_root: Path | str, kind: str, status: str, order: str = "priority",
                 skip_personas: bool = False, epics: set[str] | None = None) -> list[dict]:
    """Files of `kind` whose Status matches, with priority, ordered. Single-query
    wrapper over `select_batches` - see there for ordering semantics."""
    return select_batches(repo_root, [(kind, status)], order,
                          skip_personas=skip_personas, epics=epics)


def _token_forecast(root: Path, batch: list[dict]) -> dict:
    """The batch's token cost: SUM OF THE POINTS x a MEASURED tokens-per-point rate.

    A per-unit forecast, and for the first time an honest one: points predict measured cost at
    r = +0.68 (+0.78 at 8 points and below), where every computed signal this project tried
    failed - the one the forecast used to run on scored +0.03. A point is a stable unit of cost
    across the whole legal range, because the gate refuses the range where it stops being one.

    STRICTLY LINEAR IN POINTS. There is no base term, and adding one is a regression, not an
    improvement: a least-squares fit produces an 8,043 base and lands 11/19 units in band
    (9/19 leave-one-out) against 12/19 for the flat rate with no fitting at all.

    An ESTIMATE and never a gate: a script cannot observe real token spend (see telemetry.py), so
    a token ceiling would depend on the actor self-reporting the budget meant to constrain it.
    The wall-clock / unit-count appetite is the breaker; this only informs the operator.

    Each unit's record carries the POINTS it was priced from - which is what lets the NEXT plan
    measure the rate from this one's outcome - plus the ATTRIBUTION of the size call: WHO made it
    (`estimator`) and under what compulsion (`effort_gate`: the size gate's compulsion, whose key
    name predates Points). Both are recorded at PLAN TIME, when the field was read, for the same
    reason the number is: a size read off the artefact months later may have been revised with
    hindsight, and a value revised after the outcome is not a prediction.

    A unit with no points is NOT priced at some stand-in - it is named in `unpriced` and left out
    of the total. Only the recorded grooming opt-out can produce one, and a batch that opted out
    of being sized does not get a forecast that pretends otherwise.
    """
    rate_info = tokens_per_point(root)
    rate = rate_info["rate"]
    per_unit: dict[str, int] = {}
    units: dict[str, dict] = {}
    unpriced: list[str] = []
    total_points = 0
    gate = effort_gate(root)   # the compulsion in force for this whole plan
    for it in batch:
        text = Path(it["path"]).read_text(encoding="utf-8")
        uid = sdlc_md.norm_id(it["id"])
        points = it.get("points")
        if points is None:  # priority/manual order never stamped one - read it here
            points = sdlc_md.read_points(text)
        if points is None:
            unpriced.append(uid)
            continue
        total_points += points
        per_unit[uid] = points * rate
        units[uid] = {"tokens": points * rate, "points": points, "rate": rate,
                      "rate_source": rate_info["source"],
                      "estimator": estimator_of(root, text), "size_gate": gate}
    return {"tokens": total_points * rate, "points": total_points, "per_unit": per_unit,
            "units": units, "rate": rate, "rate_source": rate_info["source"],
            "rate_units": rate_info["units"], "rate_basis": rate_info["basis"],
            "unpriced": unpriced, "history": batch_history(root),
            "constants": forecast_constants(root),
            "basis": "sum(points) x a tokens-per-point rate measured from the evidence (never "
                     "fitted, and with no base term - fitting one does worse). Points predict "
                     "measured cost at r = +0.68, and +0.78 at 8 points and below, which is the "
                     "range the gate allows. An ESTIMATE, never a gate - a script cannot observe "
                     "token spend"}


def batch_history(repo_root: Path | str) -> list[dict]:
    """What sprints have ACTUALLY cost, per sprint, oldest first - the plan's real cost input.

    This is what the operator should plan against, and the forecast above is what they should
    treat with suspicion. "The last two five-unit sprints cost 642k and 902k" is a defensible
    basis for sizing a third. A per-unit number derived from a signal that correlates with cost
    at r = +0.03 is not, and quoting one lent the plan an authority the measurement never had.

    Read-only, from the recorded velocity history. Fail-safe: no history is an empty list, never
    an exception - a project with no measured sprints yet must still be able to plan.
    """
    out: list[dict] = []
    for r in _velocity_rows(repo_root):
        actual, units = r.get("actual_tokens"), r.get("measured")
        if not isinstance(actual, (int, float)) or not actual:
            continue
        if not isinstance(units, (int, float)) or not units:
            continue
        out.append({"id": r.get("id"), "units": int(units), "tokens": int(actual),
                    "per_unit": int(actual / units)})
    return out


def record_forecast(repo_root: Path | str, data: dict) -> dict:
    """RECORD what this plan predicted, per unit, WHEN it predicted it.

    Unconditional - not behind `--write`. A forecast that is only written when someone
    remembers a flag is a forecast that does not exist, and the retro is then left to
    re-derive one from whatever the constants say by then. That is not a prediction, and a
    loop built on it cannot falsify its own estimator.

    Each record carries the number, the POINTS it was priced from, and the CONSTANTS that
    produced it, so a later reader can tell which estimator to credit or blame. It also carries
    WHO made the size call and under what compulsion, which is what makes per-estimator accuracy
    - and the coercion comparison - answerable from the evidence instead of from opinion. First
    record for a unit wins on read (telemetry.forecasts), so a re-plan cannot rewrite it with
    hindsight.

    The `points` on the record are what CLOSE the loop: the next plan measures its rate by
    dividing the tokens these units actually cost by the points recorded here, before the work
    started. A points value re-read off the artefact afterwards would be an estimate revised with
    hindsight, and it would quietly drive the ratio towards 1.0x.
    """
    fc = data.get("token_forecast") or {}
    units = fc.get("units") or {}
    if not units:
        return {"recorded": [], "already": [], "path": None}
    constants = fc.get("constants") or forecast_constants(repo_root)
    when = data.get("generated_at") or sdlc_md.now_iso8601()
    recs = [{"id": uid, "tokens": u["tokens"], "points": u["points"],
             "estimator": u.get("estimator"), "size_gate": u.get("size_gate"),
             "constants": constants, "planned_at": when}
            for uid, u in units.items()]
    return telemetry.record_forecasts(repo_root, recs)


# ---------------------------------------------------------------------------
# The breakdown gate: a plan over an UNGROOMED or UNSPLITTABLE batch is REFUSED.
# ---------------------------------------------------------------------------
# A plan that looks authoritative over units nobody was required to groom is the false
# authority this gate exists to abolish. A unit with no `Points` cannot be forecast at all,
# and a unit that names no files cannot be checked against its neighbours - the planner
# cannot see that two of them touch the SAME FILE, so it reports them as safely parallel
# when they will collide. Both gaps were closed by hand before every plan.
#
# The gate also refuses a unit sized ABOVE the split ceiling. That one is not about grooming
# but about triage: the unit IS sized, honestly, and the honest size says nobody could size
# it. See `points_split_above`.
#
# Enforcement lives HERE, in the command people actually invoke. A separate grooming step
# that nobody runs is doctrine, and doctrine is what gets skipped under effort pressure: the
# grooming rung that already exists, and is specified to produce a reviewable estimated
# backlog, has never once been run. So `plan` refuses instead of warning: an advisory lane is
# the one that gets scrolled past.
#
# The escape is a RECORDED DECISION, never an omission: `sprint.breakdown: judgement` in the
# project config makes the lane report instead of block. Absence of config means BLOCK, and an
# unreadable or unknown mode is not an escape either - it falls back to enforce.
BREAKDOWN_MODES = ("enforce", "judgement")

# A CR at or above this many declared files, or sized at the split ceiling, is doing enough work
# to warrant stories: only a story carries executable `Verify:` lines, so an un-decomposed CR's
# Done is gated on prose. Advisory - "where the work warrants" is a judgement the report can only
# name.
DECOMPOSE_FILE_THRESHOLD = 5


def breakdown_mode(repo_root: Path | str) -> str:
    """`enforce` (the default) or the recorded opt-out `judgement`. Never fails open."""
    mode = str(config.get(repo_root, "sprint.breakdown", "enforce") or "enforce").strip().lower()
    return mode if mode in BREAKDOWN_MODES else "enforce"


def points_split_above(repo_root: Path | str) -> int:
    """The point ceiling a unit must be SPLIT above. `sdlc_md.POINTS_SPLIT_ABOVE` (8) unless the
    project has recorded a different one in `sprint.points_split_above`.

    Configurable because 8 is where the evidence broke for THIS project's units, and another
    team's 8 is not this one's. A project that finds 8-point units too chunky to deliver in one
    go tightens to 5, and the gate refuses more. Raising it is a recorded decision too - and it
    is a decision to forecast in a range where the estimate is known to fall apart (the 13s came
    in 1.9x cheaper per point than every band below).

    A malformed or non-positive value degrades to the shipped ceiling rather than disabling the
    gate: a gate that a typo can switch off is not a gate.
    """
    try:
        value = int(config.get(repo_root, "sprint.points_split_above",
                               sdlc_md.POINTS_SPLIT_ABOVE))
    except (TypeError, ValueError):
        return sdlc_md.POINTS_SPLIT_ABOVE
    return value if value > 0 else sdlc_md.POINTS_SPLIT_ABOVE


def _affect_key(root: Path, p: str) -> str:
    """One file, one key - however the path was written.

    A declared path is resolved where it exists, so `scripts/x.py` and the same file spelled
    from the repo root are ONE file for clustering. An unresolvable (not-yet-existing) path
    keeps its declared spelling rather than being dropped: a new file two units both create is
    still a collision."""
    r = _resolve(root, p)
    if r is not None:
        try:
            return str(r.relative_to(root))
        except ValueError:
            return str(r)
    return re.sub(r"^\./", "", p.strip())


def _declared_size(text: str) -> int | None:
    """The size a PERSON recorded for this unit: its `Points`, on the modified Fibonacci scale.
    None when the field is absent, or carries a value the scale does not have.

    ONE source, because there is one size vocabulary (lib/sdlc_md owns the scale and the parser).
    A seat estimate is no longer accepted here: the seats price VALUE, and a second size
    vocabulary living beside the first is exactly what this change deleted. Nor is an `unknown`
    an answer any more - the scale IS the estimate, and it is relative ("is this bigger than that
    one"), so a person who has delivered anything at all can place a unit on it."""
    return sdlc_md.read_points(text)


# SIZE BY WHAT A THING IS. A delivery unit (story, bug) is MEASURED, so it carries story points.
# A container/request (CR, RFC, epic) is DECOMPOSED before it is delivered, so it carries a coarse
# T-shirt Size instead - a request is not a unit of work until it is broken down, and pointing it
# is guessing at a shape that does not exist yet. The grooming gate therefore demands the RIGHT
# size per type: `Points` for a story or bug, a T-shirt `Size` for a CR or RFC.
TSHIRT_SIZED_TYPES = frozenset({"cr", "rfc", "epic"})


def _declared_tshirt(text: str) -> str | None:
    """The T-shirt Size (S/M/L/XL) a container/request declares, or None. `lib/sdlc_md` owns the
    scale and the parser, exactly as it does for points - one vocabulary, one reader."""
    return sdlc_md.read_size(text)


def _shared_file_clusters(files_by_unit: dict[str, list[str]]) -> list[dict]:
    """Units that touch the SAME FILE are ONE cluster, not independent parallel work.

    Derived from the `Affects` the planner already parses. The dependency graph knows only what
    someone DECLARED in `Depends on:`; a shared file is a FACT, and two units editing one file
    collide whether or not anyone declared it. Union-find over the shared files; a unit that
    shares nothing is not a cluster."""
    parent = {uid: uid for uid in files_by_unit}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    by_file: dict[str, list[str]] = {}
    for uid, files in files_by_unit.items():
        for f in files:
            by_file.setdefault(f, []).append(uid)
    for uids in by_file.values():
        for other in uids[1:]:
            union(uids[0], other)
    groups: dict[str, list[str]] = {}
    for uid in files_by_unit:
        groups.setdefault(find(uid), []).append(uid)
    out: list[dict] = []
    for members in groups.values():
        if len(members) < 2:
            continue
        members = sorted(members)
        shared = sorted(f for f, uids in by_file.items() if len(set(uids) & set(members)) > 1)
        out.append({"units": members, "files": shared})
    return sorted(out, key=lambda c: c["units"])


def _ids_cited_by_stories(root: Path) -> set:
    """Every artifact id any story mentions - so a CR a story already actions is not flagged
    for decomposition a second time."""
    cited: set = set()
    for path in sdlc_md.artifact_files("story", root):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:  # noqa: PERF203 - an unreadable story must not break planning
            sdlc_md.debug("sprint._ids_cited_by_stories", exc)
            continue
        for m in sdlc_md.ID_SEARCH_RE.finditer(text):
            cited.add(sdlc_md.norm_id(m.group(0)))
    return cited


def breakdown(repo_root: Path | str, batch: list[dict], skip_personas: bool = False) -> dict:
    """Is this batch GROOMED enough to plan? The census the gate refuses on.

    A unit is plannable when it declares the files it will touch (`Affects`) and carries the
    size its TYPE is sized by - `Points` for a story or bug (the delivery units), a T-shirt
    `Size` for a CR or RFC (the requests/containers). A pointed unit is additionally refused when
    its points are ABOVE the split ceiling: a triage rule, not an estimation one - above the
    ceiling the estimate is not worth having (the 13s in the blind re-estimation were
    over-estimated by 1.9x per point, and all three estimators said so unprompted), and the
    answer is to DECOMPOSE the unit rather than estimate it harder. A T-shirt Size has no number
    and no ceiling; a container's answer to "too big" is always decomposition.

    `ungroomed` and `oversized` are counted separately because they are different failures with
    different fixes: one unit was never sized, the other was sized honestly and is too big.
    Everything else the lane surfaces - shared-file clusters, CRs big enough to warrant stories -
    falls out of the same fields at no extra cost to the operator. Read-only: it reports, and
    `cmd_plan` decides what to do about it."""
    root = Path(repo_root)
    cited = _ids_cited_by_stories(root)
    ceiling = points_split_above(root)
    # The story-level Definition of Ready, when the project declares one, decides WHICH of
    # the grooming checks enforce (absent document = shipped defaults, byte-compatible).
    # A criterion whose tag the project removed is downgraded to human-judged - reported
    # visibly below, never skipped silently.
    dor = sdlc_md.dor_dod_level_checks(root, "ready", "story")
    def _enforced(check_id: str) -> bool:
        return dor is None or check_id in dor
    downgraded = [] if dor is None else sorted(
        c for c in ("grooming.affects", "grooming.points", "grooming.split")
        if c not in dor)
    ungroomed: list[dict] = []
    oversized: list[dict] = []
    groomed: list[str] = []
    files_by_unit: dict[str, list[str]] = {}
    decompose: list[dict] = []
    for it in batch:
        try:
            text = Path(it["path"]).read_text(encoding="utf-8")
        except OSError as exc:  # noqa: PERF203
            sdlc_md.debug("sprint.breakdown", exc)
            continue
        declared = _affects_files(text)
        # BG0144: a declared `Affects` must name at least one file that RESOLVES on disk. A unit
        # whose declared paths ALL fail to resolve is sized against a fictional list - a typo, or a
        # stale rename - and every downstream consumer then treats a guess wearing a path as a
        # sized unit. A path to a file the unit will CREATE cannot resolve yet, so SOME unresolved
        # paths are legitimate; ALL of them is the error. Unresolvable paths are named either way.
        unresolvable = [p for p in declared if _resolve(root, p) is None]
        points = _declared_size(text)
        files_by_unit[it["id"]] = sorted({_affect_key(root, p) for p in declared})
        # The size demanded depends on WHAT the unit is. A story/bug is groomed by `Points`; a
        # CR/RFC by a T-shirt `Size`. LEGACY TOLERANCE: a CR filed before this rule carries
        # `Points` and no `Size` (the earlier gate forced it) - it still counts as sized, so the
        # transition never invalidates the backlog. A T-shirt `Size` is never read as a number.
        if it["type"] in TSHIRT_SIZED_TYPES:
            sized = _declared_tshirt(text) is not None or points is not None
            size_field = "Size"
        else:
            sized = points is not None
            size_field = "Points"
        missing = (([] if declared or not _enforced("grooming.affects") else ["Affects"])
                   + ([] if sized or not _enforced("grooming.points") else [size_field]))
        # All declared paths unresolvable = a fictional Affects. Named so the author can
        # fix the typo. Not applied when Affects is absent (that is the plainer "Affects" miss).
        if declared and len(unresolvable) == len(declared) and _enforced("grooming.affects"):
            missing = missing + [f"Affects (no declared path resolves: {', '.join(unresolvable)})"]
        if missing:
            ungroomed.append({"id": it["id"], "type": it["type"], "path": it["path"],
                              "missing": missing, "unresolvable": unresolvable})
        elif points is not None and points > ceiling and _enforced("grooming.split"):
            # Only a POINTED unit can be over the split ceiling; a T-shirt Size has no number to
            # be above it. A legacy CR carrying points is judged by the same ceiling it always was.
            oversized.append({"id": it["id"], "type": it["type"], "path": it["path"],
                              "points": points, "ceiling": ceiling})
        else:
            groomed.append(it["id"])
        if it["type"] == "cr" and sdlc_md.norm_id(it["id"]) not in cited:
            big = points is not None and points >= ceiling
            wide = len(declared) >= DECOMPOSE_FILE_THRESHOLD
            if big or wide:
                why = (f"{points} points" if big else f"touches {len(declared)} files")
                decompose.append({"id": it["id"], "why": why})
    mode = breakdown_mode(root)
    return {"mode": mode, "blocking": mode != "judgement",
            "ungroomed": ungroomed, "oversized": oversized, "groomed": groomed,
            "ceiling": ceiling, "downgraded": downgraded,
            "clusters": _shared_file_clusters(files_by_unit),
            "decompose": decompose,
            "triage": _batch_triage(root, [it["id"] for it in batch]),
            "ok": not ungroomed and not oversized}


def _batch_triage(root: Path, batch_ids: list[str]) -> dict:
    """The JUDGEMENT triage lenses (duplicate/subsumed, stale, orphaned-dependency) that touch a
    unit in this batch - surfaced in the plan the operator already reads. Reporting-only: a
    duplicate is a judgement call the human makes, unlike an ungroomed unit. OVERSIZED is excluded
    here because the breakdown gate above already owns it (and blocks on it). Best-effort - a
    triage error must never break planning.

    Returns `{findings, skipped}`: `skipped` is the count of backlog artefacts the scan could
    not read, propagated from `backlog_triage.triage` so an unreadable file is logged in the plan
    ceremony rather than silently truncating the batch into a clean-looking plan (the module's
    own contract, which status already honours)."""
    try:
        import backlog_triage
        report = backlog_triage.triage(root)
    except Exception as exc:  # noqa: BLE001 - the plan must survive a triage hiccup
        sdlc_md.debug("sprint._batch_triage", exc)
        return {"findings": [], "skipped": 0}
    want = {sdlc_md.norm_id(b) for b in batch_ids}
    findings = [f for f in report["findings"] if f["lens"] != "oversized"
                and want & {sdlc_md.norm_id(u) for u in f["units"]}]
    return {"findings": findings, "skipped": report.get("skipped", 0)}


DEFAULT_SEAT_STALE_DAYS = 7  # advisory window; seat judgement does not rot on a clock


def _seat_provenance(root: Path, batch: list[dict]) -> dict:
    """Which units the review seats scored, and how fresh wsjf-inputs.json is.

    The inputs file is a cross-sprint side-channel: a later plan silently
    re-reads what an earlier consult wrote, so the plan must say whose
    judgement it consumed and from when, at the STOP where the operator
    signs off. Staleness is advisory only, never a refusal."""
    path = root / "sdlc-studio" / ".local" / "wsjf-inputs.json"
    inputs = _wsjf_inputs(root)
    scored = [it["id"] for it in batch if sdlc_md.norm_id(it["id"]) in inputs]
    unscored = [it["id"] for it in batch if sdlc_md.norm_id(it["id"]) not in inputs]
    written_at = None
    age_days = None
    if path.exists():
        import datetime as _dt
        mtime = path.stat().st_mtime
        written_at = _dt.datetime.fromtimestamp(mtime).astimezone().isoformat(timespec="seconds")
        # clamp at 0: a future-dated file (clock skew on a shared checkout)
        # must not report a negative age
        age_days = max(0.0, round((_dt.datetime.now().timestamp() - mtime) / 86400.0, 1))
    try:
        window = int(sdlc_md.project_override(
            root, "sprint.wsjf_inputs_stale_days", DEFAULT_SEAT_STALE_DAYS))
    except (TypeError, ValueError):
        window = DEFAULT_SEAT_STALE_DAYS
    return {"file": str(path), "written_at": written_at, "age_days": age_days,
            "stale_after_days": window,
            "stale": bool(age_days is not None and age_days > window),
            "scored": scored, "unscored": unscored}


def build_plan(repo_root: Path | str, kind: str | None = None, status: str | None = None,
               order: str = "priority", skip_personas: bool = False,
               epics: set[str] | None = None, queries: list[tuple[str, str]] | None = None,
               worklist: str | None = None, appetite_minutes: float | None = None,
               appetite_units: int | None = None) -> dict:
    """The triage plan: the ordered batch, a count, and (for ordered modes) the dependency
    WAVES - the parallelisable levels operators otherwise hand-derive. The batch source is
    a single kind+status, composed `queries`, or a `worklist` file (ids one per line).

    The plan also sizes the batch against the sprint CAPACITY and resolves the run appetite
    from it, so the ceiling the operator is shown at plan time is the ceiling the run breaker
    later stops on."""
    root = Path(repo_root)
    if worklist is not None:
        batch, deps = _worklist_units(root, worklist)
        batch = _order_batch(root, batch, deps, order, skip_personas)
        queries = [("worklist", worklist)]
    else:
        if queries is None:
            queries = [(kind, status)]
        batch = select_batches(root, queries, order, skip_personas=skip_personas, epics=epics)
    waves = None
    deps_declared: bool | None = None  # None for manual order (no wave computation)
    if order in ("priority", "wsjf") and batch:
        deps = {}
        for it in batch:
            text = Path(it["path"]).read_text(encoding="utf-8")
            dval = (sdlc_md.extract_field(text, "Depends on")
                    or sdlc_md.extract_field(text, "Depends On") or "")
            deps[sdlc_md.norm_id(it["id"])] = _dep_ids(dval)
        # batch already passed _topo_order above, so the graph is acyclic here.
        waves = [[it["id"] for it in w] for w in _topo_waves(batch, deps)]
        # whether ANY in-batch dependency edge was declared - a flat single wave with no
        # edges is parallel because no one declared a `Depends on:`, not because none exist.
        deps_declared = any(deps[k] & set(deps) for k in deps)
    forecast = _token_forecast(root, batch) if batch else None
    appetite = resolve_appetite(root, appetite_minutes, appetite_units)
    return {
        "generated_at": sdlc_md.now_iso8601(),
        "kind": "+".join(k for k, _ in queries),
        "status": ", ".join(str(s) for _, s in queries),
        "queries": [{"kind": k, "status": s} for k, s in queries],
        "order": order,
        "batch": batch,
        "count": len(batch),
        "waves": waves,
        "deps_declared": deps_declared,
        # Is the batch GROOMED enough to plan at all? `cmd_plan` REFUSES on this (unless the
        # project has recorded the `judgement` opt-out) - and it also carries the shared-file
        # clusters the declared dependency graph cannot see.
        "breakdown": breakdown(root, batch, skip_personas) if batch else None,
        "seat_provenance": (_seat_provenance(root, batch)
                            if order == "wsjf" and not skip_personas else None),
        # A token cost FORECAST for the batch (estimate, never a gate - see _token_forecast).
        "token_forecast": forecast,
        # Does the batch FIT? Sized against the sprint capacity at PLAN time - and carrying the
        # run appetite resolved from that same capacity, so the two cannot disagree.
        "capacity": capacity_report(root, batch, forecast, appetite),
        # The lessons the last sprints paid for, IN the plan the agent reads at sprint start.
        # A plan that merely pointed at LESSONS-SUMMARY.md relied on the agent opening it.
        "lessons": lessons.plan_digest(root),
        # The cross-project tier, ranked. It had NO automatic reader: recall was a prose
        # instruction, and prose instructions are the ones that get skipped.
        "cross_lessons": lessons.cross_digest(root),
        # What each unit must satisfy to close, and the checks every commit meets - so the
        # requirements arrive as a briefing rather than as refusals one gate run at a time.
        "gate_briefing": build_gate_briefing(root, batch),
    }


GOALS = ("triage", "plan", "design", "done")  # the goal ladder a run is driven along


def pending_handoff(repo_root: Path | str) -> dict | None:
    """The handoff the LAST run left, when it left one - so the plan that follows a stopped
    run starts from its tail instead of re-deriving it. None when there is no handoff, or
    its worklist is gone.

    `remaining` is what the handoff NAMES; `plannable` is what `--worklist` can resolve
    (a remaining unit with no file on disk is named in the document and cannot be planned).
    The two are reported separately: collapsing them would understate the tail."""
    state = run_state.read(repo_root)
    hid, rel = state.get("handoff"), state.get("handoff_worklist")
    if not hid or not rel:
        return None
    path = Path(rel)
    if not path.is_absolute():
        path = Path(repo_root) / rel
    if not path.exists():
        return None
    ids = [ln for ln in path.read_text(encoding="utf-8").splitlines()
           if ln.strip() and not ln.strip().startswith("#")]
    return {"id": hid, "worklist": str(path), "plannable": len(ids),
            "remaining": state.get("handoff_remaining", len(ids)),
            "outcome": state.get("outcome")}


def build_authoring_plan(repo_root: Path | str, prd_path: str) -> dict:
    """The greenfield authoring plan: the batch source is a PRD, not existing units.
    The planner validates the PRD and signals **authoring mode**; the decomposition itself
    (PRD -> epics -> stories) is the model-instructed phase the loop runs next. It
    cannot enumerate epics/stories here - they do not exist yet."""
    prd = Path(prd_path)
    if not prd.exists():
        raise FileNotFoundError(f"PRD not found: {prd_path}")
    return {
        "generated_at": sdlc_md.now_iso8601(),
        "mode": "authoring",
        "prd": str(prd),
        "next": "decompose the PRD into epics, then Ready stories (the authoring phase); "
                "stop at the epic-cut STOP for approval before authoring stories",
        "count": 0,
        "lessons": lessons.plan_digest(repo_root),  # a greenfield start is a sprint start too
        # A greenfield project has no lessons of its own - so the inherited registry is the
        # ONLY tier that can help it, and the one it most needs.
        "cross_lessons": lessons.cross_digest(repo_root),
    }


def pre_plan_blocker_sweep(repo_root: Path | str) -> dict:
    """Pre-plan step: surface units whose blockers have cleared so newly-unblocked work is
    eligible for the batch, mirroring the reconcile-before-plan gate. Advisory and fail-safe -
    it proposes Blocked -> Ready candidates and never transitions or blocks planning (US0050)."""
    try:
        return blocker_sweep.sweep(repo_root)
    except Exception:  # noqa: BLE001 - the sweep is advisory; never break planning on its failure
        return {"now_unblocked": [], "still_blocked": [], "errors": []}


def _git(root, *args, timeout: int = 30):
    import subprocess
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                              text=True, timeout=timeout)
    except Exception:  # noqa: BLE001 - git absent/hung must never break planning
        return None


def _has_origin(root) -> bool:
    r = _git(root, "remote")
    return bool(r) and r.returncode == 0 and "origin" in r.stdout.split()


def _default_branch(root) -> str:
    """The origin default branch, or `main`. Thin alias for the shared
    `next_id.origin_default_branch` so the resolution logic lives in one place."""
    import next_id
    return next_id.origin_default_branch(Path(root))


def origin_drift(root, do_fetch: bool = True) -> dict:
    """Compare local HEAD to origin's default branch so a sprint is not planned against a stale
    checkout. Fetches first (best-effort) unless `do_fetch=False`. Returns
    {remote, behind, paths, branch}. Fail-safe: no origin, no git, or any error -> remote False,
    behind 0 (identical to today's behaviour - no false positives)."""
    out = {"remote": False, "behind": 0, "paths": [], "branch": None}
    if not _has_origin(root):
        return out
    out["remote"] = True
    if do_fetch:
        _git(root, "fetch", "origin", "--quiet")            # best-effort; ignore failure
    br = _default_branch(root)
    out["branch"] = br
    cnt = _git(root, "rev-list", "--count", f"HEAD..origin/{br}")
    if cnt and cnt.returncode == 0:
        try:
            out["behind"] = int(cnt.stdout.strip() or 0)
        except ValueError:
            out["behind"] = 0
    if out["behind"]:
        names = _git(root, "diff", "--name-only", f"HEAD..origin/{br}")
        if names and names.returncode == 0:
            out["paths"] = [p for p in names.stdout.splitlines() if p.strip()]
    return out


def _batch_paths(root, batch_ids) -> set:
    """Repo-relative file paths of the batch's units, for overlap against incoming remote
    changes (does the drift touch a file this batch also allocates/edits)."""
    root = Path(root)
    want = {sdlc_md.norm_id(i) for i in batch_ids}
    paths = set()
    for t in sdlc_md.ARTIFACT_TYPES:
        for p in sdlc_md.artifact_files(t, root):
            rid = sdlc_md.extract_record_id(p.stem)
            if rid and sdlc_md.norm_id(rid) in want:
                try:
                    paths.add(str(p.relative_to(root)))
                except ValueError:
                    paths.add(str(p))
    return paths


def _drift_warning(drift: dict, batch_paths: set) -> str | None:
    """A warning line when local is behind origin, naming the commit-count and any overlap
    between the incoming remote changes and the batch's own artifact files (the collision the
    incident hit). None when up to date."""
    if not drift.get("behind"):
        return None
    overlap = sorted(p for p in drift["paths"] if p in batch_paths)
    msg = (f"origin drift: local is {drift['behind']} commit(s) behind origin/{drift['branch']} "
           f"- fetch and rebase before planning (a stale checkout can mint an id the remote "
           f"already used)")
    if overlap:
        msg += f"; incoming changes touch batch artifacts: {', '.join(overlap)}"
    return msg


def _preplan_reconcile(args: argparse.Namespace, kinds: list[str]) -> int | None:
    """Reconcile-before-plan: a plan must read a drift-free census (file Status vs its index
    row). Mechanical drift only; semantic staleness still needs the audit. Prints a warning and,
    under --strict, returns 2 to abort; otherwise None."""
    drift = []
    for k in kinds:
        try:
            drift += [(k, d) for d in reconcile.detect_type(k, Path(args.root)).get("drift", [])]
        except Exception:  # noqa: BLE001 - reconcile is advisory here, never block planning on its failure
            pass
    if drift:
        names = ", ".join(sorted({k for k, _ in drift}))
        print(f"reconcile: {len(drift)} drift item(s) in the {names} index(es) - reconcile before "
              f"planning (the plan reads file Status; a stale index misleads selection)",
              file=sys.stderr)
        if getattr(args, "strict", False):
            return 2
    return None


def _origin_drift_preflight(args: argparse.Namespace, data: dict) -> int | None:
    """Planning against a stale checkout can mint an id the remote already used, or plan over an
    artifact a teammate has changed. Fetch + compare; warn (refuse under --strict). Fail-safe: git
    absent/slow/odd never breaks planning. Returns 2 to abort under --strict, else None."""
    try:
        drift = origin_drift(args.root, do_fetch=not getattr(args, "no_fetch", False))
        # `waves` is None for manual order and empty batches (the key is always present) - `or []`
        # keeps the preflight alive on exactly those paths (a swallowed TypeError here silently
        # disabled the --strict refusal).
        batch_ids = [u for wave in (data.get("waves") or []) for u in wave]
        warn = _drift_warning(drift, _batch_paths(args.root, batch_ids))
        if warn:
            print(warn, file=sys.stderr)
            if getattr(args, "strict", False):
                return 2
    except (OSError, subprocess.SubprocessError, ValueError, KeyError):
        # Advisory: only the EXPECTED failure modes are contained; a programming error surfaces.
        pass
    return None


def _render_seat_provenance(data: dict) -> None:
    """The WSJF seat-provenance lines: whose judgement the order consumed, and how fresh."""
    prov = data.get("seat_provenance")
    if not prov:
        return
    if prov["scored"]:
        when = f", inputs written {prov['written_at']}" if prov["written_at"] else ""
        print(f"  seats: {len(prov['scored'])}/{data['count']} unit(s) seat-scored{when}")
    if prov["unscored"]:
        print(f"  no seat inputs (priority fallback): {', '.join(prov['unscored'])} - "
              f"seat-score them via an amigo consult writing "
              f"sdlc-studio/.local/wsjf-inputs.json (reference-sprint.md, Seat-scored WSJF)")
    if prov["stale"]:
        print(f"  advisory: wsjf-inputs.json is {prov['age_days']} day(s) old "
              f"(window {prov['stale_after_days']}) - re-run the amigo consult "
              f"if these scores no longer reflect current judgement")


def _render_waves(data: dict) -> None:
    """The parallelisable dependency levels, or the flat priority list when there are no waves."""
    if data.get("waves"):
        for i, wave in enumerate(data["waves"], 1):
            par = " (parallel)" if len(wave) > 1 else ""
            print(f"  wave {i}{par}: {', '.join(wave)}")
        # a flat single wave of >1 unit with no declared deps is not 'no dependencies exist' - it
        # is undeclared. Flag it so the operator grooms `Depends on:` (the --goal design rung).
        if data.get("deps_declared") is False and data["count"] > 1:
            print("  hint: all units are parallel because no `Depends on:` is declared "
                  "- groom inter-story dependencies (the --goal design rung) for real waves")
    else:
        for b in data["batch"]:
            print(f"  {b['id']} [{b['priority']}]")


def _render_clusters(data: dict) -> None:
    """Shared-file clusters, and the waves they falsify.

    A `Depends on:` edge is a DECLARATION; a shared file is a FACT. The wave computation only
    knows the declarations, so it has called two units parallel while both rewrote one module.
    The cluster is printed with the plan, and a wave holding more than one member of the same
    cluster is called out as NOT safely parallel."""
    bd = data.get("breakdown") or {}
    clusters = bd.get("clusters") or []
    if not clusters:
        return
    print("  shared-file clusters (one cluster = one file in common, so NOT parallel):")
    for c in clusters:
        shown = ", ".join(c["files"][:3])
        more = f" (+{len(c['files']) - 3} more)" if len(c["files"]) > 3 else ""
        print(f"    {', '.join(c['units'])} -> {shown}{more}")
    for i, wave in enumerate(data.get("waves") or [], 1):
        for c in clusters:
            both = [u for u in wave if u in set(c["units"])]
            if len(both) > 1:
                print(f"  warning: wave {i} is NOT safely parallel - {', '.join(both)} touch "
                      f"{', '.join(c['files'][:2])}. Run them in sequence, or declare "
                      f"`Depends on:` so the waves say so.", file=sys.stderr)


def _render_decompose(data: dict) -> None:
    """CRs doing enough work to warrant stories. Only a story carries executable `Verify:`
    lines, so an un-decomposed CR of this size reaches Done on prose alone."""
    items = (data.get("breakdown") or {}).get("decompose") or []
    if not items:
        return
    print("  decompose into stories (only a story's Done is gated on executable ACs):")
    for it in items:
        print(f"    {it['id']} ({it['why']}) -> `cr action {it['id']}`")


def _render_downgrades(data: dict) -> None:
    """Grooming checks the project's Definition of Ready downgraded to human judgement.
    The downgrade is the document's right; doing it INVISIBLY is not - a bar lowered
    without a trace is the silent-weakening class the documents exist to prevent."""
    downgraded = (data.get("breakdown") or {}).get("downgraded") or []
    if downgraded:
        print(f"  grooming downgraded to human-judged by definition-of-ready.md "
              f"(tag removed): {', '.join(downgraded)}")


def _breakdown_detail(bd: dict) -> list[str]:
    """The ungroomed units, one line each: which unit, what it lacks, where it lives."""
    return [f"    {u['id']:<8} lacks: {', '.join(u['missing']):<15} {u['path']}"
            for u in bd["ungroomed"]]


BREAKDOWN_FIX = """  fix each one on the artefact, then re-plan:
    Affects   > **Affects:** path/to/file.py, path/to/other.py
              the files the unit will touch. Without it nothing can size the unit, and
              nothing can see that two units touch the same file.
    Points    > **Points:** 3
              the job size on the modified Fibonacci scale ({scale}) - not its urgency,
              and not a guess at hours. It is RELATIVE: is this bigger than the last 3 you
              delivered? Nothing else is accepted: a 7 is the false precision the scale
              exists to prevent, and above {ceiling} the unit must be SPLIT, not estimated.
  see the whole grooming list, read-only:  sprint.py breakdown {sel}
  opt out ONLY as a recorded decision: set `sprint.breakdown: judgement` in
  sdlc-studio/.config.yaml and this lane reports instead of blocking. Omission is not an
  escape - an absent config BLOCKS."""

SPLIT_FIX = """  split each one into units of {ceiling} points or fewer, then re-plan:
    `cr action <id>` decomposes a CR into stories; a story that big is two stories.
    Each piece gets its OWN Points, and they do NOT have to sum to the original - the
    whole reason the estimate was refused is that nobody could size the thing in one go.
  tighten or move the ceiling as a RECORDED decision, in sdlc-studio/.config.yaml:
    sprint:
      points_split_above: 5    # this team finds 8-point units too chunky
  raising it is a decision to forecast where the model is known to break - the 13s came in
  1.9x cheaper per point than every band below, and all three blind estimators returned
  them with low confidence and the words "should be split"."""


def _refuse_ungroomed(bd: dict, count: int, sel: str) -> None:
    """The refusal. It is the only message the operator gets, so it teaches: what is wrong,
    why a plan over it would be worse than no plan, exactly how to fix each unit, and how to
    opt out on purpose."""
    n = len(bd["ungroomed"])
    print(f"sprint plan REFUSED: {n} of {count} unit(s) are ungroomed. NO PLAN WAS PRINTED.\n",
          file=sys.stderr)
    print("  A plan over unsized units is false authority. A unit with no Points cannot be\n"
          "  forecast at all, a unit that names no files cannot be checked for collisions,\n"
          "  and the planner then reports two units as safely parallel when they will\n"
          "  collide. A plan you cannot trust is worse than no plan.\n",
          file=sys.stderr)
    print("  ungroomed:", file=sys.stderr)
    print("\n".join(_breakdown_detail(bd)), file=sys.stderr)
    print(_breakdown_fix(bd, sel), file=sys.stderr)


def _breakdown_fix(bd: dict, sel: str) -> str:
    return BREAKDOWN_FIX.format(
        sel=sel, ceiling=bd.get("ceiling", sdlc_md.POINTS_SPLIT_ABOVE),
        scale=", ".join(str(p) for p in sdlc_md.POINTS_SCALE))


def _oversized_detail(bd: dict) -> list[str]:
    """The units over the ceiling, one line each: which unit, how big, where it lives."""
    return [f"    {u['id']:<8} {u['points']:>3} points  (ceiling {u['ceiling']})  {u['path']}"
            for u in bd["oversized"]]


def _refuse_oversized(bd: dict, count: int) -> None:
    """The split refusal. A unit above the ceiling is REFUSED - not warned about - because the
    warning was already tried: the estimators who sized these units said "should be split",
    unprompted, and the sprint that shipped one is the sprint whose forecast missed."""
    n = len(bd["oversized"])
    ceiling = bd["ceiling"]
    print(f"sprint plan REFUSED: {n} of {count} unit(s) are above {ceiling} points. "
          f"NO PLAN WAS PRINTED.\n", file=sys.stderr)
    print(f"  Above {ceiling} points the estimate is not worth having, and the answer is to\n"
          f"  DECOMPOSE the unit - not to estimate it harder. That is a TRIAGE decision, not\n"
          f"  an estimation one. A point is a stable unit of cost up to {ceiling} (22k-27k\n"
          f"  tokens per point, measured) and stops being one above it: the 13-point units in\n"
          f"  the blind re-estimation came in at 14,144 per point, 1.9x cheaper, and all three\n"
          f"  estimators returned them with LOW confidence saying they should be split. The one\n"
          f"  sprint whose forecast missed its band is the one that contained a 13.\n",
          file=sys.stderr)
    print("  too big:", file=sys.stderr)
    print("\n".join(_oversized_detail(bd)), file=sys.stderr)
    print(SPLIT_FIX.format(ceiling=ceiling), file=sys.stderr)


def _refuse_requests(requests: list[dict]) -> None:
    """The G1 refusal. A sprint plans the DELIVERY backlog; an RFC/CR/Issue is a DISCOVERY-backlog
    item with no executable ACs to close on. Naming the decompose path is the point - the refusal
    is only useful if it says how to turn the discovery item into plannable work (a request is
    refined, an Issue triaged)."""
    n = len(requests)
    print(f"sprint plan REFUSED: {n} unit(s) are DISCOVERY items, not deliverable work. "
          f"NO PLAN WAS PRINTED.\n", file=sys.stderr)
    print("  An RFC, a CR or an Issue is a DISCOVERY-backlog item, not a unit of work. It has\n"
          "  no executable acceptance criteria to close on, so it can be neither sprinted nor\n"
          "  verified Done. A sprint plans the DELIVERY backlog: stories and bugs.\n",
          file=sys.stderr)
    print("  discovery items:", file=sys.stderr)
    for it in requests:
        print(f"    {it['id']:8} {it['type']:5} {it['path']}", file=sys.stderr)
    print("\n  decompose each into the delivery units it produces, then plan THOSE:\n"
          "    a request (RFC/CR):  refine.py apply --request <id> --epic-title ... --story ...\n"
          "    an Issue:            triage.py apply --issue <ISxxxx> --bug 'title|points|severity'\n"
          "  the discovery item's own status then becomes terminal by DERIVATION when its children\n"
          "  are resolved (transition refuses to assert it). See `status backlog` for both backlogs.",
          file=sys.stderr)


def _report_oversized(bd: dict, count: int) -> None:
    """The recorded opt-out still REPORTS an oversized unit; it just does not block."""
    print(f"breakdown: {len(bd['oversized'])} of {count} unit(s) are above "
          f"{bd['ceiling']} points and should be SPLIT - planning anyway "
          f"(sprint.breakdown: judgement). Their forecast is outside the range the rate was "
          f"measured in:", file=sys.stderr)
    print("\n".join(_oversized_detail(bd)), file=sys.stderr)


def _report_ungroomed(bd: dict, count: int) -> None:
    """The recorded opt-out (`sprint.breakdown: judgement`): the lane still REPORTS, it just
    does not block. An opt-out that also went quiet would be the disease, not the cure."""
    n = len(bd["ungroomed"])
    print(f"breakdown: {n} of {count} unit(s) are ungroomed - planning anyway "
          f"(sprint.breakdown: judgement). They carry NO forecast at all - an unsized unit is "
          f"left out of the batch total rather than priced at a stand-in:", file=sys.stderr)
    print("\n".join(_breakdown_detail(bd)), file=sys.stderr)


# Lessons printed in the text plan before the tail is elided. One line per lesson costs
# roughly 40 tokens, so the whole of a mature registry fits inside a rounding error on a
# sprint plan; the cap exists to bound the display, not to ration the content. Growth is
# handled by decay (`revalidate` closes what no longer holds), never by silent truncation.
PLAN_DIGEST_MAX = 50

# The cross-project registry is ranked, so a cap here drops the LEAST-biting lessons, not
# an arbitrary tail. The top of this list is what the next mistake is most likely to be.
CROSS_DIGEST_MAX = 12


def _render_triage(data: dict) -> None:
    """The judgement triage lenses, printed with the plan so a dirty backlog is seen BEFORE it is
    planned FROM. Reporting-only - the human decides whether a suspected duplicate is really one -
    so it prints its findings and does not refuse. Silence here means the batch is coherent, EXCEPT
    when a backlog file could not be read: a drop is logged rather than passed off as clean."""
    bd = data.get("breakdown") or {}
    triage = bd.get("triage") or {}
    findings = triage.get("findings") or []
    skipped = triage.get("skipped") or 0
    if not findings and not skipped:
        return
    if findings:
        print(f"  backlog triage: {len(findings)} item(s) to resolve before planning FROM this "
              f"batch (judgement calls - not a refusal):")
        for f in findings:
            print(f"    [{f['lens']}] {f['detail']}")
    if skipped:
        print(f"  backlog triage: {skipped} artefact(s) unreadable - not triaged "
              f"(fix the header, then re-plan)")


def _render_lessons(data: dict) -> None:
    """The still-valid lessons, printed IN the plan. The sprint-start read was doctrine -
    a prose instruction to open a file - so it was skipped; here it arrives unasked, in the
    output the agent already reads. (The JSON form carries every lesson, uncapped.)"""
    digest = data.get("lessons")
    if not digest:
        return
    if digest["stale"]:  # the close gate FAILS on this; at plan time it is a loud warning
        print(f"  warning: {digest['reason']}", file=sys.stderr)
    if not digest["lessons"]:
        return
    print(f"  lessons in force ({digest['count']}) - read before starting:")
    for item in digest["lessons"][:PLAN_DIGEST_MAX]:
        gist = f" - {item['gist']}" if item["gist"] else ""
        print(f"    {item['id']}: {item['title']}{gist}")
    if digest["count"] > PLAN_DIGEST_MAX:
        print(f"    (+{digest['count'] - PLAN_DIGEST_MAX} more - `lessons revalidate` closes "
              f"the ones that no longer hold)")


def _render_cross_lessons(data: dict) -> None:
    """The CROSS-PROJECT lessons, ranked, printed in the plan.

    This tier had no automatic reader at all. It was reachable only by explicitly running
    `recall` - a prose instruction, and prose instructions are what get skipped. So a class
    could be written down, paid for, and written down again, without ever reaching the agent
    about to repeat it.

    Ranked by what is biting hardest, so the cap drops the least-relevant lessons rather than
    an arbitrary tail. A project with no lessons of its own still gets this: it is the only
    tier that can help a team before they have made the mistake.
    """
    cross = data.get("cross_lessons")
    if not cross or not cross.get("lessons"):
        return
    n = cross["count"]
    print(f"\n  cross-project lessons ({n}) - the classes that keep biting, hardest first:")
    for item in cross["lessons"][:CROSS_DIGEST_MAX]:
        cited = f" [x{item['recurrence']}]" if item.get("recurrence") else ""
        print(f"    {item['id']}{cited}: {item['title']}")
    if n > CROSS_DIGEST_MAX:
        print(f"    (+{n - CROSS_DIGEST_MAX} more, ranked lower - `lessons rank` for the "
              f"full order, `lessons recall` to read one)")


def _render_token_forecast(data: dict) -> None:
    """LEAD WITH WHAT SPRINTS HAVE ACTUALLY COST. The forecast follows, as a range, and it STATES
    ITS RATE AND WHERE THAT RATE CAME FROM - a bare number would read as a fact, when it is a
    measurement multiplied by an estimate."""
    tf = data.get("token_forecast")
    if not tf or not tf.get("tokens"):
        return
    hist = tf.get("history") or []
    if hist:
        print("  batch history (what sprints ACTUALLY cost - the real planning input):")
        for h in hist[-4:]:
            print(f"    {h['id']}: {h['units']} unit(s), {h['tokens']:,} tokens "
                  f"({h['per_unit']:,}/unit)")
    cap = data.get("capacity") or {}
    fc = cap.get("forecast") or {}
    band = (f" (plausible {fc['low']:,}-{fc['high']:,})"
            if fc.get("low") and fc.get("high") else "")
    print(f"  token forecast: ~{tf['tokens']:,} tokens = {tf['points']} point(s) x "
          f"{tf['rate']:,} tokens per point{band}")
    print(f"    rate ({tf['rate_source']}): {tf['rate_basis']}")
    if tf["rate_source"] == "seed" and tf["rate_units"]:
        print(f"    this project has {tf['rate_units']} unit(s) of its own evidence so far; the "
              f"rate becomes ITS measurement at {RATE_MIN_UNITS}")
    if tf.get("unpriced"):
        print(f"    NOT forecast (no Points, and nothing is invented for them): "
              f"{', '.join(tf['unpriced'])}")
    rec = data.get("forecast_record")
    if rec and not rec.get("error"):
        n = len(rec.get("recorded", [])) + len(rec.get("already", []))
        print(f"  forecast recorded: {n} unit(s) at plan time, with the points and the rate that "
              f"produced them. The retro judges THIS number - it never re-derives one, and the "
              f"points recorded here are what the NEXT rate is measured from")


#: The status a unit of each type is heading for. A briefing about "the gates you will meet"
#: has to know which transition it is briefing.
_TERMINAL_TARGET = {"story": "Done", "bug": "Fixed", "epic": "Done"}


def build_gate_briefing(root, units: list) -> dict:
    """What this batch's units must satisfy to close, and the checks every commit meets.

    GENERATED, never restated. The per-unit half runs the real transition gates through
    `transition.requirements`, so a requirement that changes in the gate changes here; the
    commit half reads `gate.DEFAULT_CHECKS`, so a check added or removed there appears or
    disappears here. A hand-written list would be a second copy that goes stale silently,
    which is the failure this briefing exists to remove rather than relocate.

    SCOPED to the batch: only the types actually present, and only requirements actually
    unmet. The plan is already long, and an irrelevant checklist is how a relevant one stops
    being read.

    Repo-local guards - a house style rule, a commit-message trailer - are deliberately NOT
    enumerated. The skill cannot know a consuming project's own hook, and inventing a list
    would be the restatement this avoids.
    """
    import transition  # noqa: PLC0415 - lazy sibling import, as elsewhere in this module
    import gate        # noqa: PLC0415

    per_unit, types = [], set()
    for unit in units:
        uid = unit.get("id") if isinstance(unit, dict) else unit
        utype = unit.get("type") if isinstance(unit, dict) else None
        if not utype:
            hit = sdlc_md.find_by_id(root, uid)
            utype = hit[1] if hit else None
        target = _TERMINAL_TARGET.get(utype)
        if not target:
            continue
        types.add(utype)
        try:
            # The gates chatter - config advisories, DoD stand-down notes - and this is a
            # REPORTER, not the gate itself. Leaking their diagnostics into the plan would
            # print them once per unit for a briefing, which is noise in the output the agent
            # is meant to read, and it tripped the suite's own printed-line budget.
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                unmet = transition.requirements(root, uid, target)
        except (FileNotFoundError, ValueError):
            continue     # a unit the briefing cannot resolve is not a reason to fail the plan
        if unmet:
            per_unit.append({"id": uid, "type": utype, "target": target, "unmet": unmet})
    return {"units": per_unit, "types": sorted(types),
            "commit_checks": sorted(gate.DEFAULT_CHECKS)}


def _render_gate_briefing(data: dict) -> None:
    brief = data.get("gate_briefing")
    if not brief or not brief["types"]:
        return
    # ONLY what is actionable. The first cut also printed all 15 commit-check names and a
    # caveat about repo-local guards on EVERY plan - two constant lines that say nothing about
    # this batch. That is the bloat AC4 forbids, and the suite's printed-line budget caught it:
    # a briefing nobody reads is worth less than no briefing, because it displaces the lines
    # that do matter. The check count stays as one short line; the names are a `gate` run away.
    n_checks = len(brief["commit_checks"])
    if not brief["units"]:
        return      # nothing owed: say nothing. A line that appears on every clean plan to
                    # report the default state is the noise this briefing must not become.
    print(f"  gates: {n_checks} commit check(s). {len(brief['units'])} unit(s) carry an unmet "
          f"close requirement - meet it as part of the work, not as a refusal after it:")
    for item in brief["units"]:
        for req in item["unmet"]:
            print(f"    {item['id']} -> {item['target']}: {req}")


def _render_capacity(data: dict) -> None:
    """Does the batch fit? The plan-time capacity check - and the appetite the run will break
    on, which is the same number. Loud when over budget, and honest about its own error bar."""
    cap = data.get("capacity")
    if not cap:
        return
    b, fc, app, cal = cap["budget"], cap["forecast"], cap["appetite"], cap["calibration"]
    units = f"{cap['units']}/{b['units']}" if b["units"] else f"{cap['units']}/unbounded"
    tokens = (f"~{fc['tokens']:,}/{b['tokens']:,}" if b["tokens"]
              else f"~{fc['tokens']:,}/unbounded")
    verdict = ("OVER BUDGET (" + ", ".join(cap["over"]) + ")") if cap["over"] else "within budget"
    print(f"  capacity: units {units}, tokens {tokens} - {verdict}")
    if cap["over"]:
        print(f"  capacity: this batch does not fit. Cut it, or raise the appetite deliberately "
              f"(--appetite-units / --appetite-minutes). This is a WARNING, not a gate - "
              f"planning is never refused on a token estimate.", file=sys.stderr)
    elif cap["tokens_may_exceed"]:
        print(f"  capacity: within budget on the point estimate, but the top of the plausible "
              f"range ({fc['high']:,}) is over {b['tokens']:,} - the forecast is not that "
              f"precise.", file=sys.stderr)
    # The Calibration line reports the OUT-OF-SAMPLE figure, or says plainly that it has none.
    # It once quoted the in-sample 1.09x back as the estimator's observed accuracy while the
    # live figure was 0.55x: a fit against its own training data cannot be wrong, which is
    # exactly why it must never be shown as validation.
    sprints = cal["sprints"]
    ratios = ", ".join(f"{r}x" for r in cal["ratios"])
    dropped = ", ".join(f"{n} {k}" for k, n in sorted(cal["excluded"].items()) if n)
    excluded = (f" ({dropped} row(s) excluded - a fit against its own training data is not "
                f"evidence)" if dropped else "")
    history = (f"{sprints} out-of-sample sprint(s), est/actual {ratios}{excluded}" if sprints
               else f"no out-of-sample evidence yet{excluded}")
    enough = ("enough history to recalibrate - a human should re-read the trend"
              if cal["enough_history"]
              else f"not enough history to recalibrate (need {cal['recalibrate_after']})")
    print(f"  capacity: the token half is a FORECAST, not a measurement - a script cannot "
          f"observe token spend, and the model is points x a measured tokens-per-point rate, "
          f"honest to about +/-50%. Calibration: {history}; {enough}. Nothing is re-fitted "
          f"automatically.")
    floor = cap.get("unit_wall_minutes_floor")
    wall = (f", ~{floor} min/unit of worker time measured (a FLOOR on a "
            f"{cap['units']}-unit run, not a forecast of it)" if floor else "")
    print(f"  capacity: the run BREAKER is wall-clock/unit-count - appetite "
          f"{app['minutes']:g} min ({app['minutes_source']}) / {app['units']} unit(s) "
          f"({app['units_source']}){wall}")


def _render_plan(args: argparse.Namespace, data: dict, queries: list, worklist, epics) -> None:
    """Render a built plan to stdout: JSON, or the human batch header + provenance + waves."""
    if args.format == "json":
        print(json.dumps(data, indent=2))
        return
    scope = f", epics {', '.join(sorted(epics))}" if epics else ""
    src = f"worklist {worklist}" if worklist else " + ".join(f"{k}s {s}" for k, s in queries)
    print(f"batch: {data['count']} unit(s) ({src}){scope}, order={args.order}")
    _render_seat_provenance(data)
    _render_waves(data)
    _render_clusters(data)
    _render_triage(data)
    _render_decompose(data)
    _render_downgrades(data)
    _render_token_forecast(data)
    _render_capacity(data)
    _render_gate_briefing(data)
    _render_lessons(data)
    _render_cross_lessons(data)


def _plan_authoring(args: argparse.Namespace) -> int:
    """The greenfield PRD path: the batch IS a PRD (PRD -> epics -> stories)."""
    try:
        data = build_authoring_plan(args.root, args.prd)
    except FileNotFoundError as exc:
        print(f"{exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(data, indent=2))
        return 0
    print(f"authoring plan: bootstrap from {data['prd']} (PRD -> epics -> stories)")
    _render_lessons(data)
    _render_cross_lessons(data)
    return 0


def _plan_batch_source(args: argparse.Namespace) -> tuple[list, object, int | None]:
    """(queries, worklist, error_code). queries from --bugs/--crs/--stories (combinable),
    worklist from --worklist; the two are mutually exclusive and at least one is required.
    error_code is 2 on a bad combination (the message is already printed), else None."""
    # each selector is repeatable (action="append"): --crs A --crs B is BOTH statuses,
    # not the last one silently. None when unused; a list of one or more when given. A
    # lone string (a hand-built Namespace) is coerced to one status, never iterated per
    # character - the char-iteration is itself a silent-wrong-batch trap.
    def _statuses(value) -> list[str]:
        if value is None:
            return []
        return [value] if isinstance(value, str) else list(value)

    queries: list[tuple[str, str]] = []
    for status in _statuses(args.bugs):
        queries.append(("bug", status))
    for status in _statuses(args.crs):
        queries.append(("cr", status))
    for status in _statuses(args.stories):
        queries.append(("story", status))
    worklist = getattr(args, "worklist", None)
    if worklist and queries:
        print("--worklist is a complete batch source; do not combine it with "
              "--bugs/--crs/--stories", file=sys.stderr)
        return queries, worklist, 2
    if not worklist and not queries:
        print("specify a batch: --bugs/--crs/--stories (combinable), --worklist, or --prd",
              file=sys.stderr)
        return queries, worklist, 2
    return queries, worklist, None


def _validate_epic_scope(args: argparse.Namespace, worklist, kinds: list) -> tuple[object, int | None]:
    """(epics, error_code). --epic scopes a STORY batch and cannot filter a --worklist (whose
    units are named). error_code is 2 on misuse (message printed), else None."""
    epics = set(getattr(args, "epic", None) or []) or None
    if epics and worklist:
        print("--epic does not filter a --worklist batch; list the story ids you want",
              file=sys.stderr)
        return epics, 2
    if epics and "story" not in kinds:
        print("--epic scopes a story batch; use it with --stories", file=sys.stderr)
        return epics, 2
    return epics, None


def _selector_hint(args: argparse.Namespace, queries: list, worklist) -> str:
    """The batch selectors, re-spelled as flags, so a refusal can name the exact command that
    reports the same census - rather than a generic one the operator has to reconstruct."""
    if worklist:
        return f"--worklist {worklist}"
    flag = {"bug": "--bugs", "cr": "--crs", "story": "--stories"}
    sel = " ".join(f"{flag.get(k, '--' + k)} {s}" for k, s in queries)
    root = getattr(args, "root", ".")
    return f"{sel} --root {root}" if root not in (".", None) else sel


def cmd_breakdown(args: argparse.Namespace) -> int:
    """The read-only grooming census: what this batch lacks before a plan can be trusted.

    Reports; never blocks and never writes (the enforcement is `plan`, the command people
    actually invoke - a separate step nobody runs is doctrine). Exists so the refusal has a
    command to name, and so a backlog can be groomed against the same census the gate reads."""
    queries, worklist, rc = _plan_batch_source(args)
    if rc is not None:
        return rc
    root = Path(args.root)
    skip = getattr(args, "skip_personas", False)
    try:
        batch = (_worklist_units(root, worklist)[0] if worklist
                 else select_batches(root, queries, order="priority", skip_personas=skip))
    except ValueError as exc:
        print(f"cannot read the batch: {exc}", file=sys.stderr)
        return 2
    bd = breakdown(root, batch, skip_personas=skip)
    if args.format == "json":
        print(json.dumps(bd, indent=2))
        return 0
    print(f"breakdown: {len(batch)} unit(s), {len(bd['ungroomed'])} ungroomed, "
          f"{len(bd['oversized'])} above {bd['ceiling']} points, "
          f"{len(bd['clusters'])} shared-file cluster(s) (mode={bd['mode']})")
    if bd["ungroomed"]:
        print("  ungroomed - `sprint plan` refuses a batch holding any of these:")
        print("\n".join(_breakdown_detail(bd)))
        print(_breakdown_fix(bd, _selector_hint(args, queries, worklist)))
    if bd["oversized"]:
        print(f"  too big to estimate - `sprint plan` refuses these; SPLIT them into units of "
              f"{bd['ceiling']} points or fewer:")
        print("\n".join(_oversized_detail(bd)))
        print(SPLIT_FIX.format(ceiling=bd["ceiling"]))
    _render_clusters({"breakdown": bd})
    _render_decompose({"breakdown": bd})
    _render_downgrades({"breakdown": bd})
    return 0


def cmd_goal_verdict(args: argparse.Namespace) -> int:
    """The closing review's Sprint Goal judgement, recorded beside the goal it judges.

    Refused when no goal was recorded: a verdict on an absent goal is invented
    alignment - the review's honest statement there is that no goal was set."""
    try:
        state = run_state.read(args.root)
    except run_state.RunStateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not (state or {}).get("sprint_goal"):
        print("goal-verdict refused: no sprint goal recorded on this run - the plan set none, "
              "so there is nothing to judge (set one at plan time with --sprint-goal)",
              file=sys.stderr)
        return 2
    run_state.update(args.root, sprint_goal_verdict={"verdict": args.verdict,
                                                     "note": args.note})
    print(f"sprint goal verdict recorded: {args.verdict}"
          + (f" - {args.note}" if args.note else ""))
    return 0


# --- sprint close: the close ceremony as one deterministic chain --------------------
# The close was the last big hand-carried ceremony (~12 sequenced steps, each a skippable
# seam under a less careful run). This orchestrates the deterministic chain - goal-verdict,
# retro validate + extract, lessons summary, the close gate, handoff, reconcile - stopping
# LOUDLY at the first failing gate with the remedy named, and ends by PRINTING the sign-off
# decision brief composed from the committed records. Judgement stays outside: the retro's
# content, the goal-verdict's note, and the signature itself remain human/agent work - the
# chain sequences and refuses, never invents.


def _run_cli(module_main, argv: list[str]) -> tuple[int, str]:
    """Run a sibling script's main() in-process, capturing its combined output.

    Not every sibling main() takes argv (retro.py's parses sys.argv directly), so the
    argv is passed when the signature accepts it and patched into sys.argv otherwise -
    a signature mismatch must not crash the chain."""
    import contextlib as _ctx
    import inspect as _inspect
    import io as _io
    buf = _io.StringIO()
    takes_argv = bool(_inspect.signature(module_main).parameters)
    with _ctx.redirect_stdout(buf), _ctx.redirect_stderr(buf):
        try:
            if takes_argv:
                rc = module_main(argv)
            else:
                old = sys.argv
                sys.argv = [old[0], *argv]
                try:
                    rc = module_main()
                finally:
                    sys.argv = old
        except SystemExit as exc:  # argparse errors surface as SystemExit
            rc = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    return rc, buf.getvalue().strip()


def _close_retro_validate(root, retro_id, state):
    import retro  # noqa: PLC0415 - deferred, like the planner's retro import
    rc, out = _run_cli(retro.main, ["--root", str(root), "validate", "--id", retro_id])
    if rc != 0:
        return False, out, (f"fix the retro's content ({retro_id}) - `retro.py validate "
                            f"--id {retro_id}` names each gap; absent, create it with "
                            "`artifact.py new --type retro --title ...` and write it")
    return True, f"{retro_id} valid", ""


def _close_retro_extract(root, retro_id, state):
    import retro  # noqa: PLC0415
    rc, out = _run_cli(retro.main, ["--root", str(root), "extract", "--id", retro_id])
    if rc != 0:
        return False, out, f"`retro.py extract --id {retro_id}` must succeed - see its output"
    return True, "lessons lifted into the project log (idempotent by content)", ""


def _close_lessons_summary(root, retro_id, state):
    rc, out = _run_cli(lessons.main, ["--root", str(root), "summary"])
    if rc != 0:
        return False, out, "`lessons.py summary` must regenerate the committed digest"
    return True, "lessons summary regenerated", ""


def _close_gate(root, retro_id, state):
    import gate  # noqa: PLC0415 - deferred so `plan` never pays for the gate import graph
    rc, out = _run_cli(gate.main, ["--root", str(root), "--require-retro", retro_id,
                                   "--require-review"])
    if rc != 0:
        return False, out, ("address each failing lane the gate names (reconcile drift -> "
                            "`reconcile.py apply`; stale review -> run `review`; lesson "
                            "horizons -> `lessons.py revalidate`), then re-run sprint close")
    return True, f"gate --require-retro {retro_id} --require-review: PASS", ""


def _close_handoff(root, retro_id, state):
    if state.get("handoff") and state.get("outcome") in run_state.CLOSED:
        # The handoff already exists, so it is not regenerated - but this branch used to
        # return without looking at the OUTCOME, and it is the branch a re-run of a close
        # takes. A run that stopped earlier and then closed with an achieved verdict kept
        # `stopped` for exactly this reason: the skip covered the outcome as well as the
        # artefact. Reconcile the outcome with the verdict here, so a plain `sprint close`
        # corrects it and not only `--apply-signoff`.
        _finalise_outcome(root, state)
        return True, f"already generated ({state['handoff']}) - skipped", ""
    import handoff  # noqa: PLC0415
    title = state.get("sprint_goal") or state.get("run_id") or "sprint close"
    # The outcome is DERIVED from the recorded goal-verdict, never defaulted: only an
    # achieved goal closes as goal-reached; partial/missed close as the honest `stopped`.
    verdict = (state.get("sprint_goal_verdict") or {}).get("verdict")
    outcome = run_state.GOAL_REACHED if verdict == "achieved" else run_state.STOPPED
    rc, out = _run_cli(handoff.main, ["generate", "--title", title,
                                      "--outcome", outcome,
                                      "--retro", retro_id, "--root", str(root)])
    if rc != 0:
        return False, out, "`handoff.py generate` must close the run - see its output"
    return True, f"handoff generated; run state closed ({outcome}, from the {verdict} verdict)", ""


def _close_reconcile(root, retro_id, state):
    rc, out = _run_cli(reconcile.main, ["detect", "--root", str(root)])
    if rc == 0:
        return True, "no index drift", ""
    # A `request-derivable` item that another gate refuses is real drift, but `reconcile apply`
    # provably CANNOT clear it - so the printed remedy is a loop with no exit, and every close in
    # the project deadlocks behind one pending decision. It is reported, never suppressed, and it
    # does not stop the ceremony. Anything else still blocks: the point of this step is that
    # mechanical drift gets fixed before the run is sealed, not that drift gets waved through.
    blocked = [d for d in reconcile.derivable_request_drift(root) if d.get("blocked_by")]
    if blocked and _only_blocked_derivable_drift(root, blocked):
        ids = ", ".join(d["id"] for d in blocked)
        return True, (f"no mechanical drift; {len(blocked)} request(s) awaiting another gate "
                      f"({ids}) - reported, not clearable by apply"), ""
    return False, out, "`reconcile.py apply` clears mechanical drift, then re-run"


def _only_blocked_derivable_drift(root, blocked) -> bool:
    """True when the ONLY thing making detect non-zero is gate-blocked derivable requests.

    Counted from the same census detect uses, so this cannot pass over a real drift item that
    happens to share the sweep with a blocked one.
    """
    total = sum(len(reconcile.detect_type(t, Path(root)).get("drift", []))
                for t in reconcile.DEFAULT_TYPES)
    derivable = reconcile.derivable_request_drift(root)
    return total == 0 and len(derivable) == len(blocked)


# Chain order is the ceremony's order; cmd_close resolves each step through globals() at
# call time so a test can patch one step without rebuilding the table.
_CLOSE_CHAIN = ("retro-validate", "retro-extract", "lessons-summary",
                "gate", "handoff", "reconcile")


def _mutation_note(root) -> str:
    """The mutation lane's evidence for the brief - read, never invented, and never
    laundered: a red baseline or an errored run is named as worthless, not rendered
    as a neutral killed/survived line."""
    p = Path(root) / "sdlc-studio" / ".local" / "mutation-report.json"
    if not p.is_file():
        return ("mutation: no mutation report - run `mutation.py run --since <base ref> "
                "--test \"<suite>\"` before the close")
    try:
        rep = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "mutation: report unreadable - re-run mutation.py"
    s = rep.get("summary", {})
    if rep.get("baseline") not in (None, "pass"):
        return (f"mutation: report is WORTHLESS - baseline {rep.get('baseline')!r} "
                "(tests fail on unmutated code); re-run mutation.py on a clean tree")
    note = (f"mutation: {s.get('killed', '?')} killed / {s.get('survived', '?')} survived "
            f"of {s.get('applied', '?')} applied (report at rev {rep.get('git_rev', '?')[:9]})")
    if s.get("errors"):
        note += f"; {s['errors']} errored - inspect before trusting the kill rate"
    if s.get("truncated"):
        note += f"; {s['truncated']} enumerated mutant(s) beyond the cost ceiling not run"
    return note


def _cost_note(root, state) -> str:
    """Forecast vs measured subagent spend, from the recorded plan forecast and the
    telemetry actuals for the batch. Unmeasured units are counted, not glossed."""
    forecast = state.get("token_forecast")
    fc = f"{forecast:,} tokens forecast at plan time" if forecast else "no forecast recorded"
    batch = state.get("batch") or []
    seen = telemetry.actuals(root)
    rows = [seen[u] for u in batch if u in seen and seen[u].get("tokens")]
    if rows:
        spent = sum(int(r["tokens"]) for r in rows)
        measured = (f"{spent:,} tokens measured across {len(rows)}/{len(batch)} "
                    "batch unit(s) (telemetry actuals)")
    else:
        measured = f"0/{len(batch)} batch unit(s) have measured tokens - not measured, not zero"
    return f"{fc}; {measured}"


def _retro_path(root, rid: str):
    """The retro file for an id (e.g. `RETRO0047` or `RETRO-0047`), or None if none exists.

    Matches on the file-id head directly: `RETRO`/`REVIEW`/`HANDOFF` are meta prefixes that
    the artifact ID_RE (EP/US/BG/... only) does not recognise, so `extract_record_id` cannot
    be used here. A retro filename is always `<file_id>-<slug>.md` with no dash inside the id."""
    key = rid.strip().upper().replace("-", "")
    d = Path(root) / "sdlc-studio" / "retros"
    if not key or not d.is_dir():
        return None
    for p in d.glob("*.md"):
        if p.name == "_index.md":
            continue
        if p.stem.split("-", 1)[0].upper() == key:
            return p
    return None


def _prefill_retro(path, batch, state) -> None:
    """Fill the scaffolded retro's objective front-matter (Batch/Goal) from run state - the
    close already holds them, so the author never re-transcribes what the run recorded. The
    narrative placeholders (Delivered, Lessons, ...) are left for the author to fill."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    text = text.replace("{{batch}}", ", ".join(batch) or "-")
    text = text.replace("{{goal}}", state.get("sprint_goal") or "-")
    sdlc_md.atomic_write(p, text)


def _resolve_retro(root, args, state) -> int | None:
    """Ensure the close has a retro to gate on, through the deterministic path.

    - `--retro` omitted: SCAFFOLD one via `artifact.meta_new` (allocated id + rendered template
      + index row), pre-fill Batch/Goal from run state, print the id, and STOP so the author
      fills it. This is the forced-scaffold path: a retro is never hand-authored into a missing
      index row that only the reconcile step would catch. Idempotent: the scaffolded id is
      stashed on run state, so a second bare close REUSES it rather than minting a duplicate.
    - `--retro` names an existing retro: proceed, and self-heal a missing index row
      (`reconcile.apply_meta`) so a retro made any other way still never stalls the close.
    - `--retro` names a missing retro: refuse (the sequential allocator cannot mint a chosen id).

    Returns an exit code to stop the close, or None to continue (args.retro is then the id)."""
    import artifact  # noqa: PLC0415 - deferred, like the chain's retro/handoff imports
    import reconcile  # noqa: PLC0415
    rid = (args.retro or "").strip()
    if rid:
        if _retro_path(root, rid) is None:
            print(f"close refused: retro {rid} not found. Omit --retro and close will scaffold "
                  f"one for you (id + index row), or create it with `artifact.py new --type "
                  f"retro`.", file=sys.stderr)
            return 2
        reconcile.apply_meta(root)  # B safety net: add the index row if a prior author skipped it
        return None
    # Reuse an already-scaffolded retro for this run if it still exists - a bare close re-run
    # (or a wrapper that retries on non-zero) must not mint a second empty retro.
    prior = (state.get("scaffolded_retro") or "").strip()
    if prior and _retro_path(root, prior) is not None:
        disp, verb = prior, "already scaffolded"
    else:
        # Through the shared helper: a Sprint Goal is a sentence, and an H1 keeping its
        # full stop fails markdownlint MD026 and blocks the commit carrying this retro.
        title = sdlc_md.heading_title(
            state.get("sprint_goal") or state.get("run_id") or "sprint retro")
        res = artifact.meta_new(root, "retro", title)
        _prefill_retro(res["path"], state.get("batch") or [], state)
        disp, verb = res["id"], f"scaffolded (indexed={res['indexed']})"
        run_state.update(root, scaffolded_retro=disp)
    # Don't silently drop a --goal-verdict passed on the scaffold call: record it now so the
    # re-run reuses it (the goal-verdict block below runs only once the retro is supplied).
    if args.goal_verdict and args.note and not state.get("sprint_goal_verdict"):
        run_state.update(root, sprint_goal_verdict={"verdict": args.goal_verdict,
                                                    "note": args.note})
        print(f"close: goal-verdict recorded ({args.goal_verdict}) - reused on the re-run")
    verdict_hint = ("" if (args.goal_verdict or state.get("sprint_goal_verdict"))
                    else " --goal-verdict <achieved|partial|missed> --note \"...\"")
    print(f"close: retro {disp} {verb} -> {_retro_path(root, disp)}")
    print(f"fill its sections, then re-run: sprint.py close --retro {disp}{verdict_hint}")
    return 1


def _batch_story_units(root, batch) -> list[str]:
    """The story units in the batch, in batch order. Sign-off + Done transition is story-scoped
    (conformance is), so a bug/CR in a mixed batch - already terminal by the time the close runs -
    is not signed off here."""
    out = []
    for uid in batch:
        hit = sdlc_md.find_by_id(Path(root), uid)
        if hit and hit[1] == "story":
            out.append(sdlc_md.norm_id(uid))
    return out


def _signoff_author(root, unit) -> str:
    """The author id the sign-off must be independent OF - read from the unit's recorded critic
    verdict, its evidence row, or the sprint-level review that covers it (a unit reviewed only at
    sprint scope still records its author there). Empty when none exists: a sign-off with no author
    to be independent of cannot clear the two-role gate, so the caller refuses rather than invent one."""
    import critic  # noqa: PLC0415
    for getter in (critic.verdict_for, critic.evidence_for, critic.sprint_review_for):
        rec = getter(root, unit)
        if rec and (rec.get("author") or "").strip() not in ("", "-"):
            return rec["author"]
    return ""


def _apply_signoff(root, state, principal: str | None, author_default: str | None = None,
                   retro_arg: str | None = None) -> int:
    """Fan the operator's recorded approval across the batch: per story unit, record the
    reviewer-of-record sign-off then transition it Done (`artifact.close` - AC-verify gated,
    cascades the parent, records telemetry), then the close tail (velocity row + final reconcile).

    Story-scoped, idempotent, and stops LOUD at the first refusal (a subagent principal, a unit
    with no recorded author, a red Done gate) leaving already-done units done - never a partial
    silent state."""
    import critic  # noqa: PLC0415
    import artifact  # noqa: PLC0415
    if not (principal or "").strip():
        print("apply-signoff needs an explicit --principal (the reviewer of record) - a sign-off "
              "with no named principal is not a review", file=sys.stderr)
        return 2
    units = _batch_story_units(root, state.get("batch") or [])
    vocab = sdlc_md.status_vocab("story", root)
    signed, done, skipped = [], [], []
    for unit in units:
        hit = sdlc_md.find_by_id(Path(root), unit)
        status = sdlc_md.canonical_status(
            sdlc_md.extract_field(hit[0].read_text(encoding="utf-8"), "Status"), vocab)
        existing = critic.signoff_for(root, unit)
        has_signoff = critic.is_independent_signoff(root, unit, existing)
        # Idempotent: a unit already Done AND independently signed off is complete - skip it, so a
        # re-run after a mid-cascade stop resumes rather than re-recording and re-transitioning.
        if status == "Done" and has_signoff:
            skipped.append(unit)
            continue
        if not has_signoff:  # a stop between signoff and Done leaves the signoff; do not duplicate it
            author = author_default or _signoff_author(root, unit)
            if not author:
                print(f"apply-signoff STOPPED at {unit}: no recorded critic author to sign off "
                      f"independently of - run the per-unit or sprint-level critic first",
                      file=sys.stderr)
                return 1
            try:
                critic.record_signoff(root, unit, principal=principal, author=author)
            except ValueError as exc:  # subagent principal, principal == author, ...
                print(f"apply-signoff STOPPED at {unit}: {exc}", file=sys.stderr)
                return 1
            signed.append(unit)
        try:
            artifact.close(root, unit)  # Done + cascade + telemetry; AC-verify gated for stories
        except Exception as exc:  # noqa: BLE001 - a red Done gate must stop the fan loudly
            print(f"apply-signoff STOPPED at {unit}: Done transition refused - {exc}",
                  file=sys.stderr)
            return 1
        done.append(unit)
        print(f"apply-signoff: {unit} signed off by {principal} -> Done")
    # the run's own units - the derivation must not reach epics this close never touched
    rc = _apply_signoff_tail(root, state, units=done + skipped, retro_arg=retro_arg)
    print(f"apply-signoff: {len(done)} transitioned Done, {len(signed)} newly signed, "
          f"{len(skipped)} already complete")
    return rc


def _declared_breakdown_ids(text: str) -> list[str]:
    """The epic's declared breakdown ids - see `reconcile.declared_breakdown_ids`.

    Delegates rather than parsing: the close-owed detector must read a breakdown exactly
    the way this derivation does, and two private copies of the rule is how they drifted.
    """
    import reconcile  # noqa: PLC0415
    return reconcile.declared_breakdown_ids(text)


def _derive_parent_epics(root, units=None) -> list[str]:
    """Transition an epic whose breakdown units are ALL terminal to Done.

    The per-unit cascade ticks an epic's breakdown checkbox but never sets the epic's own
    Status, and with `two_backlog.enforce` off (the default) reconcile does not derive it
    either - so after a close transitioned all of an epic's stories Done, the epic sat at
    Draft and had to be moved by hand.

    Deriving completion is a claim, so it is made only where the evidence is complete:

    - Scoped to the PARENTS OF THIS RUN'S UNITS (`units`). A close must never write
      completion onto an epic the run did not touch.
    - An epic with no breakdown units is skipped: "no children" is not "all children
      complete".
    - An epic with any UNRESOLVABLE child - a breakdown id with no backing file, or a unit
      with no Status - is skipped. Those are unknown, not finished, and treating them as
      absent would mark an incrementally-written epic Done off its one delivered story.
    """
    import reconcile  # noqa: PLC0415
    import transition  # noqa: PLC0415
    root = Path(root)          # callers pass either; the census helpers need a Path
    # No units means NOTHING to derive from - never "derive everywhere". A bug/CR-only batch
    # yields no story units at all (`_batch_story_units` is story-scoped by design), so a
    # truthiness escape here would silently restore the full-repo sweep on exactly the batch
    # shape that has no business touching any epic.
    wanted = {sdlc_md.norm_id(u) for u in (units or [])}
    if not wanted:
        return []
    moved: list[str] = []
    for epath in sdlc_md.artifact_files("epic", root):
        text = sdlc_md.read_text_safe(epath)
        eid = sdlc_md.extract_record_id(epath.stem) or epath.stem
        if sdlc_md.is_terminal_status("epic", sdlc_md.canonical_status(
                sdlc_md.extract_field(text, "Status"), sdlc_md.status_vocab("epic", root))):
            continue                                   # already terminal: nothing to derive
        declared = _declared_breakdown_ids(text)
        if not declared:
            continue                                   # no children to be complete
        if not ({sdlc_md.norm_id(d) for d in declared} & wanted):
            continue                                   # not this run's epic - not our claim
        resolved = list(reconcile._breakdown_units(root, text))
        if len(resolved) != len(declared):
            print(f"apply-signoff: {eid} not derived - {len(declared) - len(resolved)} of "
                  f"{len(declared)} breakdown unit(s) could not be read (no file, or no "
                  f"Status); an unreadable child is unknown, not done", file=sys.stderr)
            continue
        if not all(sdlc_md.is_terminal_status(utype, canon)
                   for _ln, _ticked, _uid, utype, canon in resolved):
            continue
        try:
            transition.transition(root, eid, "Done")
            moved.append(eid)
        except (ValueError, OSError) as exc:
            print(f"apply-signoff: {eid} not derived Done ({exc})", file=sys.stderr)
    return moved


def _apply_signoff_tail(root, state, units=None, retro_arg: str | None = None) -> int:
    """The close tail (US0237): derive parent epics terminal, write the run's velocity row,
    and run a final reconcile. The per-unit cascade ticks each epic's breakdown checkbox but
    does not set the epic's own Status, so the derivation happens here - scoped to the
    parents of THIS run's units, never the whole repo. Idempotent: an already-terminal epic
    is skipped, the velocity row is upserted by retro id, and reconcile is read-only
    detection."""
    import reconcile  # noqa: PLC0415
    import retro  # noqa: PLC0415
    derived = _derive_parent_epics(root, units)
    if derived:
        print(f"apply-signoff: derived {', '.join(derived)} Done (all children terminal)")
    # The chain wrote the handoff one step BEFORE this cascade transitioned anything, so the
    # document and its worklist described units as remaining that the close then completed.
    # Re-render it here, against this run's own batch, so the tail reports the state the close
    # actually left. Scoped explicitly: `build` would otherwise default to whatever run is open.
    hid = (state.get("handoff") or "").strip()
    if hid:
        import handoff  # noqa: PLC0415
        try:
            rep = handoff.refresh(root, hid, batch=state.get("batch") or None)
        except Exception as exc:  # noqa: BLE001 - a stale handoff must not lose the close
            print(f"apply-signoff: {hid} NOT refreshed ({exc}) - it still describes the "
                  f"state before this cascade", file=sys.stderr)
        else:
            if rep is None:
                print(f"apply-signoff: {hid} has no file on disk - not refreshed",
                      file=sys.stderr)
            else:
                s = rep["summary"]
                print(f"apply-signoff: {hid} refreshed - {s['delivered']} delivered, "
                      f"{s['remaining']} remaining")
    # The run-state field is set only when THIS close scaffolded the retro. A retro made
    # the documented way (`artifact.py new --type retro`) never sets it, so fall back to
    # the id the close was given. With neither, say so - a close that skips the
    # measurement it owes must not print unqualified success.
    retro_id = (state.get("scaffolded_retro") or "").strip() or (retro_arg or "").strip()
    if retro_id:
        # `retro accuracy --write` records the velocity row (record_velocity), keyed by retro id so
        # a re-run upserts rather than duplicating. Advisory: a mixed-model or unmeasured sprint
        # refuses the accuracy row, and that refusal never fails the close.
        # `--tokens-from-harness`: the close captures the sprint's harness-tracked token
        # actual itself (or states why it could not) - the close is the one moment the
        # current session IS the sprint's session, so the capture is attributed correctly.
        rc, out = _run_cli(retro.main,
                           ["--root", str(root), "accuracy", "--id", retro_id, "--write",
                            "--tokens-from-harness"])
        if rc == 0:
            for line in out.splitlines():
                if line.startswith("token actual"):
                    print(f"apply-signoff: {line}")
            print(f"apply-signoff: velocity row recorded for {retro_id}")
        else:
            print(f"apply-signoff: velocity not recorded ({out.splitlines()[-1] if out else 'see retro'})")
    else:
        print("apply-signoff: velocity NOT recorded - no retro id on the run state or the "
              "command line; record it with `retro.py accuracy --id RETROxxxx --write`",
              file=sys.stderr)
    rc, _ = _run_cli(reconcile.main, ["detect", "--root", str(root)])
    if rc != 0:
        # Same exemption as the close's reconcile step, and for the same reason: a derivable
        # request another gate refuses cannot be cleared by the command this message names, so
        # blocking on it strands the sign-off behind a decision nobody in this run can make.
        blocked = [d for d in reconcile.derivable_request_drift(root) if d.get("blocked_by")]
        if not (blocked and _only_blocked_derivable_drift(root, blocked)):
            print("apply-signoff: final reconcile reports drift - run `reconcile.py apply`",
                  file=sys.stderr)
            return 1
        print(f"apply-signoff: {len(blocked)} request(s) awaiting another gate "
              f"({', '.join(d['id'] for d in blocked)}) - reported, not clearable by apply")
    _finalise_outcome(root, state)
    return 0


def _finalise_outcome(root, state) -> None:
    """Record the outcome the completed close earned, at the end of the SUCCESS path.

    The outcome field was written on every failure path - blocked, budget spent, an
    operator stop - and forgotten here, so a run that stopped earlier and then completed
    its whole close chain kept `stopped`. Run state is archived per cycle, so that is the
    permanent record, and every consumer of the archive (sprint report, velocity, boundary
    regeneration, the close-owed detector) then reads a goal-reached sprint as an abandoned
    one.

    Only an `achieved` verdict promotes: following the fact that a close RAN rather than
    what it judged would make every close report goal-reached, which is this same defect
    inverted. A `partial` or `missed` verdict leaves the recorded outcome alone, because
    the vocabulary has no term for "closed cleanly, goal not met" and inventing a fifth is
    a schema change, not a bug fix. `close_run` is documented idempotent and re-stamps the
    outcome, so this is its intended use rather than a blind overwrite.
    """
    live = run_state.read(root)
    verdict = ((live.get("sprint_goal_verdict") or state.get("sprint_goal_verdict") or {})
               .get("verdict"))
    if verdict != "achieved":
        return
    if live.get("outcome") == run_state.GOAL_REACHED:
        return                               # already stamped; do not re-stamp `ended_at`
    # `close_run` re-stamps `ended_at` to now. When the close and a later `--apply-signoff`
    # are separated in time, that would stretch the archived run's elapsed span, which
    # `retro` reads - so the original end time is put back. The outcome is the correction;
    # when the run ENDED is not.
    ended_at = live.get("ended_at")
    try:
        run_state.close_run(root, run_state.GOAL_REACHED, handoff=live.get("handoff"))
    except (OSError, ValueError) as exc:   # never lose a completed ceremony to its own bookkeeping
        print(f"outcome not stamped goal-reached ({exc}) - the close itself completed; "
              f"re-stamp with `run_state.close_run`", file=sys.stderr)
        return
    if ended_at:
        # Reported separately from the stamp above: a failure HERE leaves the outcome
        # correctly promoted, so saying "not stamped" would be a wider claim than the fact.
        try:
            run_state.update(root, ended_at=ended_at)
            run_state.archive(root, run_state.read(root))   # keep the archive in step
        except (OSError, ValueError) as exc:
            print(f"outcome stamped goal-reached, but `ended_at` was left at the re-stamped "
                  f"time ({exc}) - the archived elapsed span reads long", file=sys.stderr)
    print("close: run outcome recorded goal-reached")


def _draw_report(root, retro_id) -> None:
    """Draw the sprint report on the page the operator signs off, immediately before the
    decision brief - what the sprint delivered and cost belongs in the decision, not in a
    command someone has to remember afterwards.

    Read-only and advisory, so it is idempotent across a resumed close and CANNOT fail one:
    `report.enabled: false` skips the page (the switch gates drawing only), an uncomposable
    report is rendered as `unavailable`, and any error is noted on stderr and stepped over.
    Never the reverse - a missing garnish must not lose a completed ceremony."""
    import sprint_report  # noqa: PLC0415 - deferred, like the chain's sibling imports
    try:
        if not sprint_report.rendering_enabled(Path(root)):
            return
        print(sprint_report.render(sprint_report.report(root, retro_id)))
        print()
    except Exception as exc:  # noqa: BLE001 - advisory: the close outranks its own report
        print(f"close: sprint report not drawn ({type(exc).__name__}: {exc}) - the close is "
              f"unaffected; draw it with `sprint.py report --id {retro_id}`", file=sys.stderr)


def close_preflight(root, retro_id: str | None = None) -> dict:
    """Every unmet close prerequisite, in ONE read-only pass.

    The close is a chain that stops at its first failure, and the sign-off prerequisites are not
    part of the gate block at all - they surface only after the whole chain has passed. So a
    close took as many invocations as it had unmet prerequisites, each costing a full gate run,
    and it read as the tool moving the goalposts. Every fact below was available before the
    first attempt.

    READ-ONLY BY CONSTRUCTION. It scaffolds no retro, regenerates no summary and records no
    verdict, so it can be asked the question without committing to a close. That is also why it
    cannot simply run the chain with a dry-run flag: three of the chain's steps exist to DO
    something, and a preview that performed half a close would be a worse answer than none.

    Returns {"ready": bool, "blockers": [{"stage", "detail", "remedy"}]}.
    """
    import gate   # noqa: PLC0415 - deferred, so `plan` never pays for the gate import graph
    import retro  # noqa: PLC0415 - deferred, like the planner's retro import
    root = Path(root)
    blockers: list[dict] = []

    def block(stage: str, detail: str, remedy: str) -> None:
        blockers.append({"stage": stage, "detail": detail, "remedy": remedy})

    try:
        state = run_state.read(root)
    except run_state.RunStateError as exc:
        return {"ready": False, "blockers": [{"stage": "run-state", "detail": str(exc),
                                              "remedy": "repair or remove the run state"}]}
    if not state:
        return {"ready": False, "blockers": [{
            "stage": "run-state", "detail": "no run state",
            "remedy": "`sprint plan --write` opens the run this close would end"}]}
    if not state.get("sprint_goal"):
        block("sprint-goal", "no sprint goal recorded on this run",
              "set one at plan time with --sprint-goal; a close cannot invent what the run "
              "aimed at")
    if not state.get("sprint_goal_verdict"):
        block("goal-verdict", "the Sprint Goal is unjudged",
              '`sprint.py goal-verdict --verdict achieved|partial|missed --note "..."`')

    # The retro: reported, never scaffolded. `close` mints one when omitted; that is an action.
    if retro_id:
        try:
            res = retro.validate(root, retro_id)
        except (OSError, ValueError) as exc:
            block("retro", f"{retro_id}: {exc}", "fix the retro, or name the right id")
        else:
            for err in res.get("errors", []):
                block("retro", f"{retro_id}: {err}", "fill the retro's missing sections")
    else:
        block("retro", "no retro named",
              "`sprint.py close` scaffolds one and stops, or pass --retro RETROxxxx")

    # The gate block, which already reports all of its lanes at once.
    try:
        report = gate.run_gate(str(root), require_retro=retro_id, require_review=True)
    except Exception as exc:  # noqa: BLE001 - a broken lane must not hide the other blockers
        block("gate", f"gate could not run: {exc}", "run `gate.py` directly for detail")
    else:
        for c in report.get("checks", []):
            if c.get("status") == "fail" and c.get("blocking"):
                block("gate", f"{c['check']}: {c.get('detail', '')}",
                      sdlc_md.remediation_lines("gate", [c["check"]])[0]
                      if sdlc_md.remediation_lines("gate", [c["check"]])
                      else f"address the {c['check']} lane")

    blockers.extend(_signoff_preflight(root, state))
    return {"ready": not blockers, "blockers": blockers}


def _signoff_preflight(root: Path, state: dict) -> list[dict]:
    """What `--apply-signoff` will demand of each batch unit, asked BEFORE the close runs.

    These are the prerequisites that surface last today, after a full chain has already passed.
    Every rule is asked of `critic` itself rather than restated here: a pre-flight carrying its
    own copy of the independence rule is two answers to one question, and the pair drift.
    """
    import artifact  # noqa: PLC0415 - lazy, as elsewhere in the close path
    import critic    # noqa: PLC0415
    out: list[dict] = []
    # Read the SAME way conformance reads it, so the pre-flight and the gate agree on which
    # units the two-role rule reaches. A `hasattr` guard here would silently skip the whole
    # check if the accessor were ever renamed, which is the failure mode this pre-flight exists
    # to remove.
    cutoff = sdlc_md.parse_cutoff(sdlc_md.project_override(root, "review.two_role_after"))
    # The SAME resolver apply-signoff uses, not a prefix test of our own. `startswith("US")`
    # reported a sign-off blocker for a batch id with no artefact behind it - which apply-signoff
    # skips entirely - so the pre-flight over-reported work that was never owed.
    for unit in _batch_story_units(root, state.get("batch") or []):
        verdict = critic.verdict_for(root, unit)
        covered = critic.sprint_covers_independently(
            root, unit, critic.sprint_review_for(root, unit))
        if not verdict and not covered:
            out.append({"stage": "sign-off", "detail": f"{unit}: no critic verdict and no "
                                                       "sprint-level review covering it",
                        "remedy": "`critic.py record --unit <id> ...` or "
                                  "`critic.py sprint-review --units <ids> ...`"})
            continue
        num = sdlc_md.id_number(unit)
        if cutoff is None or num is None or num <= cutoff:
            continue          # pre-cutoff units keep today's behaviour
        if not (critic.evidence_for(root, unit) or covered):
            out.append({"stage": "sign-off", "detail": f"{unit}: no adversarial pass recorded "
                                                       "as evidence",
                        "remedy": "`critic.py evidence --unit <id> ...`"})
        if not critic.is_independent_signoff(root, unit, critic.signoff_for(root, unit)):
            out.append({"stage": "sign-off",
                        "detail": f"{unit}: no independent reviewer-of-record sign-off",
                        "remedy": "`critic.py signoff --unit <id> --principal \"<name>\" ...`"})
    out.extend(_done_gate_preflight(root, state))
    return out


def _done_gate_preflight(root: Path, state: dict) -> list[dict]:
    """The Done transition apply-signoff performs on each unit, previewed.

    The critic checks above are only half of what `--apply-signoff` demands: after recording the
    sign-off it calls `artifact.close`, which is AC-verify gated. A pre-flight that asked only
    about verdicts reported READY for a unit whose executable ACs were never run, and the close
    then refused it - a pre-flight that disagrees with the run it previews is worse than none,
    which is this change's own stated reason for existing.

    Asked by previewing the real close, not by restating its gates.
    """
    import artifact  # noqa: PLC0415
    out: list[dict] = []
    for unit in _batch_story_units(root, state.get("batch") or []):
        try:
            artifact.close(root, unit, dry_run=True)
        except (ValueError, OSError) as exc:
            # OSError, not just FileNotFoundError. A PermissionError escaped and, because the
            # report correctly runs above EVERY refusal, took down closes that would otherwise
            # have refused cleanly for an unrelated reason - a pre-flight must never be able to
            # turn a clean refusal into a traceback. Matches the retro branch above.
            out.append({"stage": "done-gate",
                        "detail": f"{unit}: {str(exc).strip().splitlines()[0]}",
                        "remedy": "clear the gate this names (commonly `verify_ac.py run "
                                  "--story <id>`), then re-run"})
    return out


#: Stages only `close --apply-signoff` owes. A plain close performs no Done transitions and
#: records no sign-off, so reporting these as flatly unmet overstates what THIS invocation needs.
_SIGNOFF_ONLY_STAGES = ("sign-off", "done-gate")


def _stage_label(stage: str) -> str:
    return f"{stage}, for --apply-signoff" if stage in _SIGNOFF_ONLY_STAGES else stage


def _render_preflight(data: dict) -> None:
    if data["ready"]:
        print("preflight: ready - every close prerequisite is met")
        return
    n = len(data["blockers"])
    print(f"preflight: {n} unmet prerequisite(s) - ALL of them, so the close is one more run "
          f"once these are cleared:")
    for b in data["blockers"]:
        print(f"  [{_stage_label(b['stage'])}] {b['detail']}")
        print(f"      -> {b['remedy']}")


def _report_preflight(root, retro_id: str | None) -> dict:
    """Print every unmet prerequisite to stderr. Returns the pre-flight result.

    Never changes the caller's control flow or exit code: `close`'s own refusals and its chain
    decide what stops a close, so nothing that succeeded before this existed now fails.
    """
    pre = close_preflight(root, retro_id)
    if not pre["ready"]:
        print(f"close pre-flight: {len(pre['blockers'])} unmet prerequisite(s) - this is ALL "
              f"of them, not the first:", file=sys.stderr)
        for b in pre["blockers"]:
            print(f"  [{_stage_label(b['stage'])}] {b['detail']}\n      -> {b['remedy']}",
                  file=sys.stderr)
    return pre


def cmd_preflight(args: argparse.Namespace) -> int:
    data = close_preflight(args.root, args.retro)
    if args.format == "json":
        print(json.dumps(data, indent=2))
    else:
        _render_preflight(data)
    return 0 if data["ready"] else 1


def cmd_close(args: argparse.Namespace) -> int:
    """The sprint close ceremony as one deterministic, resumable chain."""
    root = args.root
    try:
        state = run_state.read(root)
    except run_state.RunStateError as exc:
        print(f"close refused: {exc}", file=sys.stderr)
        return 2
    if not state:
        print("close refused: no run state - `sprint plan --write` opens the run this "
              "close would end", file=sys.stderr)
        return 2
    # EVERYTHING OWED, BEFORE ANY REFUSAL CAN SHORT-CIRCUIT IT. This sits above the sprint-goal,
    # retro and goal-verdict refusals deliberately: each of those returns early, so a pre-flight
    # placed after them reported nothing whenever one of them fired - which is exactly the serial
    # discovery this exists to end, reintroduced by its own placement. Reported, never a refusal:
    # the refusals below and the chain after them still decide what stops the close.
    _report_preflight(root, args.retro)
    if not state.get("sprint_goal"):
        print("close refused: no sprint goal recorded on this run - set one at plan time "
              "with --sprint-goal; a close cannot invent what the run aimed at",
              file=sys.stderr)
        return 2
    # Resolve the retro through the deterministic path: scaffold + stop when omitted,
    # heal a missing index row when present, refuse a named-but-missing id. Runs BEFORE the
    # goal-verdict so a first `close` (scaffold) records nothing until the retro is filled.
    rc = _resolve_retro(root, args, state)
    if rc is not None:
        return rc
    # Goal-verdict: record it here when given, reuse it when already judged, refuse when
    # neither - a defaulted verdict would be invented alignment.
    if args.goal_verdict:
        if not args.note:
            print("close refused: --goal-verdict needs --note - a bare verdict is an "
                  "assertion, not a review", file=sys.stderr)
            return 2
        run_state.update(root, sprint_goal_verdict={"verdict": args.goal_verdict,
                                                    "note": args.note})
        state = run_state.read(root)
        print(f"close: goal-verdict recorded ({args.goal_verdict})")
    elif state.get("sprint_goal_verdict"):
        print(f"close: goal-verdict already judged "
              f"({state['sprint_goal_verdict'].get('verdict')}) - reused")
    else:
        print("close STOPPED at goal-verdict: the Sprint Goal is unjudged - run "
              "`sprint.py goal-verdict --verdict achieved|partial|missed --note \"...\"` "
              "(or pass --goal-verdict/--note here), then re-run close", file=sys.stderr)
        return 1
    module = sys.modules[__name__]
    for i, name in enumerate(_CLOSE_CHAIN, start=1):
        step = getattr(module, "_close_" + name.replace("-", "_"))
        ok, detail, remedy = step(root, args.retro, state)
        if not ok:
            print(f"close STOPPED at {name} [{i}/{len(_CLOSE_CHAIN)}]:\n{detail}",
                  file=sys.stderr)
            print(f"remedy: {remedy}\nthen re-run: sprint.py close --retro {args.retro} "
                  "(completed steps are idempotent)", file=sys.stderr)
            return 1
        print(f"close [{i}/{len(_CLOSE_CHAIN)}] {name}: ok - {detail.splitlines()[-1] if detail else 'ok'}")
        if name == "handoff":
            state = run_state.read(root) or state  # the handoff closes the run object
    # `--apply-signoff`: the operator has already reviewed the brief and decided - fan their
    # recorded approval into per-unit sign-offs + Done transitions, then the tail. Replaces the
    # brief print (the brief is what you read to DECIDE; here the decision is made).
    if getattr(args, "apply_signoff", False):
        print()
        return _apply_signoff(root, state, getattr(args, "principal", None),
                              getattr(args, "author", None),
                              retro_arg=getattr(args, "retro", None))
    _draw_report(root, args.retro)
    import critic  # noqa: PLC0415 - the brief composer
    gate_note = f"gate --require-retro {args.retro} --require-review: PASS; {_mutation_note(root)}"
    batch = state.get("batch") or []
    print()
    print(critic.signoff_brief(root, batch, gate_note=gate_note,
                               cost_note=_cost_note(root, state)))
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    """`sprint report`: the command surface over the report composer.

    A pure delegation - the composer owns the composing, this owns being findable. Every flag
    is threaded through and its exit code returned unchanged, so the route and the module can
    never report different things about the same sprint."""
    import sprint_report  # noqa: PLC0415 - deferred, like the chain's sibling imports
    argv = ["--root", str(args.root), "show", "--id", args.id, "--format", args.format]
    if args.tokens is not None:
        argv += ["--tokens", str(args.tokens)]
    if args.elapsed_hours is not None:
        argv += ["--elapsed-hours", str(args.elapsed_hours)]
    return sprint_report.main(argv)


def cmd_plan(args: argparse.Namespace) -> int:
    """Print the ordered batch the operator approves before a run."""
    # The standing policy is validated FIRST, before any selection, write or run-state
    # mutation: an incomplete policy must leave no trace at all, or a refused run would
    # still have half-recorded the rule it refused.
    err = policy_error(getattr(args, "cycles", None), getattr(args, "sprint_goal", None),
                       getattr(args, "worklist", None), getattr(args, "prd", None))
    if err:
        print(f"policy refused: {err}", file=sys.stderr)
        return 2
    if getattr(args, "prd", None):  # greenfield authoring - the batch is a PRD
        return _plan_authoring(args)
    queries, worklist, rc = _plan_batch_source(args)
    if rc is not None:
        return rc
    # reconcile before plan - a plan must be built on a drift-free census.
    kinds = (list(dict.fromkeys(k for k, _ in queries)) if queries
             else list(sdlc_md.ARTIFACT_TYPES))
    rc = _preplan_reconcile(args, kinds)
    if rc is not None:
        return rc
    # blocker sweep before plan - newly-unblocked work should be eligible for the batch. Advisory:
    # it proposes Blocked -> Ready candidates; the gated transition stays the actor (never auto).
    sweep = pre_plan_blocker_sweep(Path(args.root))
    if sweep["now_unblocked"]:
        print(f"blocker sweep: {len(sweep['now_unblocked'])} newly-unblocked unit(s) "
              f"({', '.join(sweep['now_unblocked'])}) - propose Blocked -> Ready via the gated "
              f"transition, then re-plan to include them", file=sys.stderr)
    # the last run's tail, surfaced where the next batch is chosen. A handoff the operator
    # has to remember to open is a handoff that goes unread. An UNREADABLE run state stops
    # the plan rather than being shrugged off: `--write` would otherwise overwrite the
    # wreckage with a blank record, losing the previous run's id, batch and outcome.
    try:
        pending = pending_handoff(Path(args.root))
    except run_state.RunStateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if pending and str(worklist or "") != pending["worklist"]:
        extra = ("" if pending["plannable"] == pending["remaining"]
                 else f" ({pending['plannable']} of them plannable; the rest have no "
                      f"artefact file - see the handoff)")
        print(f"handoff: the last run ({pending['outcome']}) left {pending['id']} with "
              f"{pending['remaining']} remaining item(s){extra} - plan them with "
              f"--worklist {pending['worklist']}", file=sys.stderr)
    epics, rc = _validate_epic_scope(args, worklist, kinds)
    if rc is not None:
        return rc
    try:
        data = build_plan(args.root, order=args.order,
                          skip_personas=getattr(args, "skip_personas", False), epics=epics,
                          queries=queries or None, worklist=worklist,
                          appetite_minutes=getattr(args, "appetite_minutes", None),
                          appetite_units=getattr(args, "appetite_units", None))
    except ValueError as exc:  # dependency cycle / bad status / unknown worklist id
        print(f"cannot order the batch: {exc}", file=sys.stderr)
        return 2
    # THE DISCOVERY GATE (G1). A sprint plans the DELIVERY backlog - stories and bugs. An RFC, CR
    # or Issue is a DISCOVERY-backlog item: it has no executable ACs to close on, so it can neither
    # be sprinted nor verified Done (a request is refined into stories, an Issue triaged into
    # bugs, and those are what a sprint plans). Refused ahead of the grooming gate (a discovery
    # item cannot be groomed as a sprint unit anyway), blocking and no plan at all. Fires ONLY when
    # the project enforces the two-backlog workflow - an existing project that has not opted in
    # plans a CR as before.
    requests = ([it for it in data["batch"] if sdlc_md.is_discovery(it["type"])]
                if sdlc_md.two_backlog_enforced(args.root) else [])
    if requests:
        _refuse_requests(requests)
        return 2
    # THE BREAKDOWN GATE. Before anything is printed, written, or opened: is this batch groomed
    # enough to plan, and is any unit too big to have been estimated at all? Either failure is
    # REFUSED - blocking, non-zero, and no plan at all, because a plan over unsized or unsizeable
    # units is exactly the false authority the gate exists to abolish. It fires here, ahead of
    # the drift preflight, so a refusal costs no fetch.
    #
    # The two are reported TOGETHER but refused in one go: an operator fixing a backlog wants the
    # whole census, not one failure per re-run.
    bd = data.get("breakdown")
    if bd and (bd["ungroomed"] or bd["oversized"]):
        if bd["blocking"]:
            if bd["ungroomed"]:
                _refuse_ungroomed(bd, data["count"], _selector_hint(args, queries, worklist))
            if bd["oversized"]:
                _refuse_oversized(bd, data["count"])
            return 2
        if bd["ungroomed"]:
            _report_ungroomed(bd, data["count"])
        if bd["oversized"]:
            _report_oversized(bd, data["count"])
    rc = _origin_drift_preflight(args, data)
    if rc is not None:
        return rc
    # THE SPRINT GOAL - the product outcome this batch serves, judged at the closing
    # review (goal-verdict). One line of ceremony, never invented: absent + non-interactive
    # records none. Recorded on the plan unconditionally (like the forecast: the intent is
    # part of the prediction), and on the run state with --write.
    raw_goal = getattr(args, "sprint_goal", None)
    if raw_goal is not None:
        sprint_goal = raw_goal.strip() or None  # explicit "" = explicitly none: never prompt
    elif getattr(args, "write", False) and sys.stdin.isatty():
        try:
            sprint_goal = input("Sprint Goal (one product-outcome line, blank for none): ").strip() or None
        except (EOFError, KeyboardInterrupt):
            sprint_goal = None
    else:
        sprint_goal = None
    data["sprint_goal"] = sprint_goal
    # RECORD THE FORECAST. Here, unconditionally, because here is where the prediction is MADE.
    # Not under --write: a forecast that depends on a flag is one the next retro will find
    # missing, and it will then have to re-derive an "estimate" from the constants it is
    # supposed to be judging - which is not a prediction at all.
    try:
        data["forecast_record"] = record_forecast(args.root, data)
    except OSError as exc:
        data["forecast_record"] = {"recorded": [], "already": [], "error": str(exc)}
        print(f"warning: the plan's token forecast could NOT be recorded ({exc}). This batch "
              f"will be UNFORECAST at retro time and can say nothing about the estimator - "
              f"the retro will NOT re-derive an estimate for it.", file=sys.stderr)
    if getattr(args, "write", False):  # persist the sprint-plan artifact for review
        out = Path(args.root) / "sdlc-studio" / ".local" / "sprint-plan.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"wrote sprint plan -> {out}")
        # ...and OPEN the run. The batch approved here is the run's batch, and until now a
        # run had no identity at all: no id, no start time, nowhere to record how it ended.
        # The close (`handoff generate`) writes the outcome back to the same object.
        state = run_state.open_run(args.root, batch=[u["id"] for u in data["batch"]],
                                   goal=getattr(args, "goal", None), plan=str(out))
        # Record the RESOLVED appetite and the token forecast - additive fields on the
        # run-state object, merged, never touching its schema. The appetite was resolved once,
        # from the sprint capacity (flag > appetite.* > capacity.*), and the plan has already
        # sized the batch against it; stamping it here is what makes `loop_guard budget` break
        # on the very number the operator was shown. 0 on an axis is unbounded, as before.
        resolved = data["capacity"]["appetite"]
        appetite = {"minutes": resolved["minutes"], "units": resolved["units"]}
        extra: dict = {"appetite": appetite}
        # Never erase a recorded goal on a mid-run re-cut: like open_run's rung goal,
        # an absent value preserves, only a stated one writes (run_state never-discard).
        if data.get("sprint_goal") is not None:
            extra["sprint_goal"] = data["sprint_goal"]
        if data.get("token_forecast"):
            extra["token_forecast"] = data["token_forecast"]["tokens"]
        # THE STANDING POLICY. Recorded on the run so every later cycle plans under the rule
        # approved here rather than under whatever the CLI defaults to at 3am.
        policy = None
        if getattr(args, "cycles", None) is not None:
            policy = build_policy(args, data, queries, epics)
            extra["policy"] = policy
            extra["cycle"] = {"index": 1, "remaining": max(policy["cycles"] - 1, 0),
                              "policy_run_id": state["run_id"]}
        state = run_state.update(args.root, **extra)
        print(f"opened run {state['run_id']} (goal={state['goal'] or 'unset'}, appetite "
              f"{appetite['minutes']:g}min/{appetite['units']}units) "
              f"-> {run_state.path(args.root)}")
        if policy:
            _render_policy(policy)
    _render_plan(args, data, queries, worklist, epics)
    return 0


# ---------------------------------------------------------------------------
# The rolling multi-sprint policy: N cycles driven by one standing rule.
# ---------------------------------------------------------------------------
# An operator wanting an unattended evening had to come back at every sprint boundary to
# re-plan. Queueing several plans up front does not work: the backlog is GENERATED by the
# work - a cycle raises bugs and lessons - so a frozen queue rots while it waits. So the
# POLICY is fixed once (cycles, goal, capacity, order, stop conditions) and the PLAN is
# regenerated at each boundary from the backlog as it actually is by then.
#
# Opt-in throughout: without `--cycles`, none of this exists and a sprint behaves exactly
# as before.

#: The three ways a boundary refuses to continue. Always enforced - they are not
#: preferences, they are the conditions under which continuing would be dishonest.
STOP_CAUSES = ("close-gate", "origin-drift", "refused-plan")

#: Optional conditions an operator can add on top of the mandatory three.
OPTIONAL_STOP_CONDITIONS = ("empty-backlog",)

_STOP_TITLES = {
    "close-gate": "boundary stop: close-gate - the cycle would not close",
    "origin-drift": "boundary stop: origin-drift - local is behind origin under --strict",
    "refused-plan": "boundary stop: refused-plan - the next batch is not plannable",
}

#: The boundary's four steps, in the order they must happen. Close the cycle before
#: reading the backlog it changed; fetch before regenerating from it; regenerate before
#: previewing; preview before anything executes.
BOUNDARY_STEPS = ("close-down", "fetch", "regenerate", "preview")


def policy_error(cycles: int | None, sprint_goal: str | None, worklist: str | None,
                 prd: str | None) -> str | None:
    """What is wrong with the standing policy, or None when it is complete.

    A policy is REFUSED rather than defaulted. The whole point is that later cycles plan
    under the rule the operator approved; a policy quietly completed from CLI defaults is a
    rule nobody approved, applied while nobody is watching."""
    if cycles is None:
        return None                       # no rolling policy asked for
    if cycles < 1:
        return (f"--cycles must be 1 or more (got {cycles}) - a policy of no cycles "
                f"describes no run")
    if not (sprint_goal or "").strip():
        return ("--cycles needs --sprint-goal \"<one product-outcome line>\" - every cycle "
                "is judged against the standing goal, and a close cannot invent one")
    if worklist:
        return ("--cycles cannot be combined with --worklist - a rolling policy regenerates "
                "its batch from the live backlog, and a worklist is the frozen queue that "
                "abolishes")
    if prd:
        return ("--cycles cannot be combined with --prd - greenfield authoring has no "
                "backlog to regenerate a batch from")
    return None


def build_policy(args: argparse.Namespace, data: dict, queries: list,
                 epics: set | None) -> dict:
    """The standing policy, as recorded on run-state and read by every later cycle."""
    resolved = data["capacity"]["appetite"]
    stop_conditions = list(STOP_CAUSES) + [c for c in (getattr(args, "stop_on", None) or [])
                                           if c not in STOP_CAUSES]
    return {
        "cycles": args.cycles,
        "sprint_goal": data.get("sprint_goal"),
        "goal": getattr(args, "goal", None),
        "order": args.order,
        "capacity": {"minutes": resolved["minutes"], "units": resolved["units"]},
        "queries": [{"kind": k, "status": s} for k, s in (queries or [])],
        "epics": sorted(epics) if epics else None,
        "stop_conditions": stop_conditions,
        "skip_personas": bool(getattr(args, "skip_personas", False)),
        "recorded_at": sdlc_md.now_iso8601(),
    }


def _render_policy(policy: dict) -> None:
    print(f"rolling policy: {policy['cycles']} cycle(s), goal \"{policy['sprint_goal']}\", "
          f"order={policy['order']}, capacity {policy['capacity']['minutes']:g}min/"
          f"{policy['capacity']['units']}units")
    print(f"  stop conditions: {', '.join(policy['stop_conditions'])}")
    print("  the plan is regenerated from the live backlog at each boundary "
          "(`sprint.py boundary`)")


def _boundary_stop(root, cause: str, detail: str, remedy: str) -> int:
    """STOP the rolling run at a boundary, leaving a handoff that says why.

    The one stop path, shared by all three causes. Each cause could have grown its own -
    and then each would have drifted, and the operator returning to a stopped run would
    find a different quality of record depending on which gate happened to fire.

    What it guarantees, whichever cause fired: the next cycle's batch does NOT execute
    (nothing opens it), a handoff names the cause and the cycles left unrun, and the run
    ends recorded. The handoff is its own document even when the cycle already wrote one at
    its close: that one says what the cycle delivered, this one says why the RUN stopped and
    what is left - different questions, and the second is the one nobody can reconstruct."""
    if cause not in STOP_CAUSES:
        raise ValueError(f"unknown boundary stop cause {cause!r} - expected one of "
                         f"{', '.join(STOP_CAUSES)}")
    state = run_state.read(root)
    cycle = state.get("cycle") or {}
    index, unrun = int(cycle.get("index") or 1), int(cycle.get("remaining") or 0)
    title = f"{_STOP_TITLES[cause]} ({unrun} cycle(s) unrun after cycle {index})"
    import handoff  # noqa: PLC0415 - deferred, as everywhere else in this module
    rc, out = _run_cli(handoff.main, ["generate", "--title", title, "--root", str(root)])
    hid = run_state.read(root).get("handoff") if rc == 0 else None
    if rc != 0:
        print(f"warning: the boundary handoff could NOT be written ({out}) - the stop is "
              f"recorded on run-state, but there is no document to return to", file=sys.stderr)
    run_state.update(root, stop={"cause": cause, "detail": detail, "remedy": remedy,
                                 "cycle": index, "cycles_unrun": unrun, "handoff": hid,
                                 "stopped_at": sdlc_md.now_iso8601()})
    # A cycle whose close completed is ALREADY closed, with the outcome its goal-verdict
    # earned; overwriting that with `blocked` would relabel delivered work as a failure. Only
    # a run still running is closed here - and then `blocked` is the honest word.
    if run_state.read(root).get("outcome") == run_state.RUNNING:
        run_state.close_run(root, run_state.BLOCKED, handoff=hid)
    else:
        run_state.archive(root)          # re-archive so the stop is in the kept record
    print(f"boundary STOPPED ({cause}) after cycle {index}: {detail}", file=sys.stderr)
    print(f"  {unrun} cycle(s) of the policy were not run; handoff {hid or '(none)'}",
          file=sys.stderr)
    print(f"remedy: {remedy}", file=sys.stderr)
    return 1


def _boundary_close_down(root, index: int, args: argparse.Namespace) -> tuple[int, str]:
    """Run the cycle's close ceremony, reported against the cycle it closed.

    Delegates to `sprint close` rather than re-implementing it, so a rolling cycle closes
    through exactly the chain a hand-run sprint closes through - retro validate and extract,
    lessons summary, gate, handoff, reconcile - and cannot quietly become a weaker close."""
    argv = ["close", "--root", str(root), "--retro", args.retro]
    if getattr(args, "goal_verdict", None):
        argv += ["--goal-verdict", args.goal_verdict, "--note", getattr(args, "note", "") or ""]
    rc, out = _run_cli(main, argv)
    for line in out.splitlines():
        print(f"cycle {index} | {line}")
    return rc, out


def _regenerate_plan(root, policy: dict) -> dict:
    """The next cycle's plan, computed fresh from the backlog as it is NOW.

    Under the policy's own filters and order rule - not the CLI's defaults, and not a slice
    of a batch selected at the start of the run. Work the last cycle raised is therefore
    eligible, and work it finished has dropped out."""
    queries = [(q["kind"], q["status"]) for q in policy.get("queries") or []]
    epics = set(policy["epics"]) if policy.get("epics") else None
    cap = policy.get("capacity") or {}
    return build_plan(root, order=policy.get("order", "priority"),
                      skip_personas=policy.get("skip_personas", False), epics=epics,
                      queries=queries or None,
                      appetite_minutes=cap.get("minutes") or None,
                      appetite_units=cap.get("units") or None)


def _render_preview(data: dict, index: int) -> None:
    """The dry-run preview of the regenerated plan, printed BEFORE the cycle executes."""
    print(f"preview of cycle {index} (dry run - nothing has executed yet):")
    ids = [u["id"] for u in data["batch"]]
    print(f"  batch ({data['count']} unit(s), order={data['order']}): "
          f"{', '.join(ids) if ids else '(empty)'}")
    _render_token_forecast(data)
    _render_capacity(data)


def _open_next_cycle(root, policy: dict, data: dict, prev: dict) -> dict:
    """Mint the next cycle's run: fresh id and start time, its own batch and forecast, the
    standing policy carried, the counter decremented.

    A fresh run rather than a continuation of the last one, because a cycle is a sprint: it
    is forecast, judged and retrospected on its own, and an N-cycle run that shared one run
    record would be one blurred session pretending to be N sprints."""
    out = Path(root) / "sdlc-studio" / ".local" / "sprint-plan.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(out, json.dumps(data, indent=2))
    try:
        record_forecast(root, data)
    except OSError as exc:
        print(f"warning: this cycle's token forecast was NOT recorded ({exc}) - it will be "
              f"UNFORECAST at retro time", file=sys.stderr)
    prev_cycle = prev.get("cycle") or {}
    index = int(prev_cycle.get("index") or 1) + 1
    remaining = max(int(prev_cycle.get("remaining") or 0) - 1, 0)
    # The previous run is closed, so this mints a fresh identity and a fresh batch - the
    # cumulative-batch rule applies within a run, never across cycles.
    state = run_state.open_run(root, batch=[u["id"] for u in data["batch"]],
                               goal=policy.get("goal"), plan=str(out))
    cap = data["capacity"]["appetite"]
    extra = {
        "policy": policy,
        "cycle": {"index": index, "remaining": remaining,
                  # the run that recorded the policy - the thread joining every cycle
                  "policy_run_id": prev_cycle.get("policy_run_id") or prev.get("run_id")},
        "appetite": {"minutes": cap["minutes"], "units": cap["units"]},
        "sprint_goal": policy.get("sprint_goal"),
    }
    if data.get("token_forecast"):
        extra["token_forecast"] = data["token_forecast"]["tokens"]
    state = run_state.update(root, **extra)
    print(f"opened cycle {index} of {policy['cycles']} as run {state['run_id']} "
          f"({data['count']} unit(s), {remaining} cycle(s) left after this one)")
    return state


def cmd_boundary(args: argparse.Namespace) -> int:
    """One sprint boundary of a rolling run: close down, fetch, regenerate, preview, open.

    Every step is a gate. Nothing of the next cycle exists until all four have passed, so a
    stale or ungated plan cannot be executed by a run nobody is watching."""
    root = args.root
    try:
        state = run_state.read(root)
    except run_state.RunStateError as exc:
        print(f"boundary refused: {exc}", file=sys.stderr)
        return 2
    policy = state.get("policy")
    if not policy:
        print("boundary refused: this run carries no rolling policy - open one with "
              "`sprint.py plan --write --cycles N --sprint-goal \"...\"`. A single sprint "
              "closes with `sprint.py close`.", file=sys.stderr)
        return 2
    cycle = state.get("cycle") or {"index": 1, "remaining": max(policy["cycles"] - 1, 0)}
    index, remaining = int(cycle.get("index") or 1), int(cycle.get("remaining") or 0)

    # [1/4] CLOSE DOWN. The next cycle must plan on judged, reconciled state, so the cycle
    # that just ran is properly closed first - retro, lessons, gate - or the run halts here.
    print(f"boundary [1/4] {BOUNDARY_STEPS[0]}: closing cycle {index} of {policy['cycles']}")
    rc, out = _boundary_close_down(root, index, args)
    if rc != 0:
        return _boundary_stop(
            root, "close-gate",
            f"the close-down chain for cycle {index} did not complete",
            "fix the step the close named above, then re-run `sprint.py boundary`; the "
            "completed steps are idempotent")
    # The cycle's retro belongs on its record - it is what makes the archived cycle
    # self-describing rather than a batch with no account of itself.
    run_state.update(root, retro=args.retro)
    # A close whose chain was interrupted can leave the run running; the next cycle must
    # never open over an open one.
    if run_state.read(root).get("outcome") == run_state.RUNNING:
        verdict = (run_state.read(root).get("sprint_goal_verdict") or {}).get("verdict")
        run_state.close_run(root,
                            run_state.GOAL_REACHED if verdict == "achieved"
                            else run_state.STOPPED)
    closed = run_state.archive(root)
    print(f"cycle {index} closed and archived -> {closed}")

    # [2/4] FETCH. At EVERY boundary, not just the first plan: a long unattended run spends
    # hours between boundaries, which is exactly enough time for the team to move past this
    # checkout.
    print(f"boundary [2/4] {BOUNDARY_STEPS[1]}: comparing against origin")
    fetched = not getattr(args, "no_fetch", False)
    drift = origin_drift(root, do_fetch=fetched)
    # The result is reported per cycle on EVERY path, not only the clean one: "no news" from
    # a boundary must mean "checked and level", never "the check was skipped".
    how = "fetched" if fetched else "compared without fetching"
    if not drift.get("remote"):
        outcome = "no origin to compare"
    elif drift.get("behind"):
        outcome = f"{drift['behind']} commit(s) behind origin/{drift['branch']}"
    else:
        outcome = f"level with origin/{drift['branch']}"
    print(f"cycle {index} | fetch: {how} - {outcome}")
    if drift.get("behind"):
        warn = _drift_warning(drift, _batch_paths(root, state.get("batch") or []))
        print(f"cycle {index} | {warn}", file=sys.stderr)
        if getattr(args, "strict", False):
            return _boundary_stop(
                root, "origin-drift",
                f"local is {drift['behind']} commit(s) behind origin/{drift['branch']}",
                "fetch and rebase, then re-run `sprint.py boundary` (or drop --strict to "
                "continue against this checkout)")

    if remaining < 1:
        print(f"policy complete: {policy['cycles']} cycle(s) run, none remaining")
        return 0

    # [3/4] REGENERATE. From the live backlog, under the standing policy.
    print(f"boundary [3/4] {BOUNDARY_STEPS[2]}: selecting cycle {index + 1} from the live "
          f"backlog")
    try:
        data = _regenerate_plan(root, policy)
    except ValueError as exc:
        return _boundary_stop(root, "refused-plan", f"the batch cannot be ordered: {exc}",
                              "resolve the dependency cycle or bad status the message names")
    bd = data.get("breakdown")
    if bd and bd.get("blocking") and (bd["ungroomed"] or bd["oversized"]):
        detail = (f"{len(bd['ungroomed'])} ungroomed and {len(bd['oversized'])} oversized "
                  f"unit(s) in the regenerated batch")
        for line in _breakdown_detail(bd) + _oversized_detail(bd):
            print(f"cycle {index + 1} | {line}", file=sys.stderr)
        return _boundary_stop(root, "refused-plan", detail,
                              "groom or split the units named above, then re-run "
                              "`sprint.py boundary`")
    if not data["batch"] and "empty-backlog" in (policy.get("stop_conditions") or []):
        print(f"policy complete: the backlog is empty at cycle {index + 1} - "
              f"{remaining} cycle(s) were not needed")
        return 0

    # [4/4] PREVIEW, then open. The preview is printed BEFORE the cycle exists, so the record
    # of what this cycle was about to do survives even if it never starts.
    print(f"boundary [4/4] {BOUNDARY_STEPS[3]}: cycle {index + 1}")
    _render_preview(data, index + 1)
    _open_next_cycle(root, policy, data, run_state.read(root))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio sprint batch selection.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan", help="Select and order a batch of work (the triage plan).")
    p.add_argument("--bugs", metavar="STATUS", action="append", help="Bugs with this Status "
                   "(e.g. Open); repeatable and combinable with --crs/--stories for one merged "
                   "mixed tranche")
    p.add_argument("--crs", metavar="STATUS", action="append",
                   help="CRs with this Status (e.g. Proposed); repeatable and combinable")
    p.add_argument("--stories", metavar="STATUS", action="append",
                   help="Stories with this Status (e.g. Ready); repeatable and combinable")
    p.add_argument("--worklist", metavar="PATH",
                   help="tranche file: one unit id per line (bullets/comments tolerated); "
                        "a complete batch source, not combinable with status queries")
    p.add_argument("--prd", metavar="PATH", help="Greenfield authoring: bootstrap from a PRD")
    p.add_argument("--epic", action="append", metavar="EPxxxx",
                   help="scope a story batch to one or more epics (repeatable; with --stories)")
    p.add_argument("--order", choices=("priority", "wsjf", "manual"), default="priority")
    p.add_argument("--goal", choices=GOALS,
                   help="the goal rung this run is driven to; recorded on the run state "
                        "(with --write) so the close can say what the run aimed at")
    p.add_argument("--sprint-goal", dest="sprint_goal", metavar="TEXT",
                   help="the Sprint Goal - ONE product-outcome sentence unifying this batch "
                        "(what the increment is judged against at the closing review). Distinct "
                        "from --goal, which is a pipeline rung. Optional: prompted when "
                        "interactive; absent is recorded as none, never invented")
    p.add_argument("--write", action="store_true",
                   help="persist the sprint plan to sdlc-studio/.local/sprint-plan.json AND "
                        "open the run (id, start time, approved batch, goal) in "
                        "sdlc-studio/.local/run-state.json - the object the close reads")
    p.add_argument("--appetite-minutes", type=float, default=None, dest="appetite_minutes",
                   help="wall-clock ceiling for the run; overrides the sprint capacity "
                        "(config capacity.minutes). The unit-boundary breaker (loop_guard "
                        "budget) stops the run cleanly when it is spent, and the plan sizes "
                        "the batch against this same number. Never auto-extended")
    p.add_argument("--appetite-units", type=int, default=None, dest="appetite_units",
                   help="unit-count ceiling for the run; overrides the sprint capacity "
                        "(config capacity.units). Evaluated at unit boundaries so no unit is "
                        "abandoned mid-implementation, and flagged at PLAN time when the batch "
                        "does not fit")
    p.add_argument("--strict", action="store_true",
                   help="refuse to plan when the index has drift or local is behind origin")
    p.add_argument("--no-fetch", action="store_true", dest="no_fetch",
                   help="skip the git fetch in the origin-drift preflight (compare against the "
                        "already-fetched origin ref)")
    p.add_argument("--skip-personas", action="store_true", dest="skip_personas",
                   help="ignore review-seat WSJF inputs; the Cost of Delay is then derived from "
                        "the declared Priority, which is what WSJF runs on by default")
    p.add_argument("--cycles", type=int, default=None, metavar="N",
                   help="Opt in to a ROLLING policy of N sprint cycles. Records the standing "
                        "policy (goal, capacity, order, stop conditions) on the run; each "
                        "boundary is then driven by `sprint.py boundary`. Needs --sprint-goal.")
    p.add_argument("--stop-on", dest="stop_on", action="append",
                   choices=OPTIONAL_STOP_CONDITIONS,
                   help="Extra stop condition for a rolling policy (repeatable). A failed "
                        "close gate, a strict origin-drift refusal and a refused plan always "
                        "stop the run.")
    p.add_argument("--root", default=".", help="Repo root (default: .)")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.set_defaults(func=cmd_plan)

    b = sub.add_parser("breakdown", help="Report what a batch lacks before it can be planned "
                                         "(Affects, size, shared-file clusters). Read-only.")
    b.add_argument("--bugs", metavar="STATUS", action="append")
    b.add_argument("--crs", metavar="STATUS", action="append")
    b.add_argument("--stories", metavar="STATUS", action="append")
    b.add_argument("--worklist", metavar="PATH")
    b.add_argument("--skip-personas", action="store_true", dest="skip_personas",
                   help="ignore review-seat sizes; judge only what the artefacts declare")
    b.add_argument("--root", default=".", help="Repo root (default: .)")
    b.add_argument("--format", choices=("text", "json"), default="text")
    b.set_defaults(func=cmd_breakdown)

    cl = sub.add_parser("close", help="Run the close ceremony as one deterministic chain "
                                      "(goal-verdict, retro, lessons, gate, handoff, reconcile), "
                                      "then print the sign-off decision brief.")
    cl.add_argument("--retro", default=None, metavar="RETROxxxx",
                    help="the batch retro this close validates and gates on. Omit it and close "
                         "SCAFFOLDS one (id + template + index row) via the deterministic path, "
                         "then stops so you fill it and re-run with the id it prints")
    cl.add_argument("--goal-verdict", dest="goal_verdict",
                    choices=("achieved", "partial", "missed"), default=None,
                    help="record the Sprint Goal judgement as part of the close")
    cl.add_argument("--note", default=None,
                    help="the judgement's one-line rationale (required with --goal-verdict)")
    cl.add_argument("--apply-signoff", dest="apply_signoff", action="store_true",
                    help="fan a recorded operator approval into per-unit reviewer-of-record "
                         "sign-offs + Done transitions + the velocity/reconcile tail (needs "
                         "--principal). Story-scoped, idempotent, stops loud at the first refusal")
    cl.add_argument("--principal", default=None,
                    help="the reviewer of record whose approval --apply-signoff fans across the "
                         "batch (an authoring-session subagent is refused, as `critic signoff` refuses one)")
    cl.add_argument("--author", default=None,
                    help="(with --apply-signoff) the author id to record independence against when "
                         "a unit has no recorded critic author; normally read from the unit's verdict")
    cl.add_argument("--root", default=".")
    cl.set_defaults(func=cmd_close)
    bo = sub.add_parser("boundary", help="Cross one sprint boundary of a rolling run: close "
                                         "down, fetch, regenerate the plan, preview, open "
                                         "the next cycle.")
    bo.add_argument("--retro", required=True, metavar="RETROxxxx",
                    help="The filled retro closing THIS cycle. Required: a boundary closes a "
                         "sprint, and a sprint closes on a retro. Scaffold one with "
                         "`sprint.py close` (no --retro) if it does not exist yet.")
    bo.add_argument("--goal-verdict", dest="goal_verdict",
                    choices=("achieved", "partial", "missed"),
                    help="Judge this cycle's Sprint Goal here (needs --note).")
    bo.add_argument("--note", default=None, help="The evidence behind --goal-verdict.")
    bo.add_argument("--strict", action="store_true",
                    help="Stop the run at a boundary where local is behind origin, instead "
                         "of warning and continuing.")
    bo.add_argument("--no-fetch", action="store_true", dest="no_fetch",
                    help="Compare against origin without fetching first (offline).")
    bo.add_argument("--root", default=".", help="Repo root (default: .)")
    bo.set_defaults(func=cmd_boundary)

    r = sub.add_parser("report", help="Compose and print the end-of-sprint report for a retro "
                                      "(delivered, cost, velocity, estimate-vs-actual). Read-only.")
    r.add_argument("--id", required=True, metavar="RETROxxxx",
                   help="the retro this report is composed from")
    r.add_argument("--tokens", type=int, default=None,
                   help="sprint actual token total (interactive sprints, harness-tracked)")
    r.add_argument("--elapsed-hours", dest="elapsed_hours", type=float, default=None,
                   help="sprint elapsed hours for the primary velocity (interactive sprints)")
    r.add_argument("--format", choices=("text", "json"), default="text")
    r.add_argument("--root", default=".", help="Repo root (default: .)")
    r.set_defaults(func=cmd_report)

    pf = sub.add_parser("preflight",
                        help="Report EVERY unmet close prerequisite in one read-only pass "
                             "(gate lanes, retro, goal-verdict and the per-unit sign-off "
                             "prerequisites), before starting a close.")
    pf.add_argument("--retro", metavar="RETROxxxx", default=None,
                    help="the batch retro the close will validate against")
    pf.add_argument("--format", choices=("text", "json"), default="text")
    pf.add_argument("--root", default=".", help="Repo root (default: .)")
    pf.set_defaults(func=cmd_preflight)

    g = sub.add_parser("goal-verdict",
                       help="Record the closing review's judgement of the Sprint Goal "
                            "(achieved / partial / missed) on the run state.")
    g.add_argument("--verdict", required=True, choices=("achieved", "partial", "missed"))
    g.add_argument("--note", required=True,
                   help="one line of judgement - why the verdict holds (required: a bare "
                        "verdict is an assertion, not a review)")
    g.add_argument("--root", default=".", help="Repo root (default: .)")
    g.set_defaults(func=cmd_goal_verdict)

    sdlc_md.add_global_root(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
