"""`docs/known-issues.md` is derived from the bug corpus, and this is what makes that true.

The page says a release discloses every open Medium and Low finding by id. A disclosure
maintained by hand decays in the direction that flatters: a bug filed after the page was
written is simply absent, and nothing notices. So the id set is compared against the
corpus in both directions, and the counts the prose states are read back out of the table
rather than trusted.

Mutants this must fail on: delete a row from the table; add a row for a bug that is not
open; change the `38 findings: 37 Medium, 1 Low` line without changing the table.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PAGE = REPO / "docs" / "known-issues.md"
BUGS = REPO / "sdlc-studio" / "bugs"

DISCLOSED = {"Medium", "Low"}


def corpus() -> dict[str, str]:
    """`{bug id: severity}` for every bug at `Open` whose severity is disclosed."""
    found: dict[str, str] = {}
    for path in sorted(BUGS.glob("BG*.md")):
        text = path.read_text(encoding="utf-8")
        status = re.search(r"^> \*\*Status:\*\* *(.+)$", text, re.M)
        severity = re.search(r"^> \*\*Severity:\*\* *(.+)$", text, re.M)
        heading = re.search(r"^# (BG\d+):", text, re.M)
        if not (status and severity and heading):
            continue
        if status.group(1).strip() != "Open":
            continue
        sev = severity.group(1).strip()
        if sev in DISCLOSED:
            found[heading.group(1)] = sev
    return found


def listed() -> dict[str, str]:
    """`{bug id: severity}` as the page's table states it."""
    rows = re.findall(r"^\| `(BG\d+)` \| (\w+) \|", PAGE.read_text(encoding="utf-8"), re.M)
    return dict(rows)


class KnownIssuesPageTests(unittest.TestCase):
    def test_page_exists(self):
        self.assertTrue(PAGE.exists(), f"{PAGE} is the release disclosure and is missing")

    def test_every_open_medium_or_low_bug_is_disclosed(self):
        missing = sorted(set(corpus()) - set(listed()))
        self.assertEqual(
            [], missing,
            "open findings absent from docs/known-issues.md - a release would ship them "
            f"undisclosed: {', '.join(missing)}",
        )

    def test_nothing_is_listed_that_is_not_open(self):
        extra = sorted(set(listed()) - set(corpus()))
        self.assertEqual(
            [], extra,
            "docs/known-issues.md lists findings that are not open at a disclosed "
            f"severity - the page is stale: {', '.join(extra)}",
        )

    def test_severities_agree_with_the_corpus(self):
        page, real = listed(), corpus()
        wrong = {b: (page[b], real[b]) for b in sorted(set(page) & set(real)) if page[b] != real[b]}
        self.assertEqual({}, wrong, f"severity disagrees with the bug file: {wrong}")

    def test_the_stated_counts_are_read_from_the_table(self):
        """The prose states a total and a split. Both are derived here, so neither can drift."""
        page = listed()
        total = len(page)
        mediums = sum(1 for s in page.values() if s == "Medium")
        lows = sum(1 for s in page.values() if s == "Low")
        text = PAGE.read_text(encoding="utf-8")
        expected = f"{total} findings: {mediums} Medium, {lows} Low."
        self.assertIn(
            expected, text,
            f"the page's count line does not match its own table; it should read: {expected}",
        )


if __name__ == "__main__":
    unittest.main()
