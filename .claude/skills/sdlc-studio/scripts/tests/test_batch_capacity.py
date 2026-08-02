#!/usr/bin/env python3
"""`sprint batch swap`: trading units is ONE recorded decision.

Drop-then-add reaches the same batch, but the ledger then carries two unrelated changes and a
reader cannot tell a trade from a cut followed later by an unrelated addition. The swap is the
intent, and the record should say so.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "sprint.py"


def _load():
    spec = importlib.util.spec_from_file_location("sprint", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sprint"] = mod
    spec.loader.exec_module(mod)
    return mod

class SwapTests(unittest.TestCase):
    """A swap is ONE recorded decision, not a drop that happens to be followed by an add."""

    def _run(self, root, *argv):
        sprint = _load()
        buf_out, buf_err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
            rc = sprint.main(["batch", *argv, "--root", str(root)])
        return rc, buf_out.getvalue() + buf_err.getvalue()

    def _root(self, d):
        root = Path(d)
        (root / "sdlc-studio" / "stories").mkdir(parents=True)
        (root / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)
        for uid, pts in (("US0001", 5), ("US0002", 3), ("US0003", 5), ("US0004", 2)):
            (root / "sdlc-studio" / "stories" / f"{uid}-x.md").write_text(
                f"# {uid}: a unit\n\n> **Status:** Ready\n> **Points:** {pts}\n"
                f"> **Affects:** src/a.py\n", encoding="utf-8")
        (root / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps({"run_id": "RUN-T", "batch": ["US0001", "US0002"],
                        "outcome": "running"}), encoding="utf-8")
        return root

    def test_swap_records_one_pair_and_matches_the_drop_then_add_equivalent(self) -> None:
        """MUTANT: record no swap entry, leaving only the individual changes.

        The BATCH is asserted equal to what drop-then-add reaches, AND the swap record asserted
        to exist - the first alone passes with the intent unrecorded, which is the defect.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            rc, out = self._run(root, "swap", "--out", "US0001", "--in", "US0003",
                                "--reason", "traded for the blocking one")
            state = json.loads(
                (root / "sdlc-studio" / ".local" / "run-state.json").read_text())
        self.assertEqual(0, rc, out)
        self.assertEqual(["US0002", "US0003"], sorted(state["batch"]),
                         "the batch is not what drop-then-add would have reached")
        swaps = state.get("batch_swaps") or []
        self.assertEqual(1, len(swaps), "the swap was not recorded as one decision")
        self.assertEqual(["US0001"], swaps[0]["out"])
        self.assertEqual(["US0003"], swaps[0]["in"])
        self.assertIn("traded for", swaps[0]["reason"])

    def test_an_unbalanced_swap_warns_with_the_delta_and_a_balanced_one_does_not(self) -> None:
        """MUTANT: warn always, or never.

        Both directions: a warning on every swap is noise the operator learns to skip, and no
        warning at all hides the thing the appetite has to absorb.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            _rc, out = self._run(root, "swap", "--out", "US0002", "--in", "US0003",
                                 "--reason", "r")          # 3 -> 5
        self.assertIn("+2", out, f"an unbalanced swap did not report its delta:\n{out}")
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            _rc, out = self._run(root, "swap", "--out", "US0001", "--in", "US0003",
                                 "--reason", "r")          # 5 -> 5
        self.assertNotIn("NOT balanced", out, "a balanced swap warned anyway")

    def test_an_absent_out_unit_refuses_atomically_and_changes_nothing(self) -> None:
        """MUTANT: check each outgoing unit as it is dropped.

        A half-applied swap leaves the batch in a state nobody chose, and the operator's next
        move is to guess which half landed. The state file is asserted byte-unchanged.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            before = (root / "sdlc-studio" / ".local" / "run-state.json").read_text()
            rc, out = self._run(root, "swap", "--out", "US0001,US0099", "--in", "US0003",
                                "--reason", "r")
            after = (root / "sdlc-studio" / ".local" / "run-state.json").read_text()
        self.assertEqual(2, rc, out)
        self.assertIn("US0099", out, "the refusal does not name the absent unit")
        self.assertEqual(before, after, "a refused swap still wrote to the run state")

    def test_a_swap_without_a_reason_is_refused(self) -> None:
        """MUTANT: default the reason to empty and carry on.

        A swap changes what the run is FOR. Unrecorded, the close cannot say why the delivered
        batch differs from the planned one.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            rc, out = self._run(root, "swap", "--out", "US0001", "--in", "US0003")
        self.assertEqual(2, rc)
        self.assertIn("--reason", out)

    def test_one_sided_swaps_are_refused(self) -> None:
        """MUTANT: allow --out alone, silently turning a swap into a drop."""
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            rc, _out = self._run(root, "swap", "--out", "US0001", "--reason", "r")
        self.assertEqual(2, rc, "a one-sided swap was accepted")

    def test_the_out_list_accepts_every_house_form_identically(self) -> None:
        """MUTANT: split on commas only, or accept only a repeated flag.

        `--out A --out B` and `--out A,B` are the same request in this project's grammar, and a
        verb that honours one is a second grammar.
        """
        sprint = _load()
        from lib import sdlc_md
        self.assertEqual(sdlc_md.split_id_list(["US0001", "US0002"]),
                         sdlc_md.split_id_list(["US0001,US0002"]),
                         "the repeated and comma forms are not read identically")


if __name__ == "__main__":
    unittest.main()
