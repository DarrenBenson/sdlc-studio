#!/usr/bin/env python3
"""SDLC Studio context tiering - summarised digests of closed artefacts.

Token cost creep is the silent failure mode: a long-lived repo pays a growing tax on every
status / planning pass that re-reads the whole corpus. This produces a mechanical (not
interpretive) digest of terminal artefacts - id, title, status, close outcome, and
cross-references - so planning and dedup reads can consume the digest instead of every
original. Originals are never summarised away; the digest is an access tier, drift-checked
like an index (mismatch vs the census -> regenerate).

    digest.py build              # write sdlc-studio/.local/digests.json
    digest.py build --format json

Once the closed-artefact count reaches `digests.min_closed` (default 500), `status`/`hint`
read a closed artefact's fields from the digest via `status_by_id` instead of opening every
original; below the threshold the feature is dormant (no digest read, no behaviour change).
The digest is byte-stable (sorted, deterministic) and `reconcile detect` flags it when it
drifts from the census, the same discipline as the progressive-disclosure indexes.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

DIGEST_REL = "sdlc-studio/.local/digests.json"
DEFAULT_MIN_CLOSED = 500


def min_closed(repo_root: Path | str) -> int:
    """The closed-artefact count at/above which digests are produced and read
    (`digests.min_closed`, default 500). Below it the feature is dormant."""
    try:
        return int(sdlc_md.project_override(repo_root, "digests.min_closed", DEFAULT_MIN_CLOSED))
    except (TypeError, ValueError):
        return DEFAULT_MIN_CLOSED


def load(repo_root: Path | str) -> dict | None:
    """The on-disk digest dict, or None when absent / unreadable."""
    p = Path(repo_root) / DIGEST_REL
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return None


def enabled(repo_root: Path | str) -> bool:
    """True when a digest exists on disk and its size reaches the threshold - the gate for the
    read-path optimisation. Below threshold (or no digest) the feature is dormant, so a small
    repo reads originals exactly as before (AC5: no behaviour change)."""
    d = load(repo_root)
    return bool(d) and d.get("count", 0) >= min_closed(repo_root)


def status_by_id(repo_root: Path | str) -> dict:
    """{normalised-id: status} for every digested closed artefact, or {} when the feature is
    dormant. Kept for id-oriented callers; the read-path optimisation uses `status_by_file`
    (filename-keyed, collision-safe against an id-sharing companion note)."""
    if not enabled(repo_root):
        return {}
    d = load(repo_root) or {}
    return {sdlc_md.norm_id(e["id"]): e.get("status", "") for e in d.get("digests", [])}


def status_by_file(repo_root: Path | str) -> dict:
    """{filename: status} for every digested closed artefact, or {} when the feature is dormant.
    Keyed by filename (not id) so a same-id companion note is never mistaken for the artefact.
    The read-path (`status`/`hint`) trusts these names and skips reading the original."""
    if not enabled(repo_root):
        return {}
    d = load(repo_root) or {}
    return {e["file"]: e.get("status", "") for e in d.get("digests", []) if e.get("file")}


def digest_artefact(path: Path, type_: str) -> dict:
    """A mechanical one-line-per-field digest of one artefact - enough for planning and dedup
    without opening the original. Field extraction only; no interpretation."""
    text = path.read_text(encoding="utf-8")
    rec = sdlc_md.extract_record_id(path.stem) or path.stem
    outcome = sdlc_md.extract_field(text, "Outcome") or sdlc_md.extract_field(text, "Close Reason")
    refs = sorted({m for m in sdlc_md.ID_SEARCH_RE.findall(text)
                   if sdlc_md.norm_id(m) != sdlc_md.norm_id(rec)})
    return {
        "id": rec,
        "type": type_,
        "file": path.name,
        "title": (sdlc_md.extract_h1_title(text) or "").split(":", 1)[-1].strip(),
        "status": sdlc_md.extract_field(text, "Status") or "",
        "outcome": (outcome or "").strip()[:200] or None,
        "refs": refs[:20],
    }


def build(repo_root: Path | str) -> dict:
    """Digest every terminal (closed) artefact. Returns {count, digests}."""
    root = Path(repo_root)
    digests = []
    for type_ in sdlc_md.ARTIFACT_TYPES:
        terminal = sdlc_md.terminal_statuses(type_)
        for p in sdlc_md.artifact_files(type_, root):
            status = sdlc_md.extract_field(p.read_text(encoding="utf-8"), "Status")
            if status and sdlc_md.canonical_status(status, sdlc_md.status_vocab(type_, root)) in terminal:
                digests.append(digest_artefact(p, type_))
    digests.sort(key=lambda dd: sdlc_md.norm_id(dd["id"]))
    return {"count": len(digests), "digests": digests}


def is_stale(repo_root: Path | str) -> bool:
    """True when the on-disk digest file does not match a freshly built one - the drift signal
    (a closed artefact added/changed since the digest was written). Missing file counts stale
    only if there is something to digest."""
    root = Path(repo_root)
    fresh = build(root)
    p = root / DIGEST_REL
    if not p.exists():
        return fresh["count"] > 0
    try:
        on_disk = json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return True
    return on_disk.get("digests") != fresh["digests"]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="digest.py", description="Build closed-artefact digests.")
    p.add_argument("cmd", choices=["build"])
    p.add_argument("--root", default=".")
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args(argv)
    res = build(args.root)
    out = Path(args.root) / DIGEST_REL
    sdlc_md.atomic_write(out, json.dumps(res, indent=2))
    if args.format == "json":
        print(json.dumps({"count": res["count"], "path": str(out)}, indent=2))
    else:
        print(f"digest: wrote {res['count']} closed-artefact digest(s) -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
