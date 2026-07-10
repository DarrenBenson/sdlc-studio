#!/usr/bin/env python3
"""SDLC Studio schema v2 -> v3 migration.

Rewrites a workspace's sequential ids (`BG0001`) to type-prefixed short ULIDs
(`BG-01JQK3F8`), preserving creation order (the ULID timestamp is derived from
each file's date, so a directory listing keeps sorting as before). The old id is
retained as an alias in the artefact's metadata (`> **Aliases:** BG0001`) and
every intra-workspace link is rewritten to the new id, so nothing dangles.

Deterministic, dry-run-first, and idempotent: an already-migrated file (its id is
already a ULID) is skipped, so a second run is a no-op. The id map is journalled to
`sdlc-studio/.local/migrate-map.json` before the first write; an interrupted apply
resumes from that SAVED map (never a fresh plan, which would cross-wire identities),
and the journal comes off only when the migration is durable.

    migrate_v3.py plan            # preview the id map, write nothing
    migrate_v3.py apply           # perform the migration
    migrate_v3.py apply --root .  # explicit root

A completed `apply` stamps `schema_version: 3` into the workspace config itself,
so new artefacts mint ULIDs from the very next filing - the era flip is never a
manual step a walk can forget.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import reconcile  # noqa: E402


def _git_add_epochs(repo_root: Path) -> dict[str, int]:
    """Map path (relative to `repo_root`) -> first-add commit epoch (ms) from ONE `git log` pass
    over the tree - this replaces a `git log --follow` per artefact, which does not scale to a
    large project. `--reverse` walks oldest-first so the first time a path appears as added wins;
    `--relative` makes paths relative to `repo_root` even when it is a subdir of the git repo.
    Empty on any git failure (callers fall back to mtime)."""
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--reverse", "--format=@%at", "--name-only",
             "--relative"],
            cwd=str(repo_root), capture_output=True, text=True, timeout=120, check=False).stdout
    except (OSError, subprocess.SubprocessError):
        return {}
    epochs: dict[str, int] = {}
    cur: int | None = None
    for line in out.splitlines():
        if line.startswith("@"):
            try:
                cur = int(line[1:]) * 1000
            except ValueError:
                cur = None
        elif line and cur is not None:
            epochs.setdefault(line, cur)  # first add wins (oldest, via --reverse)
    return epochs


def _mtime_ms(path: Path) -> int:
    """Filesystem-mtime ordering key (ms), the fallback when git has no add-date for a file."""
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
    add_epochs = _git_add_epochs(root)  # one git pass for every file's add-date
    entries = []
    for type_ in sdlc_md.ARTIFACT_TYPES:
        for p in sdlc_md.artifact_files(type_, root):
            rec = sdlc_md.extract_record_id(p.stem)
            if not rec or _is_v3(rec):
                continue
            try:
                rel = p.resolve().relative_to(root.resolve()).as_posix()
            except ValueError:
                rel = None
            ms = add_epochs.get(rel) if rel is not None else None
            entries.append((ms if ms is not None else _mtime_ms(p), rec, type_, p))
    entries.sort(key=lambda e: (e[0], sdlc_md.norm_id(e[1])))  # stable creation order
    cw = _counter_width(len(entries))  # scale the counter so it never wraps past the file count
    id_map: dict[str, dict] = {}
    minted: set[str] = set()
    for i, (ms, rec, type_, p) in enumerate(entries):
        prefix = sdlc_md.ARTIFACT_TYPES[type_][1]
        # timestamp field from the file's date (sortable) + a monotonic per-file counter as the
        # low bits, so ids are unique AND keep date order without depending on wall-clock now.
        # The counter width scales with the entry count: a fixed 2-char (10-bit) counter wrapped
        # at 1024 files and silently overwrote via rename - a fail-loud uniqueness check backs it.
        ts = sdlc_md.b32(ms & ((1 << 48) - 1), 10)
        suffix = ts[:6] + sdlc_md.b32(i, cw)
        new_id = f"{prefix}-{suffix}"
        if new_id in minted:
            raise RuntimeError(f"migrate_v3: id collision minting {new_id} for {rec} - refusing "
                               "to overwrite a file; report this (should be impossible post-fix)")
        minted.add(new_id)
        # strip the leading v2 id token from the slug so the stale number is not embedded:
        # `CR-0001-add-auth` -> `add-auth`, `US0001-login` -> `login`.
        slug = re.sub(r"^[A-Za-z]+-?\d+-", "", p.stem) or "x"
        id_map[rec] = {"new_id": new_id, "type": type_, "old_path": p,
                       "new_path": p.parent / f"{new_id}-{slug}.md"}
    return id_map


def _counter_width(n: int) -> int:
    """Crockford-base32 chars needed to encode indices 0..n-1 without wrap (min 2 for the
    compact short-id form). Each char holds 5 bits, so width = ceil(bits / 5)."""
    bits = max(1, (n - 1).bit_length()) if n > 1 else 1
    return max(2, -(-bits // 5))


def _rewrite_links(text: str, norm_to_new: dict[str, str]) -> str:
    """Replace every artefact-id reference in `text` with its migrated id (both the bare id and
    inside `(...-file.md)` link targets), keyed by normalised id so `CR-0001`/`CR0001` both hit.
    `> **Aliases:**` lines are never rewritten: the alias IS the old id, deliberately preserved -
    rewriting it on a resumed apply made every alias self-referential and lost the v2 identity."""
    def repl(m: re.Match) -> str:
        new = norm_to_new.get(sdlc_md.norm_id(m.group(0)))
        return new if new else m.group(0)
    # ID_SEARCH_RE matches the id token wherever it appears - a bare reference, a heading, or
    # the id half of a link filename stem - so one substitution fixes them all.
    out = []
    for line in text.splitlines(keepends=True):
        out.append(line if line.startswith("> **Aliases:**")
                   else sdlc_md.ID_SEARCH_RE.sub(repl, line))
    return "".join(out)


def _journal_path(root: Path) -> Path:
    """The persisted id-map journal for an in-flight apply. It exists from just before the
    first write until the migration completes; its presence means a prior apply was
    interrupted and the SAVED map (not a fresh plan) must drive the resume - re-planning
    from now-changed mtimes/order silently cross-wires identities."""
    return Path(root) / "sdlc-studio" / ".local" / "migrate-map.json"


def _save_journal(root: Path, id_map: dict[str, dict]) -> None:
    root = Path(root).resolve()
    data = {old: {"new_id": e["new_id"], "type": e["type"],
                  "old_rel": e["old_path"].resolve().relative_to(root).as_posix(),
                  "new_rel": e["new_path"].resolve().relative_to(root).as_posix()}
            for old, e in id_map.items()}
    sdlc_md.atomic_write(_journal_path(root), json.dumps(data, indent=2))


def _load_journal(root: Path) -> dict[str, dict] | None:
    """The saved id map of an interrupted apply, rehydrated - or None when no apply is in
    flight. A journal that exists but cannot be parsed fails LOUD: silently re-planning over
    a half-renamed workspace is the data-loss path this journal exists to close."""
    jp = _journal_path(root)
    if not jp.exists():
        return None
    try:
        data = json.loads(jp.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise ValueError(
            f"{jp} exists (an apply was interrupted) but cannot be parsed: {exc}. "
            "Repair or remove it only after checking which files were already renamed - "
            "do not re-run plan over a half-migrated workspace.") from exc
    root = Path(root)
    return {old: {"new_id": e["new_id"], "type": e["type"],
                  "old_path": root / e["old_rel"], "new_path": root / e["new_rel"]}
            for old, e in data.items()}


def _stamp_schema_v3(root: Path) -> None:
    """Set `schema_version: 3` in the workspace config (create the file if absent, replace the
    line if present, preserve everything else). Apply must flip the era itself: left manual,
    the next filing mints a numeric id that collides with a live `Aliases:` line."""
    cfg = root / "sdlc-studio" / ".config.yaml"
    if cfg.exists():
        text = cfg.read_text(encoding="utf-8")
        if re.search(r"(?m)^schema_version:", text):
            text = re.sub(r"(?m)^schema_version:.*$", "schema_version: 3", text, count=1)
        else:
            text = text.rstrip("\n") + "\nschema_version: 3\n"
    else:
        text = "schema_version: 3\n"
    sdlc_md.atomic_write(cfg, text)


def migrate(repo_root: Path | str, dry_run: bool = True) -> dict:
    """Perform (or preview) the v2 -> v3 migration. Returns a summary dict. An interrupted
    apply leaves a journal; the next run (plan or apply) resumes from the SAVED map."""
    root = Path(repo_root)
    journal = _load_journal(root)
    resume = journal is not None
    id_map = journal if resume else build_id_map(root)
    norm_to_new = {sdlc_md.norm_id(old): e["new_id"] for old, e in id_map.items()}
    summary = {"migrated": len(id_map), "dry_run": dry_run, "resume": resume,
               "map": {old: e["new_id"] for old, e in id_map.items()}}
    if dry_run:
        return summary
    if not id_map:
        # nothing left to rename (already-migrated workspace): still make the era stamp true
        # before returning, so a completed apply always leaves a v3 project
        _stamp_schema_v3(root)
        summary["schema_stamped"] = True
        return summary
    # 0. Persist the id map BEFORE any write - a crash at any later point resumes from this
    #    journal instead of re-planning over a half-rewritten workspace.
    if not resume:
        _save_journal(root, id_map)
    # 1. Rewrite every intra-workspace id reference (bodies, headings, link stems) FIRST, while
    #    files still have their old names - so a file's own heading/links become the new id.
    #    (No-op on a resume whose rewrite already completed: the old ids are gone.)
    for md in (root / "sdlc-studio").rglob("*.md"):
        original = md.read_text(encoding="utf-8")
        rewritten = _rewrite_links(original, norm_to_new)
        if rewritten != original:
            sdlc_md.atomic_write(md, rewritten)
    # 2. Add the alias line (the OLD id, recorded AFTER the rewrite so it is not itself
    #    rewritten) and rename each artefact file to its new id. On a resume, a file already
    #    renamed is done; a file missing from BOTH names is corruption - fail loud.
    for old, e in id_map.items():
        if not e["old_path"].exists():
            if e["new_path"].exists():
                continue  # this entry completed before the interruption
            raise FileNotFoundError(
                f"partial migration: {old} is at neither {e['old_path'].name} nor "
                f"{e['new_path'].name} - repair by hand before re-running apply")
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
    for type_ in reconcile.DEFAULT_TYPES:
        reconcile.apply_type(type_, root)
    # 4. Flip the era: new artefacts must mint ULIDs from the very next filing.
    _stamp_schema_v3(root)
    # 5. The migration is durable - only now does the journal come off.
    _journal_path(root).unlink(missing_ok=True)
    summary["schema_stamped"] = True
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
        if res.get("resume"):
            verb = f"RESUMING an interrupted apply from the journal - {verb}"
        print(f"{verb} {res['migrated']} artefact(s) to schema v3")
        for old, new in list(res["map"].items())[:20]:
            print(f"  {old} -> {new}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
