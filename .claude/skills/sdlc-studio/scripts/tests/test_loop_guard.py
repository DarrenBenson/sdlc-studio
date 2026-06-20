"""Unit tests for loop_guard.py (RED first - the script does not exist yet)."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "loop_guard.py"


def _load():
    spec = importlib.util.spec_from_file_location("loop_guard", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["loop_guard"] = mod
    spec.loader.exec_module(mod)
    return mod


class CapTests(unittest.TestCase):
    def test_cap_quarantines(self) -> None:
        mod = _load()
        st: dict = {}
        for i in range(3):
            st = mod.record_attempt(st, "US0010", f"sig{i}")  # distinct signatures
        v = mod.verdict(st, "US0010", cap=3, repeat=99)
        self.assertTrue(v["quarantine"])
        self.assertEqual(v["reason"], "cap")
        self.assertEqual(v["attempts"], 3)

    def test_under_cap_continues(self) -> None:
        mod = _load()
        st = mod.record_attempt({}, "US0010", "sig0")
        v = mod.verdict(st, "US0010", cap=3, repeat=99)
        self.assertFalse(v["quarantine"])

    def test_cap_minus_one_continues(self) -> None:
        # Boundary: at cap-1 the unit must continue (kills a `>= cap-1` off-by-one).
        mod = _load()
        st: dict = {}
        for i in range(2):
            st = mod.record_attempt(st, "US0010", f"sig{i}")
        v = mod.verdict(st, "US0010", cap=3, repeat=99)
        self.assertFalse(v["quarantine"])
        self.assertEqual(v["attempts"], 2)


class RepeatTests(unittest.TestCase):
    def test_repeat_quarantines(self) -> None:
        mod = _load()
        st: dict = {}
        st = mod.record_attempt(st, "US0010", "same")
        st = mod.record_attempt(st, "US0010", "same")
        v = mod.verdict(st, "US0010", cap=5, repeat=2)  # under cap, but repeated
        self.assertTrue(v["quarantine"])
        self.assertEqual(v["reason"], "repeat")


class CompleteTests(unittest.TestCase):
    def test_all_terminal(self) -> None:
        mod = _load()
        self.assertTrue(mod.is_complete(["Done", "Blocked", "Done"]))
        self.assertFalse(mod.is_complete(["Done", "In Progress"]))

    def test_empty_batch_is_complete(self) -> None:
        # Pin the semantics: an empty batch is vacuously complete (nothing to do).
        # The caller (autosprint plan) is responsible for not handing over an
        # empty batch when work exists.
        self.assertTrue(_load().is_complete([]))


class CliTests(unittest.TestCase):
    def test_record_quarantine_exit(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            state = Path(d) / "loop-state.json"
            mod = _load()
            rc = mod.main(["record", "--unit", "US", "--signature", "s",
                           "--cap", "1", "--state", str(state)])
            self.assertEqual(rc, 3)  # quarantine signal
            data = json.loads(state.read_text(encoding="utf-8"))
            self.assertIn("US", data["units"])

    def test_accumulates_across_invocations(self) -> None:
        # The real loop usage: separate process calls must read state back and
        # accumulate (kills a "state not read back" mutant).
        with tempfile.TemporaryDirectory() as d:
            state = Path(d) / "loop-state.json"
            mod = _load()
            # High cap + repeat so neither guardrail fires; isolates accumulation.
            args = ["record", "--unit", "US", "--signature", "s",
                    "--cap", "9", "--repeat", "9", "--state", str(state)]
            self.assertEqual(mod.main(args), 0)
            self.assertEqual(mod.main(args), 0)
            data = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(data["units"]["US"]["attempts"], 2)


if __name__ == "__main__":
    unittest.main()
