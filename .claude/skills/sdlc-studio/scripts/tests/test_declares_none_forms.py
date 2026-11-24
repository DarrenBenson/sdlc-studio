"""An Open Questions item declaring there are none, in every dash form the corpus writes."""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib import sdlc_md  # noqa: E402


def _open(items: str) -> list:
    return sdlc_md.unresolved_questions(
        "# BG9999: x\n\n> **Status:** Fixed\n\n## Open Questions\n\n" + items)


class DeclaresNoneFormsTests(unittest.TestCase):
    def test_dash_forms_declare_none(self):
        for item in ("- [ ] — None, behaviour extracted.", "- [ ] – None",
                     "- [ ] - None.", "- [ ] — n/a", "- [ ] - N/A"):
            with self.subTest(item=item):
                self.assertEqual(_open(item + "\n"), [])
        # positive controls: the plain form was always accepted, and a dash before a real
        # question is not a declaration of none
        self.assertEqual(_open("- [ ] None\n"), [])
        self.assertEqual(len(_open("- [ ] — Should we ship it?\n")), 1)
        self.assertEqual(len(_open("- [ ] - Nonetheless, should we?\n")), 1)

    def test_word_boundary_still_holds(self):
        self.assertEqual(len(_open("- [ ] Nonetheless, should we ship it?\n")), 1)
        self.assertEqual(len(_open("- [ ] Nature of it?\n")), 1)
        self.assertEqual(len(_open("- [ ] n/ab?\n")), 1)
        # `none` or `n/a` must OPEN the item: a question that merely mentions one is a question
        self.assertEqual(len(_open("- [ ] Should none of these ship?\n")), 1)
        self.assertEqual(len(_open("- [ ] - Is this n/a here?\n")), 1)
        self.assertEqual(_open("- [ ] None - behaviour fully extracted\n"), [])


if __name__ == "__main__":
    unittest.main()
