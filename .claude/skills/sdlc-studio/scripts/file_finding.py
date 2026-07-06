#!/usr/bin/env python3
"""SDLC Studio deterministic finding filer.

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


def index_template_path(type_: str) -> Path:
    return Path(__file__).resolve().parent.parent / "templates" / "indexes" / f"{type_}.md"


def ensure_index(repo_root: Path | str, type_: str, today: str) -> bool:
    """Create `<dir>/_index.md` from `templates/indexes/<type>.md` when missing.

    The canonical index-bootstrap, shared by `artifact new` (lazy, first-use) and `init`
    (front-loaded). Yields a clean *empty* index: summary counts zeroed, data-table headers
    kept (so `append_index_row` works), template sample rows/headings dropped (real content
    never carries `{{ }}`). Idempotent: never clobbers an existing index. Returns True iff
    it created the file."""
    idx = Path(repo_root) / sdlc_md.ARTIFACT_TYPES[type_][0] / "_index.md"
    if idx.exists():
        return False
    tmpl = index_template_path(type_)
    if not tmpl.exists():
        return False
    text = tmpl.read_text(encoding="utf-8")
    text = re.sub(r"^<!--.*?-->\n+", "", text, count=1, flags=re.DOTALL)  # strip template comment
    text = text.replace("{{last_updated}}", today)
    text = re.sub(r"\{\{[a-z_]*count\}\}", "0", text)  # zero the summary counts
    lines = [ln for ln in text.splitlines() if "{{" not in ln]  # drop sample rows/headings
    idx.parent.mkdir(parents=True, exist_ok=True)
    idx.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return True


def _slug(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return "-".join(s.split("-")[:8]) or "untitled"


def _next_number(repo_root: Path, type_: str) -> int:
    # Honour local files, lingering index rows, and origin/main - never re-issue an id
    # that exists only on the remote or as a stale index row.
    return next_id.allocate_number(type_, repo_root)


# Provenance stamp - marks this artifact as tool-created, same as
# `artifact new`, so `provenance check` no longer false-flags filer-created artifacts.
_STAMP = "> **Created-by:** sdlc-studio file\n"


def _render(type_: str, disp_id: str, title: str, today: str, f: dict) -> str:
    """A structured artifact body (required sections populated)."""
    if type_ == "bug":
        return (f"# {disp_id}: {title}\n\n"
                f"> **Status:** Open\n> **Severity:** {f['severity']}\n"
                f"> **Created:** {today}\n{_STAMP}\n"
                f"## Summary\n\n{f['summary']}\n\n"
                f"## Steps to Reproduce\n\n{f['steps']}\n\n"
                f"## Proposed Fix\n\n{f['fix']}\n\n"
                f"## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
                f"| {today} | audit | Filed |\n")
    if type_ == "cr":
        # normalise: an AC supplied with its own leading checkbox ('- [ ] x',
        # '-[x] y') is not doubled into '- [ ] - [ ] x'
        stripped = (re.sub(r"^\s*-\s*\[[ xX]\]\s*", "", a) for a in f["acs"])
        acs = "\n".join(f"- [ ] {a}" for a in stripped)
        return (f"# {disp_id}: {title}\n\n"
                f"> **Status:** Proposed\n> **Priority:** {f['priority']}\n"
                f"> **Type:** {f['ctype']}\n> **Date:** {today}\n{_STAMP}\n"
                f"## Summary\n\n{f['summary']}\n\n"
                f"## Acceptance Criteria\n\n{acs}\n\n"
                f"## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
                f"| {today} | audit | Raised |\n")
    options = "\n".join(f"- **{o}**" for o in f["options"])
    return (f"# {disp_id}: {title}\n\n"
            f"> **Status:** Draft\n> **Date:** {today}\n{_STAMP}\n"
            f"## Summary\n\n{f['summary']}\n\n"
            f"## Design Options\n\n{options}\n\n"
            f"## Recommendation\n\n{f.get('recommendation', 'TBD - pending decision.')}\n\n"
            f"## Open Decisions\n\n| # | Decision | Status |\n| --- | --- | --- |\n"
            f"| D1 | Act on this finding or keep status quo | Open |\n\n"
            f"## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
            f"| {today} | audit | Filed |\n")


def append_index_row(repo_root: Path | str, type_: str, row_line: str) -> bool:
    """Insert a pre-built data-table row into a type's `_index.md` and recompute its summary
    counts (reusing reconcile). Locates the DATA table by its ID-column header so the row
    never lands in the Summary table. Returns False if the index is absent. Shared by the
    finding filer and the general `artifact new`."""
    root = Path(repo_root)
    index_path = root / sdlc_md.ARTIFACT_TYPES[type_][0] / "_index.md"
    if not index_path.exists():
        return False
    lines = index_path.read_text(encoding="utf-8").splitlines()
    hdr = sdlc_md.find_data_header(lines)
    if hdr is None:
        return False
    data_header = hdr[0]
    # Bound the scan to THIS table's contiguous rows (header, separator, then rows until the
    # first non-table line). Scanning to EOF let a later link-first view/breakdown table
    # capture the appended row, so it escaped the master table.
    end = data_header + 2  # past header + separator
    while end < len(lines) and lines[end].lstrip().startswith("|"):
        end += 1
    rows_after = [j for j in range(data_header + 2, end)
                  if lines[j].strip().startswith("| [")]
    pos = (max(rows_after) + 1) if rows_after else data_header + 2
    lines.insert(pos, row_line)
    sdlc_md.atomic_write(index_path, "\n".join(lines) + "\n")
    reconcile.apply_type(type_, root)  # recompute summary counts (tested)
    return True


def file_finding(repo_root: Path | str, type_: str, title: str, fields: dict,
                 dry_run: bool = False) -> dict:
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
    if dry_run:  # preview: write nothing
        indexed = (root / rel_dir / "_index.md").exists()
        return {"id": disp_id, "file_id": file_id, "path": str(path),
                "indexed": indexed, "dry_run": True}
    path.write_text(_render(type_, disp_id, title, today, fields), encoding="utf-8")
    # One shared header-driven row builder for both create paths: read the index's
    # own columns and fill by name, identical to `artifact new`.
    indexed = False
    idx = root / rel_dir / "_index.md"
    if idx.exists():
        hdr = sdlc_md.find_data_header(idx.read_text(encoding="utf-8").splitlines())
        if hdr:
            link = f"[{disp_id}]({file_id}-{slug}.md)"
            row = sdlc_md.row_from_header(hdr[1], link, title, spec["status"], fields)
            indexed = append_index_row(root, type_, row)
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
    result = file_finding(args.root, args.type, args.title, fields, dry_run=args.dry_run)
    verb = "would file" if result.get("dry_run") else "filed"
    print(json.dumps(result, indent=2) if args.format == "json"
          else f"{verb} {result['id']} -> {result['path']}")
    return 0


def cmd_rebuild(args: argparse.Namespace) -> int:
    res = reconcile.apply_type(args.type, Path(args.root))
    print(f"rebuilt {args.type} index counts (counts_updated={res['counts_updated']})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Deterministic Bug/CR/RFC finding filer.")
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
    f.add_argument("--dry-run", action="store_true", dest="dry_run", help="preview; write nothing")
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
