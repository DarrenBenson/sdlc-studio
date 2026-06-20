#!/usr/bin/env python3
"""SDLC Studio autosprint - batch selection and ordering (RFC0001 WS2).

`autosprint plan` selects a batch of work by query (open bugs, proposed CRs, ready
stories) and orders it, so the operator sees the triage plan before the run starts.
Ordering is by priority/severity (Critical first); dependency-topological and WSJF
(priority over RFC0009 complexity) are layered later - `--order wsjf` currently
falls back to priority until the complexity signal exists. Read-only; pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

PRIORITY_FIELD = {"bug": "Severity", "cr": "Priority", "story": "Priority"}
PRIORITY_WEIGHT = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def select_batch(repo_root: Path | str, kind: str, status: str, order: str = "priority") -> list[dict]:
    """Files of `kind` whose Status matches, with priority, ordered."""
    root = Path(repo_root)
    vocab = sdlc_md.STATUS_VOCAB.get(kind, [])
    out: list[dict] = []
    for path in sdlc_md.artifact_files(kind, root):
        text = path.read_text(encoding="utf-8")
        st = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab) or "Unknown"
        if st != status:
            continue
        pri = sdlc_md.extract_field(text, PRIORITY_FIELD.get(kind, "Priority")) or "Medium"
        rid = sdlc_md.extract_record_id(path.stem) or path.stem
        out.append({"id": rid, "type": kind, "status": st, "priority": pri, "path": str(path)})
    if order in ("priority", "wsjf"):  # wsjf falls back to priority until RFC0009 ships complexity
        out.sort(key=lambda b: (PRIORITY_WEIGHT.get(b["priority"], 2), b["id"]))
    return out


def build_plan(repo_root: Path | str, kind: str, status: str, order: str = "priority") -> dict:
    """The triage plan: the ordered batch plus a count."""
    batch = select_batch(repo_root, kind, status, order)
    return {
        "generated_at": sdlc_md.now_iso8601(),
        "kind": kind,
        "status": status,
        "order": order,
        "batch": batch,
        "count": len(batch),
    }


def cmd_plan(args: argparse.Namespace) -> int:
    """Print the ordered batch the operator approves before a run."""
    if args.bugs is not None:
        kind, status = "bug", args.bugs
    elif args.crs is not None:
        kind, status = "cr", args.crs
    elif args.stories is not None:
        kind, status = "story", args.stories
    else:  # pragma: no cover - argparse marks the group required
        print("specify one of --bugs/--crs/--stories <STATUS>", file=sys.stderr)
        return 2
    data = build_plan(args.root, kind, status, args.order)
    if args.format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"batch: {data['count']} {kind}(s) with Status {status}, order={args.order}")
        for b in data["batch"]:
            print(f"  {b['id']} [{b['priority']}]")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio autosprint batch selection.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan", help="Select and order a batch of work (the triage plan).")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--bugs", metavar="STATUS", help="Bugs with this Status (e.g. Open)")
    g.add_argument("--crs", metavar="STATUS", help="CRs with this Status (e.g. Proposed)")
    g.add_argument("--stories", metavar="STATUS", help="Stories with this Status (e.g. Ready)")
    p.add_argument("--order", choices=("priority", "wsjf", "manual"), default="priority")
    p.add_argument("--root", default=".", help="Repo root (default: .)")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.set_defaults(func=cmd_plan)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
