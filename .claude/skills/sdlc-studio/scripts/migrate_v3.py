#!/usr/bin/env python3
"""SDLC Studio schema v2 -> v3 migration.

Rewrites a workspace's sequential ids (`BG0001`) to type-prefixed short ULIDs
(`BG-01JQK3F8`), preserving creation order (the ULID timestamp is derived from
each file's date, so a directory listing keeps sorting as before). The old id is
retained as an alias in the artefact's metadata (`> **Aliases:** BG0001`) and
every intra-workspace link is rewritten to the new id, so nothing dangles.

Deterministic, dry-run-first, and idempotent: an already-migrated file (its id is
already a ULID) is skipped, so a second run is a no-op.

    migrate_v3.py plan            # preview the id map, write nothing
    migrate_v3.py apply           # perform the migration
    migrate_v3.py apply --root .  # explicit root

After `apply`, the config's `schema_version` should be set to 3 so new artefacts
mint ULIDs too.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import reconcile  # noqa: E402


def _file_epoch_ms(path: Path) -> int:
    """A stable creation-ordering timestamp (ms). Prefers the file's first git commit date
    for determinism; falls back to the filesystem mtime when git is unavailable."""
    import subprocess
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--follow", "--format=%at", "-1", "--", str(path)],
            cwd=str(path.parent), capture_output=True, text=True, timeout=10, check=False).stdout.strip()
        if out:
            return int(out.splitlines()[-1]) * 1000
    except (OSError, ValueError, subprocess.SubprocessError):
        pass
    try:
        return int(path.stat().st_mtime * 1000)
    except OSError:
        return 0


def _is_v3(record_id: str) -> bool:
    """True when an id is already the v3 ULID form (has no v2 sequential number)."""
    return sdlc_md.id_number(record_id) is None


def build_id_map(repo_root: Path | str) -> dict[str, dict]:
    """Map each v2 artefact id -> {new_id, old_path, new_path, type}. Files already on v3 are
    omitted (nothing to do). Order-preserving: ULIDs are minted with a timestamp derived from
    each file's date, in date order, so lexical id order equals creation order."""
    root = Path(repo_root)
    entries = []
    for type_ in sdlc_md.ARTIFACT_TYPES:
        for p in sdlc_md.artifact_files(type_, root):
            rec = sdlc_md.extract_record_id(p.stem)
            if not rec or _is_v3(rec):
                continue
            entries.append((_file_epoch_ms(p), rec, type_, p))
    entries.sort(key=lambda e: (e[0], sdlc_md.norm_id(e[1])))  # stable creation order
    id_map: dict[str, dict] = {}
    for i, (ms, rec, type_, p) in enumerate(entries):
        prefix = sdlc_md.ARTIFACT_TYPES[type_][1]
        # timestamp field from the file's date (sortable) + a monotonic per-file counter as the
        # low bits, so ids are unique AND keep date order without depending on wall-clock now.
        ts = sdlc_md._b32(ms & ((1 << 48) - 1), 10)
        suffix = ts[:6] + sdlc_md._b32(i, 2)  # 8-char short id, deterministic and ordered
        new_id = f"{prefix}-{suffix}"
        slug = p.stem.split("-", 1)[1] if "-" in p.stem else "x"
        id_map[rec] = {"new_id": new_id, "type": type_, "old_path": p,
                       "new_path": p.parent / f"{new_id}-{slug}.md"}
    return id_map


def _rewrite_links(text: str, norm_to_new: dict[str, str]) -> str:
    """Replace every artefact-id reference in `text` with its migrated id (both the bare id and
    inside `(...-file.md)` link targets), keyed by normalised id so `CR-0001`/`CR0001` both hit."""
    def repl(m: re.Match) -> str:
        new = norm_to_new.get(sdlc_md.norm_id(m.group(0)))
        return new if new else m.group(0)
    # ID_SEARCH_RE matches the id token wherever it appears - a bare reference, a heading, or
    # the id half of a link filename stem - so one substitution fixes them all.
    return sdlc_md.ID_SEARCH_RE.sub(repl, text)


def migrate(repo_root: Path | str, dry_run: bool = True) -> dict:
    """Perform (or preview) the v2 -> v3 migration. Returns a summary dict."""
    root = Path(repo_root)
    id_map = build_id_map(root)
    norm_to_new = {sdlc_md.norm_id(old): e["new_id"] for old, e in id_map.items()}
    summary = {"migrated": len(id_map), "dry_run": dry_run,
               "map": {old: e["new_id"] for old, e in id_map.items()}}
    if dry_run or not id_map:
        return summary
    # 1. Rewrite every intra-workspace id reference (bodies, headings, link stems) FIRST, while
    #    files still have their old names - so a file's own heading/links become the new id.
    for md in (root / "sdlc-studio").rglob("*.md"):
        original = md.read_text(encoding="utf-8")
        rewritten = _rewrite_links(original, norm_to_new)
        if rewritten != original:
            sdlc_md.atomic_write(md, rewritten)
    # 2. Add the alias line (the OLD id, recorded AFTER the rewrite so it is not itself
    #    rewritten) and rename each artefact file to its new id.
    for old, e in id_map.items():
        text = e["old_path"].read_text(encoding="utf-8")
        if sdlc_md.extract_field(text, "Aliases") is None:
            new_text = re.sub(r"(^> \*\*Created-by:\*\*.*$)",
                              r"\1\n> **Aliases:** " + old, text, count=1, flags=re.MULTILINE)
            if new_text == text:  # no Created-by line: place it right after the H1
                new_text = re.sub(r"(^# .*$)", r"\1\n\n> **Aliases:** " + old, text,
                                  count=1, flags=re.MULTILINE)
            text = new_text
        e["old_path"].write_text(text, encoding="utf-8")
        e["old_path"].rename(e["new_path"])
    # 3. Regenerate index counts from the migrated census.
    for type_ in reconcile._DEFAULT_TYPES:
        reconcile.apply_type(type_, root)
    return summary


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="migrate_v3.py", description="Migrate a workspace v2 -> v3 (ULID ids).")
    p.add_argument("cmd", choices=["plan", "apply"])
    p.add_argument("--root", default=".")
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args(argv)
    res = migrate(args.root, dry_run=(args.cmd == "plan"))
    if args.format == "json":
        print(json.dumps(res, indent=2))
    else:
        verb = "would migrate" if res["dry_run"] else "migrated"
        print(f"{verb} {res['migrated']} artefact(s) to schema v3")
        for old, new in list(res["map"].items())[:20]:
            print(f"  {old} -> {new}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
