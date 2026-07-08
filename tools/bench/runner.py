#!/usr/bin/env python3
"""RFC0025 / CR0178 benchmark harness runner (repo-only, not shipped in the skill payload).

Drives the sdlc-studio-vs-plain-Claude-Code comparison over the fixtures in
`tools/bench/fixtures/`. This script does the deterministic parts only: setting up a
workspace for one (fixture, arm) run, scoring a finished workspace against the fixture's
held-back suite, and recording/summarising results. Actually running an agent against a
prepared workspace is done by the operator/orchestrator (an agent session), not by this
script - there is no API call inside this file.

Subcommands:
  prepare   Set up a workspace for one (fixture, arm) run.
  score     Run the held-back suite against a finished workspace.
  record    Append one run's metrics to the results log.
  summary   Aggregate results per fixture x arm.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BENCH_ROOT = Path(__file__).resolve().parent
FIXTURES_DIR = BENCH_ROOT / "fixtures"
ARMS_DIR = BENCH_ROOT / "arms"
RESULTS_PATH = BENCH_ROOT / "results" / "runs.jsonl"
SKILL_DIR = BENCH_ROOT.parent.parent / ".claude" / "skills" / "sdlc-studio"

ARM_CLAUDE_MD = {"A": ARMS_DIR / "pipeline_CLAUDE.md",
                 "B": ARMS_DIR / "baseline_CLAUDE.md",
                 "R": ARMS_DIR / "pipeline_routed_CLAUDE.md"}
# Arms whose workspace gets the skill copied IN (environmental isolation: arm B's
# workspace simply does not contain the skill, rather than being told not to use it).
SKILL_ARMS = ("A", "R")
# Arm R's workspace .config.yaml: routing enabled with the operator's model map,
# written at prepare time from arms/routed_config.yaml.
ROUTED_CONFIG = ARMS_DIR / "routed_config.yaml"


def list_fixtures(fixtures_dir: Path = FIXTURES_DIR) -> list[str]:
    """Fixture names, sorted, i.e. directories with both a visible/ and hidden/ subdir."""
    if not fixtures_dir.is_dir():
        return []
    return sorted(p.name for p in fixtures_dir.iterdir()
                  if p.is_dir() and (p / "visible").is_dir() and (p / "hidden").is_dir())


def prepare_workspace(fixture: str, arm: str, dest: Path,
                       fixtures_dir: Path = FIXTURES_DIR,
                       skill_dir: Path = SKILL_DIR) -> Path:
    """Copy the fixture's visible/ files plus the arm's CLAUDE.md into `dest`. Never touches
    the fixture's hidden/ (or audit/, reference/) content - that is the whole point of
    "held-back". Arms A/R additionally get the skill copied INTO the workspace
    (.claude/skills/sdlc-studio) so arm B's isolation is environmental - the skill is absent
    from B's world, not merely forbidden by instruction. Arm R also gets a .config.yaml
    enabling routing (from arms/routed_config.yaml)."""
    if arm not in ARM_CLAUDE_MD:
        raise ValueError(f"unknown arm {arm!r} - expected one of {sorted(ARM_CLAUDE_MD)}")
    visible = fixtures_dir / fixture / "visible"
    if not visible.is_dir():
        raise ValueError(f"unknown fixture {fixture!r} (no visible/ dir under {fixtures_dir})")
    dest.mkdir(parents=True, exist_ok=True)
    for item in visible.iterdir():
        target = dest / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)
    shutil.copy2(ARM_CLAUDE_MD[arm], dest / "CLAUDE.md")
    if arm in SKILL_ARMS:
        shutil.copytree(skill_dir, dest / ".claude" / "skills" / "sdlc-studio",
                        dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", ".local"))
    if arm == "R":
        cfg_dir = dest / "sdlc-studio"
        cfg_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROUTED_CONFIG, cfg_dir / ".config.yaml")
    return dest


def score(fixture: str, workspace: Path, fixtures_dir: Path = FIXTURES_DIR,
          timeout: int = 120) -> dict:
    """Run the fixture's held-back suite against `workspace`. Returns {"passed": bool,
    "defect_escape": bool, "output": str}. `defect_escape` is the inverse of `passed` - named
    per the protocol's metric, so callers don't have to remember to invert it. The hidden
    tree is copied whole (subdirectories included) into a scoring tempdir - pytest never
    runs from the fixture directory itself."""
    hidden = fixtures_dir / fixture / "hidden"
    if not hidden.is_dir():
        raise ValueError(f"unknown fixture {fixture!r} (no hidden/ dir under {fixtures_dir})")
    with tempfile.TemporaryDirectory() as scoring_dir:
        scoring_dir = Path(scoring_dir)
        for item in hidden.iterdir():
            target = scoring_dir / item.name
            if item.is_dir():
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(scoring_dir), "--workspace", str(workspace), "-q"],
            capture_output=True, text=True, timeout=timeout,
        )
        passed = result.returncode == 0
        return {"passed": passed, "defect_escape": not passed,
                "output": (result.stdout + result.stderr)[-4000:]}


def record(entry: dict, results_path: Path | None = None) -> dict:
    """Append one run's metrics. Required keys: fixture, arm, run_id. Optional: tokens,
    wall_time_s, iterations, defect_escape, rework. Unknown extra keys are kept as-is -
    this is a benchmark log, not a fixed schema like the skill's own telemetry.py.
    `results_path` resolves at CALL time (module attribute, not a def-time default) so
    tests can redirect it - a def-time default silently wrote test rows into the real log."""
    results_path = results_path if results_path is not None else RESULTS_PATH
    for k in ("fixture", "arm", "run_id"):
        if k not in entry:
            raise ValueError(f"record: missing required key {k!r}")
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with results_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    return entry


def read_all(results_path: Path | None = None) -> list[dict]:
    results_path = results_path if results_path is not None else RESULTS_PATH
    if not results_path.exists():
        return []
    out = []
    for line in results_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def _mean(vals: list) -> float | None:
    return round(sum(vals) / len(vals), 2) if vals else None


def _min_max(vals: list):
    return (round(min(vals), 2), round(max(vals), 2)) if vals else (None, None)


def parse_price_map(spec: str | None) -> dict:
    """`tiny=0.25,small=1,large=5` -> {tier: relative price}. Pricing is operator-supplied
    at invocation, never stored in the repo or the skill payload."""
    if not spec:
        return {}
    out = {}
    for part in spec.split(","):
        name, _, val = part.partition("=")
        if not name.strip() or not val.strip():
            raise ValueError(f"bad --price entry {part!r} - expected tier=number")
        out[name.strip()] = float(val)
    return out


def parse_model_mix(spec: str | None) -> dict:
    """`tiny:2,medium:1` -> {tier: unit count} - which tiers delivered how many units."""
    if not spec:
        return {}
    out = {}
    for part in spec.split(","):
        name, _, val = part.partition(":")
        if not name.strip() or not val.strip():
            raise ValueError(f"bad --model-mix entry {part!r} - expected tier:count")
        out[name.strip()] = int(val)
    return out


def cost_index(model_mix: dict, prices: dict) -> float | None:
    """Sum of units x relative tier price. None (never a fabricated 0) when the mix or
    any needed price is missing."""
    if not model_mix or not prices:
        return None
    if any(t not in prices for t in model_mix):
        return None
    return round(sum(n * prices[t] for t, n in model_mix.items()), 3)


def summarize(entries: list[dict], prices: dict | None = None) -> dict:
    """Per (fixture, arm) aggregates: n, defect_escape_rate, rework_rate, mean/min/max
    tokens and wall_time_s, mean audit score, and (when the operator supplies --price and
    runs carry a model mix) a mean cost index. A field absent from every entry in a group
    is None, not a fabricated 0."""
    prices = prices or {}
    groups: dict[tuple, list[dict]] = {}
    for e in entries:
        groups.setdefault((e.get("fixture"), e.get("arm")), []).append(e)
    out = {}
    for (fixture, arm), rows in sorted(groups.items()):
        tokens = [r["tokens"] for r in rows if isinstance(r.get("tokens"), (int, float))]
        wall = [r["wall_time_s"] for r in rows if isinstance(r.get("wall_time_s"), (int, float))]
        escapes = [r["defect_escape"] for r in rows if r.get("defect_escape") is not None]
        rework = [r["rework"] for r in rows if r.get("rework") is not None]
        audit = [r["audit_score"] for r in rows if isinstance(r.get("audit_score"), (int, float))]
        costs = [c for r in rows
                 if (c := cost_index(r.get("model_mix") or {}, prices)) is not None]
        g = {
            "n": len(rows),
            "mean_tokens": _mean(tokens),
            "mean_wall_time_s": _mean(wall),
            "defect_escape_rate": _mean([1 if v else 0 for v in escapes]),
            "rework_rate": _mean([1 if v else 0 for v in rework]),
        }
        g["min_tokens"], g["max_tokens"] = _min_max(tokens)
        g["min_wall_time_s"], g["max_wall_time_s"] = _min_max(wall)
        if audit:
            g["mean_audit_score"] = _mean(audit)
        if costs:
            g["mean_cost_index"] = _mean(costs)
        out[f"{fixture}::{arm}"] = g
    return out


def cmd_prepare(args: argparse.Namespace) -> int:
    dest = Path(args.dest)
    prepare_workspace(args.fixture, args.arm, dest)
    print(f"prepared {dest} ({args.fixture}, arm {args.arm})")
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    r = score(args.fixture, Path(args.workspace), timeout=args.timeout)
    print(json.dumps(r) if args.format == "json" else
          ("PASS" if r["passed"] else "FAIL (defect escape)"))
    return 0 if r["passed"] else 1


def cmd_record(args: argparse.Namespace) -> int:
    entry = {"fixture": args.fixture, "arm": args.arm, "run_id": args.run_id}
    if args.metrics_json:
        # automatic capture: tokens/wall-time parsed from the orchestrator's per-run
        # usage JSON (transcript_metrics.py output) - the preferred, disclosed-by-default path
        m = json.loads(Path(args.metrics_json).read_text(encoding="utf-8"))
        if m.get("tokens") is not None:
            entry["tokens"] = m["tokens"]
        if m.get("wall_time_s") is not None:
            entry["wall_time_s"] = m["wall_time_s"]
        entry["metrics_source"] = "parsed"
    if args.tokens is not None:
        entry["tokens"] = args.tokens
        entry["metrics_source"] = "manual"
    if args.wall_time_s is not None:
        entry["wall_time_s"] = args.wall_time_s
        entry["metrics_source"] = "manual"
    if args.iterations is not None:
        entry["iterations"] = args.iterations
    if args.defect_escape is not None:
        entry["defect_escape"] = args.defect_escape.lower() in ("true", "yes", "1")
    if args.rework is not None:
        entry["rework"] = args.rework.lower() in ("true", "yes", "1")
    if args.audit_score is not None:
        entry["audit_score"] = args.audit_score
    if args.model_mix:
        entry["model_mix"] = parse_model_mix(args.model_mix)
    record(entry)
    print(f"recorded {entry['fixture']}/{entry['arm']}/{entry['run_id']}")
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    s = summarize(read_all(), prices=parse_price_map(args.price))
    print(json.dumps(s, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Benchmark harness runner (repo-only).")
    sub = p.add_subparsers(dest="cmd", required=True)
    arms = tuple(sorted(ARM_CLAUDE_MD))

    pr = sub.add_parser("prepare", help="Set up a workspace for one (fixture, arm) run.")
    pr.add_argument("--fixture", required=True)
    pr.add_argument("--arm", required=True, choices=arms)
    pr.add_argument("--dest", required=True)
    pr.set_defaults(func=cmd_prepare)

    sc = sub.add_parser("score", help="Run the held-back suite against a finished workspace.")
    sc.add_argument("--fixture", required=True)
    sc.add_argument("--workspace", required=True)
    sc.add_argument("--timeout", type=int, default=120)
    sc.add_argument("--format", choices=("text", "json"), default="text")
    sc.set_defaults(func=cmd_score)

    rc = sub.add_parser("record", help="Append one run's metrics to the results log.")
    rc.add_argument("--fixture", required=True)
    rc.add_argument("--arm", required=True, choices=arms)
    rc.add_argument("--run-id", dest="run_id", required=True)
    rc.add_argument("--metrics-json", dest="metrics_json",
                    help="path to a transcript_metrics.py output file (automatic capture)")
    rc.add_argument("--tokens", type=int, help="manual fallback; stamps metrics_source=manual")
    rc.add_argument("--wall-time-s", dest="wall_time_s", type=float,
                    help="manual fallback; stamps metrics_source=manual")
    rc.add_argument("--iterations", type=int)
    rc.add_argument("--defect-escape", dest="defect_escape")
    rc.add_argument("--rework", dest="rework")
    rc.add_argument("--audit-score", dest="audit_score", type=float,
                    help="0-1 Auditability score from audit_quiz.py")
    rc.add_argument("--model-mix", dest="model_mix",
                    help="tiers that delivered the run, e.g. tiny:2,medium:1 (arm R)")
    rc.set_defaults(func=cmd_record)

    sm = sub.add_parser("summary", help="Aggregate results per fixture x arm.")
    sm.add_argument("--price", help="relative tier prices, e.g. tiny=0.25,small=1,large=5 "
                                      "(operator-supplied; enables the cost index)")
    sm.set_defaults(func=cmd_summary)

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
