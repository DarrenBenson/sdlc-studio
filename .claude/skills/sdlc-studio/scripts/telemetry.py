#!/usr/bin/env python3
"""Run telemetry recorder (CR0050, RFC0014 WS1).

Append a per-unit run outcome to the gitignored `sdlc-studio/.local/telemetry.jsonl` so estimation and
the complexity/churn calibration can become continuous (RFC0009 WS5) instead of one-off.
**Local-only, no upload, no network.** Tokens are recorded only when the caller passes them
(a script cannot read them reliably). The loop wires `record` on each unit close (CR0051).

Subcommands:
  record   Append one run-outcome record.
  show     Print the recorded records (count + the JSON).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# The project's gitignored state dir (sdlc-studio/.local/), not repo-root .local/.
LOCAL = Path("sdlc-studio") / ".local" / "telemetry.jsonl"
# The captured fields (RFC0014 D1). Optional ones are omitted when not supplied.
FIELDS = ("id", "type", "iterations", "wall_time_s", "stages", "critic_verdict",
          "complexity", "churn", "reopened", "tokens")


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
              "churn": _int(args.churn), "reopened": args.reopened, "tokens": _int(args.tokens)}
    rec = record(args.root, fields)
    print(json.dumps(rec) if args.format == "json" else f"recorded {rec.get('id', '?')}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    recs = read_all(args.root)
    print(json.dumps(recs, indent=2) if args.format == "json" else f"{len(recs)} record(s)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run telemetry recorder (CR0050).")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record", help="Append one run-outcome record.")
    r.add_argument("--id"); r.add_argument("--type"); r.add_argument("--iterations")
    r.add_argument("--wall-time-s", dest="wall_time_s"); r.add_argument("--stages")
    r.add_argument("--verdict"); r.add_argument("--complexity"); r.add_argument("--churn")
    r.add_argument("--reopened"); r.add_argument("--tokens")
    r.add_argument("--root", default="."); r.add_argument("--format", choices=("text", "json"), default="text")
    r.set_defaults(func=cmd_record)
    s = sub.add_parser("show", help="Print recorded records.")
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
