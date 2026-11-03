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
import time
import unittest
from pathlib import Path
from unittest import mock

import pytest

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
    nodes = []
    for rel, cases in files.items():
        (root / rel).write_text(_module(cases), encoding="utf-8")
        nodes += [f"{rel}::{case[0]}" for case in cases]
    _stories(root, nodes)
    return nodes


def _stories(root: Path, nodes: list[str]) -> None:
    """One Done story per node, US9101 upwards, whose one criterion is `pytest <node>`."""
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True, exist_ok=True)
    for i, node in enumerate(nodes, 1):
        (stories / f"US{9100 + i}-s.md").write_text(
            f"# US{9100 + i}: s\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n"
            f"### AC1: it holds\n\n- **Verify:** pytest {node}\n", encoding="utf-8")


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
        resolving a node as passed (the red criterion reads green); a batch that ran and
        answered none of its verifiers stating no reason. A 1 s batch ceiling cannot hold a 2 s
        test, so the batch times out; a second workspace names a file that does not exist, so
        the batch has nothing to run; a third names a class holding a skip, which the batch runs
        and cannot answer. Each criterion's verdict is the one a per-criterion run gives."""
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
        with tempfile.TemporaryDirectory() as other:
            (Path(other) / "pytest.ini").write_text(PYTEST_INI, encoding="utf-8")
            (Path(other) / "tests").mkdir()
            (Path(other) / "tests" / "test_c.py").write_text(
                "import pytest\n\nclass TestC:\n    def test_a(self):\n        assert True\n\n"
                "    @pytest.mark.skip\n    def test_b(self):\n        pass\n", encoding="utf-8")
            _stories(Path(other), ["tests/test_c.py::TestC"])
            with mock.patch.dict(os.environ, _env(), clear=True):
                skipped = gate._verify_acs(other, timeout=60, batch=True)
        self.assertIn("batch resolved 0 of 1 pytest verifier(s)", skipped["detail"])
        self.assertIn("its 2 reported test(s) answered none of them, so each ran on its own",
                      skipped["detail"])
        self.assertEqual(0, skipped["count"], "a skip beside a pass passes on its own run")

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

    def test_each_phase_argv_splits_by_its_plugin_and_never_by_a_mark_expression(self) -> None:
        """MUTANTS: the xdist arguments given to a phase other than the parallel one (a serial
        run an install without pytest-xdist refuses with exit 4, or serial_only tests on
        workers); a phase's plugin missing or swapped; a `-m` back on a command line."""
        files = ["t.py", "u.py"]
        serial = verify_ac.pytest_batch_argv("serial", files, ["-n", "auto"])
        parallel = verify_ac.pytest_batch_argv("parallel", files, ["-n", "auto"])
        alone = verify_ac.pytest_batch_argv("serial_only", ["u.py"], ["-n", "auto"])
        self.assertEqual((["pytest"], files), (serial[:1], serial[-2:]))
        self.assertEqual(["-n", "auto", "-p", "_sdlc_batch_parallel", *files], parallel[4:])
        self.assertEqual(["-p", "_sdlc_batch_serial_only", "u.py"], alone[4:])
        for argv in (serial, parallel, alone):
            self.assertNotIn("-m", argv)
        self.assertNotIn("-n", serial + alone)
        self.assertNotIn("-p", serial)

    def test_a_phase_that_exits_with_no_verdict_empties_the_batch(self) -> None:
        """MUTANT: the exit-code guard dropped, so a phase that ended its session (exit 2) is
        trusted for the partial report it still writes, and the test it never ran reads as one
        that does not exist. `pytest.exit` writes that report, so the report check alone cannot
        see it, where the `os._exit` above leaves none."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _workspace(root, {"tests/test_e.py": []})
            (root / "tests" / "test_e.py").write_text(
                "import pytest\n\n@pytest.mark.serial_only\ndef test_a():\n"
                "    pytest.exit('stop', returncode=2)\n\n@pytest.mark.serial_only\n"
                "def test_b():\n    assert True\n\ndef test_c():\n    assert True\n",
                encoding="utf-8")
            with mock.patch.dict(os.environ, _env(), clear=True):
                cache = verify_ac.pytest_batch_cache(root, 60, ["tests/test_e.py"],
                                                     batch_timeout=120)
        self.assertEqual({}, dict(cache))
        self.assertRegex(cache.reason, r"phase exited 2 with no usable report")

    # A wall-clock bound measures the load beside other work, so a commit's pytest run leaves it
    # out and the push runs it, serially (BG0963); the hook's unittest fallback runs it (BG1144).
    @pytest.mark.serial_only
    @pytest.mark.boundary_only
    def test_the_batch_ceiling_kills_the_whole_run_at_its_bound(self) -> None:
        """MUTANTS: the process group left running once the ceiling passes, so the batch waits
        for its phase to finish and the bound `SDLC_VERIFY_BATCH_TIMEOUT` sets is lost; only the
        phase's own process killed, so a process it started runs on. Asked of `_run_phase`, the
        call each phase makes, with a phase that starts a 6 s child and waits 6 s itself, under
        a 3 s ceiling: it answers None well inside the 6 s, and the file the child writes once
        its sleep ends is never written. A Python phase, not a pytest one, so no start-up under
        load can outlast the ceiling before the child exists (`started`)."""
        child = "import time, pathlib; time.sleep(6); pathlib.Path('done').write_text('x')"
        phase = ("import pathlib, subprocess, sys, time\n"
                 f"subprocess.Popen([sys.executable, '-c', {child!r}])\n"
                 "pathlib.Path('started').write_text('x')\ntime.sleep(6)\n")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            started = time.monotonic()
            rc = verify_ac._run_phase([sys.executable, "-c", phase], root, root / "out.txt", 3)
            elapsed = time.monotonic() - started
            self.assertIsNone(rc, "a phase past its ceiling answers no exit code")
            self.assertLess(elapsed, 5, "the batch waited for its phase")
            self.assertTrue((root / "started").exists(), "the phase never started its child")
            time.sleep(max(0.0, 8.0 - elapsed))
            self.assertFalse((root / "done").exists(), "the phase's child ran on past it")

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


class ProjectConfigurationTests(unittest.TestCase):
    """The batch gives the verdict a criterion's own run gives under the project's own pytest
    configuration: its mark expression, the marks its hooks apply, and the `pytest` on PATH."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_a_project_mark_expression_stays_in_force(self) -> None:
        """MUTANT: a phase's split passed as `-m`, which replaces the `-m` the project's addopts
        give. The batch then runs a test the project's own run deselects, and a criterion red on
        its own run (it selects nothing) reads green from the batch."""
        _workspace(self.root, {"tests/test_m.py": []})
        (self.root / "pytest.ini").write_text(
            '[pytest]\naddopts = -p no:cacheprovider -m "not slow"\nmarkers =\n'
            "    serial_only: s\n    slow: s\n", encoding="utf-8")
        (self.root / "tests" / "test_m.py").write_text(
            "import pytest\n\n@pytest.mark.slow\ndef test_slow():\n    assert True\n\n"
            "def test_plain():\n    assert True\n\n@pytest.mark.serial_only\n"
            "def test_serial():\n    assert True\n", encoding="utf-8")
        _stories(self.root, [f"tests/test_m.py::{name}"
                             for name in ("test_slow", "test_plain", "test_serial")])
        with mock.patch.dict(os.environ, _env(), clear=True):
            batched = gate._verify_acs(str(self.root), timeout=60, batch=True)
            alone = gate._verify_acs(str(self.root), timeout=60, batch=False)
        self.assertEqual((1, 1), (batched["count"], alone["count"]), batched["detail"])
        self.assertIn("US9101::AC1", batched["detail"], "the deselected test reads red")
        self.assertIn("batch resolved 3 of 3 pytest verifier(s)", batched["detail"])

    @unittest.skipUnless(HAS_XDIST, "the split is given pytest-xdist")
    def test_a_serial_only_mark_from_a_hook_runs_in_the_serial_phase(self) -> None:
        """MUTANTS: the serial phase run over the files whose text names the marker, so a test a
        conftest hook or a project plugin marks runs in neither phase: a passing criterion reads
        as a test that does not exist, and a class whose red case is so marked reads green; the
        phase plugin's hook not `trylast` (a project plugin loaded before it marks the test after
        it has looked); the plugins' directory last on PYTHONPATH (a module of the same name
        earlier there, as an outer batch's is, loads instead)."""
        _workspace(self.root, {"tests/test_g.py": [
            ("test_conf_tree", 0, True, False), ("test_plug_tree", 0, True, False),
            ("test_plain", 0, True, False)]})
        mark = ("import pytest\n\ndef pytest_collection_modifyitems(items):\n"
                "    for item in items:\n        if item.name.startswith('{0}'):\n"
                "            item.add_marker(pytest.mark.serial_only)\n")
        (self.root / "tests" / "conftest.py").write_text(mark.format("test_conf"),
                                                         encoding="utf-8")
        (self.root / "markplug.py").write_text(mark.format("test_plug"), encoding="utf-8")
        (self.root / "pytest.ini").write_text(
            PYTEST_INI.replace("cacheprovider", "cacheprovider -p markplug"), encoding="utf-8")
        with (self.root / "tests" / "test_g.py").open("a", encoding="utf-8") as fh:
            fh.write("\n\nclass TestC:\n    def test_ok(self):\n        assert True\n\n"
                     "    def test_conf_red(self):\n        assert False\n")
        decoy = self.root / "decoy"
        decoy.mkdir()
        (decoy / "_sdlc_batch_parallel.py").write_text("raise ImportError('decoy')\n",
                                                       encoding="utf-8")
        nodes = [f"tests/test_g.py::{n}" for n in ("test_conf_tree", "test_plug_tree",
                                                    "test_plain", "TestC")]
        _stories(self.root, nodes)
        env = _env(PYTHONPATH=f"{self.root}{os.pathsep}{decoy}")
        with mock.patch.dict(os.environ, env, clear=True):
            cache = verify_ac.pytest_batch_cache(self.root, 60, nodes, batch_timeout=120)
            ran = {name: worker for name, worker, _ in _ran(self.root)}
            batched = gate._verify_acs(str(self.root), timeout=60, batch=True)
            alone = gate._verify_acs(str(self.root), timeout=60, batch=False)
        self.assertEqual(("", ("parallel", "serial_only")), (cache.reason, cache.phases))
        self.assertEqual(("-", "-"), (ran.get("test_conf_tree"), ran.get("test_plug_tree")),
                         ran)
        self.assertRegex(ran.get("test_plain", ""), r"^gw\d+$")
        self.assertIs(False, cache.get("tests/test_g.py::TestC::test_conf_red"))
        self.assertEqual((1, 1), (batched["count"], alone["count"]), batched["detail"])
        self.assertIn("US9104::AC1", batched["detail"], "the class with a red case reads red")

    def test_the_batch_asks_the_pytest_it_runs_whether_it_takes_xdist(self) -> None:
        """MUTANTS: xdist detected in this interpreter while the batch runs the `pytest` on
        PATH. A `pytest` there that refuses `-n` (a wrapper passing `-p no:xdist`) then refuses
        the parallel phase (exit 4) and the batch resolves nothing; asked of that `pytest`, the
        batch is one serial run that resolves the criterion. Also: no retry without
        `--maxschedchunk=1`, so a `pytest` that takes `-n` and refuses only that runs serially."""
        nodes = _workspace(self.root, {"tests/test_a.py": [("test_a", 0, True, False)]})
        path = os.environ.get("PATH", "")
        with tempfile.TemporaryDirectory() as bindir:
            shim = Path(bindir) / "pytest"
            shim.write_text(f'#!/bin/sh\nexec "{sys.executable}" -m pytest -p no:xdist "$@"\n',
                            encoding="utf-8")
            shim.chmod(0o755)
            with mock.patch.dict(os.environ, _env(PATH=f"{bindir}{os.pathsep}{path}"),
                                 clear=True):
                cache = verify_ac.pytest_batch_cache(self.root, 60, nodes, batch_timeout=120)
            shim.write_text(
                '#!/bin/sh\nfor a in "$@"; do [ "$a" = --maxschedchunk=1 ] && exit 4; done\n'
                f'exec "{sys.executable}" -m pytest "$@"\n', encoding="utf-8")
            with mock.patch.dict(os.environ, _env(PATH=f"{bindir}{os.pathsep}{path}"),
                                 clear=True):
                unchunked = verify_ac._xdist_args(self.root, nodes[0].split("::")[0], 60)
        self.assertEqual(("", ("serial",)), (cache.reason, cache.phases))
        self.assertEqual({nodes[0]: True}, dict(cache))
        self.assertEqual(["-n", "auto"] if HAS_XDIST else None, unchunked)

    def test_a_refused_command_line_is_named_by_its_error(self) -> None:
        """MUTANT: the reason quoting the phase's last output line, which for a refused command
        line is pytest's `rootdir:` line rather than the error."""
        nodes = _workspace(self.root, {"tests/test_a.py": [("test_a", 0, True, False)]})
        (self.root / "pytest.ini").write_text(
            PYTEST_INI.replace("cacheprovider", "cacheprovider --no-such-option"),
            encoding="utf-8")
        with mock.patch.dict(os.environ, _env(), clear=True):
            cache = verify_ac.pytest_batch_cache(self.root, 60, nodes, batch_timeout=120)
        self.assertEqual({}, dict(cache))
        self.assertRegex(cache.reason, r"phase exited 4 with no usable report \(.*unrecognized "
                                       r"arguments: --no-such-option\)$")


if __name__ == "__main__":
    unittest.main()
