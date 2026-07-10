#!/usr/bin/env python3
"""SDLC Studio epic resume helper.

`epic implement --resume` restarts a partially-done epic at the first non-Done
story instead of from scratch. The resume point is computed from each story's
canonical **Status** - the authoritative Done signal - not from a workflow
execution table, which is a derived view that can drift. The
run-state is persisted to `sdlc-studio/.local/epic-state.json` so resumption is
deterministic rather than reconstructed from prose. Read-only census; pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

# Terminal story statuses - resume skips all of these, not just Done; a Superseded
# or Won't-Implement story must not be handed back to the agent as work to do.
TERMINAL = {"Done", "Won't Implement", "Superseded", "Deferred"}


def epic_stories(repo_root: Path | str, epic_id: str) -> list[dict]:
    """Ordered [{id, status}] for stories whose **primary** Epic link is `epic_id`.

    Ordered by story id; that is deterministic but assumes id order tracks
    implementation order within the epic (no per-epic dependency graph here).
    """
    root = Path(repo_root)
    target = sdlc_md.norm_id(epic_id)
    vocab = sdlc_md.status_vocab("story", root)
    out: list[dict] = []
    for path in sdlc_md.artifact_files("story", root):
        text = path.read_text(encoding="utf-8")
        epic = sdlc_md.extract_field(text, "Epic")
        refs = sdlc_md.ID_SEARCH_RE.findall(epic) if epic else []
        # The primary (first) id is the canonical link; a trailing "(was EPxxxx)"
        # annotation must not pull the story into another epic's resume run.
        if not refs or sdlc_md.norm_id(refs[0]) != target:
            continue
        rid = sdlc_md.extract_record_id(path.stem) or path.stem
        status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab) or "Unknown"
        out.append({"id": rid, "status": status})
    out.sort(key=lambda s: s["id"])
    return out


def resume_point(repo_root: Path | str, epic_id: str) -> str | None:
    """The first non-terminal story id in the epic, or None when all are terminal."""
    return next((s["id"] for s in epic_stories(repo_root, epic_id) if s["status"] not in TERMINAL), None)


def build_state(repo_root: Path | str, epic_id: str) -> dict:
    """The resumable run-state for an epic."""
    stories = epic_stories(repo_root, epic_id)
    resume = next((s["id"] for s in stories if s["status"] not in TERMINAL), None)
    return {
        "generated_at": sdlc_md.now_iso8601(),
        "epic": sdlc_md.norm_id(epic_id),
        "stories": stories,
        "resume_at": resume,
        "complete": resume is None,
    }


def write_state(repo_root: Path | str, epic_id: str) -> tuple[dict, Path]:
    """Persist the run-state to .local/epic-state.json; return (state, path)."""
    state = build_state(repo_root, epic_id)
    path = Path(repo_root) / "sdlc-studio" / ".local" / "epic-state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(path, json.dumps(state, indent=2))  # atomic: a crash mid-write must not reset guardrail state
    return state, path


def cmd_resume(args: argparse.Namespace) -> int:
    """Compute + persist the resume point for an epic."""
    state, _ = write_state(args.root, args.epic)
    if args.format == "json":
        print(json.dumps(state, indent=2))
    elif state["complete"]:
        print(f"{state['epic']}: all stories Done; nothing to resume")
    else:
        print(f"{state['epic']}: resume at {state['resume_at']} ({len(state['stories'])} stories)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio epic resume helper.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("resume", help="First non-Done story in an epic + persist run-state.")
    r.add_argument("--epic", required=True, help="Epic id (e.g. EP0007)")
    r.add_argument("--root", default=".", help="Repo root (default: .)")
    r.add_argument("--format", choices=("text", "json"), default="text")
    r.set_defaults(func=cmd_resume)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
