"""US0567: the shipped doctrine states that a fix's author is not sufficient evidence.

The guard anchors on the RULE'S OWN passage, never on a whole-file substring. A whole-file
`assertIn` is satisfied by the Revision History row describing the change that added the
prose - which is BG0457's recorded defect, and a guard shipped in the same change that
introduces the prose is the easiest possible place to repeat it.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCTRINE = ROOT / ".claude/skills/sdlc-studio/reference-doctrine.md"
DOD = ROOT / ".claude/skills/sdlc-studio/templates/core/definition-of-done.md"


def _states_the_rule(text: str) -> bool:
    """Does THIS text state rule 21 and name its enforcing mechanism?

    Takes the text rather than reading the file, so the discrimination below can put a
    doctored corpus through the identical predicate. Asserting a length comparison instead
    proved too weak: a mutant that pointed the rule test at the whole file survived it,
    because the length check computed its own slice and never saw the sibling stop
    discriminating. The property has to be exercised, not inferred.
    """
    passage = _slice_rule(text)
    if not passage:
        return False
    low = passage.lower()
    return "author" in low and "mutant" in low and "transition.py" in passage


def _slice_rule(text: str) -> str:
    """Rule 21's own text, from its numbered heading to the next top-level heading or rule.

    Sliced rather than searched, so the assertions below cannot be satisfied by any other
    part of the file - a Revision History row included.
    """
    m = re.search(r"^21\. \*\*(.+?)\*\*.*?$", text, re.M)
    if not m:
        return ""
    rest = text[m.start():]
    end = re.search(r"^(?:## |\d+\. \*\*)", rest[len(m.group(0)):], re.M)
    return rest[: len(m.group(0)) + end.start()] if end else rest


class DoctrineTests(unittest.TestCase):
    def test_doctrine_states_the_rule_and_names_the_enforcing_gate(self) -> None:
        """A reader must arrive at a MECHANISM, not at advice.

        Mutant: delete the passage and leave every other line intact, Revision History
        included - this reddens. Mutant: state the rule and drop the sentence naming
        `transition.py` - a rule with no mechanism behind it is one this doctrine is
        explicit about distrusting, and the enforcement assertion catches it alone.
        """
        text = DOCTRINE.read_text(encoding="utf-8")
        self.assertTrue(_states_the_rule(text), "rule 21 is absent, or states no mechanism")
        passage = _slice_rule(text)
        low = passage.lower()
        self.assertIn("author", low, "the rule does not name whose evidence is insufficient")
        self.assertIn("mutant", low, "the rule does not name the evidence it demands")
        self.assertIn("transition.py", passage,
                      "the rule states no enforcing mechanism, so it is advice")

    def test_the_guard_discriminates_against_its_own_revision_row(self) -> None:
        """THE DISCRIMINATION, exercised rather than inferred.

        The predicate is run over a doctored corpus: rule 21 removed, and a Revision History
        row describing the change that added it left in place. That row contains every word
        the assertions look for. A guard anchored on the whole file passes it; one anchored on
        the rule's own passage does not. BG0457 records exactly this defect - four guards
        comparing a document against a projection of itself - and a guard shipped in the same
        change as the prose it checks is the easiest place to repeat it.

        Mutant: point `_states_the_rule` at the whole text instead of the slice - this reddens,
        and the earlier length-comparison version did not.
        """
        real = DOCTRINE.read_text(encoding="utf-8")
        self.assertTrue(_states_the_rule(real), "the positive control does not hold")
        doctored = real.replace(_slice_rule(real), "") + (
            "\n| 2026-08-06 | sdlc | Added the repair-evidence rule: a fix's author is not "
            "sufficient evidence, held by a mutant and enforced by transition.py |\n")
        self.assertFalse(_states_the_rule(doctored),
                         "the guard is satisfied by a Revision History row describing the "
                         "rule rather than by the rule itself")

    def test_the_definition_of_done_carries_a_consistent_clause(self) -> None:
        """A consuming project copies this file as its own Done contract.

        Mutant: drop the clause from the template - the doctrine states a rule the shipped
        contract does not carry, and a consuming project inherits the prose without the bar.
        """
        dod = DOD.read_text(encoding="utf-8")
        story = dod[dod.index("## Story"): dod.index("## Delivery batch")]
        self.assertIn("repair", story.lower(), "the Story contract carries no repair clause")
        self.assertIn("mutant", story.lower(),
                      "the clause does not name the evidence the gate demands")


if __name__ == "__main__":
    unittest.main()
