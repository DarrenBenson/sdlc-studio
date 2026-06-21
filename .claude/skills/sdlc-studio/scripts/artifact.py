#!/usr/bin/env python3
"""Deterministic artifact create + close cascade (CR0045).

`new` creates ANY numbered/indexed artifact (epic, story, plan, bug, cr, rfc, test-spec,
workflow) as a structured scaffold AND wires it: allocate a collision-free id, render a
valid file (required sections so it passes validate), append the index data-table row
(built generically from that index's own header), recompute counts, and wire cross-links
(a story into its parent epic's Story Breakdown). `close` terminal-transitions an artifact
and cascades (reusing transition). The agent fills the scaffold's content; the wiring is
deterministic. This replaces the ~10-step hand cascade (the v2.x friction).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import file_finding  # noqa: E402  (reuse _slug, _next_number, append_index_row)
import reconcile  # noqa: E402
import transition  # noqa: E402

# Per-type create status, terminal (close) status, and disp-id form (cr/rfc carry a dash).
SPEC = {
    "epic": {"status": "Draft", "terminal": "Done", "dash": False},
    "story": {"status": "Draft", "terminal": "Done", "dash": False},
    "plan": {"status": "Draft", "terminal": "Complete", "dash": False},
    "test-spec": {"status": "Draft", "terminal": "Complete", "dash": False},
    "workflow": {"status": "Created", "terminal": "Done", "dash": False},
    "bug": {"status": "Open", "terminal": "Fixed", "dash": False},
    "cr": {"status": "Proposed", "terminal": "Complete", "dash": True},
    "rfc": {"status": "Draft", "terminal": "Accepted", "dash": True},
}
_PREFIX_TYPE = {sdlc_md.ARTIFACT_TYPES[t][1].upper(): t for t in SPEC}


def _disp(type_: str, n: int) -> str:
    p = sdlc_md.ARTIFACT_TYPES[type_][1]
    return f"{p}-{n:04d}" if SPEC[type_]["dash"] else f"{p}{n:04d}"


def _render(type_: str, disp: str, title: str, today: str, f: dict) -> str:
    st = SPEC[type_]["status"]
    head = f"# {disp}: {title}\n\n> **Status:** {st}\n> **Created:** {today}\n"
    rev = (f"\n## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
           f"| {today} | {f.get('author', 'sdlc')} | Created via `new` (deterministic) |\n")
    if type_ == "story":
        return (head + f"> **Epic:** {f['epic']}\n\n"
                "## User Story\n\n**As a** {{role}}\n**I want** {{capability}}\n"
                "**So that** {{benefit}}\n\n## Acceptance Criteria\n\n"
                "### AC1: {{define}}\n\n- **Given** {{context}}\n- **When** {{action}}\n"
                "- **Then** {{outcome}}\n- **Verify:** {{executable check}}\n" + rev)
    if type_ == "epic":
        return (head + "\n## Summary\n\n{{what this epic groups}}\n\n"
                "## Story Breakdown\n\n_No stories yet._\n" + rev)
    if type_ == "cr":
        return (head + f"> **Priority:** {f.get('priority', 'Medium')}\n"
                f"> **Type:** {f.get('ctype', 'Feature')}\n\n"
                "## Summary\n\n{{what changes and why}}\n\n"
                "## Acceptance Criteria\n\n- [ ] {{criterion}}\n" + rev)
    if type_ == "rfc":
        return (head + "\n## Summary\n\n{{the unsettled design}}\n\n"
                "## Design Options\n\n- **Option A** {{...}}\n\n"
                "## Recommendation\n\nTBD\n\n## Open Decisions\n\n"
                "| # | Decision | Status |\n| --- | --- | --- |\n| D1 | {{decision}} | Open |\n" + rev)
    if type_ == "bug":
        return (head + f"> **Severity:** {f.get('severity', 'Medium')}\n\n"
                "## Summary\n\n{{symptom}}\n\n## Steps to Reproduce\n\n{{steps}}\n\n"
                "## Proposed Fix\n\n{{fix}}\n" + rev)
    return head + "\n## Overview\n\n{{purpose}}\n" + rev  # plan / test-spec / workflow


def _header_cells(root: Path, type_: str) -> list[str] | None:
    idx = Path(root) / sdlc_md.ARTIFACT_TYPES[type_][0] / "_index.md"
    if not idx.exists():
        return None
    found = None
    for ln in idx.read_text(encoding="utf-8").splitlines():
        cells = reconcile._table_cells(ln)
        if cells and len(cells) > 2 and "id" in [c.lower() for c in cells]:
            found = cells  # last matching header (consistent with append_index_row)
    return found


def _row_from_header(header: list[str], link: str, title: str, status: str, f: dict) -> str:
    """Build a data row matching the index's own columns - generic across types."""
    out = []
    for h in header:
        hl = h.strip().lower()
        if hl == "id":
            out.append(link)
        elif hl in ("title", "description", "feature", "name"):
            out.append(title)
        elif hl == "status":
            out.append(status)
        elif hl == "priority":
            out.append(f.get("priority", "Medium"))
        elif hl == "type":
            out.append(f.get("ctype", "Feature"))
        elif hl == "epic":
            out.append(f.get("epic", "--"))
        elif hl == "severity":
            out.append(f.get("severity", "--"))
        elif hl == "author":
            out.append(f.get("author", "--"))
        elif hl in ("created", "date", "raised", "updated"):
            out.append(f["date"])
        else:
            out.append("--")
    return reconcile._join_row(out)


def _wire_story_to_epic(root: Path, epic_id: str, disp: str, title: str,
                        file_id: str, slug: str) -> bool:
    """Append the story to its parent epic's Story Breakdown (idempotent)."""
    eid = sdlc_md.norm_id(epic_id)  # exact id match - never a substring (EP001 != EP0010)
    files = [p for p in sdlc_md.artifact_files("epic", Path(root))
             if sdlc_md.norm_id(p.stem.split("-")[0]) == eid]
    if not files:
        return False
    ep = files[0]
    text = ep.read_text(encoding="utf-8")
    line = f"- [ ] [{disp}: {title}](../stories/{file_id}-{slug}.md)"
    if disp in text:  # already wired
        return True
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.strip().lower().startswith("## story breakdown"):
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("## "):
                j += 1
            # drop a "_No stories yet._" placeholder if present
            block = [k for k in range(i + 1, j) if lines[k].strip().startswith("_No stories")]
            for k in reversed(block):
                lines.pop(k)
                j -= 1
            lines.insert(j, line)
            ep.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return True
    return False


def new(repo_root: Path | str, type_: str, title: str, fields: dict | None = None) -> dict:
    if type_ not in SPEC:
        raise ValueError(f"unknown type {type_!r} (expected one of {', '.join(SPEC)})")
    root = Path(repo_root)
    f = dict(fields or {})
    f["date"] = f.get("date") or date.today().isoformat()
    if type_ == "story" and not f.get("epic"):
        raise ValueError("a story needs --epic <EPxxxx>")
    n = file_finding._next_number(root, type_)
    prefix = sdlc_md.ARTIFACT_TYPES[type_][1]
    file_id = f"{prefix}{n:04d}"
    disp = _disp(type_, n)
    slug = file_finding._slug(title)
    path = root / sdlc_md.ARTIFACT_TYPES[type_][0] / f"{file_id}-{slug}.md"
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render(type_, disp, title, f["date"], f), encoding="utf-8")
    header = _header_cells(root, type_)
    indexed = False
    if header:
        row = _row_from_header(header, f"[{disp}]({file_id}-{slug}.md)", title,
                               SPEC[type_]["status"], f)
        indexed = file_finding.append_index_row(root, type_, row)
    linked = _wire_story_to_epic(root, f["epic"], disp, title, file_id, slug) \
        if type_ == "story" else None
    return {"id": disp, "file_id": file_id, "path": str(path),
            "indexed": indexed, "epic_linked": linked}


def close(repo_root: Path | str, artifact_id: str, status: str | None = None) -> dict:
    """Terminal-transition an artifact and cascade (reuse transition)."""
    prefix = "".join(c for c in artifact_id if c.isalpha()).upper()
    type_ = _PREFIX_TYPE.get(prefix)
    if type_ is None:
        raise ValueError(f"cannot infer type from id {artifact_id!r}")
    st = status or SPEC[type_]["terminal"]
    return transition.transition(repo_root, artifact_id, st)


def cmd_new(args: argparse.Namespace) -> int:
    f = {k: v for k, v in {"epic": args.epic, "priority": args.priority, "ctype": args.ctype,
                           "severity": args.severity, "author": args.author}.items() if v}
    r = new(args.root, args.type, args.title, f)
    print(json.dumps(r, indent=2) if args.format == "json"
          else f"created {r['id']} -> {r['path']} (indexed={r['indexed']}, epic_linked={r['epic_linked']})")
    return 0


def cmd_close(args: argparse.Namespace) -> int:
    r = close(args.root, args.id, args.status)
    print(json.dumps(r, indent=2) if args.format == "json" else f"closed {args.id}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Deterministic artifact create + close (CR0045).")
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new", help="Create + wire any numbered artifact.")
    n.add_argument("--type", required=True, choices=tuple(SPEC))
    n.add_argument("--title", required=True)
    n.add_argument("--epic", help="parent epic (required for a story)")
    n.add_argument("--priority")
    n.add_argument("--ctype", help="cr type")
    n.add_argument("--severity", help="bug severity")
    n.add_argument("--author")
    n.add_argument("--root", default=".")
    n.add_argument("--format", choices=("text", "json"), default="text")
    n.set_defaults(func=cmd_new)
    c = sub.add_parser("close", help="Terminal-transition an artifact + cascade.")
    c.add_argument("--id", required=True)
    c.add_argument("--status", help="override the per-type terminal status")
    c.add_argument("--root", default=".")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_close)
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
