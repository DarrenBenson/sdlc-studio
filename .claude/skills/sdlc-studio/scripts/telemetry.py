#!/usr/bin/env python3
"""Run telemetry recorder.

Append a per-unit run outcome to the gitignored `sdlc-studio/.local/telemetry.jsonl` so estimation and
the complexity/churn calibration can become continuous instead of one-off.
**Local-only, no upload, no network.** Tokens are recorded only when the caller passes them
(a script cannot read them reliably). The loop wires `record` on each unit close.

Subcommands:
  record   Append one run-outcome record.
  show     Print the recorded records (count + the JSON).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # resolve sibling imports (critic)

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
    except Exception:  # noqa: BLE001 - telemetry is advisory; never raise into the loop
        pass
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
    except Exception:  # noqa: BLE001 - telemetry is advisory; never raise into the loop
        pass
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


def cmd_show(args: argparse.Namespace) -> int:
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
    s = sub.add_parser("show", help="Print recorded records.")
    s.add_argument("--summary", action="store_true",
                   help="aggregate per type: count, mean iterations/wall-time, reopen rate, verdict mix")
    s.add_argument("--root", default="."); s.add_argument("--format", choices=("text", "json"), default="text")
    s.set_defaults(func=cmd_show)
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
