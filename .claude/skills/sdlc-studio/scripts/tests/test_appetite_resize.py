#!/usr/bin/env python3
"""`sprint appetite resize`: a ceiling that moves does so ON THE RECORD.

A run that turns out bigger than planned has two honest endings - stop at the planned ceiling,
or raise it deliberately - and one dishonest one, where the appetite is quietly rewritten so the
close reports a run that fitted. The standing pair is what makes the third impossible: raising
the accepted number makes the overage TRUE rather than hiding it.
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

SCRIPTS = Path(__file__).resolve().parent.parent
SCRIPT = SCRIPTS / "sprint.py"


def _load():
    spec = importlib.util.spec_from_file_location("sprint", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sprint"] = mod
    spec.loader.exec_module(mod)
    return mod


class AppetiteResizeTests(unittest.TestCase):

    def _run(self, root, *argv):
        """Through `main`, the shipped entry point - a library call would not see the wiring."""
        sprint = _load()
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sprint.main(["appetite", *argv, "--root", str(root)])
        return rc, out.getvalue() + err.getvalue()

    def _root(self, d, *, outcome="running", appetite=None):
        root = Path(d)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        (root / "sdlc-studio" / "stories").mkdir(parents=True, exist_ok=True)
        state = {"run_id": "RUN-T", "batch": ["US0001"], "outcome": outcome}
        if appetite is not None:
            state["appetite"] = appetite
        (root / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps(state), encoding="utf-8")
        return root

    def _state(self, root):
        return json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                          .read_text(encoding="utf-8"))

    _PLANNED = {"units": 10, "minutes": 120, "standing_units": 10,
                "standing_minutes": 120, "over_appetite": False}

    def test_a_resize_writes_the_new_pair_and_records_the_reason(self) -> None:
        """MUTANT: write the new number without the change record.

        Both are asserted. The number alone says a ceiling moved and not why, and the why is the
        entire content of the decision an auditor is looking for at the close.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, appetite=dict(self._PLANNED))
            rc, out = self._run(root, "resize", "--units", "16",
                                "--reason", "the batch grew by an epic")
            st = self._state(root)
        self.assertEqual(0, rc, out)
        self.assertEqual(16, st["appetite"]["units"])
        changes = st.get("appetite_changes") or []
        self.assertEqual(1, len(changes), "the resize was not recorded")
        self.assertIn("the batch grew by an epic", changes[0]["reason"])
        self.assertEqual(10, changes[0]["from"]["units"],
                         "the record does not say what the ceiling was before")

    def test_a_reasonless_resize_and_a_runless_resize_both_write_nothing(self) -> None:
        """MUTANT: accept an empty reason, or resize a closed run.

        Both refusals in one test because both have the same failure shape - a write that
        happened when it should not have. The state is compared BYTE-for-byte, so a partial
        write is caught as well as a complete one.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, appetite=dict(self._PLANNED))
            path = root / "sdlc-studio" / ".local" / "run-state.json"
            before = path.read_text(encoding="utf-8")
            rc_noreason, out_nr = self._run(root, "resize", "--units", "16")
            after_noreason = path.read_text(encoding="utf-8")

            closed = self._root(str(Path(d) / "closed"), outcome="goal-reached",
                                appetite=dict(self._PLANNED))
            cpath = closed / "sdlc-studio" / ".local" / "run-state.json"
            cbefore = cpath.read_text(encoding="utf-8")
            rc_closed, out_cl = self._run(closed, "resize", "--units", "16",
                                          "--reason", "too late")
            cafter = cpath.read_text(encoding="utf-8")
        self.assertNotEqual(0, rc_noreason, "a reasonless resize was accepted")
        self.assertEqual(before, after_noreason, "a refused resize still wrote state")
        self.assertNotEqual(0, rc_closed, "a closed run was resized")
        self.assertEqual(cbefore, cafter, "a resize on a closed run still wrote state")

    def test_a_raised_appetite_reports_the_overage_against_the_unchanged_standing_pair(
            self) -> None:
        """The one that matters. MUTANT: move the standing pair with the accepted one.

        That is the dishonest ending - the close would then report a run that fitted, because
        the ceiling it was measured against moved with it. Raising the accepted number must MAKE
        the overage true, not hide it.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, appetite=dict(self._PLANNED))
            self._run(root, "resize", "--units", "16", "--reason", "an epic was added")
            st = self._state(root)
            sprint = _load()
            line = sprint.appetite_overage_line(root)
        self.assertEqual(10, st["appetite"]["standing_units"],
                         "the standing pair moved with the accepted one, so the close would "
                         "report a run that fitted")
        self.assertTrue(st["appetite"]["over_appetite"],
                        "raising the accepted ceiling did not register as an overage")
        self.assertIsNotNone(line, "the close reports no overage after a raise")
        self.assertIn("10", line, "the overage line does not name the standing ceiling")

    def test_loop_guard_resolves_the_resized_appetite_and_does_not_fire(self) -> None:
        """MUTANT: write the resize somewhere the breaker does not read.

        The breaker is the whole point: a resize the loop guard cannot see moves a number in a
        file and stops nothing. Asserted through `loop_guard`'s own resolution, at a unit count
        BETWEEN the old ceiling and the new one - so it fires before the resize and not after.
        """
        import argparse
        sys.path.insert(0, str(SCRIPTS))
        import loop_guard  # noqa: E402
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, appetite=dict(self._PLANNED))
            args = argparse.Namespace(appetite_minutes=None, appetite_units=None)
            _, units_before = loop_guard._resolve_appetite(root, args)
            self._run(root, "resize", "--units", "16", "--reason", "an epic was added")
            _, units_after = loop_guard._resolve_appetite(root, args)
        self.assertEqual(10, units_before)
        self.assertEqual(16, units_after,
                         "the breaker still resolves the PLANNED ceiling, so the resize stops "
                         "nothing")
        self.assertTrue(loop_guard.budget_verdict(0, units_before, 0, 12)["exhausted"],
                        "control: 12 units should exceed the planned ceiling of 10")
        self.assertFalse(loop_guard.budget_verdict(0, units_after, 0, 12)["exhausted"],
                         "12 units still spent the appetite after raising it to 16")


if __name__ == "__main__":
    unittest.main()
