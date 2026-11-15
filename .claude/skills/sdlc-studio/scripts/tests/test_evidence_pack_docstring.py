"""`evidence_pack.py`'s module docstring states the accountable rule the code applies.

A principal is refused only when it reads as an agent or is a live author of one of the
report's own units; an author of any other unit is still a person. The docstring once said
every recorded author was refused, which the code stopped doing.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import evidence_pack  # noqa: E402


def refusal_sentence() -> str:
    """The module docstring's sentence that says what refuses the whole build, on one line."""
    doc = " ".join((evidence_pack.__doc__ or "").split())
    found = [s for s in re.split(r"(?<=[.:])\s+", doc) if "refuses the whole build" in s]
    if len(found) != 1:
        raise AssertionError(f"expected one refusal sentence in the docstring, found {found}")
    return found[0]


class DocstringTests(unittest.TestCase):
    def test_refusal_names_agents_and_live_authors_of_the_reports_own_units(self) -> None:
        sentence = refusal_sentence()
        self.assertIn("reads as an agent", sentence)
        self.assertIn("live author of one of the report's own units", sentence)

    def test_no_wording_refuses_every_recorded_author(self) -> None:
        sentence = refusal_sentence()
        # Every mention of an author in the refusal is qualified by the report's own units.
        for at in (m.start() for m in re.finditer(r"\bauthor\b", sentence)):
            self.assertIn("the report's own units", sentence[at:at + 60],
                          f"an unqualified author in the refusal: {sentence!r}")
        doc = " ".join((evidence_pack.__doc__ or "").split())
        self.assertIn("an author of any other unit is still accepted", doc)


if __name__ == "__main__":
    unittest.main()
