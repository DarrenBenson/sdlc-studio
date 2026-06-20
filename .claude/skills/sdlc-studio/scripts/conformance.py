#!/usr/bin/env python3
"""SDLC Studio lifecycle-conformance check (RFC0001 WS7).

Asserts each unit (story) passed through the required lifecycle stages -
decomposed (an Epic link), specified (at least one AC), verifiable (a `Verify:`
line), and for Done stories verified (AC marked `Verified: yes/manual`). Exits
non-zero on any non-conformant unit, so the autosprint loop cannot mark a unit
Done with a stage silently skipped. Read-only over the workspace; pure stdlib.

The reconciled and reviewed stages are layered in later; this v1 covers the
structural core that the loop produces per story.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402


def detect_conformance(repo_root: Path | str) -> dict:
    """Per-story lifecycle conformance.

    Returns {"units": [{id, type, status, stages, conformant, missing}],
    "summary": {total, conformant, nonconformant}}. A story is conformant when
    every required stage for its status is present.
    """
    root = Path(repo_root)
    vocab = sdlc_md.STATUS_VOCAB.get("story", [])
    units: list[dict] = []
    ok = 0
    for path in sdlc_md.artifact_files("story", root):
        text = path.read_text(encoding="utf-8")
        rid = sdlc_md.extract_record_id(path.stem) or path.stem
        status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab) or "Unknown"
        decomposed = sdlc_md.extract_field(text, "Epic") is not None
        has_ac = has_verify = False
        verified_states: list[str] = []
        for line in text.splitlines():
            if sdlc_md.AC_HEADING_RE.match(line) or sdlc_md.AC_BULLET_RE.match(line):
                has_ac = True
            if sdlc_md.VERIFY_RE.match(line):
                has_verify = True
            m = sdlc_md.VERIFIED_RE.match(line)
            if m:
                verified_states.append(m.group(2).lower())
        verified = None
        if status == "Done":
            verified = bool(verified_states) and all(v in ("yes", "manual") for v in verified_states)
        stages = {
            "decomposed": decomposed,
            "specified": has_ac,
            "verifiable": has_verify,
            "verified": verified,
        }
        required = ["decomposed", "specified", "verifiable"]
        if status == "Done":
            required.append("verified")
        missing = [s for s in required if not stages[s]]
        conformant = not missing
        ok += int(conformant)
        units.append({
            "id": rid,
            "type": "story",
            "status": status,
            "stages": stages,
            "conformant": conformant,
            "missing": missing,
        })
    units.sort(key=lambda u: u["id"])
    total = len(units)
    return {
        "generated_at": sdlc_md.now_iso8601(),
        "units": units,
        "summary": {"total": total, "conformant": ok, "nonconformant": total - ok},
    }


def cmd_check(args: argparse.Namespace) -> int:
    """Run the conformance check; exit non-zero if any unit is non-conformant."""
    result = detect_conformance(args.root)
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        s = result["summary"]
        print(f"conformance: {s['conformant']}/{s['total']} conformant, {s['nonconformant']} not")
        for u in result["units"]:
            if not u["conformant"]:
                print(f"  {u['id']} ({u['status']}): missing {', '.join(u['missing'])}")
    return 1 if result["summary"]["nonconformant"] else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio lifecycle-conformance check.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Check each story passed the required lifecycle stages.")
    c.add_argument("--root", default=".", help="Repo root (default: .)")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_check)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
