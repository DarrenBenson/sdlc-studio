"""US0880: a commit's tests finish inside a 90-second budget.

A commit runs only the test modules its change reaches - the changed test module, `test_x.py`
for `x.py`, and the modules that import or load `x` by name - in parallel where pytest-xdist is
installed, and reports its elapsed time against 90 seconds without ever refusing on it. A docs
or artefact commit runs no unit suite; the full suite at push is the backstop for both.

The hook cases DRIVE THE REAL HOOKS in throwaway repositories. Only the selection-speed case
reads this repository, because its criterion is about this repository.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/gate.py
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
REPO = SCRIPTS.parents[3]
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(HERE))
import gate  # noqa: E402
import gitutil  # noqa: E402

SKILL = ".claude/skills/sdlc-studio/scripts"


def _write(root: Path, rel: str, body: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _hook_env() -> dict:
    """The confined git env, minus the pytest variables of the run executing THIS test: a nested
    run must not inherit an outer xdist worker's identity, or the probe below proves nothing."""
    return {k: v for k, v in gitutil.git_env().items()
            if not k.startswith(("PYTEST_XDIST", "PYTEST_CURRENT_TEST"))}


def _hook_fixture(tmp: Path):
    """The pre-commit fixture from tools/tests, with gate.py answering the selection for real.

    Every other lane is stubbed to pass, so the only thing deciding whether a suite runs is the
    shipped selection and the hooks that act on it."""
    sys.path.insert(0, str(REPO / "tools" / "tests"))
    import test_precommit_window_guard as wg  # noqa: PLC0415 - repo-only fixture module
    root = wg.WindowGuardTests("run")._repo(tmp)
    real = str(SCRIPTS / "gate.py")
    _write(root, f"{SKILL}/gate.py",
           "import runpy, sys\n"
           "if '--suite-decision' in sys.argv or '--run-tests' in sys.argv:\n"
           f"    sys.argv[0] = {real!r}\n"
           f"    runpy.run_path({real!r}, run_name='__main__')\n"
           "sys.exit(0)\n")
    _write(root, "tools/tests/test_thing.py", "def test_thing():\n    assert True\n")
    # Names the doc the docs-only commit edits: a selection that matched test sources by text
    # would pick it, and selection must not.
    _write(root, "tools/tests/test_reads_guide.py",
           "GUIDE = 'docs/guide.md'\n\n\ndef test_guide():\n    assert GUIDE\n")
    gitutil.git(["add", "-A"], cwd=root)
    gitutil.git(["commit", "-q", "--no-verify", "-m", "selection answers for real"], cwd=root)
    return root


def _commit(root: Path, files: dict) -> tuple[int, str]:
    for rel, body in files.items():
        _write(root, rel, body)
    gitutil.git(["add", "-A"], cwd=root)
    out = subprocess.run(["git", "-C", str(root), "commit", "-m", "docs: paperwork"],
                         capture_output=True, text=True, env=_hook_env(), timeout=600)
    return out.returncode, out.stdout + out.stderr


#: A probe test for the commit-msg fixture. Where pytest-xdist is installed it fails unless it
#: runs inside an xdist worker, so a serial run of a selection cannot pass for a parallel one.
PROBE = """\
import importlib.util
import os


def test_probe():
    assert {verdict}
    if importlib.util.find_spec("xdist") is not None:
        assert os.environ.get("PYTEST_XDIST_WORKER"), "the selection did not run in parallel"
"""


#: A red `serial_only` test: only the serial phase runs it where pytest-xdist is installed.
RED_SERIAL = """\
import pytest


@pytest.mark.serial_only
def test_red_alone():
    assert False, "the serial phase ran and this test failed"
"""

#: A module that cannot be collected: pytest exits 2, which is not a pass.
UNIMPORTABLE = "import no_such_module_us0880  # noqa: F401\n\n\ndef test_x():\n    pass\n"

#: Runs gate.py with pytest-xdist hidden, so `--run-tests` takes its serial path.
HIDE_XDIST = ("import importlib.util, runpy, sys\n"
              "real = importlib.util.find_spec\n"
              "importlib.util.find_spec = lambda n, *a: None if n == 'xdist' else real(n, *a)\n"
              "sys.argv = sys.argv[1:]\n"
              "runpy.run_path(sys.argv[0], run_name='__main__')\n")


def _commit_msg(tmp: Path, precommit_seconds: int, passing: bool = True,
                extra: "dict | None" = None) -> tuple[int, str]:
    """Run the real commit-msg hook over a handover selecting the probe module and `extra`."""
    root = tmp / "r"
    root.mkdir()
    gitutil.git(["init", "-q"], cwd=root)
    _write(root, ".githooks/commit-msg", (REPO / ".githooks" / "commit-msg").read_text())
    (root / ".claude" / "skills" / "sdlc-studio").mkdir(parents=True)
    (root / SKILL).symlink_to(SCRIPTS)
    modules = {"tools/tests/test_probe.py": PROBE.format(verdict="True" if passing else "False"),
               **(extra or {})}
    for rel, body in modules.items():
        _write(root, rel, body)
    git_dir = root / ".git"
    _write(root, ".git/sdlc-gate-suites", f"precommit_seconds={precommit_seconds}\n"
           + "".join(f"suite-selector={rel}\n" for rel in modules))
    msg = _write(root, ".git/COMMIT_EDITMSG", "chore: probe\n")
    out = subprocess.run(["bash", str(root / ".githooks" / "commit-msg"), str(msg)], cwd=root,
                         capture_output=True, text=True, env=_hook_env(), timeout=600)
    assert not (git_dir / "sdlc-gate-suites").exists(), "the handover was not consumed"
    return out.returncode, out.stdout + out.stderr


class SelectionTests(unittest.TestCase):

    def test_a_script_change_selects_its_tests_and_importers(self) -> None:
        """AC1. MUTANTS: always add the modules with no measurable reads; drop the import, the
        naming or the loader route; follow dependents transitively."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, f"{SKILL}/foo.py", "def bar():\n    return 1\n")
            _write(root, f"{SKILL}/hub.py", "import foo\n")
            tests = f"{SKILL}/tests"
            _write(root, f"{tests}/test_foo.py", "def test_x():\n    pass\n")
            _write(root, f"{tests}/test_uses_foo.py", "from foo import bar\n")
            _write(root, f"{tests}/test_grouped.py",
                   "from lib import (\n    sdlc_md,\n    foo,\n)\n")
            _write(root, "tools/tests/test_loads_foo.py",
                   "import importlib.util\n"
                   "spec = importlib.util.spec_from_file_location('foo', 'x/foo.py')\n")
            # Reads nothing a scanner could measure: the shape the old selection always added.
            _write(root, f"{tests}/test_unrelated.py", "import json\n\nVALUE = json.dumps(1)\n")
            _write(root, f"{tests}/test_foo_extra.py", "import foo_extra\n")
            # Reaches foo only through hub.py: a transitive dependent, not an importer.
            _write(root, f"{tests}/test_hub.py", "import hub\n")
            got = gate.select_tests(str(root), [f"{SKILL}/foo.py"])
        self.assertTrue(got["resolved"], got["reason"])
        self.assertEqual({f"{tests}/test_foo.py", f"{tests}/test_uses_foo.py",
                          f"{tests}/test_grouped.py", "tools/tests/test_loads_foo.py"},
                         set(got["selectors"]))
        self.assertEqual(7 - 4, got["excluded"])

    def test_a_docs_only_commit_runs_no_suite(self) -> None:
        """AC2, through the real hooks. MUTANTS: select a module for a markdown path, or the
        modules whose source names it; run everything on a `skip` answer, or fall back to the
        path match (the doc under tools/ matches it)."""
        with tempfile.TemporaryDirectory() as d:
            root = _hook_fixture(Path(d))
            rc, out = _commit(root, {"docs/guide.md": "# Guide\n",
                                     "sdlc-studio/stories/US0001-a-story.md": "# US0001: A\n",
                                     ".claude/skills/sdlc-studio/reference-x.md": "# Ref\n",
                                     "tools/README.md": "# Tools\n"})
            self.assertEqual(0, rc, out)
            self.assertRegex(out, r"SKIP\S*\s+unit suites - no test module imports")
            self.assertNotRegex(out, r"\b(ok|FAIL)\S*\s+(unit-tests|skill-tests|tool-tests)\b")
            self.assertIn("gate green.", out)
            # The control: a code change in the same fixture reaches its test module and runs it.
            rc, out = _commit(root, {"tools/thing.py": "VALUE = 2\n"})
            self.assertEqual(0, rc, out)
            self.assertRegex(out, r"\bok\S*\s+(unit-tests|tool-tests)\b",
                             f"the control commit ran no suite, so the skip proves nothing:\n{out}")

    def test_the_budget_is_reported_not_enforced(self) -> None:
        """AC3. MUTANTS: set `fail` when over budget; drop the report; run the selection
        serially where pytest-xdist is installed; drop the selected suite lane; ignore the
        serial phase's exit code or never run it; read a collection error (exit 2) as a pass."""
        parallel = gate.run_tests_plan(["a/test_a.py"], parallel=True)
        self.assertIn("-n", parallel[0])
        self.assertEqual("auto", parallel[0][parallel[0].index("-n") + 1])
        self.assertEqual(1, len(parallel), "no module carries the marker, so no serial phase")
        self.assertNotIn("-n", gate.run_tests_plan(["a/test_a.py"], parallel=False)[0])
        with tempfile.TemporaryDirectory() as d:
            rc, out = _commit_msg(Path(d), precommit_seconds=500)
        self.assertEqual(0, rc, f"an over-budget commit was refused:\n{out}")
        self.assertRegex(out, r"\bok\S*\s+unit-tests\b", out)
        self.assertRegex(out, r"over budget\S*\s+this commit took 5\d\ds against a 90s budget - "
                              r"reported, not refused", out)
        with tempfile.TemporaryDirectory() as d:
            rc, out = _commit_msg(Path(d), precommit_seconds=0)
        self.assertEqual(0, rc, out)
        self.assertRegex(out, r"this commit took \d+s of its 90s budget", out)
        self.assertNotIn("over budget", out)
        # The control: the lane does gate on the tests it runs.
        with tempfile.TemporaryDirectory() as d:
            rc, out = _commit_msg(Path(d), precommit_seconds=500, passing=False)
        self.assertNotEqual(0, rc, f"a failing selected test was committed:\n{out}")
        self.assertRegex(out, r"FAIL\S*\s+\S*unit-tests", out)
        self.assertIn("reported, not refused", out)
        # A red serial_only test and an unimportable module each refuse the commit, beside a
        # green probe - so neither phase's verdict can be dropped.
        for case, extra, evidence in (
                ("red serial_only test", {"tools/tests/test_red_alone.py": RED_SERIAL},
                 "the serial phase ran and this test failed"),
                ("unimportable module", {"tools/tests/test_unimportable.py": UNIMPORTABLE},
                 "no_such_module_us0880")):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as d:
                rc, out = _commit_msg(Path(d), precommit_seconds=0, extra=extra)
                self.assertNotEqual(0, rc, f"a {case} was committed:\n{out}")
                self.assertRegex(out, r"FAIL\S*\s+\S*unit-tests", out)
                self.assertIn(evidence, out, f"the {case} never reached the run:\n{out}")
        # Under xdist a collection error exits 1; a serial run - no xdist, or the serial phase -
        # exits 2, and that is not a pass either.
        with tempfile.TemporaryDirectory() as d:
            _write(Path(d), "test_unimportable.py", UNIMPORTABLE)
            _write(Path(d), "test_ok.py", "def test_ok():\n    pass\n")
            proc = subprocess.run([sys.executable, "-c", HIDE_XDIST, str(SCRIPTS / "gate.py"),
                                   "--root", d, "--run-tests", "test_unimportable.py",
                                   "test_ok.py"],
                                  capture_output=True, text=True, env=_hook_env(), timeout=300)
        self.assertIn("serially", proc.stdout, proc.stdout + proc.stderr)
        self.assertIn("no_such_module_us0880", proc.stdout + proc.stderr)
        self.assertNotEqual(0, proc.returncode, f"a collection error passed:\n{proc.stdout}")

    def test_selection_is_fast_on_this_repository(self) -> None:
        """AC4. MUTANT: build the whole repository's import graph again (about four seconds)."""
        changed = f"{SKILL}/next_id.py"
        started = time.monotonic()
        proc = subprocess.run([sys.executable, str(SCRIPTS / "gate.py"), "--root", str(REPO),
                               "--suite-decision", "--changed", changed],
                              capture_output=True, text=True, timeout=60)
        elapsed = time.monotonic() - started
        self.assertIn(f"suite-selector: {SKILL}/tests/test_next_id.py", proc.stdout,
                      f"the selection did not answer, so its speed proves nothing:\n{proc.stdout}"
                      f"{proc.stderr}")
        self.assertLess(elapsed, 3.0, f"selection took {elapsed:.1f}s")


#: Forty quick tests, each recording the xdist worker that ran it under its own index.
RECORD_WORKER = """\
import os
from pathlib import Path

import pytest

OUT = Path(__file__).parent / "ran"


@pytest.mark.parametrize("i", range(40))
def test_n(i):
    OUT.mkdir(exist_ok=True)
    (OUT / f"{i:02d}").write_text(os.environ.get("PYTEST_XDIST_WORKER", ""))
"""

#: A pytest plugin standing in for a sibling process: each time a mutation run creates its sink,
#: another process drops a `mutation_run_*` file into the SHARED temp directory. With
#: US0892_LEAK set it also stops the run removing its own sink, which is the leak the check is for.
SIBLING_PLUGIN = """\
import itertools
import os
import subprocess
import tempfile

_mkstemp, _unlink, _count = tempfile.mkstemp, os.unlink, itertools.count()


def mkstemp(*args, **kwargs):
    if kwargs.get("prefix") == "mutation_run_":
        shared = os.environ["US0892_SHARED"]
        subprocess.run(["touch", os.path.join(shared, f"mutation_run_sibling_{next(_count)}.log")],
                       check=True)
    return _mkstemp(*args, **kwargs)


def unlink(path, *args, **kwargs):
    if os.environ.get("US0892_LEAK") and os.path.basename(path).startswith("mutation_run_"):
        return None
    return _unlink(path, *args, **kwargs)


tempfile.mkstemp, os.unlink = mkstemp, unlink
"""

LEAK_CHECK = (f"{SKILL}/tests/test_mutation.py::TheRunLeavesNothingBehindTests::"
              "test_a_construction_failure_leaks_no_descriptor_and_no_temp_file")


def _pytest_env(**extra: str) -> dict:
    """This environment minus the pytest identity of the run executing THIS test, plus `extra`."""
    import os  # noqa: PLC0415
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("PYTEST_XDIST", "PYTEST_CURRENT_TEST"))}
    env.update(extra)
    return env


def _xdist_version(version: "str | None"):
    """Stub the installed pytest-xdist version; None stands for a missing distribution."""
    import importlib.metadata  # noqa: PLC0415
    import unittest.mock  # noqa: PLC0415
    real = importlib.metadata.version

    def version_of(name: str) -> str:
        if name != "pytest-xdist":
            return real(name)
        if version is None:
            raise importlib.metadata.PackageNotFoundError(name)
        return version
    return unittest.mock.patch("importlib.metadata.version", side_effect=version_of)


class SchedulingTests(unittest.TestCase):
    """US0892: the parallel phase hands tests out one at a time, so a run of heavy consecutive
    tests is spread across the workers rather than queued up front on one of them."""

    def test_the_parallel_phase_hands_out_one_test_at_a_time(self) -> None:
        """AC1. MUTANTS: drop `--maxschedchunk=1` (xdist's first hand-out is then a quarter of
        each worker's share, so tests 0-4 of 40 land on one of two workers); misspell it (pytest
        refuses the option); add it to the serial phase or the xdist-less command (the exact
        command comparison below changes)."""
        with tempfile.TemporaryDirectory() as d, _xdist_version("3.2.0"):
            root = Path(d)
            _write(root, "a/test_a.py", "def test_a():\n    pass\n")
            _write(root, "b/test_b.py",
                   "import pytest\n\n\n@pytest.mark.serial_only\ndef test_b():\n    pass\n")
            plan = gate.run_tests_plan(["a/test_a.py", "b/test_b.py"], parallel=True, root=d)
        base = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"]
        self.assertEqual(2, len(plan), plan)
        self.assertIn("--maxschedchunk=1", plan[0])
        self.assertEqual(base + ["-m", "serial_only", "b/test_b.py"], plan[1],
                         "the serial_only phase changed")
        with _xdist_version("3.2.0"):
            serial = gate.run_tests_plan(["a/test_a.py"], parallel=False)
        self.assertEqual([base + ["a/test_a.py"]], serial)
        # Behaviour, not the flag's spelling: the parallel command, on two workers, over forty
        # tests. xdist's default first hand-out gives each worker five consecutive tests; one at
        # a time it gives two (the floor xdist keeps queued), so test 02 is on the other worker.
        import importlib.util  # noqa: PLC0415
        if importlib.util.find_spec("xdist") is None:
            self.skipTest("pytest-xdist is not installed, so there is no hand-out to observe")
        if not gate.xdist_takes_maxschedchunk():
            self.skipTest("this pytest-xdist predates --maxschedchunk, so the default hand-out")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "test_record.py", RECORD_WORKER)
            argv = gate.run_tests_plan(["test_record.py"], parallel=True, root=d)[0]
            argv[argv.index("-n") + 1] = "2"
            proc = subprocess.run(argv, cwd=d, capture_output=True, text=True,
                                  env=_pytest_env(), timeout=300)
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            ran = {p.name: p.read_text() for p in (root / "ran").iterdir()}
        self.assertEqual(40, len(ran), ran)
        self.assertEqual({"gw0", "gw1"}, set(ran.values()), ran)
        self.assertNotEqual(ran["00"], ran["02"],
                            f"tests 00 and 02 were handed to one worker up front: {ran}")

    def test_an_xdist_without_the_option_gets_the_default_hand_out(self) -> None:
        """Round-2 review: `--maxschedchunk` arrived in pytest-xdist 3.2.0, and an older one exits
        4 on it, refusing every commit and push. MUTANTS: add the flag whatever the version;
        compare the version as text ("3.10.0" < "3.2.0"); read a missing or unparseable version
        as new enough."""
        for version, expected in (("3.1.0", False), ("2.5.0", False), ("3.2.0", True),
                                  ("3.10.1", True), ("4.0", True), ("3.2.0rc1", False),
                                  (None, False)):
            with self.subTest(version=version), _xdist_version(version):
                plan = gate.run_tests_plan(["a/test_a.py"], parallel=True)
                self.assertEqual(expected, "--maxschedchunk=1" in plan[0], plan[0])
                self.assertEqual(["-n", "auto"], plan[0][6:8], plan[0])

    def test_a_refused_option_is_named_in_the_full_suite_verdict(self) -> None:
        """Round-2 review: a pytest usage error (exit 4) ends on its rootdir line, so the push's
        full-suite refusal named no reason. MUTANT: name the last line of the output again."""
        import unittest.mock  # noqa: PLC0415
        bad = [[sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                "--no-such-option-us0892", "tools/tests/test_x.py"]]
        with tempfile.TemporaryDirectory() as d:
            _write(Path(d), "tools/tests/test_x.py", "def test_x():\n    pass\n")
            with unittest.mock.patch.object(gate, "run_tests_plan", return_value=bad):
                got = gate._full_suite(d)
        self.assertEqual(1, got["count"], got)
        self.assertIn("unrecognized arguments: --no-such-option-us0892", got["detail"])

    def test_a_sibling_temp_file_cannot_redden_the_leak_check(self) -> None:
        """AC2. The leak check runs while a sibling process drops `mutation_run_*` files into the
        shared temp directory, and passes; the control makes the run leak its own sink, and the
        check still catches it. MUTANTS: count the shared temp directory again (the siblings
        redden it); count a private directory the sink never lands in (the control passes)."""
        import importlib.util  # noqa: PLC0415
        if importlib.util.find_spec("pytest") is None:
            self.skipTest("pytest is not installed")
        for leak in (False, True):
            with self.subTest(leak=leak), tempfile.TemporaryDirectory() as d:
                shared, plugins = Path(d) / "tmp", Path(d) / "plugins"
                shared.mkdir()
                _write(plugins, "us0892_sibling.py", SIBLING_PLUGIN)
                env = _pytest_env(TMPDIR=str(shared), US0892_SHARED=str(shared),
                                  PYTHONPATH=str(plugins), **({"US0892_LEAK": "1"} if leak else {}))
                proc = subprocess.run(
                    [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                     "-p", "no:xdist", "-p", "us0892_sibling", str(REPO / LEAK_CHECK)],
                    cwd=d, capture_output=True, text=True, env=env, timeout=300)
                out = proc.stdout + proc.stderr
                siblings = list(shared.glob("mutation_run_sibling_*"))
                self.assertEqual(5, len(siblings),
                                 f"the sibling never wrote, so a pass proves nothing:\n{out}")
                if leak:
                    self.assertNotEqual(0, proc.returncode, f"a leaked sink went unseen:\n{out}")
                    self.assertIn("a failed run left its sink behind", out)
                else:
                    self.assertEqual(0, proc.returncode, out)


#: Four tests, each recording that it ran: two the commit leaves to the push, in each phase.
BOUNDARY_ONLY_MODULE = """\
import os
from pathlib import Path

import pytest


def _ran(name):
    Path(os.environ["US0893_RAN"], name).write_text("ran")


@pytest.mark.boundary_only
def test_live_repository():
    _ran("boundary")


def test_quick():
    _ran("quick")


@pytest.mark.serial_only
@pytest.mark.boundary_only
def test_live_tree():
    _ran("serial-boundary")


@pytest.mark.serial_only
def test_tree():
    _ran("serial")
"""

#: The tests the measurement named: each runs the real gate over this repository.
LIVE_REPOSITORY_TESTS = (
    "GateRealWrapperTests::test_real_wrappers_run_and_shape",
    "GateRealWrapperTests::test_the_real_gate_runs_once_per_class",
    "RevertCheckLaneTests::test_the_lane_runs_at_the_boundary_and_not_per_commit",
    "ModuleAloneLaneTests::test_the_push_boundary_runs_every_module_alone_and_names_the_one_"
    "that_fails",
    "DocSurfaceApplicabilityTests::test_doc_surface_still_measures_the_skill_repo_and_a_bare_tree",
)


class BoundaryOnlyTests(unittest.TestCase):
    """US0893: a commit's selected run leaves the `boundary_only` tests to the push, whose full
    suite runs them."""

    def test_the_commit_skips_boundary_only_and_the_push_runs_it(self) -> None:
        """AC1. MUTANTS: never pass the commit switch (the commit runs the marked tests); exclude
        the marker in the parallel phase only (the serial phase runs `test_live_tree`); exclude
        it where xdist is installed only (the serial path runs both); exclude it at the push
        too (the full suite never runs them)."""
        with tempfile.TemporaryDirectory() as d:
            root, ran = Path(d) / "proj", Path(d) / "ran"
            (root / "sdlc-studio").mkdir(parents=True)
            _write(root, "pytest.ini", (REPO / "pytest.ini").read_text(encoding="utf-8"))
            _write(root, "tools/tests/test_us0893.py", BOUNDARY_ONLY_MODULE)
            env = {k: v for k, v in _pytest_env(US0893_RAN=str(ran)).items()
                   if not k.startswith("GIT_")}
            gate_py = str(SCRIPTS / "gate.py")
            runs = (
                ("commit", [gate_py, "--root", str(root), "--run-tests",
                            "tools/tests/test_us0893.py"], {"quick", "serial"}),
                ("commit without xdist", ["-c", HIDE_XDIST, gate_py, "--root", str(root),
                                          "--run-tests", "tools/tests/test_us0893.py"],
                 {"quick", "serial"}),
                ("push", [gate_py, "--root", str(root), "--boundary", "push", "--only",
                          "full-suite"], {"quick", "serial", "boundary", "serial-boundary"}),
            )
            for label, argv, expected in runs:
                with self.subTest(run=label):
                    shutil.rmtree(ran, ignore_errors=True)
                    ran.mkdir()
                    proc = subprocess.run([sys.executable, *argv], cwd=root, capture_output=True,
                                          text=True, env=env, timeout=600)
                    out = proc.stdout + proc.stderr
                    self.assertEqual(0, proc.returncode, out)
                    self.assertEqual(expected, {p.name for p in ran.iterdir()}, out)

    def test_the_live_repository_tests_are_boundary_only(self) -> None:
        """AC2. MUTANTS: drop a named test's marker (it leaves the collected set); mark the whole
        class (an unmarked sibling joins it); drop the marker's registration from pytest.ini."""
        import configparser  # noqa: PLC0415
        ini = configparser.ConfigParser()
        ini.read(REPO / "pytest.ini", encoding="utf-8")
        markers = {line.split(":")[0].strip()
                   for line in ini["pytest"]["markers"].splitlines() if line.strip()}
        self.assertLessEqual({"serial_only", "boundary_only"}, markers, markers)
        module = f"{SKILL}/tests/test_gate.py"
        proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                               "-p", "no:xdist", "--collect-only", "-m", "boundary_only", module],
                              cwd=REPO, capture_output=True, text=True, env=_pytest_env(),
                              timeout=300)
        collected = {line.split("::", 1)[1] for line in proc.stdout.splitlines()
                     if line.startswith(f"{module}::")}
        for node in LIVE_REPOSITORY_TESTS:
            self.assertIn(node, collected, proc.stdout + proc.stderr)
        # The control: each marked test's quick sibling still runs on the commit.
        for sibling in ("GateRealWrapperTests::test_main_maps_result_to_exit_code_without_rerunning",
                        "DocSurfaceApplicabilityTests::test_one_applicability_predicate_decides_"
                        "for_every_reader"):
            self.assertNotIn(sibling, collected, collected)


if __name__ == "__main__":
    unittest.main()
