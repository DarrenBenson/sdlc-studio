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
sys.path.insert(0, str(SCRIPT_PATH.parent))
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


def _make_meta(root: Path, rel: str, prefix: str, nums: list[int]) -> None:
    d = root / rel
    d.mkdir(parents=True, exist_ok=True)
    for n in nums:
        (d / f"{prefix}{n:04d}-x.md").write_text(f"# {prefix}{n}\n", encoding="utf-8")


class MetaTypeTests(unittest.TestCase):
    """CR0105: review/retro carry a numeric id and must allocate deterministically."""

    def test_review_allocates_above_max(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _make_meta(root, "sdlc-studio/reviews", "RV", [1, 4])
            self.assertEqual(next_id.local_ids("review", root), [1, 4])
            self.assertEqual(next_id.allocate_number("review", root, remote=False), 5)

    def test_retro_first_id_when_empty(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(next_id.allocate_number("retro", Path(d), remote=False), 1)

    def test_retro_ignores_non_index_noise(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _make_meta(root, "sdlc-studio/retros", "RETRO", [2])
            (root / "sdlc-studio" / "retros" / "_index.md").write_text("# x\n", encoding="utf-8")
            self.assertEqual(next_id.allocate_number("retro", root, remote=False), 3)


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



class AllocateNumberTests(unittest.TestCase):
    def test_empty_repo_allocates_one(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(next_id.allocate_number("cr", Path(d), remote=False), 1)

    def test_index_row_ids_ignores_malformed_rows(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sd = Path(d) / "sdlc-studio" / "change-requests"; sd.mkdir(parents=True)
            (sd / "_index.md").write_text(
                "# I\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [CR-0003](x.md) | a | Done |\n| Open | 2 |\n| no id here | b | Draft |\n", encoding="utf-8")
            self.assertEqual(next_id.index_row_ids("cr", Path(d)), [3])
            self.assertEqual(next_id.allocate_number("cr", Path(d), remote=False), 4)

    def test_remote_ids_graceful_without_git(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(next_id.remote_ids("cr", Path(d)), ([], False))

    def test_remote_ahead_id_not_reissued(self) -> None:
        import os, shutil, subprocess
        if shutil.which("git") is None:
            self.skipTest("git not available")
        env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
               "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        def g(args, cwd):
            subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True, env=env)
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d) / "repo"; (repo / "sdlc-studio" / "change-requests").mkdir(parents=True)
            (repo / "sdlc-studio" / "change-requests" / "CR0009-x.md").write_text(
                "# CR0009: x\n\n> **Status:** Done\n", encoding="utf-8")
            g(["init", "-q", "-b", "main"], repo); g(["add", "-A"], repo); g(["commit", "-qm", "i"], repo)
            bare = Path(d) / "bare.git"; g(["clone", "-q", "--bare", str(repo), str(bare)], Path(d))
            g(["remote", "add", "origin", str(bare)], repo); g(["fetch", "-q", "origin"], repo)
            (repo / "sdlc-studio" / "change-requests" / "CR0009-x.md").unlink()  # local census now empty
            self.assertEqual(next_id.local_ids("cr", repo), [])
            rids, avail = next_id.remote_ids("cr", repo)
            self.assertTrue(avail); self.assertIn(9, rids)
            self.assertEqual(next_id.allocate_number("cr", repo, remote=True), 10)  # above remote, not 1


if __name__ == "__main__":
    unittest.main()
