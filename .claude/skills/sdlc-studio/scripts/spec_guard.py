#!/usr/bin/env python3
"""SDLC Studio spec-edit guard (schema v3 only - dormant under schema_version: 2).

US0092/CR0195. In the N=5 benchmark a delivery worker edited the workspace's requirements
spec to match its (wrong) implementation - adding clauses stating the inverse of the real
rule - and the change passed review because nothing distinguished a REQUESTED spec edit from
an unrequested one. Falsifying the source of truth is the worst propagation a bad plan can
have: it poisons every later reader, including auditors and future planners.

A read-only rule would be wrong (spec edits are sometimes legitimately requested). Instead
this is a deterministic ASSIST: given the changed-file set, it surfaces which files are
requirements/spec documents (config `review.spec_paths`) and whether any AC of the story
being delivered cites a spec change. A spec-path edit that no AC cites is `untraced` - the
signal the critic charter turns into a blocking finding. The traceability judgement itself
stays with the critic; the pre-check only guarantees the edit cannot be silently missed
(TRD ADR-006: the fire/skip trigger is deterministic; judgement acts inside the fired step).
"""
from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import config  # noqa: E402

_DEFAULT_SPEC_PATHS = ["*prd*.md", "*trd*.md", "*tsd*.md", "*spec*.md",
                       "*requirements*", "*/specs/*", "specs/*", "*/spec/*", "spec/*"]
# A path token WITH an extension, OR an extension-less token under a directory (specs/design) -
# a spec section is often referenced without a file extension; missing it would under-flag.
_PATH_RE = re.compile(r"[\w.-]+/[\w./-]+|[\w./-]+\.[A-Za-z0-9]+")


def _cfg(root, key: str, default):
    try:
        return config.get(root, f"review.{key}", default)
    except Exception:  # noqa: BLE001 - config must never break the pre-check
        return default


def spec_paths(root) -> list[str]:
    raw = _cfg(root, "spec_paths", _DEFAULT_SPEC_PATHS)
    return [str(g) for g in raw] if isinstance(raw, list) and raw else list(_DEFAULT_SPEC_PATHS)


def _matches(path: str, globs: list[str]) -> bool:
    p = (path or "").strip().lower()
    base = p.rsplit("/", 1)[-1]
    return any(fnmatch.fnmatch(p, g.lower()) or fnmatch.fnmatch(base, g.lower())
               for g in globs)


def spec_edits(root, changed_files) -> list[str]:
    """The subset of `changed_files` that are requirements/spec documents. Deterministic;
    a no-op ([]) unless the project is schema v3, so v2 projects are untouched."""
    if not sdlc_md.is_schema_v3(root):
        return []
    globs = spec_paths(root)
    return [f for f in changed_files if _matches(f, globs)]


def referenced_spec_tokens(root, text: str) -> set[str]:
    """The spec-glob path tokens the story actually names (Affects, Verify lines, AC prose).
    Path tokens only, never bare prose. Used to decide, PER edited file, whether the story
    references it - a story-wide 'mentions any spec' flag would let an untraced edit to file B
    ride on a mention of file A (the under-flag CR0195 forbids)."""
    globs = spec_paths(root)
    return {t.strip().lower() for t in _PATH_RE.findall(text or "") if _matches(t, globs)}


def _is_referenced(edited: str, tokens: set[str]) -> bool:
    ef = (edited or "").strip().lower()
    base = ef.rsplit("/", 1)[-1]
    return any(t == ef or t.rsplit("/", 1)[-1] == base for t in tokens)


def check(root, changed_files, story_text: str = "") -> dict:
    """Surface spec-document edits for the critic, PER edited file. Returns
    {spec_edits, referenced_files, untraced_files, story_references, untraced}.

    `untraced_files` are edited spec documents the story never references - the strong signal
    the critic charter treats as a blocking finding. `referenced_files` are edited spec docs the
    story does name; a reference is NOT proof the CHANGE was requested (a `Verify: grep` line
    references a spec without asking to edit it), so the critic must still confirm those. A no-op
    on v2 (spec_edits is empty). Deterministic; the traceability judgement stays with the critic
    (TRD ADR-006)."""
    edits = spec_edits(root, list(changed_files))
    refs = referenced_spec_tokens(root, story_text) if edits else set()
    untraced_files = [f for f in edits if not _is_referenced(f, refs)]
    referenced_files = [f for f in edits if _is_referenced(f, refs)]
    return {"spec_edits": edits, "referenced_files": referenced_files,
            "untraced_files": untraced_files, "story_references": sorted(refs),
            "untraced": bool(untraced_files)}


def _changed(spec: str | None) -> list[str]:
    if not spec:
        return []
    return [s.strip() for s in spec.replace("\n", ",").split(",") if s.strip()]


def cmd_check(args: argparse.Namespace) -> int:
    story_text = Path(args.story).read_text(encoding="utf-8") if args.story else ""
    res = check(args.root, _changed(args.changed), story_text)
    if res["untraced_files"]:
        print("UNTRACED spec edit(s) - the story never references these files; a blocking "
              "finding unless the critic confirms the change was requested: "
              + ", ".join(res["untraced_files"]))
        return 1  # check-failure: the family returns 1 (argparse owns 2 for usage errors)
    if res["referenced_files"]:
        print("spec edit(s) the story references (NOT proof the change was requested - a "
              "reference is not a change-request; critic must confirm): "
              + ", ".join(res["referenced_files"]))
    else:
        print("no spec-document edits in the changed set")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="SDLC Studio spec-edit guard (schema v3).")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Flag untraced edits to a requirements/spec document.")
    c.add_argument("--changed", required=True,
                   help="Comma/newline-separated changed file paths (e.g. from git diff --name-only)")
    c.add_argument("--story", default=None, help="Story file being delivered (for AC citations)")
    c.add_argument("--root", default=".")
    c.set_defaults(func=cmd_check)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
