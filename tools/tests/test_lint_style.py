"""Unit tests for the British-spelling pass of tools/lint-style.sh.

The script takes an optional scan-root argument precisely so these tests can
point it at a fixture tree; the fixture supplies its own allowlist.
"""
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "lint-style.sh"


def _run(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", str(SCRIPT), str(root)],
                          capture_output=True, text=True)


def _fixture(root: Path, body: str, allow: str = "") -> Path:
    (root / "doc.md").write_text(body, encoding="utf-8")
    tools = root / "tools"
    tools.mkdir()
    (tools / "style-allowlist.txt").write_text(allow, encoding="utf-8")
    return root


class BritishSpellingTests(unittest.TestCase):
    def test_american_spelling_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            r = _run(_fixture(Path(d), "The color of this behavior is analyzed.\n"))
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("British English", r.stdout)
            self.assertIn("colour", r.stdout)          # the British form is suggested

    def test_british_spelling_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            r = _run(_fixture(Path(d), "The colour of this behaviour is analysed.\n"))
            self.assertEqual(r.returncode, 0, r.stdout)

    def test_allowlisted_line_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            r = _run(_fixture(Path(d), "run: gh label create x --color FBCA04\n",
                              allow="--color\n"))
            self.assertEqual(r.returncode, 0, r.stdout)

    def test_word_boundary_no_false_positive(self) -> None:
        # 'size', 'prize', 'colorful' (not in the bounded list) must not flag.
        with tempfile.TemporaryDirectory() as d:
            r = _run(_fixture(Path(d), "The size of the prize is colourful.\n"))
            self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == "__main__":
    unittest.main()
