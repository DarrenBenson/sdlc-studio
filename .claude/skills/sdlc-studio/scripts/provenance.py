#!/usr/bin/env python3
"""Artifact provenance: stamp check + remake backfill.

Makes deterministic creation the *checkable* path. `new` stamps every artifact it
creates (`> **Created-by:** sdlc-studio ...`); this module:
  check    flags artifacts past the adoption cutoff that LACK the stamp (hand-authored),
           with remediation. Advisory by default; `provenance.enforce: true` makes it block.
           `provenance.adopt_after` (per-type id cutoff) exempts legacy artifacts. An
           artifact it cannot read is reported blocking in either mode: unjudged, not clean.
  remake   content-preservingly backfills the stamp into un-stamped artifacts (idempotent,
           dry-run-able). Stamp-backfill only - it never re-lays-out content (no loss risk).
           Names every file it could not read or write, and exits 1 rather than printing a
           count that reads as a complete backfill.

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
# ANY non-empty Created-by is provenance - a field report or human attribution
# counts. Tool-stamping is how `new` records itself, not the only valid value;
# treating a non-tool value as absent made check nag forever and remake append
# a SECOND Created-by line beside the human one.
_PROVENANCE_RE = re.compile(r"(?im)^\s*>\s*\*\*Created-by:\*\*\s*\S")
_STAMP = "> **Created-by:** sdlc-studio remake (backfilled)"


def has_stamp(text: str) -> bool:
    return bool(_STAMP_RE.search(text or ""))


def has_provenance(text: str) -> bool:
    """True when the artifact carries ANY non-empty Created-by header field."""
    return bool(_PROVENANCE_RE.search(text or ""))


def _truthy(v) -> bool:
    return str(v).strip().lower() in ("true", "1", "yes", "on")


def _add_stamp(text: str) -> tuple[str, bool]:
    """Insert the stamp into the HEADER metadata blockquote ONLY (the contiguous `>` run
    immediately after the H1, allowing blanks between). Never scans the body, so a prose
    blockquote / HTML comment / table cannot be corrupted. Content-preserving; idempotent.
    An existing Created-by of ANY value is provenance - never add a second line."""
    if has_provenance(text):
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
        # Consume the (path, text) pairs rather than re-reading: iter_artifact_files
        # yields an unreadable or non-UTF-8 artifact as (path, None) precisely so a
        # checker can NAME it. Re-reading here swallowed the OSError and reported the
        # file clean, and crashed outright on a non-UTF-8 one.
        for p, text in sdlc_md.iter_artifact_files(t, root):
            aid = p.stem.split("-")[0]
            idn = sdlc_md.id_number(aid) or 0  # number is in the id prefix, not the slug
            if idn <= cutoff:  # legacy, pre-adoption: exempt
                continue
            if text is None:
                # Never judged, so never clean. Blocking whatever `enforce` says: that
                # toggle governs whether MISSING provenance blocks, not whether an
                # unjudgeable file counts as a pass.
                findings.append({"id": aid, "type": t, "kind": "unreadable",
                                 "blocking": True,
                                 "detail": f"{aid} could not be read as UTF-8 text "
                                           f"({p}) - provenance was not judged"})
            elif not has_provenance(text):
                findings.append({"id": aid, "type": t, "kind": "no-provenance",
                                 "blocking": enforce,
                                 "detail": f"{aid} carries no Created-by "
                                           "provenance - recreate with `new` or run `remake`"})
    return {"findings": findings, "enforced": enforce,
            "ok": not any(f["blocking"] for f in findings)}


def remake(repo_root: Path | str, types: list[str] | None = None, dry_run: bool = False,
           include_exempt: bool = False) -> dict:
    """Backfill the stamp into artifacts with no Created-by (idempotent,
    content-preserving). Honours the same `provenance.adopt_after` exemption as
    `check` - existing pre-adoption artifacts are exempt, not mass-stamped
    (reference-upgrade.md); `include_exempt` (CLI `--all`) backfills those too."""
    root = Path(repo_root)
    cutoff = 0 if include_exempt else \
        (sdlc_md.parse_cutoff(sdlc_md.project_override(root, "provenance.adopt_after")) or 0)
    changed, failed = [], []
    for t in (types or list(sdlc_md.ARTIFACT_TYPES)):
        for p, text in sdlc_md.iter_artifact_files(t, root):
            aid = p.stem.split("-")[0]
            idn = sdlc_md.id_number(aid) or 0
            if idn <= cutoff:  # legacy, pre-adoption: exempt (mirror check)
                continue
            if text is None:  # unreadable/non-UTF-8: name it, never skip it silently
                failed.append(aid)
                continue
            new_text, did = _add_stamp(text)
            if not did:
                continue
            if dry_run:
                changed.append(aid)
                continue
            try:  # a single unwritable file must not abort the whole backfill,
                p.write_text(new_text, encoding="utf-8")  # but it must be REPORTED -
                changed.append(aid)                       # a swallowed write left the
            except OSError:                               # run claiming a complete
                failed.append(aid)                        # backfill it did not do
    return {"changed": changed, "count": len(changed),
            "failed": failed, "dry_run": dry_run}


def cmd_check(args: argparse.Namespace) -> int:
    types = [args.type] if args.type else None
    r = check(args.root, types)
    if args.format == "json":
        print(json.dumps(r, indent=2))
    else:
        for f in r["findings"]:
            print(f"  [{'FAIL' if f['blocking'] else 'warn'}] {f['detail']}")
        # Count the two kinds apart: an unreadable artifact is not an un-stamped one,
        # and folding it into that total would hide it inside an advisory number.
        unreadable = sum(1 for f in r["findings"] if f["kind"] == "unreadable")
        print(f"provenance: {len(r['findings']) - unreadable} un-stamped "
              f"({'enforced' if r['enforced'] else 'advisory'})"
              + (f", {unreadable} unreadable (not judged)" if unreadable else ""))
    return 0 if r["ok"] else 1


def cmd_remake(args: argparse.Namespace) -> int:
    types = [args.type] if args.type else None
    r = remake(args.root, types, args.dry_run, include_exempt=args.all)
    verb = "would stamp" if args.dry_run else "stamped"
    if args.format == "json":
        print(json.dumps(r, indent=2))
    else:
        print(f"{verb} {r['count']} artifact(s): {', '.join(r['changed']) or '(none)'}")
        if r["failed"]:  # a partial backfill must not read as a complete one
            print(f"  [FAIL] {len(r['failed'])} not stamped (unreadable or unwritable): "
                  f"{', '.join(r['failed'])}")
    return 1 if r["failed"] else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Artifact provenance check + remake.")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Flag un-stamped artifacts past the adoption cutoff.")
    c.add_argument("--type"); c.add_argument("--root", default=".")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_check)
    r = sub.add_parser("remake", help="Backfill the provenance stamp (content-preserving).")
    r.add_argument("--type"); r.add_argument("--dry-run", action="store_true")
    r.add_argument("--all", action="store_true",
                   help="also backfill artifacts the provenance.adopt_after cutoff exempts")
    r.add_argument("--root", default="."); r.add_argument("--format", choices=("text", "json"), default="text")
    r.set_defaults(func=cmd_remake)
    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Resolve the root ONCE and write it back, so every verb below anchors on the tree the
    # run belongs to. The family default `.` means "work it out from here", not "the cwd
    # is the project": otherwise a run from a subdirectory acts on a stray tree and exits 0.
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
