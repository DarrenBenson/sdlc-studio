"""US1331: v6.5.0 discloses what it ships with, under the bar it was held to.

Both criteria judge the release, never the live corpus alone, because `gate.py --release` runs
every story's Verify at each later cut and a finding filed after 6.5.0 must not turn them red.
The release is the v6.5.0 tag once it exists. Before it, the release is the working tree while
its `docs/known-issues.md` differs from HEAD's (the cut being committed now), else the commit that
last wrote that page. AC1 reads the page and the notes there, and holds the page's Not carried
section to every finding at Medium or above that left without a fix, since the v6.5 bar bars
Medium. AC2 counts the open findings in that commit's corpus against the operator's bar for 6.5
(fewer than 50 open, none at Medium or above). `known_issues.py bar` holds a tree to the
severities of the bar its page names, Medium among them for 6.5, but not to the count of fewer
than 50, which is this test's alone; AC2 runs that command too, at the tag, or on the working
tree before the tag exists. Each check returns its problems and is run on a mutated copy, which
it must refuse. The git helpers and the page's heading and count patterns are the 6.4 cut's own,
imported from its test module.

Run from the repo root:
    python3 -m pytest tools/tests/test_lean_release_disclosure_v65.py
"""
# test-census-subject: docs/known-issues.md
from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_release_cut_v64 as v64  # noqa: E402 - the 6.4 cut's helpers, reused

REPO = v64.REPO
PAGE = v64.PAGE
NOTES = "docs/release-notes-v6.5.0.md"
TAG = "v6.5.0"
known_issues = v64.known_issues

#: The one sentence of the notes `known_issues.py write` fills, with its three figures.
COUNT_LINE = re.compile(
    r"^\*\*v6\.5\.0 discloses (\d+) open defects: (\d+) Medium, (\d+) Low\.\*\*$", re.M)
#: The bar D0560 sets for 6.5, as the page's v6.5 section must lead with it. Pinned here rather
#: than read from `known_issues.BARS`, so a weaker sentence written there is refused, not echoed.
BAR_V65 = "Fewer than 50 open bugs at the tag, and none at Medium or above."
#: The v6.0 bar, which the 6.5 page keeps as history below the bar in force.
BAR_V60 = ("Zero open Critical or High finding at the tag, and every open Medium ruled by one "
           "triage decision.")
#: The statuses a finding leaves by without a fix, which the page's Not carried section names.
NOT_FIXED = ("won't fix", "superseded")
#: D0560's ceiling: 6.5 ships with fewer than this many open findings.
CEILING = 50
#: The severities D0560 allows none of at the tag: Medium and above.
BARRED = ("medium", "high", "critical")


def cut_revision() -> tuple[str | None, str]:
    """`(revision, how)`: the commit that cut 6.5.0 and how it was found, as `v64.cut_revision`
    finds 6.4.0's. The revision is None when the working tree is the cut, its page differing from
    HEAD's because the cut is being committed now."""
    tag = v64._git("rev-parse", "-q", "--verify", f"refs/tags/{TAG}^{{commit}}")
    if tag.returncode == 0:
        return tag.stdout.strip(), f"the {TAG} tag"
    diff = v64._git("diff", "--quiet", "HEAD", "--", PAGE)
    if diff.returncode not in (0, 1):
        raise AssertionError(f"git cannot compare {PAGE} with HEAD: {diff.stderr.strip()}")
    if diff.returncode == 1:
        return None, "the working tree, whose page is not yet committed"
    last = v64._git("log", "-1", "--format=%H", "--", PAGE).stdout.strip()
    return (last or None), f"{last[:8]}, the commit that last wrote {PAGE}"


def section(page: str, heading: str) -> str | None:
    """The page from just below `## heading` to its end, or None when the page has no such
    heading. Found by name, never by position; `lead` reads the bold sentence it opens with."""
    marker = f"## {heading}\n"
    return page[page.index(marker) + len(marker):] if marker in page else None


def lead(body: str | None) -> str | None:
    """The bold sentence a bar section opens with, its line breaks folded to spaces, or None
    when the section does not open with one."""
    found = re.match(r"\s*\*\*(.+?)\*\*", body or "", re.S)
    return " ".join(found.group(1).split()) if found else None


def disclosure_problems(page: str, notes: str) -> list[str]:
    """Why `page` and `notes` are not what the 6.5.0 cut writes: the page names a bar series other
    than 6.5, its v6.5 section does not lead with D0560's bar, the v6.0 bar is not kept as
    history, the notes carry other than one filled count line, or that line's figures differ
    from the page's own count line. Empty when all hold."""
    problems = []
    series = v64.BAR_HEADING.findall(page)
    if series != ["6.5"]:
        problems.append(f"the page states the bar for {', '.join(series) or 'no release'}, "
                        "not v6.5")
    else:
        stated = lead(section(page, "The bar v6.5 is held to"))
        if stated != BAR_V65:
            problems.append(f"the v6.5 bar reads {stated!r}, not D0560's {BAR_V65!r}")
    if lead(section(page, "The bar v6.0 was held to, kept as history")) != BAR_V60:
        problems.append("the page does not keep the v6.0 bar as history")
    filled = COUNT_LINE.findall(notes)
    if len(filled) != 1:
        problems.append(f"the notes carry {len(filled)} filled count lines, not one")
    counted = v64.PAGE_COUNT.findall(page)
    if len(counted) != 1:
        problems.append(f"the page carries {len(counted)} count lines, not one")
    elif len(filled) == 1 and filled[0] != counted[0]:
        problems.append(f"the notes disclose {'/'.join(filled[0])} (total/Medium/Low); the page "
                        f"lists {'/'.join(counted[0])}")
    return problems


def not_carried_problems(page: str, root: Path) -> list[str]:
    """Why the page's Not carried section does not name exactly the findings in `root`'s corpus
    at Medium or above that were ruled `Won't Fix` or superseded. Empty when it does."""
    wanted = set()
    for path in (root / known_issues.BUGS_REL).glob("BG*.md"):
        row = known_issues._read(path)
        if (row is not None and row[1].strip().casefold() in NOT_FIXED
                and row[2].strip().casefold() in BARRED):
            wanted.add(row[0])
    # Only the page's closing section, which names no finding, follows Not carried.
    named = set(re.findall(r"`(BG-?\d+)`", section(page, "Not carried") or ""))
    problems = []
    if wanted - named:
        problems.append(f"the Not carried section leaves out {', '.join(sorted(wanted - named))}")
    if named - wanted:
        problems.append(f"the Not carried section names {', '.join(sorted(named - wanted))}, "
                        "which did not leave at Medium or above without a fix")
    return problems


def open_findings(root: Path) -> tuple[dict[str, str], list[str]]:
    """`({bug id: severity}, [unparseable file])` for every open finding in `root`'s corpus, at
    any severity, read as `known_issues.py` reads a finding."""
    found = {}
    for path in sorted((root / known_issues.BUGS_REL).glob("BG*.md")):
        row = known_issues._read(path)
        if row is not None and known_issues._is_open(row[1]):
            found[row[0]] = row[2]
    return found, known_issues.unparseable(root)


def bar_problems(found: dict[str, str], blind: list[str]) -> list[str]:
    """Why a corpus whose open findings are `found` misses D0560's bar for 6.5: CEILING or more
    open, any open at Medium or above, or a finding nobody can read. Empty when the bar holds."""
    problems = []
    if len(found) >= CEILING:
        problems.append(f"{len(found)} findings are open, not fewer than {CEILING}")
    above = sorted(b for b, sev in found.items() if sev.strip().casefold() in BARRED)
    if above:
        problems.append(f"{len(above)} open at Medium or above: {', '.join(above)}")
    if blind:
        problems.append(f"{len(blind)} finding(s) cannot be read: {', '.join(blind)}")
    return problems


class DisclosureTests(unittest.TestCase):

    def _release(self, tmp: str) -> tuple[Path, str | None, str]:
        """`(root, revision, how)`: the tree the release holds, exported under `tmp` unless it is
        the working tree."""
        if not v64.checkout():
            self.skipTest(f"{REPO} is not a git checkout of its own, so no commit is the cut")
        rev, how = cut_revision()
        shallow = v64._git("rev-parse", "--is-shallow-repository").stdout.strip() == "true"
        if rev is not None and shallow and how != f"the {TAG} tag":
            self.skipTest("a shallow clone cannot name the commit that last wrote the page")
        self.assertTrue(rev is not None or how.startswith("the working tree"),
                        f"no commit has written {PAGE}")
        if rev is None:
            return REPO, None, how
        root = Path(tmp)
        self.assertTrue(known_issues._export(REPO, rev, root), f"cannot read {how}")
        return root, rev, how

    def test_the_known_issues_page_is_cut_for_650(self) -> None:
        """AC1. Mutants: the page at HEAD before this cut (v6.4's heading, 369 findings, 65
        Medium); `known_issues.render(REPO, "6.5.0")` with no v6.5 row in BARS, which heads "The
        bar v6.5 is held to" with v6.0's sentence; the v6.0 row dropped, so no history keeps it;
        a notes count line whose figures disagree with the page's, doubled, or left unfilled. The
        controls run first, on a page `known_issues.render` cuts for 6.5.0 from a fixture corpus,
        so they run where no commit can be named as the release too. Mutants of the Not carried
        section: read under Critical and High, as the v6.0 bar reads it, so the Medium findings
        ruled `Won't Fix` or superseded are left out."""
        with tempfile.TemporaryDirectory(prefix="us1331_fixture_") as tmp:
            bugs = Path(tmp) / known_issues.BUGS_REL
            bugs.mkdir(parents=True)
            for bid, status, severity in (
                    ("BG9001", "Open", "Medium"), ("BG9002", "Open", "Low"),
                    ("BG9003", "Open", "Low"), ("BG9004", "Won't Fix", "Medium"),
                    ("BG9005", "Superseded", "High"), ("BG9006", "Superseded", "medium"),
                    ("BG9007", "Won't Fix", "Low"), ("BG9008", "Fixed", "Medium")):
                (bugs / f"{bid}-x.md").write_text(f"# {bid}: a finding\n\n> **Status:** {status}\n"
                                                  f"> **Severity:** {severity}\n", encoding="utf-8")
            page = known_issues.render(Path(tmp), "6.5.0")
            self._refuses_what_the_650_cut_does_not_write(
                page, "# v6.5.0\n\n**v6.5.0 discloses 3 open defects: 1 Medium, 2 Low.**\n")
            self.assertEqual([], not_carried_problems(page, Path(tmp)))
            trimmed = (page.split("\n## Not carried")[0] + "\n## Not carried"
                       + known_issues.render(Path(tmp), "6.0.0").split("\n## Not carried")[1])
            self.assertEqual(["the Not carried section leaves out BG9004, BG9006"],
                             not_carried_problems(trimmed, Path(tmp)))
            padded = page.replace("`BG9005`", "`BG9005`, `BG9007`")
            self.assertEqual([("the Not carried section names BG9007, which did not leave at "
                               "Medium or above without a fix")],
                             not_carried_problems(padded, Path(tmp)))
        with tempfile.TemporaryDirectory(prefix="us1331_cut_") as tmp:
            root, rev, how = self._release(tmp)
            at = () if rev is None else ("--at", rev)
            check = v64._known_issues("check", "--root", str(REPO), *at)
            self.assertEqual(0, check.returncode, f"`known_issues.py check` refuses the page at "
                             f"{how}:\n{check.stdout}{check.stderr}")
            page = (root / PAGE).read_text(encoding="utf-8")
            self.assertEqual([], not_carried_problems(page, root), how)
        # `_export` copies the page and the corpus only, so the notes are read from the release
        # itself. `git show` prints nothing for notes the commit does not hold, and notes with no
        # count line are a problem the check names.
        if rev is None:
            notes = (REPO / NOTES).read_text(encoding="utf-8")
        else:
            notes = v64._git("show", f"{rev}:{NOTES}").stdout
        self.assertEqual([], disclosure_problems(page, notes), how)

    def _refuses_what_the_650_cut_does_not_write(self, page: str, notes: str) -> None:
        """`disclosure_problems` accepts the 6.5.0 cut of `page` and `notes`, and refuses each
        mutant of them with its own problem."""
        self.assertEqual([], disclosure_problems(page, notes))
        self.assertEqual(["the page states the bar for 6.4, not v6.5"], disclosure_problems(
            page.replace("## The bar v6.5 is held to", "## The bar v6.4 is held to"), notes))
        v60 = next(prose for _s, name, _b, prose in known_issues.BARS if name == "v6.0")
        v65 = next(prose for _s, name, _b, prose in known_issues.BARS if name == "v6.5")
        self.assertIn(v65, page)
        self.assertEqual(
            [f"the v6.5 bar reads {BAR_V60!r}, not D0560's {BAR_V65!r}"],
            disclosure_problems(page.replace(v65, v60, 1), notes))
        history = "## The bar v6.0 was held to, kept as history\n\n"
        self.assertEqual(["the page does not keep the v6.0 bar as history"],
                         disclosure_problems(page.replace(history + v60, ""), notes))
        line = COUNT_LINE.search(notes).group(0)
        total, mediums, lows = COUNT_LINE.search(notes).groups()
        off = line.replace(f"{lows} Low", f"{int(lows) + 1} Low")
        self.assertEqual(
            [(f"the notes disclose {total}/{mediums}/{int(lows) + 1} (total/Medium/Low); the page "
              f"lists {total}/{mediums}/{lows}")],
            disclosure_problems(page, notes.replace(line, off)))
        self.assertEqual(["the notes carry 2 filled count lines, not one"],
                         disclosure_problems(page, notes.replace(line, f"{line}\n\n{line}")))
        unfilled = "**v6.5.0 discloses N open defects: N Medium, N Low.**"
        self.assertEqual(["the notes carry 0 filled count lines, not one"],
                         disclosure_problems(page, notes.replace(line, unfilled)))

    def test_the_release_bars_hold_at_the_cut(self) -> None:
        """AC2. Mutants: the corpus of the commit that cut 6.4.0 (369 open findings, 65 of them
        Medium); `bar --at v6.5.0` run before the tag exists, which exits 2; a cut made while 50
        findings are open, or one at Medium, High or Critical, or one nobody can read. The
        controls run first, on fixtures, so they run where no commit can be named as the release
        too."""
        self._refuses_a_corpus_the_65_bar_does_not_allow()
        with tempfile.TemporaryDirectory(prefix="us1331_bar_") as tmp:
            root, _rev, how = self._release(tmp)
            found, blind = open_findings(root)
        self.assertEqual([], bar_problems(found, blind), how)
        tagged = how == f"the {TAG} tag"
        bar = v64._known_issues("bar", "--root", str(REPO), *(("--at", TAG) if tagged else ()))
        self.assertEqual(0, bar.returncode, f"`known_issues.py bar` refuses the release:\n"
                         f"{bar.stdout}{bar.stderr}")
        if not tagged:
            early = v64._known_issues("bar", "--root", str(REPO), "--at", TAG)
            self.assertEqual(2, early.returncode, "`bar --at` a tag nobody cut must not pass")

    def _refuses_a_corpus_the_65_bar_does_not_allow(self) -> None:
        """`bar_problems` refuses each corpus D0560's bar does not allow, and `open_findings`
        reads open findings only, naming a finding it cannot parse."""
        cut_640 = {f"BG{i:04d}": "Medium" if i < 65 else "Low" for i in range(369)}
        self.assertEqual(["369 findings are open, not fewer than 50",
                          f"65 open at Medium or above: {', '.join(sorted(cut_640)[:65])}"],
                         bar_problems(cut_640, []))
        fifty = {f"BG{i:04d}": "Low" for i in range(CEILING)}
        self.assertEqual(["50 findings are open, not fewer than 50"], bar_problems(fifty, []))
        self.assertEqual([], bar_problems(dict(list(fifty.items())[:CEILING - 1]), []))
        for severity in ("Medium", "high", " Critical "):
            with self.subTest(severity=severity):
                self.assertEqual(["1 open at Medium or above: BG9001"],
                                 bar_problems({"BG9001": severity, "BG9002": "Low"}, []))
        self.assertEqual(["1 finding(s) cannot be read: BG9003-x.md"],
                         bar_problems({"BG9002": "Low"}, ["BG9003-x.md"]))
        with tempfile.TemporaryDirectory(prefix="us1331_corpus_") as tmp:
            bugs = Path(tmp) / known_issues.BUGS_REL
            bugs.mkdir(parents=True)
            for bid, status, severity in (("BG9001", "Fixed", "Medium"), ("BG9002", "Open", "Low"),
                                          ("BG9004", "Won't Fix", "High")):
                (bugs / f"{bid}-x.md").write_text(f"# {bid}: a finding\n\n> **Status:** {status}\n"
                                                  f"> **Severity:** {severity}\n", encoding="utf-8")
            (bugs / "BG9003-x.md").write_text("# no heading a reader parses\n", encoding="utf-8")
            self.assertEqual(({"BG9002": "Low"}, [f"{known_issues.BUGS_REL}/BG9003-x.md"]),
                             open_findings(Path(tmp)))


if __name__ == "__main__":
    unittest.main()
