#!/usr/bin/env python3
"""Lite-profile promotion.

The lite profile (`profile: lite` in `.config.yaml`) collapses the pipeline to
PRD -> story -> implement: no epic layer, so a small repo never accumulates more
workflow markdown than source. `promote` is the one-way door to the full pipeline
when a lite project outgrows it: it inserts a single umbrella epic above the
existing epic-less stories, wires each story to it, and flips the profile to full.
The reader itself lives in `lib/sdlc_md.profile`. Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import artifact  # noqa: E402
import reconcile  # noqa: E402

_EPIC_LINE = re.compile(r"^> \*\*Epic:\*\*.*$", re.M)
_PROFILE_LINE = re.compile(r"^\s*profile:\s*\S+\s*$", re.M)
_UMBRELLA_TITLE = "Existing stories (migrated from the lite profile)"


def _story_epic(path: Path) -> str | None:
    """The epic a story names, or None when it has none. Delegates to the shared
    `sdlc_md.story_epic` (one source of truth)."""
    return sdlc_md.story_epic(path)


def _story_title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line.split(":", 1)[1].strip() if ":" in line else line[2:].strip()
    return path.stem


def _set_epic_line(path: Path, epic_id: str) -> None:
    text = path.read_text(encoding="utf-8")
    new = _EPIC_LINE.sub(f"> **Epic:** {epic_id}", text, count=1)
    sdlc_md.atomic_write(path, new)


def _set_profile_full(root: Path) -> None:
    cfg = root / "sdlc-studio" / ".config.yaml"
    text = cfg.read_text(encoding="utf-8") if cfg.exists() else ""
    if _PROFILE_LINE.search(text):
        text = _PROFILE_LINE.sub("profile: full", text, count=1)
    else:
        text = (text.rstrip("\n") + "\n" if text else "") + "profile: full\n"
    sdlc_md.atomic_write(cfg, text)


def promote(repo_root: Path | str, epic_title: str = _UMBRELLA_TITLE,
            dry_run: bool = False) -> dict:
    """Insert an umbrella epic above the epic-less stories, wire them to it, and flip
    the profile to full. Idempotent-safe: only stories without an epic are moved."""
    root = Path(repo_root)
    if sdlc_md.profile(root) != "lite":
        raise ValueError("project is not on the lite profile - nothing to promote")
    orphans = [p for p in sdlc_md.artifact_files("story", root) if _story_epic(p) is None]
    plan = {"epic": None, "stories": [sdlc_md.extract_record_id(p.stem) for p in orphans],
            "count": len(orphans), "dry_run": dry_run}
    if dry_run:
        return plan

    epic = artifact.new(root, "epic", epic_title)
    eid = epic["id"]
    plan["epic"] = eid
    for p in orphans:
        disp = sdlc_md.extract_record_id(p.stem)
        slug = p.stem[len(disp) + 1:]
        _set_epic_line(p, eid)
        artifact._wire_story_to_epic(root, eid, disp, _story_title(p), disp, slug)
    _set_profile_full(root)
    reconcile.apply_type("story", root)
    reconcile.apply_type("epic", root)
    return plan


def cmd_promote(args: argparse.Namespace) -> int:
    r = promote(args.root, dry_run=args.dry_run)
    if args.format == "json":
        print(json.dumps(r, indent=2))
        return 0
    verb = "would promote" if r["dry_run"] else "promoted"
    print(f"lite promote: {verb} {r['count']} epic-less stories"
          + (f" under {r['epic']}" if r["epic"] else ""))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Lite-profile promotion to the full pipeline.")
    sub = p.add_subparsers(dest="cmd", required=True)
    pr = sub.add_parser("promote", help="Insert an umbrella epic and flip profile to full.")
    pr.add_argument("--root", default=".")
    pr.add_argument("--dry-run", action="store_true", dest="dry_run")
    pr.add_argument("--format", choices=("text", "json"), default="text")
    pr.set_defaults(func=cmd_promote)
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
