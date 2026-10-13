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


def _pip_installs(job: dict) -> list[str]:
    """Each `pip install` command line in a job's steps."""
    found = []
    for step in job.get("steps") or []:
        for line in str(step.get("run") or "").splitlines():
            if "pip install" in line:
                found.append(line.strip())
    return found


def _packages(command: str) -> list[str]:
    """The package specs a `pip install` line names, flags dropped."""
    words = shlex.split(command)
    words = words[words.index("install") + 1:]
    out, skip = [], False
    for word in words:
        if skip:
            skip = False
            continue
        if word in ("-r", "--requirement", "-c", "--constraint"):
            skip = True
            continue
        if not word.startswith("-"):
            out.append(word)
    return out


class OneListTests(unittest.TestCase):
    def setUp(self) -> None:
        self.jobs = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]

    def test_the_ci_suite_step_installs_from_requirements_dev(self) -> None:
        suite = [c for c in _pip_installs(self.jobs["ci"])
                 if "requirements-dev.txt" in c
                 or SUITE_PACKAGES & {_norm(re.split(r"[<>=!~ ]", p)[0]) for p in _packages(c)}]
        self.assertTrue(suite, "the ci job installs no suite packages at all")
        for command in suite:
            with self.subTest(command=command):
                self.assertIn("-r requirements-dev.txt", command)
                self.assertEqual([], _packages(command),
                                 "the suite step still carries a package list of its own")

    def test_the_corpus_verify_job_installs_a_declared_subset(self) -> None:
        declared = _declared()
        commands = _pip_installs(self.jobs["corpus-verify"])
        self.assertTrue(commands, "corpus-verify installs nothing, so this pins nothing")
        for command in commands:
            for spec in _packages(command):
                name = _norm(re.split(r"[<>=!~ ]", spec, maxsplit=1)[0])
                with self.subTest(package=name):
                    self.assertIn(name, declared, f"{name} is installed but not declared")
                    if declared[name]:
                        self.assertIsNotNone(_floor(spec), f"{name} drops the declared floor")
                        self.assertGreaterEqual(_floor(spec), declared[name],
                                                f"{name}'s floor is looser than declared")


if __name__ == "__main__":
    unittest.main()
