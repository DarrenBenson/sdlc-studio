"""BG1066: the product seat approves a story serving a declared Secondary's goal, and with more
than one Primary judges a unit against the Primary of the interface it touches.

The cards are read whole, because `critic.py brief` hands the reviewer the whole card ("Read and
adopt the charter at ..."), so the sentences checked here are the ones a reviewer is actually
given. The three sentences that decide approval are found by their own headings - the first
Craft Goal, the Lens's first question, the Authority's Approves line - so a fourth place that
restates the rule is not exempted by being unnamed here.
"""
# test-census-subject: .claude/skills/sdlc-studio/templates/personas/amigos/product.md
import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
REPO = SKILL.parents[2]
SHIPPED = SKILL / "templates" / "personas" / "amigos" / "product.md"
PROJECT = REPO / "sdlc-studio" / "personas" / "seats" / "product.md"


def section(text: str, heading: str) -> str:
    match = re.search(rf"^##\s+{re.escape(heading)}[^\n]*\n(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    return match.group(1) if match else ""


def approval_sentences(text: str) -> dict[str, str]:
    """The sentences that decide what the seat approves, each found by its own heading."""
    craft = re.search(r"^1\.\s.*?(?=^\d\.\s|\Z)", section(text, "Craft Goals"), re.M | re.S)
    lens = re.search(r"^-\s.*?(?=^-\s|\Z)", section(text, "Lens"), re.M | re.S)
    approves = re.search(r"^-\s\*\*Approves:\*\*.*?(?=^-\s|\Z)", section(text, "Authority / Scope"),
                         re.M | re.S)
    work = section(text, "How They Work")
    found = {"craft goal 1": craft.group(0) if craft else "", "lens": lens.group(0) if lens else "",
             "approves": approves.group(0) if approves else "", "work render": work}
    return {k: " ".join(v.split()) for k, v in found.items()}


def cards() -> list[Path]:
    return [SHIPPED] + ([PROJECT] if PROJECT.exists() else [])


class ProductSeatLensTests(unittest.TestCase):

    def test_product_seat_admits_a_secondary_goal(self) -> None:
        """AC1. Mutant: any card's approval sentence back to 'a Primary-persona goal' alone."""
        for card in cards():
            sentences = approval_sentences(card.read_text(encoding="utf-8"))
            self.assertTrue(all(sentences.values()), f"{card}: an approval sentence is missing")
            for where, sentence in sentences.items():
                self.assertIn("Secondary", sentence, f"{card} ({where}) admits no Secondary goal")

    def test_product_seat_judges_against_the_interfaces_primary(self) -> None:
        """AC2. Mutants: an approval sentence naming 'the Primary' with no interface; the project
        card declaring one person as the design persona; a shipped-product unit not routed to
        the shipped product's Primary."""
        for card in cards():
            text = card.read_text(encoding="utf-8")
            for where, sentence in approval_sentences(text).items():
                self.assertIn("interface", sentence, f"{card} ({where}) names no interface")
            self.assertRegex(" ".join(section(text, "How They Work").split()),
                             r"touching the shipped product is judged against the shipped "
                             r"product's Primary", f"{card}: a shipped unit is not routed")
            self.assertNotRegex(text, r"(?i)the Primary\s+design\s+persona\s+is\b",
                                f"{card} names a single Primary as the design persona")
        if not PROJECT.exists():
            self.skipTest("no project seat card in this checkout - the shipped card is checked")

    def test_a_single_primary_cast_reads_as_before(self) -> None:
        """AC3. Mutant: the shipped card's Approves line losing its one-Primary fallback, so a
        consuming project with one Primary and no interfaces reads a rule it cannot apply."""
        approves = approval_sentences(SHIPPED.read_text(encoding="utf-8"))["approves"]
        self.assertRegex(approves, r"With one Primary and no interfaces declared, that is the "
                                   r"Primary\.")
        work = approval_sentences(SHIPPED.read_text(encoding="utf-8"))["work render"]
        self.assertIn("with one Primary and no interfaces declared, that is simply the Primary", work)


if __name__ == "__main__":
    unittest.main()
