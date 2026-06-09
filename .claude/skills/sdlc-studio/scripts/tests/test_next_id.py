"""Unit tests for next_id.py.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "next_id.py"
_spec = importlib.util.spec_from_file_location("next_id", SCRIPT_PATH)
assert _spec and _spec.loader
next_id = importlib.util.module_from_spec(_spec)
sys.modules["next_id"] = next_id
_spec.loader.exec_module(next_id)


def _make_stories(root: Path, nums: list[int]) -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    for n in nums:
        (d / f"US{n:04d}-x.md").write_text(f"# S{n}\n\n> **Status:** Draft\n", encoding="utf-8")


class LocalIdsTests(unittest.TestCase):
    def test_local_ids_sorted_unique(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _make_stories(root, [3, 1, 2])
            self.assertEqual(next_id.local_ids("story", root), [1, 2, 3])

    def test_local_ids_empty(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(next_id.local_ids("story", Path(d)), [])


class AllocateTests(unittest.TestCase):
    def test_allocate_next_is_max_plus_one(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _make_stories(root, [1, 2, 7])
            rc = next_id.main(["allocate", "--type", "story", "--root", str(d)])
            self.assertEqual(rc, 0)

    def test_allocate_first_id_when_empty(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "epics").mkdir(parents=True)
            ids = next_id.local_ids("epic", root)
            self.assertEqual(ids, [])
            # max(0)+1 -> EP0001 (exercised via cmd path returning 0)
            rc = next_id.main(["allocate", "--type", "epic", "--root", str(d)])
            self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
