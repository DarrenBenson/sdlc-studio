#!/usr/bin/env python3
"""SDLC Studio review-prep: deterministic inputs for the five-leg review.

The unified review (PRD - TRD - TSD - Persona - Code) is Claude's judgment
call. This script front-loads the *mechanical* inputs each leg needs, so the
review starts from data instead of re-deriving it in-context: artifact
staleness (changed since last review), persona usage (defined vs referenced in
the PRD), and the count/AC-verification inputs. It makes no judgements and
mutates nothing - it gathers.

Subcommand:
  prep  Emit the review inputs as JSON/text.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

PROJECT_DOCS = ["prd", "trd", "tsd", "personas"]


def _mtime_iso(path: Path) -> str:
    """File modification time as an ISO-8601 Z string."""
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def staleness(repo_root: Path) -> dict:
    """For each artifact and project doc, whether it changed since last review.

    Uses file mtime as the deterministic 'last modified' signal and the
    review-state.json `last_reviewed` timestamp. No entry -> needs review.
    """
    base = repo_root / "sdlc-studio"
    state = sdlc_md.read_json(base / ".local" / "review-state.json", {})
    reviewed = state.get("artifacts", {}) if isinstance(state, dict) else {}
    out: dict[str, dict] = {}

    def consider(key: str, path: Path) -> None:
        if not path.exists():
            return
        modified = _mtime_iso(path)
        entry = reviewed.get(key, {})
        last_reviewed = entry.get("last_reviewed")
        needs = (last_reviewed is None) or (modified > last_reviewed)
        out[key] = {
            "path": str(path.relative_to(repo_root)),
            "last_modified": modified,
            "last_reviewed": last_reviewed,
            "needs_review": needs,
        }

    for doc in PROJECT_DOCS:
        consider(doc, base / f"{doc}.md")
    for type_ in sdlc_md.ARTIFACT_TYPES:
        for path in sdlc_md.artifact_files(type_, repo_root):
            rec = sdlc_md.extract_record_id(path.stem)
            if rec:
                consider(rec, path)
    return out


def persona_usage(repo_root: Path) -> dict:
    """Persona names defined vs referenced in the PRD (heuristic, deterministic).

    Definitions are H2 headings in personas.md; a persona is 'referenced' if its
    name appears anywhere in prd.md. 'unused' lists defined-but-unreferenced
    personas for the Persona leg to judge.
    """
    base = repo_root / "sdlc-studio"
    personas_md = base / "personas.md"
    prd_md = base / "prd.md"
    defined: list[str] = []
    if personas_md.exists():
        for line in personas_md.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^##\s+(.+?)\s*$", line)
            if m:
                defined.append(m.group(1).strip())
    prd_text = prd_md.read_text(encoding="utf-8") if prd_md.exists() else ""
    referenced = [name for name in defined if name and name in prd_text]
    unused = [name for name in defined if name not in referenced]
    return {
        "defined": defined,
        "referenced_in_prd": referenced,
        "unused": unused,
        "method": "heuristic: H2 headings in personas.md, substring match in prd.md",
    }


def inputs(repo_root: Path) -> dict:
    """Count and AC-verification inputs the review legs consume."""
    base = repo_root / "sdlc-studio"
    counts = {
        type_: len(sdlc_md.artifact_files(type_, repo_root))
        for type_ in sdlc_md.ARTIFACT_TYPES
    }
    verify_report = sdlc_md.read_json(base / ".local" / "verify-report.json", None)
    ac_summary = None
    if isinstance(verify_report, dict):
        stories = verify_report.get("stories", {})
        ac_summary = {
            "stories": len(stories),
            "verified": sum(s.get("verified", 0) for s in stories.values()),
            "failed": sum(s.get("failed", 0) for s in stories.values()),
        }
    return {"counts": counts, "ac_verification": ac_summary}


def cmd_prep(args: argparse.Namespace) -> int:
    """Emit the review inputs."""
    repo_root = Path(args.root).resolve()
    stale = staleness(repo_root)
    data = {
        "generated_at": sdlc_md.now_iso8601(),
        "staleness": stale,
        "needs_review": sorted(k for k, v in stale.items() if v["needs_review"]),
        "persona_usage": persona_usage(repo_root),
        "inputs": inputs(repo_root),
    }
    if args.format == "json":
        print(json.dumps(data, indent=2))
    else:
        nr = data["needs_review"]
        pu = data["persona_usage"]
        print(f"needs_review ({len(nr)}): {', '.join(nr) if nr else 'none'}")
        print(f"personas defined={len(pu['defined'])} unused={len(pu['unused'])}"
              + (f" ({', '.join(pu['unused'])})" if pu["unused"] else ""))
        print(f"counts: {data['inputs']['counts']}")
        if data["inputs"]["ac_verification"]:
            print(f"ac: {data['inputs']['ac_verification']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser for the prep subcommand."""
    p = argparse.ArgumentParser(
        prog="review_prep.py",
        description="Gather deterministic inputs for the five-leg unified review.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    pr = sub.add_parser("prep", help="Emit review inputs (staleness, persona usage, counts).")
    pr.add_argument("--root", default=".", help="Repo root (default: .)")
    pr.add_argument("--format", choices=("text", "json"), default="text")
    pr.set_defaults(func=cmd_prep)
    return p


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch to the chosen subcommand."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
