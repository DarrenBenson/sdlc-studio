#!/usr/bin/env python3
"""SDLC Studio index archival.

`archive --type <t> --release <r>` moves a type's TERMINAL index rows out of the live
`_index.md` master table into `<type>/archive/{release}/{type}.md`, leaving a bullet
pointer in the live index. Rows-only: the artifact FILES stay put (IDs and links
intact). `reconcile`/`status` still count the archived rows because `parse_index` unions
the archive sub-indexes, so the census stays correct and the live index stays
bounded - the read-cost win on large projects.

Explicit, operator-run (no auto-trigger). Idempotent per release. Read-then-write.

Subcommand:
  archive  Move terminal rows of one type into an archive sub-index by release.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import reconcile  # noqa: E402  (sibling - cell helpers + the union-aware count recompute)

# Terminal (closed) statuses safe to archive by default come from the single shared
# source (sdlc_md.terminal_statuses), which deliberately excludes re-activatable states
# like Deferred/Blocked/Paused. A hardcoded copy here drifted and archived Deferred rows
# as if closed; the `--statuses` override remains for explicit operator opt-in.
_ARCHIVABLE_TYPES = sorted(t for t in sdlc_md.ARTIFACT_TYPES if sdlc_md.terminal_statuses(t))
_ARCHIVED_HEADING = "## Archived Releases"


def _range_label(ids: list) -> str:
    nums = sorted(n for n in (sdlc_md.id_number(i) for i in ids) if n is not None)
    if not nums:
        return ", ".join(ids[:3])
    prefix = "".join(c for c in ids[0] if not c.isdigit()).rstrip("-")
    return f"{prefix}{nums[0]:04d}-{prefix}{nums[-1]:04d}" if nums[0] != nums[-1] else ids[0]


def archive(repo_root: Path | str, type_: str, release: str,
            statuses: set | None = None, dry_run: bool = False) -> dict:
    """Move `type_`'s terminal rows into archive/{release}/{type}.md. Returns
    {archived: [ids], count, release, archive_path}."""
    if type_ not in sdlc_md.ARTIFACT_TYPES:
        raise ValueError(f"unknown type {type_!r}")
    root = Path(repo_root)
    terminal = statuses or sdlc_md.terminal_statuses(type_)
    rel, prefix = sdlc_md.ARTIFACT_TYPES[type_]
    index_path = root / rel / "_index.md"
    result = {"archived": [], "count": 0, "release": release, "archive_path": None}
    if not index_path.exists():
        return result
    text = index_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    # Shared iter_tables walker (no hand-rolled table parsing): the master table + its rows.
    # An explicit `--statuses` override selects by that set; otherwise the type's terminal set.
    m = reconcile.master_terminal_rows(text, type_, root)
    if m is None:
        return result
    targets = [(line0, rid, st) for line0, rid, st, _term in m["rows"] if st in terminal]
    if not targets:
        return result
    moved_idx = {i for i, _id, _st in targets}
    moved_lines = [lines[i] for i, _id, _st in targets]
    ids = [rid for _i, rid, _st in targets]
    archive_rel = f"{rel}/archive/{release}/{type_}.md"
    result.update(archived=ids, count=len(ids), archive_path=archive_rel)
    if dry_run:
        return result

    # 1) write the moved rows into the archive sub-index (full rows = full traceability).
    archive_path = root / archive_rel
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    header_line = lines[m["header_line0"]]
    sep_line = "|" + " --- |" * (header_line.count("|") - 1)
    if archive_path.exists():
        atext = archive_path.read_text(encoding="utf-8").rstrip("\n")
        # Dedupe against ids already archived: a crash between this write and the live-index
        # trim (step 2) leaves the rows in BOTH files, so a re-run would append them twice
        # (permanent, unflagged - detect_duplicate_rows scans only the live index). Idempotent.
        seen = {sdlc_md.norm_id(rid) for rid in reconcile.index_row_ids(atext)}
        fresh = [ln for ln, rid in zip(moved_lines, ids)
                 if sdlc_md.norm_id(rid) not in seen]
        if fresh:
            sdlc_md.atomic_write(archive_path, atext + "\n" + "\n".join(fresh) + "\n")
    else:
        sdlc_md.atomic_write(archive_path,
            f"# {type_} archive - {release}\n\n"
            "Terminal rows archived from the live index. Artifact files are "
            "unchanged; these rows keep the census correct via parse_index's union.\n\n"
            f"{header_line}\n{sep_line}\n" + "\n".join(moved_lines) + "\n")

    # 2) drop the moved rows from the live index and add/refresh the release bullet.
    kept = [ln for i, ln in enumerate(lines) if i not in moved_idx]
    bullet = f"- **{release}** ({_range_label(ids)}, {len(ids)} archived) -> {archive_rel}"
    if _ARCHIVED_HEADING in kept:
        h = kept.index(_ARCHIVED_HEADING)
        existing = next((j for j in range(h + 1, len(kept))
                         if kept[j].startswith(f"- **{release}** ")), None)
        if existing is not None:
            kept[existing] = bullet  # refresh this release's pointer
        else:
            kept.insert(h + 2, bullet)
    else:
        kept += ["", _ARCHIVED_HEADING, "", bullet]
    index_path.write_text("\n".join(kept) + "\n", encoding="utf-8")

    # 3) recompute the live summary counts (apply unions archive rows -> active+archived).
    reconcile.apply_type(type_, root)
    return result


def cmd_archive(args: argparse.Namespace) -> int:
    statuses = set(s.strip() for s in args.statuses.split(",")) if args.statuses else None
    res = archive(args.root, args.type, args.release, statuses=statuses, dry_run=args.dry_run)
    if args.format == "json":
        print(json.dumps(res, indent=2))
    else:
        verb = "would archive" if args.dry_run else "archived"
        print(f"{verb} {res['count']} {args.type} row(s) to {res['archive_path'] or '-'}"
              + (f" [{res['release']}]" if res["count"] else " (nothing terminal to archive)"))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Archive terminal index rows by release.")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("archive", help="Move a type's terminal rows into an archive sub-index.")
    a.add_argument("--type", required=True, choices=_ARCHIVABLE_TYPES)
    a.add_argument("--release", required=True, help="Release label, e.g. r2.5")
    a.add_argument("--statuses", help="Comma-separated statuses to archive (default: terminal set)")
    a.add_argument("--root", default=".")
    a.add_argument("--dry-run", action="store_true")
    a.add_argument("--format", choices=("text", "json"), default="text")
    a.set_defaults(func=cmd_archive)
    sdlc_md.add_global_root(p)
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
