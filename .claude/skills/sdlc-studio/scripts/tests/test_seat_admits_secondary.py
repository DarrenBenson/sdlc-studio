"""BG1066: the product seat approves a story serving a declared Secondary's goal, never at the
Primary's expense, and with more than one Primary judges a unit against the Primary of the
interface its Affects touch.

The cards are read whole, because `critic.py brief` hands the reviewer the whole card ("Read and
adopt the charter at ..."), so the sentences checked here are the ones a reviewer is actually
given. The four sentences that decide approval are found by their own headings - the first Craft
Goal, the work render, the Lens's first question, the Authority's Approves line - and each must
state the RULE, not merely use its words: a test that only looks for "Secondary" passes a card
that says "never of a declared Secondary", and one that only looks for "interface" passes "any
Primary, whatever interface it touches" (round 1 of this unit's review).
"""
# test-census-subject: .claude/skills/sdlc-studio/templates/personas/amigos/product.md
import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
REPO = SKILL.parents[2]
SHIPPED = SKILL / "templates" / "personas" / "amigos" / "product.md"
PROJECT = REPO / "sdlc-studio" / "personas" / "seats" / "product.md"
REGISTRY = REPO / "sdlc-studio" / "personas" / "index.md"

#: AC1: a declared Secondary is admitted, and only ever behind the Primary.
ADMITS_SECONDARY = re.compile(r"or of a declared Secondary, never at that Primary's expense")
#: AC2: the Primary judged against is the one for the interface the unit's Affects touch.
ROUTES_BY_INTERFACE = re.compile(r"the Primary for the interface (?:the story's|its) Affects touch\b")


def section(text: str, heading: str) -> str:
    match = re.search(rf"^##\s+{re.escape(heading)}[^\n]*\n(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    return match.group(1) if match else ""


def approval_sentences(text: str) -> dict[str, str]:
    """The sentences that decide what the seat approves, each found by its own heading."""
    craft = re.search(r"^1\.\s.*?(?=^\d\.\s|\Z)", section(text, "Craft Goals"), re.M | re.S)
    lens = re.search(r"^-\s.*?(?=^-\s|\Z)", section(text, "Lens"), re.M | re.S)
    approves = re.search(r"^-\s\*\*Approves:\*\*.*?(?=^-\s|\Z)", section(text, "Authority / Scope"),
                         re.M | re.S)
    found = {"craft goal 1": craft.group(0) if craft else "", "lens": lens.group(0) if lens else "",
             "approves": approves.group(0) if approves else "",
             "work render": section(text, "How They Work")}
    return {k: " ".join(v.split()) for k, v in found.items()}


def cards() -> list[Path]:
    return [SHIPPED] + ([PROJECT] if PROJECT.exists() else [])


def registry_names() -> list[str]:
    """Every persona the project's registry declares, read from it, never written here."""
    if not REGISTRY.exists():
        return []
    return re.findall(r"^\s*-\s+\[([^\]]+)\]\(", REGISTRY.read_text(encoding="utf-8"), re.M)


class ProductSeatLensTests(unittest.TestCase):

    def test_product_seat_admits_a_secondary_goal(self) -> None:
        """AC1. Mutants: an approval sentence back to 'a Primary-persona goal' alone; the
        qualifier 'never at that Primary's expense' dropped or turned to 'even at'; the Secondary
        excluded ('never of a declared Secondary')."""
        for card in cards():
            sentences = approval_sentences(card.read_text(encoding="utf-8"))
            self.assertTrue(all(sentences.values()), f"{card}: an approval sentence is missing")
            for where, sentence in sentences.items():
                self.assertRegex(sentence, ADMITS_SECONDARY,
                                 f"{card} ({where}) does not admit a declared Secondary behind "
                                 f"the Primary")

    def test_product_seat_judges_against_the_interfaces_primary(self) -> None:
        """AC2. Mutants: an approval sentence naming any Primary rather than the one for the
        interface the unit's Affects touch; a shipped-product unit not routed to the shipped
        product's Primary; the project card declaring one registry persona as the design
        persona, in either word order."""
        for card in cards():
            text = card.read_text(encoding="utf-8")
            for where, sentence in approval_sentences(text).items():
                self.assertRegex(sentence, ROUTES_BY_INTERFACE,
                                 f"{card} ({where}) does not route by the interface its Affects touch")
            self.assertRegex(" ".join(section(text, "How They Work").split()),
                             r"touching the shipped product is judged against the shipped "
                             r"product's Primary", f"{card}: a shipped unit is not routed")
        if not PROJECT.exists():
            self.skipTest("no project seat card in this checkout - the shipped card is checked")
        project = " ".join(PROJECT.read_text(encoding="utf-8").split())
        names = registry_names()
        self.assertTrue(names, "the project registry declares no persona to check against")
        for name in names:
            self.assertNotRegex(project, rf"{re.escape(name)}[^.]{{0,40}}\bdesign persona\b",
                                f"the project card names {name} as the design persona")
            self.assertNotRegex(project, rf"\bdesign persona\b[^.]{{0,40}}{re.escape(name)}",
                                f"the project card names {name} as the design persona")

    def test_a_single_primary_cast_reads_as_before(self) -> None:
        """AC3. Mutant: the shipped card's Approves line or work render losing its one-Primary
        fallback, so a consuming project with one Primary and no interfaces reads a rule it
        cannot apply."""
        sentences = approval_sentences(SHIPPED.read_text(encoding="utf-8"))
        self.assertRegex(sentences["approves"],
                         r"With one Primary and no interfaces declared, that is the Primary\.")
        self.assertIn("with one Primary and no interfaces declared, that is simply the Primary",
                      sentences["work render"])


if __name__ == "__main__":
    unittest.main()
