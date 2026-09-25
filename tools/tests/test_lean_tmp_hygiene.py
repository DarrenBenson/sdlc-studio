"""BG0753: a test run leaves nothing behind in the temporary directory.

Tests call `tempfile.mkdtemp()` and never remove what they made, and so do the subprocesses they
spawn: one run of both suites left 225 entries, about 1,900 inodes, and a sprint of runs exhausted
/tmp's inodes mid-commit. Rather than chase each fixture, the runner confines its run to a
private directory it removes at the end, pass or fail: the repository-root conftest for pytest
(the commit's `gate.py --run-tests`, the push's full suite, a Verify line), and
`tools/skill-tests.sh` for the unittest runner, which never loads a conftest.

Each test drives the REAL conftest or script over a probe module that leaks three ways - in
process, from a subprocess, and from a failing test - with TMPDIR at an empty directory, then
counts what is left in it.
"""
# test-census-subject: tools/skill-tests.sh
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TREES = ("tools/tests", ".claude/skills/sdlc-studio/scripts/tests")

#: Leaks in process, leaks from a subprocess, and fails: the cleanup must not depend on a green run.
PROBE = '''\
import subprocess
import sys
import tempfile
import unittest


class Probe(unittest.TestCase):
    def test_leaks_a_directory(self):
        tempfile.mkdtemp()

    def test_leaks_from_a_subprocess(self):
        subprocess.run([sys.executable, "-c", "import tempfile; tempfile.mkdtemp()"], check=True)

    def test_fails(self):
        self.fail("the probe's deliberate red")
'''

#: pytest started after something has already asked `tempfile` for its directory, as a plugin or
#: the runner itself may: `tempfile` caches the answer, so a fix that only sets TMPDIR is too late.
PRIMED_PYTEST = ("import sys, tempfile; tempfile.gettempdir(); import pytest; "
                 "sys.exit(pytest.main(sys.argv[1:]))")


def _xdist_imports() -> bool:
    """CI installs pytest without pytest-xdist, so `-n` there is a usage error (BG0770)."""
    try:
        import xdist  # noqa: F401
    except ImportError:
        return False
    return True


def _env(tmpdir: Path) -> dict:
    return {**os.environ, "TMPDIR": str(tmpdir)}


def _left(tmpdir: Path) -> list[str]:
    return sorted(os.listdir(tmpdir))


class TmpHygieneTests(unittest.TestCase):

    def setUp(self) -> None:
        self._root = Path(tempfile.mkdtemp(prefix="bg0753-"))
        self.addCleanup(shutil.rmtree, self._root, True)

    def _empty_tmpdir(self, name: str) -> Path:
        path = self._root / f"tmp-{name}"
        path.mkdir()
        return path

    def test_the_probe_leaks_when_nothing_confines_it(self) -> None:
        """Positive control: with no conftest and no runner, the probe does leave directories,
        so an empty directory after a confined run is the runner's doing."""
        tests = self._root / "bare"
        tests.mkdir()
        (tests / "test_tmp_probe.py").write_text(PROBE, encoding="utf-8")
        tmp = self._empty_tmpdir("bare")
        proc = subprocess.run([sys.executable, "-m", "unittest", "test_tmp_probe"], cwd=tests,
                              env=_env(tmp), capture_output=True, text=True, timeout=120)
        self.assertEqual(1, proc.returncode, proc.stdout + proc.stderr)
        self.assertEqual(2, len(_left(tmp)), _left(tmp))

    def test_a_pytest_session_in_either_tree_leaves_no_temp_dir_behind(self) -> None:
        """AC1. The probe runs under pytest in each test tree, and in both at once as the push's
        full suite runs them, serially and under `-n 2`, with every conftest and pytest.ini copied
        into a fixture at its repository path; the `-n 2` sessions are skipped, named, where
        pytest-xdist is not installed, as on CI. MUTANTS: set only `os.environ["TMPDIR"]` (the
        primed `tempfile` cache still points at the empty directory); confine only tools/tests;
        remove the directory only on a green session."""
        fixture = self._root / "repo"
        fixture.mkdir()
        for name in ("pytest.ini", "conftest.py"):
            shutil.copy2(REPO / name, fixture / name)
        probes = []
        for tree in TREES:
            (fixture / tree).mkdir(parents=True)
            if (REPO / tree / "conftest.py").is_file():
                shutil.copy2(REPO / tree / "conftest.py", fixture / tree / "conftest.py")
            probe = fixture / tree / f"test_tmp_probe_{len(probes)}.py"   # one name per tree
            probe.write_text(PROBE, encoding="utf-8")
            probes.append(str(probe.relative_to(fixture)))
        for i, session in enumerate(([probes[0]], [probes[1]], probes)):
            for workers in ([], ["-n", "2"]):
                with self.subTest(session=session, workers=workers):
                    if workers and not _xdist_imports():
                        self.skipTest("pytest-xdist is not installed, so a -n session cannot run")
                    tmp = self._empty_tmpdir(f"session{i}-workers{len(workers)}")
                    proc = subprocess.run(
                        [sys.executable, "-c", PRIMED_PYTEST, "-q", "-p", "no:cacheprovider",
                         *workers, *session],
                        cwd=fixture, env=_env(tmp), capture_output=True, text=True, timeout=300)
                    out = proc.stdout + proc.stderr
                    self.assertEqual(1, proc.returncode, out)
                    n = len(session)
                    self.assertIn(f"{n} failed, {2 * n} passed", out)
                    self.assertEqual([], _left(tmp), out)

    def test_the_unittest_runner_leaves_no_temp_dir_behind_and_keeps_its_verdict(self) -> None:
        """AC2. `tools/skill-tests.sh` runs the probe through its unittest path. MUTANTS: a
        conftest-only fix (unittest never loads one); a trap that removes the directory and
        exits 0, replacing the suite's red."""
        skill = self._root / "skill"
        (skill / "tests").mkdir(parents=True)
        (skill / "tests" / "test_tmp_probe.py").write_text(PROBE, encoding="utf-8")
        tmp = self._empty_tmpdir("unittest")
        proc = subprocess.run(["bash", str(REPO / "tools" / "skill-tests.sh"), str(skill)],
                              cwd=REPO, env=_env(tmp), capture_output=True, text=True, timeout=300)
        out = proc.stdout + proc.stderr
        self.assertEqual(1, proc.returncode, out)
        self.assertIn("FAILED (failures=1)", out)
        self.assertEqual([], _left(tmp), out)


if __name__ == "__main__":
    unittest.main()
