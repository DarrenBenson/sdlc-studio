"""A seat's worked example must quote a persona goal the persona actually has (BG0333).

The Product seat's first Craft Goal is that every story traces to a REAL End goal, "not a
guess" - and its worked example demonstrated that behaviour by tracing to a sentence the
Primary persona's card does not contain. A worked example is how a seat is learned, so an
example doing the thing the seat refuses teaches the refusal away. `validate.py seats` passed
it because it checks stamps and structure, not whether a quotation is true.

The check is a containment test against the persona cards, so it cannot be satisfied by
writing the expected sentence twice.

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SEATS = REPO / "sdlc-studio" / "personas" / "seats"
PERSONAS = REPO / "sdlc-studio" / "personas"

#: `... whose End goal is "..."` / `End goal: "..."` - a quotation presented as a persona's own.
_QUOTED_GOAL = re.compile(r"End goal[^\"\n]{0,40}\"([^\"]{15,})\"", re.I | re.S)


def _normalise(text: str) -> str:
    return " ".join(text.lower().replace("\n", " ").split())


class SeatExampleGoalsTests(unittest.TestCase):
    def _persona_text(self) -> str:
        return _normalise(" ".join(p.read_text(encoding="utf-8")
                                   for p in PERSONAS.glob("*.md")))

    def test_the_persona_corpus_is_readable(self) -> None:
        """Guard the guard - an empty corpus would make every assertion below vacuous."""
        self.assertGreater(len(self._persona_text()), 500)
        self.assertTrue(list(SEATS.glob("*.md")), "no seat cards found")

    def test_every_quoted_end_goal_appears_on_a_persona_card(self) -> None:
        corpus = self._persona_text()
        checked = 0
        for seat in sorted(SEATS.glob("*.md")):
            text = seat.read_text(encoding="utf-8")
            for m in _QUOTED_GOAL.finditer(text):
                quoted = _normalise(m.group(1)).rstrip(".")
                checked += 1
                with self.subTest(seat=seat.name, goal=quoted[:60]):
                    self.assertIn(
                        quoted, corpus,
                        f"{seat.name} quotes an End goal no persona card carries. A seat that "
                        f"demands tracing to a real goal must not demonstrate the behaviour by "
                        f"tracing to a guess")
        self.assertGreater(checked, 0,
                           "no quoted End goal was found in any seat card - the pattern has "
                           "stopped matching, so this guard is inert rather than clean")


if __name__ == "__main__":
    unittest.main()
