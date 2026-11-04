"""BG1160: `gate.py --run-tests` refuses a path that does not exist, by name, before any test runs.

A missing path beside a real one made pytest-xdist exit 5 having run nothing ('no tests ran'),
and the lane reads 5 as a pass, so a failing module beside a stale path read green. A serial run
exits 4 on the same argv. Each case below drives the shipped CLI against a throwaway root, once
with pytest-xdist and once with it hidden, and a test that runs leaves a file behind, so "no test
ran" is observed rather than inferred from an exit code; a conftest leaves another when pytest
starts at all.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/gate.py
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

gate = loader.load_script("gate")

GATE = Path(__file__).resolve().parent.parent / "gate.py"

#: A failing test that leaves `ran.flag` in its root when it executes.
RED = ('from pathlib import Path\n\n\n'
       'def test_red():\n'
       '    (Path(__file__).parent / "ran.flag").write_text("ran")\n'
       '    assert False, "the red module ran and failed"\n')

#: Runs gate.py with pytest-xdist hidden, so `--run-tests` takes its serial path.
HIDE_XDIST = ("import importlib.util, runpy, sys\n"
              "real = importlib.util.find_spec\n"
              "importlib.util.find_spec = lambda n, *a: None if n == 'xdist' else real(n, *a)\n"
              "sys.argv = sys.argv[1:]\n"
              "runpy.run_path(sys.argv[0], run_name='__main__')\n")

RUNNERS = {"xdist": [sys.executable, str(GATE)],
           "serial": [sys.executable, "-c", HIDE_XDIST, str(GATE)]}


def _env() -> dict:
    """This environment minus an outer xdist worker's identity and any boundary the caller set."""
    return {k: v for k, v in os.environ.items()
            if not k.startswith(("PYTEST_XDIST", "PYTEST_CURRENT_TEST", "GIT_"))
            and k not in ("SDLC_GATE_BOUNDARY", "SDLC_STUDIO_BOUNDARY_SUITE")}


#: A conftest that leaves `started.flag` when pytest starts in the root, whatever it runs.
STARTED = ('from pathlib import Path\n\n\n'
           'def pytest_configure(config):\n'
           '    (Path(__file__).parent / "started.flag").write_text("started")\n')


def _fixture(root: Path) -> None:
    (root / "conftest.py").write_text(STARTED, encoding="utf-8")
    (root / "test_red.py").write_text(RED, encoding="utf-8")
    (root / "sub").mkdir()
    (root / "sub" / "test_ok.py").write_text("def test_ok():\n    pass\n", encoding="utf-8")


def _run(runner: str, root: Path, *selectors: str) -> subprocess.CompletedProcess:
    # cwd is a different directory from --root, so a check read against the cwd is caught.
    return subprocess.run([*RUNNERS[runner], "--root", str(root), "--run-tests", *selectors],
                          capture_output=True, text=True, env=_env(), cwd=str(GATE.parent),
                          timeout=300)


class RunTestsPathTests(unittest.TestCase):

    def test_a_missing_path_is_refused_by_name_before_any_test_runs(self) -> None:
        """AC1. MUTANTS: drop the refusal (xdist exits 5 and the lane passes); refuse with exit 0;
        refuse after the run; name the count but not the paths; test the path against the cwd
        rather than `--root`."""
        for runner in RUNNERS:
            for missing in (["does_not_exist.py"], ["gone/test_x.py::test_x", "nope/"]):
                with self.subTest(runner=runner, missing=missing), \
                        tempfile.TemporaryDirectory() as d:
                    root = Path(d)
                    _fixture(root)
                    proc = _run(runner, root, "test_red.py", *missing)
                    self.assertEqual(2, proc.returncode, proc.stdout + proc.stderr)
                    self.assertIn("refused", proc.stderr)
                    listed = proc.stderr.rsplit("no test ran: ", 1)[-1].strip().split(", ")
                    self.assertEqual(missing, listed, proc.stderr)
                    self.assertFalse((root / "ran.flag").exists(), "a test ran before the refusal")
                    self.assertFalse((root / "started.flag").exists(), "pytest started")

    def test_a_failing_test_fails_the_run_when_every_path_is_real(self) -> None:
        """AC2, the positive control: a file, a directory and a node id under `--root` all pass the
        check, the red test runs and the run exits 1. MUTANTS: keep the `::test_red` suffix in the
        existence check; test the path against the cwd; treat pytest's 1 as a pass."""
        for runner in RUNNERS:
            with self.subTest(runner=runner), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _fixture(root)
                proc = _run(runner, root, "test_red.py::test_red", "sub")
                out = proc.stdout + proc.stderr
                self.assertEqual(1, proc.returncode, out)
                self.assertNotIn("refused", out)
                self.assertIn("the red module ran and failed", out)
                self.assertTrue((root / "ran.flag").exists(), out)
                self.assertTrue((root / "started.flag").exists(), "the conftest probe is inert")
                passing = _run(runner, root, "sub", str(root / "sub" / "test_ok.py"))
                self.assertEqual(0, passing.returncode, passing.stdout + passing.stderr)

    def test_a_name_that_cannot_be_statted_reads_as_missing(self) -> None:
        """A component longer than the filesystem allows, or a NUL byte, is named missing rather
        than raising. MUTANT: `Path(root, path).exists()`, which raises ENAMETOOLONG on the long name
        under Python 3.10 and 3.12, though not 3.14."""
        with tempfile.TemporaryDirectory() as d:
            _fixture(Path(d))
            long_name, nul = "x" * 300 + ".py", "a\0b.py"
            self.assertEqual([long_name, nul, "nope.py::t"],
                             gate.missing_test_paths(
                                 ["test_red.py", long_name, "sub", nul, "nope.py::t"], d))

    def test_the_commit_selection_never_names_a_deleted_module(self) -> None:
        """The hook hands `--run-tests` only what `select_tests` names, so a commit deleting a test
        module must not select it, or the refusal would block that commit. MUTANT: add a changed
        test-module path without asking whether it is on disk."""
        with tempfile.TemporaryDirectory() as d:
            kept = Path(d) / "tools" / "tests" / "test_kept.py"
            kept.parent.mkdir(parents=True)
            kept.write_text("def test_kept():\n    pass\n", encoding="utf-8")
            got = gate.select_tests(d, ["tools/tests/test_gone.py", "tools/tests/test_kept.py"])
        self.assertTrue(got["resolved"], got)
        self.assertEqual(["tools/tests/test_kept.py"], got["selectors"])


if __name__ == "__main__":
    unittest.main()
