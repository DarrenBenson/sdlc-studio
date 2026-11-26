"""US1340: what a seat may change in the document it reviews against, and what it proposes.

The seats section of reference-workflow-personas.md says a seat's delegated authority lets it
correct a fact in its document (two of which the review's step 3b makes in the PRD unasked),
that a change to what the document requires goes to the person as a proposed change request,
and that a seat unsure which kind a change is treats it as a proposal and asks the person.
"""
from __future__ import annotations

# test-census-subject: .claude/skills/sdlc-studio/reference-workflow-personas.md
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
sys.path.insert(0, str(REPO / "tools"))

import check_links  # noqa: E402

PERSONAS_PAGE = SKILL / "reference-workflow-personas.md"
REVIEW_PAGE = SKILL / "reference-review.md"
#: The review step that applies a correction of fact without confirmation.
AUTO_APPLY_HEADING = "### 3b. Auto-Apply Mechanical Fixes"


def normalise(text: str) -> str:
    """Strip blockquote marks and bold, and join the lines into one."""
    lines = [re.sub(r"^\s*(?:>\s?)+", "", line) for line in text.splitlines()]
    return re.sub(r"\s+", " ", " ".join(lines).replace("**", ""))


def seats_section() -> str:
    """The body of the `###` section that holds the Product Owner seat's row."""
    text = PERSONAS_PAGE.read_text(encoding="utf-8")
    row = text.index("| **Product Owner** |")
    start = text.rindex("\n### ", 0, row) + 1
    end = min(j for j in (text.find("\n### ", row), text.find("\n## ", row), len(text)) if j != -1)
    return text[start:end]


def sentences(text: str | None = None) -> list[str]:
    body = seats_section() if text is None else text
    return re.split(r"(?<=[.!?])\s+", normalise(body))


def unsure_rule(text: str | None = None) -> list[str]:
    """The sentences that tie a seat being unsure of the kind of change to proposing it."""
    return [s for s in sentences(text)
            if re.search(r"\b(?:unsure|cannot tell)\b", s) and re.search(r"\bpropos", s)]


def auto_applied() -> list[str]:
    """The items step 3b of reference-review.md lists as applied without confirmation."""
    text = REVIEW_PAGE.read_text(encoding="utf-8")
    start = text.index("**Auto-applied (no confirmation needed):**", text.index(AUTO_APPLY_HEADING))
    block = text[start:text.index("**Reported only", start)]
    return [line[2:].strip() for line in block.splitlines() if line.startswith("- ")]


#: The ask-when-unsure sentence alone, with the proposal in another sentence.
NEAR_MISS_UNSURE = "The seat asks the person when unsure. It proposes a change request."


class SeatChangeAuthorityTests(unittest.TestCase):
    def test_a_seat_may_correct_a_fact_in_its_document(self) -> None:
        """AC1. MUTANT: HEAD's section, which says nothing of what a seat may change and has no
        link to reference-review.md; a link to a step the review page does not define; and a
        sentence crediting step 3b with corrections it does not make ('the first three')."""
        said = [s for s in sentences() if "delegat" in s and re.search(r"\bcorrect a fact\b", s)]
        self.assertTrue(said, "no sentence says delegated authority lets a seat correct a fact")
        for fact in ("status", "criterion", "count", "date", "link"):
            self.assertRegex(said[0], rf"\b{fact}\b", f"the correction leaves out a {fact}")
        links = re.findall(r"\]\(reference-review\.md#([\w-]+)\)", seats_section())
        slug = check_links.slug(AUTO_APPLY_HEADING.lstrip("# "))
        self.assertIn(slug, links, "the section does not link to the review's step 3b")
        self.assertIn(AUTO_APPLY_HEADING, REVIEW_PAGE.read_text(encoding="utf-8").splitlines())
        # The sentence linking step 3b says only what step 3b's auto-applied list makes: a PRD
        # feature's status and a PRD criterion's checkbox, no count, date or link, nothing in the PVD.
        auto = auto_applied()
        self.assertTrue([i for i in auto if i.startswith("PRD feature status")], auto)
        self.assertTrue([i for i in auto if i.startswith("PRD AC checkbox")], auto)
        self.assertEqual([i for i in auto if "PVD" in i], [])
        step = [s for s in sentences() if f"reference-review.md#{slug}" in s]
        self.assertEqual(len(step), 1, "one sentence links step 3b")
        for said_of_3b in (r"\bPRD\b", r"\bstatus\b", r"\bcheckbox\b", r"\bnone\b[^.]*\bPVD\b"):
            self.assertRegex(step[0], said_of_3b)
        for word in ("count", "date", "link", "three", "five", "all", "every"):
            self.assertNotRegex(step[0], rf"\b{word}\b", f"step 3b does not make {word!r}")

    def test_a_change_to_a_requirement_is_proposed_and_the_person_decides(self) -> None:
        """AC2. MUTANT: HEAD's section, with no 'propos' before 'change' in any sentence; and a
        rule that lets a seat write the requirements it signs against."""
        said = [s for s in sentences()
                if re.search(r"\bpropos\w*\b.*\bchange request\b", s)]
        self.assertTrue(said, "no sentence says a seat proposes a change request")
        rule = said[0]
        for kind in ("requirement", "added", "removed", "reworded", "priority", "scope",
                     "wording"):
            self.assertRegex(rule, rf"\b{kind}\b", f"the proposal rule leaves out {kind}")
        self.assertRegex(rule, r"\bthe person decides\b")
        self.assertRegex(rule, r"\bnever writes the requirements it signs against\b")

    def test_a_seat_unsure_of_the_kind_proposes_and_asks(self) -> None:
        """AC3. MUTANT: HEAD's section, with no 'unsure'; and a sentence that asks the person
        when unsure without tying it to proposing the change."""
        said = unsure_rule()
        self.assertTrue(said, "no sentence ties being unsure of the kind to proposing it")
        self.assertRegex(said[0], r"\basks the person\b")
        self.assertEqual(unsure_rule(NEAR_MISS_UNSURE), [])
        self.assertTrue(unsure_rule(NEAR_MISS_UNSURE.replace(". It proposes", " and proposes")))


if __name__ == "__main__":
    unittest.main()
