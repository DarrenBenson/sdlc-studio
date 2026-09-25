"""BG0695: the ungroomed count and its groom nudge leave retired stories out.

A story retired unbuilt (Superseded, Won't Implement) owes no criteria, so telling the user to
groom it before planning it to Done is advice about work nobody will do. HEAD counted every
story still carrying the refine placeholder, and this repository was told to groom 124 stories,
about 110 of them retired by one sweep.
MUTANTS: count every placeholder story whatever its status (AC1 red: 3, not 1); print the nudge
even at a zero count (AC2 red: the line appears).
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import sdlc_md  # noqa: E402

SCRIPT = Path(__file__).resolve().parents[1] / "conformance.py"
NUDGE = "still carry the refine ungroomed-AC placeholder"


def _story(root: Path, num: int, status: str) -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"US{num:04d}-sample.md").write_text(
        f"# US{num:04d}: sample\n\n> **Status:** {status}\n"
        "> **Epic:** [EP0001: x](../epics/EP0001-x.md)\n\n"
        f"## Acceptance Criteria\n\n{sdlc_md.UNGROOMED_AC_MARKER}\n", encoding="utf-8")


def _check(root: Path, fmt: str) -> str:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "check", "--root", str(root), "--format", fmt],
        capture_output=True, text=True, timeout=120, check=False)
    return proc.stdout


class UngroomedCountTests(unittest.TestCase):

    def test_retired_stories_are_not_counted_ungroomed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _story(root, 1, "Superseded")
            _story(root, 2, "Won't Implement")
            _story(root, 3, "Draft")
            result = json.loads(_check(root, "json"))
            # The fixture is what it claims: all three carry the placeholder, two are retired.
            self.assertEqual(3, len(result["units"]))
            self.assertEqual(3, sum(1 for u in result["units"] if u["ungroomed"]))
            self.assertEqual(1, result["summary"]["ungroomed"])
            nudge = [ln for ln in _check(root, "text").splitlines() if NUDGE in ln]
            self.assertEqual(1, len(nudge), nudge)
            self.assertTrue(nudge[0].strip().startswith("1 story(ies)"), nudge[0])

    def test_no_nudge_when_only_retired_stories_carry_the_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _story(root, 1, "Superseded")
            _story(root, 2, "Won't Implement")
            out = _check(root, "text")
            # Positive control: the summary line printed, so an absent nudge is not an absent run.
            self.assertIn("conformance: 2/2 conformant", out)
            self.assertNotIn(NUDGE, out)


if __name__ == "__main__":
    unittest.main()
