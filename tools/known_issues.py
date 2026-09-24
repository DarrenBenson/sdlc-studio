#!/usr/bin/env python3
"""Derive `docs/known-issues.md` from the bug corpus.

The page is a release disclosure: every finding this release ships open, by id. A disclosure
maintained by hand decays in one direction only, because a bug filed after the page was written
is simply absent and nothing notices. So the page is GENERATED here, at the release cut, together
with the one open-defect sentence of that version's notes. It is checked against the corpus at
the tag only (`.githooks/pre-push`): between releases the page and the notes state what the last
cut shipped, and filing or closing a finding moves neither.

    python3 tools/known_issues.py write --release 5.2.0   # the cut: the page and the notes' count
    python3 tools/known_issues.py check [--at REV]        # 1 when page and corpus disagree
    python3 tools/known_issues.py bar                     # non-zero while a barred finding is open

Repo-only tooling: not shipped with the skill. Pure stdlib.
"""

from __future__ import annotations

import argparse
import io
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import traceback
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PAGE_REL = "docs/known-issues.md"
BUGS_REL = "sdlc-studio/bugs"

#: The severities a release discloses rather than blocks on. High and Critical are the bar: they
#: are fixed before a tag, so a High finding appearing here would mean the bar had been dropped
#: rather than met, and the page would be reporting a decision nobody recorded.
DISCLOSED = ("Medium", "Low")

#: The severities the release BAR is stated in. Zero open at the tag is the whole claim v5.0.0
#: rests on, and until now nothing checked it: the disclosure guard compared the Medium and Low
#: sets in both directions and was silent on the one sentence a reader actually acts on.
BARRED = ("Critical", "High")

#: The notes of the release being cut, by version. Derived from `--release`, never pinned: a
#: hand-kept pointer at "the current notes" made every finding filed or closed demand an edit to
#: notes that had already shipped.
NOTES_TEMPLATE = "docs/release-notes-v{version}.md"

#: The one sentence of the notes the cut writes. Everything else in them is the author's prose.
_NOTES_COUNT = r"^\*\*v{version} discloses \d+ open defects: \d+ Medium, \d+ Low\.\*\*$"

#: Titles are the finding's own H1. Long ones are elided rather than wrapped, because a table
#: cell that wraps to five lines is a table nobody reads to the bottom of.
TITLE_MAX = 150

_STATUS = re.compile(r"^> \*\*Status:\*\* *(.+)$", re.M)
_SEVERITY = re.compile(r"^> \*\*Severity:\*\* *(.+)$", re.M)
#: The id form is `BG0123` canonically, but 21 files in this corpus write `BG-0123`, and a
#: heading that does not match skips the WHOLE file - status and severity with it. A finding
#: does not leave the release bar because of a hyphen.
_HEADING = re.compile(r"^# (BG-?\d+): (.+)$", re.M)

#: The page's prose is DERIVED from the count it sits above, because a sentence that is true of
#: fifteen findings is false of none: "they ship open, listed here by id" describes an empty
#: table as a list of findings, and "each id below is a file" promises files nobody can open.
#: The bar named is the one the release being cut is held to; the previous release's bar stays
#: below it as history, because a reader needs to know which bar the list in front of them serves.
def _head(count: int) -> str:
    if count:
        body = (
            "**Medium and Low findings ship open, listed here by id, triaged to v5.1.** Each is a real\n"
            "defect with a reproduction and, in most cases, a proposed fix. None of them stops the\n"
            "lifecycle running. They are listed rather than closed, because closing a bug to make a\n"
            "release look clean is the practice this tool exists to prevent.\n\n"
            "Each id below is a file in `sdlc-studio/bugs/` in the source repository, carrying the\n"
            "evidence, the reproduction and the proposed fix in full.\n")
    else:
        body = (
            "**No Medium or Low finding is open.** The corpus carries none at this commit, so the\n"
            "table below is empty rather than omitted: an absent section and an empty one say\n"
            "different things, and only one of them is checkable.\n")
    return f"""# Known issues

The defects SDLC Studio knows about and has chosen to ship. This page is the disclosure
half of the release bar: a project that hides its open findings is asking to be trusted
rather than read.

## The bar v5.1 is held to

**Zero open High-severity bugs at the tag, and every Medium disposed of or ruled.** A
finding either reaches a terminal status with its own verifiers passing, or it stays open
carrying a dated ruling that says why it ships.

## The bar v5.0.0 was held to, kept as history

**Zero open High-severity bugs at the tag.** Every High finding raised against v5 was
fixed and closed before the tag was cut. The bar was originally zero open bugs of any
severity; it moved on 2026-08-11, because holding a release for findings that are real
but not release-blocking had cost a month and was buying nothing a disclosure could not
buy honestly.

{body}
## Triaged to v5.1

"""


TAIL = """
## Not carried

Three High findings were ruled `Won't Fix` on their own merits before this bar was set,
and one was superseded by later work. They are not in the list above because they are not
open, and a disclosure that pads its count is as misleading as one that trims it.

## How this list is kept

It is derived from the bug corpus by `tools/known_issues.py` when a release is cut, not
maintained by hand, and the pre-push hook refuses a tag whose page disagrees with the corpus.
Any open bug whose severity is Medium or Low appears here; a bug that reaches a terminal
status leaves at the next cut. Cut it with
`python3 tools/known_issues.py write --release <version>`.
"""


#: The statuses at which a finding has LEFT the population. Everything else is open, including
#: `In Progress` and `Blocked`. Enumerating the open states instead - which is what a literal
#: `== "Open"` does - is an enumeration of a rule, and an enumeration is a lower bound rather
#: than a boundary: it silently exempts whatever it forgot, and what it forgot here was the
#: resting state of every bug somebody is halfway through fixing.
TERMINAL = ("Fixed", "Verified", "Closed", "Won't Fix", "Superseded")


def _is_open(status: str) -> bool:
    """Whether a finding is still open - NOT terminal, rather than one literal spelling."""
    return status.strip().casefold() not in {s.casefold() for s in TERMINAL}


def _matches(severity: str, wanted: tuple[str, ...]) -> bool:
    """Severity against a set, case-insensitively. `file_finding.py` does not normalise the
    field and the corpus holds seven bugs written `high`, so a case-sensitive compare makes the
    release bar's answer depend on how somebody typed."""
    return severity.strip().casefold() in {w.casefold() for w in wanted}


def _read(path: Path):
    """`(id, status, severity, title)` for a finding file, or None when it cannot be parsed."""
    text = path.read_text(encoding="utf-8")
    status, severity, heading = _STATUS.search(text), _SEVERITY.search(text), _HEADING.search(text)
    if not (status and severity and heading):
        return None
    return (heading.group(1), status.group(1).strip(), severity.group(1).strip(),
            heading.group(2).strip())


def unparseable(repo: Path | None = None) -> list[str]:
    """Every finding file neither reader can parse, repo-relative.

    The three guards this replaced each dropped such a file SILENTLY, and a finding absent from
    a release bar is indistinguishable from a corpus that is clean. Whatever the fourth
    unreadable shape turns out to be, it is reported rather than skipped.
    """
    base = repo or REPO
    return [str(p.relative_to(base)) for p in sorted((base / BUGS_REL).glob("BG*.md"))
            if _read(p) is None]


def unclassifiable(repo: Path | None = None) -> dict[str, str]:
    """`{bug id: severity}` for every finding whose severity is in NEITHER recognised set.

    `corpus()` keeps only DISCLOSED severities and `barred_open()` only BARRED ones, and both
    `continue` past anything else - so a value in neither is dropped by both, silently, and a
    finding absent from the bar reads exactly like a corpus that is clean. `unparseable()` cannot
    catch it, because the file parses: every field is present and one of them is just a word
    nobody recognises.

    EVERY finding file, not only the open ones. Both readers test open-ness before severity, so
    an unrecognised value on a closed unit is excluded twice over and would never be seen; the
    corpus's only instance today is exactly that shape. It is REPORTED rather than barred - an
    unreadable finding cannot be judged at all, while this one can be read and corrected in a
    single edit, and making the release bar hostage to a typo is the wrong trade.
    """
    base = repo or REPO
    found: dict[str, str] = {}
    for path in sorted((base / BUGS_REL).glob("BG*.md")):
        row = _read(path)
        if row is None or _matches(row[2], DISCLOSED) or _matches(row[2], BARRED):
            continue
        found[row[0]] = row[2]
    return found


def _warn_unclassifiable(repo: Path | None = None) -> None:
    """Name them, on every path that reads the corpus - the same rule `_warn_unparseable` follows."""
    odd = unclassifiable(repo)
    if odd:
        named = ", ".join(f"{k} ({v})" for k, v in sorted(odd.items()))
        print(f"warning: {len(odd)} finding(s) carry a severity in neither the barred nor the "
              f"disclosed set, so they are absent from both - {named}", file=sys.stderr)


def _warn_unparseable(repo: Path | None = None) -> None:
    """Say so, on any path that reads the corpus - not only at the release boundary.

    `--bar` refuses on an unreadable finding, but `--check` and `--write` ran the same readers
    and said nothing, so a malformed filing stayed invisible until somebody cut a tag. The
    per-commit lane is where it should be caught; that is LL0027, and it is what let BG0131 sit
    unread from 2026-07-14.
    """
    blind = unparseable(repo)
    if blind:
        print(f"warning: {len(blind)} finding(s) neither the bar nor this page can parse, so "
              f"they are absent from both - {', '.join(blind)}", file=sys.stderr)


def corpus(repo: Path | None = None) -> dict[str, tuple[str, str]]:
    """`{bug id: (severity, title)}` for every OPEN bug at a disclosed severity.

    Reads the same population as `barred_open` - the page and the bar are both surfaces a
    release is judged on, and repairing one alone leaves the defect standing in this file.
    """
    found: dict[str, tuple[str, str]] = {}
    for path in sorted(((repo or REPO) / BUGS_REL).glob("BG*.md")):
        row = _read(path)
        if row is None or not _is_open(row[1]) or not _matches(row[2], DISCLOSED):
            continue
        found[row[0]] = (row[2], row[3])
    return found


def barred_open(repo: Path | None = None) -> dict[str, str]:
    """`{bug id: severity}` for every OPEN finding at a severity the release bar forbids.

    Non-empty means the tag would ship against a bar it does not meet. This is deliberately a
    separate read from `corpus()` rather than a filter on it: the two answer different questions,
    and folding them together is how a residue check ends up standing in for a bar check.
    """
    found: dict[str, str] = {}
    for path in sorted(((repo or REPO) / BUGS_REL).glob("BG*.md")):
        row = _read(path)
        if row is None or not _is_open(row[1]) or not _matches(row[2], BARRED):
            continue
        found[row[0]] = row[2]
    return found


def _split(found: dict[str, tuple[str, str]]) -> tuple[int, int, int]:
    """`(total, mediums, lows)` - the one count the page's line and the notes' sentence state."""
    sevs = [s for s, _t in found.values()]
    return len(sevs), sevs.count("Medium"), sevs.count("Low")


def render(repo: Path | None = None) -> str:
    """The page the corpus implies. Low sorts first so the one Low finding is not lost mid-table."""
    found = corpus(repo)
    rows = sorted(found.items(), key=lambda kv: (kv[1][0] != "Low", kv[0]))
    lines = ["| Id | Severity | Finding |", "| --- | --- | --- |"]
    for bug_id, (sev, title) in rows:
        if len(title) > TITLE_MAX:
            title = title[: TITLE_MAX - 3].rstrip() + "..."
        lines.append(f"| `{bug_id}` | {sev} | {title} |")
    total, mediums, lows = _split(found)
    lines += ["", f"{total} findings: {mediums} Medium, {lows} Low."]
    return _head(total) + "\n".join(lines) + "\n" + TAIL


def _git(root: Path, *args: str, text: bool = True) -> subprocess.CompletedProcess:
    """git at `root`, never steered elsewhere by a locating variable a hook exported."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=text,
                          timeout=120, check=False, env=env)


def _tagged(root: Path, tag: str) -> bool | None:
    """Whether `tag` exists in the repository at `root`; None when git cannot say."""
    try:
        r = _git(root, "tag", "--list", tag)
    except OSError:
        return None
    return bool(r.stdout.strip()) if r.returncode == 0 else None


def _cut(root: Path, version: str) -> int:
    """Write the page and the notes' open-defect sentence for `version`, or refuse and write
    nothing. A tagged version is refused: its notes state what THAT release shipped with, and a
    count rewritten after the tag describes a release nobody cut."""
    tag = f"v{version}"
    tagged = _tagged(root, tag)
    if tagged is None:
        print(f"cannot tell whether {tag} is tagged: git could not read the tags at {root}",
              file=sys.stderr)
        return 1
    if tagged:
        print(f"{tag} already has a tag, so its notes stay as shipped - cut the next version "
              f"instead", file=sys.stderr)
        return 1
    notes_rel = NOTES_TEMPLATE.format(version=version)
    notes = root / notes_rel
    if not notes.is_file():
        print(f"{notes_rel} does not exist - write the release notes first", file=sys.stderr)
        return 1
    sentence = re.compile(_NOTES_COUNT.format(version=re.escape(version)), re.M)
    text = notes.read_text(encoding="utf-8")
    if len(sentence.findall(text)) != 1:
        print(f"{notes_rel} must carry exactly one line reading `**{tag} discloses N open "
              f"defects: N Medium, N Low.**` for the cut to fill in", file=sys.stderr)
        return 1
    total, mediums, lows = _split(corpus(root))
    line = f"**{tag} discloses {total} open defects: {mediums} Medium, {lows} Low.**"
    (root / PAGE_REL).write_text(render(root), encoding="utf-8")
    notes.write_text(sentence.sub(lambda _m: line, text), encoding="utf-8")
    print(f"wrote {PAGE_REL} and {notes_rel}: {total} disclosed finding(s)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    # No default mode: a generator that writes by default rewrites the page for anyone who runs
    # it to see what it does, so the mode is always stated.
    sub = ap.add_subparsers(dest="mode", required=True)
    write = sub.add_parser("write", help="the release cut: write the page and the open-defect "
                                         "sentence of that version's notes")
    write.add_argument("--release", required=True,
                       help="the version being cut, e.g. 5.2.0; refused once it has a tag")
    check = sub.add_parser("check", help="exit 1 when the page and the corpus disagree, 2 when "
                                         "they cannot be read - the tag-time check the pre-push "
                                         "hook runs")
    check.add_argument("--at", metavar="REV",
                       help="judge the page and the corpus as committed at REV (the pushed tag), "
                            "not as they stand in the working tree")
    sub.add_parser("bar", help="exit non-zero when any finding at a barred severity is still "
                               "open. A RELEASE-boundary check: an open High is ordinary "
                               "mid-sprint and is only a defect at the tag")
    for mode in sub.choices.values():
        mode.add_argument("--root", default=str(REPO))
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()

    if args.mode == "bar":
        # Named on this path too, and BEFORE the verdict. A severity in neither set is
        # dropped by both readers, so it does not hold the bar - but saying nothing about
        # it is how it stayed invisible, and this is the surface a release is judged on.
        _warn_unclassifiable(root)
        open_barred = barred_open(root)
        # A finding neither reader can parse is NOT evidence of a clean corpus. Reported before
        # the verdict and it refuses, because the three guards this replaced each dropped such a
        # file silently, and silence read exactly like "bar met".
        blind = unparseable(root)
        if blind:
            print(f"release bar UNKNOWN: {len(blind)} finding(s) neither the bar nor the "
                  f"disclosure page can parse, so their status and severity are invisible to "
                  f"both - {', '.join(blind)}. Repair the heading, status or severity field; a "
                  f"finding nobody can read must never count as a corpus with nothing in it")
        if not open_barred and not blind:
            print(f"release bar met: no open finding at {' or '.join(BARRED)} severity")
            return 0
        if not open_barred:
            return 1
        listing = ", ".join(f"{b} ({s})" for b, s in sorted(open_barred.items()))
        print(f"release bar NOT met: {len(open_barred)} open finding(s) at a barred severity - "
              f"{listing}. Fix them or change the bar in a recorded decision, but do not tag "
              f"against a bar the corpus contradicts.", file=sys.stderr)
        return 1

    if args.mode == "write":
        _warn_unparseable(root)     # every path that reads the corpus, not the bar alone
        _warn_unclassifiable(root)  # ...and the severities neither reader recognises
        return _cut(root, args.release.removeprefix("v"))
    if args.at is None:
        return _check(root)
    with tempfile.TemporaryDirectory(prefix="known_issues_at_") as tmp:
        if not _export(root, args.at, Path(tmp)):
            return 2
        return _check(Path(tmp))


def _export(root: Path, rev: str, dest: Path) -> bool:
    """Extract the page and the corpus as committed at `rev` into `dest`; False when unreadable.

    A tag ships its COMMIT, not the working tree: a page written and left uncommitted must not
    pass for the page the tag carries. Only the paths the commit holds are extracted, because
    `git archive` refuses a pathspec matching nothing: an absent corpus is an empty one, and an
    absent page is a disagreement."""
    held = _git(root, "ls-tree", "--name-only", rev, "--", PAGE_REL, BUGS_REL)
    if held.returncode != 0:
        return _unreadable(rev, held.stderr)
    paths = held.stdout.splitlines()
    if not paths:
        return True
    tar = _git(root, "archive", "--format=tar", rev, "--", *paths, text=False)
    if tar.returncode != 0:
        return _unreadable(rev, tar.stderr.decode(errors="replace"))
    with tarfile.open(fileobj=io.BytesIO(tar.stdout)) as archive:
        archive.extractall(dest, filter="data")
    return True


def _unreadable(rev: str, why: str) -> bool:
    print(f"cannot read {PAGE_REL} and {BUGS_REL} at {rev}: {why.strip()}", file=sys.stderr)
    return False


def _check(root: Path) -> int:
    """0 when the page is what the corpus implies, 1 when it is not."""
    _warn_unparseable(root)     # every path that reads the corpus, not the bar alone
    _warn_unclassifiable(root)  # ...and the severities neither reader recognises
    page = root / PAGE_REL
    if page.is_file() and page.read_text(encoding="utf-8") == render(root):
        print(f"{PAGE_REL} agrees with the corpus ({len(corpus(root))} disclosed finding(s))")
        return 0
    print(f"{PAGE_REL} disagrees with the bug corpus - cut it with "
          f"`python3 tools/known_issues.py write --release <version>`", file=sys.stderr)
    return 1


if __name__ == "__main__":
    # Exit 1 means "disagrees" and nothing else, so a crash exits 2 and the hook can say which.
    try:
        raise SystemExit(main())
    except Exception:  # noqa: BLE001 - reported in full, then a distinct exit code
        traceback.print_exc()
        raise SystemExit(2)
