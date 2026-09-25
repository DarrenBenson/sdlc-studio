"""BG0529: the CLI lane test US0642, US0644 was delivered without, for `critic.py`.

Each of US0640, US0642, US0644 and US0645 changes a command, and every criterion any of them
carries is pinned IN-PROCESS only. That is not the same as unverified - both adversarial seats
drove each mechanism through the shipped verb during the review, and the transcripts are in the
run's record - but a hand-run transcript verifies today and pins nothing for tomorrow. It is
exactly the state `critic.py brief --tier` sat in for a whole sprint while
`brief_fingerprint(brief(...))` passed in-process and the shipped verb printed nothing.

So these drive the shipped entry point in a subprocess and assert on exit code and OUTPUT. The
wiring is the part a library test cannot exercise, which is the whole reason `verify_ac
lane-check` names a unit that changes a command and has no lane verifier. US0644's lane (the
sign-off capacity) went with the per-unit sign-off verb (US0919).
"""
from __future__ import annotations

import subprocess
import sys
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


if __name__ == "__main__":
    unittest.main()
