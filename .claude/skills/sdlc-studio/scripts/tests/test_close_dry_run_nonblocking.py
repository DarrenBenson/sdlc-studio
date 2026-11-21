"""BG0985: `sprint close --dry-run` previews a non-blocking pre-flight row as what it is.

The pre-flight carries rows that say they do not hold the close (the gate's review-current lane
reports cadence debt and lets the close proceed). The dry run copied every row into its preview
as a refusal, so it printed `STOP gate: ... (reported, not blocking)`, counted a refusal and
exited 1 for a close that would proceed. Driven through `sprint.main(["close", "--dry-run"])` on
the lean close fixture with every chain step stubbed green and the pre-flight's rows fixed, so
the pre-flight row is the only thing the preview can refuse on.

MUTANTS, each of which a test here fails on: (1) every row is a refusal again; (2) the advisory
row is dropped from the preview rather than shown; (3) every row is advisory, so a blocking row
previews as a pass; (4) the gate step is left out whenever the pre-flight carries any gate row,
blocking or not.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_close as lean  # noqa: E402 - the close fixture and its green chain, shared

ADVISORY = "review-current: CADENCE DEBT (reported, not blocking) - so the close proceeds"
HELD = "review-coverage: US0101 is covered by no independent review"


def _preview(row: dict) -> tuple[int, str]:
    """`close --dry-run` over the lean fixture, its pre-flight returning `row` alone."""
    mod = lean._live("sprint")
    pre = {"blockers": [row], "ready": not row.get("blocking", True), "gate_ran": True}
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        lean._fixture(root)
        out = io.StringIO()
        with lean._green_steps(mod), \
                unittest.mock.patch.object(mod, "close_preflight", lambda *a, **k: pre), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            rc = mod.main(["close", "--retro", "RETRO0001", "--dry-run", "--root", str(root)])
    return rc, out.getvalue()


class CloseDryRunNonBlockingTests(unittest.TestCase):

    def test_advisory_row_not_a_refusal(self) -> None:
        rc, out = _preview({"stage": "gate", "detail": ADVISORY, "remedy": "refresh the anchor",
                            "blocking": False})
        self.assertNotIn("STOP", out, f"a row that holds nothing previews as a refusal:\n{out}")
        self.assertIn(ADVISORY, out, f"the advisory row is not shown at all:\n{out}")
        self.assertIn("reported not blocking", out,
                      f"the advisory row does not say it does not hold the close:\n{out}")
        self.assertRegex(out, r"ok   gate: ", "the gate step went missing from the preview")
        self.assertIn("dry run CLEAN", out, out)
        self.assertNotIn("refusal(s)", out, out)
        self.assertEqual(0, rc, f"a close that would proceed previews as refused:\n{out}")

    def test_blocking_row_still_refuses(self) -> None:
        rc, out = _preview({"stage": "review-coverage", "detail": HELD,
                            "remedy": "record a review", "blocking": True})
        self.assertIn(f"STOP review-coverage: {HELD}", out, out)
        self.assertIn("dry run: 1 refusal(s)", out, out)
        self.assertEqual(1, rc, out)
        rc, out = _preview({"stage": "gate", "detail": "lint: 3 findings", "remedy": "fix them"})
        self.assertIn("STOP gate: lint: 3 findings", out,
                      f"a row carrying no flag must hold the close, as the close reads it:\n{out}")
        self.assertEqual(1, rc, out)


if __name__ == "__main__":
    unittest.main()
