"""Unit tests for tools/check_links.py (skill-dev link checker).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

# tools/ lives at the repo root, six parents up from this test file.
TOOLS = Path(__file__).resolve().parents[1] / "check_links.py"
_spec = importlib.util.spec_from_file_location("check_links", TOOLS)
assert _spec and _spec.loader
check_links = importlib.util.module_from_spec(_spec)
sys.modules["check_links"] = check_links
_spec.loader.exec_module(check_links)


def _write(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


class SlugTests(unittest.TestCase):
    def test_slug_and_explicit_id_stripped(self) -> None:
        self.assertEqual(check_links.slug("Test Organisation (X)"), "test-organisation-x")
        self.assertEqual(check_links.slug("Foo {#bar}"), "foo")


class CheckTests(unittest.TestCase):
    def test_resolves_valid_and_flags_broken(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.md", "## Foo {#foo}\n\n## Plain Heading\n")
            _write(root, "b.md",
                   "see `a.md#foo` and `a.md#plain-heading` and `a.md#missing` and `c.md#x`\n")
            _write(root, "sub/e.md", "rel link `../a.md#foo`\n")  # file-relative, valid
            broken = check_links.check(root, set())
            joined = "\n".join(broken)
            self.assertIn("a.md#missing [anchor missing]", joined)
            self.assertIn("c.md#x [file missing]", joined)
            # Valid references must not be reported.
            self.assertNotIn("a.md#foo", joined)
            self.assertNotIn("a.md#plain-heading", joined)
            self.assertNotIn("../a.md#foo", joined)

    def test_allowlist_suppresses(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "g.md", "example `doc.md#section-name`\n")
            self.assertEqual(check_links.check(root, {"doc.md#section-name"}), [])

    def test_explicit_anchor_on_non_heading_line(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.md", "- e. Post-Wave Merge Protocol {#merge}\n")
            _write(root, "b.md", "ref `a.md#merge`\n")
            self.assertEqual(check_links.check(root, set()), [])


if __name__ == "__main__":
    unittest.main()
