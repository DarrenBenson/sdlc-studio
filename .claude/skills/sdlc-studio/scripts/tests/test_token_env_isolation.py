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

BG1249: the same conftest gives the session a private home. `PrivateHomeTests` runs a probe under
a fixture's copy of it with `HOME`, every XDG base directory and each harness's home naming a
fake operator's home, which holds a store for each harness whose step-3 probe opens one. The
probe finds each moved under the session's private directory, and the `--noconftest` control
finds the operator's.
"""
# test-census-subject: conftest.py
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import site
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


#: The variables the session moves under its private directory, and the harness homes it unsets.
PRIVATE_VARS = ("HOME", "XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME")
HARNESS_HOMES = ("CODEX_HOME", "COPILOT_HOME", "CLAUDE_CONFIG_DIR", "OPENCODE_DB")
#: Every variable the session changes, so every one `pytest_unconfigure` puts back.
SESSION_VARS = (*PRIVATE_VARS, *HARNESS_HOMES, "PYTHONUSERBASE")

#: Run under the fixture's copy of the root conftest, with each of `SESSION_VARS` but the user
#: base naming the fake operator's home `BG1249_OPERATOR`. The audit hook records every path
#: the process opens or lists, so a step-3 probe that reaches the operator's store is seen.
HOME_PROBE = f"""\
import os
import pwd
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.path.insert(0, {str(REPO / SCRIPTS)!r})
from lib import meter_codex, meter_copilot, meter_opencode, token_meters

#: The fixture's fake operator home, and the real harness stores and config under the home the
#: passwd entry names, not `$HOME`. Not the passwd home itself: a run whose TMPDIR sits under it
#: (this repo commits with `$HOME/.cache/sdlc-tmp`) has its private directory there too.
_REAL = Path(pwd.getpwuid(os.getuid()).pw_dir).resolve()
OPERATORS = (Path(os.environ["BG1249_OPERATOR"]).resolve(),
             *(_REAL / rel for rel in (".codex", ".copilot", ".local/share/opencode", ".claude",
                                       ".config")))
PRIVATE = Path(os.environ.get("SDLC_TEST_TMPDIR") or "/no-private-directory").resolve()
#: Read at collection: after `pytest_configure`, before a test's fixture clears anything.
AT_COLLECTION = {{name: os.environ.get(name) for name in {HARNESS_HOMES!r}}}
TOUCHED = []


def _path(arg):
    if isinstance(arg, (bytes, os.PathLike)):
        arg = os.fsdecode(arg)
    if not isinstance(arg, str):
        return None
    return unquote(urlsplit(arg).path) if arg.startswith("file:") else arg


def _record(event, args):
    if event in ("open", "os.listdir", "os.scandir", "sqlite3.connect") and args:
        path = _path(args[0])
        if path:
            TOUCHED.append(path)


sys.addaudithook(_record)


def inside(path, root):
    path = Path(path).resolve()
    return path == root or root in path.parents


class Probe(unittest.TestCase):
    def assert_private(self, what, path):
        for home in OPERATORS:
            self.assertFalse(inside(path, home), f"{{what}} is under the operator's home: {{path}}")
        self.assertTrue(inside(path, PRIVATE), f"{{what}} is outside the private directory: {{path}}")

    def test_home(self):
        Path(os.environ["BG1249_WORKER"]).write_text(os.environ.get("PYTEST_XDIST_WORKER", "main"))
        for name in {PRIVATE_VARS!r}:
            self.assertTrue(os.environ.get(name), name + " is unset")
            self.assert_private(name, os.environ[name])
        self.assert_private("Path.home()", Path.home())
        self.assertEqual(dict.fromkeys(AT_COLLECTION), AT_COLLECTION, "a harness home is set")

    def test_user_base(self):
        want = os.environ["BG1249_USER_BASE"]
        self.assertEqual(want, os.environ.get("PYTHONUSERBASE"))
        got = subprocess.run([sys.executable, "-c", "import site; print(site.getuserbase())"],
                             env=dict(os.environ), capture_output=True, text=True, check=True)
        self.assertEqual(want, got.stdout.strip(), "a child Python lost the operator's user base")

    def test_step_three(self):
        del TOUCHED[:]
        got = token_meters.select(Path.cwd(), None)
        for where in (meter_codex.codex_home(os.environ), meter_copilot.copilot_home(os.environ),
                      meter_opencode.data_dir(os.environ)):
            self.assert_private("a harness store", where)
        self.assertEqual([], [p for p in TOUCHED if any(inside(p, h) for h in OPERATORS)])
        self.assertEqual("claude", got["harness"], got)

    def test_commit(self):
        # The point is the identity the session's HOME gives git, so this env is the session's
        # own, not gitutil.git_env(), whose fixed identity and null global config would hide it.
        env = dict(os.environ)
        repo = tempfile.mkdtemp()
        for argv in (["git", "init", "-q"], ["git", "commit", "-q", "--allow-empty", "-m", "probe"]):
            got = subprocess.run(argv, env=env, cwd=repo, capture_output=True, text=True)
            self.assertEqual(0, got.returncode, "the commit was refused: " + got.stderr)
        author = subprocess.run(["git", "log", "-1", "--format=%ae"], env=env, cwd=repo,
                                capture_output=True, text=True, check=True).stdout.strip()
        for scope, key, want in (["--global"], "user.email", author), ([], "maintenance.auto", "false"):
            got = subprocess.run(["git", "config", *scope, "--get", key], env=env, cwd=repo,
                                 capture_output=True, text=True)
            self.assertEqual(want, got.stdout.strip(), key + " is not the session's")
"""

#: Loaded with `-p`; `trylast` runs it after the conftest's `pytest_unconfigure`.
AFTER_PLUGIN = """\
import json
import os
from pathlib import Path

import pytest


@pytest.hookimpl(trylast=True)
def pytest_unconfigure(config):
    names = json.loads(os.environ["BG1249_NAMES"])
    Path(os.environ["BG1249_AFTER"]).write_text(json.dumps({n: os.environ.get(n) for n in names}))
"""


def user_site_of(home: Path) -> tuple[str, str]:
    """The user base and user site a Python started with `HOME=home` and no `PYTHONUSERBASE`
    derives, asked of this interpreter."""
    env = {k: v for k, v in os.environ.items() if k != "PYTHONUSERBASE"}
    env["HOME"] = str(home)
    got = subprocess.run([sys.executable, "-c", "import site; print(site.getuserbase()); "
                          "print(site.getusersitepackages())"],
                         env=env, capture_output=True, text=True, check=True)
    base, user_site = got.stdout.splitlines()
    return base, user_site


class PrivateHomeTests(unittest.TestCase):
    """BG1249: a pytest session from this repository opens no store in the operator's home, and
    puts the operator's environment back when it ends."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.fixture, op = root / "fixture", root / "operator"
        self.fixture.mkdir()
        for name in ("pytest.ini", "conftest.py"):
            shutil.copy2(REPO / name, self.fixture / name)
        (self.fixture / "test_bg1249.py").write_text(HOME_PROBE, encoding="utf-8")
        (self.fixture / "bg1249_after.py").write_text(AFTER_PLUGIN, encoding="utf-8")
        for store in (op / ".codex" / "state_5.sqlite",
                      op / ".local" / "share" / "opencode" / "opencode.db"):
            store.parent.mkdir(parents=True)
            store.write_bytes(b"")
        (op / ".copilot" / "session-state").mkdir(parents=True)
        base, user_site = user_site_of(op)
        if site.ENABLE_USER_SITE:
            # The fake home's user site loads this interpreter's, so a child started with no
            # PYTHONUSERBASE still finds pytest where a base interpreter keeps it (BG0978).
            Path(user_site).mkdir(parents=True, exist_ok=True)
            (Path(user_site) / "bg1249-operator-site.pth").write_text(
                f"import site; site.addsitedir({site.getusersitepackages()!r})\n", encoding="utf-8")
        self.after, self.worker = root / "after.json", root / "worker.txt"
        # Every GIT_ variable goes, so no inherited one sets the child's identity or git config,
        # and every PYTEST_ one, so an outer xdist worker's PYTEST_XDIST_WORKER does not name
        # the child's main process as a worker.
        drop = {"SDLC_TEST_TMPDIR", "PYTHONUSERBASE", "EMAIL"}
        self.env = {k: v for k, v in harness_free().items()
                    if k not in drop and not k.startswith(("GIT_", "PYTEST_"))}
        self.env.update({
            "HOME": str(op), "XDG_DATA_HOME": str(op / ".local" / "share"),
            "XDG_CONFIG_HOME": str(op / ".config"), "XDG_STATE_HOME": str(op / ".local" / "state"),
            "XDG_CACHE_HOME": str(op / ".cache"), "CODEX_HOME": str(op / ".codex"),
            "COPILOT_HOME": str(op / ".copilot"), "CLAUDE_CONFIG_DIR": str(op / ".claude"),
            "OPENCODE_DB": str(op / ".local" / "share" / "opencode" / "opencode.db"),
            "BG1249_OPERATOR": str(op), "BG1249_USER_BASE": base,
            "BG1249_AFTER": str(self.after), "BG1249_NAMES": json.dumps(SESSION_VARS),
            "BG1249_WORKER": str(self.worker),
        })

    def probe(self, select: str, *args: str, conftest: bool = True) -> str:
        """Run the probe's tests `select` names; returns the output. Under the conftest the run
        exits 0; with `conftest=False` (the control) it exits non-zero."""
        control = [] if conftest else ["--noconftest"]
        code, out = pytest_run([*control, "-p", "bg1249_after", *args, "-k", select,
                                "test_bg1249.py"], self.fixture, self.env)
        (self.assertEqual if conftest else self.assertNotEqual)(0, code, out)
        return out

    def test_the_session_home_is_private(self) -> None:
        """AC1, in the main process and in an xdist worker; the control finds the operator's
        `HOME`. MUTANTS: one of `PRIVATE_VARS` left as the operator's; one of `HARNESS_HOMES`
        left set; no `PYTHONUSERBASE` pin (a child Python derives its user base from the private
        home)."""
        self.assertIn("HOME is under the operator's home", self.probe("test_home", conftest=False))
        self.assertIn("2 passed", self.probe("test_home or test_user_base"))
        self.assertEqual("main", self.worker.read_text(encoding="utf-8"))
        if importlib.util.find_spec("xdist") is None:
            self.skipTest("pytest-xdist is not installed, so no worker is probed")
        self.assertIn("2 passed", self.probe("test_home or test_user_base", "-n", "1"))
        self.assertEqual("gw0", self.worker.read_text(encoding="utf-8"))

    def test_a_step_three_probe_stays_private(self) -> None:
        """AC2: Codex's, Copilot's and OpenCode's store paths resolve in the private directory,
        and the probes open nothing under the fake operator's home or the harness stores under
        the passwd entry's home; the control resolves the operator's `~/.codex`. MUTANT: `CODEX_HOME` or `XDG_DATA_HOME`
        left as the operator's."""
        out = self.probe("test_step_three", conftest=False)
        self.assertIn(f"a harness store is under the operator's home: {self.env['CODEX_HOME']}", out)
        self.assertIn("1 passed", self.probe("test_step_three"))

    def test_a_fixture_commit_has_an_identity(self) -> None:
        """AC3: a repository with no identity of its own commits as the private home's
        `.gitconfig` names, under the maintenance pin. MUTANTS: no `.gitconfig` seeded; the
        maintenance pin dropped. The control is refused the commit, or, on a host whose name
        git can make an email of, commits as an identity no config names."""
        self.assertRegex(self.probe("test_commit", conftest=False),
                         "the commit was refused|user.email is not the session's")
        self.assertIn("1 passed", self.probe("test_commit"))

    def test_unconfigure_restores_what_it_changed(self) -> None:
        """AC3: after `pytest_unconfigure` each of `SESSION_VARS` holds what it held before the
        session, set or unset. MUTANT: `pytest_unconfigure` leaves the home moved."""
        self.probe("test_home")
        after = json.loads(self.after.read_text(encoding="utf-8"))
        self.assertEqual({name: self.env.get(name) for name in SESSION_VARS}, after,
                         "pytest_unconfigure did not put back the operator's environment")


if __name__ == "__main__":
    unittest.main()
