#!/usr/bin/env python3
"""SDLC Studio artifact-ID allocator.

Deterministically pick the next free artifact number for a type, so Claude
never has to scan files and guess (doctrine rule 13: cross-repo numbering).
Scans local files and, with --remote, the highest number already on
`origin/main` (read-only `git ls-tree`, no fetch - the caller fetches first).

Subcommands:
  allocate    Print the next free ID for a type.
  scan        List every ID currently used for a type.
  collisions  Flag any normalised ID claimed by more than one file.

Output: text (the ID) by default, or JSON with --format json.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import re  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

# CR0105: meta-artifacts that carry a numeric id but are NOT pipeline artifacts (no status vocab,
# no reconcile/conformance). Kept out of sdlc_md.ARTIFACT_TYPES so the pipeline machinery ignores
# them; the allocator resolves them here so review/retro ids are never hand-picked. (lessons LL####
# have their own manager in lessons.py; personas are named, not numbered.)
META_TYPES: dict[str, tuple[str, str]] = {
    "review": ("sdlc-studio/reviews", "RV"),
    "retro": ("sdlc-studio/retros", "RETRO"),
}


def _spec(type_: str) -> tuple[str, str]:
    """(relative dir, id prefix) for a pipeline or meta type."""
    return sdlc_md.ARTIFACT_TYPES.get(type_) or META_TYPES[type_]


def _meta_nums(prefix: str, stems) -> list[int]:
    """Numeric ids from file stems for a meta prefix (e.g. RV0005, RETRO0001) - the standard
    extract_record_id does not recognise these prefixes, so match prefix + 3-4 digits directly."""
    pat = re.compile(rf"^{re.escape(prefix)}-?(\d{{3,4}})", re.IGNORECASE)
    return sorted({int(m.group(1)) for s in stems if (m := pat.match(s))})


def local_ids(type_: str, repo_root: Path) -> list[int]:
    """Numeric IDs of all local artifact files of `type_` (pipeline or meta)."""
    if type_ in META_TYPES:
        rel, prefix = META_TYPES[type_]
        d = Path(repo_root) / rel
        stems = [p.stem for p in d.glob("*.md") if p.name != "_index.md"] if d.exists() else []
        return _meta_nums(prefix, stems)
    ids: list[int] = []
    for path in sdlc_md.artifact_files(type_, repo_root):
        rec = sdlc_md.extract_record_id(path.stem)
        num = sdlc_md.id_number(rec) if rec else None
        if num is not None:
            ids.append(num)
    return sorted(set(ids))


def index_row_ids(type_: str, repo_root: Path) -> list[int]:
    """Numeric ids present as rows in the type's `_index.md`. Catches an id whose file was
    deleted but whose index row remains: re-issuing it would collide (BG0022)."""
    if type_ in META_TYPES:  # meta-artifacts have no derived _index.md
        return []
    import reconcile  # local import avoids any import cycle
    rel = sdlc_md.ARTIFACT_TYPES[type_][0]
    index_path = Path(repo_root) / rel / "_index.md"
    if not index_path.exists():
        return []
    ids = [num for norm in reconcile._index_row_ids(index_path.read_text(encoding="utf-8"))
           if (num := sdlc_md.id_number(norm)) is not None]
    return sorted(set(ids))


def allocate_number(type_: str, repo_root: Path | str, remote: bool = True) -> int:
    """The next free numeric id: above the max of local files, index rows, and (when
    available) origin/main - so a deleted-but-still-indexed id, or an id only on the remote,
    is never re-issued (BG0022). `remote=False` skips the read-only git lookup."""
    root = Path(repo_root)
    base = max([0, *local_ids(type_, root), *index_row_ids(type_, root)])
    if remote:
        rids, available = remote_ids(type_, root)
        if available and rids:
            base = max(base, max(rids))
    return base + 1


def remote_ids(type_: str, repo_root: Path) -> tuple[list[int], bool]:
    """Numeric IDs on origin/main for `type_`. Returns (ids, available).

    Uses `git ls-tree` (read-only, no network). `available` is False when the
    repo has no origin/main or git is unavailable.
    """
    rel, prefix = _spec(type_)
    try:
        result = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", "origin/main", "--", rel],
            capture_output=True, text=True, cwd=str(repo_root), check=False,
        )
    except FileNotFoundError:
        return [], False
    if result.returncode != 0:
        return [], False
    stems = [Path(line).stem for line in result.stdout.splitlines()]
    if type_ in META_TYPES:
        return _meta_nums(prefix, stems), True
    ids: list[int] = []
    for stem in stems:
        rec = sdlc_md.extract_record_id(stem)
        num = sdlc_md.id_number(rec) if rec else None
        if num is not None:
            ids.append(num)
    return sorted(set(ids)), True


def cmd_allocate(args: argparse.Namespace) -> int:
    """Print the next free ID for a type."""
    type_ = args.type
    repo_root = Path(args.root).resolve()
    prefix = _spec(type_)[1]
    local = local_ids(type_, repo_root)
    local_max = max(local) if local else 0
    remote_max = 0
    remote_available = False
    if args.remote:
        remote, remote_available = remote_ids(type_, repo_root)
        remote_max = max(remote) if remote else 0
    base = max(local_max, remote_max)
    next_num = base + 1
    next_id = f"{prefix}{next_num:04d}"
    warning = None
    if args.remote and remote_available and remote_max > local_max:
        warning = (
            f"origin/main is ahead of local for {type_} "
            f"({prefix}{remote_max:04d} > {prefix}{local_max:04d}); "
            f"allocating above the remote maximum"
        )
    if args.format == "json":
        print(json.dumps({
            "type": type_,
            "prefix": prefix,
            "local_max": local_max,
            "remote_max": remote_max,
            "remote_available": remote_available,
            "next_id": next_id,
            "warning": warning,
        }, indent=2))
    else:
        if warning:
            print(f"warning: {warning}", file=sys.stderr)
        print(next_id)
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    """List all IDs currently used for a type."""
    type_ = args.type
    repo_root = Path(args.root).resolve()
    prefix = _spec(type_)[1]
    local = local_ids(type_, repo_root)
    ids = [f"{prefix}{n:04d}" for n in local]
    if args.format == "json":
        print(json.dumps({"type": type_, "ids": ids, "count": len(ids)}, indent=2))
    else:
        for i in ids:
            print(i)
        print(f"# {len(ids)} {type_}(s)", file=sys.stderr)
    return 0


def detect_collisions(repo_root: Path | str) -> dict:
    """Find every normalised artifact ID claimed by more than one file.

    Scans all artifact types under repo_root, normalises each file's ID
    (`CR0007` and `CR-0007` collapse to one key), groups files by that key,
    and flags any key backed by more than one distinct file. Returns the
    documented shape:

        { "duplicates": [ { "id", "files": [<sorted paths>] } ], "count" }

    `duplicates` is sorted by normalised ID; `files` within each group are
    sorted. `count` equals len(duplicates).
    """
    root = Path(repo_root)
    groups: dict[str, set[str]] = {}
    for type_ in sdlc_md.ARTIFACT_TYPES:
        for path in sdlc_md.artifact_files(type_, root):
            rec = sdlc_md.extract_record_id(path.stem)
            if not rec:
                continue
            key = sdlc_md.norm_id(rec)
            groups.setdefault(key, set()).add(str(path))
    duplicates = [
        {"id": key, "files": sorted(files)}
        for key, files in sorted(groups.items())
        if len(files) > 1
    ]
    return {"duplicates": duplicates, "count": len(duplicates)}


def cmd_collisions(args: argparse.Namespace) -> int:
    """Report duplicate artifact IDs; exit non-zero if any are found."""
    repo_root = Path(args.root).resolve()
    result = detect_collisions(repo_root)
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        for group in result["duplicates"]:
            print(f"{group['id']}:")
            for path in group["files"]:
                print(f"  {path}")
        if result["count"]:
            print(
                f"# {result['count']} duplicate ID(s)", file=sys.stderr
            )
        else:
            print("# no duplicate IDs", file=sys.stderr)
    return 1 if result["count"] else 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser for allocate and scan."""
    p = argparse.ArgumentParser(
        prog="next_id.py",
        description="Allocate the next free sdlc-studio artifact ID.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    types = sorted({*sdlc_md.ARTIFACT_TYPES, *META_TYPES})

    a = sub.add_parser("allocate", help="Print the next free ID for a type.")
    a.add_argument("--type", required=True, choices=types)
    a.add_argument("--remote", action="store_true",
                   help="Also consider origin/main (read-only git ls-tree, no fetch)")
    a.add_argument("--root", default=".", help="Repo root (default: .)")
    a.add_argument("--format", choices=("text", "json"), default="text")
    a.set_defaults(func=cmd_allocate)

    s = sub.add_parser("scan", help="List all IDs used for a type.")
    s.add_argument("--type", required=True, choices=types)
    s.add_argument("--root", default=".", help="Repo root (default: .)")
    s.add_argument("--format", choices=("text", "json"), default="text")
    s.set_defaults(func=cmd_scan)

    c = sub.add_parser(
        "collisions",
        help="Flag any normalised ID claimed by more than one file.",
    )
    c.add_argument("--root", default=".", help="Repo root (default: .)")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_collisions)

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
