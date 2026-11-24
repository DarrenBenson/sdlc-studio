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

`shape` checks that format when a fragment is WRITTEN rather than when it is folded: it names
every fragment `compose` would refuse, with compose's own message, and `shape --staged` judges
the index blobs a commit will record. Compose stops at the first bad fragment, correctly, since
a partial fold is worse than none; that makes the release cut the costliest place to learn of
the drift, and the commit that wrote the fragment the cheapest.

`required` is the same rule applied one step earlier still: the commit-msg hook asks it whether
a commit that names a unit and stages code also stages (or already tracks) that unit's fragment,
since only the message says which unit the commit belongs to. On a shared commit only a unit that
owns a staged code file is asked.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

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


# A unit id in a commit subject: the judged types, a v2 sequential id or a v3 short ULID.
_UNIT_ID = re.compile(r"\b((?:US|BG|CR)(?:-[0-9A-HJKMNP-TV-Z]{8,}|-?\d{4,}))\b")
_REFS_LINE = re.compile(r"^[ \t]*Refs:[ \t]*(.+)$", re.MULTILINE | re.IGNORECASE)
# `Changelog: none - <reason>`: the one exemption, and it must say why.
_EXEMPT_LINE = re.compile(r"^[ \t]*Changelog:[ \t]*none\b(.*)$", re.MULTILINE | re.IGNORECASE)
_EXEMPT_REASON = re.compile(r"^[ \t]+-[ \t]+\S")
# Paths that are paperwork, not shipped behaviour: they never ask for a fragment.
_PAPERWORK_ROOTS = ("sdlc-studio/", f"{FRAGMENT_DIR}/")


class FragmentError(ValueError):
    """A fragment that cannot be composed - named, never skipped."""


def _fragment_paths(root: Path) -> list[Path]:
    d = Path(root) / FRAGMENT_DIR
    return sorted(d.glob("*.md")) if d.is_dir() else []


class StagedReadError(RuntimeError):
    """`shape --staged` could not read what the commit will record. Refused, never read as
    nothing staged."""


def _parse(name: str, text: str) -> tuple[str, str]:
    """(section, entry_text) - refuses a missing marker or unknown section.

    Takes the fragment's TEXT rather than its path, so the working-tree reader (compose) and the
    index reader (`shape --staged`) share one parser and one set of messages."""
    lines = text.splitlines()
    if not lines:
        raise FragmentError(f"{name}: empty fragment")
    m = _MARKER.match(lines[0].strip())
    if not m:
        raise FragmentError(f"{name}: first line must be '<!-- section: <name> -->' "
                            f"(one of {', '.join(SECTIONS)})")
    section = m.group(1).capitalize() if m.group(1).capitalize() in SECTIONS else m.group(1)
    if section not in SECTIONS:
        raise FragmentError(f"{name}: unknown section {section!r} - "
                            f"one of {', '.join(SECTIONS)}")
    entry = "\n".join(lines[1:]).strip("\n")
    if not entry.strip():
        raise FragmentError(f"{name}: no entry text after the section marker")
    return section, entry


def _first_line(raw: bytes) -> str:
    """git's own reason, without the usage screen it prints after it."""
    lines = raw.decode("utf-8", "replace").strip().splitlines()
    return lines[0] if lines else "(no message)"


def _staged_fragments(root: Path) -> list[tuple[str, str]]:
    """(name, staged text) for every fragment the index adds, modifies or renames.

    Deletions are excluded (`--diff-filter=d`): the release cut's own commit stages the deletion
    of every fragment it folded, and a deleted fragment is not composed by anybody. The text is
    the INDEX blob, never the working tree, so an untracked draft is not judged and a bad blob
    repaired on disk but not re-staged still is. A git call that fails, or a blob that cannot be
    read, is refused rather than skipped."""
    try:
        cp = subprocess.run(["git", "-c", "core.quotepath=false", "diff", "--cached",
                             "--name-only", "-z", "--diff-filter=d", "--",
                             f"{FRAGMENT_DIR}/*.md"],
                            cwd=str(root), capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        raise StagedReadError(f"git could not list the staged fragments: {exc}") from exc
    if cp.returncode != 0:
        raise StagedReadError("git could not list the staged fragments (rc "
                              f"{cp.returncode}): {_first_line(cp.stderr)}")
    out = []
    for rel in sorted(r for r in cp.stdout.decode("utf-8", "replace").split("\0") if r):
        # compose reads only the directory's own *.md, so a nested file is nobody's fragment
        if PurePosixPath(rel).parent.name != FRAGMENT_DIR:
            continue
        try:
            blob = subprocess.run(["git", "show", f":{rel}"], cwd=str(root),
                                  capture_output=True, timeout=60)
        except (OSError, subprocess.SubprocessError) as exc:
            raise StagedReadError(f"git could not read the staged blob of {rel}: {exc}") from exc
        if blob.returncode != 0:
            raise StagedReadError(f"git could not read the staged blob of {rel} (rc "
                                  f"{blob.returncode}): {_first_line(blob.stderr)}")
        try:
            out.append((PurePosixPath(rel).name, blob.stdout.decode("utf-8")))
        except UnicodeDecodeError as exc:
            raise StagedReadError(f"the staged blob of {rel} is not UTF-8 text") from exc
    return out


def _git_lines(root: Path, args: list[str]) -> list[str]:
    """The NUL-separated paths a git call prints, raising StagedReadError when git fails."""
    try:
        cp = subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=str(root),
                            capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        raise StagedReadError(f"git could not read the index: {exc}") from exc
    if cp.returncode != 0:
        raise StagedReadError(f"git could not read the index (rc {cp.returncode}): "
                              f"{_first_line(cp.stderr)}")
    return [r for r in cp.stdout.decode("utf-8", "replace").split("\0") if r]


def _message_lines(message: str) -> list[str]:
    """The message as git records it: the `#` scaffold lines are dropped."""
    return [ln for ln in message.splitlines() if not ln.startswith("#")]


def _subject_ids(message: str) -> set[str]:
    """The unit ids the subject names, normalised: `BG-1574` and `BG1574` are one id."""
    subject = next((ln for ln in _message_lines(message) if ln.strip()), "")
    return {sdlc_md.norm_id(i) for i in _UNIT_ID.findall(subject)}


def owning_ids(message: str) -> list[str]:
    """The unit ids a commit message attributes the commit to, normalised and sorted.

    A subject naming one unit gives that unit the commit. A subject naming several leaves the
    attribution to the `Refs:` trailers among the ids it names (the hook writes them from the
    staged files' ownership before this runs, a unit's own record included), and an id only a
    `Mentions:` trailer names owns nothing. A subject naming no unit owns nothing."""
    named = _subject_ids(message)
    if len(named) <= 1:
        return sorted(named)
    refs = {sdlc_md.norm_id(i) for m in _REFS_LINE.finditer("\n".join(_message_lines(message)))
            for i in _UNIT_ID.findall(m.group(1))}
    return sorted(refs & named)


def _code_owners(root: Path, ids: list[str], code: list[str]) -> list[str]:
    """The ids among `ids` that own one of the staged `code` paths, read the way the hook's
    trailer derivation reads ownership: the unit's `Affects` covers the path (the file, a
    directory it sits under or a glob it matches), or the path carries the unit's id in its
    name. An id with no artefact in the workspace declares nothing. A unit whose only staged
    file is paperwork (its record, its fragment) owns no code, so it owes no fragment."""
    import engagement_floor  # noqa: PLC0415 - read only for a shared commit; sibling script
    owners = []
    for rid in ids:
        found = sdlc_md.find_by_id(root, rid)
        declared = (engagement_floor.declared_keys(root, sdlc_md.read_text_safe(found[0]) or "")
                    if found else set())
        if any(engagement_floor._path_owner(f) == rid
               or any(engagement_floor.declaration_covers(f, d) for d in declared)
               for f in code):
            owners.append(rid)
    return owners


def fragment_names(unit_id: str) -> list[str]:
    """The fragment paths that satisfy a normalised unit id, the one a refusal names first:
    both the dashless spelling `sdlc_md.norm_id` gives and the dashed one, since a subject's
    `BG-1574` reads as `BG1574`. A sequential id (`BG1574`) is named dashless first, as this
    project writes it; a schema 3 id (`BG-01JQK3F8`) dashed first, as its artefacts spell it."""
    dashless = f"{FRAGMENT_DIR}/{unit_id}.md"
    dashed = f"{FRAGMENT_DIR}/{unit_id[:2]}-{unit_id[2:]}.md"
    return [dashless, dashed] if unit_id[2:].isdigit() else [dashed, dashless]


def _exemption(message: str) -> tuple[bool, bool]:
    """(a `Changelog: none` trailer is present, it carries a reason after ` - `)."""
    found = reasoned = False
    for m in _EXEMPT_LINE.finditer("\n".join(_message_lines(message))):
        found = True
        reasoned = reasoned or bool(_EXEMPT_REASON.match(m.group(1)))
    return found, reasoned


def required(root, message: str) -> list[str]:
    """The refusals for a commit that owns code but not its fragment; empty when it passes.

    Applies only where the project keeps a `changelog.d/` directory. A commit passes when no unit
    owns it, when everything it stages is paperwork (under `sdlc-studio/` or `changelog.d/`), when
    each owning unit's `changelog.d/<ID>.md` is in the index (staged, or tracked and not staged
    for deletion), or under a `Changelog: none - <reason>` trailer. On a shared commit only a
    `Refs:` id that owns a staged code file is asked (`_code_owners`). A `Changelog: none` with no
    reason exempts nothing. A refusal names each unit as the fragment it asks for spells it
    (`fragment_names`). Raises StagedReadError when git cannot answer."""
    root = Path(root)
    if not (root / FRAGMENT_DIR).is_dir():
        return []
    ids = owning_ids(message)
    if not ids:
        return []
    staged = _git_lines(root, ["diff", "--cached", "--name-only", "-z", "--"])
    code = [p for p in staged if not p.startswith(_PAPERWORK_ROOTS)]
    if not code:
        return []
    if len(_subject_ids(message)) > 1:
        ids = _code_owners(root, ids, code)
    indexed = set(_git_lines(root, ["ls-files", "-z", "--", f"{FRAGMENT_DIR}/*.md"]))
    missing = [i for i in ids if not indexed.intersection(fragment_names(i))]
    if not missing:
        return []
    found, reasoned = _exemption(message)
    if reasoned:
        return []
    # Each unit is named as the fragment the refusal asks for spells it, never as the dashless
    # comparison key: `BG-01JQK3F8` for a schema 3 id, `BG1574` for a sequential one.
    faults = [f"{PurePosixPath(want).stem}: the commit stages code but not {want}"
              for want in (fragment_names(i)[0] for i in missing)]
    if found:
        faults.append("`Changelog: none` exempts nothing without a reason: write "
                      "`Changelog: none - <why this commit needs no fragment>`")
    return faults


def shape(root, *, staged: bool = False) -> tuple[int, list[str]]:
    """(fragments judged, compose's message for EVERY one it would refuse).

    The same parser compose uses, run over every fragment rather than stopping at the first:
    compose refuses the whole fold on one bad fragment, which is right for a destructive action
    and wrong for a check, whose job is to name all of them in one pass. `staged` judges the
    index blobs a commit will record; otherwise every pending fragment in the working tree."""
    root = Path(root)
    if staged:
        frags = _staged_fragments(root)
    else:
        frags = [(p.name, p.read_text(encoding="utf-8")) for p in _fragment_paths(root)]
    faults = []
    for name, text in frags:
        try:
            _parse(name, text)
        except FragmentError as exc:
            faults.append(str(exc))
    return len(frags), faults


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
    partial compose). Each entry starts its own top-level bullet, one written as prose gaining a
    `- ` marker. Entries land at the TOP of their section's list, except a fragment's `####`
    block (a retired-flags table), which lands at the END of its section; a missing section heading
    is created at the head of [Unreleased] (most recently composed first - a hand-edit may reorder
    headings freely)."""
    root = Path(root)
    frags = _fragment_paths(root)
    if not frags:
        return {"composed": 0, "would_compose": 0, "sections": [], "applied": apply}
    # refuses before any write, in dry-run too
    parsed = [(p, *_parse(p.name, p.read_text(encoding="utf-8"))) for p in frags]
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
        # a fragment's `####` block (a retired-flags table, say) goes after the section's
        # bullets, never between them: folded at the top, it ran into the next fragment's bullet
        bullets, block = _split_block(entry)
        # an entry written as prose gets its own bullet: folded as written, the bullet above
        # it read it as a lazy continuation line and the two entries became one
        bullets = _as_bullet(bullets)
        # line-anchored: the heading must BE a line, not a substring of one
        pattern = re.compile(rf"(^{re.escape(heading)}[ \t]*\n\n?)", re.M)
        if pattern.search(unreleased):
            if bullets:
                # insert at the top of the section: right after the heading line + blank, and
                # a blank line after them when the section opens with a `####` block instead
                unreleased = pattern.sub(
                    lambda m: m.group(1) + bullets + "\n"
                    + ("\n" if unreleased[m.end():].startswith("#") else ""),
                    unreleased, count=1)
        else:
            # create the missing section at its CANONICAL position among the existing
            # headings, so compose never emits an out-of-order heading its own structural
            # check (structure_errors) would then reject - the writer is bound by the same
            # ordering rule as the hand-editor, and the two cannot end in a standoff
            unreleased = _create_section(unreleased, section, bullets or block)
            if not bullets:
                block = ""
        if block:
            unreleased = _append_to_section(unreleased, heading, block)
    sdlc_md.atomic_write(clog, head + "## [Unreleased]" + unreleased + tail)
    for p, _s, _e in parsed:
        p.unlink()
    return {"composed": len(parsed), "would_compose": len(parsed), "applied": True,
            "sections": sorted({s for _p, s, _e in parsed})}


_LIST_ITEM = re.compile(r"^[-*+][ \t]")


def _as_bullet(entry: str) -> str:
    """`entry` as one top-level list item. An entry that already opens with a `-`, `*` or `+`
    list item comes back byte for byte; any other gets a `- ` marker on its first line and every
    later line indented two spaces under it, a blank line left empty."""
    if not entry or _LIST_ITEM.match(entry):
        return entry
    first, *rest = entry.split("\n")
    return "\n".join(["- " + first] + ["  " + ln if ln.strip() else "" for ln in rest])


def _split_block(entry: str) -> tuple[str, str]:
    """(the entry's bullets, its `####` block from the first `#### ` heading on), each stripped
    of blank edge lines; either may be empty."""
    m = re.search(r"^#### ", entry, re.M)
    if not m:
        return entry, ""
    return entry[:m.start()].strip("\n"), entry[m.start():].strip("\n")


def _append_to_section(unreleased: str, heading: str, block: str) -> str:
    """Put `block` at the end of the `heading` section (before the next `### ` heading, or at
    the end of `unreleased`) with a blank line either side. A block whose `####` heading the
    section already holds joins it under that one heading, and a table repeating the held
    table's header row continues that table."""
    start = re.search(rf"^{re.escape(heading)}[ \t]*$", unreleased, re.M).end()
    nxt = re.search(r"^### ", unreleased[start:], re.M)
    end = start + nxt.start() if nxt else len(unreleased)
    after = "\n" + unreleased[end:] if nxt else ""
    body = unreleased[start:end].rstrip("\n")
    title, _nl, rest = block.partition("\n")
    held = re.search(rf"^{re.escape(title.rstrip())}[ \t]*$", body, re.M)
    if held:
        below = re.search(r"^#{1,4} ", body[held.end():], re.M)
        cut = held.end() + below.start() if below else len(body)
        mine, later = body[:cut].rstrip("\n"), body[cut:].strip("\n")
        rest = rest.strip("\n")
        lines = rest.split("\n")
        if (len(lines) > 2 and lines[0].startswith("|") and mine.endswith("|")
                and "\n".join(lines[:2]) in mine):
            mine += "\n" + "\n".join(lines[2:])
        else:
            mine += "\n\n" + rest
        body = mine + ("\n\n" + later if later else "")
        return unreleased[:start] + body + "\n" + after
    return unreleased[:end].rstrip("\n") + "\n\n" + block + "\n" + after


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


def build_parser() -> argparse.ArgumentParser:
    """The parser, as a module-level function so the surface can be enumerated without
    running the command. `lib/surface.py` walks every one of these; a parser built inside
    `main()` is invisible to it, which is a verb no coverage number can count."""
    ap = argparse.ArgumentParser(
        prog="changelog", description="Per-unit CHANGELOG fragments: write one per unit "
        "under changelog.d/, compose them deterministically into [Unreleased].")
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
    sh = sub.add_parser("shape", help="name EVERY fragment compose would refuse, with compose's "
                        "own message; exit 1 only on a malformed fragment, never on a pending one")
    sh.add_argument("--staged", action="store_true",
                    help="judge the fragments this commit adds, modifies or renames, read from "
                         "the index (never the working tree; deletions are not judged)")
    rq = sub.add_parser("required", help="refuse a commit message that owns staged code but not "
                        "its unit's fragment; exit 1 on a refusal, 2 when git cannot answer")
    rq.add_argument("message_file", help="the commit message file git hands the commit-msg hook")
    for p in (c, k, s, sh, rq):
        p.add_argument("--root", default=".", help="Repo root (default: .)")
    # Uniform family grammar: `--root` valid before OR after the verb, with the
    # per-subcommand copies re-pointed to SUPPRESS so a value given first is not
    # clobbered by a subparser default. Must run AFTER every subparser exists.
    sdlc_md.add_global_root(ap)
    return ap


def main(argv=None) -> int:
    ap = build_parser()
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
    if args.cmd == "required":
        try:
            message = Path(args.message_file).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            # a message nobody can read is not this check's to refuse; the hook has its own rule
            print(f"required skipped: cannot read the message ({exc})", file=sys.stderr)
            return 0
        try:
            faults = required(args.root, message)
        except StagedReadError as exc:
            print(f"required refused: {exc}", file=sys.stderr)
            return 2
        for f in faults:
            print(f, file=sys.stderr)
        return 1 if faults else 0
    if args.cmd == "shape":
        where = "staged" if args.staged else "pending"
        try:
            judged, faults = shape(args.root, staged=args.staged)
        except StagedReadError as exc:
            print(f"shape refused: {exc}", file=sys.stderr)
            return 2
        if faults:
            print(f"{len(faults)} of {judged} {where} fragment(s) cannot be composed - the "
                  "release cut's compose refuses the whole fold on any one of them:",
                  file=sys.stderr)
            for f in faults:
                print(f"  {f}", file=sys.stderr)
            return 1
        # names no fragment: a clean run has nothing to point at
        print(f"{judged} {where} fragment(s) well-formed")
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
