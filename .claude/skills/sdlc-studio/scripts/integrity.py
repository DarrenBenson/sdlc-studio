#!/usr/bin/env python3
"""SDLC Studio referential-integrity check.

Two deterministic guards `validate.py` does not cover:

- **required-link presence** - per the reference-outputs.md matrix (Epic in
  Story/Plan/Bug/TestSpec/Workflow; Story in Plan/Bug/TestSpec/Workflow). A missing
  required link on an *active* (non-terminal) artifact is an error; on a terminal
  artifact it is advisory (historical, not worth blocking on).
- **dangling references** - each ID referenced in a link field is resolved via
  `norm_id` against the on-disk census; an unresolved reference is advisory.

Emits JSON findings; exits non-zero only when an active artifact is missing a
required link. Read-only; pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

# Required link fields per artifact type (reference-outputs.md link matrix).
REQUIRED_LINKS = {
    "story": ["Epic"],
    "plan": ["Epic", "Story"],
    "bug": ["Epic", "Story"],
    # Epic only: a test-spec always carries an Epic but may be story- or epic-scoped
    # (reference-test-spec.md#epic-scoped-coverage), so Story cannot be required. BG0038.
    "test-spec": ["Epic"],
    "workflow": ["Epic", "Story"],
}

# Terminal statuses across all vocabularies - a missing link here is historical.
TERMINAL = {
    "Done", "Complete", "Superseded", "Won't Implement", "Won't Fix",
    "Deferred", "Rejected", "Withdrawn", "Closed", "Fixed", "Verified",
}

# Types whose links are recommended, not required: a bug is often filed pre-triage
# with no epic/story, so a missing link is advisory at any status, never an error.
LINK_OPTIONAL = {"bug"}

# A field carrying one of these placeholders declares "no link" - treated as absent,
# so `Epic: --` on an active story is caught, not waved through.
_BLANK = {"", "--", "—", "-", "tbd", "n/a", "na", "none"}


def _is_blank(val: str | None) -> bool:
    return val is None or val.strip().lower() in _BLANK


def _census(root: Path) -> set[str]:
    """Every artifact ID on disk, normalised for comparison."""
    ids: set[str] = set()
    for type_ in sdlc_md.ARTIFACT_TYPES:
        for path in sdlc_md.artifact_files(type_, root):
            rec = sdlc_md.extract_record_id(path.stem)
            if rec:
                ids.add(sdlc_md.norm_id(rec))
    return ids


def detect_integrity(repo_root: Path | str) -> dict:
    """Required-link presence + dangling-reference findings over the workspace."""
    root = Path(repo_root)
    census = _census(root)
    findings: list[dict] = []
    for type_, required in REQUIRED_LINKS.items():
        vocab = sdlc_md.status_vocab(type_, root)
        for path in sdlc_md.artifact_files(type_, root):
            text = path.read_text(encoding="utf-8")
            rid = sdlc_md.extract_record_id(path.stem) or path.stem
            status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab) or "Unknown"
            terminal = status in TERMINAL
            for field in required:
                val = sdlc_md.extract_field(text, field)
                refs = set() if _is_blank(val) else {sdlc_md.norm_id(r) for r in sdlc_md.ID_SEARCH_RE.findall(val)}
                if not refs:  # absent, a `--` placeholder, or present but carrying no resolvable ID
                    findings.append({
                        "id": rid, "type": type_, "status": status,
                        "kind": "missing-required", "field": field,
                        "severity": "advisory" if (terminal or type_ in LINK_OPTIONAL) else "error",
                    })
                    continue
                for ref in refs:
                    if ref not in census:
                        findings.append({
                            "id": rid, "type": type_, "status": status,
                            "kind": "dangling", "field": field, "ref": ref,
                            "severity": "advisory",
                        })
    findings.sort(key=lambda f: (f["id"], f["field"], f["kind"]))
    errors = sum(1 for f in findings if f["severity"] == "error")
    return {
        "generated_at": sdlc_md.now_iso8601(),
        "findings": findings,
        "summary": {"errors": errors, "advisories": len(findings) - errors, "total": len(findings)},
    }


def cmd_check(args: argparse.Namespace) -> int:
    """Run the integrity check; exit non-zero only on an active missing-required."""
    res = detect_integrity(args.root)
    if args.format == "json":
        print(json.dumps(res, indent=2))
    else:
        s = res["summary"]
        print(f"integrity: {s['errors']} error(s), {s['advisories']} advisory, {s['total']} total")
        for f in res["findings"]:
            mark = "ERR" if f["severity"] == "error" else "adv"
            ref = f" -> {f['ref']}" if f["kind"] == "dangling" else ""
            print(f"  {mark} {f['id']} ({f['status']}): {f['kind']} {f['field']}{ref}")
        hints = sdlc_md.remediation_lines("integrity", {f["kind"] for f in res["findings"]})
        if hints:
            print("Guidance:")
            for h in hints:
                print(f"  - {h}")
    return 1 if res["summary"]["errors"] else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio referential-integrity check.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Check required links + dangling references.")
    c.add_argument("--root", default=".", help="Repo root (default: .)")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_check)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
