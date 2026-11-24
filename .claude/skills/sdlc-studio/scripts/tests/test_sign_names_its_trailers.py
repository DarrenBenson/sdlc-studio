"""BG1062: `sprint sign` names the `Refs:` trailers its paperwork commit needs.

The seal moves each batch unit not already terminal to its terminal status, so the operator's
paperwork commit stages those unit files. A message that names another unit and not these draws
one `engagement floor (attribution)` advisory per unit moved. The sign now prints, after the
seal, one `Refs: <id>` line per unit it moved, and nothing when it moved none.

These run the real `sprint sign` (`_seal_units` unstubbed) on BG0848's close-and-sign fixture
(`test_lean_sign._SignMovesRun`). MUTANTS, each failed here: no trailer printed (AC1); the whole
batch printed, the unit already terminal included (AC1, AC3); the header printed over an empty
block (AC3); the printed ids not the ones the attribution reads (AC2).
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_sign as signing  # noqa: E402 - BG0848's close-and-sign fixture, shared

import engagement_floor  # noqa: E402

HEADER = "sign: name the units this seal moved in the paperwork commit, one trailer each:"


class _MovesTwo(signing._SignMovesRun):
    """A story at Review and a bug In Progress the seal moves, and a bug already Fixed."""

    UNITS = {"US0101": ("stories", "Ready", "Review"), "BG0101": ("bugs", "Open", "In Progress"),
             "BG0102": ("bugs", "Open", "Fixed")}


class _MovesNone(signing._SignMovesRun):
    """Every unit already at its terminal status before the sign."""

    UNITS = {"US0101": ("stories", "Ready", "Done"), "BG0101": ("bugs", "Open", "Fixed")}


def _refs(out: str) -> list[str]:
    """Every stdout line that is a `Refs:` trailer, bare or not."""
    return [ln for ln in out.splitlines() if ln.startswith("Refs:")]


class SignNamesItsTrailersTests(unittest.TestCase):

    def _signed(self, kind: type) -> tuple[signing._SignMovesRun, str]:
        """Build, close and sign `kind`'s run: `(the run, sign's stdout)`."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        run = kind(tmp.name)
        env = unittest.mock.patch.dict(os.environ, run.env, clear=True)
        env.start()
        self.addCleanup(env.stop)
        run.build()
        return run, run.sign(run.close())

    def test_sign_prints_a_refs_trailer_per_unit_it_moved(self) -> None:
        """AC1. The block is the header and then exactly the two moved units' `Refs:` lines,
        one after another, in the batch's order; the unit already Fixed is not named."""
        run, out = self._signed(_MovesTwo)
        self.assertEqual(("Done", "Fixed", "Fixed"),
                         tuple(run.status(u) for u in ("US0101", "BG0101", "BG0102")), out)
        lines = out.splitlines()
        self.assertIn(HEADER, lines, out)
        at = lines.index(HEADER)
        self.assertEqual(["Refs: US0101", "Refs: BG0101"], lines[at + 1:at + 3], out)
        self.assertEqual(["Refs: US0101", "Refs: BG0101"], _refs(out),
                         f"the trailers are not exactly the units the seal moved:\n{out}")
        self.assertEqual(1, lines.count(HEADER), out)

    def test_the_printed_trailers_satisfy_the_attribution_advisory(self) -> None:
        """AC2. The moved units' files staged, under a message naming another bug: with the
        printed trailers appended no note names a moved unit; without them (the control) each
        moved unit draws exactly one note."""
        run, out = self._signed(_MovesTwo)
        subprocess.run(["git", "-C", str(run.root), "add", "-A"], env=run.env, check=True,
                       capture_output=True)
        staged = subprocess.run(["git", "-C", str(run.root), "diff", "--cached", "--name-only"],
                                env=run.env, check=True, capture_output=True,
                                text=True).stdout.splitlines()
        for uid in ("US0101", "BG0101"):
            self.assertTrue(any(re.search(rf"/{uid}-x\.md$", p) for p in staged), staged)
        message = "docs(BG0999): file the bug the sign turned up\n"
        trailers = "\n".join(_refs(out))
        control = engagement_floor.unnamed_unit_attribution(run.root, message)
        self.assertEqual(["BG0101", "US0101"],
                         sorted(n["id"] for n in control if n["id"] in ("US0101", "BG0101")),
                         control)
        named = engagement_floor.unnamed_unit_attribution(run.root, f"{message}\n{trailers}\n")
        self.assertEqual([], [n for n in named if n["id"] in ("US0101", "BG0101")], named)

    def test_a_seal_that_moves_nothing_prints_no_trailers(self) -> None:
        """AC3. Every unit terminal before the sign: no header, no `Refs:` line at all."""
        run, out = self._signed(_MovesNone)
        self.assertEqual(("Done", "Fixed"), (run.status("US0101"), run.status("BG0101")), out)
        self.assertIn("sign: 0 moved to their terminal status, 2 already there", out)
        self.assertNotIn(HEADER, out)
        self.assertEqual([], _refs(out), out)


if __name__ == "__main__":
    unittest.main()
