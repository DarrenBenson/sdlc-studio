"""The repository-root conftest keeps CI's red-detail file out of the tests' own runs (BG1731).

CI's corpus-verify step exports `SDLC_VERIFY_RED_DETAIL` in the environment that starts the test
session, so every Done fixture story a test verified red wrote a block there. These tests start a
nested session with the variable set, as CI does, and ask what a test inside it sees.
"""
# test-census-subject: conftest.py
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
VAR = "SDLC_VERIFY_RED_DETAIL"

PROBE = '''
import os


def test_probe():
    print("SEEN=" + repr(os.environ.get("{var}")))
'''


def _env(**extra: str) -> dict:
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("PYTEST_", "SDLC_TEST_")) and k not in (VAR, "TMPDIR")}
    env["PYTHONPATH"] = str(REPO)
    env.update(extra)
    return env


def _probe(parent: Path) -> Path:
    probe = parent / "probe"
    probe.mkdir()
    (probe / "test_probe.py").write_text(PROBE.format(var=VAR), encoding="utf-8")
    return probe


class RedDetailTests(unittest.TestCase):
    def _session(self, probe: Path, **env: str) -> subprocess.CompletedProcess:
        """A pytest session over a probe file outside the repository that loads the root
        conftest by name, as a session started in the repository does."""
        return subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-s", "-p", "conftest", "-p",
             "no:cacheprovider", "-o", "addopts=", str(probe)],
            cwd=probe, env=_env(**env), capture_output=True, text=True, timeout=120,
            check=False)

    def test_a_session_started_with_the_red_detail_file_set_sees_it_unset(self) -> None:
        """AC4. The probe reads `None` though the session started with a file named, and the
        file is never created."""
        with tempfile.TemporaryDirectory() as d:
            detail = Path(d, "detail.txt")
            run = self._session(_probe(Path(d)), **{VAR: str(detail)})
            self.assertEqual(0, run.returncode, run.stdout + run.stderr)
            self.assertIn("SEEN=None", run.stdout)
            self.assertFalse(detail.exists())

    def test_the_probe_reports_the_variable_when_the_conftest_is_not_loaded(self) -> None:
        """The positive control: without the conftest the same probe reads the file's name, so
        the `None` above is the conftest's doing."""
        with tempfile.TemporaryDirectory() as d:
            probe = _probe(Path(d))
            run = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", "-s", "-p", "no:cacheprovider", "-o",
                 "addopts=", str(probe)], cwd=probe, env=_env(**{VAR: "named"}),
                capture_output=True, text=True, timeout=120, check=False)
        self.assertIn("SEEN='named'", run.stdout, run.stdout + run.stderr)

    def test_the_variable_is_put_back_when_the_session_ends(self) -> None:
        """A session unsets the variable for itself and restores it afterwards, as it does the
        harness homes: the process that ran it still names the file."""
        code = ("import os, pytest\n"
                f"os.environ['{VAR}'] = 'kept'\n"
                "pytest.main(['-q', '-p', 'conftest', '-p', 'no:cacheprovider', '-o', "
                "'addopts=', os.environ['PROBE_DIR']])\n"
                f"print('AFTER=' + os.environ.get('{VAR}', 'gone'))\n")
        with tempfile.TemporaryDirectory() as d:
            probe = _probe(Path(d))
            run = subprocess.run([sys.executable, "-c", code], cwd=probe,
                                 env=_env(PROBE_DIR=str(probe)), capture_output=True, text=True,
                                 timeout=120, check=False)
        self.assertIn("AFTER=kept", run.stdout, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
