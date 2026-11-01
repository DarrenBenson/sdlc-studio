"""BG1065: the gate's cost budget sits beside the run it was derived from, and a boundary run's
boundary lanes are not judged against it.

`GATE_BUDGET_S` was set against a measured 33s that no record kept, so nothing tied the budget
to a run once the lane set changed. The measurement is now data beside the budget, so a budget
below its own measurement is a red test rather than a standing warning. A push or release run is
judged on its standard lanes alone: the budget never measured the full suite, so every push read
OVER.

Run from the repo root:
    python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_budget.py
"""
from __future__ import annotations

import contextlib
import sys
import tempfile
import types
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402 - confined git, which the unconfined-call sweep requires
import loader  # noqa: E402
import workspace  # noqa: E402 - the shared "am I in the dev repo?" check

gate = loader.load_script("gate")


class GateBudgetTests(unittest.TestCase):
    """The budget and the measurement it was derived from, read as data."""

    def test_the_budget_is_not_below_its_recorded_measurement(self) -> None:
        """AC1. Fails when `GATE_BUDGET_S` is set below the recorded seconds, when the record is
        removed, and when its seconds, date or commit is missing or malformed."""
        record = getattr(gate, "GATE_BUDGET_MEASURED", None)
        self.assertIsInstance(record, dict, "the budget must sit beside its measurement as data")
        seconds = record.get("seconds")
        self.assertIsInstance(seconds, (int, float))
        self.assertNotIsInstance(seconds, bool)
        self.assertGreater(seconds, 0)
        measured_on = date.fromisoformat(record.get("date", ""))
        self.assertLessEqual(measured_on, date.today(), "a measurement cannot be dated ahead")
        self.assertRegex(record.get("commit", ""), r"^[0-9a-f]{7,40}$")
        self.assertGreaterEqual(gate.GATE_BUDGET_S, seconds,
                                "a budget below its own measurement fires on a normal run")

    @unittest.skipUnless(workspace.in_dev_repo(), workspace.SKIP_REASON)
    def test_the_recorded_commit_is_one_this_repository_holds(self) -> None:
        """Fails when the record names a commit this repository does not hold, so the figure
        cannot cite a run nobody can check out."""
        commit = gate.GATE_BUDGET_MEASURED["commit"]
        cp = gitutil.git(["cat-file", "-e", f"{commit}^{{commit}}"], workspace.REPO, check=False)
        self.assertEqual(cp.returncode, 0, f"{commit} is not a commit in this repository")


class BoundaryRunCostTests(unittest.TestCase):
    """A boundary run names its boundary lanes and judges only its standard lanes.

    Fails when the whole elapsed time is judged against the budget (the push reads OVER), when
    the dominant lane is chosen among the boundary lanes, when a boundary run is recorded as the
    baseline (the 300s baseline moves), when it is compared with the baseline, at the push and
    at the release boundary, when the release boundary's two extra lanes are judged, and when
    the shipped registry's swapped push lanes are named outside the budget."""

    BOUNDARY_LANES = ("_full_suite", "_release_rehearsal", "_module_alone")

    def _root(self, tmp: str) -> str:
        (Path(tmp) / "sdlc-studio").mkdir()
        (Path(tmp) / "sdlc-studio" / ".config.yaml").write_text(
            "gate:\n  budget_seconds: 30\n", encoding="utf-8")
        gate.record_gate_cost(tmp, 300.0)
        return tmp

    def _run(self, root: str, standard: float, boundary: str | None = "push") -> dict:
        """The gate under a clock that only the lanes move: each fake lane advances it by its
        own seconds, so every figure here is exact whatever the machine's load."""
        clock = [1000.0]

        def lane(seconds: float):
            def check(_root):
                clock[0] += seconds
                return {"count": 0, "blocking": True, "detail": "ok"}
            return check
        with contextlib.ExitStack() as stack:
            for name in self.BOUNDARY_LANES:
                stack.enter_context(mock.patch.object(gate, name, lane(600.0)))
            stack.enter_context(mock.patch.object(
                gate, "time", types.SimpleNamespace(monotonic=lambda: clock[0])))
            return gate.run_gate(root, checks={"conformance": lane(standard),
                                               "validate": lane(1.0)},
                                 boundary=boundary, record_cost=True)["cost"]

    def test_a_push_run_judges_its_standard_lanes_alone(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            cost = self._run(self._root(d), standard=10.0)
        self.assertEqual(cost["seconds"], 611.0)
        self.assertEqual(cost["judged_seconds"], 11.0)
        self.assertFalse(cost["over"], cost["detail"])
        self.assertEqual(cost["outside_budget"], {"full-suite": 600.0})
        self.assertEqual(cost["dominant"], "conformance")
        self.assertIn("at the push boundary; its standard lanes 11.0s of a 30s budget",
                      cost["detail"])
        self.assertIn("outside the budget: full-suite at 600.0s", cost["detail"])
        self.assertNotIn("OVER", cost["detail"])

    def test_a_push_run_still_reads_over_when_its_standard_lanes_are(self) -> None:
        """The positive control: the budget still binds the lanes it measured."""
        with tempfile.TemporaryDirectory() as d:
            cost = self._run(self._root(d), standard=40.0)
        self.assertTrue(cost["over"])
        self.assertIn("its standard lanes 41.0s - OVER the 30s budget by 11.0s", cost["detail"])
        self.assertEqual(cost["dominant"], "conformance")

    def test_a_boundary_run_neither_reads_nor_writes_the_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            cost = self._run(root, standard=10.0)
            self.assertEqual(gate.read_gate_cost_baseline(root), 300.0,
                             "a push run overwrote the standard run's baseline")
            self.assertFalse(cost["recorded"])
            self.assertIn("BOUNDARY run - not compared with the baseline", cost["detail"])
            self.assertNotIn("faster than", cost["detail"])
            self.assertNotIn("slower than", cost["detail"])
            # The discriminating half: the same lanes off a boundary still compare and record.
            standard = self._run(root, standard=10.0, boundary=None)
            self.assertIn("faster than the 300.0s baseline", standard["detail"])
            self.assertEqual(gate.read_gate_cost_baseline(root), 11.0)

    def test_a_release_run_leaves_all_three_boundary_lanes_outside_the_budget(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            cost = self._run(root, standard=10.0, boundary="release")
            self.assertEqual(gate.read_gate_cost_baseline(root), 300.0,
                             "a release run overwrote the standard run's baseline")
        self.assertEqual(cost["outside_budget"], {"full-suite": 600.0,
                                                  "release-rehearsal": 600.0,
                                                  "module-alone": 600.0})
        self.assertEqual(cost["judged_seconds"], 11.0)
        self.assertFalse(cost["over"], cost["detail"])
        self.assertFalse(cost["recorded"])
        self.assertIn("at the release boundary; its standard lanes 11.0s of a 30s budget",
                      cost["detail"])
        self.assertIn("BOUNDARY run - not compared with the baseline", cost["detail"])
        self.assertNotIn("faster than", cost["detail"])
        self.assertNotIn("slower than", cost["detail"])

    def test_the_shipped_registry_keeps_its_swapped_push_lanes_inside_the_budget(self) -> None:
        """With no injected registry, a push swaps conformance and validate for their
        pushed-range lanes. Fails when the boundary lanes are worked out after that swap, which
        names both outside the budget beside the full suite. Every lane the run selects is a
        stub, so the run is hermetic."""
        clock = [1000.0]
        calls: list[str] = []

        def lane(name: str, seconds: float):
            def check(_root):
                calls.append(name)
                clock[0] += seconds
                return {"count": 0, "blocking": True, "detail": "ok"}
            return check
        with tempfile.TemporaryDirectory() as d, contextlib.ExitStack() as stack:
            root = self._root(d)
            stack.enter_context(mock.patch.dict(gate.DEFAULT_CHECKS, {
                n: lane(f"default:{n}", 0.0) for n in gate.DEFAULT_CHECKS}))
            stack.enter_context(mock.patch.dict(gate.PUSHED_RANGE_LANES, {
                "conformance": lane("pushed:conformance", 10.0),
                "validate": lane("pushed:validate", 1.0)}))
            for name in self.BOUNDARY_LANES:
                stack.enter_context(mock.patch.object(gate, name, lane(name, 600.0)))
            stack.enter_context(mock.patch.object(
                gate, "time", types.SimpleNamespace(monotonic=lambda: clock[0])))
            out = gate.run_gate(root, boundary="push", record_cost=True)
        # The discriminating half: the swap ran, so the pushed lanes stood in for the shipped ones.
        self.assertIn("pushed:conformance", calls)
        self.assertIn("pushed:validate", calls)
        self.assertNotIn("default:conformance", calls)
        self.assertNotIn("default:validate", calls)
        self.assertIn("_full_suite", calls)
        self.assertEqual(len(calls), len(out["checks"]), "a lane ran that is not a stub")
        cost = out["cost"]
        self.assertEqual(cost["outside_budget"], {"full-suite": 600.0})
        self.assertEqual(cost["judged_seconds"], 11.0)
        self.assertEqual(cost["dominant"], "conformance")
        self.assertIn("outside the budget: full-suite at 600.0s; BOUNDARY run", cost["detail"])


if __name__ == "__main__":
    unittest.main()
