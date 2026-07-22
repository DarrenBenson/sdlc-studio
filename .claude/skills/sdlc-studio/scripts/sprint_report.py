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


def _run_window(root: Path, unit_ids: list[str]) -> tuple | None:
    """`(started_at, ended_at)` of the run that delivered THIS sprint, or None.

    Same guard as `_sprint_goal`: a run record counts only when its batch names this sprint's
    units. Where more than one does, the record covering MOST of them wins, live or archived
    alike. Trying the live record first regardless was the same defect one level up: a run that
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
    best = None                   # (units covered, started_at, ended_at)
    for state in records:
        batch = {sdlc_md.norm_id(u) for u in (state.get("batch") or [])}
        cover = len(batch & want)
        if not cover:
            continue
        start = telemetry._parse_iso(state.get("started_at"))  # noqa: SLF001 - ONE stamp reader
        if start is None:
            continue              # a run with no start bounds nothing
        if best is None or cover > best[0]:
            best = (cover, start, telemetry._parse_iso(state.get("ended_at")))  # noqa: SLF001
    return (best[1], best[2]) if best else None


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
    return {
        "ok": True, "id": retro_id, "date": acc.get("date", ""),
        "sprint_goal": goal, "sprint_goal_verdict": goal_verdict,
        "flow": _flow_summary(Path(root)),
        "mutation": _mutation_summary(Path(root), unit_ids),
        "units": unit_ids,
        "delivered_points": b.get("delivered_points"),
        "spend": _spend(root, unit_ids),
        "sprint_actual_tokens": b.get("sprint_actual_tokens"),
        "velocity": {
            "points_per_elapsed_hour": b.get("points_per_elapsed_hour"),
            "elapsed_hours": b.get("sprint_elapsed_hours"),
            "elapsed_source": b.get("elapsed_source"),
            "points_per_worker_hour": b.get("points_per_worker_hour"),
            "tokens_per_point": b.get("tokens_per_point"),
            "sprint_tokens_per_point": b.get("sprint_tokens_per_point"),
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
    lines.append(f"Delivered: {len(rep['units'])} unit(s), {rep['delivered_points']} points.")
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
    acc = rep["accuracy"]
    if acc["refused"]:
        lines.append(f"Estimate vs actual: {acc['refused']}")
    elif acc["ratio"]:
        lines.append(f"Estimate vs actual: {acc['ratio']}x (>1 = over-forecast), over "
                     f"{acc['n_measured']} measured unit(s).")
    if acc["models"]:
        lines.append(f"Models: {', '.join(acc['models'])}.")
    lines.extend(_mutation_lines(rep.get("mutation")))
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
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
