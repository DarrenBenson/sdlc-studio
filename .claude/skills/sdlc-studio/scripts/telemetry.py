#!/usr/bin/env python3
"""Run telemetry recorder.

Append a per-unit run outcome to the gitignored `sdlc-studio/.local/telemetry.jsonl` so estimation and
the complexity/churn calibration can become continuous instead of one-off.
**Local-only, no upload, no network.** Tokens are recorded only when the caller passes them
(a script cannot read them reliably). The loop wires `record` on each unit close.

It also holds the OTHER side of the estimate-vs-actual ratio: the plan-time FORECAST log
(`sdlc-studio/.local/forecasts.jsonl`). A forecast that is not recorded when it is made does
not exist - re-deriving it later, from the constants it is meant to be judging, is not a
prediction. See the forecast section below.

Subcommands:
  record    Append one run-outcome record.
  forecast  Append one plan-time forecast record (what the planner predicted, and with what).
  show      Print the recorded records (count + the JSON); `--forecasts` for the forecast log.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # resolve sibling imports (critic)
from lib import sdlc_md  # noqa: E402

# The project's gitignored state dir (sdlc-studio/.local/), not repo-root .local/.
LOCAL = Path("sdlc-studio") / ".local" / "telemetry.jsonl"
# The captured fields. Optional ones are omitted when not supplied. The tier_* fields
# (routing) record which model tier was recommended vs actually delivered a unit,
# so per-tier escape/escalation rates become measurable - the routing calibration loop.
FIELDS = ("id", "type", "iterations", "wall_time_s", "stages", "critic_verdict",
          "complexity", "churn", "reopened", "tokens",
          "tier_recommended", "tier_delivered", "model", "escalated")


def _path(repo_root: Path | str) -> Path:
    return Path(repo_root) / LOCAL


def record(repo_root: Path | str, fields: dict) -> dict:
    """Append one record (only the recognised, non-None fields). Best-effort: a write
    failure is swallowed (telemetry must never break the loop)."""
    rec = {k: fields[k] for k in FIELDS if fields.get(k) is not None}
    try:
        p = _path(repo_root)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
        sdlc_md.roll_jsonl(p)  # bound the append-only telemetry log
    except Exception as exc:  # noqa: BLE001 - telemetry is advisory; never raise into the loop
        sdlc_md.debug("telemetry.record", exc)
    return rec


def record_plan_review(repo_root: Path | str, unit: str, verdict: str,
                       reviewer: str, author: str) -> dict:
    """Append a plan-review outcome event (US0091) so the gate's value is measurable over
    time: how often plan-review runs, its verdict mix, and that it was independent. Best-effort
    (a write failure never breaks the recording path). Carries an `event: "plan-review"` marker
    AND a `phase` field; `summarise` reads it as a distinct block, never as a unit-close type.
    Independence uses the SAME notion as the gate (`critic.is_independent`), so the `-` sentinel
    and empty author read as not-independent - the metric cannot over-report independence. The
    whole thing is best-effort: neither the independence read nor the write raises into the loop."""
    try:
        import critic  # lazy: telemetry is a leaf; critic has no telemetry dep
        independent = critic.is_independent({"author": author, "reviewer": reviewer})
    except Exception:  # noqa: BLE001 - never raise into the recording path; fall back locally
        def _norm(x):
            x = (x or "").strip().casefold()
            return "" if x == "-" else x
        a, r = _norm(author), _norm(reviewer)
        independent = bool(a) and r != a
    rec = {"event": "plan-review", "phase": "plan-review", "id": str(unit),
           "verdict": (verdict or "").upper(), "reviewer": reviewer, "author": author,
           "independent": independent}
    try:
        p = _path(repo_root)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
        sdlc_md.roll_jsonl(p)  # bound the append-only telemetry log
    except Exception as exc:  # noqa: BLE001 - telemetry is advisory; never raise into the loop
        sdlc_md.debug("telemetry.record", exc)
    return rec


def read_all(repo_root: Path | str) -> list[dict]:
    """All records; malformed lines are skipped (a corrupt line never breaks a read)."""
    out: list[dict] = []
    try:
        text = _path(repo_root).read_text(encoding="utf-8")
    except OSError:
        return out
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


#: The per-unit fields an actual is made of. `type` and `model` are context, not
#: measurements; the rest are what a run actually cost.
ACTUAL_FIELDS = ("type", "model", "tokens", "wall_time_s", "iterations", "complexity",
                 "churn", "critic_verdict")


def latest_actuals(records: list[dict]) -> dict[str, dict]:
    """Per-unit measured actuals, keyed by normalised id: the LAST non-null value seen for
    each field.

    Last-non-null, not last-record. The loop appends a second, bare record on close
    (`{"id": "BG0126", "type": "bug"}`), so taking the last record wholesale would erase a
    measurement that was genuinely taken. A field no record ever carried stays ABSENT - it is
    never defaulted to 0, because an unmeasured unit must be reportable as unmeasured rather
    than as a unit that cost nothing.

    Event records (plan-review) are not unit closes and are excluded.
    """
    out: dict[str, dict] = {}
    for rec in records:
        if rec.get("event"):
            continue
        rid = sdlc_md.norm_id(str(rec.get("id") or "").strip())
        if not rid:
            continue
        bucket = out.setdefault(rid, {})
        for field in ACTUAL_FIELDS:
            val = rec.get(field)
            if val is not None:
                bucket[field] = val
    return out


def actuals(repo_root: Path | str) -> dict[str, dict]:
    """`latest_actuals` over the project's telemetry log. The single read the retro's
    estimate-vs-actual report goes through."""
    return latest_actuals(read_all(repo_root))


# ---------------------------------------------------------------------------
# The forecast log: what the planner PREDICTED, recorded when it predicted it.
# ---------------------------------------------------------------------------
# The actuals above are one side of the estimate-vs-actual ratio. This is the other side, and
# it has to be a RECORD for exactly the same reason they do.
#
# An estimate re-derived at judgement time, from the constants it is meant to be judging, is
# not a prediction. Recalibrate and every past sprint is retroactively deemed to have forecast
# something else, so the ratio drifts toward 1.0x and the loop can never falsify its own
# estimator. It is not hypothetical: a recorded 5.2x miss was the entire evidence for a
# recalibration, and the recalibration erased it.
#
# It lives NEXT TO the actuals, in the same gitignored run-state directory, because it is the
# same kind of thing: a per-unit run record, keyed by unit id, written once by the tool that
# observed it. Its own file rather than a record type inside telemetry.jsonl, so the bounded
# roll on the append-only actuals log can never evict a forecast; and this log is deliberately
# NOT rolled, because the record it would drop first is the oldest - the authoritative one.
#
# FIRST WINS. The reader takes the EARLIEST record for a unit. Re-planning a batch after the
# work is done must not be able to rewrite what was predicted before it started; a later record
# is kept as history and never overrides. Hindsight is not a forecast.
FORECASTS = Path("sdlc-studio") / ".local" / "forecasts.jsonl"

#: A forecast record. `tokens` is the number the plan quoted; `seed` is the complexity/effort
#: input it came from; `constants` is the estimator that produced it (so a later reader can
#: tell whether the row was forecast by the constants now in force, or by a different model);
#: `planned_at` is when the plan was made.
FORECAST_FIELDS = ("id", "tokens", "seed", "seed_source", "complexity", "effort",
                   "constants", "planned_at")


def _forecast_path(repo_root: Path | str) -> Path:
    return Path(repo_root) / FORECASTS


def read_forecasts(repo_root: Path | str) -> list[dict]:
    """Every forecast record, oldest first. A malformed line is skipped, never fatal."""
    out: list[dict] = []
    try:
        text = _forecast_path(repo_root).read_text(encoding="utf-8")
    except OSError:
        return out
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if isinstance(rec, dict) and rec.get("id"):
            out.append(rec)
    return out


def forecasts(repo_root: Path | str) -> dict[str, dict]:
    """The plan-time forecast per unit, keyed by normalised id. FIRST record wins - see the
    note above. The single read the retro's estimate-vs-actual report goes through; it never
    recomputes an estimate."""
    out: dict[str, dict] = {}
    for rec in read_forecasts(repo_root):
        rid = sdlc_md.norm_id(str(rec.get("id") or "").strip())
        if rid:
            out.setdefault(rid, rec)
    return out


def record_forecasts(repo_root: Path | str, records: list[dict]) -> dict:
    """Append the plan's per-unit forecasts. Idempotent: a record identical to one already
    held for that unit (same tokens, same constants) is not written twice, so re-planning an
    unchanged batch does not grow the log.

    NOT best-effort, unlike `record`. A telemetry write that fails costs a measurement; a
    forecast write that fails silently would leave the planner announcing a forecast that was
    never recorded, which is the whole defect. The caller is told, and says so.
    """
    have = read_forecasts(repo_root)
    seen = {(sdlc_md.norm_id(str(r.get("id"))), r.get("tokens"),
             json.dumps(r.get("constants"), sort_keys=True)) for r in have}
    fresh: list[dict] = []
    already: list[str] = []
    for rec in records:
        rid = sdlc_md.norm_id(str(rec.get("id") or "").strip())
        if not rid:
            continue
        key = (rid, rec.get("tokens"), json.dumps(rec.get("constants"), sort_keys=True))
        if key in seen:
            already.append(rid)
            continue
        seen.add(key)
        row = {k: rec[k] for k in FORECAST_FIELDS if rec.get(k) is not None}
        row["id"] = rid
        fresh.append(row)
    if fresh:
        p = _forecast_path(repo_root)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as fh:
            for row in fresh:
                fh.write(json.dumps(row) + "\n")
    return {"path": str(_forecast_path(repo_root)),
            "recorded": [r["id"] for r in fresh], "already": already}


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def cmd_record(args: argparse.Namespace) -> int:
    fields = {"id": args.id, "type": args.type, "iterations": _int(args.iterations),
              "wall_time_s": _int(args.wall_time_s), "stages": args.stages,
              "critic_verdict": args.verdict, "complexity": _int(args.complexity),
              "churn": _int(args.churn), "reopened": args.reopened, "tokens": _int(args.tokens),
              "tier_recommended": args.tier_recommended,
              "tier_delivered": args.tier_delivered,
              "model": args.model, "escalated": args.escalated}
    rec = record(args.root, fields)
    print(json.dumps(rec) if args.format == "json" else f"recorded {rec.get('id', '?')}")
    return 0


def summarise(records: list[dict]) -> dict:
    """Per-type aggregates over the raw records: count, mean iterations, mean wall
    time, reopen rate, verdict mix. A field absent from every record of a type is
    None, never a fabricated 0 - the summary reports what was measured.

    Event records (those carrying an `event` key, e.g. plan-review) are NOT unit-close
    records and are excluded from the per-type/per-tier aggregates - pooling them would inflate
    a phantom `unknown` type. Plan-review events are summarised in their own `plan_review` block
    (US0091): count, verdict mix, and the independent-review rate."""
    unit_recs = [r for r in records if not r.get("event")]
    out: dict = {}
    for rec in unit_recs:
        t = rec.get("type") or "unknown"
        b = out.setdefault(t, {"count": 0, "_iters": [], "_wall": [],
                               "_reopened": [], "verdicts": {}})
        b["count"] += 1
        if isinstance(rec.get("iterations"), (int, float)):
            b["_iters"].append(rec["iterations"])
        if isinstance(rec.get("wall_time_s"), (int, float)):
            b["_wall"].append(rec["wall_time_s"])
        if rec.get("reopened") is not None:
            b["_reopened"].append(str(rec["reopened"]).strip().lower() in ("yes", "true", "1"))
        v = rec.get("critic_verdict")
        if v:
            b["verdicts"][v] = b["verdicts"].get(v, 0) + 1
    for b in out.values():
        iters, wall, reop = b.pop("_iters"), b.pop("_wall"), b.pop("_reopened")
        b["mean_iterations"] = round(sum(iters) / len(iters), 2) if iters else None
        b["mean_wall_time_s"] = round(sum(wall) / len(wall), 2) if wall else None
        b["reopen_rate"] = round(sum(reop) / len(reop), 3) if reop else None
    # Per-delivered-tier grouping (verdict mix + reopen rate) - the routing
    # calibration signal. Emitted only when some record actually carries a tier, so a
    # non-routed project's summary is byte-identical to before.
    tiers: dict = {}
    for rec in unit_recs:
        t = rec.get("tier_delivered")
        if not t:
            continue
        b = tiers.setdefault(t, {"count": 0, "_reopened": [], "_escalated": [],
                                  "verdicts": {}})
        b["count"] += 1
        if rec.get("reopened") is not None:
            b["_reopened"].append(str(rec["reopened"]).strip().lower() in ("yes", "true", "1"))
        if rec.get("escalated") is not None:
            b["_escalated"].append(str(rec["escalated"]).strip().lower() in ("yes", "true", "1"))
        v = rec.get("critic_verdict")
        if v:
            b["verdicts"][v] = b["verdicts"].get(v, 0) + 1
    if tiers:
        for b in tiers.values():
            reop, esc = b.pop("_reopened"), b.pop("_escalated")
            b["reopen_rate"] = round(sum(reop) / len(reop), 3) if reop else None
            b["escalation_rate"] = round(sum(esc) / len(esc), 3) if esc else None
        out["by_tier"] = tiers
    # Plan-review events (their own block, US0091): how often the gate ran, its verdict mix,
    # and the independent-review rate - so the gate's value is measurable.
    pr_events = [r for r in records if r.get("event") == "plan-review"]
    if pr_events:
        verdicts: dict = {}
        for r in pr_events:
            v = r.get("verdict")
            if v:
                verdicts[v] = verdicts.get(v, 0) + 1
        indep = [bool(r.get("independent")) for r in pr_events]
        out["plan_review"] = {
            "count": len(pr_events), "verdicts": verdicts,
            "independent_rate": round(sum(indep) / len(indep), 3) if indep else None}
    return out


def cmd_forecast(args: argparse.Namespace) -> int:
    """Record ONE plan-time forecast by hand. `sprint plan` records the batch's forecasts
    itself; this exists so a forecast recoverable from the record (an old retro's own
    estimate-vs-actual table) can be restored, and so the log can be inspected."""
    rec = {"id": args.id, "tokens": _int(args.tokens), "seed": _int(args.seed),
           "seed_source": args.seed_source, "effort": args.effort,
           "planned_at": args.planned_at or sdlc_md.now_iso8601(),
           "constants": {"BASE_TOKEN_BUDGET": _int(args.base),
                         "TOKENS_PER_COGNITIVE": _int(args.per_cognitive)}}
    res = record_forecasts(args.root, [rec])
    if args.format == "json":
        print(json.dumps(res, indent=2))
    elif res["recorded"]:
        print(f"recorded forecast {args.id} ({rec['tokens']:,} tokens) -> {res['path']}")
    else:
        print(f"forecast {args.id} already recorded, unchanged - the first one stands")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    if getattr(args, "forecasts", False):
        recs = read_forecasts(args.root)
        if args.format == "json":
            print(json.dumps(recs, indent=2))
            return 0
        for r in recs:
            c = r.get("constants") or {}
            print(f"  {r['id']:8} est={r.get('tokens', 0):>9,}  seed={r.get('seed')}  "
                  f"base={c.get('BASE_TOKEN_BUDGET')} tpc={c.get('TOKENS_PER_COGNITIVE')}  "
                  f"planned {r.get('planned_at', '-')}")
        print(f"{len(recs)} forecast record(s); the FIRST for a unit is its plan-time forecast")
        return 0
    recs = read_all(args.root)
    if getattr(args, "summary", False):
        s = summarise(recs)
        if args.format == "json":
            print(json.dumps(s, indent=2))
        else:
            by_tier = s.pop("by_tier", None)
            plan_review = s.pop("plan_review", None)
            unit_n = sum(b["count"] for b in s.values())
            print(f"{unit_n} unit record(s), {len(s)} type(s)")
            for t, b in sorted(s.items()):
                verdicts = ", ".join(f"{k}:{n}" for k, n in sorted(b["verdicts"].items())) or "-"
                print(f"  {t:8} count={b['count']} mean_iterations={b['mean_iterations']} "
                      f"mean_wall_time_s={b['mean_wall_time_s']} "
                      f"reopen_rate={b['reopen_rate']} verdicts[{verdicts}]")
            if plan_review:
                verdicts = ", ".join(f"{k}:{n}" for k, n in
                                     sorted(plan_review["verdicts"].items())) or "-"
                print(f"plan-review: count={plan_review['count']} "
                      f"independent_rate={plan_review['independent_rate']} verdicts[{verdicts}]")
            if by_tier:
                print("by tier delivered:")
                for t, b in sorted(by_tier.items()):
                    verdicts = ", ".join(f"{k}:{n}" for k, n in sorted(b["verdicts"].items())) or "-"
                    print(f"  {t:8} count={b['count']} reopen_rate={b['reopen_rate']} "
                          f"escalation_rate={b['escalation_rate']} verdicts[{verdicts}]")
        return 0
    print(json.dumps(recs, indent=2) if args.format == "json" else f"{len(recs)} record(s)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run telemetry recorder.")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record", help="Append one run-outcome record.")
    r.add_argument("--id"); r.add_argument("--type"); r.add_argument("--iterations")
    r.add_argument("--wall-time-s", dest="wall_time_s"); r.add_argument("--stages")
    r.add_argument("--verdict"); r.add_argument("--complexity"); r.add_argument("--churn")
    r.add_argument("--reopened"); r.add_argument("--tokens")
    r.add_argument("--tier-recommended", dest="tier_recommended")
    r.add_argument("--tier-delivered", dest="tier_delivered")
    r.add_argument("--model"); r.add_argument("--escalated")
    r.add_argument("--root", default="."); r.add_argument("--format", choices=("text", "json"), default="text")
    r.set_defaults(func=cmd_record)
    f = sub.add_parser("forecast", help="Record one plan-time token forecast (the estimate side "
                                        "of the ratio; `sprint plan` records a batch's itself).")
    f.add_argument("--id", required=True); f.add_argument("--tokens", required=True)
    f.add_argument("--seed", help="the complexity/effort input the forecast came from")
    f.add_argument("--seed-source", dest="seed_source", default="complexity",
                   choices=("complexity", "effort", "none"))
    f.add_argument("--effort", help="the declared Effort (S/M/L), when there was one")
    f.add_argument("--base", required=True, help="BASE_TOKEN_BUDGET in force at plan time")
    f.add_argument("--per-cognitive", dest="per_cognitive", required=True,
                   help="TOKENS_PER_COGNITIVE in force at plan time")
    f.add_argument("--planned-at", dest="planned_at", help="when the plan was made (ISO8601)")
    f.add_argument("--root", default=".")
    f.add_argument("--format", choices=("text", "json"), default="text")
    f.set_defaults(func=cmd_forecast)
    s = sub.add_parser("show", help="Print recorded records.")
    s.add_argument("--summary", action="store_true",
                   help="aggregate per type: count, mean iterations/wall-time, reopen rate, verdict mix")
    s.add_argument("--forecasts", action="store_true",
                   help="print the plan-time forecast log instead of the measured actuals")
    s.add_argument("--root", default="."); s.add_argument("--format", choices=("text", "json"), default="text")
    s.set_defaults(func=cmd_show)
    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
