"""BG0529: the CLI lane test US0642, US0644 was delivered without, for `critic.py`.

Each of US0640, US0642, US0644 and US0645 changes a command, and every criterion any of them
carries is pinned IN-PROCESS only. That is not the same as unverified - both adversarial seats
drove each mechanism through the shipped verb during the review, and the transcripts are in the
run's record - but a hand-run transcript verifies today and pins nothing for tomorrow. It is
exactly the state `critic.py brief --tier` sat in for a whole sprint while
`brief_fingerprint(brief(...))` passed in-process and the shipped verb printed nothing.

So these drive the shipped entry point in a subprocess and assert on exit code and OUTPUT. The
wiring is the part a library test cannot exercise, which is the whole reason `verify_ac
lane-check` names a unit that changes a command and has no lane verifier.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent
REPO = DIR.parent.parent.parent.parent


def _run(script: str, *argv: str, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(DIR / script), *argv],
                          capture_output=True, text=True, cwd=str(cwd or REPO), timeout=180)


class US0642TheClaimInventoryPassIsTierGated(unittest.TestCase):
    """US0642. The claim-inventory pass is the single largest block in a brief and costs more
    than a low-band unit does, so it belongs at `full` and not at `light`. In-process the block
    is a module constant; through the CLI it is either in the printed brief or it is not."""

    def test_the_inventory_block_is_present_at_full_and_absent_at_light(self) -> None:
        """MUTANT: derive the inventory from something other than the tier - the two briefs
        become identical and the tier stops meaning anything at the command."""
        full = _run("critic.py", "brief", "--unit", "BG0486", "--seat", "qa", "--tier", "full")
        light = _run("critic.py", "brief", "--unit", "BG0486", "--seat", "qa", "--tier", "light")
        self.assertEqual(0, full.returncode, full.stderr[-300:])
        self.assertEqual(0, light.returncode, light.stderr[-300:])
        # "CLAIM INVENTORY", as the brief actually prints it. Asserting the hyphenated spelling
        # failed against a brief that carried the block - the test was wrong, not the command.
        self.assertIn("claim inventory", full.stdout.lower(),
                      "the full-tier brief carries no claim-inventory pass")
        self.assertNotIn("claim inventory", light.stdout.lower(),
                         "the light-tier brief carries the pass it exists to omit")
        self.assertNotEqual(full.stdout, light.stdout, "the tier changed nothing that prints")

class US0644TheCapacityReachesTheWrittenRecord(unittest.TestCase):
    """US0644. A capacity carried only in a return value is a figure nobody can read back. The
    lane question is whether it reaches the RECORD the next reader opens."""

    def test_a_signoff_record_carries_its_fields_to_disk(self) -> None:
        """MUTANT: keep the parsed field in memory and never write it - the in-process assertion
        still passes and the file the next command reads has nothing in it."""
        # A THROWAWAY workspace, so this asserts on a record it created rather than on the
        # repository's own. The first cut ran against the real tree with an if/else on the exit
        # code - BOTH arms passed, so it could not fail either way, which is the exact shape of
        # test this unit exists to replace.
        d = Path(tempfile.mkdtemp(prefix="signoff_lane_"))
        self.addCleanup(__import__("shutil").rmtree, d, ignore_errors=True)
        (d / "sdlc-studio" / "bugs").mkdir(parents=True)
        (d / "sdlc-studio" / "reviews").mkdir(parents=True)
        (d / "sdlc-studio" / "bugs" / "BG9200-x.md").write_text(
            "# BG9200: a fixture bug\n\n> **Status:** Fixed\n> **Severity:** Medium\n"
            "> **Points:** 2\n> **Affects:** f.py\n\n## Acceptance Criteria\n\n"
            "- [x] **AC1** Given a thing, when it happens, then it works.\n"
            "  - **Verify:** manual a human checks it\n", encoding="utf-8")
        note = "a lane test asserting the record reaches disk with its fields"
        proc = _run("critic.py", "signoff", "--unit", "BG9200", "--root", str(d),
                    "--principal", "Lane Principal", "--author", "lane-author", "--note", note)
        self.assertEqual(0, proc.returncode,
                         f"signoff refused in a clean fixture: {proc.stderr[-400:]}")
        record = d / "sdlc-studio" / "reviews" / "signoff-record.md"
        self.assertTrue(record.is_file(), "signoff exited 0 and wrote no record at all")
        text = record.read_text(encoding="utf-8", errors="replace")
        for field in ("BG9200", "Lane Principal", "lane-author"):
            self.assertIn(field, text, f"{field!r} never reached the written record")

if __name__ == "__main__":
    unittest.main()
