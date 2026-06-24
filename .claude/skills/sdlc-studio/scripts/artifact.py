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
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import file_finding  # noqa: E402  (reuse _slug, _next_number, append_index_row)
import reconcile  # noqa: E402
import transition  # noqa: E402
import telemetry  # noqa: E402  (CR0051: record a telemetry event on close)

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
    # Provenance stamp (CR0052) - marks this artifact as tool-created (deterministic path).
    head = (f"# {disp}: {title}\n\n> **Status:** {st}\n> **Created:** {today}\n"
            f"> **Created-by:** sdlc-studio new\n")
    rev = (f"\n## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
           f"| {today} | {f.get('author', 'sdlc')} | Created via `new` (deterministic) |\n")
    if type_ == "story":
        return (head + f"> **Epic:** {f['epic']}\n> **Persona:** {{{{persona}}}}\n\n"
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


def _core_template(type_: str) -> Path:
    return _skill_root() / "templates" / "core" / f"{type_}.md"


def _render_full(type_: str, disp: str, title: str, today: str, f: dict) -> str:
    """`--template full` (CR0077 Item 2): the deterministic provenance head (identical to
    minimal, so validate/provenance behave the same) followed by the rich section body from
    `templates/core/<type>.md`. Placeholders stay unresolved for the agent, exactly as in
    minimal. Falls back to minimal when no core template ships for the type."""
    minimal = _render(type_, disp, title, today, f)
    core_path = _core_template(type_)
    if "\n## " not in minimal or not core_path.exists():
        return minimal
    head = minimal[:minimal.index("\n## ")]  # provenance + metadata block, no trailing newline
    core = re.sub(r"^<!--.*?-->\n+", "", core_path.read_text(encoding="utf-8"),
                  count=1, flags=re.DOTALL)
    lines = core.splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.startswith("## ")), None)
    if start is None:  # no section body to graft - keep minimal
        return minimal
    body = "\n".join(lines[start:]).rstrip()
    return f"{head}\n\n{body}\n"


def _skill_root() -> Path:
    """The skill directory (…/sdlc-studio/), where templates live - this script is in scripts/."""
    return Path(__file__).resolve().parent.parent


def _index_template(type_: str) -> Path:
    return file_finding.index_template_path(type_)


def _ensure_index(root: Path, type_: str, today: str) -> bool:
    """Create a missing `<dir>/_index.md` on the empty-project first run (CR0077).
    Delegates to the shared `file_finding.ensure_index` (also used by `init`, CR0079)."""
    return file_finding.ensure_index(root, type_, today)


def _header_cells(root: Path, type_: str) -> list[str] | None:
    idx = Path(root) / sdlc_md.ARTIFACT_TYPES[type_][0] / "_index.md"
    if not idx.exists():
        return None
    found = sdlc_md.find_data_header(idx.read_text(encoding="utf-8").splitlines())
    return found[1] if found else None


def _find_epic(root: Path, epic_id: str) -> Path | None:
    """The epic file whose id matches exactly (never a substring: EP001 != EP0010)."""
    eid = sdlc_md.norm_id(epic_id)
    return next((p for p in sdlc_md.artifact_files("epic", Path(root))
                 if sdlc_md.norm_id(p.stem.split("-")[0]) == eid), None)


def _wire_story_to_epic(root: Path, epic_id: str, disp: str, title: str,
                        file_id: str, slug: str) -> bool:
    """Append the story to its parent epic's Story Breakdown (idempotent)."""
    ep = _find_epic(root, epic_id)
    if ep is None:
        return False
    text = ep.read_text(encoding="utf-8")
    line = f"- [ ] [{disp}: {title}](../stories/{file_id}-{slug}.md)"
    if f"[{disp}:" in text or f"[{disp}]" in text:  # already wired (exact, not substring: US0001 != US00012)
        return True
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.strip().lower().startswith("## story breakdown"):
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("## "):
                j += 1
            # Insert after the LAST list item, preserving the section's existing structure
            # (prose, internal blanks) - a full rebuild would collapse blanks and orphan a
            # list against neighbouring prose (MD032). Only an item-less section is rebuilt.
            last_item = max((k for k in range(i + 1, j)
                             if lines[k].strip().startswith("- [")), default=None)
            if last_item is not None:
                lines.insert(last_item + 1, line)
                nxt = last_item + 2  # guard: a blank before the next heading (no orphan)
                if nxt < len(lines) and lines[nxt].lstrip().startswith("## "):
                    lines.insert(nxt, "")
            else:  # empty section (e.g. "_No stories yet._") - rebuild cleanly
                keep = [lines[k] for k in range(i + 1, j)
                        if lines[k].strip() and not lines[k].strip().startswith("_No stories")]
                lines[i:j] = [lines[i], ""] + keep + [line, ""]
            ep.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return True
    return False


def new(repo_root: Path | str, type_: str, title: str, fields: dict | None = None,
        dry_run: bool = False) -> dict:
    if type_ not in SPEC:
        raise ValueError(f"unknown type {type_!r} (expected one of {', '.join(SPEC)})")
    root = Path(repo_root)
    f = dict(fields or {})
    f["date"] = f.get("date") or date.today().isoformat()
    if type_ == "story":
        if not f.get("epic"):
            raise ValueError("a story needs --epic <EPxxxx>")
        # Fail fast before writing - a story wired to a non-existent epic is an orphan whose
        # dangling link only surfaces at the next integrity run (BG0022).
        if _find_epic(root, f["epic"]) is None:
            raise ValueError(f"epic {f['epic']} not found - create it first, or fix the id")
    n = file_finding._next_number(root, type_)
    prefix = sdlc_md.ARTIFACT_TYPES[type_][1]
    file_id = f"{prefix}{n:04d}"
    disp = _disp(type_, n)
    slug = file_finding._slug(title)
    path = root / sdlc_md.ARTIFACT_TYPES[type_][0] / f"{file_id}-{slug}.md"
    if path.exists():
        raise FileExistsError(path)
    if dry_run:  # preview: write nothing, report what would happen (CR0057)
        idx_exists = _header_cells(root, type_) is not None
        would_create_index = (not idx_exists) and _index_template(type_).exists()
        return {"id": disp, "file_id": file_id, "path": str(path),
                "indexed": idx_exists or would_create_index,
                "would_create_index": would_create_index,
                "epic_linked": (type_ == "story") or None, "dry_run": True}
    path.parent.mkdir(parents=True, exist_ok=True)
    render = _render_full if f.get("template") == "full" else _render  # CR0077 Item 2
    path.write_text(render(type_, disp, title, f["date"], f), encoding="utf-8")
    index_created = _ensure_index(root, type_, f["date"])  # greenfield first run (CR0077)
    header = _header_cells(root, type_)
    indexed = False
    if header:
        row = sdlc_md.row_from_header(header, f"[{disp}]({file_id}-{slug}.md)", title,
                                      SPEC[type_]["status"], f)
        indexed = file_finding.append_index_row(root, type_, row)
    linked = _wire_story_to_epic(root, f["epic"], disp, title, file_id, slug) \
        if type_ == "story" else None
    return {"id": disp, "file_id": file_id, "path": str(path),
            "indexed": indexed, "index_created": index_created,
            "epic_linked": linked, "dry_run": False}


def new_batch(repo_root: Path | str, type_: str, items: list[dict],
              template: str = "full", dry_run: bool = False) -> dict:
    """Create many artifacts of one type in a single atomic pass (CR0078).

    Reserve a contiguous id block up front (LL0002: reserve before writing), render each
    file (full template by default - batch is the fan-out case where structure must be
    guaranteed), append every index row, and wire each story into its parent epic - one pass.
    All-or-nothing: a missing epic or a file collision aborts before any write. `--dry-run`
    returns the full id map and planned wiring."""
    if type_ not in SPEC:
        raise ValueError(f"unknown type {type_!r}")
    root = Path(repo_root)
    today = date.today().isoformat()
    if not items:
        raise ValueError("batch is empty")
    # Validate the whole batch BEFORE writing anything (atomic) - a story wired to a
    # missing epic is an orphan (BG0022); a colliding id would corrupt the run.
    if type_ == "story":
        for it in items:
            if not it.get("epic"):
                raise ValueError("each story item needs an 'epic'")
            if _find_epic(root, it["epic"]) is None:
                raise ValueError(f"epic {it['epic']} not found - create it first")
    n0 = file_finding._next_number(root, type_)
    prefix = sdlc_md.ARTIFACT_TYPES[type_][1]
    plan = []
    for i, it in enumerate(items):
        if not it.get("title"):
            raise ValueError("each item needs a 'title'")
        n = n0 + i
        file_id = f"{prefix}{n:04d}"
        slug = file_finding._slug(it["title"])
        path = root / sdlc_md.ARTIFACT_TYPES[type_][0] / f"{file_id}-{slug}.md"
        if path.exists():
            raise FileExistsError(f"{path} (batch aborted, nothing written)")
        plan.append({"n": n, "file_id": file_id, "disp": _disp(type_, n),
                     "slug": slug, "path": path, "item": it})
    if dry_run:
        return {"type": type_, "count": len(plan), "template": template, "dry_run": True,
                "ids": [{"id": p["disp"], "path": str(p["path"]),
                         "epic": p["item"].get("epic")} for p in plan]}
    render = _render_full if template == "full" else _render
    _ensure_index(root, type_, today)
    created = []
    for p in plan:
        it = p["item"]
        f = dict(it)
        f["date"] = today
        p["path"].parent.mkdir(parents=True, exist_ok=True)
        p["path"].write_text(render(type_, p["disp"], it["title"], today, f), encoding="utf-8")
        header = _header_cells(root, type_)
        link = f"[{p['disp']}]({p['file_id']}-{p['slug']}.md)"
        if header:
            row = sdlc_md.row_from_header(header, link, it["title"], SPEC[type_]["status"], f)
            file_finding.append_index_row(root, type_, row)
        if type_ == "story":
            _wire_story_to_epic(root, it["epic"], p["disp"], it["title"], p["file_id"], p["slug"])
        created.append({"id": p["disp"], "file_id": p["file_id"], "path": str(p["path"])})
    return {"type": type_, "count": len(created), "template": template,
            "created": created, "dry_run": False}


def close(repo_root: Path | str, artifact_id: str, status: str | None = None,
          metrics: dict | None = None, dry_run: bool = False, force: bool = False) -> dict:
    """Terminal-transition an artifact and cascade (reuse transition), then record a
    telemetry event (CR0051 / RFC0014 WS2). Telemetry is advisory - it never affects the
    close result (the recorder swallows its own failures). `force` bypasses the story->Done
    AC-verify gate (CR0084); it is inert for non-story types."""
    prefix = "".join(c for c in artifact_id if c.isalpha()).upper()
    type_ = _PREFIX_TYPE.get(prefix)
    if type_ is None:
        raise ValueError(f"cannot infer type from id {artifact_id!r}")
    st = status or SPEC[type_]["terminal"]
    if dry_run:  # preview the transition target, write nothing, record nothing (CR0057)
        return {"id": artifact_id, "type": type_, "to": st, "dry_run": True}
    result = transition.transition(repo_root, artifact_id, st, force=force)
    telemetry.record(repo_root, {"id": artifact_id, "type": type_, **(metrics or {})})
    return result


def cmd_new(args: argparse.Namespace) -> int:
    f = {k: v for k, v in {"epic": args.epic, "priority": args.priority, "ctype": args.ctype,
                           "severity": args.severity, "author": args.author,
                           "template": args.template}.items() if v}
    r = new(args.root, args.type, args.title, f, dry_run=args.dry_run)
    verb = "would create" if r.get("dry_run") else "created"
    print(json.dumps(r, indent=2) if args.format == "json"
          else f"{verb} {r['id']} -> {r['path']} (indexed={r['indexed']}, epic_linked={r['epic_linked']})")
    return 0


def cmd_batch(args: argparse.Namespace) -> int:
    items = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    if not isinstance(items, list):
        print("error: --spec must be a JSON list of items", file=sys.stderr)
        return 1
    r = new_batch(args.root, args.type, items, template=args.template, dry_run=args.dry_run)
    if args.format == "json":
        print(json.dumps(r, indent=2))
        return 0
    verb = "would create" if r.get("dry_run") else "created"
    print(f"batch: {verb} {r['count']} {args.type}(s) (template={r['template']})")
    for row in (r.get("ids") or r.get("created") or []):
        print(f"  {row['id']} -> {row['path']}")
    return 0


def cmd_close(args: argparse.Namespace) -> int:
    metrics = {}
    if args.iterations is not None:
        metrics["iterations"] = int(args.iterations)
    if args.verdict:
        metrics["critic_verdict"] = args.verdict
    if args.wall_time_s is not None:
        metrics["wall_time_s"] = int(args.wall_time_s)
    if args.stages:
        metrics["stages"] = args.stages
    r = close(args.root, args.id, args.status, metrics or None, dry_run=args.dry_run,
              force=getattr(args, "force", False))
    verb = "would close" if r.get("dry_run") else "closed"
    print(json.dumps(r, indent=2) if args.format == "json" else f"{verb} {args.id}")
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
    n.add_argument("--template", choices=("minimal", "full"), default="minimal",
                   help="scaffold richness: minimal (default) or the full templates/core body")
    n.add_argument("--root", default=".")
    n.add_argument("--dry-run", action="store_true", dest="dry_run", help="preview; write nothing")
    n.add_argument("--format", choices=("text", "json"), default="text")
    n.set_defaults(func=cmd_new)
    b = sub.add_parser("batch", help="Create many artifacts of one type in one atomic pass (CR0078).")
    b.add_argument("--type", required=True, choices=tuple(SPEC))
    b.add_argument("--spec", required=True, help="JSON file: a list of {title, epic?, ...} items")
    b.add_argument("--template", choices=("minimal", "full"), default="full",
                   help="batch defaults to full (the fan-out case); --template minimal opts out")
    b.add_argument("--root", default=".")
    b.add_argument("--dry-run", action="store_true", dest="dry_run", help="preview the id map; write nothing")
    b.add_argument("--format", choices=("text", "json"), default="text")
    b.set_defaults(func=cmd_batch)
    c = sub.add_parser("close", help="Terminal-transition an artifact + cascade + record telemetry.")
    c.add_argument("--id", required=True)
    c.add_argument("--status", help="override the per-type terminal status")
    c.add_argument("--force", action="store_true",
                   help="bypass the story->Done AC-verify gate (CR0084; inert for non-stories)")
    c.add_argument("--iterations", help="run metric: iterations to green (telemetry)")
    c.add_argument("--verdict", help="run metric: critic verdict (telemetry)")
    c.add_argument("--wall-time-s", dest="wall_time_s", help="run metric: wall time (telemetry)")
    c.add_argument("--stages", help="run metric: stages passed (telemetry)")
    c.add_argument("--root", default=".")
    c.add_argument("--dry-run", action="store_true", dest="dry_run", help="preview; write nothing")
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
