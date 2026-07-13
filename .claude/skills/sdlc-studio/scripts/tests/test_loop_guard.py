"""Unit tests for loop_guard.py (RED first - the script does not exist yet)."""
from __future__ import annotations

import datetime as _dt
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
        # The caller (sprint plan) is responsible for not handing over an
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


class BudgetVerdictTests(unittest.TestCase):
    """The fourth guardrail: the run-level appetite breaker (pure function)."""

    def test_minutes_exhausted_at_boundary(self) -> None:
        mod = _load()
        v = mod.budget_verdict(appetite_minutes=30, appetite_units=0,
                               elapsed_minutes=30.0, units_done=0)
        self.assertTrue(v["exhausted"])
        self.assertEqual(v["reason"], "minutes")

    def test_minutes_under_continues(self) -> None:
        # kills an always-true mutant on the wall-clock arm.
        mod = _load()
        v = mod.budget_verdict(appetite_minutes=30, appetite_units=0,
                               elapsed_minutes=29.9, units_done=0)
        self.assertFalse(v["exhausted"])

    def test_units_exhausted_at_boundary(self) -> None:
        # MUTATION PROOF: removing the boundary check (the `units_done >= appetite_units`
        # comparison) turns this red - the breaker would never fire on the unit-count arm.
        mod = _load()
        v = mod.budget_verdict(appetite_minutes=0, appetite_units=2,
                               elapsed_minutes=0.0, units_done=2)
        self.assertTrue(v["exhausted"])
        self.assertEqual(v["reason"], "units")

    def test_units_minus_one_continues(self) -> None:
        # Boundary: one unit short of the appetite continues (kills a `>` -> `>=` off-by-one
        # AND an always-true mutant on the unit arm).
        mod = _load()
        v = mod.budget_verdict(appetite_minutes=0, appetite_units=2,
                               elapsed_minutes=0.0, units_done=1)
        self.assertFalse(v["exhausted"])

    def test_unbounded_never_fires(self) -> None:
        # 0 appetite on both axes = today's unbounded behaviour: the breaker never fires,
        # however much has been spent.
        mod = _load()
        v = mod.budget_verdict(appetite_minutes=0, appetite_units=0,
                               elapsed_minutes=9999.0, units_done=9999)
        self.assertFalse(v["exhausted"])

    def test_either_axis_fires(self) -> None:
        mod = _load()
        v = mod.budget_verdict(appetite_minutes=10, appetite_units=5,
                               elapsed_minutes=11.0, units_done=1)
        self.assertTrue(v["exhausted"])
        self.assertIn("minutes", v["reason"])
        self.assertNotIn("units", v["reason"])


class BudgetExitCodeTests(unittest.TestCase):
    def test_budget_exit_distinct_from_quarantine(self) -> None:
        # Budget-exhausted is NOT quarantine: a distinct exit code, so a harness can tell a
        # clean stop (units left in their true status) from a per-unit block.
        mod = _load()
        self.assertNotEqual(mod.BUDGET_EXIT, mod.QUARANTINE_EXIT)


class BudgetCliTests(unittest.TestCase):
    def _write_run_state(self, root: Path, started_at: str, appetite: dict,
                         batch: list) -> None:
        p = root / "sdlc-studio" / ".local" / "run-state.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({
            "schema": 1, "run_id": "RUN-TEST", "started_at": started_at,
            "ended_at": None, "outcome": "running", "goal": None,
            "batch": batch, "appetite": appetite,
        }), encoding="utf-8")

    def test_cli_wall_clock_exhausts(self) -> None:
        # The CLI reads elapsed from run_state.started_at: a start two hours ago against a
        # one-minute appetite exits BUDGET_EXIT.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            past = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(hours=2)
                    ).strftime("%Y-%m-%dT%H:%M:%SZ")
            self._write_run_state(root, past, {"minutes": 1, "units": 0}, [])
            mod = _load()
            rc = mod.main(["budget", "--root", str(root), "--format", "json"])
            self.assertEqual(rc, mod.BUDGET_EXIT)

    def test_cli_unbounded_continues(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            past = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(hours=2)
                    ).strftime("%Y-%m-%dT%H:%M:%SZ")
            self._write_run_state(root, past, {"minutes": 0, "units": 0}, [])
            mod = _load()
            rc = mod.main(["budget", "--root", str(root), "--format", "json"])
            self.assertEqual(rc, 0)

    def test_cli_flag_overrides_state(self) -> None:
        # An explicit --appetite-minutes overrides the recorded appetite (ad-hoc breaker).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            past = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(hours=2)
                    ).strftime("%Y-%m-%dT%H:%M:%SZ")
            self._write_run_state(root, past, {"minutes": 0, "units": 0}, [])
            mod = _load()
            rc = mod.main(["budget", "--root", str(root), "--appetite-minutes", "1",
                           "--format", "json"])
            self.assertEqual(rc, mod.BUDGET_EXIT)

    def test_cli_no_run_state_is_unbounded(self) -> None:
        # No run opened -> no start time -> the breaker cannot fire (it never fabricates one).
        with tempfile.TemporaryDirectory() as d:
            mod = _load()
            rc = mod.main(["budget", "--root", str(d), "--appetite-minutes", "1",
                           "--format", "json"])
            self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
