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
# A release heading (## [x]) and a bare subsection heading (### Added). The subsection
# pattern matches ONLY `### <Word>` with nothing trailing, so a decorated heading like
# `### Added (EP0026, the backlog-clear sprint)` is left alone - the structural rule
# governs the canonical bare vocabulary, not an author's annotated section title.
_RELEASE_H = re.compile(r"^## (.+?)[ \t]*$")
_SUBSECTION_H = re.compile(r"^### ([A-Za-z]+)[ \t]*$")


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


def compose(root, *, apply: bool = False) -> dict:
    """Fold every fragment into `## [Unreleased]` and consume it - the RELEASE-time action.

    `apply=False` (the default) is a DRY RUN: it parses and validates every fragment (so a bad one
    still refuses the run) and reports what WOULD be composed, but writes nothing and consumes
    nothing. Folding is destructive - it rewrites [Unreleased] and DELETES every fragment - and it
    consumes the WHOLE pending set, not the caller's one. Run out of habit while adding a single
    fragment, that silently destroys every other unit's pending fragment. So the consuming form is
    opt-in: only `apply=True`, which the release cut passes.

    All fragments are parsed BEFORE anything is written (a bad one refuses the whole run - no
    partial compose). Entries land at the TOP of their section's list; a missing section heading is
    created at the head of [Unreleased] (most recently composed first - a hand-edit may reorder
    headings freely)."""
    root = Path(root)
    frags = _fragment_paths(root)
    if not frags:
        return {"composed": 0, "would_compose": 0, "sections": [], "applied": apply}
    parsed = [(p, *_parse(p)) for p in frags]  # refuses before any write, in dry-run too
    if not apply:
        # DRY RUN: report what a release cut would fold, touch nothing. The pending set survives.
        return {"composed": 0, "would_compose": len(parsed), "applied": False,
                "sections": sorted({s for _p, s, _e in parsed})}
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
            # create the missing section at its CANONICAL position among the existing
            # headings, so compose never emits an out-of-order heading its own structural
            # check (structure_errors) would then reject - the writer is bound by the same
            # ordering rule as the hand-editor, and the two cannot end in a standoff
            unreleased = _create_section(unreleased, section, entry)
    sdlc_md.atomic_write(clog, head + "## [Unreleased]" + unreleased + tail)
    for p, _s, _e in parsed:
        p.unlink()
    return {"composed": len(parsed), "would_compose": len(parsed), "applied": True,
            "sections": sorted({s for _p, s, _e in parsed})}


def _create_section(unreleased: str, section: str, entry: str) -> str:
    """Splice a new `### section` block into `unreleased` at its canonical position -
    immediately before the first existing subsection that ranks after it, or at the end
    when none does. Keeps compose's output in SECTIONS order for the structural check."""
    rank = SECTIONS.index(section)
    block = f"### {section}\n\n{entry}\n"
    later = [m.start()
             for m in re.finditer(r"^### ([A-Za-z]+)[ \t]*$", unreleased, re.M)
             if m.group(1) in SECTIONS and SECTIONS.index(m.group(1)) > rank]
    if later:
        pos = min(later)
        return unreleased[:pos].rstrip("\n") + "\n\n" + block + "\n" + unreleased[pos:]
    return unreleased.rstrip("\n") + "\n\n" + block


def _unreleased_body(text: str) -> str:
    """The `[Unreleased]` region of a CHANGELOG, or "" when there is none."""
    lines = (text or "").splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.lstrip().startswith("## ")
                  and "unreleased" in ln.lower()), None)
    if start is None:
        return ""
    end = next((i for i in range(start + 1, len(lines))
                if lines[i].lstrip().startswith("## ")), len(lines))
    return "\n".join(lines[start + 1:end]).strip()


def unreleased_hand_edit(before: str, after: str) -> str | None:
    """The refusal when a lane edited `[Unreleased]` directly, or None when it did not.

    `[Unreleased]` is ONE region of ONE file. Two lanes owing a changelog entry both edit it,
    and the collision surfaces as a merge conflict in the paperwork rather than in the work -
    which is how a lane comes to spend its time resolving a conflict about a sentence. A
    fragment under `changelog.d/` is per-unit by construction and cannot collide.

    The refusal NAMES THE COMMAND. A refusal that says only what the author did wrong sends
    them to read a reference page to find out what to do instead; this project has filed that
    complaint against its own tools more than once.
    """
    if _unreleased_body(before) == _unreleased_body(after):
        return None
    return ("refused: this edits the `[Unreleased]` section of CHANGELOG.md directly. That "
            "section is one region of one file, so two lanes editing it collide - and the "
            "collision lands in the paperwork rather than in the work. Write a fragment "
            "instead, which is per-unit and cannot collide:\n"
            "    changelog.d/<UNIT-ID>.md, first line `<!-- section: Added|Fixed|Changed -->`\n"
            "`changelog compose --apply` folds every fragment at the RELEASE cut - editing "
            "[Unreleased] is a release step, never a delivery step.")


def structure_errors(root) -> list[str]:
    """Structural faults in CHANGELOG.md's `[Unreleased]` headings: subsections out of the
    canonical SECTIONS order, a subsection repeated inside the release, or an empty
    subsection - the shapes a bad hand-insert produces. Returns a list of named faults;
    an empty list means well-formed.

    Scoped to `[Unreleased]` deliberately. It is the machine-managed section a compose
    writes and a bad insert lands in; the released history below it is frozen and stays
    hand-editable, so a correction to a published section must never trip this. Only bare
    `### <Word>` headings are governed - a decorated title is the author's, not the tool's.
    """
    clog = Path(root) / "CHANGELOG.md"
    if not clog.is_file():
        return []  # a project with no CHANGELOG.md has no headings to police
    try:
        lines = clog.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [f"CHANGELOG.md unreadable: {exc}"]
    start = None
    for i, ln in enumerate(lines):
        m = _RELEASE_H.match(ln)
        if m and m.group(1).strip() == "[Unreleased]":
            start = i
            break
    if start is None:
        return []  # no [Unreleased] to police (compose refuses that case on its own)
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if _RELEASE_H.match(lines[i]):
            end = i
            break
    return _unreleased_faults(lines, start, end)


def _unreleased_faults(lines: list[str], start: int, end: int) -> list[str]:
    """The three structural checks over the `[Unreleased]` slice `lines[start:end]`.
    Line numbers reported are 1-based positions in the whole file."""
    heads = [(m.group(1), i + 1, i)
             for i in range(start + 1, end)
             for m in [_SUBSECTION_H.match(lines[i])]
             if m and m.group(1) in SECTIONS]
    errs: list[str] = []
    # 1. a subsection repeated inside the release - name both line numbers, because every
    # entry between them reads as belonging to the second (the exact incident shape).
    by_name: dict[str, list[int]] = {}
    for name, lineno, _i in heads:
        by_name.setdefault(name, []).append(lineno)
    for name, occ in by_name.items():
        if len(occ) > 1:
            errs.append(f"[Unreleased]: '### {name}' repeated at lines "
                        + " and ".join(str(n) for n in occ)
                        + " - every entry between them reads as belonging to the second")
    # 2. subsections out of canonical order - name the out-of-place heading, what it
    # follows, and the order expected.
    high_rank, high_name = -1, None
    for name, lineno, _i in heads:
        rank = SECTIONS.index(name)
        if rank < high_rank:
            errs.append(f"[Unreleased]: '### {name}' at line {lineno} is out of canonical "
                        f"order - it follows '### {high_name}'; expected order is "
                        + ", ".join(SECTIONS))
        elif rank > high_rank:
            high_rank, high_name = rank, name
    # 3. an empty subsection - no entry before the next heading or the release end.
    for name, lineno, i in heads:
        has_entry = False
        for j in range(i + 1, end):
            if _SUBSECTION_H.match(lines[j]) or _RELEASE_H.match(lines[j]):
                break
            if lines[j].strip():
                has_entry = True
                break
        if not has_entry:
            errs.append(f"[Unreleased]: '### {name}' at line {lineno} is empty - no entry "
                        f"before the next heading or the release end")
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="changelog", description="Per-unit CHANGELOG fragments: write one per unit "
        "under changelog.d/, compose them deterministically into [Unreleased].")
    sdlc_md.add_global_root(ap)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compose", help="RELEASE cut: fold all fragments into CHANGELOG.md and "
                       "consume them. Dry-run by default (reports what it would fold, touches "
                       "nothing); pass --apply to actually fold and delete the fragments")
    c.add_argument("--apply", action="store_true",
                   help="fold and CONSUME the fragments - the destructive release-cut action; "
                        "without it, compose only reports what it would do")
    k = sub.add_parser("check", help="list stray (uncomposed) fragments; exit 1 if any")
    s = sub.add_parser("structure", help="check [Unreleased] headings are in order, "
                       "unrepeated and non-empty; exit 1 on a fault")
    for p in (c, k, s):
        p.add_argument("--root", default=".", help="Repo root (default: .)")
    args = ap.parse_args(argv)
    # Resolve the root ONCE and write it back, so every verb below anchors on the tree the
    # run belongs to. The family default `.` means "work it out from here", not "the cwd
    # is the project": otherwise a run from a subdirectory acts on a stray tree and exits 0.
    args.root = str(sdlc_md.resolve_root(args))
    if args.cmd == "structure":
        errs = structure_errors(args.root)
        if errs:
            for e in errs:
                print(e, file=sys.stderr)
            return 1
        print("[Unreleased] headings are well-formed")
        return 0
    if args.cmd == "compose":
        try:
            r = compose(args.root, apply=args.apply)
        except FragmentError as exc:
            print(f"compose refused: {exc}", file=sys.stderr)
            return 2
        into = f" into {', '.join(r['sections'])}" if r["sections"] else " (none present)"
        if r["applied"]:
            print(f"composed {r['composed']} fragment(s){into}")
        else:
            print(f"would compose {r['would_compose']} fragment(s){into} - re-run with --apply "
                  "to fold and consume them (this is the release cut; without --apply nothing is "
                  "written and no fragment is deleted)")
        return 0
    strays = check(args.root)
    if strays:
        print(f"{len(strays)} stray fragment(s): " + ", ".join(p.name for p in strays))
        return 1
    print("no stray fragments")
    return 0


if __name__ == "__main__":
    sys.exit(main())
