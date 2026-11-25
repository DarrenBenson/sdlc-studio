"""BG0973: `artifact.py new --type review` printed the NOT FINISHED grooming line about acceptance
criteria for a record whose template has no Acceptance Criteria section, so the warning named
something the file does not hold. The line is given only when the file has that section and it
still holds the scaffold placeholder.

Each case runs the shipped CLI (`artifact.py new`) into a throwaway root (`--root`).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_artifact_review_scaffold.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/artifact.py
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "artifact.py"
NOT_FINISHED = "NOT FINISHED"


def _new(root: Path, type_: str, title: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), "new", "--type", type_, "--title", title,
                           "--root", str(root)], capture_output=True, text=True, check=False)


class ReviewScaffoldTests(unittest.TestCase):

    def setUp(self) -> None:
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.root = Path(td.name)

    def test_no_ac_warning_for_review(self) -> None:
        """AC1. Mutant: the warning read from the whole body when the file has no Acceptance
        Criteria section, so a review's own `{{scope}}` slot trips it."""
        r = _new(self.root, "review", "a review")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        path = next((self.root / "sdlc-studio" / "reviews").glob("RV*.md"))
        body = path.read_text(encoding="utf-8")
        self.assertIn("{{", body, "premise: the review scaffold still holds unfilled slots")
        self.assertNotIn("## Acceptance Criteria", body, "premise: it has no such section")
        self.assertNotIn(NOT_FINISHED, r.stdout + r.stderr)

    def test_a_review_titled_with_the_slot_is_not_warned(self) -> None:
        """The section guard is the only test: a review whose title names `{{criterion}}` holds no
        Acceptance Criteria section, so it is not warned. Mutant: a whole-body `{{criterion}}`
        test kept beside the guard."""
        r = _new(self.root, "review", "the {{criterion}} slot survives")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertNotIn(NOT_FINISHED, r.stdout + r.stderr)

    def test_slots_before_the_section_do_not_warn_a_story_with_criteria(self) -> None:
        """The window is read AFTER the heading: a story with authored criteria still holds
        `{{role}}` slots in its user story above them and is not warned. Mutant: the 400
        characters before the heading read instead."""
        subprocess.run([sys.executable, str(SCRIPT), "new", "--type", "epic", "--title", "e",
                        "--root", str(self.root)], capture_output=True, text=True, check=True)
        r = subprocess.run([sys.executable, str(SCRIPT), "new", "--type", "story", "--epic",
                            "EP0001", "--title", "s", "--ac", "it holds", "--root",
                            str(self.root)], capture_output=True, text=True, check=False)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        body = next((self.root / "sdlc-studio" / "stories").glob("US*.md")).read_text(
            encoding="utf-8")
        self.assertIn("{{", body.split("## Acceptance Criteria", 1)[0], "premise: slots above")
        self.assertNotIn("{{", body.split("## Acceptance Criteria", 1)[1][:400], "premise")
        self.assertNotIn(NOT_FINISHED, r.stdout + r.stderr)

    def test_no_ac_warning_for_the_other_records_without_criteria(self) -> None:
        """The same line is not given for a retro, which holds no criteria either."""
        for type_ in ("retro",):
            with self.subTest(type=type_):
                r = _new(self.root, type_, f"a {type_}")
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                self.assertNotIn(NOT_FINISHED, r.stdout + r.stderr)

    def test_a_story_with_the_placeholder_is_still_warned(self) -> None:
        """The control: a story minted with its Acceptance Criteria section still holding the
        scaffold placeholder gets the line, so the warning was not switched off wholesale."""
        r = _new(self.root, "epic", "an epic")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertNotIn(NOT_FINISHED, r.stdout + r.stderr, "an epic holds no criteria section")
        r = subprocess.run([sys.executable, str(SCRIPT), "new", "--type", "story", "--epic",
                            "EP0001", "--title", "a story", "--root", str(self.root)],
                           capture_output=True, text=True, check=False)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        body = next((self.root / "sdlc-studio" / "stories").glob("US*.md")).read_text(
            encoding="utf-8")
        self.assertIn("## Acceptance Criteria", body)
        self.assertIn(NOT_FINISHED, r.stdout)


if __name__ == "__main__":
    unittest.main()
