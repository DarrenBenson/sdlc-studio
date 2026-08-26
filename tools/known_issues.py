#!/usr/bin/env python3
"""Derive `docs/known-issues.md` from the bug corpus.

The page is a release disclosure: every finding this release ships open, by id. A disclosure
maintained by hand decays in one direction only, because a bug filed after the page was written
is simply absent and nothing notices. So the page is GENERATED here and compared against the
corpus by `tools/tests/test_known_issues.py`, which is what makes the page's own claim to be
derived a fact rather than a sentence.

    python3 tools/known_issues.py --check    # non-zero when the page and the corpus disagree
    python3 tools/known_issues.py --write    # regenerate the page

Repo-only tooling: not shipped with the skill. Pure stdlib.
"""

from __future__ import annotations

import argparse
import re
import sys
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

#: The page that states the bar in prose, for a reader outside this repository.
#: The CURRENT release's notes - the ones whose finding count must match the corpus today.
#: Pointed at v5.0.0 until v5.0.1 shipped, which made the guard demand that a HISTORICAL record
#: be rewritten every time a bug closed. A released version's notes state what THAT version
#: shipped with and must not move; only the current one tracks the corpus.
NOTES_REL = "docs/release-notes-v5.0.1.md"

#: Titles are the finding's own H1. Long ones are elided rather than wrapped, because a table
#: cell that wraps to five lines is a table nobody reads to the bottom of.
TITLE_MAX = 150

_STATUS = re.compile(r"^> \*\*Status:\*\* *(.+)$", re.M)
_SEVERITY = re.compile(r"^> \*\*Severity:\*\* *(.+)$", re.M)
#: The id form is `BG0123` canonically, but 21 files in this corpus write `BG-0123`, and a
#: heading that does not match skips the WHOLE file - status and severity with it. A finding
#: does not leave the release bar because of a hyphen.
_HEADING = re.compile(r"^# (BG-?\d+): (.+)$", re.M)
_ROW = re.compile(r"^\| `(BG\d+)` \| (\w+) \|", re.M)

HEAD = """# Known issues

The defects SDLC Studio knows about and has chosen to ship. This page is the disclosure
half of the release bar: a project that hides its open findings is asking to be trusted
rather than read.

## The bar v5.0.0 was held to

**Zero open High-severity bugs at the tag.** Every High finding raised against v5 was
fixed and closed before the tag was cut. The bar was originally zero open bugs of any
severity; it moved on 2026-08-11, because holding a release for findings that are real
but not release-blocking had cost a month and was buying nothing a disclosure could not
buy honestly.

**Medium and Low findings ship open, listed here by id, triaged to v5.1.** Each is a real
defect with a reproduction and, in most cases, a proposed fix. None of them stops the
lifecycle running. They are listed rather than closed, because closing a bug to make a
release look clean is the practice this tool exists to prevent.

Each id below is a file in `sdlc-studio/bugs/` in the source repository, carrying the
evidence, the reproduction and the proposed fix in full.

## Triaged to v5.1

"""

TAIL = """
## Not carried

Three High findings were ruled `Won't Fix` on their own merits before this bar was set,
and one was superseded by later work. They are not in the list above because they are not
open, and a disclosure that pads its count is as misleading as one that trims it.

## How this list is kept

It is derived from the bug corpus by `tools/known_issues.py`, not maintained by hand, and
`tools/tests/test_known_issues.py` fails when the two disagree. Any bug at `Open` whose
severity is Medium or Low appears here; a bug that reaches a terminal status leaves.
Regenerate with `python3 tools/known_issues.py --write`.
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


def listed(repo: Path | None = None) -> dict[str, str]:
    """`{bug id: severity}` as the shipped page's table states it."""
    page = (repo or REPO) / PAGE_REL
    if not page.exists():
        return {}
    return dict(_ROW.findall(page.read_text(encoding="utf-8")))


def render(repo: Path | None = None) -> str:
    """The page the corpus implies. Low sorts first so the one Low finding is not lost mid-table."""
    found = corpus(repo)
    rows = sorted(found.items(), key=lambda kv: (kv[1][0] != "Low", kv[0]))
    lines = ["| Id | Severity | Finding |", "| --- | --- | --- |"]
    for bug_id, (sev, title) in rows:
        if len(title) > TITLE_MAX:
            title = title[: TITLE_MAX - 3].rstrip() + "..."
        lines.append(f"| `{bug_id}` | {sev} | {title} |")
    mediums = sum(1 for _, (s, _t) in rows if s == "Medium")
    lows = sum(1 for _, (s, _t) in rows if s == "Low")
    lines += ["", f"{len(rows)} findings: {mediums} Medium, {lows} Low."]
    return HEAD + "\n".join(lines) + "\n" + TAIL


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="regenerate the page")
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero when the page and the corpus disagree")
    ap.add_argument("--bar", action="store_true",
                    help="exit non-zero when any finding at a barred severity is still open. "
                         "A RELEASE-boundary check, not a per-commit one: an open High is "
                         "ordinary mid-sprint and is only a defect at the tag")
    ap.add_argument("--root", default=str(REPO))
    args = ap.parse_args(argv)

    if args.bar:
        root = Path(args.root).resolve()
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
              f"{listing}. {NOTES_REL} claims zero; fix them or change the bar in a recorded "
              f"decision, but do not tag against a claim the corpus contradicts.", file=sys.stderr)
        return 1

    if args.write == args.check:
        # Neither, or both. A generator whose default action is to WRITE rewrites the page for
        # anyone who runs it to see what it does, and one whose default is to check makes --check
        # a switch that changes nothing - which is a documented flag doing nothing, the thing the
        # dead-flags lane exists to refuse. So the mode is stated.
        ap.error("pass exactly one of --write or --check")

    root = Path(args.root).resolve()
    _warn_unparseable(root)   # every path that reads the corpus, not only the release boundary
    want = render(root)
    page = root / PAGE_REL

    if args.write:
        page.write_text(want, encoding="utf-8")
        print(f"wrote {page} ({len(corpus(root))} disclosed finding(s))")
        return 0

    have = page.read_text(encoding="utf-8") if page.exists() else ""
    if have == want:
        print(f"{PAGE_REL} agrees with the corpus ({len(corpus(root))} disclosed finding(s))")
        return 0
    print(f"{PAGE_REL} disagrees with the bug corpus - regenerate with "
          f"`python3 tools/known_issues.py --write`", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
