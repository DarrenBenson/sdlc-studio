#!/usr/bin/env python3
"""Claude Code plan-file manager.

Manages the plan-mode files Claude Code persists under `~/.claude/plans/`
(one kebab-case-slugged file per task; see reference-plan-files.md).
Active plans live at the top level; retired plans move to
`archive/<yyyy-mm>/<slug>.md`. Read-only except the explicit archive
move; nothing is ever deleted or overwritten.

Note: the plans directory is operator-owned and lives outside the
project's `sdlc-studio/.local/`; `archive` is the one sanctioned write.

Subcommands:
  list     Table of active plans: slug, modified date, age, first heading.
  archive  Move an active plan to archive/<yyyy-mm>/.

Output: aligned text by default, or JSON with --format json.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

DEFAULT_PLANS_DIR = "~/.claude/plans"
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$")


def first_heading(text: str) -> str:
    """First markdown heading, skipping a YAML frontmatter or HTML comment header.

    Plan files often open with a YAML block (`---`...`---`) or an HTML
    comment; the identifying heading comes after. Returns "(no heading)"
    when the file carries none.
    """
    lines = text.splitlines()
    i = 0
    # YAML frontmatter: a leading `---` fence closed by another.
    if i < len(lines) and lines[i].strip() == "---":
        for j in range(i + 1, len(lines)):
            if lines[j].strip() in ("---", "..."):
                i = j + 1
                break
    # HTML comment header(s), possibly multi-line.
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("<!--"):
            while i < len(lines) and "-->" not in lines[i]:
                i += 1
            i += 1
            continue
        break
    for line in lines[i:]:
        m = HEADING_RE.match(line)
        if m:
            return m.group(1)
    return "(no heading)"


def plan_record(path: Path, archived: bool, now: datetime) -> dict:
    """Metadata record for one plan file."""
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    age_days = max(0, (now - mtime).days)
    try:
        heading = first_heading(path.read_text(encoding="utf-8"))
    except OSError:
        heading = "(unreadable)"
    return {
        "slug": path.stem,
        "path": str(path),
        "modified": mtime.strftime("%Y-%m-%d"),
        "age_days": age_days,
        "heading": heading,
        "archived": archived,
    }


def collect_plans(plans_dir: Path, include_archived: bool) -> list[dict]:
    """All plan records under `plans_dir`, newest first."""
    now = datetime.now(timezone.utc)
    records = [
        plan_record(p, archived=False, now=now)
        for p in sdlc_md.walk_glob(plans_dir, "*.md")
    ]
    if include_archived:
        archive_dir = plans_dir / "archive"
        if archive_dir.exists():
            for p in sorted(archive_dir.rglob("*.md")):
                if p.is_file():
                    records.append(plan_record(p, archived=True, now=now))
    return sorted(records, key=lambda r: r["age_days"])


def cmd_list(args: argparse.Namespace) -> int:
    """Print the plan table (active by default; --all includes archive)."""
    plans_dir = Path(args.plans_dir).expanduser()
    records = collect_plans(plans_dir, include_archived=args.all)
    if args.stale:
        records = [r for r in records if not r["archived"] and r["age_days"] > args.days]
    if args.format == "json":
        print(json.dumps({
            "plans_dir": str(plans_dir),
            "stale_threshold_days": args.days if args.stale else None,
            "plans": records,
            "count": len(records),
        }, indent=2))
        return 0
    if not records:
        if args.stale:
            print(f"No plans older than {args.days} days in {plans_dir}")
        else:
            print(f"No plans found in {plans_dir}")
        return 0
    slug_w = max(len(r["slug"]) for r in records)
    label = "STALE PLANS" if args.stale else "PLANS"
    print(label)
    for r in records:
        mark = "  [archived]" if r["archived"] else ""
        print(f"  {r['slug']:<{slug_w}}  ({r['modified']}, {r['age_days']}d){mark}")
        print(f"  {'':<{slug_w}}  {r['heading']}")
    active = sum(1 for r in records if not r["archived"])
    archived = len(records) - active
    summary = f"{active} active plan(s)"
    if archived:
        summary += f", {archived} archived"
    print(summary)
    return 0


def cmd_archive(args: argparse.Namespace) -> int:
    """Move `<plans-dir>/<slug>.md` into `archive/<yyyy-mm>/`."""
    plans_dir = Path(args.plans_dir).expanduser()
    src = plans_dir / f"{args.slug}.md"
    archive_dir = plans_dir / "archive"
    if not src.is_file():
        existing = sorted(archive_dir.glob(f"*/{args.slug}.md")) if archive_dir.exists() else []
        if existing:
            print(f"error: plan '{args.slug}' is already archived at {existing[0]}",
                  file=sys.stderr)
        else:
            print(f"error: no active plan named '{args.slug}' in {plans_dir}",
                  file=sys.stderr)
        return 1
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    dest = archive_dir / month / f"{args.slug}.md"
    if dest.exists():
        print(f"error: archive target already exists, refusing to overwrite: {dest}",
              file=sys.stderr)
        return 1
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest))
    print(f"Archived {args.slug} -> {dest}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser for list and archive."""
    p = argparse.ArgumentParser(
        prog="plan.py",
        description="Manage Claude Code plan-mode files (~/.claude/plans).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    ls = sub.add_parser("list", help="Table of plans: slug, date, age, heading.")
    ls.add_argument("--all", action="store_true", help="Include archived plans")
    ls.add_argument("--stale", action="store_true",
                    help="Show only active plans older than --days")
    ls.add_argument("--days", type=int, default=30,
                    help="Staleness threshold in days (default: 30)")
    ls.add_argument("--plans-dir", default=DEFAULT_PLANS_DIR,
                    help=f"Plans directory (default: {DEFAULT_PLANS_DIR})")
    ls.add_argument("--format", choices=("text", "json"), default="text")
    ls.set_defaults(func=cmd_list)

    ar = sub.add_parser("archive", help="Move an active plan to archive/<yyyy-mm>/.")
    ar.add_argument("slug", help="Plan slug (filename without .md)")
    ar.add_argument("--plans-dir", default=DEFAULT_PLANS_DIR,
                    help=f"Plans directory (default: {DEFAULT_PLANS_DIR})")
    ar.set_defaults(func=cmd_archive)

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
