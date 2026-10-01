"""BG0827: the review brief names the commit the reviewer diffs against.

`critic.py brief` asked the reviewer to judge what the unit's diff did "at the base ref" and
scoped it by Affects, but named no ref, so a carried repair and the round-1 code in one tree
could not be told apart and reviewers had to be told the run's commit. The brief now prints the
run's recorded base ref as the exact `git diff <base> -- <Affects>` command. Each test drives the
shipped CLI against a throwaway git tree.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402 - confined git for the fixture repo

SCRIPTS = Path(__file__).resolve().parent.parent

_BUG = ("# BG0001: a bug\n\n> **Status:** In Progress\n> **Severity:** Low\n> **Affects:** a.py\n\n"
        "## Acceptance Criteria\n\n- [ ] **AC1** Given a, when b, then c. Fails on: x\n"
        "  - **Verify:** shell true\n")
_DIFF_CMD = re.compile(r"git diff \S+ --")


class BriefBaseRefTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / "a.py").write_text("x = 1\n", encoding="utf-8")
        bugs = self.root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True)
        (bugs / "BG0001-a-bug.md").write_text(_BUG, encoding="utf-8")
        gitutil.git(["init", "-q"], self.root)
        gitutil.git(["add", "-A"], self.root)
        gitutil.git(["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base"],
                    self.root)
        self.sha = gitutil.git(["rev-parse", "HEAD"], self.root,
                               capture_output=True, text=True).stdout.strip()

    def _brief(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / "critic.py"), "brief", "--unit", "BG0001",
             "--seat", "qa", "--root", str(self.root)],
            capture_output=True, text=True, check=False, timeout=120)

    def _open_run(self, batch: list[str]) -> None:
        state = self.root / "sdlc-studio" / ".local" / "run-state.json"
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text(json.dumps({"schema": 1, "run_id": "RUN-A", "outcome": "running",
                                     "started_at": "2026-10-01T08:00:00Z", "batch": batch,
                                     "base_ref": self.sha}), encoding="utf-8")

    def test_the_brief_names_its_base_commit(self) -> None:
        """AC1. MUTANT: HEAD, which names no ref. MUTANT: print the command whether or not a
        run names the unit - with no run, or a run whose batch is other work, there is no base
        to name. MUTANT: name the ref but not the Affects - the diff is then unbounded."""
        self._open_run(["BG0001"])
        proc = self._brief()
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn(f"git diff {self.sha} -- a.py", proc.stdout)
        # no run at all: the brief still renders, and names no diff command
        (self.root / "sdlc-studio" / ".local" / "run-state.json").unlink()
        proc = self._brief()
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIsNone(_DIFF_CMD.search(proc.stdout), proc.stdout)
        # a run whose batch is other work: its ref is not this unit's base
        self._open_run(["BG0002"])
        proc = self._brief()
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertNotIn(self.sha, proc.stdout)


if __name__ == "__main__":
    unittest.main()
