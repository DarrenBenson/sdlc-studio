#!/usr/bin/env python3
"""Backfill a structured `raised_by` reference onto artefacts that predate it.

The audit trail cannot be honestly rewritten later, so a v2 -> v3 project backfills authorship
once, inferring the author from the existing `Requester` / `Created-by` / revision-history
fields. An inferred attribution is marked `(inferred)` so it never masquerades as first-hand;
existing prose fields are left in place (the block is additive). Idempotent: an artefact that
already has a `Raised-by` line is skipped.

    backfill_authorship.py plan     # count what would change, write nothing
    backfill_authorship.py apply    # write the raised_by lines
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402


def _infer(text: str, root: Path) -> tuple[str, str]:
    """(name, type) inferred from an artefact's existing metadata. Prefers an explicit
    Requester / Created-by; falls back to the first revision-history author; defaults to a
    human placeholder. type is `persona` when the name resolves to a persona, else `human`."""
    for field in ("Requester", "Raised-by", "Created-by", "Author"):
        v = sdlc_md.extract_field(text, field)
        if v and v.strip() and v.strip() != "sdlc-studio new":
            name = re.split(r"[;,(]", v.strip())[0].strip()
            if name:
                return name, ("persona" if sdlc_md.resolve_author(name, "persona", root) else "human")
    # revision-history: first data row's Author cell
    for ln in text.splitlines():
        m = re.match(r"^\|\s*[\d-]{4,}\s*\|\s*([^|]+?)\s*\|", ln)
        if m and m.group(1).strip().lower() not in ("author", "---"):
            name = m.group(1).strip()
            return name, ("persona" if sdlc_md.resolve_author(name, "persona", root) else "human")
    return "unknown", "human"


def backfill(repo_root: Path | str, dry_run: bool = True) -> dict:
    root = Path(repo_root)
    changed = 0
    for type_ in sdlc_md.ARTIFACT_TYPES:
        for p in sdlc_md.artifact_files(type_, root):
            text = p.read_text(encoding="utf-8")
            if sdlc_md.extract_field(text, "Raised-by") is not None:
                continue  # already has structured authorship
            name, atype = _infer(text, root)
            line = f"> **Raised-by:** {name}; {atype}; v1 (inferred)"
            changed += 1
            if not dry_run:
                new = re.sub(r"(^> \*\*(?:Created-by|Status):\*\*.*$)",
                             r"\1\n" + line, text, count=1, flags=re.MULTILINE)
                if new == text:  # no anchor line: after the H1
                    new = re.sub(r"(^# .*$)", r"\1\n\n" + line, text, count=1, flags=re.MULTILINE)
                sdlc_md.atomic_write(p, new)
    return {"backfilled": changed, "dry_run": dry_run}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="backfill_authorship.py",
                                description="Backfill structured raised_by onto artefacts.")
    p.add_argument("cmd", choices=["plan", "apply"])
    p.add_argument("--root", default=".")
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args(argv)
    res = backfill(args.root, dry_run=(args.cmd == "plan"))
    if args.format == "json":
        print(json.dumps(res, indent=2))
    else:
        verb = "would backfill" if res["dry_run"] else "backfilled"
        print(f"{verb} raised_by on {res['backfilled']} artefact(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
