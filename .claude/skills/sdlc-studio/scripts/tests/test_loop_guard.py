"""Unit tests for loop_guard.py (RED first - the script does not exist yet)."""
from __future__ import annotations

import contextlib
import datetime as _dt
import importlib.util
import io
import json
import os
import shutil
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


def _quiet_main(mod, argv: list[str]) -> int:
    """Run the CLI with its verdict line captured. A green suite must say nothing, or a
    real error hides in the scroll."""
    with contextlib.redirect_stdout(io.StringIO()):
        return mod.main(argv)


class CliTests(unittest.TestCase):
    def test_record_quarantine_exit(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            state = Path(d) / "loop-state.json"
            mod = _load()
            rc = _quiet_main(mod, ["record", "--unit", "US", "--signature", "s",
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
            self.assertEqual(_quiet_main(mod, args), 0)
            self.assertEqual(_quiet_main(mod, args), 0)
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
            rc = _quiet_main(mod, ["budget", "--root", str(root), "--format", "json"])
            self.assertEqual(rc, mod.BUDGET_EXIT)

    def test_cli_unbounded_continues(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            past = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(hours=2)
                    ).strftime("%Y-%m-%dT%H:%M:%SZ")
            self._write_run_state(root, past, {"minutes": 0, "units": 0}, [])
            mod = _load()
            rc = _quiet_main(mod, ["budget", "--root", str(root), "--format", "json"])
            self.assertEqual(rc, 0)

    def test_cli_flag_overrides_state(self) -> None:
        # An explicit --appetite-minutes overrides the recorded appetite (ad-hoc breaker).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            past = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(hours=2)
                    ).strftime("%Y-%m-%dT%H:%M:%SZ")
            self._write_run_state(root, past, {"minutes": 0, "units": 0}, [])
            mod = _load()
            rc = _quiet_main(mod, ["budget", "--root", str(root), "--appetite-minutes", "1",
                                   "--format", "json"])
            self.assertEqual(rc, mod.BUDGET_EXIT)

    def test_cli_no_run_state_is_unbounded(self) -> None:
        # No run opened -> no start time -> the breaker cannot fire (it never fabricates one).
        with tempfile.TemporaryDirectory() as d:
            mod = _load()
            rc = _quiet_main(mod, ["budget", "--root", str(d), "--appetite-minutes", "1",
                                   "--format", "json"])
            self.assertEqual(rc, 0)


class RootAnchoringTests(unittest.TestCase):
    """The guardrail state is written and read under the PROJECT ROOT, never beside the cwd.

    A NAMED `--root` was honoured; the family default `.` was taken as the cwd, so `record`
    from any subdirectory - the skill's own `scripts/` above all - wrote a stray
    `<cwd>/sdlc-studio/.local/loop-state.json`, printed a verdict and exited 0. The handoff
    reads `<root>/sdlc-studio/.local/loop-state.json`, so every attempt and every failure
    signature the run recorded was invisible to it. The `budget` breaker read its run state
    the same way, and reported an appetite it had not found as no appetite at all.

    Every test below runs from a cwd that is NOT the root: a test that chdir'd to the root
    would pass on a script that ignored `--root` entirely, and would prove nothing. The
    write-then-read pairs deliberately use DIFFERENT directories - sharing one cwd lets two
    equally cwd-relative paths agree with each other and both still be wrong.
    """

    DEFAULT_STATE = Path("sdlc-studio") / ".local" / "loop-state.json"

    def setUp(self) -> None:
        self._prev_cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="loop_guard_root_"))
        self.root = self.tmp / "proj"
        # `sdlc-studio/stories` is one of the project-root markers discovery looks for.
        (self.root / "sdlc-studio" / "stories").mkdir(parents=True)
        self.inner = self.root / "scripts"      # a subdirectory inside the project
        self.inner.mkdir()
        self.outside = self.tmp / "elsewhere"   # a cwd with no project above it
        self.outside.mkdir()
        self.mod = _load()

    def tearDown(self) -> None:
        os.chdir(self._prev_cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = self.mod.main(argv)
        return rc, out.getvalue(), err.getvalue()

    def _record(self, extra: list[str]) -> tuple[int, str, str]:
        return self._run(["record", "--unit", "US0010", "--signature", "sig",
                          "--cap", "9", "--repeat", "9"] + extra)

    def test_record_without_a_root_discovers_the_project_from_a_subdirectory(self) -> None:
        os.chdir(self.inner)
        rc, _out, err = self._record([])
        self.assertEqual(rc, 0, err)
        self.assertTrue((self.root / self.DEFAULT_STATE).is_file(),
                        "the state did not land under the discovered project root")
        self.assertEqual(sorted(p.name for p in self.inner.iterdir()), [],
                         "the state was written beside the cwd")

    def test_record_writes_under_the_named_root_not_the_cwd(self) -> None:
        os.chdir(self.outside)
        rc, _out, err = self._record(["--root", str(self.root)])
        self.assertEqual(rc, 0, err)
        self.assertTrue((self.root / self.DEFAULT_STATE).is_file())
        self.assertEqual(sorted(p.name for p in self.outside.iterdir()), [])

    def test_status_reads_what_record_wrote_from_a_different_directory(self) -> None:
        """Write from inside the project on the default root, read from outside it on a
        named one. If either end anchored on its own cwd the attempt count reads back 0,
        which is exactly how the handoff lost the signatures it was meant to carry."""
        os.chdir(self.inner)
        self.assertEqual(self._record([])[0], 0)
        os.chdir(self.outside)
        rc, out, err = self._run(["status", "--unit", "US0010", "--root", str(self.root)])
        self.assertEqual(rc, 0, err)
        self.assertEqual(json.loads(out)["attempts"], 1,
                         "the reader did not find the state the writer wrote")

    def test_record_prints_the_resolved_state_path(self) -> None:
        """It printed no path at all, so a state file landing in the wrong tree looked
        exactly like one landing in the right one."""
        os.chdir(self.inner)
        _rc, out, _err = self._record([])
        self.assertIn(str(self.root / self.DEFAULT_STATE), out)

    def test_a_quarantine_also_names_where_it_recorded(self) -> None:
        """The louder verdict is the one whose destination matters most."""
        os.chdir(self.inner)
        rc, out, _err = self._run(["record", "--unit", "US0010", "--signature", "sig",
                                   "--cap", "1"])
        self.assertEqual(rc, self.mod.QUARANTINE_EXIT)
        self.assertIn(str(self.root / self.DEFAULT_STATE), out)

    def test_a_relative_state_flag_anchors_on_the_root(self) -> None:
        os.chdir(self.outside)
        rc, _out, err = self._record(["--root", str(self.root), "--state", "ls.json"])
        self.assertEqual(rc, 0, err)
        self.assertTrue((self.root / "ls.json").is_file(),
                        "a relative --state was resolved against the cwd")

    def test_an_absolute_state_flag_is_honoured_verbatim(self) -> None:
        """Anchoring must not capture a path the caller chose deliberately."""
        os.chdir(self.outside)
        chosen = self.tmp / "chosen.json"
        rc, _out, err = self._record(["--root", str(self.root), "--state", str(chosen)])
        self.assertEqual(rc, 0, err)
        self.assertTrue(chosen.is_file(), "an absolute --state was re-anchored under the root")

    def test_a_named_root_is_not_re_pointed_by_discovery(self) -> None:
        """Discovery widens the default `.` only. A root the caller NAMED is where the
        state goes, even with a bigger project above it."""
        os.chdir(self.outside)
        rc, _out, err = self._record(["--root", str(self.inner)])
        self.assertEqual(rc, 0, err)
        self.assertTrue((self.inner / self.DEFAULT_STATE).is_file(),
                        "the named root was overridden by discovery")
        self.assertFalse((self.root / "sdlc-studio" / ".local").exists())

    def test_discovery_does_not_escape_a_cwd_with_no_project_above_it(self) -> None:
        """With no project anywhere above, the cwd is the honest answer - discovery must
        not walk to `/` and write into something unrelated."""
        os.chdir(self.outside)
        rc, _out, err = self._record([])
        self.assertEqual(rc, 0, err)
        self.assertTrue((self.outside / self.DEFAULT_STATE).is_file())
        self.assertFalse((self.root / "sdlc-studio" / ".local").exists())

    def test_budget_finds_the_run_state_from_a_subdirectory(self) -> None:
        """The appetite breaker read `<cwd>/sdlc-studio/.local/run-state.json`, found
        nothing from a subdirectory, and reported the run unbounded with exit 0 - a spent
        ceiling reads as 'continue'. The run it must stop is the one above it."""
        past = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(hours=2)
                ).strftime("%Y-%m-%dT%H:%M:%SZ")
        p = self.root / "sdlc-studio" / ".local" / "run-state.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"schema": 1, "run_id": "RUN-TEST", "started_at": past,
                                 "ended_at": None, "outcome": "running", "goal": None,
                                 "batch": [], "appetite": {"minutes": 1, "units": 0}}),
                     encoding="utf-8")
        os.chdir(self.inner)
        rc, _out, err = self._run(["budget", "--format", "json"])
        self.assertEqual(rc, self.mod.BUDGET_EXIT,
                         f"a spent appetite read as unbounded from a subdirectory: {err!r}")


if __name__ == "__main__":
    unittest.main()
