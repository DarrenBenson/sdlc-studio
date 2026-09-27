"""BG0782: a fixture repository made under either test runner has git's automatic maintenance off.

Every `git commit` starts `git maintenance run --auto --detach`, and from git 2.55 (CI's) that
process outlives the commit and writes into `.git` while `TemporaryDirectory` removes it, so a
green test fails on teardown with Errno 39 (BG0711, fixed there for one module). About a hundred
modules commit in temporary repositories, so the runners turn it off for the whole run instead:
the repository-root conftest.py for pytest, `tools/skill-tests.sh` for unittest, each appending
`maintenance.auto=false` through `GIT_CONFIG_COUNT`/`KEY`/`VALUE` after what the caller set.

`tools/tests/test_lean_git_maintenance_off.py` runs this module through `tools/skill-tests.sh`.
"""
# test-census-subject: conftest.py
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gitutil import git  # noqa: E402

REPO = HERE.parents[4]
TREES = ("tools/tests", ".claude/skills/sdlc-studio/scripts/tests")

#: Reads both the runner's setting and an entry the caller made before the run started.
PROBE = '''\
import os
import subprocess
import tempfile
import unittest


class Probe(unittest.TestCase):
    def test_reads_both_entries(self):
        env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["git", "init", "-q"], cwd=d, env=env, check=True)
            read = [subprocess.run(["git", "config", "--get", key], cwd=d, env=env,
                                   capture_output=True, text=True).stdout.strip()
                    for key in ("maintenance.auto", "sdlc.kept")]
        self.assertEqual(["false", "yes"], read)
'''


def without_git_config_entries(env: dict) -> dict:
    """`env` with no `GIT_CONFIG_COUNT`/`KEY_n`/`VALUE_n`, so a child run starts from none."""
    return {k: v for k, v in env.items() if not re.fullmatch(r"GIT_CONFIG_(COUNT|KEY_\d+|VALUE_\d+)", k)}


def with_one_callers_entry(env: dict) -> dict:
    """`env` carrying exactly one entry of the caller's own, `sdlc.kept=yes`."""
    return {**without_git_config_entries(env), "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "sdlc.kept", "GIT_CONFIG_VALUE_0": "yes"}


class GitMaintenanceOffTests(unittest.TestCase):

    def test_a_fixture_repo_reads_maintenance_off(self) -> None:
        """AC1. In this run, when a runner of this repository owns it (both set
        `SDLC_TEST_TMPDIR`; a bare `python3 -m unittest` does not, and runs only the half after),
        a fresh fixture repository reads `maintenance.auto` false. Then a pytest session over a
        probe in each test tree, with the root conftest copied into a fixture at its repository
        path and the caller holding one entry of its own, reads it false with that entry kept.
        MUTANTS: drop the conftest's call (both halves go red under pytest); overwrite
        `GIT_CONFIG_COUNT` instead of appending (the session loses `sdlc.kept`)."""
        if os.environ.get("SDLC_TEST_TMPDIR"):
            with tempfile.TemporaryDirectory() as d:
                git(["init", "-q"], d)
                read = git(["config", "--get", "maintenance.auto"], d, check=False, text=True)
            self.assertEqual("false", read.stdout.strip(),
                             "this run's fixture repositories run automatic maintenance")

        with tempfile.TemporaryDirectory() as root:
            fixture = Path(root)
            for name in ("pytest.ini", "conftest.py"):
                shutil.copy2(REPO / name, fixture / name)
            probes = []
            for i, tree in enumerate(TREES):
                (fixture / tree).mkdir(parents=True)
                if (REPO / tree / "conftest.py").is_file():
                    shutil.copy2(REPO / tree / "conftest.py", fixture / tree / "conftest.py")
                probe = fixture / tree / f"test_maintenance_probe_{i}.py"
                probe.write_text(PROBE, encoding="utf-8")
                probes.append(str(probe.relative_to(fixture)))
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *probes],
                cwd=fixture, env=with_one_callers_entry(os.environ), capture_output=True,
                text=True, timeout=300)
        out = proc.stdout + proc.stderr
        self.assertEqual(0, proc.returncode, out)
        self.assertIn(f"{len(TREES)} passed", out)


if __name__ == "__main__":
    unittest.main()
