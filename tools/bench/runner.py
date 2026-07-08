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

ARM_CLAUDE_MD = {"A": ARMS_DIR / "pipeline_CLAUDE.md", "B": ARMS_DIR / "baseline_CLAUDE.md"}


def list_fixtures(fixtures_dir: Path = FIXTURES_DIR) -> list[str]:
    """Fixture names, sorted, i.e. directories with both a visible/ and hidden/ subdir."""
    if not fixtures_dir.is_dir():
        return []
    return sorted(p.name for p in fixtures_dir.iterdir()
                  if p.is_dir() and (p / "visible").is_dir() and (p / "hidden").is_dir())


def prepare_workspace(fixture: str, arm: str, dest: Path,
                       fixtures_dir: Path = FIXTURES_DIR) -> Path:
    """Copy the fixture's visible/ files plus the arm's CLAUDE.md into `dest`. Never touches
    the fixture's hidden/ suite - that is the whole point of "held-back"."""
    if arm not in ARM_CLAUDE_MD:
        raise ValueError(f"unknown arm {arm!r} - expected 'A' or 'B'")
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
    return dest


def score(fixture: str, workspace: Path, fixtures_dir: Path = FIXTURES_DIR,
          timeout: int = 60) -> dict:
    """Run the fixture's held-back suite against `workspace`. Returns {"passed": bool,
    "defect_escape": bool, "output": str}. `defect_escape` is the inverse of `passed` - named
    per the protocol's metric, so callers don't have to remember to invert it."""
    hidden = fixtures_dir / fixture / "hidden"
    if not hidden.is_dir():
        raise ValueError(f"unknown fixture {fixture!r} (no hidden/ dir under {fixtures_dir})")
    with tempfile.TemporaryDirectory() as scoring_dir:
        scoring_dir = Path(scoring_dir)
        for item in hidden.iterdir():
            shutil.copy2(item, scoring_dir / item.name)
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(scoring_dir), "--workspace", str(workspace), "-q"],
            capture_output=True, text=True, timeout=timeout,
        )
        passed = result.returncode == 0
        return {"passed": passed, "defect_escape": not passed,
                "output": (result.stdout + result.stderr)[-4000:]}


def record(entry: dict, results_path: Path = RESULTS_PATH) -> dict:
    """Append one run's metrics. Required keys: fixture, arm, run_id. Optional: tokens,
    wall_time_s, iterations, defect_escape, rework. Unknown extra keys are kept as-is -
    this is a benchmark log, not a fixed schema like the skill's own telemetry.py."""
    for k in ("fixture", "arm", "run_id"):
        if k not in entry:
            raise ValueError(f"record: missing required key {k!r}")
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with results_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    return entry


def read_all(results_path: Path = RESULTS_PATH) -> list[dict]:
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


def summarize(entries: list[dict]) -> dict:
    """Per (fixture, arm) aggregates: n, defect_escape_rate, rework_rate, mean tokens,
    mean wall_time_s. A field absent from every entry in a group is None, not a fabricated 0."""
    groups: dict[tuple, list[dict]] = {}
    for e in entries:
        groups.setdefault((e.get("fixture"), e.get("arm")), []).append(e)
    out = {}
    for (fixture, arm), rows in sorted(groups.items()):
        tokens = [r["tokens"] for r in rows if isinstance(r.get("tokens"), (int, float))]
        wall = [r["wall_time_s"] for r in rows if isinstance(r.get("wall_time_s"), (int, float))]
        escapes = [r["defect_escape"] for r in rows if r.get("defect_escape") is not None]
        rework = [r["rework"] for r in rows if r.get("rework") is not None]
        out[f"{fixture}::{arm}"] = {
            "n": len(rows),
            "mean_tokens": _mean(tokens),
            "mean_wall_time_s": _mean(wall),
            "defect_escape_rate": _mean([1 if v else 0 for v in escapes]),
            "rework_rate": _mean([1 if v else 0 for v in rework]),
        }
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
    if args.tokens is not None:
        entry["tokens"] = args.tokens
    if args.wall_time_s is not None:
        entry["wall_time_s"] = args.wall_time_s
    if args.iterations is not None:
        entry["iterations"] = args.iterations
    if args.defect_escape is not None:
        entry["defect_escape"] = args.defect_escape.lower() in ("true", "yes", "1")
    if args.rework is not None:
        entry["rework"] = args.rework.lower() in ("true", "yes", "1")
    record(entry)
    print(f"recorded {entry['fixture']}/{entry['arm']}/{entry['run_id']}")
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    s = summarize(read_all())
    print(json.dumps(s, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Benchmark harness runner (repo-only).")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("prepare", help="Set up a workspace for one (fixture, arm) run.")
    pr.add_argument("--fixture", required=True)
    pr.add_argument("--arm", required=True, choices=("A", "B"))
    pr.add_argument("--dest", required=True)
    pr.set_defaults(func=cmd_prepare)

    sc = sub.add_parser("score", help="Run the held-back suite against a finished workspace.")
    sc.add_argument("--fixture", required=True)
    sc.add_argument("--workspace", required=True)
    sc.add_argument("--timeout", type=int, default=60)
    sc.add_argument("--format", choices=("text", "json"), default="text")
    sc.set_defaults(func=cmd_score)

    rc = sub.add_parser("record", help="Append one run's metrics to the results log.")
    rc.add_argument("--fixture", required=True)
    rc.add_argument("--arm", required=True, choices=("A", "B"))
    rc.add_argument("--run-id", dest="run_id", required=True)
    rc.add_argument("--tokens", type=int)
    rc.add_argument("--wall-time-s", dest="wall_time_s", type=float)
    rc.add_argument("--iterations", type=int)
    rc.add_argument("--defect-escape", dest="defect_escape")
    rc.add_argument("--rework", dest="rework")
    rc.set_defaults(func=cmd_record)

    sm = sub.add_parser("summary", help="Aggregate results per fixture x arm.")
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
