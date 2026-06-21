#!/usr/bin/env python3
"""PVD projection + drift check (CR0048, RFC0015 WS2).

Project the one writable master Product Vision Document into each child repo **read-only**
(a symlink in production, a synced copy in dev) and detect when a project's copy has drifted
from - or fallen behind - the master (sha256 + version). The master has one writable home
(the product/anchor repo); children never edit their copy.

Subcommands:
  sync    Project the master into a target repo's sdlc-studio/product/pvd.md (read-only).
  drift   Compare a target's copy against the master (in-sync / stale / missing).
  sync-all / drift-all   Apply across the repos listed in a product manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path

PROJECTED = Path("sdlc-studio") / "product" / "pvd.md"
_VERSION = re.compile(r"^>?\s*\*\*Version:\*\*\s*(\S+)", re.M)


def checksum(path: Path) -> str | None:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def _version(text: str) -> str | None:
    m = _VERSION.search(text or "")
    return m.group(1) if m else None


def sync(master: Path, target_repo: Path, mode: str = "copy", dry_run: bool = False) -> dict:
    """Project master -> <target_repo>/sdlc-studio/product/pvd.md, read-only.
    mode 'copy' writes a chmod-readonly copy (dev); 'symlink' links to the master (prod)."""
    master = Path(master)
    dest = Path(target_repo) / PROJECTED
    if dry_run:  # preview: write nothing (CR0057)
        return {"action": "would-sync", "target": str(dest), "mode": mode, "dry_run": True}
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() or dest.is_symlink():
        try:
            dest.chmod(stat.S_IWUSR | stat.S_IRUSR)  # make writable so we can replace
        except OSError:
            pass
        dest.unlink()
    if mode == "symlink":
        dest.symlink_to(master.resolve())
    else:
        dest.write_bytes(master.read_bytes())
        dest.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)  # read-only (0444)
    return {"action": "synced", "target": str(dest), "mode": mode}


def drift(master: Path, target: Path) -> dict:
    """Status of a projected copy vs the master: in-sync / stale / behind / missing."""
    master, target = Path(master), Path(target)
    mc = checksum(master)
    if mc is None:  # master unreadable/missing - never report a vacuous in-sync
        return {"status": "error", "target": str(target), "detail": "master unreadable/missing"}
    if not target.exists():
        return {"status": "missing", "target": str(target)}
    tc = checksum(target)
    if tc is None:  # target exists but unreadable - drifted, not in-sync
        return {"status": "stale", "target": str(target), "detail": "target unreadable"}
    if mc == tc:
        return {"status": "in-sync", "target": str(target)}
    mv, tv = _version(master.read_text(encoding="utf-8")), _version(target.read_text(encoding="utf-8"))
    # "behind" = the master moved on (different version); "stale" = same version, content differs
    status = "behind" if (mv and tv and mv != tv) else "stale"
    return {"status": status, "target": str(target), "master_version": mv, "target_version": tv}


def read_manifest(path: Path) -> dict:
    """Best-effort parse of product-manifest.yaml (master_pvd + repos[].path) without a
    hard PyYAML dependency."""
    text = Path(path).read_text(encoding="utf-8")
    master = None
    repos: list[dict] = []
    cur: dict | None = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#") or not s:
            continue
        m = re.match(r"master_pvd:\s*(\S+)", s)
        if m:
            master = m.group(1)
            continue
        if s.startswith("- id:"):
            cur = {"id": s.split(":", 1)[1].partition("#")[0].strip()}  # strip inline comment
            repos.append(cur)
        elif cur is not None and ":" in s:
            k, _, v = s.partition(":")
            cur[k.strip()] = v.partition("#")[0].strip()  # strip inline comment
    return {"master_pvd": master, "repos": repos}


def cmd_sync(args: argparse.Namespace) -> int:
    print(json.dumps(sync(args.master, args.target, args.mode,
                          dry_run=getattr(args, "dry_run", False)), indent=2))
    return 0


def cmd_drift(args: argparse.Namespace) -> int:
    r = drift(args.master, args.target)
    print(json.dumps(r, indent=2) if args.format == "json"
          else f"{r['status']}: {r['target']}")
    return 0 if r["status"] == "in-sync" else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="PVD projection + drift (CR0048).")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sync", help="Project the master into a target repo, read-only.")
    s.add_argument("--master", required=True)
    s.add_argument("--target", required=True, help="Target repo root")
    s.add_argument("--mode", choices=("copy", "symlink"), default="copy")
    s.add_argument("--dry-run", action="store_true", dest="dry_run", help="preview; write nothing")
    s.set_defaults(func=cmd_sync)
    d = sub.add_parser("drift", help="Compare a projected copy vs the master.")
    d.add_argument("--master", required=True)
    d.add_argument("--target", required=True, help="The projected pvd.md")
    d.add_argument("--format", choices=("text", "json"), default="text")
    d.set_defaults(func=cmd_drift)
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
