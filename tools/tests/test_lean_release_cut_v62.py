"""US1111: v6.2.0 is cut through the shipped release path.

AC2 judges the disclosure at the commit that cut 6.2.0, never at the live corpus, because
`gate.py --release` runs every story's Verify at each later cut and a finding filed after this
one must not turn it red (BG1054). That commit is the v6.2.0 tag once it exists, else the commit
that last wrote `docs/known-issues.md`. While the cut is being committed, the page in the working
tree differs from HEAD's, and the working tree is then the commit about to be made, so it is the
one judged. AC3's notes link is read against the anchor of the CHANGELOG's own `## [6.2.0]`
heading. Each check returns its problems and is run on a mutated copy it must refuse.

Run from the repo root:
    python3 -m pytest tools/tests/test_lean_release_cut_v62.py
"""
# test-census-subject: docs/known-issues.md
from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
KNOWN_ISSUES = REPO / "tools" / "known_issues.py"
CHANGELOG = REPO / "CHANGELOG.md"
PAGE = "docs/known-issues.md"
NOTES = "docs/release-notes-v6.2.0.md"
TAG = "v6.2.0"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


known_issues = _load("known_issues")  # the page's own reader: its export of a committed corpus
check_links = _load("check_links")    # the slug a CHANGELOG heading's anchor is spelt by

#: The one sentence of the notes `known_issues.py write` fills, with its three figures.
COUNT_LINE = re.compile(
    r"^\*\*v6\.2\.0 discloses (\d+) open defects: (\d+) Medium, (\d+) Low\.\*\*$", re.M)
#: The page's own count line, as `known_issues.render` writes it below the table.
PAGE_COUNT = re.compile(r"^(\d+) findings: (\d+) Medium, (\d+) Low\.$", re.M)
#: The heading a page names its release series in, which `known_issues.py check` reads it by.
BAR_HEADING = re.compile(r"^## The bar v(\d+\.\d+) is held to$", re.M)
CHANGELOG_LINK = re.compile(r"\]\(\.\./CHANGELOG\.md#([\w-]+)\)")


def _env() -> dict:
    """This environment without the GIT_ variables a hook exports, so git reads this clone."""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True,
                          env=_env(), timeout=120, check=False)


def _known_issues(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(KNOWN_ISSUES), *args], capture_output=True,
                          text=True, env=_env(), timeout=300, check=False)


def checkout() -> bool:
    """Whether this tree is the top of its own git work tree. A copy of its files with no history,
    as `test_lean_release_notes` makes to file a finding in, is not, and names no commit."""
    top = _git("rev-parse", "--show-toplevel")
    return top.returncode == 0 and Path(top.stdout.strip()).resolve() == REPO.resolve()


def cut_revision() -> tuple[str | None, str]:
    """`(revision, how)`: the commit that cut 6.2.0 and how it was found. The revision is None
    when the working tree is the cut, its page differing from HEAD's because the cut is being
    committed now. A comparison git cannot make raises rather than reading as a difference."""
    tag = _git("rev-parse", "-q", "--verify", f"refs/tags/{TAG}^{{commit}}")
    if tag.returncode == 0:
        return tag.stdout.strip(), f"the {TAG} tag"
    diff = _git("diff", "--quiet", "HEAD", "--", PAGE)
    if diff.returncode not in (0, 1):
        raise AssertionError(f"git cannot compare {PAGE} with HEAD: {diff.stderr.strip()}")
    if diff.returncode == 1:
        return None, "the working tree, whose page is not yet committed"
    last = _git("log", "-1", "--format=%H", "--", PAGE).stdout.strip()
    return (last or None), f"{last[:8]}, the commit that last wrote {PAGE}"


def disclosure_problems(page: str, notes: str) -> list[str]:
    """Why `page` and `notes` are not what the 6.2.0 cut writes: the page names a bar series other
    than 6.2, the notes carry other than one filled count line, or that line's figures differ from
    the page's own count line. Empty when all three hold."""
    problems = []
    series = BAR_HEADING.findall(page)
    if series != ["6.2"]:
        problems.append(f"the page states the bar for {', '.join(series) or 'no release'}, "
                        "not v6.2")
    filled = COUNT_LINE.findall(notes)
    if len(filled) != 1:
        problems.append(f"the notes carry {len(filled)} filled count lines, not one")
    counted = PAGE_COUNT.findall(page)
    if len(counted) != 1:
        problems.append(f"the page carries {len(counted)} count lines, not one")
    elif len(filled) == 1 and filled[0] != counted[0]:
        problems.append(f"the notes disclose {'/'.join(filled[0])} (total/Medium/Low); the page "
                        f"lists {'/'.join(counted[0])}")
    return problems


def notes_link_problems(notes: str, changelog: str) -> list[str]:
    """Why the 6.2.0 notes do not link the CHANGELOG's `## [6.2.0]` section, or still link
    `[Unreleased]`."""
    heading = re.search(r"^## \[6\.2\.0\] - \d{4}-\d{2}-\d{2}$", changelog, re.M)
    if not heading:
        return ["the CHANGELOG has no `## [6.2.0] - <date>` heading"]
    anchor = check_links.slug(heading.group(0)[3:])
    links = CHANGELOG_LINK.findall(notes)
    problems = [] if anchor in links else [f"the notes do not link #{anchor}"]
    if "unreleased" in links:
        problems.append("the notes still link #unreleased")
    return problems


class ReleaseCutTests(unittest.TestCase):

    def test_the_known_issues_page_is_cut_for_620(self) -> None:
        """AC2. Mutants: the 6.1.0 page left in place (its heading names v6.1); a count line whose
        figures disagree with the page's; the count line doubled, or left unfilled."""
        if not checkout():
            self.skipTest(f"{REPO} is not a git checkout of its own, so no commit is the cut")
        rev, how = cut_revision()
        shallow = _git("rev-parse", "--is-shallow-repository").stdout.strip() == "true"
        if rev is not None and shallow and how != f"the {TAG} tag":
            self.skipTest("a shallow clone cannot name the commit that last wrote the page")
        self.assertTrue(rev is not None or how.startswith("the working tree"),
                        f"no commit has written {PAGE}")
        with tempfile.TemporaryDirectory(prefix="us1111_cut_") as tmp:
            if rev is None:
                root = REPO
                check = _known_issues("check", "--root", str(REPO))
                notes = (REPO / NOTES).read_text(encoding="utf-8")
            else:
                root = Path(tmp)
                self.assertTrue(known_issues._export(REPO, rev, root), f"cannot read {how}")
                check = _known_issues("check", "--root", str(REPO), "--at", rev)
                shown = _git("show", f"{rev}:{NOTES}")
                self.assertEqual(0, shown.returncode, f"{NOTES} is not in {how}")
                notes = shown.stdout
            self.assertEqual(0, check.returncode, f"`known_issues.py check` refuses the page at "
                             f"{how}:\n{check.stdout}{check.stderr}")
            bar = _known_issues("bar", "--root", str(root))
            self.assertEqual(0, bar.returncode, f"`known_issues.py bar` refuses {how}:\n"
                             f"{bar.stdout}{bar.stderr}")
            page = (root / PAGE).read_text(encoding="utf-8")
        self.assertEqual([], disclosure_problems(page, notes), how)

        line = COUNT_LINE.search(notes).group(0)
        total, mediums, lows = COUNT_LINE.search(notes).groups()
        off = line.replace(f"{mediums} Medium", f"{int(mediums) + 1} Medium")
        self.assertEqual(
            ["the page states the bar for 6.1, not v6.2"],
            disclosure_problems(page.replace("## The bar v6.2 is held to",
                                             "## The bar v6.1 is held to"), notes))
        self.assertEqual(
            [f"the notes disclose {total}/{int(mediums) + 1}/{lows} (total/Medium/Low); the page "
             f"lists {total}/{mediums}/{lows}"],
            disclosure_problems(page, notes.replace(line, off)))
        self.assertEqual(["the notes carry 2 filled count lines, not one"],
                         disclosure_problems(page, notes.replace(line, f"{line}\n\n{line}")))
        unfilled = "**v6.2.0 discloses N open defects: N Medium, N Low.**"
        self.assertEqual(["the notes carry 0 filled count lines, not one"],
                         disclosure_problems(page, notes.replace(line, unfilled)))

    def test_the_notes_link_the_620_section(self) -> None:
        """AC3. Mutants: the notes' CHANGELOG link left at `#unreleased`; the CHANGELOG with no
        6.2.0 heading."""
        notes = (REPO / NOTES).read_text(encoding="utf-8")
        changelog = CHANGELOG.read_text(encoding="utf-8")
        self.assertEqual([], notes_link_problems(notes, changelog))
        anchor = next(a for a in CHANGELOG_LINK.findall(notes) if a.startswith("620-"))
        stale = notes.replace(f"#{anchor})", "#unreleased)")
        self.assertNotEqual(notes, stale)
        self.assertEqual([f"the notes do not link #{anchor}", "the notes still link #unreleased"],
                         notes_link_problems(stale, changelog))
        uncut = re.sub(r"^## \[6\.2\.0\] - ", "## [6.2.0-draft] - ", changelog, flags=re.M)
        self.assertEqual(["the CHANGELOG has no `## [6.2.0] - <date>` heading"],
                         notes_link_problems(notes, uncut))


if __name__ == "__main__":
    unittest.main()
