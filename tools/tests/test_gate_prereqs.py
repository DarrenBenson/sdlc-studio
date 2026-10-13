"""US1003: `tools/enable-hooks.sh` names every missing gate prerequisite, with what breaks
without it and an install route that works on the interpreter the hooks run.

Each test runs the real `enable-hooks.sh` in a throwaway clone that carries the checker and its
own `requirements-dev.txt`, with the clone's git config isolated from this machine's. A missing
or too-old distribution is declared rather than uninstalled, and the interpreter's facts (what it
can import, whether it is externally managed, whether pip exists) are shimmed through a
`sitecustomize` on PYTHONPATH, so no test depends on what this machine happens to have.

MUTANTS, one per test: the checker's non-zero exit aborting setup before the keepalive block, or a
presence-only check that ignores the floor, or a list held in the checker instead of read from
requirements-dev.txt (AC1); one generic consequence for every gap (AC2); a fixed `pip install`
line whatever the interpreter (AC3); only Python packages checked (AC4); a package looked up by
its import name, so a present distribution reads missing (AC5).
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
    sys.base_prefix = sys.prefix                     # not a virtual environment
    _get_path = sysconfig.get_path
    def get_path(name, *a, **k):
        return {stdlib!r} if name == "stdlib" else _get_path(name, *a, **k)
    sysconfig.get_path = get_path
    _find = importlib.util.find_spec
    def find_spec(name, *a, **k):
        if name == "pip" and {hide_pip!r}:
            return None
        return _find(name, *a, **k)
    importlib.util.find_spec = find_spec
''')


class EnableHooksPrerequisiteTests(unittest.TestCase):
    def _clone(self, requirements: str) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="prereqs_"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
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
        d = Path(tempfile.mkdtemp(prefix="prereqs_shim_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "sitecustomize.py").write_text(source, encoding="utf-8")
        return str(d)

    def _stub_path(self, *present: str) -> str:
        """A PATH holding what enable-hooks.sh itself needs, `python3` as the interpreter running
        these tests, and a stub for each of `present` - nothing else."""
        d = Path(tempfile.mkdtemp(prefix="prereqs_path_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
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

    def _run(self, clone: Path, **extra: str) -> subprocess.CompletedProcess:
        return subprocess.run(["bash", "tools/enable-hooks.sh"], cwd=clone, capture_output=True,
                              text=True, timeout=120, env=self._env(**extra))

    def test_a_missing_or_too_old_prerequisite_is_named_and_setup_completes(self) -> None:
        clone = self._clone("zzq-absent-dist>=1\ncoverage>=999\n")
        r = self._run(clone)
        out = r.stdout + r.stderr
        self.assertEqual(0, r.returncode, out)
        self.assertIn("zzq-absent-dist is missing", out)
        self.assertRegex(out, r"coverage [0-9][0-9.]* is too old: 999 or later is needed")
        got = subprocess.run(["git", "-C", str(clone), "config", "--get", "core.hooksPath"],
                             capture_output=True, text=True, env=self._env()).stdout.strip()
        self.assertEqual(".githooks", got)
        self.assertRegex(out, r"(Set|Left) core\.sshCommand", "setup stopped before the keepalive")

    def test_a_suite_prerequisite_is_named_with_the_consequence_of_its_absence(self) -> None:
        clone = self._clone("coverage>=7.10\npytest-xdist\n")
        r = self._run(clone, PYTHONPATH=self._shim(HIDE.format(hidden=("coverage", "pytest-xdist"))))
        lines = (r.stdout + r.stderr).splitlines()
        coverage = next((ln for ln in lines if "coverage is missing" in ln), "")
        xdist = next((ln for ln in lines if "pytest-xdist is missing" in ln), "")
        self.assertIn("the push suite goes red without it", coverage, lines)
        self.assertIn("runs serially", xdist, lines)
        self.assertNotIn("goes red", xdist, "every gap was given one consequence")

    def test_the_install_route_is_read_from_the_interpreter(self) -> None:
        clone = self._clone("zzq-absent-dist\n")
        managed = Path(tempfile.mkdtemp(prefix="prereqs_stdlib_"))
        self.addCleanup(shutil.rmtree, managed, ignore_errors=True)
        (managed / "EXTERNALLY-MANAGED").write_text("[externally-managed]\n", encoding="utf-8")
        plain = Path(tempfile.mkdtemp(prefix="prereqs_stdlib_"))
        self.addCleanup(shutil.rmtree, plain, ignore_errors=True)
        pip_route = "python3 -m pip install -r requirements-dev.txt"
        r = self._run(clone, PYTHONPATH=self._shim(
            INTERPRETER.format(stdlib=str(managed), hide_pip=True)))
        out = r.stdout + r.stderr
        self.assertIn("is externally managed", out, out)
        self.assertNotIn(pip_route, out, "a pip line was offered to an interpreter that refuses it")
        self.assertIn("python3 -m venv", out)
        with_pip = self._shim(INTERPRETER.format(stdlib=str(plain), hide_pip=False))
        (Path(with_pip) / "pip").mkdir()                   # an importable pip, stubbed
        (Path(with_pip) / "pip" / "__init__.py").write_text("", encoding="utf-8")
        r = self._run(clone, PYTHONPATH=with_pip)
        self.assertIn(pip_route, r.stdout + r.stderr)

    def test_missing_tools_outside_python_are_named_with_their_consequence(self) -> None:
        clone = self._clone("")
        r = self._run(clone, PATH=self._stub_path())
        lines = (r.stdout + r.stderr).splitlines()
        for name, consequence, route in (
                ("markdownlint", "markdown lanes skip", "npm ci"),
                ("rg", "skip", "ripgrep"),
                ("gh", "reads UNREAD", "cli.github.com")):
            line = next((ln for ln in lines if ln.strip().startswith(f"{name} is not found")), "")
            with self.subTest(tool=name):
                self.assertIn(consequence, line, lines)
                self.assertIn(route, line, lines)

    def test_a_complete_environment_reports_nothing_missing(self) -> None:
        # Distribution names that differ from their import names (PyYAML is `yaml`,
        # pytest-xdist is `xdist`): a lookup by import name reads them missing.
        clone = self._clone("PyYAML\npytest-xdist\npytest\n")
        r = self._run(clone, PATH=self._stub_path("markdownlint", "rg", "gh"))
        out = r.stdout + r.stderr
        self.assertEqual(0, r.returncode, out)
        self.assertIn("gate prerequisites: every one present", out)
        self.assertNotIn("missing", out)
        self.assertNotIn("not found", out)


if __name__ == "__main__":
    unittest.main()
