#!/usr/bin/env python3
"""Artifact provenance: stamp check + remake backfill.

Makes deterministic creation the *checkable* path. `new` stamps every artifact it
creates (`> **Created-by:** sdlc-studio ...`); this module:
  check    flags artifacts past the adoption cutoff that LACK the stamp (hand-authored),
           with remediation. Advisory by default; `provenance.enforce: true` makes it block.
           `provenance.adopt_after` (per-type id cutoff) exempts legacy artifacts.
  remake   content-preservingly backfills the stamp into un-stamped artifacts (idempotent,
           dry-run-able). Stamp-backfill only - it never re-lays-out content (no loss risk).

Standalone + advisory by design: it is NOT wired into the gate, so adopting it is a project
choice (set `provenance.enforce` to gate on it). Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

# Line-anchored: the stamp must be on a `>` metadata line, so a prose mention of
# "Created-by: sdlc-studio" (e.g. this CR's own artifact) is not a false match.
_STAMP_RE = re.compile(r"(?im)^\s*>\s*\*\*Created-by:\*\*\s*sdlc-studio")
_STAMP = "> **Created-by:** sdlc-studio remake (backfilled)"


def has_stamp(text: str) -> bool:
    return bool(_STAMP_RE.search(text or ""))


def _truthy(v) -> bool:
    return str(v).strip().lower() in ("true", "1", "yes", "on")


def _add_stamp(text: str) -> tuple[str, bool]:
    """Insert the stamp into the HEADER metadata blockquote ONLY (the contiguous `>` run
    immediately after the H1, allowing blanks between). Never scans the body, so a prose
    blockquote / HTML comment / table cannot be corrupted. Content-preserving; idempotent."""
    if has_stamp(text):
        return text, False
    nl = "\n" if text.endswith("\n") else ""
    lines = text.splitlines()
    h1 = next((i for i, l in enumerate(lines) if l.lstrip().startswith("# ")), None)
    if h1 is None:  # no H1 - prepend the stamp safely
        return "\n".join([_STAMP, ""] + lines) + nl, True
    i = h1 + 1
    while i < len(lines) and lines[i].strip() == "":  # skip blanks after the H1
        i += 1
    if i < len(lines) and lines[i].lstrip().startswith(">"):
        last = i  # contiguous header metadata block - insert after its last line
        while last + 1 < len(lines) and lines[last + 1].lstrip().startswith(">"):
            last += 1
        lines.insert(last + 1, _STAMP)
    else:  # no header metadata block - normalise to: H1, blank, stamp, blank, <rest>
        rest = lines[h1 + 1:]
        while rest and rest[0].strip() == "":
            rest.pop(0)
        lines[h1 + 1:] = ["", _STAMP, ""] + rest
    return "\n".join(lines) + nl, True


def check(repo_root: Path | str, types: list[str] | None = None) -> dict:
    root = Path(repo_root)
    # Shared cutoff parser: accepts a bare int (57) or a prefixed id (US0057), and raises
    # loud on a typo rather than coercing to 0 and judging everything (lesson LL0008).
    # ids <= cutoff are legacy/exempt; None means no cutoff (judge all).
    cutoff = sdlc_md.parse_cutoff(sdlc_md.project_override(root, "provenance.adopt_after"))
    if cutoff is None:
        cutoff = 0
    enforce = _truthy(sdlc_md.project_override(root, "provenance.enforce", False))
    findings = []
    for t in (types or list(sdlc_md.ARTIFACT_TYPES)):
        for p in sdlc_md.artifact_files(t, root):
            idn = sdlc_md.id_number(p.stem.split("-")[0]) or 0  # number is in the id prefix, not the slug
            if idn <= cutoff:  # legacy, pre-adoption: exempt
                continue
            try:
                if not has_stamp(p.read_text(encoding="utf-8")):
                    findings.append({"id": p.stem.split("-")[0], "type": t, "kind": "no-provenance",
                                     "blocking": enforce,
                                     "detail": f"{p.stem.split('-')[0]} is not tool-stamped - "
                                               "recreate with `new` or run `remake`"})
            except OSError:
                continue
    return {"findings": findings, "enforced": enforce,
            "ok": not any(f["blocking"] for f in findings)}


def remake(repo_root: Path | str, types: list[str] | None = None, dry_run: bool = False) -> dict:
    """Backfill the stamp into un-stamped artifacts (idempotent, content-preserving)."""
    root = Path(repo_root)
    changed = []
    for t in (types or list(sdlc_md.ARTIFACT_TYPES)):
        for p in sdlc_md.artifact_files(t, root):
            try:
                text = p.read_text(encoding="utf-8")
            except OSError:
                continue
            new_text, did = _add_stamp(text)
            if not did:
                continue
            if dry_run:
                changed.append(p.stem.split("-")[0])
                continue
            try:  # a single unwritable file must not abort the whole backfill
                p.write_text(new_text, encoding="utf-8")
                changed.append(p.stem.split("-")[0])
            except OSError:
                continue
    return {"changed": changed, "count": len(changed), "dry_run": dry_run}


def cmd_check(args: argparse.Namespace) -> int:
    types = [args.type] if args.type else None
    r = check(args.root, types)
    if args.format == "json":
        print(json.dumps(r, indent=2))
    else:
        for f in r["findings"]:
            print(f"  [{'FAIL' if f['blocking'] else 'warn'}] {f['detail']}")
        print(f"provenance: {len(r['findings'])} un-stamped "
              f"({'enforced' if r['enforced'] else 'advisory'})")
    return 0 if r["ok"] else 1


def cmd_remake(args: argparse.Namespace) -> int:
    types = [args.type] if args.type else None
    r = remake(args.root, types, args.dry_run)
    verb = "would stamp" if args.dry_run else "stamped"
    print(json.dumps(r, indent=2) if args.format == "json"
          else f"{verb} {r['count']} artifact(s): {', '.join(r['changed']) or '(none)'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Artifact provenance check + remake.")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Flag un-stamped artifacts past the adoption cutoff.")
    c.add_argument("--type"); c.add_argument("--root", default=".")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_check)
    r = sub.add_parser("remake", help="Backfill the provenance stamp (content-preserving).")
    r.add_argument("--type"); r.add_argument("--dry-run", action="store_true")
    r.add_argument("--root", default="."); r.add_argument("--format", choices=("text", "json"), default="text")
    r.set_defaults(func=cmd_remake)
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
