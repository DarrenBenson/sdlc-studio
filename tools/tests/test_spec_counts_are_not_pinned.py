"""The specs must not pin a component count that drifts (BG0332).

Both specs defined the script tier as "58 scripts" and a "six-module lib/" while the tree
carried 70 and 5. That number was the only inventory bounding the unit-test scope, so the
scope it described was about a fifth short - in documents whose own stated rule is not to pin
drifting numbers. The TRD already restated its component counts as growth-tolerant bands; this
holds the TSD to the same rule.

The check is against the CENSUS, not against a second number written here: a guard that
carries its own copy of the count is the defect it exists to catch.

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
SPECS = ("sdlc-studio/tsd.md", "sdlc-studio/trd.md")

#: A claim of the form "<n> scripts" / "<n> shipped helpers" / "<n> shared modules".
_PINNED = re.compile(r"\b(\d+)\s+(?:shipped\s+)?(?:scripts?|helpers?|shared modules?)\b", re.I)
#: The section that RECORDS history. A revision row naming the number that was true when it was
#: written is a record, not a live claim, and rewriting history to satisfy a guard is worse.
_HISTORY = re.compile(r"^##+\s*(Revision History|Changelog)\b", re.M)


def _live_prose(text: str) -> str:
    m = _HISTORY.search(text)
    return text[:m.start()] if m else text


class SpecCountsTests(unittest.TestCase):
    def _census(self) -> tuple[int, int]:
        scripts = len([p for p in SCRIPTS.glob("*.py") if p.name != "__init__.py"])
        libs = len([p for p in (SCRIPTS / "lib").glob("*.py") if p.name != "__init__.py"])
        return scripts, libs

    def test_the_census_is_readable(self) -> None:
        """Guard the guard: a census of zero would make every assertion below vacuous."""
        scripts, libs = self._census()
        self.assertGreater(scripts, 10)
        self.assertGreater(libs, 1)

    def test_no_spec_pins_a_component_count_it_does_not_match(self) -> None:
        scripts, libs = self._census()
        allowed = {scripts, libs}
        for rel in SPECS:
            text = _live_prose((REPO / rel).read_text(encoding="utf-8"))
            for m in _PINNED.finditer(text):
                n = int(m.group(1))
                with self.subTest(spec=rel, claim=m.group(0)):
                    self.assertIn(
                        n, allowed,
                        f"{rel} pins {m.group(0)!r} against a census of {scripts} scripts and "
                        f"{libs} lib modules. State the SET or a growth-tolerant band - a "
                        f"pinned count is true on the day it is written and wrong after")


if __name__ == "__main__":
    unittest.main()
