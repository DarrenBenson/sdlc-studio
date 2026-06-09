#!/usr/bin/env python3
"""SDLC Studio artifact-ID allocator.

Deterministically pick the next free artifact number for a type, so Claude
never has to scan files and guess (doctrine rule 13: cross-repo numbering).
Scans local files and, with --remote, the highest number already on
`origin/main` (read-only `git ls-tree`, no fetch - the caller fetches first).

Subcommands:
  allocate  Print the next free ID for a type.
  scan      List every ID currently used for a type.

Output: text (the ID) by default, or JSON with --format json.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402


def local_ids(type_: str, repo_root: Path) -> list[int]:
    """Numeric IDs of all local artifact files of `type_`."""
    ids: list[int] = []
    for path in sdlc_md.artifact_files(type_, repo_root):
        rec = sdlc_md.extract_record_id(path.stem)
        num = sdlc_md.id_number(rec) if rec else None
        if num is not None:
            ids.append(num)
    return sorted(set(ids))


def remote_ids(type_: str, repo_root: Path) -> tuple[list[int], bool]:
    """Numeric IDs on origin/main for `type_`. Returns (ids, available).

    Uses `git ls-tree` (read-only, no network). `available` is False when the
    repo has no origin/main or git is unavailable.
    """
    rel, prefix = sdlc_md.ARTIFACT_TYPES[type_]
    try:
        result = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", "origin/main", "--", rel],
            capture_output=True, text=True, cwd=str(repo_root), check=False,
        )
    except FileNotFoundError:
        return [], False
    if result.returncode != 0:
        return [], False
    ids: list[int] = []
    for line in result.stdout.splitlines():
        stem = Path(line).stem
        rec = sdlc_md.extract_record_id(stem)
        num = sdlc_md.id_number(rec) if rec else None
        if num is not None:
            ids.append(num)
    return sorted(set(ids)), True


def cmd_allocate(args: argparse.Namespace) -> int:
    """Print the next free ID for a type."""
    type_ = args.type
    repo_root = Path(args.root).resolve()
    prefix = sdlc_md.ARTIFACT_TYPES[type_][1]
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
    prefix = sdlc_md.ARTIFACT_TYPES[type_][1]
    local = local_ids(type_, repo_root)
    ids = [f"{prefix}{n:04d}" for n in local]
    if args.format == "json":
        print(json.dumps({"type": type_, "ids": ids, "count": len(ids)}, indent=2))
    else:
        for i in ids:
            print(i)
        print(f"# {len(ids)} {type_}(s)", file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser for allocate and scan."""
    p = argparse.ArgumentParser(
        prog="next_id.py",
        description="Allocate the next free sdlc-studio artifact ID.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    types = sorted(sdlc_md.ARTIFACT_TYPES)

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
