"""BG1197: a pytest run from this repository reads the meter its fixtures mean, whatever harness runs it.

The token meter chooses its reader from `SDLC_STUDIO_HARNESS`, then from each harness's signal
variables, so a suite run inside Cursor, Copilot CLI or OpenCode chose that harness's reader for
tests whose fixture is a Claude transcript. The repository-root conftest.py clears every variable
`token_meters.selection_variables()` names before each test.

Each harness case runs `test_lean_transcript_dir.py`, one of the modules that reach the meter, in
a child pytest from the repository root under that harness's environment, and again with
`--noconftest` as the control: the first passes, and the control fails with the meter's reason for
that environment in its output, so the environment does turn the meter away from the Claude
transcript and the root conftest is what keeps it out. Each
child starts from this process's environment with every selection variable removed, so the case
alone decides what is set, under either runner.
"""
# test-census-subject: conftest.py
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from lib import token_meters  # noqa: E402

REPO = HERE.parents[4]
SCRIPTS = Path(".claude") / "skills" / "sdlc-studio" / "scripts"
#: A module that reads a Claude transcript fixture through `run_state.session_tokens`.
MODULE = str(SCRIPTS / "tests" / "test_lean_transcript_dir.py")
#: A signal only the fixture's stub reader declares, so no fixed list of variables names it.
LATER = "BG1197_LATER_SIGNAL"

#: A fixture's own Cursor reader, declaring `LATER` as a further signal.
STUB_READER = f'''\
SIGNALS = ("{LATER}",)


def read(repo_root, env):
    return {{"tokens": None, "reason": "the stub cursor reader"}}
'''

#: Run under the fixture's copy of the root conftest. `tearDownModule` runs after the last
#: test's fixtures are torn down, so it records what the session's environment holds again.
PROBE = f'''\
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent / "{SCRIPTS.as_posix()}"))
from lib import token_meters


def tearDownModule():
    Path(os.environ["BG1197_AFTER"]).write_text(os.environ.get("{LATER}", "unset"))


class Probe(unittest.TestCase):
    def test_the_meter_reads_claude(self):
        got = token_meters.select(Path.cwd(), None)
        self.assertEqual("claude", got["harness"], got)

    def test_a_signal_the_test_sets_is_kept(self):
        with mock.patch.dict(os.environ, {{"CURSOR_AGENT": "1"}}):
            self.assertEqual("cursor", token_meters.select(Path.cwd(), None)["harness"])
'''


def pytest_run(args: list[str], cwd: Path, env: dict) -> tuple[int, str]:
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *args],
                          cwd=cwd, env=env, capture_output=True, text=True, timeout=300)
    return proc.returncode, proc.stdout + proc.stderr


def harness_free(**extra: str) -> dict:
    """This process's environment with no selection variable and no `LATER`, then `extra`."""
    names = {*token_meters.selection_variables(), LATER}
    return {**{k: v for k, v in os.environ.items() if k not in names}, **extra}


class HarnessEnvironmentTests(unittest.TestCase):

    def assert_scrubbed(self, env: dict, chose: str) -> None:
        code, out = pytest_run([MODULE], REPO, env)
        self.assertEqual(0, code, out)
        code, out = pytest_run(["--noconftest", MODULE], REPO, env)
        self.assertNotEqual(0, code, "the control passed, so this environment chooses no other "
                                     f"reader for {MODULE}:\n{out}")
        self.assertIn(chose, out)

    def test_a_harness_named_outright_is_cleared(self) -> None:
        """AC2. `SDLC_STUDIO_HARNESS=cursor`, with `CLAUDECODE` unset. MUTANT: the scrub leaves
        `HARNESS_ENV` out (the run selects the Cursor reader and fails)."""
        self.assert_scrubbed(harness_free(SDLC_STUDIO_HARNESS="cursor"), "the cursor reader")

    def test_copilot_beside_claude_is_cleared(self) -> None:
        """AC2. `COPILOT_HOME` beside `CLAUDECODE=1`. MUTANT: the scrub leaves `COPILOT_HOME`
        (two harnesses signalled, so no reading is taken)."""
        with tempfile.TemporaryDirectory() as home:
            env = harness_free(CLAUDECODE="1", COPILOT_HOME=home)
            self.assert_scrubbed(env, "copilot (COPILOT_HOME)")

    def test_opencodes_database_signal_is_cleared(self) -> None:
        """AC2. `OPENCODE_DB`, with `CLAUDECODE` unset. MUTANT: the scrub leaves a harness's
        second signal, `OPENCODE_DB`, beside its first, `OPENCODE`."""
        with tempfile.TemporaryDirectory() as d:
            env = harness_free(OPENCODE_DB=str(Path(d) / "opencode.db"))
            self.assert_scrubbed(env, "the environment (OPENCODE_DB)")

    def test_a_signal_a_reader_adds_later_is_cleared(self) -> None:
        """AC1. A fixture holding the root conftest and pytest.ini, the real `lib/token_meters.py`,
        and a Cursor reader declaring `LATER`, a signal no list names. With `LATER` and
        `CLAUDECODE` set, the probe reads Claude, a signal the test sets itself chooses Cursor
        alone, and the session holds `LATER` again after the test; the `--noconftest` control
        names Cursor. MUTANTS: the scrub is a fixed list of today's variables (the probe reads
        Cursor); it leaves Claude's own signal (the test's signal makes two); it pops without
        putting back, or scrubs once for the session (either way `unset` after)."""
        with tempfile.TemporaryDirectory() as d:
            fixture = Path(d)
            for name in ("pytest.ini", "conftest.py"):
                shutil.copy2(REPO / name, fixture / name)
            lib = fixture / SCRIPTS / "lib"
            lib.mkdir(parents=True)
            for name in ("__init__.py", "token_meters.py"):
                shutil.copy2(REPO / SCRIPTS / "lib" / name, lib / name)
            (lib / "meter_cursor.py").write_text(STUB_READER, encoding="utf-8")
            (fixture / "test_probe.py").write_text(PROBE, encoding="utf-8")
            after = fixture / "after.txt"
            env = harness_free(**{LATER: "1", "CLAUDECODE": "1", "BG1197_AFTER": str(after)})
            code, out = pytest_run(["test_probe.py"], fixture, env)
            self.assertEqual(0, code, out)
            self.assertIn("2 passed", out)
            self.assertEqual("1", after.read_text(encoding="utf-8"),
                             "the scrub did not put back the variable it cleared")
            code, out = pytest_run(["--noconftest", "test_probe.py"], fixture, env)
            self.assertNotEqual(0, code, out)
            self.assertIn("FAILED test_probe.py::Probe::test_the_meter_reads_claude", out)
            self.assertIn("'cursor'", out)


if __name__ == "__main__":
    unittest.main()
