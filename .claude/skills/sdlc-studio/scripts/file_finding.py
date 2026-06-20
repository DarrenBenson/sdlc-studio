#!/usr/bin/env python3
"""SDLC Studio deterministic finding filer (RFC0002 WS3).

Files a Bug / CR / RFC from an audit (or any) finding: allocate a collision-free ID,
render a STRUCTURED artifact (required sections enforced, so it cannot emit a hollow
stub - the 2nd audit run's lesson), write it, append the index row, and recompute the
index summary counts (reusing reconcile's tested count pass). Deterministic given the
inputs; the caller supplies the rich content.

Subcommands:
  file     Create one artifact (--type bug|cr|rfc) from --title + fields.
  rebuild  Recompute a type's index summary counts from its rows (delegates to reconcile).

Read-only over everything except the new artifact file and its index. Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import next_id  # noqa: E402  (sibling)
import reconcile  # noqa: E402  (sibling - reuse the tested count recompute)

# Per-type: workspace dir, filename prefix, index display-id form, default status, and
# the fields a non-hollow artifact must carry (the richness guard).
TYPES = {
    "bug": {"dir": "bugs", "prefix": "BG", "disp": "BG{n:04d}",
            "status": "Open", "required": ("severity", "summary", "steps", "fix")},
    "cr": {"dir": "change-requests", "prefix": "CR", "disp": "CR-{n:04d}",
           "status": "Proposed", "required": ("priority", "ctype", "summary", "acs")},
    "rfc": {"dir": "rfcs", "prefix": "RFC", "disp": "RFC-{n:04d}",
            "status": "Draft", "required": ("summary", "options")},
}


def _slug(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return "-".join(s.split("-")[:8]) or "untitled"


def _next_number(repo_root: Path, type_: str) -> int:
    used = next_id.local_ids(type_, repo_root)
    return (max(used) + 1) if used else 1


def _render(type_: str, disp_id: str, title: str, today: str, f: dict) -> str:
    """A structured artifact body (required sections populated)."""
    if type_ == "bug":
        return (f"# {disp_id}: {title}\n\n"
                f"> **Status:** Open\n> **Severity:** {f['severity']}\n"
                f"> **Created:** {today}\n\n"
                f"## Summary\n\n{f['summary']}\n\n"
                f"## Steps to Reproduce\n\n{f['steps']}\n\n"
                f"## Proposed Fix\n\n{f['fix']}\n\n"
                f"## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
                f"| {today} | audit | Filed |\n")
    if type_ == "cr":
        acs = "\n".join(f"- [ ] {a}" for a in f["acs"])
        return (f"# {disp_id}: {title}\n\n"
                f"> **Status:** Proposed\n> **Priority:** {f['priority']}\n"
                f"> **Type:** {f['ctype']}\n> **Date:** {today}\n\n"
                f"## Summary\n\n{f['summary']}\n\n"
                f"## Acceptance Criteria\n\n{acs}\n\n"
                f"## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
                f"| {today} | audit | Raised |\n")
    options = "\n".join(f"- **{o}**" for o in f["options"])
    return (f"# {disp_id}: {title}\n\n"
            f"> **Status:** Draft\n> **Date:** {today}\n\n"
            f"## Summary\n\n{f['summary']}\n\n"
            f"## Design Options\n\n{options}\n\n"
            f"## Recommendation\n\n{f.get('recommendation', 'TBD - pending decision.')}\n\n"
            f"## Open Decisions\n\n| # | Decision | Status |\n| --- | --- | --- |\n"
            f"| D1 | Act on this finding or keep status quo | Open |\n\n"
            f"## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
            f"| {today} | audit | Filed |\n")


def _index_row(type_: str, disp_id: str, file_id: str, slug: str, title: str, f: dict) -> str:
    link = f"[{disp_id}]({file_id}-{slug}.md)"
    if type_ == "bug":
        cells = [link, title, "Open", f["severity"], f["date"], f["date"]]
    elif type_ == "cr":
        cells = [link, title, "Proposed", f["priority"], f["ctype"], f["date"], "--"]
    else:  # rfc
        cells = [link, title, f.get("priority", "Medium"), "Draft", f.get("author", "audit"),
                 f["date"], "--"]
    return reconcile._join_row(cells)


def file_finding(repo_root: Path | str, type_: str, title: str, fields: dict) -> dict:
    """Allocate an ID, write a structured artifact, append its index row, recompute
    counts. Returns {id, path}. Raises ValueError on a missing required field."""
    if type_ not in TYPES:
        raise ValueError(f"unknown type {type_!r} (expected bug|cr|rfc)")
    spec = TYPES[type_]
    missing = [k for k in spec["required"] if not fields.get(k)]
    if missing:
        raise ValueError(f"{type_} finding missing required field(s): {', '.join(missing)} "
                         "- the filer refuses to write a hollow artifact")
    root = Path(repo_root)
    today = fields.get("date") or date.today().isoformat()
    fields = {**fields, "date": today}
    n = _next_number(root, type_)
    file_id = f"{spec['prefix']}{n:04d}"
    disp_id = spec["disp"].format(n=n)
    slug = _slug(title)
    rel_dir = sdlc_md.ARTIFACT_TYPES[type_][0]
    path = root / rel_dir / f"{file_id}-{slug}.md"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(_render(type_, disp_id, title, today, fields), encoding="utf-8")

    # Append the row to the index data table, then reuse reconcile to recompute counts.
    index_path = root / rel_dir / "_index.md"
    indexed = False
    if index_path.exists():
        lines = index_path.read_text(encoding="utf-8").splitlines()
        # Locate the DATA table by its header (a row with an ID column), so the new row
        # never lands inside the Summary table (whose header is `| Status | Count |`).
        data_header = None
        for i, ln in enumerate(lines):
            cells = reconcile._table_cells(ln)
            if cells and len(cells) > 2 and "id" in [c.lower() for c in cells]:
                data_header = i
        if data_header is not None:
            rows_after = [j for j in range(data_header + 1, len(lines))
                          if lines[j].strip().startswith("| [")]
            pos = (max(rows_after) + 1) if rows_after else data_header + 2  # past header+separator
            lines.insert(pos, _index_row(type_, disp_id, file_id, slug, title, fields))
            index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            reconcile.apply_type(type_, root)  # recompute summary counts (tested)
            indexed = True
    return {"id": disp_id, "file_id": file_id, "path": str(path), "indexed": indexed}


def cmd_file(args: argparse.Namespace) -> int:
    fields = {"severity": args.severity, "priority": args.priority, "ctype": args.ctype,
              "summary": args.summary, "steps": args.steps, "fix": args.fix,
              "author": args.author, "recommendation": args.recommendation}
    fields = {k: v for k, v in fields.items() if v is not None}
    if args.ac:
        fields["acs"] = args.ac
    if args.option:
        fields["options"] = args.option
    result = file_finding(args.root, args.type, args.title, fields)
    print(json.dumps(result, indent=2) if args.format == "json"
          else f"filed {result['id']} -> {result['path']}")
    return 0


def cmd_rebuild(args: argparse.Namespace) -> int:
    res = reconcile.apply_type(args.type, Path(args.root))
    print(f"rebuilt {args.type} index counts (counts_updated={res['counts_updated']})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Deterministic Bug/CR/RFC finding filer (RFC0002).")
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("file", help="File one structured artifact from a finding.")
    f.add_argument("--type", required=True, choices=("bug", "cr", "rfc"))
    f.add_argument("--title", required=True)
    f.add_argument("--summary")
    f.add_argument("--severity", help="bug severity")
    f.add_argument("--priority", help="cr/rfc priority")
    f.add_argument("--ctype", help="cr type (Improvement/Feature/Bug)")
    f.add_argument("--steps", help="bug steps to reproduce")
    f.add_argument("--fix", help="bug proposed fix")
    f.add_argument("--ac", action="append", help="cr acceptance criterion (repeatable)")
    f.add_argument("--option", action="append", help="rfc design option (repeatable)")
    f.add_argument("--recommendation", help="rfc recommendation")
    f.add_argument("--author", default="audit")
    f.add_argument("--root", default=".")
    f.add_argument("--format", choices=("text", "json"), default="text")
    f.set_defaults(func=cmd_file)
    r = sub.add_parser("rebuild", help="Recompute a type's index summary counts.")
    r.add_argument("--type", required=True, choices=("bug", "cr", "rfc", "story", "epic"))
    r.add_argument("--root", default=".")
    r.set_defaults(func=cmd_rebuild)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
