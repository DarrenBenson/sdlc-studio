"""US1112: the release verify lane's pytest batch runs on every core under its own ceiling.

The batch ran every verifier file as one serial `pytest -q` under the per-verifier ceiling. On
this workspace (2026-11-02: 1,116 stories, 262 of the 355 named test files present, 2,112 bare
pytest verifiers) it timed out at 300 s and returned `{}`, logged only under SDLC_DEBUG, and
the lane still printed `(batched)` while each of those verifiers paid its own cold start.

Each fixture test appends `<name> <PYTEST_XDIST_WORKER or -> <batch|spawn>` to a log when it
starts, so which process ran a test, and how many times, is observed rather than patched
(LL0014). A batch process carries `--junit-xml` on its command line or is an xdist worker; a
criterion's own spawn is neither.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/gate.py
from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

gate = loader.load_script("gate")
verify_ac = loader.load_script("verify_ac")

GATE = Path(__file__).resolve().parent.parent / "gate.py"
HAS_XDIST = importlib.util.find_spec("xdist") is not None

PYTEST_INI = ("[pytest]\naddopts = -p no:cacheprovider\nmarkers =\n"
              "    serial_only: runs in the serial phase\n")

#: A test that logs who ran it, sleeps, then passes or fails.
CASE = '''
def {name}():
    worker = os.environ.get("PYTEST_XDIST_WORKER", "-")
    batch = worker != "-" or any(a.startswith("--junit-xml") for a in sys.argv)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write("{name} " + worker + (" batch" if batch else " spawn") + "\\n")
    time.sleep({sleep})
    assert {passes}
'''
HEAD = ("import os\nimport sys\nimport time\nfrom pathlib import Path\n\nimport pytest\n\n"
        "LOG = Path(__file__).resolve().parent.parent / 'ran.log'\n")


def _module(cases: list[tuple[str, float, bool, bool]]) -> str:
    """A test module from (name, sleep seconds, passes, serial_only) rows."""
    body = HEAD
    for name, sleep, passes, serial in cases:
        body += ("\n@pytest.mark.serial_only" if serial else "\n") + CASE.format(
            name=name, sleep=sleep, passes=passes)
    return body


def _workspace(root: Path, files: dict[str, list]) -> list[str]:
    """Write the test files and one Done story per test naming it; return the node ids."""
    (root / "pytest.ini").write_text(PYTEST_INI, encoding="utf-8")
    (root / "tests").mkdir()
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True)
    nodes = []
    for rel, cases in files.items():
        (root / rel).write_text(_module(cases), encoding="utf-8")
        nodes += [f"{rel}::{case[0]}" for case in cases]
    for i, node in enumerate(nodes, 1):
        (stories / f"US{9100 + i}-s.md").write_text(
            f"# US{9100 + i}: s\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n"
            f"### AC1: it holds\n\n- **Verify:** pytest {node}\n", encoding="utf-8")
    return nodes


def _ran(root: Path) -> list[tuple[str, str, str]]:
    """The log, in order, as (test name, xdist worker or '-', 'batch' or 'spawn')."""
    log = root / "ran.log"
    text = log.read_text(encoding="utf-8") if log.is_file() else ""
    return [tuple(line.split(" ", 2)) for line in text.splitlines() if line]


def _env(**extra: str) -> dict:
    """This process's environment for a nested pytest: an outer xdist worker's identity removed,
    so a test reading PYTEST_XDIST_WORKER sees only its own run's, and two workers a fixture."""
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("PYTEST_XDIST_") and k != "PYTEST_ADDOPTS"}
    env["PYTEST_XDIST_AUTO_NUM_WORKERS"] = "2"
    env.update(extra)
    return env


class VerifyLaneBatchTests(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    @unittest.skipUnless(HAS_XDIST, "the criterion is given pytest-xdist")
    def test_the_batch_runs_on_xdist_with_serial_only_tests_after(self) -> None:
        """AC1. MUTANTS: `-n auto` dropped from the batch argv (the parallel tests log no
        worker); the `serial_only` tests run in the parallel phase (they log one); the second
        phase's nodes replacing the first's rather than merging (the parallel nodes go missing
        from the cache)."""
        nodes = _workspace(self.root, {
            "tests/test_par.py": [("test_p1", 0, True, False), ("test_p2", 0, True, False)],
            "tests/test_mixed.py": [("test_m1", 0, True, False), ("test_s1", 0, True, True),
                                    ("test_s2", 0, False, True)]})
        with mock.patch.dict(os.environ, _env(), clear=True):
            cache = verify_ac.pytest_batch_cache(
                self.root, 60, ["tests/test_par.py", "tests/test_mixed.py"], batch_timeout=120)
        self.assertEqual(set(nodes), set(cache), cache.reason)
        self.assertEqual(("parallel", "serial_only"), cache.phases)
        self.assertFalse(cache["tests/test_mixed.py::test_s2"], "a red serial test stays red")
        self.assertTrue(cache["tests/test_mixed.py::test_s1"])
        ran = _ran(self.root)
        parallel = [i for i, (name, _, _) in enumerate(ran) if not name.startswith("test_s")]
        serial = [i for i, (name, _, _) in enumerate(ran) if name.startswith("test_s")]
        for name, worker, _ in ran:
            if name.startswith("test_s"):
                self.assertEqual("-", worker, f"{name} is serial_only and ran on a worker")
            else:
                self.assertRegex(worker, r"^gw\d+$", f"{name} did not run on an xdist worker")
        self.assertEqual((3, 2), (len(parallel), len(serial)), ran)
        self.assertLess(max(parallel), min(serial), "the serial_only tests run afterwards")

    def test_the_batch_is_not_cut_off_at_one_verifiers_ceiling(self) -> None:
        """AC2. MUTANT: the per-verifier ceiling passed to the batch subprocess, as before. Eight
        half-second serial tests outlast a 3 s ceiling, so under it the batch is killed and the
        criteria run in their own spawns, which the log records as `spawn`."""
        cases = [(f"test_s{i}", 0.5, True, True) for i in range(8)]
        nodes = _workspace(self.root, {"tests/test_slow.py": cases})
        with mock.patch.dict(os.environ, _env(**{gate.VERIFY_BATCH_TIMEOUT_ENV: "120"}),
                             clear=True):
            res = gate._verify_acs(str(self.root), timeout=3, batch=True)
        ran = [(name, where) for name, _, where in _ran(self.root)]
        self.assertEqual(sorted((c[0], "batch") for c in cases), sorted(ran),
                         "each test runs once, in the batch, and no criterion spawns")
        self.assertEqual(0, res["count"], res["detail"])
        self.assertIn(f"batch resolved {len(nodes)} of {len(nodes)} pytest verifier(s)",
                      res["detail"])

    def test_an_empty_batch_is_named_and_falls_back(self) -> None:
        """AC3. MUTANTS: `' (batched)' if batch` restored (the clause is gone); an empty cache
        resolving a node as passed (the red criterion reads green). A 1 s batch ceiling cannot
        hold a 2 s test, so the batch times out; a second workspace names a file that does not
        exist, so the batch has nothing to run. Either way each criterion's verdict is the one a
        per-criterion run gives."""
        _workspace(self.root, {"tests/test_x.py": [("test_green", 2, True, False),
                                                   ("test_red", 0, False, False)]})
        with mock.patch.dict(os.environ, _env(**{gate.VERIFY_BATCH_TIMEOUT_ENV: "1"}),
                             clear=True):
            batched = gate._verify_acs(str(self.root), timeout=60, batch=True)
            alone = gate._verify_acs(str(self.root), timeout=60, batch=False)
        detail = batched["detail"]
        self.assertIn("batch resolved 0 of 2 pytest verifier(s)", detail)
        self.assertIn("timed out at its 1s ceiling", detail)
        self.assertNotIn("(batched)", detail)
        self.assertEqual((1, 1), (batched["count"], alone["count"]), detail)
        self.assertIn("US9102::AC1", detail, "the red criterion keeps its verdict")
        self.assertNotIn("US9101::AC1", detail, "the green criterion keeps its verdict")
        with tempfile.TemporaryDirectory() as other:
            stories = Path(other) / "sdlc-studio" / "stories"
            stories.mkdir(parents=True)
            (stories / "US9201-s.md").write_text(
                "# US9201: s\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n### AC1: a\n\n"
                "- **Verify:** pytest tests/test_gone.py::test_a\n", encoding="utf-8")
            with mock.patch.dict(os.environ, _env(), clear=True):
                gone = gate._verify_acs(other, timeout=60, batch=True)
        self.assertIn("batch resolved 0 of 1 pytest verifier(s)", gone["detail"])
        self.assertIn("none of the named test files exists", gone["detail"])
        self.assertEqual(1, gone["count"], "a verifier naming a missing file is still red")

    def test_a_batched_node_over_the_per_verifier_ceiling_reads_red(self) -> None:
        """AC4. MUTANT: a batch result trusted whatever its junit duration, which would let a
        criterion slower than its ceiling read green from the batch while its own spawn times
        out. A 3 s test under a 2 s ceiling must read as that spawn does: red, exit 124, kind
        pytest, `timeout`; the instant test beside it is the positive control. The batch
        ceiling's variable and default are named in the lane's detail and in `gate.py --help`."""
        _workspace(self.root, {"tests/test_t.py": [("test_slow", 3, True, False),
                                                   ("test_fast", 0, True, False)]})
        story = next((self.root / "sdlc-studio" / "stories").glob("US9101-*.md"))
        with mock.patch.dict(os.environ, _env(**{gate.VERIFY_BATCH_TIMEOUT_ENV: "120"}),
                             clear=True):
            res = gate._verify_acs(str(self.root), timeout=2, batch=True)
            ran_in_lane = [(name, where) for name, _, where in _ran(self.root)]
            cache = verify_ac.pytest_batch_cache(self.root, 2, ["tests/test_t.py"],
                                                 batch_timeout=120)
            from_batch = verify_ac.verify_story(story, dry_run=True, timeout=2,
                                                repo_root=self.root, pytest_cache=cache)
            own_spawn = verify_ac.verify_story(story, dry_run=True, timeout=2,
                                               repo_root=self.root)
        self.assertEqual([("test_fast", "batch"), ("test_slow", "batch")], sorted(ran_in_lane),
                         "both resolve from the batch; neither spawns on its own")
        self.assertEqual(1, res["count"], res["detail"])
        self.assertIn("US9101::AC1", res["detail"])
        self.assertNotIn("US9102::AC1", res["detail"], "the fast test is the positive control")
        self.assertEqual((1, 1), (len(from_batch.failures), len(own_spawn.failures)),
                         "the slow criterion reads red from the batch and on its own")
        got, want = from_batch.failures[0], own_spawn.failures[0]
        self.assertEqual((want["kind"], want["exit_code"]), (got["kind"], got["exit_code"]))
        self.assertEqual((("pytest", 124)), (got["kind"], got["exit_code"]))
        self.assertTrue(got["stderr"].startswith(want["stderr"]), (got, want))
        named = (rf"{gate.VERIFY_BATCH_TIMEOUT_ENV}, default "
                 rf"{gate.VERIFY_BATCH_TIMEOUT}s")
        self.assertRegex(res["detail"], named)
        out = subprocess.run([sys.executable, str(GATE), "--help"], capture_output=True,
                             text=True, check=False, timeout=60).stdout
        self.assertRegex(re.sub(r"\s+", " ", out), named)


class BatchPhaseTests(unittest.TestCase):
    """The phases' edges the criteria do not reach."""

    def test_one_failed_phase_empties_the_whole_batch(self) -> None:
        """MUTANT: the parallel phase's nodes kept when the serial_only phase dies. They would
        make the file read as collected, and its serial node, missing, as a test that does not
        exist. A serial_only test that kills its process leaves that phase no report."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _workspace(root, {"tests/test_mixed.py": [("test_p1", 0, True, False)]})
            (root / "tests" / "test_mixed.py").write_text(
                _module([("test_p1", 0, True, False)])
                + "\n@pytest.mark.serial_only\ndef test_dies():\n    os._exit(3)\n",
                encoding="utf-8")
            with mock.patch.dict(os.environ, _env(), clear=True):
                cache = verify_ac.pytest_batch_cache(root, 60, ["tests/test_mixed.py"],
                                                     batch_timeout=120)
        self.assertEqual({}, dict(cache))
        self.assertRegex(cache.reason, r"phase exited 3 with no usable report")

    def test_without_xdist_the_plan_is_one_serial_run(self) -> None:
        """MUTANT: the xdist phase planned whether or not pytest-xdist is installed, which an
        install without it refuses (exit 4), so its batch never resolves a node."""
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "t.py").write_text("import pytest\n@pytest.mark.serial_only\n",
                                          encoding="utf-8")
            serial = verify_ac.pytest_batch_plan(Path(d), ["t.py"], None)
            parallel = verify_ac.pytest_batch_plan(Path(d), ["t.py"], ["-n", "auto"])
        self.assertEqual(["serial"], [name for name, _ in serial])
        self.assertNotIn("-n", serial[0][1])
        self.assertEqual(["parallel", "serial_only"], [name for name, _ in parallel])
        self.assertEqual(["-n", "auto", "-m", "not serial_only"],
                         parallel[0][1][4:8])
        self.assertEqual(["-m", "serial_only", "t.py"], parallel[1][1][-3:])

    def test_a_class_or_file_target_is_judged_by_the_cases_under_it(self) -> None:
        """MUTANTS: a class, file or parametrised target read as a missing node (the vacuous
        red every one of the corpus's 106 such verifiers got from a batch that resolved);
        such a target read red from the batch when a case under it did not pass, where pytest
        passes a skip beside a pass; its cases' durations not summed against the ceiling."""
        cache = verify_ac.PytestBatch(
            {"t.py::C::test_a": True, "t.py::C::test_b": True, "t.py::D::test_c": False,
             "t.py::test_p[1]": True, "t.py::test_p[2]": True, "u.py::E::test_e": True,
             "u.py::E::test_f": True},
            ceiling=10, durations={"u.py::E::test_e": 6.0, "u.py::E::test_f": 6.0})
        collected = verify_ac.pytest_batch_collected(cache)

        def resolve(target):
            return verify_ac.resolve_pytest_from_cache(f"pytest {target}", cache, collected)

        self.assertEqual((True, 0), (resolve("t.py::C").ok, resolve("t.py::C").exit_code))
        self.assertTrue(resolve("t.py::test_p").ok, "a parametrised function's cases")
        self.assertIsNone(resolve("t.py::D"), "a red case under it: its own run decides")
        self.assertIsNone(resolve("t.py"), "the whole file holds D's red case")
        self.assertEqual((False, 124), (resolve("u.py::E").ok, resolve("u.py::E").exit_code),
                         "6 s + 6 s run one after another outlast a 10 s ceiling")
        self.assertTrue(resolve("u.py::E::test_e").ok, "one 6 s case is within it")
        self.assertTrue(resolve("t.py::Cx").vacuous, "a name no case sits under is missing")
        self.assertIsNone(resolve("t.py::C::test_a extra"), "two targets run on their own")

    def test_the_batch_ceiling_is_read_from_its_variable(self) -> None:
        """MUTANT: the override ignored, or a nonsense value honoured."""
        env = gate.VERIFY_BATCH_TIMEOUT_ENV
        for raw, want in (("45", 45), ("", gate.VERIFY_BATCH_TIMEOUT),
                          ("0", gate.VERIFY_BATCH_TIMEOUT), ("-5", gate.VERIFY_BATCH_TIMEOUT),
                          ("1.5", gate.VERIFY_BATCH_TIMEOUT), ("abc", gate.VERIFY_BATCH_TIMEOUT)):
            with mock.patch.dict(os.environ, {env: raw}):
                self.assertEqual(want, gate._ceiling(env, gate.VERIFY_BATCH_TIMEOUT), raw)


if __name__ == "__main__":
    unittest.main()
