#!/usr/bin/env python3
"""SDLC Studio RFC decision-readiness digest.

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
        cells = sdlc_md.table_cells(line)  # escaped-pipe-aware
        if cells is None:
            continue  # separator
        rows.append(cells)
    return rows[1:] if rows else []  # drop the header row


def digest(repo_root: Path | str, decidable_only: bool = True) -> dict:
    """Per-RFC decision-readiness over the workspace."""
    root = Path(repo_root)
    vocab = sdlc_md.status_vocab("rfc", root)
    rfcs: list[dict] = []
    for path in sdlc_md.artifact_files("rfc", root):
        text = path.read_text(encoding="utf-8")
        status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab) or "Unknown"
        if decidable_only and status not in DECIDABLE:
            continue
        rid = sdlc_md.extract_record_id(path.stem) or path.stem
        decision_rows = _table_data_rows(_section(text, "Open Decisions"))
        open_count = sum(1 for r in decision_rows if any(c == "Open" for c in r))
        # Workstreams = the RFC's REAL children (the Decomposed-into/Parent links the
        # derivation gate and reconcile already use - one authority, LL0016), falling
        # back to a Workstream/Phased Plan table only when no children are linked yet.
        children = sdlc_md.children_of(root, sdlc_md.norm_id(rid))
        workstreams = len(children) or len(
            _table_data_rows(_section(text, "Workstream")) or
            _table_data_rows(_section(text, "Phased Plan")))
        rec = "\n".join(_section(text, "Recommendation")).strip()
        has_rec = bool(rec) and rec.upper() != "TBD"
        # Decided-awaiting-delivery (every decision row resolved) must never read
        # READY-for-decision: the digest would invite re-deciding settled questions.
        decided = bool(decision_rows) and open_count == 0
        ready = status in DECIDABLE and has_rec and open_count == 0 and not decided
        rfcs.append({
            "id": rid,
            "title": sdlc_md.extract_h1_title(text) or rid,
            "status": status,
            "open_decisions": len(decision_rows),
            "open_count": open_count,
            "workstreams": workstreams,
            "has_recommendation": has_rec,
            "decided": decided,
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
            if r["ready_for_decision"]:
                flag, note = "READY", ""
            elif r.get("decided"):
                flag = "DECIDED"
                note = " (awaiting delivery of its workstreams)"
            else:
                flag = "    -"
                note = (f" ({r['open_count']} open decision(s))" if r["open_count"]
                        else " (no recommendation)")
            print(f"  {flag} {r['id']} [{r['status']}] ws={r['workstreams']}{note}")
    return 0


def resolve(repo_root: Path | str, rfc_id: str, decision: str, resolution: str,
            refs: list[str] | None = None) -> Path:
    """Mark ONE decision row Resolved with the operator's text (+ spawned-CR refs) and
    append a revision row. The judgement is the operator's; only the table surgery is
    tool-carried - every other row stays byte-identical. Refuses an unknown RFC or
    decision id loudly, before any write."""
    root = Path(repo_root)
    found = sdlc_md.find_by_id(root, rfc_id)
    if not found or found[1] != "rfc":
        raise ValueError(f"no RFC with id {rfc_id!r}")
    path = found[0]
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    target = decision.strip()
    # scope the search to the Open Decisions SECTION: a body table elsewhere whose
    # first cell happens to be "D2" must never be edited (the critic's live probe)
    start = end = None
    for i, line in enumerate(lines):
        if line.startswith("## "):
            if start is not None:
                end = i
                break
            if "open decisions" in line.lower():
                start = i
    if start is None:
        raise ValueError(f"{rfc_id} has no '## Open Decisions' section")
    end = end if end is not None else len(lines)
    hit = None
    for i in range(start, end):
        cells = sdlc_md.table_cells(lines[i])
        if cells and cells[0] == target and len(cells) >= 3:
            hit = i
            break
    if hit is None:
        raise ValueError(f"{rfc_id} has no decision row {target!r} in its Open Decisions "
                         f"table - nothing was changed")
    cells = sdlc_md.table_cells(lines[hit])
    status = f"Resolved: {resolution.strip()}"
    if refs:
        status += " -> " + ", ".join(sdlc_md.norm_id(r) for r in refs)
    cells[-1] = status
    lines[hit] = sdlc_md.join_row(cells) + "\n"
    new_text = "".join(lines)
    row = (f"| {sdlc_md.now_date()} | rfc resolve (operator decision) | "
           f"resolve: {target} - {resolution.strip().replace('|', '/')} |\n")
    if "## Revision History" not in new_text:
        new_text = (new_text.rstrip("\n")
                    + "\n\n## Revision History\n\n| Date | Author | Change |\n"
                      "| --- | --- | --- |\n" + row)
    else:
        # insert after the LAST row of the Revision History table (the section may
        # not be the file's final section - appending at EOF would strand the row)
        out = new_text.splitlines(keepends=True)
        sec = next(i for i, ln in enumerate(out)
                   if ln.startswith("## ") and "revision history" in ln.lower())
        j = sec + 1
        last_row = None
        while j < len(out) and not out[j].startswith("## "):
            if out[j].lstrip().startswith("|"):
                last_row = j
            j += 1
        insert_at = (last_row + 1) if last_row is not None else j
        out.insert(insert_at, row)
        new_text = "".join(out)
    sdlc_md.atomic_write(path, new_text)
    return path


def cmd_resolve(args: argparse.Namespace) -> int:
    try:
        path = resolve(args.root, args.rfc, args.decision, args.resolution,
                       refs=[r.strip() for r in (args.refs or "").split(",") if r.strip()])
    except ValueError as exc:
        print(f"resolve refused: {exc}", file=sys.stderr)
        return 2
    print(f"resolved {args.decision} on {args.rfc} -> {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio RFC decision-readiness digest.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("decide", help="Digest Draft/In-Review RFCs for a decision session.")
    d.add_argument("--all", action="store_true", help="Include non-decidable (terminal) RFCs too")
    d.add_argument("--root", default=".", help="Repo root (default: .)")
    d.add_argument("--format", choices=("text", "json"), default="text")
    d.set_defaults(func=cmd_decide)
    r = sub.add_parser("resolve", help="Mark one decision row Resolved with the operator's "
                                       "text (+ spawned-CR refs); other rows byte-identical.")
    r.add_argument("--rfc", required=True)
    r.add_argument("--decision", required=True, metavar="D2")
    r.add_argument("--resolution", required=True, help="the operator's decision, one line")
    r.add_argument("--refs", help="comma-separated spawned workstream ids")
    r.add_argument("--root", default=".", help="Repo root (default: .)")
    r.set_defaults(func=cmd_resolve)
    sdlc_md.add_global_root(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
