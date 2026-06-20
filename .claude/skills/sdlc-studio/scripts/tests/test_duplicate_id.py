"""Unit tests for the deterministic duplicate-ID collision detector (US0006).

TDD RED: these tests target a `collisions` subcommand on next_id.py that does
not exist yet. They are expected to fail until US0006 is implemented.

Contract (from sdlc-studio/stories/US0006-duplicate-id-detector.md):
  python3 scripts/next_id.py collisions [--root ROOT] [--format {text,json}]
  JSON: { "duplicates": [ { "id", "files": [<sorted paths>] } ], "count" }
  exit: 0 = no collisions, 1 = one or more collisions

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "next_id.py"
_spec = importlib.util.spec_from_file_location("next_id", SCRIPT_PATH)
assert _spec and _spec.loader
next_id = importlib.util.module_from_spec(_spec)
sys.modules["next_id"] = next_id
_spec.loader.exec_module(next_id)


def _write(root: Path, rel: str, body: str = "# x\n\n> **Status:** Open\n") -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return p


def _detect(root: Path) -> dict:
    """Call the detector and return its parsed JSON object.

    Uses the public `detect_collisions` helper when present, otherwise drives
    the `collisions --format json` subcommand and parses stdout. Either entry
    point is acceptable per the story; both must yield the documented shape.
    """
    if hasattr(next_id, "detect_collisions"):
        return next_id.detect_collisions(root)
    buf = io.StringIO()
    with redirect_stdout(buf):
        next_id.main(["collisions", "--root", str(root), "--format", "json"])
    return json.loads(buf.getvalue())


class GroupingTests(unittest.TestCase):
    def test_dash_insensitive_normalisation(self) -> None:
        # CR0007 and CR-0007 must normalise to one key CR0007 and be flagged.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/change-requests/CR0007-a.md")
            _write(root, "sdlc-studio/change-requests/CR-0007-b.md")
            obj = _detect(root)
            ids = [g["id"] for g in obj["duplicates"]]
            self.assertEqual(ids, ["CR0007"])


class DetectTests(unittest.TestCase):
    def test_two_files_one_id_flagged(self) -> None:
        # Two distinct bug files both claiming BG0001 -> one collision listing
        # both paths. This is the core RED case in the prompt.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            a = _write(root, "sdlc-studio/bugs/BG0001-first.md")
            b = _write(root, "sdlc-studio/bugs/BG0001-second.md")
            obj = _detect(root)
            self.assertEqual(obj["count"], 1)
            self.assertEqual(len(obj["duplicates"]), 1)
            dup = obj["duplicates"][0]
            self.assertEqual(dup["id"], "BG0001")
            self.assertEqual(
                sorted(dup["files"]),
                sorted([str(a), str(b)]),
            )

    def test_single_file_not_self_collision(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/bugs/BG0001-lonely.md")
            obj = _detect(root)
            self.assertEqual(obj["count"], 0)
            self.assertEqual(obj["duplicates"], [])


class ExitTests(unittest.TestCase):
    def test_nonzero_exit_on_collision(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/bugs/BG0001-first.md")
            _write(root, "sdlc-studio/bugs/BG0001-second.md")
            rc = next_id.main(["collisions", "--root", str(root)])
            self.assertEqual(rc, 1)

    def test_zero_exit_when_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/bugs/BG0001-only.md")
            _write(root, "sdlc-studio/bugs/BG0002-only.md")
            rc = next_id.main(["collisions", "--root", str(root)])
            self.assertEqual(rc, 0)


class OutputTests(unittest.TestCase):
    def test_json_shape(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/bugs/BG0001-first.md")
            _write(root, "sdlc-studio/bugs/BG0001-second.md")
            obj = _detect(root)
            self.assertIn("duplicates", obj)
            self.assertIn("count", obj)
            self.assertIsInstance(obj["duplicates"], list)
            self.assertEqual(obj["count"], len(obj["duplicates"]))
            for g in obj["duplicates"]:
                self.assertIn("id", g)
                self.assertIn("files", g)
                self.assertEqual(g["files"], sorted(g["files"]))


if __name__ == "__main__":
    unittest.main()
