#!/usr/bin/env python3
"""changelog - per-unit fragments composed deterministically into CHANGELOG.md.

The same-commit paperwork rule (LL0004) collides with one shared CHANGELOG file:
unit A's bullet is written before unit B ships, so committing A cleanly means
hand-holding B's text back. The ecosystem's proven answer (towncrier/reno) is
FRAGMENTS: each unit writes its own small file under `changelog.d/`, trivially
committed with its unit; `compose` folds every fragment into `## [Unreleased]`
under its declared section and CONSUMES the fragment (idempotence by
consumption). A fragment that cannot be placed refuses loudly before anything
is written (all-validate-then-write, the atomic-create rule), and the release
gate fails while a stray fragment exists - an entry is never silently dropped
from a cut.

Fragment format (first line declares the section, the rest is the entry):

    <!-- section: Added -->
    - **The thing (USxxxx).** What shipped, in CHANGELOG voice.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from lib import sdlc_md
except ImportError:  # pragma: no cover - flat install layout
    import sdlc_md  # type: ignore

FRAGMENT_DIR = "changelog.d"
# Keep-a-Changelog vocabulary plus the Breaking section this repo already uses.
SECTIONS = ("Breaking", "Added", "Changed", "Deprecated", "Removed", "Fixed", "Security")
_MARKER = re.compile(r"^<!--\s*section:\s*([A-Za-z]+)\s*-->\s*$")


class FragmentError(ValueError):
    """A fragment that cannot be composed - named, never skipped."""


def _fragment_paths(root: Path) -> list[Path]:
    d = Path(root) / FRAGMENT_DIR
    return sorted(d.glob("*.md")) if d.is_dir() else []


def _parse(path: Path) -> tuple[str, str]:
    """(section, entry_text) - refuses a missing marker or unknown section."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise FragmentError(f"{path.name}: empty fragment")
    m = _MARKER.match(lines[0].strip())
    if not m:
        raise FragmentError(f"{path.name}: first line must be '<!-- section: <name> -->' "
                            f"(one of {', '.join(SECTIONS)})")
    section = m.group(1).capitalize() if m.group(1).capitalize() in SECTIONS else m.group(1)
    if section not in SECTIONS:
        raise FragmentError(f"{path.name}: unknown section {section!r} - "
                            f"one of {', '.join(SECTIONS)}")
    entry = "\n".join(lines[1:]).strip("\n")
    if not entry.strip():
        raise FragmentError(f"{path.name}: no entry text after the section marker")
    return section, entry


def check(root) -> list[Path]:
    """Stray (uncomposed) fragments. The release gate fails while any exist."""
    return _fragment_paths(Path(root))


def compose(root) -> dict:
    """Fold every fragment into `## [Unreleased]` and consume it.

    All fragments are parsed BEFORE anything is written (a bad one refuses the
    whole run - no partial compose). Entries land at the TOP of their section's
    list; a missing section heading is created at the head of [Unreleased]
    (most recently composed first - a hand-edit may reorder headings freely)."""
    root = Path(root)
    frags = _fragment_paths(root)
    if not frags:
        return {"composed": 0, "sections": []}
    parsed = [(p, *_parse(p)) for p in frags]  # refuses before any write
    clog = root / "CHANGELOG.md"
    try:
        text = clog.read_text(encoding="utf-8")
    except OSError as exc:
        raise FragmentError(f"CHANGELOG.md unreadable: {exc}") from exc
    if "## [Unreleased]" not in text:
        raise FragmentError("CHANGELOG.md has no '## [Unreleased]' section to compose into")
    head, rest = text.split("## [Unreleased]", 1)
    nxt = re.search(r"\n## \[", rest)
    unreleased, tail = (rest[:nxt.start()], rest[nxt.start():]) if nxt else (rest, "")

    for _path, section, entry in parsed:
        heading = f"### {section}"
        # line-anchored: the heading must BE a line, not a substring of one
        pattern = re.compile(rf"(^{re.escape(heading)}[ \t]*\n\n?)", re.M)
        if pattern.search(unreleased):
            # insert at the top of the section: right after the heading line + blank
            unreleased = pattern.sub(lambda m: m.group(1) + entry + "\n", unreleased, count=1)
        else:
            # create the missing section at the head of [Unreleased] - deterministic,
            # and a later hand-edit can reorder headings without breaking compose
            unreleased = f"\n\n{heading}\n\n{entry}\n\n" + unreleased.lstrip("\n")
    sdlc_md.atomic_write(clog, head + "## [Unreleased]" + unreleased + tail)
    for p, _s, _e in parsed:
        p.unlink()
    return {"composed": len(parsed), "sections": sorted({s for _p, s, _e in parsed})}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="changelog", description="Per-unit CHANGELOG fragments: write one per unit "
        "under changelog.d/, compose them deterministically into [Unreleased].")
    sdlc_md.add_global_root(ap)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compose", help="fold all fragments into CHANGELOG.md and consume them")
    k = sub.add_parser("check", help="list stray (uncomposed) fragments; exit 1 if any")
    for p in (c, k):
        p.add_argument("--root", default=".", help="Repo root (default: .)")
    args = ap.parse_args(argv)
    if args.cmd == "compose":
        try:
            r = compose(args.root)
        except FragmentError as exc:
            print(f"compose refused: {exc}", file=sys.stderr)
            return 2
        print(f"composed {r['composed']} fragment(s)"
              + (f" into {', '.join(r['sections'])}" if r["sections"] else " (none present)"))
        return 0
    strays = check(args.root)
    if strays:
        print(f"{len(strays)} stray fragment(s): " + ", ".join(p.name for p in strays))
        return 1
    print("no stray fragments")
    return 0


if __name__ == "__main__":
    sys.exit(main())
