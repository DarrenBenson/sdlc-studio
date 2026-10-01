"""BG0835: the token meter finds the session transcript for a repo path holding `.` or `_`.

The harness names a project's transcript folder after its path with every character outside
`[A-Za-z0-9]` mapped to `-`; `run_state` mapped only `/`, so a repo at `my_app.v2` looked in
`-...-my_app.v2`, found nothing, and the report's token actual read NOT ATTRIBUTABLE. HOME points
at a fixture and the env override is cleared, so the default derivation is what is read.
"""
from __future__ import annotations

# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/run_state.py
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import run_state  # noqa: E402


def _harness_name(root: Path) -> str:
    """The harness's folder name, spelled out character by character as the fixture states it:
    `/`, `.` and `_` each become `-`; letters, digits and `-` stay."""
    out = str(root)
    for ch in "/._":
        out = out.replace(ch, "-")
    return out


class TranscriptDirTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name).resolve()
        self.home = base / "home"
        self.root = base / "x" / "my_app.v2"
        self.root.mkdir(parents=True)
        env = {k: v for k, v in os.environ.items() if k != run_state.TRANSCRIPTS_ENV}
        env["HOME"] = str(self.home)
        patch = mock.patch.dict(os.environ, env, clear=True)
        patch.start()
        self.addCleanup(patch.stop)

    def test_dots_and_underscores_map_to_dashes(self) -> None:
        """AC1. MUTANT: HEAD, which maps only `/` and looks in `-...-my_app.v2`. MUTANT: map
        `/` and `.` but not `_` - it looks in `-...-my_app-v2` and misses the folder."""
        name = _harness_name(self.root)
        self.assertTrue(name.endswith("-x-my-app-v2"), name)
        folder = self.home / ".claude" / "projects" / name
        folder.mkdir(parents=True)
        (folder / "s.jsonl").write_text(
            json.dumps({"message": {"usage": {"input_tokens": 7, "output_tokens": 5}}}) + "\n",
            encoding="utf-8")
        got = run_state.session_tokens(self.root)
        self.assertEqual(12, got.get("tokens"), got)
        self.assertEqual(name, run_state.harness_project_slug(self.root))

    def test_an_explicit_directory_still_wins(self) -> None:
        """The env override and the argument are untouched by the derivation. MUTANT: derive
        the folder even when one is given."""
        given = self.root.parent / "given"
        given.mkdir()
        (given / "s.jsonl").write_text(
            json.dumps({"message": {"usage": {"input_tokens": 3}}}) + "\n", encoding="utf-8")
        self.assertEqual(3, run_state.session_tokens(self.root, given).get("tokens"))


if __name__ == "__main__":
    unittest.main()
