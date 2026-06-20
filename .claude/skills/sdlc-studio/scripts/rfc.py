#!/usr/bin/env python3
"""SDLC Studio RFC decision-readiness digest (CR0024).

`rfc decide` is the multi-RFC decision session: triage the Draft backlog into
per-RFC briefs, then accept / defer / withdraw across them. This script is the
deterministic input - per Draft RFC it reports the open-decision count (total +
still-Open), the workstream count, whether a recommendation is present, and a
`ready_for_decision` flag - so the session starts from data, not a re-read of every
RFC. Read-only; pure stdlib. The adversarial judgement stays model-instructed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

DECIDABLE = {"Draft", "In Review"}


def _section(text: str, title_substr: str) -> list[str]:
    """Lines of the first `## ` section whose heading contains `title_substr`."""
    out: list[str] = []
    capturing = False
    for line in text.splitlines():
        if line.startswith("## "):
            if capturing:
                break
            capturing = title_substr.lower() in line.lower()
            continue
        if capturing:
            out.append(line)
    return out


def _table_data_rows(lines: list[str]) -> list[list[str]]:
    """Data rows (cells) of the first markdown table in `lines` - header + separator dropped."""
    rows: list[list[str]] = []
    for line in lines:
        if not line.strip().startswith("|"):
            if rows:
                break  # table ended (a non-table line)
            continue
        cells = sdlc_md.table_cells(line)  # escaped-pipe-aware (BG0021)
        if cells is None:
            continue  # separator
        rows.append(cells)
    return rows[1:] if rows else []  # drop the header row


def digest(repo_root: Path | str, decidable_only: bool = True) -> dict:
    """Per-RFC decision-readiness over the workspace."""
    root = Path(repo_root)
    vocab = sdlc_md.STATUS_VOCAB.get("rfc", [])
    rfcs: list[dict] = []
    for path in sdlc_md.artifact_files("rfc", root):
        text = path.read_text(encoding="utf-8")
        status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab) or "Unknown"
        if decidable_only and status not in DECIDABLE:
            continue
        rid = sdlc_md.extract_record_id(path.stem) or path.stem
        decision_rows = _table_data_rows(_section(text, "Open Decisions"))
        open_count = sum(1 for r in decision_rows if any(c == "Open" for c in r))
        workstreams = len(_table_data_rows(_section(text, "Workstream")) or
                          _table_data_rows(_section(text, "Phased Plan")))
        rec = "\n".join(_section(text, "Recommendation")).strip()
        has_rec = bool(rec) and rec.upper() != "TBD"
        ready = status in DECIDABLE and has_rec and open_count == 0
        rfcs.append({
            "id": rid,
            "title": sdlc_md.extract_h1_title(text) or rid,
            "status": status,
            "open_decisions": len(decision_rows),
            "open_count": open_count,
            "workstreams": workstreams,
            "has_recommendation": has_rec,
            "ready_for_decision": ready,
        })
    rfcs.sort(key=lambda r: r["id"])
    ready = sum(1 for r in rfcs if r["ready_for_decision"])
    return {
        "generated_at": sdlc_md.now_iso8601(),
        "rfcs": rfcs,
        "summary": {"total": len(rfcs), "ready": ready, "not_ready": len(rfcs) - ready},
    }


def cmd_decide(args: argparse.Namespace) -> int:
    """Print the RFC decision-readiness digest for the session."""
    data = digest(args.root, decidable_only=not args.all)
    if args.format == "json":
        print(json.dumps(data, indent=2))
    else:
        s = data["summary"]
        print(f"rfc decide: {s['ready']}/{s['total']} ready for decision")
        for r in data["rfcs"]:
            flag = "READY" if r["ready_for_decision"] else "    -"
            note = "" if r["ready_for_decision"] else (
                f" ({r['open_count']} open decision(s))" if r["open_count"]
                else " (no recommendation)")
            print(f"  {flag} {r['id']} [{r['status']}] ws={r['workstreams']}{note}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio RFC decision-readiness digest.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("decide", help="Digest Draft/In-Review RFCs for a decision session.")
    d.add_argument("--all", action="store_true", help="Include non-decidable (terminal) RFCs too")
    d.add_argument("--root", default=".", help="Repo root (default: .)")
    d.add_argument("--format", choices=("text", "json"), default="text")
    d.set_defaults(func=cmd_decide)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
