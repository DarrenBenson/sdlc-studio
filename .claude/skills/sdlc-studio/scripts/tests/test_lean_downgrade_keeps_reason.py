"""BG0737: the stale downgrade keeps the author's reason on the positive verdict it replaces.

When a criterion stamped `yes (<date>) - <reason>` goes red, `verify_ac run` rewrites the line to
its marked `no`. It used to write only the mark, so the author's reason was gone from the file
and recorded nowhere. Each test drives the shipped CLI as a subprocess against a throwaway
workspace holding one story; nothing reads this repository's own artefacts.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
NOTE = "downgraded by verify_ac - the selector was red at verification time"
REASON = "four tests, each driving a shipped main([...])"

_STORY = ("# US0001: a story\n\n> **Status:** In Progress\n\n## Acceptance Criteria\n\n"
          "- [x] **AC1** Given a, when b, then c\n  - **Verify:** shell test -f {flag}\n"
          "  - **Verified:** {verified}\n")


class DowngradeKeepsReasonTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.flag = self.root / "flag.txt"
        stories = self.root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        self.story = stories / "US0001-a-story.md"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _run(self, verified: str | None = None) -> tuple[subprocess.CompletedProcess, str]:
        if verified is not None:
            self.story.write_text(_STORY.format(flag=self.flag, verified=verified),
                                  encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / "verify_ac.py"), "run", "--story",
             str(self.story), "--repo-root", str(self.root)],
            capture_output=True, text=True, check=False, timeout=300)
        lines = [ln.strip() for ln in self.story.read_text(encoding="utf-8").splitlines()
                 if "**Verified:**" in ln]
        self.assertEqual(1, len(lines), lines)
        return proc, lines[0]

    @staticmethod
    def _today() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def test_a_red_run_keeps_the_recorded_reason(self) -> None:
        """AC1. MUTANT: HEAD, which writes `no (<today>) - <note>` and drops the reason."""
        proc, line = self._run(f"yes (2026-08-03) - {REASON}")
        self.assertEqual(1, proc.returncode, proc.stdout + proc.stderr)
        self.assertEqual(f"- **Verified:** no ({self._today()}) - {NOTE}; was: {REASON}", line)

    def test_a_bare_yes_downgrades_unchanged(self) -> None:
        """AC2. MUTANT: append `; was: ` unconditionally, leaving `; was: ` with nothing after."""
        proc, line = self._run("yes (2026-01-01)")
        self.assertEqual(1, proc.returncode, proc.stdout + proc.stderr)
        self.assertEqual(f"- **Verified:** no ({self._today()}) - {NOTE}", line)

    def test_the_kept_reason_does_not_stop_the_loop_closing(self) -> None:
        """Neighbour of AC1: the downgrade is still read as the tool's own, so a green rerun
        clears it. MUTANT: write the reason in place of the mark (`no (<today>) - <reason>`),
        which the next green run reads as the author's disclosure and refuses forever."""
        self._run(f"yes (2026-08-03) - {REASON}")
        self.flag.write_text("", encoding="utf-8")
        proc, line = self._run()
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertTrue(line.startswith("- **Verified:** yes"), line)


if __name__ == "__main__":
    unittest.main()
