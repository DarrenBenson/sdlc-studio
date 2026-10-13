"""US1005: the pre-push hook refuses in seconds, before the suite, when the suite cannot be green
on this interpreter, and only then.

A missing coverage or PyYAML was found only by the suite's own red tests after a full run; a
missing pytest-xdist, rg, markdownlint or gh never makes the suite red. The hook now runs
`tools/gate_prereqs.py check --refusing` right after it decides the boundary: the first class
refuses the push, the second is named as a note and the push proceeds.

Each test drives the tracked hook through `test_pre_push_hook._Clone`, whose stub gate.py records
its argv, so "before the gate" is decided by the gate never being invoked, not by timing. What is
installed is the test's choice: distributions are `*.dist-info` records first on PYTHONPATH, and a
`sitecustomize` hides the ones a test needs missing.

MUTANTS: no preflight (AC1); the preflight on the branch path only (AC2); every gap refused, so
a machine without xdist cannot push (AC3); the check's exit read inverted, or any output read as
a refusal (AC4).
"""
# test-census-subject: .githooks/pre-push
from __future__ import annotations

import os
import shutil
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_pre_push_hook as hook  # noqa: E402 - the hook's fixture, shared

REPO = Path(__file__).resolve().parents[2]
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


class PushPrerequisiteTests(unittest.TestCase):
    def _tmp(self) -> Path:
        d = Path(tempfile.mkdtemp(prefix="prepush_prereqs_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def _clone(self) -> hook._Clone:
        fx = hook._Clone()
        self.addCleanup(fx.cleanup)
        shutil.copy(REPO / "tools" / "gate_prereqs.py", fx.clone / "tools" / "gate_prereqs.py")
        shutil.copy(REPO / "requirements-dev.txt", fx.clone / "requirements-dev.txt")
        hook._git(fx.clone, "add", "-A")
        hook._git(fx.clone, "commit", "-q", "-m", "the prerequisite check")
        return fx

    def _pythonpath(self, hidden: tuple[str, ...] = (), **dists: str) -> str:
        paths = []
        if hidden:
            shim = self._tmp()
            (shim / "sitecustomize.py").write_text(HIDE.format(hidden=hidden), encoding="utf-8")
            paths.append(str(shim))
        if dists:
            d = self._tmp()
            for name, version in dists.items():
                info = d / f"{name.replace('-', '_')}-{version}.dist-info"
                info.mkdir()
                (info / "METADATA").write_text(
                    f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n", encoding="utf-8")
            paths.append(str(d))
        return os.pathsep.join(paths)

    def _push(self, fx: hook._Clone, *refspec: str, pythonpath: str, tools: tuple[str, ...] = (),
              gh: bool = True):
        path = fx.stub_path()
        for tool in tools:
            (path / tool).write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            (path / tool).chmod(0o755)
        if not gh:
            (path / "gh").unlink()
        env = {"STUB_ARGV": str(fx.argv), "STUB_RC": "0", "PATH": str(path),
               "STUB_GH_MODE": "empty", "STUB_GH_ARGV": str(fx.tmp / "gh-argv.txt"),
               "PYTHONPATH": pythonpath}
        return hook._git(fx.clone, "push", "-q", "origin", *(refspec or ("main",)),
                         check=False, env=env)

    def test_a_missing_suite_prerequisite_refuses_before_the_gate_runs(self) -> None:
        fx = self._clone()
        before = fx.remote_count()
        r = self._push(fx, pythonpath=self._pythonpath(("coverage",), **{
            k: v for k, v in COMPLETE.items() if k != "coverage"}), tools=("rg", "markdownlint"))
        self.assertNotEqual(0, r.returncode, r.stderr)
        self.assertIn("coverage is missing", r.stderr)
        self.assertIn("Install:", r.stderr)
        self.assertIn("git push --no-verify", r.stderr)
        self.assertEqual([], fx.gate_calls(), "the gate ran before the push was refused")
        self.assertEqual(before, fx.remote_count(), "the remote advanced despite the refusal")

    def test_a_tag_push_is_refused_before_the_release_gate(self) -> None:
        fx = self._clone()
        hook._git(fx.clone, "tag", "v9.9.9")
        r = self._push(fx, "refs/tags/v9.9.9", pythonpath=self._pythonpath(("pyyaml",), **{
            k: v for k, v in COMPLETE.items() if k != "PyYAML"}), tools=("rg", "markdownlint"))
        self.assertNotEqual(0, r.returncode, r.stderr)
        self.assertIn("PyYAML is missing", r.stderr)
        self.assertIn("release boundary gate", r.stderr)
        self.assertEqual([], fx.gate_calls(), "the release gate ran before the tag was refused")
        self.assertEqual("", hook._git(fx.remote, "tag", "-l").stdout.strip())

    def test_a_prerequisite_that_does_not_make_the_suite_red_is_named_not_refused(self) -> None:
        fx = self._clone()
        r = self._push(fx, pythonpath=self._pythonpath(("pytest-xdist",), **{
            k: v for k, v in COMPLETE.items() if k != "pytest-xdist"}), gh=False)
        self.assertEqual(0, r.returncode, r.stderr)
        for name, consequence in (("pytest-xdist is missing", "runs serially"),
                                  ("rg is not found", "ripgrep skip"),
                                  ("markdownlint is not found", "markdown lanes skip"),
                                  ("gh is not found", "reads UNREAD")):
            line = next((ln for ln in r.stderr.splitlines() if name in ln), "")
            with self.subTest(gap=name):
                self.assertIn("note", line, r.stderr)
                self.assertIn(consequence, line, r.stderr)
        self.assertEqual(["--boundary push"], fx.gate_calls())

    def test_a_complete_environment_reaches_the_gate(self) -> None:
        fx = self._clone()
        r = self._push(fx, pythonpath=self._pythonpath(**COMPLETE), tools=("rg", "markdownlint"))
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertNotIn("is missing", r.stderr)
        self.assertNotIn("is not found", r.stderr)
        self.assertIn("every one present", r.stderr)
        self.assertEqual(["--boundary push"], fx.gate_calls())


    def test_a_clone_without_the_check_is_told_and_pushes(self) -> None:
        """The Notes' absent case: a clone whose tools/ lacks gate_prereqs.py names that it was
        not checked, and the push proceeds. MUTANT: the hook refuses, or says nothing."""
        fx = hook._Clone()
        self.addCleanup(fx.cleanup)
        r = self._push(fx, pythonpath=self._pythonpath(**COMPLETE), tools=("rg", "markdownlint"))
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn("the prerequisite check is not present in this clone", r.stderr)
        self.assertEqual(["--boundary push"], fx.gate_calls())

if __name__ == "__main__":
    unittest.main()
