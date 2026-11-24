"""An inline ruling is recognised in every form prose writes it.

`_RULING_RE` once ended in a word boundary after the colon, so `ruled: yes` and `**Decided:** no`
were never read as rulings and the item was reported unanswered.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib import sdlc_md  # noqa: E402


def _doc(item: str) -> str:
    return ("# US0001: t\n\n> **Status:** Done\n\n## Open Questions\n\n" + item + "\n")


def _open(item: str, repo_root=None) -> list:
    return sdlc_md.unresolved_questions(_doc(item), repo_root)


class InlineRulingFormTests(unittest.TestCase):
    def test_colon_forms(self):
        """`ruled:` and `decided:`, spaced, any case, bold or plain, are rulings."""
        for form in ("ruled: yes", "Ruled: yes", "RULED: yes", "**Ruled:** yes",
                     "decided: no", "Decided: no", "DECIDED: no", "**Decided:** no",
                     "ruled:yes", "decided:no"):
            with self.subTest(form=form):
                self.assertEqual(_open(f"- [x] Cache? - {form}"), [])
        # Positive control: the same item with no ruling is still reported.
        self.assertTrue(_open("- [x] Cache? - maybe later"))

    def test_every_alternative(self):
        """Each alternative, written as prose writes it, followed by a space and an answer."""
        for form in ("ruled by the consult", "Ruled by the consult", "settled in the review",
                     "Settled in the review", "resolved by the consult", "Resolved by the consult",
                     "ruled: yes, shipped", "decided: no, dropped",
                     "(ruled by the consult)", "- ruled by the consult."):
            with self.subTest(form=form):
                self.assertEqual(_open(f"- [x] Cache? - {form}"), [])
        # A boundary before each word: a longer word that merely ends in one is no ruling.
        for near in ("overruled by nobody", "unsettled in places", "unresolved by anyone",
                     "undecided: still", "misruled: x", "settled inside the cache",
                     "ruled bylines only", "resolved bylaw"):
            with self.subTest(near=near):
                self.assertTrue(_open(f"- [x] Cache? - {near}"))

    def test_destination_still_held(self):
        """A ruling that names a destination is held to it, in either colon form."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sdlc-studio").mkdir()
            for form in ("ruled: moved to BG9999", "**Decided:** see BG9999",
                         "resolved by BG9999"):
                with self.subTest(form=form):
                    out = _open(f"- [x] Cache? - {form}", root)
                    self.assertEqual(len(out), 1)
                    self.assertIn("BG9999", out[0])
                    self.assertIn("resolves to no artefact", out[0])
            # Positive control: the same ruling with no citation is accepted.
            self.assertEqual(_open("- [x] Cache? - ruled: yes", root), [])


if __name__ == "__main__":
    unittest.main()
