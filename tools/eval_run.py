#!/usr/bin/env python3
"""Deterministic spine of the two-Claude eval gate.

The eval gate (release-gate template, rc checklist, epic close) runs each scenario as a
fresh WORKER session graded by an independent GRADER - both irreducibly judgement. What
was manual ceremony around them is now deterministic:

    setup   build a scenario's fixture repo from its machine-readable `fixture` spec
            and print the worker prompt (a scenario without a spec degrades honestly:
            it prints the prose setup and exits 1 so the gap is visible)
    record  append one graded behaviour verdict (pass/fail + evidence) for a run
    report  summarise a run: exit 1 if any BLOCKING behaviour failed, else 0

Results land in evals/.results/<run>.json (repo-only, like evals/ itself).

Usage:
    python3 tools/eval_run.py setup  --scenario 05-schema-v3-identity --dir /tmp/fx
    python3 tools/eval_run.py record --scenario 05-schema-v3-identity --run 2026-07-10 \\
        --behaviour EB1 --verdict pass --evidence "id BG-01KX58PH minted"
    python3 tools/eval_run.py report --run 2026-07-10
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCENARIOS = REPO / "evals" / "scenarios"
RESULTS = REPO / "evals" / ".results"


def load_scenario(sid: str) -> dict:
    path = SCENARIOS / f"{sid}.json"
    if not path.exists():
        raise FileNotFoundError(f"no scenario {sid} under {SCENARIOS}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_fixture(scenario: dict, dest: Path) -> list[str]:
    """Materialise the scenario's `fixture` spec: {"files": {relpath: content}}. Returns
    the created paths. Raises KeyError when the scenario has no machine-readable spec."""
    spec = scenario["fixture"]
    created = []
    for rel, content in spec.get("files", {}).items():
        p = dest / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        created.append(rel)
    return created


def cmd_setup(args: argparse.Namespace) -> int:
    sc = load_scenario(args.scenario)
    dest = Path(args.dir)
    if "fixture" not in sc:
        print(f"{args.scenario}: no machine-readable fixture spec - follow the prose setup "
              f"by hand, then file a fixture spec so the next run is deterministic:\n"
              f"  {sc.get('setup', '(no setup text)')}", file=sys.stderr)
        return 1
    created = build_fixture(sc, dest)
    print(f"fixture: {len(created)} file(s) under {dest}")
    print("\n--- WORKER PROMPT (fresh session, skill installed) ---")
    print(f"Fixture root: {dest}")
    print(sc["prompt"])
    print("\n--- GRADE AGAINST (behaviour: severity) ---")
    for eb in sc.get("expected_behaviours", []):
        print(f"  {eb['id']} ({eb['severity']}): {eb['description']}")
    for fb in sc.get("forbidden_behaviours", []):
        print(f"  FORBIDDEN: {fb}")
    return 0


def _run_path(run: str) -> Path:
    return RESULTS / f"{run}.json"


def cmd_record(args: argparse.Namespace) -> int:
    sc = load_scenario(args.scenario)  # validates the scenario id
    known = {eb["id"]: eb["severity"] for eb in sc.get("expected_behaviours", [])}
    if args.behaviour not in known:
        print(f"error: {args.scenario} has no behaviour {args.behaviour} "
              f"(known: {', '.join(known)})", file=sys.stderr)
        return 2
    RESULTS.mkdir(parents=True, exist_ok=True)
    path = _run_path(args.run)
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    data.setdefault(args.scenario, {})[args.behaviour] = {
        "verdict": args.verdict, "severity": known[args.behaviour],
        "evidence": args.evidence}
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"recorded {args.scenario}/{args.behaviour} = {args.verdict}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    path = _run_path(args.run)
    if not path.exists():
        print(f"error: no results for run {args.run} under {RESULTS}", file=sys.stderr)
        return 2
    data = json.loads(path.read_text(encoding="utf-8"))
    blocking_failed = 0
    for sid, behaviours in sorted(data.items()):
        sc = load_scenario(sid)
        expected = {eb["id"] for eb in sc.get("expected_behaviours", [])}
        missing = sorted(expected - set(behaviours))
        for bid, r in sorted(behaviours.items()):
            mark = "PASS" if r["verdict"] == "pass" else "FAIL"
            if mark == "FAIL" and r["severity"] == "blocking":
                blocking_failed += 1
            print(f"{sid} {bid} [{r['severity']}]: {mark} - {r['evidence']}")
        for bid in missing:  # an ungraded blocking behaviour cannot pass the gate
            sev = next(eb["severity"] for eb in sc["expected_behaviours"] if eb["id"] == bid)
            print(f"{sid} {bid} [{sev}]: UNGRADED")
            if sev == "blocking":
                blocking_failed += 1
    print(f"report: {'GATE FAIL' if blocking_failed else 'gate pass'} "
          f"({blocking_failed} blocking failure(s)/ungraded)")
    return 1 if blocking_failed else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Deterministic spine of the two-Claude eval gate.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("setup", help="Build a scenario fixture + print the worker prompt.")
    s.add_argument("--scenario", required=True)
    s.add_argument("--dir", required=True, help="Fixture root to create (a scratch dir)")
    s.set_defaults(func=cmd_setup)
    r = sub.add_parser("record", help="Record one graded behaviour verdict for a run.")
    r.add_argument("--scenario", required=True)
    r.add_argument("--run", required=True, help="Run label (e.g. the date)")
    r.add_argument("--behaviour", required=True, help="e.g. EB1")
    r.add_argument("--verdict", required=True, choices=("pass", "fail"))
    r.add_argument("--evidence", required=True, help="One line of evidence for the grade")
    r.set_defaults(func=cmd_record)
    g = sub.add_parser("report", help="Summarise a run; exit 1 on any blocking failure.")
    g.add_argument("--run", required=True)
    g.set_defaults(func=cmd_report)
    args = p.parse_args(argv)
    try:
        return args.func(args)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
