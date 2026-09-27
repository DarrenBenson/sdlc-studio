"""BG0796: the checklist's cost row reads the run's measured token total.

RPT0010's Estimates section measured 19,225,437 tokens from the run record while its cost row
read `unattributed - no harness-tracked sprint total`: two readers of one fact disagreed. The
fixture is the one-page report's run (`test_lean_report.lean_run`): a meter that moved by
1,700,000 and one delegated agent that reported 123,456, and no hand-supplied total.
"""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import test_lean_report as lean  # noqa: E402 - the one-page report's fixture run

sr = lean.sr


class CostRowTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        lean.lean_run(self.root)

    def _cost_row(self) -> dict:
        items = sr.checklist(self.root, lean.RETRO)["items"]
        return next(item for item in items if item["id"] == "cost")

    def _estimates_tokens(self) -> int:
        rows = lean._sections(sr.build_report(self.root, lean.RETRO))["estimates"]["rows"]
        return next(r for r in rows if r["est_measure"]["value"] == "Tokens")["est_actual"][
            "value"]

    def test_the_cost_row_reads_the_run_s_measured_total(self) -> None:
        """AC1. MUTANTS: HEAD's resolver, which answers `unattributed` unless a total was
        supplied by hand; the main-thread meter alone (1,700,000), which disagrees with the
        Estimates section beside it."""
        measured = self._estimates_tokens()
        self.assertEqual(1_823_456, measured, "premise: the Estimates section's figure")
        row = self._cost_row()
        self.assertEqual(sr.ANSWERED, row["state"], row)
        self.assertEqual(f"{measured:,} tokens, measured", row["value"])
        self.assertIn("1 delegated agent", row["detail"])
        self.assertNotIn("supplied", row["value"])

    def test_a_supplied_total_overrides_and_is_named(self) -> None:
        """AC2. MUTANT: the measured total silently replacing the operator's override, so the
        row reads 1,823,456 and names no supplied figure."""
        import retro  # noqa: PLC0415 - imported after `sr` binds its own, as the fixture does
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = retro.main(["--root", str(self.root), "accuracy", "--id", lean.RETRO,
                             "--tokens", "777777", "--write"])
        self.assertEqual(0, rc, out.getvalue())
        row = self._cost_row()
        self.assertEqual(sr.ANSWERED, row["state"], row)
        self.assertEqual("777,777 tokens, supplied", row["value"])
        self.assertIn("1,823,456", row["detail"], "the measured total it overrides is named")

    def test_the_close_s_own_capture_is_not_an_override(self) -> None:
        """The close records its harness capture on the same velocity row, earlier than the
        page. MUTANT: read any recorded total back as supplied, so the row states the close's
        earlier reading and calls it an operator's figure."""
        import retro  # noqa: PLC0415
        capture = {"tokens": 555_555, "delegated_tokens": 0, "basis": "b", "source": "s",
                   "model": None}
        out = io.StringIO()
        with mock.patch.object(retro, "run_attributed_tokens", return_value=capture), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = retro.main(["--root", str(self.root), "accuracy", "--id", lean.RETRO,
                             "--tokens-from-harness", "--write"])
        self.assertEqual(0, rc, out.getvalue())
        self.assertEqual(555_555, next(r for r in retro.velocity_history(self.root)
                                       if r["id"] == lean.RETRO)["actual_tokens"], "premise")
        self.assertEqual("1,823,456 tokens, measured", self._cost_row()["value"])


if __name__ == "__main__":
    unittest.main()
