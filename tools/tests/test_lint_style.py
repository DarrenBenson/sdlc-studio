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


def _prov_fixture(root: Path, py_body: str) -> Path:
    """A fixture skill tree with a shipped scripts/*.py, for the provenance-tag guard."""
    scripts = root / ".claude" / "skills" / "sdlc-studio" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "x.py").write_text(py_body, encoding="utf-8")
    tools = root / "tools"
    tools.mkdir()
    (tools / "style-allowlist.txt").write_text("", encoding="utf-8")
    return root


class ProvenanceGuardTests(unittest.TestCase):
    """CR0201: the guard catches a US-led provenance pair (the old pattern missed US-form) and a
    CR/BG/RFC-led tag, without false-positiving on legitimate example ids."""

    def test_flags_us_led_provenance_pair(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            r = _run(_prov_fixture(Path(d), "# added by (US0101/CR0186) here\n"))
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("provenance tag", r.stdout)
            self.assertIn("US0101/CR0186", r.stdout)

    def test_flags_cr_led_tag(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            r = _run(_prov_fixture(Path(d), "# see (CR0186) for context\n"))
            self.assertEqual(r.returncode, 1, r.stdout)

    def test_does_not_flag_example_ids(self) -> None:
        # comma/hyphen lists, a lone id, and ids trailing narrative text are legitimate examples
        clean = (
            "# stories created: (US0045, US0046, US0047)\n"
            "# range (US0023-US0064, archived)\n"
            "# tree node Story (US0001)\n"
            "# a prefixed id (US0057) is accepted\n"
            "# see the retired check (e.g. CR0003)\n"
        )
        with tempfile.TemporaryDirectory() as d:
            r = _run(_prov_fixture(Path(d), clean))
            self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == "__main__":
    unittest.main()
