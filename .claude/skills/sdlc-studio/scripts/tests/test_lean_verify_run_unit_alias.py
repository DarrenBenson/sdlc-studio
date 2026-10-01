"""US0804: `verify_ac.py run --unit <id>` selects the same story `--id <id>` does.

`revert-check --unit` and `critic.py brief --unit` name a unit with `--unit`, so the first guess
at `run` was refused with `unrecognized arguments`. Each test drives the shipped CLI as a
subprocess against a throwaway workspace; nothing reads this repository's own artefacts.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent

_STORY = ("# US0001: a story\n\n> **Status:** In Progress\n\n## Acceptance Criteria\n\n"
          "- [ ] **AC1** Given a, when b, then c\n  - **Verify:** shell test -d /\n")


def _run(root: Path, *flags: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / "verify_ac.py"), "run", *flags, "--dry-run",
         "--root", str(root)],
        capture_output=True, text=True, check=False, timeout=300)


def _summary(out: str) -> list[str]:
    return [ln for ln in out.splitlines() if "ac=" in ln and "pass=" in ln]


class VerifyRunUnitAliasTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        stories = self.root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        (stories / "US0001-a-story.md").write_text(_STORY, encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_unit_runs_the_same_story_as_id(self) -> None:
        """AC1. MUTANT: HEAD, where `run` declares no `--unit` and argparse exits 2."""
        by_unit = _run(self.root, "--unit", "US0001")
        by_id = _run(self.root, "--id", "US0001")
        out = by_unit.stdout + by_unit.stderr
        self.assertEqual(0, by_unit.returncode, out)
        self.assertEqual(0, by_id.returncode, by_id.stdout + by_id.stderr)
        self.assertTrue(any("ac=1 pass=1" in ln for ln in _summary(by_unit.stdout)), out)
        self.assertEqual(_summary(by_id.stdout), _summary(by_unit.stdout))

    def test_unit_with_another_selector_is_refused(self) -> None:
        """The alias is `--id` itself, so it stays in the one-selector group. MUTANT: a separate
        `--unit` argument outside the group, which lets `--unit X --ids Y` through with one
        selector silently ignored."""
        proc = _run(self.root, "--unit", "US0001", "--ids", "US0002")
        self.assertEqual(2, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("not allowed with", proc.stderr)


if __name__ == "__main__":
    unittest.main()
