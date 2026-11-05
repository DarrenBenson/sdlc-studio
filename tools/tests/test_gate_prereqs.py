"""US1003: `tools/enable-hooks.sh` names every missing gate prerequisite, with what breaks
without it and an install route that works on the interpreter that lacks it.

Each test runs the real `enable-hooks.sh` (or the checker it calls) in a throwaway clone that
carries the checker and its own `requirements-dev.txt`, with the clone's git config isolated from
this machine's. What is installed is decided by the test, not the machine: each distribution
the test needs is a `*.dist-info` it writes first on PYTHONPATH, at the version it chooses, and
the interpreter's facts (what it can import, whether it is a virtual environment, externally
managed, or has pip) are shimmed through a `sitecustomize` on PYTHONPATH.

MUTANTS, each failing a test here: the checker's non-zero exit aborting setup before the
keepalive block, a presence-only check that ignores the floor, a floor met at exactly its value
read as too old, or a list held in the checker instead of read from requirements-dev.txt (AC1);
one generic consequence for every gap, or an unlisted distribution not treated as refusing (AC2);
a fixed `pip install` line whatever the interpreter, the interpreter's path, the OS package or
the PATH step left out of the managed route, a virtual environment read as not one, or pip
assumed present (AC3); only Python packages checked, the tools' consequences confused, or a
present but non-executable node_modules markdownlint counted (AC4); a package looked up by its
import name (AC5); SDLC_COVERAGE_PYTHON ignored, resolved onto this interpreter, given this
interpreter's route, or crashing when it names nothing; a specifier other than `>=` silently
dropped; the checker's exit status on a gap.
"""
# test-census-subject: tools/gate_prereqs.py
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

#: The git locations the enabling script's environment is scrubbed of, as every hook fixture's.
_GIT_ENV_VARS = (
    "GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_INDEX_VERSION",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE",
    "GIT_CEILING_DIRECTORIES", "GIT_DISCOVERY_ACROSS_FILESYSTEM", "GIT_PREFIX",
)

#: Every distribution a complete environment declares, at versions that meet the shipped floors.
COMPLETE = {"PyYAML": "6.0.2", "pytest": "8.3.0", "pytest-xdist": "3.6.0", "coverage": "7.10.0"}

HIDE = textwrap.dedent('''
    import importlib.metadata as _m
    _HIDDEN = {hidden!r}
    _version = _m.version
    def version(name):
        if name.lower() in _HIDDEN:
            raise _m.PackageNotFoundError(name)
        return _version(name)
    _m.version = version
''')

INTERPRETER = textwrap.dedent('''
    import importlib.util, sys, sysconfig
    if {venv!r}:
        sys.base_prefix = "/nonexistent-base-interpreter"     # a virtual environment
    else:
        sys.base_prefix = sys.prefix                          # not one
    _get_path = sysconfig.get_path
    def get_path(name, *a, **k):
        return {stdlib!r} if name == "stdlib" else _get_path(name, *a, **k)
    sysconfig.get_path = get_path
    _find = importlib.util.find_spec
    def find_spec(name, *a, **k):
        if name == "pip":
            return _find("json") if {has_pip!r} else None
        return _find(name, *a, **k)
    importlib.util.find_spec = find_spec
''')

OLD_PYTHON = "import sys\nsys.version_info = (3, 9, 18, 'final', 0)\n"


class _Fixture(unittest.TestCase):
    def _tmp(self, prefix: str) -> Path:
        d = Path(tempfile.mkdtemp(prefix=prefix))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def _clone(self, requirements: str) -> Path:
        tmp = self._tmp("prereqs_")
        subprocess.run(["git", "init", "-q", "-b", "main", str(tmp)], check=True,
                       capture_output=True, env=self._env())
        (tmp / ".githooks").mkdir()
        (tmp / ".githooks" / "pre-push").write_text("#!/usr/bin/env bash\n# a hook\n",
                                                    encoding="utf-8")
        (tmp / "tools").mkdir()
        for name in ("enable-hooks.sh", "gate_prereqs.py"):
            shutil.copy(REPO / "tools" / name, tmp / "tools" / name)
        (tmp / "requirements-dev.txt").write_text(requirements, encoding="utf-8")
        return tmp

    def _env(self, **extra: str) -> dict:
        env = {k: v for k, v in os.environ.items() if k not in _GIT_ENV_VARS}
        env.pop("SDLC_COVERAGE_PYTHON", None)
        env.update({"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"})
        env.update(extra)
        return env

    def _shim(self, source: str) -> str:
        d = self._tmp("prereqs_shim_")
        (d / "sitecustomize.py").write_text(source, encoding="utf-8")
        return str(d)

    def _dists(self, **versions: str) -> str:
        """A directory of `*.dist-info` records, one per distribution at the version given."""
        d = self._tmp("prereqs_dists_")
        for name, version in versions.items():
            info = d / f"{name.replace('-', '_')}-{version}.dist-info"
            info.mkdir()
            (info / "METADATA").write_text(
                f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n", encoding="utf-8")
        return str(d)

    def _stub_path(self, *present: str) -> str:
        """A PATH holding what enable-hooks.sh itself needs, `python3` as the interpreter running
        these tests, and a stub for each of `present` - nothing else."""
        d = self._tmp("prereqs_path_")
        for tool in ("git", "bash", "sed", "basename"):
            real = shutil.which(tool)
            assert real, tool
            (d / tool).symlink_to(real)
        (d / "python3").write_text(f'#!/bin/sh\nexec "{sys.executable}" "$@"\n', encoding="utf-8")
        (d / "python3").chmod(0o755)
        for tool in present:
            (d / tool).write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            (d / tool).chmod(0o755)
        return str(d)

    def _run(self, clone: Path, *, path: tuple[str, ...] = ("markdownlint", "rg", "gh"),
             pythonpath: tuple[str, ...] = (), **extra: str) -> str:
        env = self._env(PATH=self._stub_path(*path), **extra)
        if pythonpath:
            env["PYTHONPATH"] = os.pathsep.join(pythonpath)
        r = subprocess.run(["bash", "tools/enable-hooks.sh"], cwd=clone, capture_output=True,
                           text=True, timeout=120, env=env)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        return r.stdout + r.stderr

    @staticmethod
    def _line(out: str, starts: str) -> str:
        return next((ln.strip() for ln in out.splitlines() if ln.strip().startswith(starts)), "")


class EnableHooksPrerequisiteTests(_Fixture):
    def test_a_missing_or_too_old_prerequisite_is_named_and_setup_completes(self) -> None:
        clone = self._clone("zzq-absent-dist>=1\ncoverage>=999\npytest>=8.3.0\npluggy>=1.5\n")
        out = self._run(clone, pythonpath=(self._dists(coverage="7.10.0", pytest="8.3",
                                                       pluggy="1.5.0"),))
        self.assertIn("zzq-absent-dist is missing - the push suite goes red without it", out,
                      "an unlisted distribution is not treated as refusing the push")
        self.assertIn("coverage 7.10.0 is too old: 999 or later is needed", out)
        self.assertNotIn("pytest 8.3 is too old", out, "8.3 read as older than a floor of 8.3.0")
        self.assertNotIn("pluggy 1.5.0 is too old", out, "a version AT its floor read as too old")
        got = subprocess.run(["git", "-C", str(clone), "config", "--get", "core.hooksPath"],
                             capture_output=True, text=True, env=self._env()).stdout.strip()
        self.assertEqual(".githooks", got)
        self.assertRegex(out, r"(Set|Left) core\.sshCommand", "setup stopped before the keepalive")

    def test_a_suite_prerequisite_is_named_with_the_consequence_of_its_absence(self) -> None:
        clone = self._clone("coverage>=7.10\npytest-xdist\nPyYAML\n")
        out = self._run(clone, pythonpath=(
            self._shim(HIDE.format(hidden=("coverage", "pytest-xdist", "pyyaml"))),))
        for name, consequence in (("coverage", "the push suite goes red without it"),
                                  ("PyYAML", "the push suite goes red without it"),
                                  ("pytest-xdist", "runs serially")):
            with self.subTest(dist=name):
                self.assertIn(consequence, self._line(out, f"{name} is missing"), out)
        self.assertNotIn("goes red", self._line(out, "pytest-xdist is missing"),
                         "every gap was given one consequence")

    def test_the_install_route_is_read_from_the_interpreter(self) -> None:
        clone = self._clone("zzq-absent-dist\n")
        managed = self._tmp("prereqs_stdlib_")
        (managed / "EXTERNALLY-MANAGED").write_text("[externally-managed]\n", encoding="utf-8")
        plain = self._tmp("prereqs_stdlib_")
        pip_route = "python3 -m pip install -r requirements-dev.txt"

        def route(stdlib: Path, venv: bool, has_pip: bool) -> str:
            out = self._run(clone, pythonpath=(self._shim(INTERPRETER.format(
                stdlib=str(stdlib), venv=venv, has_pip=has_pip)),))
            return self._line(out, "zzq-absent-dist is missing")

        line = route(managed, venv=False, has_pip=False)
        with self.subTest(interpreter="externally managed, no pip"):
            self.assertIn(f"{sys.executable} is externally managed", line)
            self.assertIn("install the OS packages", line)
            self.assertIn("python3 -m venv .venv", line)
            self.assertIn('export PATH="$PWD/.venv/bin:$PATH"', line)
            self.assertNotIn(pip_route, line)
        with self.subTest(interpreter="unmanaged, pip importable"):
            self.assertIn(pip_route, route(plain, venv=False, has_pip=True))
        with self.subTest(interpreter="unmanaged, no pip"):
            line = route(plain, venv=False, has_pip=False)
            self.assertIn(f"{sys.executable} has no pip", line)
            self.assertNotIn(pip_route, line)
        with self.subTest(interpreter="a virtual environment on a managed base, with pip"):
            line = route(managed, venv=True, has_pip=True)
            self.assertIn(pip_route, line)
            self.assertNotIn("externally managed", line)
        with self.subTest(interpreter="a virtual environment with no pip"):
            line = route(plain, venv=True, has_pip=False)
            self.assertIn("is a virtual environment with no pip", line)
            self.assertNotIn(pip_route, line)

    def test_missing_tools_outside_python_are_named_with_their_consequence(self) -> None:
        clone = self._clone("")
        out = self._run(clone, path=())
        for name, consequence, route in (
                ("markdownlint",
                 "the commit's markdown lanes skip it, and CI enforces them after the push",
                 "npm ci"),
                ("rg", "the tests that need ripgrep skip", "ripgrep"),
                ("gh", "the red-CI read before a push reads UNREAD", "cli.github.com")):
            line = self._line(out, f"{name} is not found")
            with self.subTest(tool=name):
                self.assertIn(consequence, line, out)
                self.assertIn(route, line, out)
        local = clone / "node_modules" / ".bin" / "markdownlint"
        local.parent.mkdir(parents=True)
        local.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        self.assertIn("markdownlint is not found", self._run(clone, path=()),
                      "a node_modules markdownlint that cannot run cleared the gap")
        local.chmod(0o755)
        self.assertNotIn("markdownlint is not found", self._run(clone, path=()),
                         "`npm ci`'s own markdownlint does not clear the gap it is offered for")

    def test_a_complete_environment_reports_nothing_missing(self) -> None:
        # Distribution names that differ from their import names (PyYAML is `yaml`,
        # pytest-xdist is `xdist`): a lookup by import name reads them missing.
        clone = self._clone("PyYAML\npytest-xdist\npytest\ncoverage>=7.10\n")
        out = self._run(clone, pythonpath=(self._dists(**COMPLETE),))
        self.assertIn("gate prerequisites: every one present", out)
        self.assertNotIn("missing", out)
        self.assertNotIn("not found", out)


class CheckerEdgeTests(_Fixture):
    """Behaviour the checker states that no criterion above reaches."""

    def _check(self, clone: Path, **extra: str) -> subprocess.CompletedProcess:
        env = self._env(PATH=self._stub_path("markdownlint", "rg", "gh"), **extra)
        return subprocess.run(["python3", "tools/gate_prereqs.py", "check"], cwd=clone,
                              capture_output=True, text=True, timeout=120, env=env)

    def _venv_without_coverage(self) -> str:
        venv = self._tmp("prereqs_venv_") / "venv"
        subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(venv)], check=True,
                       capture_output=True, timeout=120)
        return str(venv / "bin" / "python3")

    def test_sdlc_coverage_python_is_checked_on_that_interpreter(self) -> None:
        clone = self._clone("coverage>=7.10\n")
        other = self._venv_without_coverage()
        # No fake distributions on PYTHONPATH here: the override's subprocess would inherit them.
        r = self._check(clone, SDLC_COVERAGE_PYTHON=other)
        line = self._line(r.stdout, "coverage is missing")
        self.assertIn(f"coverage is missing on {other}", line, r.stdout + r.stderr)
        self.assertIn(f"{other} -m pip install 'coverage>=7.10'", line,
                      "the gap on the other interpreter was given this one's route")

    def test_sdlc_coverage_python_that_cannot_run_is_named(self) -> None:
        clone = self._clone("coverage>=7.10\nzzq-absent-dist\n")
        r = self._check(clone, SDLC_COVERAGE_PYTHON="/nonexistent/python3")
        self.assertNotIn("Traceback", r.stderr, r.stderr)
        self.assertIn("SDLC_COVERAGE_PYTHON names /nonexistent/python3, which cannot run", r.stdout)
        self.assertIn("zzq-absent-dist is missing", r.stdout, "one bad override hid every gap")

    def test_every_floor_specifier_is_read_and_nothing_is_dropped(self) -> None:
        dists = self._dists(coverage="7.10.0", PyYAML="6.0.2", pytest="8.3.0")
        for line in ("coverage==999", "coverage~=999.0", "coverage>=999,<1000",
                     "PyYAML[libyaml]>=999", 'pytest>=999; python_version >= "3"'):
            with self.subTest(requirement=line):
                r = self._check(self._clone(line + "\n"), PYTHONPATH=dists)
                self.assertIn("is too old", r.stdout, r.stdout + r.stderr)
        r = self._check(self._clone("!!not a requirement\n"), PYTHONPATH=dists)
        self.assertIn("is not understood", r.stdout, "a line the checker cannot read was dropped")

    def test_the_check_exits_one_on_a_gap_and_zero_without(self) -> None:
        dists = self._dists(**COMPLETE)
        self.assertEqual(1, self._check(self._clone("zzq-absent-dist\n"),
                                        PYTHONPATH=dists).returncode)
        self.assertEqual(0, self._check(self._clone("pytest\n"), PYTHONPATH=dists).returncode)

    def test_an_interpreter_below_the_floor_is_named(self) -> None:
        r = self._check(self._clone(""), PYTHONPATH=self._shim(OLD_PYTHON))
        self.assertIn("is older than 3.10", r.stdout, r.stdout + r.stderr)


class HostScopeTests(_Fixture):
    """BG1138: gh is the pusher's (the red-CI read runs in the local pre-push hook), so a check
    run on a gate host leaves it out, and the local check still names it.

    MUTANTS, each failing a test here: remote-gate.sh's preflight run without `--host` (AC1);
    the host doctor reading the list without the host scope; `--host` ignored by the checker;
    `--host` dropping every tool, not only gh; `--host` hiding a gap that refuses the push; gh
    left out of the local check too, or counted as refusing there (AC2)."""

    def _check(self, clone: Path, *flags: str, present: tuple[str, ...]) -> subprocess.CompletedProcess:
        env = self._env(PATH=self._stub_path(*present))
        return subprocess.run(["python3", "tools/gate_prereqs.py", "check", *flags], cwd=clone,
                              capture_output=True, text=True, timeout=120, env=env)

    @staticmethod
    def _path_without(root: Path, *names: str) -> str:
        """One directory linking the first executable of each name on this PATH, less `names`."""
        d = root / "path-without"
        d.mkdir()
        for directory in os.environ.get("PATH", "/usr/bin:/bin").split(os.pathsep):
            if not os.path.isdir(directory):
                continue
            for entry in os.scandir(directory):
                link = d / entry.name
                if entry.name in names or os.path.lexists(link):
                    continue
                if entry.is_file() and os.access(entry.path, os.X_OK):
                    link.symlink_to(entry.path)
        return str(d)

    def test_a_host_check_leaves_out_gh_and_nothing_else(self) -> None:
        clone = self._clone("")
        r = self._check(clone, "--refusing", "--host", present=("markdownlint",))
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertNotIn("gh is not found", r.stdout, "a host check named the pusher's gh")
        self.assertIn("note: rg is not found", r.stdout, "the host scope dropped every tool")
        r = self._check(clone, "--host", present=("markdownlint", "rg"))
        self.assertEqual((0, "gate prerequisites: every one present"),
                         (r.returncode, r.stdout.strip()), "a host lacking only gh has a gap")
        r = self._check(self._clone("zzq-absent-dist\n"), "--refusing", "--host",
                        present=("markdownlint", "rg"))
        self.assertEqual(1, r.returncode, "the host scope hid a gap that refuses the push")
        self.assertIn("REFUSES: zzq-absent-dist is missing", r.stdout)

    def test_the_local_check_still_names_a_missing_gh(self) -> None:
        """AC2."""
        clone = self._clone("")
        r = self._check(clone, "--refusing", present=("markdownlint", "rg"))
        self.assertEqual(0, r.returncode, "a missing gh refused the push: " + r.stdout)
        self.assertIn("note: gh is not found - the red-CI read before a push reads UNREAD",
                      r.stdout)
        r = self._check(clone, present=("markdownlint", "rg"))
        self.assertEqual(1, r.returncode, r.stdout)
        self.assertIn("gh is not found - the red-CI read before a push reads UNREAD. Install: "
                      "https://cli.github.com", r.stdout)

    def test_the_gate_hosts_preflight_and_doctor_leave_gh_out(self) -> None:
        """AC1: a real push judged on a fixture host whose PATH has neither gh nor rg; the rg
        note shows that the host's preflight ran and printed its notes."""
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from test_remote_gate_doctor import _DoctorClone  # noqa: PLC0415 - its fixture, not its tests
        fx = _DoctorClone()
        self.addCleanup(fx.cleanup)
        host = os.pathsep.join([fx.host().split(os.pathsep)[0],
                                self._path_without(fx.tmp, "gh", "rg")])
        self.assertIsNone(shutil.which("gh", path=host), "the fixture host has a gh")
        r = fx.push(host_path=host)
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn("note: rg is not found", r.stderr, "the host's preflight printed no notes")
        self.assertNotIn("gh is not found", r.stderr, "the host's preflight named the pusher's gh")
        r = fx.doctor(fx.host(lacking=("_",)))
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn("note: rg is not found", r.stderr, "the host doctor printed no notes")
        self.assertNotIn("gh is not found", r.stderr, "the host doctor named the pusher's gh")


class ReleaseScopeTests(_Fixture):
    """BG1220: the release gate's criteria run Python 3.10 and pdftotext, so the release route's
    preflight names each one missing and refuses before the gate starts.

    MUTANTS, each failing a test here: `--release` ignored by the checker; a missing release
    prerequisite printed as a note, not refusing; only the first missing one named; a
    `python3.10` trusted by its name, not asked its version; `uv python find` not consulted; the
    release prerequisites added to the push's scope too (AC1, the checker); remote-gate.sh's
    release preflight run without `--release`, or every route's preflight run with it; the
    preflight run after the release gate rather than before it (AC1, the route)."""

    _RELEASE = "the release gate reads red without it"

    def _check(self, clone: Path, *flags: str, path: str) -> subprocess.CompletedProcess:
        return subprocess.run(["python3", "tools/gate_prereqs.py", "check", *flags], cwd=clone,
                              capture_output=True, text=True, timeout=120,
                              env=self._env(PATH=path))

    @staticmethod
    def _python(at: Path, version: str) -> Path:
        """A stand-in interpreter that answers the version probe with `version` ("3 10")."""
        at.write_text(f"#!/bin/sh\necho {version}\n", encoding="utf-8")
        at.chmod(0o755)
        return at

    def _release_path(self, *, floor: str = "", uv: str = "", pdftotext: bool = False) -> str:
        """`_stub_path` with markdownlint and rg, plus a `python3.10` answering `floor`, a `uv`
        whose `python find --no-project 3.10` prints a Python answering `uv`, and a pdftotext."""
        d = Path(self._stub_path("markdownlint", "rg", *(("pdftotext",) if pdftotext else ())))
        if floor:
            self._python(d / "python3.10", floor)
        if uv:
            found = self._python(self._tmp("prereqs_uv_") / "python", uv)
            (d / "uv").write_text(
                '#!/bin/sh\n[ "$*" = "python find --no-project 3.10" ] || exit 2\n'
                f"echo {found}\n", encoding="utf-8")
            (d / "uv").chmod(0o755)
        return str(d)

    def test_the_release_check_names_each_missing_release_prerequisite_and_refuses(self) -> None:
        clone = self._clone("")
        r = self._check(clone, "--refusing", "--host", "--release", path=self._release_path())
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn("REFUSES: Python 3.10 is not found (no python3.10 on PATH, and `uv python "
                      f"find 3.10` finds none) - {self._RELEASE}: the criteria that compile and "
                      "start every shipped script at the 3.10 floor cannot run. Install: uv python "
                      "install 3.10", r.stdout)
        self.assertIn(f"REFUSES: pdftotext is not found - {self._RELEASE}: the criterion that "
                      "reads docs/whitepaper.pdf cannot run. Install: the package `poppler-utils`",
                      r.stdout)
        for present, absent in (("pdftotext", "Python 3.10"), ("Python 3.10", "pdftotext")):
            with self.subTest(present=present):
                path = self._release_path(floor="3 10" if present == "Python 3.10" else "",
                                          pdftotext=present == "pdftotext")
                r = self._check(clone, "--refusing", "--host", "--release", path=path)
                self.assertEqual(1, r.returncode, r.stdout)
                self.assertIn(f"REFUSES: {absent} is not found", r.stdout)
                self.assertNotIn(f"{present} is not found", r.stdout, "a present one was named")
        r = self._check(clone, "--host", "--release", path=self._release_path(floor="3 10", pdftotext=True))
        self.assertEqual((0, "gate prerequisites: every one present"),
                         (r.returncode, r.stdout.strip()), r.stderr)

    def test_python_3_10_is_asked_its_version_and_looked_for_through_uv(self) -> None:
        clone = self._clone("")
        r = self._check(clone, "--host", "--release", path=self._release_path(floor="3 12", pdftotext=True))
        self.assertIn("Python 3.10 is not found", r.stdout, "a python3.10 that is 3.12 counted")
        r = self._check(clone, "--host", "--release", path=self._release_path(uv="3 10", pdftotext=True))
        self.assertEqual(0, r.returncode, "the 3.10 `uv python find` names was not found: "
                         + r.stdout + r.stderr)
        r = self._check(clone, "--host", "--release", path=self._release_path(uv="3 11", pdftotext=True))
        self.assertIn("Python 3.10 is not found", r.stdout, "uv's 3.11 counted as 3.10")

    def test_the_push_scope_is_unchanged(self) -> None:
        r = self._check(self._clone(""), "--refusing", "--host", path=self._release_path())
        self.assertEqual((0, "gate prerequisites: every one present"),
                         (r.returncode, r.stdout.strip()), "the push's check gained the release's")

    def test_the_release_route_refuses_before_the_gate_starts(self) -> None:
        """AC1 through the shipped route: `remote-gate.sh push --release` on a fixture host whose
        PATH has no python3.10, uv or pdftotext, then the same host given both."""
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from test_remote_gate_doctor import _DoctorClone  # noqa: PLC0415 - its fixture, not its tests
        fx = _DoctorClone()
        self.addCleanup(fx.cleanup)
        sha = fx.commit("a release the stub gate refuses", verdict="1\n")
        bare = os.pathsep.join([fx.host().split(os.pathsep)[0],
                                HostScopeTests._path_without(fx.tmp, "python3.10", "uv", "pdftotext")])

        def release(host: str) -> subprocess.CompletedProcess:
            return subprocess.run(["bash", "tools/remote-gate.sh", "push", "--commit", sha,
                                   "--release"], cwd=fx.clone, env=fx.env(host),
                                  capture_output=True, text=True, timeout=300)

        r = release(bare)
        self.assertEqual(4, r.returncode, r.stderr)
        self.assertIn("REFUSES: Python 3.10 is not found", r.stderr)
        self.assertIn("REFUSES: pdftotext is not found", r.stderr)
        self.assertIn("refused before the release gate runs", r.stderr)
        self.assertEqual([], fx.gate_runs(), "the release gate started before its preflight refused")
        stubs = self._tmp("prereqs_release_host_")
        self._python(stubs / "python3.10", "3 10")
        self._python(stubs / "pdftotext", "")
        r = release(os.pathsep.join([str(stubs), bare]))
        self.assertEqual(1, r.returncode, r.stderr)
        for name in ("Python 3.10", "pdftotext"):
            self.assertNotIn(f"{name} is not found", r.stderr, r.stderr)
        self.assertEqual([["--release"]], [run["argv"] for run in fx.gate_runs()], r.stderr)
        r = fx.push(host_path=bare)
        for name in ("Python 3.10", "pdftotext"):
            self.assertNotIn(f"{name} is not found", r.stderr, "a push's preflight checked it")
        self.assertEqual(["--boundary", "push"], fx.gate_runs()[-1]["argv"], r.stderr)


if __name__ == "__main__":
    unittest.main()
