"""US1004: CI and the prerequisite checker read one list of the suite's Python packages.

`tools/gate_prereqs.py` checks a clone against `requirements-dev.txt`; CI's suite step installed
its own inline list, so the two could drift and a clone could pass the checker yet miss what CI
runs with. The ci job now installs from the file. The scheduled corpus-verify job keeps its own
list on purpose (moving it would add pytest-xdist to a lane compared against a recorded
baseline), so it is held to a declared subset instead.

MUTANTS: the inline package list left in the ci job's suite step (AC1); the corpus-verify job
installing a package, or a looser floor, that requirements-dev.txt does not declare (AC2).
"""
# test-census-subject: .github/workflows/lint.yml
from __future__ import annotations

import re
import shlex
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
WORKFLOW = REPO / ".github" / "workflows" / "lint.yml"
SUITE_PACKAGES = {"pytest", "pytest-xdist", "pyyaml", "coverage"}


def _norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _floor(spec: str) -> tuple[int, ...] | None:
    m = re.search(r">=\s*([0-9][0-9.]*)", spec)
    return tuple(int(p) for p in m.group(1).split(".")) if m else None


def _declared() -> dict[str, tuple[int, ...] | None]:
    out = {}
    for line in (REPO / "requirements-dev.txt").read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            name = re.split(r"[<>=!~ ]", line, maxsplit=1)[0]
            out[_norm(name)] = _floor(line)
    return out


_PIP = re.compile(r"\bpip3?\s+install\b")


def _pip_installs(step: dict) -> list[str]:
    """Each `pip install` or `pip3 install` command line in one step, comments cut."""
    return [line.split("#", 1)[0].strip()
            for line in str(step.get("run") or "").splitlines()
            if _PIP.search(line.split("#", 1)[0])]


def _packages(command: str, *, expand: bool = False) -> list[str]:
    """The package specs a `pip install` line names, flags dropped; with `expand`, a `-r <file>`
    contributes that file's requirement lines, read from the repository."""
    words = shlex.split(command)
    words = words[words.index("install") + 1:]
    out, i = [], 0
    while i < len(words):
        word = words[i]
        if word in ("-r", "--requirement", "-c", "--constraint"):
            if expand and word in ("-r", "--requirement") and i + 1 < len(words):
                for line in (REPO / words[i + 1]).read_text(encoding="utf-8").splitlines():
                    line = line.split("#", 1)[0].strip()
                    if line and not line.startswith("-"):
                        out.append(line)
            i += 2
            continue
        if not word.startswith("-"):
            out.append(word)
        i += 1
    return out


def _name(spec: str) -> str:
    return _norm(re.split(r"[<>=!~;\[ ]", spec, maxsplit=1)[0])


class OneListTests(unittest.TestCase):
    def setUp(self) -> None:
        self.jobs = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]

    def test_the_ci_suite_step_installs_from_requirements_dev(self) -> None:
        steps = self.jobs["ci"]["steps"]
        suite_steps = [s for s in steps
                       if any("requirements-dev.txt" in c for c in _pip_installs(s))]
        self.assertTrue(suite_steps, "no ci step installs from requirements-dev.txt")
        for step in suite_steps:
            for command in _pip_installs(step):
                with self.subTest(command=command):
                    self.assertEqual([], _packages(command),
                                     "the suite step still carries a package list of its own")
        for step in steps:
            for command in _pip_installs(step):
                named = {_name(p) for p in _packages(command)} & SUITE_PACKAGES
                with self.subTest(command=command):
                    self.assertFalse(named, f"a ci step installs suite packages by hand: {named}")

    def test_the_corpus_verify_job_installs_a_declared_subset(self) -> None:
        declared = _declared()
        specs = [spec for step in self.jobs["corpus-verify"]["steps"]
                 for command in _pip_installs(step) for spec in _packages(command, expand=True)]
        self.assertTrue(specs, "corpus-verify installs no package, so this pins nothing")
        for spec in specs:
            name = _name(spec)
            with self.subTest(package=name):
                self.assertIn(name, declared, f"{name} is installed but not declared")
                if declared[name]:
                    self.assertIsNotNone(_floor(spec), f"{name} drops the declared floor")
                    self.assertGreaterEqual(_floor(spec), declared[name],
                                            f"{name}'s floor is looser than declared")

if __name__ == "__main__":
    unittest.main()
