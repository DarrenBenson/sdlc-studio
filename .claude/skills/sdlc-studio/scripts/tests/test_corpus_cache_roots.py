"""The corpus cache serves every caller paths in that caller's own root spelling."""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib import sdlc_md  # noqa: E402
import reconcile  # noqa: E402


class CorpusCacheRootsTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="cache_roots_")).resolve()
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        d = self.root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True)
        for n, t in (("BG0001-x", "x"), ("BG0002-y", "y")):
            (d / f"{n}.md").write_text(f"# {n[:6]}: {t}\n\n> **Status:** Open\n", encoding="utf-8")
        self.cwd = os.getcwd()
        self.addCleanup(os.chdir, self.cwd)
        os.chdir(self.root.parent)
        self.rel = Path(self.root.name)

    def test_a_relative_then_an_absolute_root_returns_the_same_names(self):
        outside = reconcile._census_filenames("bug", self.root)
        self.assertEqual(sorted(outside.values()), ["BG0001-x.md", "BG0002-y.md"])
        with sdlc_md.corpus_cache():
            first = sdlc_md.artifact_files("bug", self.rel)
            self.assertTrue(first and all(not p.is_absolute() for p in first))
            self.assertEqual(reconcile._census_filenames("bug", self.root), outside)
            self.assertEqual(reconcile._census_filenames("bug", self.rel), outside)
            again = sdlc_md.artifact_files("bug", self.root)
            self.assertTrue(all(p.is_absolute() for p in again))
            self.assertEqual([p.name for p in first], [p.name for p in again])
            # the text the first walk read is still served from the memo, keyed by file
            self.assertIn("BG0001", sdlc_md.read_text_safe(again[0]))

    def test_both_spellings_share_one_walk_and_one_read_of_each_file(self):
        walks = []
        real = sdlc_md._walk_artifact_files

        def counting(*a, **k):
            walks.append(a)
            return real(*a, **k)

        with mock.patch.object(sdlc_md, "_walk_artifact_files", counting):
            with sdlc_md.corpus_cache():
                relative = sdlc_md.artifact_files("bug", self.rel)
                sdlc_md.artifact_files("bug", self.root)
                self.assertEqual(len(walks), 1)
                # the walk's text is served for the file under either spelling, never re-read
                (self.root / "sdlc-studio" / "bugs" / "BG0001-x.md").unlink()
                self.assertIn("BG0001", sdlc_md.read_text_safe(self.root / "sdlc-studio" / "bugs"
                                                               / "BG0001-x.md"))
                self.assertIn("BG0001", sdlc_md.read_text_safe(relative[0]))

    def test_an_absolute_then_a_relative_root_returns_the_same_names(self):
        outside = reconcile._census_filenames("bug", self.root)
        with sdlc_md.corpus_cache():
            self.assertEqual(reconcile._census_filenames("bug", self.root), outside)
            self.assertEqual(reconcile._census_filenames("bug", self.rel), outside)


if __name__ == "__main__":
    unittest.main()
