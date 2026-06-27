#!/usr/bin/env python3
"""SDLC Studio lessons manager (both tiers).

Two lesson tiers (see help/lessons.md and reference-agentic-lessons.md):

  Project tier  `sdlc-studio/.local/lessons.md` in the consuming project -
                transient agentic-wave failure memory, reverse-chronological
                `## L-NNNN:` entries, never committed.
  Skill tier    the skill's own `lessons/` folder - durable, generalisable
                `LL{NNNN}-{slug}.md` lessons indexed in `_index.md`.

Subcommands:
  list    Print project-tier lessons (newest first); --global for the skill tier.
  add     Append a project-tier entry; --global promotes into the skill tier
          (next LL id, file from _template.md, index row appended).
  prune   Drop project-tier entries tied to old epics.
  recall  Surface skill-tier lessons matching tags or a query; --all searches
          both tiers.

Output: text by default, or JSON with --format json.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

DEFAULT_PROJECT_FILE = "sdlc-studio/.local/lessons.md"
SKILL_LESSONS_DIR = Path(__file__).resolve().parent.parent / "lessons"

PROJECT_ENTRY_RE = re.compile(r"^##\s+(L-\d{4}):\s*(.+?)\s*$")
FIELD_BULLET_RE = re.compile(r"^-\s+\*\*([^*]+):\*\*\s*(.*)$")
INDEX_ROW_RE = re.compile(
    r"^\|\s*\[(LL\d{4})\]\(([^)]+)\)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$"
)
LL_FILE_RE = re.compile(r"^LL(\d{4})-")

PROJECT_HEADER = """# Project Lessons

**Last Updated:** {date}

<!-- Append new entries at the top. Keep each entry under 10 lines. -->
"""


# -----------------------------------------------------------------------------
# Project tier
# -----------------------------------------------------------------------------


def parse_project_lessons(text: str) -> list[dict]:
    """Entries from a project lessons file, in file order (newest first)."""
    entries: list[dict] = []
    current: dict | None = None
    body: list[str] = []
    for line in text.splitlines():
        m = PROJECT_ENTRY_RE.match(line)
        if m:
            if current:
                current["body"] = "\n".join(body).strip()
                entries.append(current)
            current = {"id": m.group(1), "title": m.group(2), "fields": {}}
            body = []
            continue
        if current is None:
            continue
        body.append(line)
        f = FIELD_BULLET_RE.match(line)
        if f:
            current["fields"][f.group(1).strip().lower()] = f.group(2).strip()
    if current:
        current["body"] = "\n".join(body).strip()
        entries.append(current)
    return entries


def project_header_of(text: str) -> str:
    """Everything before the first `## L-NNNN:` heading (the file header)."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if PROJECT_ENTRY_RE.match(line):
            return "\n".join(lines[:i]).rstrip() + "\n"
    return text.rstrip() + "\n" if text.strip() else ""


def refresh_last_updated(header: str) -> str:
    """Set the header's `**Last Updated:**` line to today when present (the PROJECT_HEADER template
    always carries it); a header without the line is returned unchanged."""
    today = sdlc_md.now_date()
    if "**Last Updated:**" in header:
        return re.sub(r"\*\*Last Updated:\*\*.*", f"**Last Updated:** {today}", header)
    return header


def render_entry(entry: dict) -> str:
    """One project-tier entry back as markdown."""
    out = [f"## {entry['id']}: {entry['title']}", ""]
    if entry["body"]:
        out.append(entry["body"])
    return "\n".join(out).rstrip() + "\n"


def write_project_file(path: Path, header: str, entries: list[dict]) -> None:
    """Rewrite the lessons file: refreshed header, then entries newest first."""
    parts = [refresh_last_updated(header).rstrip() + "\n"]
    parts.extend("\n" + render_entry(e) for e in entries)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(parts), encoding="utf-8")


def next_project_id(entries: list[dict]) -> str:
    """Next free L-NNNN, scanning existing entry IDs for the maximum."""
    nums = [sdlc_md.id_number(e["id"]) or 0 for e in entries]
    return f"L-{(max(nums) if nums else 0) + 1:04d}"


# -----------------------------------------------------------------------------
# Skill tier
# -----------------------------------------------------------------------------


def parse_index_rows(index_path: Path) -> list[dict]:
    """Lesson rows from the skill tier's `_index.md` table."""
    rows: list[dict] = []
    if not index_path.is_file():
        return rows
    for line in index_path.read_text(encoding="utf-8").splitlines():
        m = INDEX_ROW_RE.match(line)
        if m:
            rows.append({
                "id": m.group(1),
                "file": m.group(2),
                "title": m.group(3),
                "tags": [t.strip() for t in m.group(4).split(",") if t.strip()],
            })
    return rows


def next_global_id(lessons_dir: Path) -> str:
    """Next free LL{NNNN}, scanning existing LL files for the maximum."""
    nums = [0]
    for p in sdlc_md.walk_glob(lessons_dir, "LL*.md"):
        m = LL_FILE_RE.match(p.name)
        if m:
            nums.append(int(m.group(1)))
    return f"LL{max(nums) + 1:04d}"


def render_global_lesson(template: str, id_: str, title: str, tags: list[str],
                         body: str, origin: str, date: str) -> str:
    """Fill `_template.md` for a new skill-tier lesson.

    Strips the leading HTML usage comment, fills the frontmatter and the
    Lesson paragraph; the remaining `{{placeholder}}` sections stay for the
    author to complete by judgement.
    """
    lines = template.splitlines()
    i = 0
    if lines and lines[0].lstrip().startswith("<!--"):
        while i < len(lines) and "-->" not in lines[i]:
            i += 1
        i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
    out: list[str] = []
    for line in lines[i:]:
        if line.startswith("id:"):
            out.append(f"id: {id_}")
        elif line.startswith("title:"):
            out.append(f"title: {title}")
        elif line.startswith("tags:"):
            out.append(f"tags: [{', '.join(tags)}]")
        elif line.startswith("added:"):
            out.append(f"added: {date}")
        elif line.startswith("origin:"):
            out.append(f"origin: {origin}")
        elif line.startswith("**Lesson.**"):
            out.append(f"**Lesson.** {body}")
        else:
            out.append(line)
    return "\n".join(out).rstrip() + "\n"


def append_index_row(index_path: Path, id_: str, filename: str, title: str,
                     tags: list[str]) -> None:
    """Append a lesson row to the `_index.md` table (after the last row)."""
    row = f"| [{id_}]({filename}) | {title} | {', '.join(tags)} |"
    lines = index_path.read_text(encoding="utf-8").splitlines()
    last_row = None
    separator = None
    for i, line in enumerate(lines):
        if INDEX_ROW_RE.match(line):
            last_row = i
        elif separator is None and re.match(r"^\|\s*-{3,}", line.replace(" ", "")):
            separator = i
    anchor = last_row if last_row is not None else separator
    if anchor is None:
        raise ValueError(f"no lessons table found in {index_path}")
    lines.insert(anchor + 1, row)
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# -----------------------------------------------------------------------------
# Subcommands
# -----------------------------------------------------------------------------


def cmd_list(args: argparse.Namespace) -> int:
    """Print lessons: project tier by default, skill tier with --global."""
    if args.global_:
        rows = parse_index_rows(Path(args.lessons_dir) / "_index.md")
        if args.format == "json":
            print(json.dumps({"tier": "skill", "lessons": rows, "count": len(rows)},
                             indent=2))
            return 0
        if not rows:
            print("No skill-tier lessons found.")
            return 0
        for r in rows:
            print(f"{r['id']}  {r['title']}  [{', '.join(r['tags'])}]")
        print(f"{len(rows)} lesson(s)")
        return 0
    path = Path(args.project_file)
    if not path.is_file():
        if args.format == "json":
            print(json.dumps({"tier": "project", "lessons": [], "count": 0}, indent=2))
        else:
            print(f"No lessons recorded yet ({path} does not exist).")
        return 0
    entries = parse_project_lessons(path.read_text(encoding="utf-8"))
    if args.format == "json":
        print(json.dumps({"tier": "project", "lessons": entries,
                          "count": len(entries)}, indent=2))
        return 0
    if not entries:
        print(f"No lessons recorded yet in {path}.")
        return 0
    for e in entries:
        print(f"## {e['id']}: {e['title']}")
        if e["body"]:
            print(e["body"])
        print()
    print(f"{len(entries)} lesson(s), newest first")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    """Append a project-tier entry, or promote to the skill tier with --global."""
    tags = [t.strip() for t in (args.tags or "").split(",") if t.strip()]
    if args.global_:
        lessons_dir = Path(args.lessons_dir)
        template_path = lessons_dir / "_template.md"
        index_path = lessons_dir / "_index.md"
        if not template_path.is_file():
            print(f"error: template not found: {template_path}", file=sys.stderr)
            return 1
        if not index_path.is_file():
            print(f"error: index not found: {index_path}", file=sys.stderr)
            return 1
        id_ = next_global_id(lessons_dir)
        filename = f"{id_}-{sdlc_md.slug(args.title)}.md"
        dest = lessons_dir / filename
        if dest.exists():
            print(f"error: refusing to overwrite {dest}", file=sys.stderr)
            return 1
        origin = args.origin or Path.cwd().name
        content = render_global_lesson(
            template_path.read_text(encoding="utf-8"),
            id_, args.title, tags, args.body, origin, sdlc_md.now_date(),
        )
        dest.write_text(content, encoding="utf-8")
        append_index_row(index_path, id_, filename, args.title, tags)
        print(f"Wrote {id_} to {dest} and appended the index row")
        return 0
    path = Path(args.project_file)
    if path.is_file():
        text = path.read_text(encoding="utf-8")
    else:
        text = PROJECT_HEADER.format(date=sdlc_md.now_date())
    entries = parse_project_lessons(text)
    header = project_header_of(text)
    entry: dict = {"id": next_project_id(entries), "title": args.title, "fields": {}}
    bullets = []
    if args.epic:
        bullets.append(f"- **Epic:** {args.epic}")
    if args.wave is not None:
        bullets.append(f"- **Wave:** {args.wave}")
    if tags:
        bullets.append(f"- **Tags:** {', '.join(tags)}")
    body_parts = []
    if bullets:
        body_parts.append("\n".join(bullets))
    if args.body:
        body_parts.append(args.body)
    entry["body"] = "\n\n".join(body_parts)
    write_project_file(path, header, [entry] + entries)
    print(f"Wrote {entry['id']} to {path}")
    return 0


def cmd_prune(args: argparse.Namespace) -> int:
    """Drop project-tier entries tied to epics <= --older, or == --epic."""
    path = Path(args.project_file)
    if not path.is_file():
        print(f"No lessons file at {path}; nothing to prune.")
        return 0
    text = path.read_text(encoding="utf-8")
    entries = parse_project_lessons(text)
    target = args.older or args.epic
    target_num = sdlc_md.id_number(target)
    if target_num is None:
        print(f"error: '{target}' is not a valid epic ID (expected EP000N)",
              file=sys.stderr)
        return 2

    def drops(e: dict) -> bool:
        epic = e["fields"].get("epic")
        num = sdlc_md.id_number(epic) if epic else None
        if num is None:
            return False
        return num <= target_num if args.older else num == target_num

    dropped = [e for e in entries if drops(e)]
    kept = [e for e in entries if not drops(e)]
    if not dropped:
        print("Nothing to prune.")
        return 0
    write_project_file(path, project_header_of(text), kept)
    for e in dropped:
        epic = e["fields"].get("epic", "?")
        print(f"Pruned {e['id']}: {e['title']} ({epic})")
    print(f"{len(dropped)} pruned, {len(kept)} kept")
    return 0


def _matches(title: str, tags: list[str], want_tags: list[str], query: str | None) -> bool:
    """Case-insensitive substring match of tags/query against title and tags."""
    hay_title = title.lower()
    hay_tags = [t.lower() for t in tags]
    if want_tags:
        ok = any(w in t for w in want_tags for t in hay_tags)
        if not ok:
            return False
    if query:
        q = query.lower()
        if q not in hay_title and not any(q in t for t in hay_tags):
            return False
    return True


def cmd_recall(args: argparse.Namespace) -> int:
    """Print skill-tier lessons matching --tags/--query (both tiers with --all)."""
    want_tags = [t.strip().lower() for t in (args.tags or "").split(",") if t.strip()]
    rows = parse_index_rows(Path(args.lessons_dir) / "_index.md")
    matches = [
        {**r, "tier": "skill"}
        for r in rows if _matches(r["title"], r["tags"], want_tags, args.query)
    ]
    if args.all:
        path = Path(args.project_file)
        if path.is_file():
            for e in parse_project_lessons(path.read_text(encoding="utf-8")):
                tags = [t.strip() for t in e["fields"].get("tags", "").split(",") if t.strip()]
                if _matches(e["title"], tags, want_tags, args.query):
                    matches.append({"id": e["id"], "file": str(path),
                                    "title": e["title"], "tags": tags,
                                    "tier": "project"})
    if args.format == "json":
        print(json.dumps({"matches": matches, "count": len(matches)}, indent=2))
        return 0
    if not matches:
        print("No matching lessons.")
        return 0
    for m in matches:
        tier = "" if m["tier"] == "skill" else "  (project tier)"
        print(f"{m['id']}  {m['title']}  [{', '.join(m['tags'])}]  -> {m['file']}{tier}")
    print(f"{len(matches)} match(es)")
    return 0


# -----------------------------------------------------------------------------
# Re-validation + rolling summary
# -----------------------------------------------------------------------------


def is_closed(entry: dict) -> bool:
    """A lesson is closed (no longer valid) when it carries a Status field starting 'Closed'."""
    return entry["fields"].get("status", "").strip().lower().startswith("closed")


def close_entry(entry: dict, reason: str | None) -> bool:
    """Mark an entry closed by appending a Status bullet. Idempotent - returns False if it
    was already closed (so re-running closes nothing new)."""
    if is_closed(entry):
        return False
    label = f"Closed - {reason}" if reason else "Closed"
    bullet = f"- **Status:** {label}"
    entry["body"] = (entry["body"].rstrip() + "\n" + bullet).strip() if entry["body"] else bullet
    entry["fields"]["status"] = label
    return True


def cmd_revalidate(args: argparse.Namespace) -> int:
    """List open project lessons, or close named ones by validity (generalises prune from
    age-based to validity-based). Deterministic; the judgement of what is stale stays the
    operator's, the closure record is mechanical."""
    path = Path(args.project_file)
    if not path.is_file():
        if args.format == "json":
            print(json.dumps({"open": [], "closed": []}, indent=2))
        else:
            print(f"No lessons file at {path}; nothing to re-validate.")
        return 0
    text = path.read_text(encoding="utf-8")
    entries = parse_project_lessons(text)
    if args.close:
        wanted = set(args.close)
        closed = [e["id"] for e in entries if e["id"] in wanted and close_entry(e, args.reason)]
        if closed:
            write_project_file(path, project_header_of(text), entries)
        if args.format == "json":
            print(json.dumps({"closed": closed}, indent=2))
        else:
            for cid in closed:
                print(f"Closed {cid}")
            print(f"{len(closed)} closed")
        return 0
    open_entries = [{"id": e["id"], "title": e["title"]} for e in entries if not is_closed(e)]
    if args.format == "json":
        print(json.dumps({"open": open_entries, "count": len(open_entries)}, indent=2))
        return 0
    if not open_entries:
        print("No open lessons.")
        return 0
    for e in open_entries:
        print(f"{e['id']}  {e['title']}")
    print(f"{len(open_entries)} open lesson(s) - close the stale ones with "
          "`lessons revalidate --close L-NNNN`")
    return 0


def build_summary_text(entries: list[dict]) -> str:
    """The rolling digest of still-valid lessons. Deterministic for a given input (no date),
    so the generator is reproducible - the byte-identical regeneration AC depends on it."""
    open_entries = [e for e in entries if not is_closed(e)]
    out = [
        "# Lessons Summary", "",
        "Rolling digest of still-valid project lessons, read at sprint start. The full log "
        "with closed entries lives in the project tier (`.local/lessons.md`); regenerate this "
        "with `lessons summary`.", "",
    ]
    if not open_entries:
        out.append("_No open lessons._")
    for e in open_entries:
        gist = (e["fields"].get("rule") or e["fields"].get("fix")
                or e["fields"].get("applies to") or "").strip()
        line = f"- **{e['id']}: {e['title']}**"
        if gist:
            line += f" - {gist}"
        out.append(line)
    return "\n".join(out).rstrip() + "\n"


def _default_summary_out(project_file: Path) -> Path:
    """`<repo>/sdlc-studio/retros/LESSONS-SUMMARY.md` derived from the project-file location."""
    rf = project_file.resolve()
    root = rf.parents[2] if len(rf.parents) >= 3 else rf.parent
    return root / "sdlc-studio" / "retros" / "LESSONS-SUMMARY.md"


def cmd_summary(args: argparse.Namespace) -> int:
    """Refresh the committed rolling lessons summary from the still-valid project lessons."""
    path = Path(args.project_file)
    entries = parse_project_lessons(path.read_text(encoding="utf-8")) if path.is_file() else []
    out_path = Path(args.out) if args.out else _default_summary_out(path)
    text = build_summary_text(entries)
    if not args.dry_run:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
    n = sum(1 for e in entries if not is_closed(e))
    if args.format == "json":
        print(json.dumps({"out": str(out_path), "open": n, "written": not args.dry_run}, indent=2))
        return 0
    print(f"{'would write' if args.dry_run else 'wrote'} {n} open lesson(s) -> {out_path}")
    return 0


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------


def _common(sp: argparse.ArgumentParser) -> None:
    """Flags shared by every subcommand (tier locations and output format)."""
    sp.add_argument("--project-file", default=DEFAULT_PROJECT_FILE,
                    help=f"Project-tier lessons file (default: {DEFAULT_PROJECT_FILE})")
    sp.add_argument("--lessons-dir", default=str(SKILL_LESSONS_DIR),
                    help="Skill-tier lessons directory (default: the skill's lessons/)")
    sp.add_argument("--format", choices=("text", "json"), default="text")


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser for list, add, prune, and recall."""
    p = argparse.ArgumentParser(
        prog="lessons.py",
        description="Manage sdlc-studio lessons (project and skill tiers).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    ls = sub.add_parser("list", help="Print lessons (project tier; --global for skill tier).")
    ls.add_argument("--global", dest="global_", action="store_true",
                    help="List the skill tier from lessons/_index.md")
    _common(ls)
    ls.set_defaults(func=cmd_list)

    ad = sub.add_parser("add", help="Add a lesson (project tier; --global promotes).")
    ad.add_argument("--title", required=True, help="Short descriptive title")
    ad.add_argument("--body", required=True, help="The lesson text")
    ad.add_argument("--epic", help="Epic context, e.g. EP0004 (project tier)")
    ad.add_argument("--wave", type=int, help="Wave number (project tier)")
    ad.add_argument("--tags", help="Comma-separated tags")
    ad.add_argument("--origin", help="Origin note for --global (default: cwd name)")
    ad.add_argument("--global", dest="global_", action="store_true",
                    help="Create a skill-tier LL lesson and append the index row")
    _common(ad)
    ad.set_defaults(func=cmd_add)

    pr = sub.add_parser("prune", help="Drop project-tier entries tied to old epics.")
    grp = pr.add_mutually_exclusive_group(required=True)
    grp.add_argument("--older", help="Drop entries with Epic <= this, e.g. EP0003")
    grp.add_argument("--epic", help="Drop entries with Epic == this, e.g. EP0004")
    _common(pr)
    pr.set_defaults(func=cmd_prune)

    rc = sub.add_parser("recall", help="Surface skill-tier lessons by tags/query.")
    rc.add_argument("--tags", help="Comma-separated tags to match (substring)")
    rc.add_argument("--query", help="Free-text match against title/tags")
    rc.add_argument("--all", action="store_true", help="Search both tiers")
    _common(rc)
    rc.set_defaults(func=cmd_recall)

    rv = sub.add_parser("revalidate",
                        help="List open project lessons, or --close stale ones by validity.")
    rv.add_argument("--close", nargs="+", metavar="L-NNNN",
                    help="Close these lesson ids (mark no longer valid)")
    rv.add_argument("--reason", help="Reason recorded on the closed lesson(s)")
    _common(rv)
    rv.set_defaults(func=cmd_revalidate)

    sm = sub.add_parser("summary",
                        help="Refresh the committed rolling lessons summary (read at sprint start).")
    sm.add_argument("--out", help="Summary output path (default: sdlc-studio/retros/LESSONS-SUMMARY.md)")
    sm.add_argument("--dry-run", action="store_true", help="Report without writing")
    _common(sm)
    sm.set_defaults(func=cmd_summary)

    return p


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch to the chosen subcommand."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
