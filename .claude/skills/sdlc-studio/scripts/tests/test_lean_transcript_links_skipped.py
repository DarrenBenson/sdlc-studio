"""BG0932: a broken or self-looping transcript link in the project's own folder is skipped.

BG0927 skipped a transcript whose `stat` fails while the long-path scan chooses a folder, but
`session_tokens`, the reading the report takes, sorted the chosen folder's `.jsonl` files by
`stat` itself, so a dangling link there raised FileNotFoundError and a self-looping one raised
OSError (ELOOP). It now picks the newest transcript as the scan does, skipping both.

HOME points at a fixture and the env override is cleared, so the default derivation is read.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/run_state.py
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import run_state  # noqa: E402


class TranscriptLinksSkippedTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name).resolve()
        self.projects = self.base / "home" / ".claude" / "projects"
        env = {k: v for k, v in os.environ.items() if k != run_state.TRANSCRIPTS_ENV}
        env["HOME"] = str(self.base / "home")
        patch = mock.patch.dict(os.environ, env, clear=True)
        patch.start()
        self.addCleanup(patch.stop)

    def _folder(self, root: Path, folder: Path) -> None:
        """`folder` holding one real transcript recording `root`, worth 5 tokens, an older
        decoy worth 3, a dangling link and a link to itself."""
        folder.mkdir(parents=True)
        now = time.time()
        for name, tokens, mtime in (("old.jsonl", 3, now - 200), ("real.jsonl", 5, now - 100)):
            f = folder / name
            f.write_text(json.dumps({"cwd": str(root),
                                     "message": {"usage": {"input_tokens": tokens}}}) + "\n",
                         encoding="utf-8")
            os.utime(f, (mtime, mtime))
        (folder / "gone.jsonl").symlink_to(self.base / "nowhere.jsonl")
        (folder / "loop.jsonl").symlink_to(folder / "loop.jsonl")
        for link in ("gone.jsonl", "loop.jsonl"):
            with self.assertRaises(OSError, msg=f"premise: {link} cannot be stat'd"):
                (folder / link).stat()

    def test_broken_and_looping_links_are_skipped(self) -> None:
        """AC1. MUTANT: HEAD's `session_tokens`, which sorts the folder by `stat` and raises on
        the dangling link. The control is the reading itself: the real transcript's 5 tokens,
        so a mutant that skips the whole folder, or reads the older decoy, also fails. Run for
        the folder named by the slug and for the one the long-path scan finds."""
        short = self.base / "repo"
        long_ = self.base / ("a" * 70) / ("b" * 70) / ("c" * 70)
        for root in (short, long_):
            with self.subTest(slug_length=len(run_state.harness_project_slug(root))):
                root.mkdir(parents=True)
                slug = run_state.harness_project_slug(root)
                folder = self.projects / (slug if len(slug) <= 200 else slug[:200] + "-1abc2d")
                self._folder(root, folder)
                self.assertEqual(folder, run_state._harness_transcript_dir(root))

                got = run_state.session_tokens(root)

                self.assertEqual(5, got.get("tokens"), got)
                self.assertEqual("real.jsonl", Path(got.get("source") or "").name, got)


if __name__ == "__main__":
    unittest.main()
