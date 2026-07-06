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
import re
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


def _type_id(text: str, prefix: str) -> str | None:
    """An artifact id of this type in a cell (e.g. US0042), allowing a `CR-0042` dash.
    The id column header varies across house formats (ID / Story / Bug / CR), so the
    master table is recognised by its rows carrying this type's ids, not by the header."""
    m = re.search(rf"\b{re.escape(prefix)}-?\d+\b", text)
    return m.group(0) if m else None


def _table_end(lines: list, start: int):
    """Yield (i, row_cells) for the data rows of the table beginning after `start`,
    stopping at a blank/non-table line or the next header."""
    for i in range(start + 1, len(lines)):
        row = reconcile._table_cells(lines[i])
        if row is None:
            if lines[i].strip().startswith("|"):
                continue  # separator
            break
        if "status" in [c.lower() for c in row]:
            break  # next table's header
        yield i, row


def _id_col(header_cells: list) -> int:
    """The id column of a data table: the explicit `ID` header, else column 0 (the
    universal convention - the artifact id is the first column, named ID / Story / Bug /
    CR / EP in the house formats). Reading the id from this column only (not any cell)
    means the master `## All` table - which holds every artifact - always has the most
    id-bearing rows, so a secondary status view never wins selection."""
    low = [c.lower() for c in header_cells]
    return low.index("id") if "id" in low else 0


def _master_header(lines: list, prefix: str) -> int | None:
    """Index of the master data-table header: the `status`-bearing header with the most
    rows carrying this type's id in its ID column."""
    best, best_n = None, 0
    for i, ln in enumerate(lines):
        cells = reconcile._table_cells(ln)
        if not (cells and len(cells) > 2 and "status" in [c.lower() for c in cells]):
            continue
        idc = _id_col(cells)
        n = sum(1 for _j, row in _table_end(lines, i) if idc < len(row) and _type_id(row[idc], prefix))
        if n > best_n:
            best, best_n = i, n
    return best


def _terminal_rows(lines: list, header_i: int, vocab: list, terminal: set, prefix: str) -> list:
    """(line_index, id, status) for terminal data rows under the master header. Both the
    id and status are read from their header columns (positional), not by scanning cells."""
    hcells = reconcile._table_cells(lines[header_i])
    status_col = [c.lower() for c in hcells].index("status")
    id_col = _id_col(hcells)
    out = []
    for i, row in _table_end(lines, header_i):
        if status_col >= len(row) or id_col >= len(row):
            continue
        rid = _type_id(row[id_col], prefix)
        st = reconcile._canonical_status(row[status_col], vocab)
        if rid and st in terminal:
            out.append((i, rid, st))
    return out


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
    vocab = sdlc_md.status_vocab(type_, root)
    terminal = statuses or sdlc_md.terminal_statuses(type_)
    rel, prefix = sdlc_md.ARTIFACT_TYPES[type_]
    index_path = root / rel / "_index.md"
    result = {"archived": [], "count": 0, "release": release, "archive_path": None}
    if not index_path.exists():
        return result
    lines = index_path.read_text(encoding="utf-8").splitlines()
    hi = _master_header(lines, prefix)
    if hi is None:
        return result
    targets = _terminal_rows(lines, hi, vocab, terminal, prefix)
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
    header_line = lines[hi]
    sep_line = "|" + " --- |" * (header_line.count("|") - 1)
    if archive_path.exists():
        atext = archive_path.read_text(encoding="utf-8").rstrip("\n")
        archive_path.write_text(atext + "\n" + "\n".join(moved_lines) + "\n", encoding="utf-8")
    else:
        archive_path.write_text(
            f"# {type_} archive - {release}\n\n"
            "Terminal rows archived from the live index. Artifact files are "
            "unchanged; these rows keep the census correct via parse_index's union.\n\n"
            f"{header_line}\n{sep_line}\n" + "\n".join(moved_lines) + "\n", encoding="utf-8")

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
