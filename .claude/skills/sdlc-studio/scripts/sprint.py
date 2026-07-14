#!/usr/bin/env python3
"""SDLC Studio sprint - batch selection and ordering.

`sprint plan` selects a batch of work by query (open bugs, proposed CRs, ready
stories) and orders it, so the operator sees the triage plan before the run starts.
Ordering is by priority/severity (Critical first); dependency-topological; and WSJF
(`--order wsjf`): priority stays the dominant axis and the cognitive complexity of the
files a unit will touch (its `Affects`, scored by complexity.py) breaks
ties within a priority, so the smaller blast-radius job goes first. Complexity never
overrides priority, and the order degrades to plain priority when no complexity is
known. The WSJF job size is the review seat's estimate when the seats scored the unit,
else the human `Effort:` (S/M/L) recorded on the artefact at filing, else a neutral
default. The plan also carries a per-unit token budget, weighted by complexity, or by
the declared effort when the unit names no files.

The plan then SIZES the batch against the sprint's CAPACITY (`capacity.*`: tokens, wall-clock
minutes, units) and says whether it fits - at plan time, while the operator can still cut it,
rather than mid-run when the breaker halts the sprint. The same capacity resolves the run
APPETITE that `loop_guard budget` later breaks on, so the plan-time ceiling and the run-time
ceiling are ONE number and cannot disagree. Over budget is a WARNING, never a refusal: a script
cannot observe token spend, and the token model is a hypothesis, not a measurement.

The plan also EMITS the still-valid lessons digest (`lessons.plan_digest`): the lessons the
last sprints paid for arrive inside the plan the agent reads at sprint start, rather than as a
prose instruction to open a file that an agent under effort pressure skips. Read-only;
pure stdlib (complexity and lessons are sibling helpers).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import run_state, sdlc_md  # noqa: E402
import complexity  # noqa: E402  (sibling - blast-radius complexity for WSJF)
import config  # noqa: E402  (sibling - routing block for tier enrichment)
import lessons  # noqa: E402  (sibling - the still-valid lessons digest carried in the plan)
import reconcile  # noqa: E402  (sibling - reconcile before plan)
import blocker_sweep  # noqa: E402  (sibling - blocker sweep before plan)

PRIORITY_FIELD = {"bug": "Severity", "cr": "Priority", "story": "Priority"}
# One weight scale across types (documented in reference-sprint.md): bug Severity and
# CR/story Priority - including the P1-P4 form - map onto the same rank, so a merged
# bugs + CRs tranche orders on a single documented axis instead of two vocabularies.
PRIORITY_WEIGHT = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3,
                   "P1": 0, "P2": 1, "P3": 2, "P4": 3}
# The token forecast, calibrated against measured actuals for the first time.
#
# PROVISIONAL - fitted to 6 units measured in one sprint, one model, one repo. It is a
# HYPOTHESIS to be falsified by the next sprint's actuals, not a settled calibration. The
# previous coefficient (5,000) was never validated at all; this one at least has evidence
# behind it, and the next sprint tests it.
#
# What the 6 units showed:
#   BASE holds. The one unit with complexity 0 (a docs-only change) cost 46,359 tokens, so a
#   ~50k fixed floor per unit is real - it is the cost of an agent taking on the task at all
#   (context, orientation, tests), independent of the code it touches.
#
#   The old slope was ~9x too steep. The observed slope is ~550 tokens per complexity point;
#   the constant said 5,000. That inflated the batch estimate 3.3x (1,285,000 forecast against
#   384,278 actually spent) and caused a real planning error: a 10-unit batch was cut to 5 on
#   the belief it was too big, when it was not.
#
#   Complexity is a WEAK PER-UNIT PREDICTOR and this forecast must be read as a BATCH tool.
#   Two units of identical complexity (39) cost 46,792 and 98,513 - 2.1x apart. The cognitive
#   complexity of the FILE is a poor proxy for the WORK done in it: a small, well-scoped fix in
#   a large file does not pay the whole file's complexity. At the batch level the errors wash
#   out (the fit lands within 9% across 6 units); per unit they do not.
BASE_TOKEN_BUDGET = 50_000        # per-unit fixed floor - measured, holds
TOKENS_PER_COGNITIVE = 600        # per point of blast-radius complexity - fitted, PROVISIONAL
DEFAULT_UNKNOWN_SIZE = 3          # neutral WSJF denominator when neither the seat size nor
                                  # the declared effort resolves - unknown effort is never
                                  # treated as minimal (new-file work is often the biggest)
# The human `Effort:` estimate (S/M/L), captured at filing, as a WSJF job size. It is the one
# size a person actually recorded, so it beats the neutral default and loses only to a seat
# score. M is deliberately the neutral default: declaring the middle changes nothing.
EFFORT_SIZE = {"S": 1, "M": 3, "L": 8}
EFFORT_ALIAS = {"SMALL": "S", "MEDIUM": "M", "LARGE": "L"}
# The same estimate as a stand-in complexity seed for the TOKEN FORECAST, used only when a unit
# declares no `Affects` (complexity 0) - otherwise a Large unit with no file list forecasts the
# same flat floor as a Small one. Deliberately conservative, and bounded by the six measured
# units the constants above were fitted to (complexity 0-52, actuals 42k-98k): S keeps the
# measured floor, M sits mid-range, L near the top. A unit with real complexity is untouched.
EFFORT_COMPLEXITY_PROXY = {"S": 0, "M": 25, "L": 50}

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

# The honest error band on the token forecast. It is NOT a precision estimate: it was fitted to
# 6 units of one sprint, one model, one repo, and out-of-sample it has already run ~0.7x (under-
# forecasting) against 1.09x in-sample. +/-30% is the floor of the band; observed ratios in the
# velocity history WIDEN it (never narrow it - one sprint agreeing with the model is not
# evidence the model is tight).
FORECAST_BAND = 0.30

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
    """What the velocity history says about the forecast the plan is about to quote.

    REPORTS, never re-fits. `low`/`high` are multipliers on the point forecast that bound the
    plausible actual: FORECAST_BAND is the floor, and any observed estimate/actual ratio widens
    them (an actual of estimate/ratio). A history that agrees with the model does not shrink the
    band - agreeing once is not evidence of precision."""
    rows: list[dict] = []
    try:
        import retro  # noqa: PLC0415 - deferred: the planner must not pay for the retro import graph
        rows = [r for r in retro.velocity_history(repo_root)
                if isinstance(r.get("ratio"), (int, float)) and r["ratio"] > 0]
    except Exception as exc:  # noqa: BLE001 - no history must never break planning
        sdlc_md.debug("sprint.calibration", exc)
    ratios = [float(r["ratio"]) for r in rows]
    low, high = 1.0 - FORECAST_BAND, 1.0 + FORECAST_BAND
    if ratios:
        low = min(low, 1.0 / max(ratios))
        high = max(high, 1.0 / min(ratios))
    return {"sprints": len(rows), "ratios": ratios,
            "low": round(low, 2), "high": round(high, 2),
            "recalibrate_after": CALIBRATION_MIN_SPRINTS,
            "enough_history": len(rows) >= CALIBRATION_MIN_SPRINTS,
            "note": "the token forecast is a HYPOTHESIS fitted to 6 units of one sprint, one "
                    "model, one repo; it is a BATCH tool with a weak per-unit signal, and it "
                    "is not re-fitted automatically"}


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


def _complexity_size(root: Path, text: str) -> int:
    """Max cognitive complexity across the files a unit will touch (0 if none resolve)."""
    paths = [str(r) for p in _affects_files(text) if (r := _resolve(root, p))]
    if not paths:
        return 0
    try:
        return complexity.assess(root, paths)["max_cognitive"]
    except Exception as exc:  # noqa: BLE001 - WSJF must degrade to priority, never break planning
        sdlc_md.debug("sprint._complexity_size", exc)
        return 0


def _effort_code(text: str) -> str | None:
    """The declared `Effort:` estimate normalised to S/M/L, or None when absent or unreadable.

    Reads the metadata field through the shared parser, so a CR's `**Effort:** M` (body) and a
    bug's `> **Effort:** L` (header) are the same field. Tolerates a decorated value
    (`M - two files`, `Large`); anything it cannot map is treated as undeclared, never guessed.
    """
    raw = sdlc_md.extract_field(text, "Effort")
    if not raw or not raw.strip():
        return None
    tok = raw.strip().split()[0].strip("*_`:,;.()").upper()
    tok = EFFORT_ALIAS.get(tok, tok)
    return tok if tok in EFFORT_SIZE else None


def _token_budget(complexity_seed: int, effort: str | None) -> int:
    """One unit's token forecast: the measured fixed floor plus the blast-radius slope.

    When the unit declares no `Affects` (complexity 0) the human effort estimate stands in as
    the seed, so a Large unit no longer forecasts the same flat base as a Small one. A unit
    that DOES resolve complexity keeps the measured model unchanged - effort never inflates it.
    """
    seed = complexity_seed or EFFORT_COMPLEXITY_PROXY.get(effort or "", 0)
    return BASE_TOKEN_BUDGET + TOKENS_PER_COGNITIVE * seed


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
    """Tiebreak order among ready units: highest WSJF first, else priority then the
    smaller blast-radius job, else priority then id. Shared by topo order + waves."""
    w = _weight(it["priority"])
    if "wsjf" in it:
        return (-it["wsjf"], w, it["id"])
    if "complexity" in it:
        return (w, it["complexity"], it["id"])
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


def wsjf_score(value: float, time_criticality: float, risk_reduction: float, size: float) -> float:
    """WSJF = (value + time-criticality + risk-reduction) / job size. Size >= 1."""
    return round((value + time_criticality + risk_reduction) / max(size, 1), 3)


def _wsjf_inputs(root: Path) -> dict:
    """Per-unit value/time-criticality/risk-reduction the review seats scored, written
    to `sdlc-studio/.local/wsjf-inputs.json` by the model after the PO/Eng/QA consult. Keyed by
    normalised id. Absent -> {} -> the planner falls back to priority + complexity."""
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
    """WSJF enrichment + dependency-topological ordering over one (possibly mixed) batch."""
    _enrich_routing(root, out)  # difficulty always; tier/model when routing.enabled
    if order == "wsjf":  # seat-scored WSJF when available, else priority+complexity
        seat_inputs = {} if skip_personas else _wsjf_inputs(root)
        for it in out:
            text = Path(it["path"]).read_text(encoding="utf-8")
            seed = _complexity_size(root, text)
            effort = _effort_code(text)
            it["complexity"] = seed
            if effort:
                it["effort"] = effort
            it["token_budget"] = _token_budget(seed, effort)
            inp = seat_inputs.get(sdlc_md.norm_id(it["id"]))
            # Size, in falling order of authority: the Engineering seat's estimate
            # (wsjf-inputs `size`), else the human `Effort:` recorded on the artefact,
            # else the declared neutral default. The complexity seed is blast-radius
            # risk (tiebreak + token budget), never the size - a one-line fix in a
            # complex file must not sink.
            seat_size = (inp or {}).get("size")
            if isinstance(seat_size, (int, float)) and seat_size > 0:
                size = seat_size
            elif effort:
                size = EFFORT_SIZE[effort]
            else:
                size = DEFAULT_UNKNOWN_SIZE
            it["size"] = size
            if inp:  # the review seats scored this unit (value / time-criticality / risk)
                it["value"] = inp.get("value", 0)
                it["time_criticality"] = inp.get("time_criticality", 0)
                it["risk_reduction"] = inp.get("risk_reduction", 0)
                it["wsjf"] = wsjf_score(it["value"], it["time_criticality"],
                                        it["risk_reduction"], size)
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
    """The batch's token cost as a FORECAST - the plan's existing per-unit estimate
    (`BASE_TOKEN_BUDGET` + `TOKENS_PER_COGNITIVE` x seed, where the seed is blast-radius
    complexity, or the declared effort when the unit names no files) summed. It is an
    ESTIMATE and never a gate: a script cannot observe real token spend (see telemetry.py), so
    a token ceiling would depend on the actor self-reporting the budget meant to constrain it.
    The wall-clock / unit-count appetite is the breaker; this only informs the operator."""
    total = 0
    per_unit: dict[str, int] = {}
    for it in batch:
        budget = it.get("token_budget")
        if budget is None:  # priority/manual order never stamped one - derive it here
            text = Path(it["path"]).read_text(encoding="utf-8")
            seed = it.get("complexity")
            if seed is None:
                seed = _complexity_size(root, text)
            budget = _token_budget(seed, _effort_code(text))
        per_unit[sdlc_md.norm_id(it["id"])] = budget
        total += budget
    return {"tokens": total, "per_unit": per_unit,
            "basis": "plan per-unit estimate (base + complexity blast-radius, or the declared "
                     "effort when no files are named); an ESTIMATE, never a gate - a script "
                     "cannot observe token spend"}


# ---------------------------------------------------------------------------
# The breakdown gate: a plan over an UNGROOMED batch is REFUSED.
# ---------------------------------------------------------------------------
# A plan that looks authoritative over units nobody was required to groom is the false
# authority this gate exists to abolish. A unit that names no files cannot be sized: the
# complexity seed is 0, so the forecast collapses to the flat per-unit floor, and the
# planner cannot see that two units touch the SAME FILE - so it reports them as safely
# parallel when they will collide. Both gaps were closed by hand before every plan.
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

# A CR at or above this many declared files, or declared Large, is doing enough work to warrant
# stories: only a story carries executable `Verify:` lines, so an un-decomposed CR's Done is
# gated on prose. Advisory - "where the work warrants" is a judgement the report can only name.
DECOMPOSE_FILE_THRESHOLD = 5


def breakdown_mode(repo_root: Path | str) -> str:
    """`enforce` (the default) or the recorded opt-out `judgement`. Never fails open."""
    mode = str(config.get(repo_root, "sprint.breakdown", "enforce") or "enforce").strip().lower()
    return mode if mode in BREAKDOWN_MODES else "enforce"


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


def _declared_size(text: str, seat: dict | None) -> str | None:
    """The size a PERSON recorded for this unit, from any accepted source, or None.

    Accepted, in falling order of authority: the review seat's estimate, the artefact's
    `Effort:` (S/M/L), a story's `Points:`. With none of the three the unit is UNSIZED - the
    forecast would quote it at the flat floor and the operator would never know that number
    was a fallback rather than an estimate."""
    seat_size = (seat or {}).get("size")
    if isinstance(seat_size, (int, float)) and seat_size > 0:
        return f"seat size {seat_size}"
    effort = _effort_code(text)
    if effort:
        return f"Effort: {effort}"
    raw = sdlc_md.extract_field(text, "Points")
    if raw and raw.strip():
        tok = raw.strip().split()[0].strip("*_`:,;.()")
        try:
            if float(tok) > 0:
                return f"Points: {tok}"
        except ValueError:
            pass
    return None


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

    A unit is groomed when it declares the files it will touch (`Affects`) AND a size somebody
    actually recorded. Everything else the lane surfaces - shared-file clusters, CRs big enough
    to warrant stories - is derived from the same two fields, at no extra cost to the operator.
    Read-only: it reports, and `cmd_plan` decides what to do about it."""
    root = Path(repo_root)
    seats = {} if skip_personas else _wsjf_inputs(root)
    cited = _ids_cited_by_stories(root)
    ungroomed: list[dict] = []
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
        size = _declared_size(text, seats.get(sdlc_md.norm_id(it["id"])))
        files_by_unit[it["id"]] = sorted({_affect_key(root, p) for p in declared})
        missing = ([] if declared else ["Affects"]) + ([] if size else ["size"])
        if missing:
            ungroomed.append({"id": it["id"], "type": it["type"], "path": it["path"],
                              "missing": missing})
        else:
            groomed.append(it["id"])
        if it["type"] == "cr" and sdlc_md.norm_id(it["id"]) not in cited:
            big = _effort_code(text) == "L"
            wide = len(declared) >= DECOMPOSE_FILE_THRESHOLD
            if big or wide:
                why = ("declared Large" if big
                       else f"touches {len(declared)} files")
                decompose.append({"id": it["id"], "why": why})
    mode = breakdown_mode(root)
    return {"mode": mode, "blocking": mode != "judgement",
            "ungroomed": ungroomed, "groomed": groomed,
            "clusters": _shared_file_clusters(files_by_unit),
            "decompose": decompose,
            "ok": not ungroomed}


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


def _breakdown_detail(bd: dict) -> list[str]:
    """The ungroomed units, one line each: which unit, what it lacks, where it lives."""
    return [f"    {u['id']:<8} lacks: {', '.join(u['missing']):<15} {u['path']}"
            for u in bd["ungroomed"]]


BREAKDOWN_FIX = """  fix each one on the artefact, then re-plan:
    Affects   > **Affects:** path/to/file.py, path/to/other.py
              the files the unit will touch. Without it nothing can size the unit, and
              nothing can see that two units touch the same file.
    size      > **Effort:** S|M|L    (bug/CR - the job size of the work, not its urgency)
              > **Points:** 3        (story)
              or have the review seats score it -> sdlc-studio/.local/wsjf-inputs.json
  see the whole grooming list, read-only:  sprint.py breakdown {sel}
  opt out ONLY as a recorded decision: set `sprint.breakdown: judgement` in
  sdlc-studio/.config.yaml and this lane reports instead of blocking. Omission is not an
  escape - an absent config BLOCKS."""


def _refuse_ungroomed(bd: dict, count: int, sel: str) -> None:
    """The refusal. It is the only message the operator gets, so it teaches: what is wrong,
    why a plan over it would be worse than no plan, exactly how to fix each unit, and how to
    opt out on purpose."""
    n = len(bd["ungroomed"])
    print(f"sprint plan REFUSED: {n} of {count} unit(s) are ungroomed. NO PLAN WAS PRINTED.\n",
          file=sys.stderr)
    print("  A plan over unsized units is false authority. A unit that names no files cannot\n"
          "  be sized (the forecast silently falls back to a flat floor), and the planner\n"
          "  cannot see that two units touch the same file - so it reports them as safely\n"
          "  parallel when they will collide. A plan you cannot trust is worse than no plan.\n",
          file=sys.stderr)
    print("  ungroomed:", file=sys.stderr)
    print("\n".join(_breakdown_detail(bd)), file=sys.stderr)
    print(BREAKDOWN_FIX.format(sel=sel), file=sys.stderr)


def _report_ungroomed(bd: dict, count: int) -> None:
    """The recorded opt-out (`sprint.breakdown: judgement`): the lane still REPORTS, it just
    does not block. An opt-out that also went quiet would be the disease, not the cure."""
    n = len(bd["ungroomed"])
    print(f"breakdown: {n} of {count} unit(s) are ungroomed - planning anyway "
          f"(sprint.breakdown: judgement). Their forecast is a flat floor, not an estimate:",
          file=sys.stderr)
    print("\n".join(_breakdown_detail(bd)), file=sys.stderr)


# Lessons printed in the text plan before the tail is elided. One line per lesson costs
# roughly 40 tokens, so the whole of a mature registry fits inside a rounding error on a
# sprint plan; the cap exists to bound the display, not to ration the content. Growth is
# handled by decay (`revalidate` closes what no longer holds), never by silent truncation.
PLAN_DIGEST_MAX = 50

# The cross-project registry is ranked, so a cap here drops the LEAST-biting lessons, not
# an arbitrary tail. The top of this list is what the next mistake is most likely to be.
CROSS_DIGEST_MAX = 12


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
    """The batch's token forecast, quoted as a RANGE, never a bare number. The point estimate
    on its own reads as a fact; it is a hypothesis that has already been ~30% out."""
    tf = data.get("token_forecast")
    if not tf or not tf.get("tokens"):
        return
    cap = data.get("capacity") or {}
    fc = cap.get("forecast") or {}
    band = (f" (plausible {fc['low']:,}-{fc['high']:,})"
            if fc.get("low") and fc.get("high") else "")
    print(f"  token forecast: ~{tf['tokens']:,} tokens across {data['count']} unit(s)"
          f"{band} - an estimate, never a gate")


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
    sprints = cal["sprints"]
    ratios = ", ".join(f"{r}x" for r in cal["ratios"])
    history = (f"{sprints} measured sprint(s), est/actual {ratios}" if sprints
               else "no measured sprints yet")
    enough = ("enough history to recalibrate - a human should re-read the trend"
              if cal["enough_history"]
              else f"not enough history to recalibrate (need {cal['recalibrate_after']})")
    print(f"  capacity: the token half is a FORECAST, not a measurement - a script cannot "
          f"observe token spend, and the model is a hypothesis fitted to one sprint. "
          f"Calibration: {history}; {enough}. Nothing is re-fitted automatically.")
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
    _render_decompose(data)
    _render_token_forecast(data)
    _render_capacity(data)
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
          f"{len(bd['clusters'])} shared-file cluster(s) (mode={bd['mode']})")
    if bd["ungroomed"]:
        print("  ungroomed - `sprint plan` refuses a batch holding any of these:")
        print("\n".join(_breakdown_detail(bd)))
        print(BREAKDOWN_FIX.format(sel=_selector_hint(args, queries, worklist)))
    _render_clusters({"breakdown": bd})
    _render_decompose({"breakdown": bd})
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    """Print the ordered batch the operator approves before a run."""
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
    # THE BREAKDOWN GATE. Before anything is printed, written, or opened: is this batch
    # groomed enough to plan? An ungroomed batch is REFUSED - blocking, non-zero, and no plan
    # at all, because a plan over unsized units is exactly the false authority the gate exists
    # to abolish. It fires here, ahead of the drift preflight, so a refusal costs no fetch.
    bd = data.get("breakdown")
    if bd and bd["ungroomed"]:
        if bd["blocking"]:
            _refuse_ungroomed(bd, data["count"], _selector_hint(args, queries, worklist))
            return 2
        _report_ungroomed(bd, data["count"])
    rc = _origin_drift_preflight(args, data)
    if rc is not None:
        return rc
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
        if data.get("token_forecast"):
            extra["token_forecast"] = data["token_forecast"]["tokens"]
        state = run_state.update(args.root, **extra)
        print(f"opened run {state['run_id']} (goal={state['goal'] or 'unset'}, appetite "
              f"{appetite['minutes']:g}min/{appetite['units']}units) "
              f"-> {run_state.path(args.root)}")
    _render_plan(args, data, queries, worklist, epics)
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
                   help="ignore review-seat WSJF inputs; order by priority + complexity")
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

    sdlc_md.add_global_root(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
