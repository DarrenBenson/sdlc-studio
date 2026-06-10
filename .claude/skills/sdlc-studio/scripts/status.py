#!/usr/bin/env python3
"""SDLC Studio pipeline status.

Deterministic census of the four pillars (Requirements, Code, Tests, Reviews)
and the next-step hint, so Claude renders the dashboard from JSON instead of
reading every artifact in-context. Live metrics that need to run the project's
own toolchain (lint, type-check, coverage) are deliberately left out - the
script reports artifact-derived state; Claude runs the live checks.

Subcommands:
  pillars  Census of artifacts and reviews as JSON/text (default).
  hint     The single next action from the mechanical priority ladder.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402


def count_by_status(type_: str, repo_root: Path) -> dict:
    """Tally a type's files by canonical Status, plus a total.

    Decorated statuses (`Done (v2.66.0)`) collapse to their vocabulary token
    (`Done`) so the tally and done-percentages are correct; consultations files
    are excluded by `artifact_files`.
    """
    vocab = sdlc_md.STATUS_VOCAB.get(type_, [])
    counts: dict[str, int] = {}
    total = 0
    for path in sdlc_md.artifact_files(type_, repo_root):
        total += 1
        raw = sdlc_md.extract_field(path.read_text(encoding="utf-8"), "Status") or "Unknown"
        status = sdlc_md.canonical_status(raw, vocab) or "Unknown"
        counts[status] = counts.get(status, 0) + 1
    return {"total": total, "by_status": counts}


def _pct_done(census: dict, done_states: tuple[str, ...]) -> int:
    """Percentage of a census in any of the done_states (0 if empty)."""
    total = census["total"]
    if not total:
        return 0
    done = sum(census["by_status"].get(s, 0) for s in done_states)
    return round(100 * done / total)


def gather(repo_root: Path) -> dict:
    """Compute all four pillars from the artifact files and review state."""
    base = repo_root / "sdlc-studio"
    epics = count_by_status("epic", repo_root)
    stories = count_by_status("story", repo_root)
    test_specs = count_by_status("test-spec", repo_root)

    review_state = sdlc_md.read_json(base / ".local" / "review-state.json", {})
    review_files = sdlc_md.walk_glob(base / "reviews", "RV*.md")

    return {
        "generated_at": sdlc_md.now_iso8601(),
        "requirements": {
            "prd": (base / "prd.md").exists(),
            "personas": (base / "personas.md").exists(),
            "epics": epics,
            "stories": stories,
            "epics_ready_pct": _pct_done(epics, ("Ready", "Approved", "Done")),
            "stories_done_pct": _pct_done(stories, ("Done",)),
        },
        "code": {
            "trd": (base / "trd.md").exists(),
            "note": "run project lint/type-check/coverage live; not derivable from files",
        },
        "tests": {
            "tsd": (base / "tsd.md").exists(),
            "test_specs": test_specs,
        },
        "reviews": {
            "has_review_state": bool(review_state),
            "review_files": len(review_files),
            "latest": (base / "reviews" / "LATEST.md").exists(),
        },
    }


def cmd_pillars(args: argparse.Namespace) -> int:
    """Print the four-pillar census."""
    data = gather(Path(args.root).resolve())
    if args.format == "json":
        print(json.dumps(data, indent=2))
        return 0
    req = data["requirements"]
    print(f"Requirements: PRD={'yes' if req['prd'] else 'no'} "
          f"personas={'yes' if req['personas'] else 'no'} "
          f"epics={req['epics']['total']} ({req['epics_ready_pct']}% ready+) "
          f"stories={req['stories']['total']} ({req['stories_done_pct']}% done)")
    print(f"Code:         TRD={'yes' if data['code']['trd'] else 'no'}")
    print(f"Tests:        TSD={'yes' if data['tests']['tsd'] else 'no'} "
          f"test-specs={data['tests']['test_specs']['total']}")
    print(f"Reviews:      files={data['reviews']['review_files']} "
          f"latest={'yes' if data['reviews']['latest'] else 'no'}")
    return 0


def compute_hint(data: dict, repo_root: Path) -> dict:
    """Mechanical next-step ladder. Judgment branches are left to Claude."""
    req = data["requirements"]
    base = repo_root / "sdlc-studio"
    has_code = any((repo_root / d).exists() for d in ("src", "lib", "app", "cmd"))
    if not req["prd"]:
        return {"next_command": "prd generate" if has_code else "prd create",
                "reason": "no PRD yet"}
    if not data["code"]["trd"]:
        return {"next_command": "trd generate" if has_code else "trd create",
                "reason": "no TRD yet"}
    if not data["tests"]["tsd"]:
        return {"next_command": "tsd", "reason": "no TSD yet"}
    if not req["personas"]:
        return {"next_command": "persona", "reason": "no personas yet"}
    if req["epics"]["total"] == 0:
        return {"next_command": "epic", "reason": "no epics yet"}
    if req["stories"]["total"] == 0:
        return {"next_command": "story", "reason": "no stories yet"}
    if (base / ".local" / "workflow-state.json").exists():
        return {"next_command": "resume workflow",
                "reason": "a workflow-state.json is present (judgment: confirm with the operator)"}
    return {"next_command": "story plan / story implement",
            "reason": "pipeline seeded; pick the next Ready story (judgment)"}


def cmd_hint(args: argparse.Namespace) -> int:
    """Print the single next recommended action."""
    repo_root = Path(args.root).resolve()
    data = gather(repo_root)
    hint = compute_hint(data, repo_root)
    if args.format == "json":
        print(json.dumps(hint, indent=2))
    else:
        print(f"/sdlc-studio {hint['next_command']}  ({hint['reason']})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser for pillars and hint."""
    p = argparse.ArgumentParser(
        prog="status.py",
        description="Deterministic sdlc-studio pipeline status and hint.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("pillars", help="Census of the four pillars.")
    pi.add_argument("--root", default=".", help="Repo root (default: .)")
    pi.add_argument("--format", choices=("text", "json"), default="text")
    pi.set_defaults(func=cmd_pillars)

    hi = sub.add_parser("hint", help="The next recommended action.")
    hi.add_argument("--root", default=".", help="Repo root (default: .)")
    hi.add_argument("--format", choices=("text", "json"), default="text")
    hi.set_defaults(func=cmd_hint)

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
