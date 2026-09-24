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


if __name__ == "__main__":
    unittest.main()
