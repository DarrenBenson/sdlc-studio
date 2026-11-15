"""The front page and the 6.2 notes claim only what the shipped self-check default enforces.

`review.author_self_check` ships as `report`, under which a review brief prints with a notice
naming the missing self-check; only `block` refuses it. So no public line may say a reviewer
judges only work its author has self-checked: the 6.2 notes' first theme and its row in the
Sources table say a review brief can require the author's own check first, and no README line
naming the self-check says the reviewer is held to self-checked work. Each check returns its
problems and runs on the live page and on the old wording beside it, which it must refuse.
"""
# test-census-subject: README.md
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
README = REPO / "README.md"
NOTES = REPO / "docs" / "release-notes-v6.2.0.md"
DEFAULTS = REPO / ".claude" / "skills" / "sdlc-studio" / "templates" / "config-defaults.yaml"

#: What the theme now says, read with backticks, bold and case set aside.
CAN_REQUIRE = "a review brief can require the author's own check first"
#: A sentence that says a reviewer is held to self-checked work, whatever the default.
ENFORCED = re.compile(
    r"\bjudges?\s+only\b[^.|]*\bself-check"
    r"|\bonly\s+(?:reviews?|judges?|sees?)\b[^.|]*\bself-check"
    r"|\b(?:reviews?|reviewers?|briefs?)\b[^.|]*\bonly\b[^.|]*\bself-checked\b"
    r"|\bself-checks?\s+(?:is|are)\s+(?:always\s+)?(?:enforced|required|mandatory)\b",
    re.I)
OLD_THEME = "A reviewer judges only work its author has self-checked"


def _norm(text: str) -> str:
    return " ".join(text.replace("`", "").replace("**", "").lower().split())


def _section(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return match.group(1) if match else ""


def first_theme_bullet(text: str) -> str:
    """The first bullet of 'What changed for you', its wrapped lines joined."""
    body = _section(text, "What changed for you")
    match = re.search(r"^- (.*?)(?=^- |^\S|\Z)", body, re.M | re.S)
    return " ".join(match.group(1).split()) if match else ""


def theme_row(text: str, theme_opening: str) -> str:
    """The Sources table row whose passage opens as the first theme's bold lead does."""
    for line in _section(text, "Sources").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and cells and _norm(cells[0]).startswith(theme_opening):
            return line
    return ""


def notes_problems(text: str) -> list[str]:
    problems = []
    bullet = first_theme_bullet(text)
    lead = re.match(r"\*\*(.*?)\*\*", bullet)
    if not lead:
        return ["the first theme bullet has no bold lead"]
    if CAN_REQUIRE not in _norm(lead.group(1)):
        problems.append(f"the first theme's lead does not say {CAN_REQUIRE!r}: {lead.group(1)!r}")
    row = theme_row(text, "a review brief can require")
    if not row:
        problems.append("the Sources table has no row for the first theme")
    elif CAN_REQUIRE not in _norm(row):
        problems.append(f"the first theme's Sources row does not say {CAN_REQUIRE!r}: {row!r}")
    for where, line in (("first theme bullet", bullet), ("Sources table", _section(text, "Sources"))):
        problems += [f"the {where} says a reviewer judges only self-checked work: {m.group(0)!r}"
                     for m in ENFORCED.finditer(line)]
    return problems


def readme_problems(text: str) -> list[str]:
    """Every line naming the author's self-check, and none saying it is enforced."""
    return [f"README line {n} says a reviewer judges only self-checked work: {line.strip()!r}"
            for n, line in enumerate(text.splitlines(), 1)
            if re.search(r"self-check", line, re.I) and ENFORCED.search(line)]


class SelfCheckClaimWordingTests(unittest.TestCase):
    def test_the_shipped_default_only_reports_a_missing_self_check(self) -> None:
        """The premise: the key ships as `report`, so an enforcement claim would be false."""
        defaults = DEFAULTS.read_text(encoding="utf-8")
        self.assertRegex(defaults, r"(?m)^\s+author_self_check:\s*report\b")

    def test_the_62_notes_say_a_brief_can_require_the_self_check(self) -> None:
        """AC1: the first theme bullet and its Sources row say a brief can require the
        author's own check first, and neither says a reviewer judges only self-checked work.
        The old heading, in the bullet or in the row, is refused."""
        live = NOTES.read_text(encoding="utf-8")
        self.assertEqual(notes_problems(live), [])
        lead = re.search(r"^- \*\*(.*?)\*\*", _section(live, "What changed for you"), re.M)
        self.assertIsNotNone(lead)
        old_bullet = live.replace(f"**{lead.group(1)}**", f"**{OLD_THEME}.**", 1)
        self.assertTrue(any("first theme's lead" in p for p in notes_problems(old_bullet)))
        self.assertTrue(any("judges only" in p for p in notes_problems(old_bullet)))
        row = theme_row(live, "a review brief can require")
        old_row = live.replace(row, re.sub(r"^\|[^|]*\|", f"| {OLD_THEME} |", row), 1)
        self.assertTrue(any("Sources table has no row" in p for p in notes_problems(old_row)))
        both = old_row + f"\n| {CAN_REQUIRE} - {OLD_THEME} | US1087 |\n"
        self.assertTrue(any("Sources table says" in p for p in notes_problems(both)))

    def test_the_readme_claims_no_enforced_self_check(self) -> None:
        """AC2: no README line naming the self-check says a reviewer judges only
        self-checked work; the 6.2.0 line as it stood is refused, a fair one passes."""
        self.assertEqual(readme_problems(README.read_text(encoding="utf-8")), [])
        old = ("- [docs/release-notes-v6.2.0.md](docs/release-notes-v6.2.0.md) - a reviewer "
               "judges only work its author has self-checked, one command gives a builder its "
               "whole brief")
        self.assertEqual(len(readme_problems(old)), 1)
        for planted in ("Reviewers only see self-checked units.",
                        "The author's self-check is enforced on every unit."):
            self.assertEqual(len(readme_problems(planted)), 1, planted)
        fair = "A review brief can require the author's self-check first; `report` is the default."
        self.assertEqual(readme_problems(fair), [])


if __name__ == "__main__":
    unittest.main()
