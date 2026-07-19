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


def _ledger_rows(root: Path) -> list[tuple[datetime, str, str]] | None:
    """Parsed deploy-log rows, or None when no ledger exists (not-applicable)."""
    import re
    log = Path(root) / "sdlc-studio" / _LOG
    if not log.is_file():
        return None
    rows = []
    pat = re.compile(r"^\|\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\s*\|\s*(\S+)\s*\|\s*(.*?)\s*\|\s*$")
    # A corrupt ledger yields no parseable rows, which `metrics` reports as "exists but
    # unparseable" - distinct from the None that means no ledger at all.
    for line in sdlc_md.read_text_safe(log).splitlines():
        m = pat.match(line)
        if m and m.group(2) in _STATUSES:
            rows.append((datetime.strptime(m.group(1), "%Y-%m-%d %H:%M"),
                         m.group(2), m.group(3)))
    return rows


def metrics(root: Path | str) -> dict:
    """The DORA four keys from records the project already keeps. Advisory only -
    no key feeds a gate (a targeted measure stops measuring: the velocity rule).

    Definitions, stated because each is a choice: deployment events = `rolled-out` +
    `verified` rows; change failures = `failed` + `rolled-back` rows over ALL rows;
    lead time = deploy-event time minus author time of each commit landed since the
    previous deploy event (median); MTTR = mean Created -> delivered for High/Critical
    severity bugs. A key whose source is absent is UNMEASURABLE by name, never guessed;
    a workspace with no deploy ledger is not-applicable, never nagged."""
    root = Path(root)
    rows = _ledger_rows(root)
    if rows is None:
        return {"applicable": False,
                "detail": f"no deploy ledger (sdlc-studio/{_LOG}) - not applicable"}
    events = [(when, s) for when, s, _ in rows if s in ("rolled-out", "verified")]
    failures = sum(1 for _, s, _ in rows if s in ("failed", "rolled-back"))
    out: dict = {"applicable": True}
    if events:
        span_days = max(1, (max(w for w, _ in events) - min(w for w, _ in events)).days)
        out["deployment_frequency"] = {
            "events": len(events), "per_week": round(len(events) / (span_days / 7), 2),
            "window": {"from": min(w for w, _ in events).date().isoformat(),
                       "to": max(w for w, _ in events).date().isoformat()},
            "definition": "rolled-out + verified ledger rows"}
    else:
        out["deployment_frequency"] = {"unmeasurable": "no rolled-out/verified rows in the ledger"}
    if rows:
        out["change_failure_rate"] = {
            "rate": round(failures / len(rows), 2),
            "failures": failures, "total_rows": len(rows),
            "definition": "failed + rolled-back rows over all ledger rows"}
    else:
        out["change_failure_rate"] = {"unmeasurable": "ledger exists but no parseable rows"}
    # lead time for changes: commits landed between consecutive deploy events. The
    # measurement lives in flow (deploy NEVER shells out - the module's safety contract);
    # this module only composes the ledger's event times with flow's git read.
    try:
        import flow as _flow
    except ImportError:  # pragma: no cover
        _flow = None
    leads = (_flow.lead_times(root, [w for w, _ in events])
             if (_flow is not None and events) else [])
    git_ok = leads is not None
    leads = leads or []
    if git_ok and leads:
        leads.sort()
        n = len(leads)
        med = leads[n // 2] if n % 2 else (leads[n // 2 - 1] + leads[n // 2]) / 2
        out["lead_time_days"] = {"median": round(med, 2), "commits": n,
                                 "definition": "deploy-event time minus commit author time, "
                                               "commits since the previous deploy event"}
    elif not git_ok:
        out["lead_time_days"] = {"unmeasurable": "no readable git history"}
    elif not events:
        out["lead_time_days"] = {"unmeasurable": "no deploy events to anchor lead time to"}
    else:
        out["lead_time_days"] = {"unmeasurable": "no commits found between deploy events"}
    # MTTR: High/Critical bugs, Created -> delivered
    flow = _flow
    repairs: list[int] = []
    if flow is not None:
        for path, text in sdlc_md.iter_artifact_files("bug", root):
            if text is None:
                continue
            sev = (sdlc_md.extract_field(text, "Severity") or "").strip().lower()
            status = sdlc_md.extract_field(text, "Status") or ""
            if sev not in ("high", "critical") or status not in ("Fixed", "Closed"):
                continue
            created_raw = sdlc_md.extract_field(text, "Created") or sdlc_md.extract_field(text, "Date")
            if not created_raw:
                continue
            try:
                created = datetime.strptime(created_raw.strip()[:10], "%Y-%m-%d").date()
            except ValueError:
                continue
            when, _src = flow.terminal_date(root, path, "bug", status)
            if when is not None:
                repairs.append((when.date() - created).days)
    if repairs:
        out["mttr_days"] = {"mean": round(sum(repairs) / len(repairs), 2), "bugs": len(repairs),
                            "definition": "mean Created -> Fixed/Closed, High/Critical severity"}
    else:
        out["mttr_days"] = {"unmeasurable": "no resolved High/Critical-severity bugs with "
                                            "resolvable dates"}
    return out


def cmd_metrics(args: argparse.Namespace) -> int:
    m = metrics(args.root)
    if getattr(args, "format", "text") == "json":
        print(json.dumps(m, indent=2))
        return 0
    if not m["applicable"]:
        print(f"DORA metrics: not applicable - {m['detail']}")
        return 0
    lines = ["DORA four keys (advisory - no key feeds a gate):"]
    df = m["deployment_frequency"]
    lines.append(f"  deployment frequency: "
                 + (f"{df['per_week']}/week ({df['events']} events, {df['window']['from']}"
                    f"..{df['window']['to']}) [{df['definition']}]"
                    if "events" in df else f"UNMEASURABLE - {df['unmeasurable']}"))
    lt = m["lead_time_days"]
    lines.append(f"  lead time for changes: "
                 + (f"median {lt['median']}d over {lt['commits']} commit(s) [{lt['definition']}]"
                    if "median" in lt else f"UNMEASURABLE - {lt['unmeasurable']}"))
    cf = m["change_failure_rate"]
    lines.append("  change failure rate: "
                 + (f"{cf['rate']} ({cf['failures']} of {cf['total_rows']} rows) "
                    f"[{cf['definition']}]"
                    if "rate" in cf else f"UNMEASURABLE - {cf['unmeasurable']}"))
    mt = m["mttr_days"]
    lines.append(f"  MTTR: "
                 + (f"mean {mt['mean']}d over {mt['bugs']} bug(s) [{mt['definition']}]"
                    if "mean" in mt else f"UNMEASURABLE - {mt['unmeasurable']}"))
    print("\n".join(lines))
    return 0


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
    p = argparse.ArgumentParser(description="Orchestrate-only deploy last-mile.")
    sub = p.add_subparsers(dest="cmd", required=True)
    pf = sub.add_parser("preflight",
                        help="gate + readiness verdict + operator hand-off (no deploy)")
    pf.add_argument("--format", choices=("text", "json"), default="text")
    pf.add_argument("--root", default=".", help="Repo root (default: .)")
    pf.set_defaults(func=cmd_preflight)
    met = sub.add_parser("metrics", help="the DORA four keys from the deploy ledger + git + "
                                         "bug dates (advisory; not-applicable without a ledger)")
    met.add_argument("--format", choices=("text", "json"), default="text")
    met.add_argument("--root", default=".", help="Repo root (default: .)")
    met.set_defaults(func=cmd_metrics)

    rec = sub.add_parser("record", help="append a deploy outcome to the deploy log")
    rec.add_argument("--status", required=True, choices=_STATUSES)
    rec.add_argument("--detail", default="")
    rec.add_argument("--root", default=".", help="Repo root (default: .)")
    rec.set_defaults(func=cmd_record)
    sdlc_md.add_global_root(p)  # --root valid before OR after the subcommand
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
