#!/usr/bin/env python3
"""The orchestrate-only deploy last-mile.

The skill GATES before a deploy and helps VERIFY + RECORD after it. It never holds the production
trigger, never auto-rolls-back, and never deploys inside the autonomous loop - the *act* of
deploying is the operator's, run out-of-band with the project's own command. This helper provides
the deterministic, read-only pieces:

  preflight  - read deploy config, run the pre-deploy gate, and emit a readiness verdict plus the
               operator hand-off (the deploy command to run, the rollback procedure to keep ready).
               Never executes the deploy.
  record     - append the deploy outcome (rolled-out / verified / rolled-back / failed) to the
               project's deploy log, so the last mile is closed back into the artifact graph.

Ecosystem-neutral: the project supplies `deploy.command` / `deploy.smoke` / `deploy.rollback` in
`.config.yaml`; this script assumes no CI, cloud, or registry. Secrets are never read.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import gate  # noqa: E402

_LOG = "deploy-log.md"
_STATUSES = ("rolled-out", "verified", "rolled-back", "failed")


def deploy_config(root: Path | str) -> dict:
    """The project's `deploy.*` settings, all optional with safe defaults."""
    return {
        "command": sdlc_md.project_override(root, "deploy.command", "") or "",
        "smoke": sdlc_md.project_override(root, "deploy.smoke", "") or "",
        "soak_minutes": sdlc_md.project_override(root, "deploy.soak_minutes", 0) or 0,
        "rollback": sdlc_md.project_override(root, "deploy.rollback", "") or "",
    }


def preflight(root: Path | str = ".") -> dict:
    """Read-only readiness check: the pre-deploy gate must be green before a deploy. Returns the
    verdict + the operator hand-off. NEVER executes the deploy command."""
    cfg = deploy_config(root)
    report = gate.run_gate(str(root))
    gate_ok = report.get("ok", False)
    fails = [c for c in report.get("checks", []) if c.get("blocking") and c.get("status") != "pass"]
    handoff = []
    if cfg["command"]:
        handoff.append(f"operator runs the deploy: {cfg['command']}")
    else:
        handoff.append("no deploy.command configured - trigger your own deploy out-of-band")
    if cfg["smoke"]:
        handoff.append(f"then verify smoke: {cfg['smoke']} (green == rolled out)")
    if cfg["soak_minutes"]:
        handoff.append(f"soak {cfg['soak_minutes']} min before marking verified")
    handoff.append("keep rollback ready: " + (cfg["rollback"] or "no deploy.rollback documented"))
    return {
        "ready": bool(gate_ok),
        "gate_ok": gate_ok,
        "gate_fails": [{"check": c["check"], "detail": c["detail"]} for c in fails],
        "config": cfg,
        "handoff": handoff,
        # the skill orchestrates; it never runs the deploy or the rollback itself
        "executes": False,
    }


def record(root: Path | str, status: str, detail: str = "",
           now: datetime | None = None) -> str:
    """Append a deploy outcome to `sdlc-studio/<deploy-log>`. Returns the row written."""
    if status not in _STATUSES:
        raise ValueError(f"status must be one of {_STATUSES}, got {status!r}")
    sd = Path(root) / "sdlc-studio"
    sd.mkdir(parents=True, exist_ok=True)
    log = sd / _LOG
    stamp = (now or datetime.now()).strftime("%Y-%m-%d %H:%M")
    safe = detail.replace("|", "/").replace("\n", " ").strip()
    row = f"| {stamp} | {status} | {safe} |"
    if not log.exists():
        log.write_text("# Deploy Log\n\nAppend-only record of deploy outcomes.\n\n"
                       "| When | Status | Detail |\n| --- | --- | --- |\n", encoding="utf-8")
    with log.open("a", encoding="utf-8") as fh:
        fh.write(row + "\n")
    return row


def cmd_preflight(args: argparse.Namespace) -> int:
    r = preflight(args.root)
    if args.format == "json":
        print(json.dumps(r, indent=2))
    else:
        print("deploy preflight: " + ("READY (gate green)" if r["ready"]
                                       else "NOT READY - gate is not green"))
        for f in r["gate_fails"]:
            print(f"  [gate] {f['check']}: {f['detail']}")
        print("hand-off (operator-triggered - the skill does not deploy):")
        for h in r["handoff"]:
            print(f"  - {h}")
    return 0 if r["ready"] else 1


def cmd_record(args: argparse.Namespace) -> int:
    try:
        row = record(args.root, args.status, args.detail or "")
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"recorded: {row}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parent = argparse.ArgumentParser(add_help=False)  # --root works before OR after the subcommand
    parent.add_argument("--root", default=".")
    p = argparse.ArgumentParser(description="Orchestrate-only deploy last-mile.",
                               parents=[parent])
    sub = p.add_subparsers(dest="cmd", required=True)
    pf = sub.add_parser("preflight", parents=[parent],
                        help="gate + readiness verdict + operator hand-off (no deploy)")
    pf.add_argument("--format", choices=("text", "json"), default="text")
    pf.set_defaults(func=cmd_preflight)
    rec = sub.add_parser("record", parents=[parent], help="append a deploy outcome to the deploy log")
    rec.add_argument("--status", required=True, choices=_STATUSES)
    rec.add_argument("--detail", default="")
    rec.set_defaults(func=cmd_record)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
