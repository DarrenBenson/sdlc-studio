"""US0944: `verify_ac.py stamps` never reports green on nothing.

`stamps --story` skipped a value that was not an existing path, so an unknown id, or an id
given where a path was expected, read nothing and still printed that every stamped verifier
resolves, exit 0. Both tests drive the shipped CLI against a fixture project, from a working
directory where the bare id is not a path.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "verify_ac.py"

TEST_FILE = "class TestT:\n    def test_live(self):\n        assert True\n"


def _unit(path: Path, uid: str, verifier: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# {uid}: a stamped criterion\n\n> **Status:** Done\n\n"
        "## Acceptance Criteria\n\n### AC1: it holds\n\n"
        f"- **Verify:** {verifier}\n- **Verified:** yes (2026-09-25)\n", encoding="utf-8")


class StampsHonestTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "repo"
        (self.root / "tests").mkdir(parents=True)
        (self.root / "tests" / "test_x.py").write_text(TEST_FILE, encoding="utf-8")
        # The CLI runs from a sibling directory, so a bare id is never a path by accident.
        self.cwd = Path(tmp.name) / "elsewhere"
        self.cwd.mkdir()

    def _stamps(self, story: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "stamps", "--story", story, "--root", str(self.root)],
            capture_output=True, text=True, timeout=120, cwd=str(self.cwd))

    def test_an_unknown_story_is_refused(self) -> None:
        """AC1. MUTANT: HEAD's `if not p.exists(): continue` - one file 'checked', exit 0."""
        _unit(self.root / "sdlc-studio" / "stories" / "US0001-x.md", "US0001",
              "pytest tests/test_x.py::TestT::test_live")
        for bad in ("NOSUCH", "US9999"):
            with self.subTest(story=bad):
                proc = self._stamps(bad)
                self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
                self.assertIn(bad, proc.stderr, "the refusal must name the unknown id")
                self.assertNotIn("still resolves", proc.stdout,
                                 "a check that read nothing must not report green")

    def test_an_id_resolves_to_its_file(self) -> None:
        """AC2. MUTANTS: refusing every id instead of resolving it (exit 2); resolving under
        the stories directory alone, so a bug id is refused; matching case-sensitively, so a
        lower-case id is refused."""
        dead = "pytest tests/test_x.py::TestT::test_gone"
        _unit(self.root / "sdlc-studio" / "stories" / "US0001-x.md", "US0001", dead)
        _unit(self.root / "sdlc-studio" / "bugs" / "BG0001-y.md", "BG0001", dead)
        for given, uid in (("US0001", "US0001"), ("BG0001", "BG0001"), ("us0001", "US0001")):
            with self.subTest(id=given):
                proc = self._stamps(given)
                self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                self.assertIn(f"{uid} AC1", proc.stdout,
                              "the stale stamp must be named by unit and criterion")


if __name__ == "__main__":
    unittest.main()
