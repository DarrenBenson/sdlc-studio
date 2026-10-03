"""BG0882: the token meter finds the transcript folder the harness actually writes.

The harness maps each UTF-16 code unit outside `[A-Za-z0-9]` to `-`, so a non-BMP character (an
emoji, two code units) becomes two dashes; `run_state` mapped per code point and wrote one. It
also truncates a slug past 200 characters and appends a hash, which `run_state` never did, so a
repo under a deep path looked in a folder that does not exist. The long case is found by the
`cwd` the transcript records rather than by re-deriving the harness's hash.

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


def _record(tokens: int, cwd: str | None = None) -> str:
    rec: dict = {"message": {"usage": {"input_tokens": tokens}}}
    if cwd is not None:
        rec["cwd"] = cwd
    return json.dumps(rec) + "\n"


def _write(folder: Path, body: str, mtime: float) -> None:
    folder.mkdir(parents=True)
    f = folder / "s.jsonl"
    f.write_text(body, encoding="utf-8")
    os.utime(f, (mtime, mtime))


class TranscriptDirHarnessTests(unittest.TestCase):
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

    def test_a_non_bmp_character_maps_to_two_dashes(self) -> None:
        """AC1. MUTANT: HEAD maps per code point, so the emoji becomes ONE dash, the meter looks
        in `...-x-app` and reports `no harness transcript directory`."""
        root = self.base / "x\U0001F600app"
        root.mkdir()
        # The harness's name, spelled out: `/` -> `-`, the emoji (two UTF-16 units) -> `--`.
        name = str(self.base).replace("/", "-").replace("_", "-").replace(".", "-") + "-x--app"
        _write(self.projects / name, _record(9), time.time())
        got = run_state.session_tokens(root)
        self.assertEqual(9, got.get("tokens"), got)

    def test_a_long_path_is_found_by_its_recorded_cwd(self) -> None:
        """AC2. MUTANT: HEAD looks only in the untruncated slug folder and reports `no harness
        transcript directory`. MUTANT: take the newest folder sharing the slug's first 200
        characters without reading its `cwd` - the decoy below is newer, shares that prefix and
        records another repo's `cwd`, so it reads 999."""
        root = self.base / ("a" * 70) / ("b" * 70) / ("c" * 70)
        root.mkdir(parents=True)
        slug = run_state.harness_project_slug(root)
        self.assertGreater(len(slug), 200, "the premise: a slug the harness truncates")
        now = time.time()
        _write(self.projects / (slug[:200] + "-1abc2d"), _record(1, cwd=None)
               + _record(41, cwd=str(root)), now - 100)
        _write(self.projects / (slug[:200] + "-9zz9zz"), _record(999, cwd=str(root) + "-other"),
               now)
        got = run_state.session_tokens(root)
        self.assertEqual(42, got.get("tokens"), got)


if __name__ == "__main__":
    unittest.main()
