"""BG0927: a dangling transcript in another project's folder does not crash the long-path scan.

BG0882 finds a long-path project's transcript folder by reading, in every folder under
`projects/`, the `cwd` its newest transcript records. `_newest_transcript` sorted by `stat()`,
so one dangling `.jsonl` link in an unrelated folder raised FileNotFoundError and the report
could not be built. The link is now skipped where its `stat` fails, as an unreadable transcript
is skipped when its `cwd` is read.

HOME points at a fixture and the env override is cleared, so the default derivation is read.
"""
from __future__ import annotations

# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/run_state.py
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


def _write(folder: Path, cwd: str, mtime: float) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    f = folder / "s.jsonl"
    f.write_text(json.dumps({"cwd": cwd, "message": {"usage": {"input_tokens": 1}}}) + "\n",
                 encoding="utf-8")
    os.utime(f, (mtime, mtime))


class TranscriptScanDanglingTests(unittest.TestCase):
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

    def test_a_dangling_transcript_is_skipped(self) -> None:
        """AC1. MUTANT: HEAD's `_newest_transcript`, which stats every `.jsonl` it globs - the
        dangling link in the unrelated folder raises FileNotFoundError. The control is the
        matching folder, which must still resolve: a mutant that gives up on the first folder it
        cannot read, or skips a whole folder holding a dangling link, returns the slug folder."""
        root = self.base / ("a" * 70) / ("b" * 70) / ("c" * 70)
        root.mkdir(parents=True)
        slug = run_state.harness_project_slug(root)
        self.assertGreater(len(slug), 200, "the premise: a slug the harness truncates")
        now = time.time()
        match = self.projects / (slug[:200] + "-1abc2d")
        _write(match, str(root), now - 100)
        # The matching folder holds a dangling link too, newer than its real transcript.
        (match / "gone.jsonl").symlink_to(self.base / "nowhere-a.jsonl")
        other = self.projects / "-unrelated-project"
        _write(other, "/somewhere/else", now)
        (other / "broken.jsonl").symlink_to(self.base / "nowhere-b.jsonl")
        self.assertFalse((other / "broken.jsonl").exists(), "the premise: a dangling link")

        got = run_state._harness_transcript_dir(root)

        self.assertEqual(match, got)


if __name__ == "__main__":
    unittest.main()
