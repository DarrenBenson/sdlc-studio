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

The read-path integration (status/hint reading digests) and the size threshold are the
remaining CR0179 workstream; this ships the deterministic generator and its drift check.
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
