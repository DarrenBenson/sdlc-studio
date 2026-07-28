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
sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the shared gitutil helper
import gitutil  # noqa: E402
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

    def test_off_template_file_still_holds_its_id(self) -> None:
        # allocation safety keys on the FILENAME, never the header shape: an
        # id-named file with no artifact header (off-template import, or a
        # companion) must still hold its number so it is never re-issued
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-login.md").write_text(
                "# US0001 - Login\n\nStatus: Draft\n", encoding="utf-8")  # off-template
            self.assertEqual(next_id.local_ids("story", root), [1])
            self.assertEqual(next_id.allocate_number("story", root), 2)


class AllocateTests(unittest.TestCase):
    def test_cli_allocate_matches_library_and_skips_lingering_index_row(self) -> None:
        # BG0060: the `allocate` CLI must not re-issue an id whose file was deleted but
        # whose index row remains - the CLI must agree with allocate_number (one authority).
        import io
        import json
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "change-requests"
            sd.mkdir(parents=True)
            (sd / "_index.md").write_text(
                "# Index\n\n## All\n\n| ID | Title | Status | Priority | Type | Date | Linked Epics |\n"
                "| --- | --- | --- | --- | --- | --- | --- |\n"
                "| [CR-0005](CR0005-x.md) | gone | Complete | Medium | Feature | 2026-01-01 | - |\n",
                encoding="utf-8")  # row present, file absent
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = next_id.main(["allocate", "--type", "cr", "--root", str(d), "--format", "json"])
            self.assertEqual(rc, 0)
            cli_next = json.loads(buf.getvalue())["next_id"]
            lib_next = f"CR{next_id.allocate_number('cr', root, remote=False):04d}"
            self.assertEqual(cli_next, "CR0006")     # above the lingering row, not CR0001
            self.assertEqual(cli_next, lib_next)      # CLI == library authority

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

    def test_remote_ids_reports_absent_where_there_is_no_origin(self) -> None:
        # A directory that is not a checkout has no origin to read, so silence is correct
        # and allocation carries on locally - the case the tri-state must NOT warn about.
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(next_id.remote_ids("cr", Path(d)), ([], next_id.REMOTE_ABSENT))

    def test_remote_ahead_id_not_reissued(self) -> None:
        import os, shutil, subprocess
        if shutil.which("git") is None:
            self.skipTest("git not available")
        env = gitutil.git_env()  # host config neutralised (gpgsign-safe)
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


class RemoteScanHonestyTests(unittest.TestCase):
    """BG0326: 'there is no origin' and 'the origin scan FAILED' are different answers.

    Collapsing them made a failed remote read degrade to a local-only allocation with no
    signal anywhere, which re-issues an id origin already holds - the LL0002 collision
    class, minted by the one tool whose job is to prevent it.
    """

    def _repo_with_unreachable_origin(self, d: Path) -> Path:
        """A checkout whose `origin` is configured but whose origin/<branch> is not there:
        the never-fetched / bad-remote case, indistinguishable from success before the fix."""
        import subprocess
        repo = d / "repo"
        (repo / "sdlc-studio" / "change-requests").mkdir(parents=True)
        (repo / "sdlc-studio" / "change-requests" / "CR0001-x.md").write_text(
            "# CR0001: x\n\n> **Status:** Done\n", encoding="utf-8")
        env = gitutil.git_env()
        for args in (["init", "-q", "-b", "main"],
                     ["remote", "add", "origin", str(d / "nowhere.git")]):
            subprocess.run(["git", *args], cwd=str(repo), check=True,
                           capture_output=True, env=env)
        return repo

    def _repo_without_origin(self, d: Path) -> Path:
        import subprocess
        repo = d / "solo"
        (repo / "sdlc-studio" / "change-requests").mkdir(parents=True)
        (repo / "sdlc-studio" / "change-requests" / "CR0001-x.md").write_text(
            "# CR0001: x\n\n> **Status:** Done\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=str(repo), check=True,
                       capture_output=True, env=gitutil.git_env())
        return repo

    def setUp(self) -> None:
        import shutil
        if shutil.which("git") is None:
            self.skipTest("git not available")

    def test_failed_scan_is_distinguished_from_no_origin(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.assertEqual(next_id.remote_ids("cr", self._repo_with_unreachable_origin(root))[1],
                             next_id.REMOTE_FAILED)
            self.assertEqual(next_id.remote_ids("cr", self._repo_without_origin(root))[1],
                             next_id.REMOTE_ABSENT)

    def test_failed_scan_warns_loudly_on_the_library_path(self) -> None:
        # artifact.py allocates through allocate_number, so the warning has to live here:
        # the mandated creation path never touches the CLI.
        import io
        from contextlib import redirect_stderr
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo_with_unreachable_origin(Path(d))
            err = io.StringIO()
            with redirect_stderr(err):
                self.assertEqual(next_id.allocate_number("cr", repo, remote=True), 2)
            self.assertIn("origin", err.getvalue())
            self.assertIn("LOCAL", err.getvalue())

    def test_no_origin_allocates_in_silence(self) -> None:
        import io
        from contextlib import redirect_stderr
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo_without_origin(Path(d))
            err = io.StringIO()
            with redirect_stderr(err):
                self.assertEqual(next_id.allocate_number("cr", repo, remote=True), 2)
            self.assertEqual(err.getvalue(), "")

    def test_strict_refuses_to_allocate_on_a_failed_scan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo_with_unreachable_origin(Path(d))
            with self.assertRaises(next_id.RemoteScanError):
                next_id.allocate_number("cr", repo, remote=True, strict=True)
            # ... and strict is not a blanket refusal: a repo with nothing to scan is fine.
            solo = self._repo_without_origin(Path(d))
            self.assertEqual(next_id.allocate_number("cr", solo, remote=True, strict=True), 2)

    def test_git_absent_counts_as_failed_not_absent(self) -> None:
        # With no git we cannot rule out an origin holding ids, and an unanswerable question
        # is not a clean answer.
        from unittest import mock
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(next_id.subprocess, "run", side_effect=FileNotFoundError):
                self.assertEqual(next_id.remote_ids("cr", Path(d))[1], next_id.REMOTE_FAILED)

    def test_cli_text_mode_warns_and_strict_exits_non_zero(self) -> None:
        import io
        import json as _json
        from contextlib import redirect_stderr, redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo_with_unreachable_origin(Path(d))
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                rc = next_id.main(["allocate", "--type", "cr", "--remote", "--root", str(repo)])
            self.assertEqual(rc, 0)
            self.assertEqual(out.getvalue().strip(), "CR0002")
            self.assertIn("origin", err.getvalue())
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                rc = next_id.main(["allocate", "--type", "cr", "--remote", "--root", str(repo),
                                   "--format", "json"])
            payload = _json.loads(out.getvalue())
            self.assertEqual(payload["remote_state"], next_id.REMOTE_FAILED)
            self.assertFalse(payload["remote_available"])
            self.assertIn("origin", payload["warning"])  # JSON consumers see it too
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                rc = next_id.main(["allocate", "--type", "cr", "--remote", "--root", str(repo),
                                   "--strict"])
            self.assertNotEqual(rc, 0)


class ArchiveUnionTests(unittest.TestCase):
    """US0041 / CR0125: next_id must union the archive sub-indexes so an archived id is
    never re-issued, even after its artefact file is removed."""

    def _index(self, d: Path, rows: str) -> None:
        d.mkdir(parents=True, exist_ok=True)
        (d / "_index.md").write_text(
            "# Stories\n\n| ID | Title | Status |\n| --- | --- | --- |\n" + rows,
            encoding="utf-8")

    def test_next_id_unions_archive(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            sd = root / "sdlc-studio" / "stories"
            self._index(sd, "| [US0001](US0001-a.md) | A | Draft |\n")
            self._index(sd / "archive", "| [US0007](US0007-g.md) | G | Done |\n")
            ids = next_id.index_row_ids("story", root)
            self.assertIn(7, ids)  # archived row is seen
            self.assertGreater(next_id.allocate_number("story", root, remote=False), 7)

    def test_next_id_archived_id_not_reused(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            sd = root / "sdlc-studio" / "stories"
            # only the archive row remains; the artefact file is gone
            self._index(sd, "| [US0001](US0001-a.md) | A | Draft |\n")
            self._index(sd / "archive", "| [US0009](US0009-i.md) | I | Superseded |\n")
            (sd / "US0001-a.md").write_text("# A\n\n> **Status:** Draft\n", encoding="utf-8")
            self.assertNotEqual(next_id.allocate_number("story", root, remote=False), 9)
            self.assertEqual(next_id.allocate_number("story", root, remote=False), 10)


class RootAnchoringTests(unittest.TestCase):
    """The allocator is the collision case for a bare `Path(args.root)`: run from a
    subdirectory with no `--root`, it read an EMPTY tree and minted an id the workspace above
    it already holds. It must resolve upward to the real workspace instead."""

    def test_allocation_from_a_subdirectory_sees_the_real_workspace(self) -> None:
        import io
        import json
        import os
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            _make_stories(root, [1, 383])
            sub = root / ".claude" / "skills" / "sdlc-studio" / "scripts"
            sub.mkdir(parents=True)
            here = Path.cwd()
            os.chdir(sub)
            try:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = next_id.main(["allocate", "--type", "story", "--format", "json"])
            finally:
                os.chdir(here)
            self.assertEqual(rc, 0)
            allocated = json.loads(buf.getvalue())
            self.assertEqual(allocated["next_id"], "US0384")  # not US0001 off an empty cwd
            self.assertEqual(allocated["local_max"], 383)


class MetaIdWidthTests(unittest.TestCase):
    """BG0338: a meta id past 9999 must read back WHOLE.

    The meta reader matched at most four digits, so RETRO10000 read back as 1000 - the
    allocator then allocated over ids that already exist. `sdlc_md.id_number` was widened
    to 4-7 digits for exactly this class; the meta reader was left behind."""

    def _write(self, root: Path, rel: str, stems: list[str]) -> Path:
        d = root / rel
        d.mkdir(parents=True, exist_ok=True)
        for s in stems:
            (d / f"{s}.md").write_text(f"# {s}\n", encoding="utf-8")
        return d

    def test_five_digit_meta_id_reads_back_whole(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._write(root, "sdlc-studio/retros", ["RETRO10000-x"])
            self.assertEqual(next_id.local_ids("retro", root), [10000])

    def test_allocation_above_a_five_digit_id_does_not_re_mint_a_live_id(self) -> None:
        # RETRO10000 truncated to 1000, so the allocator handed back 1001 - the number
        # RETRO01001 already holds. Two files, one id.
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._write(root, "sdlc-studio/retros", ["RETRO10000-a", "RETRO01001-b"])
            taken = set(next_id.local_ids("retro", root))
            allocated = next_id.allocate_number("retro", root, remote=False)
            self.assertNotIn(allocated, taken)
            self.assertEqual(allocated, 10001)

    def test_seven_digit_meta_id_matches_id_number_range(self) -> None:
        # The upper bound is id_number's, so the two readers agree on the same id.
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._write(root, "sdlc-studio/reviews", ["RV1234567-x"])
            self.assertEqual(next_id.local_ids("review", root), [1234567])
            self.assertEqual(next_id.sdlc_md.id_number("RV1234567"), 1234567)

    def test_a_digit_run_past_the_range_is_ignored_not_truncated(self) -> None:
        # Widening the cap without refusing a longer run just moves the truncation: an
        # eight-digit stem would read back as its first seven digits - a number no file
        # holds, and one that would drag every later allocation up with it. id_number
        # returns None there, and so must this reader.
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._write(root, "sdlc-studio/retros", ["RETRO12345678-x", "RETRO0004-y"])
            self.assertEqual(next_id.local_ids("retro", root), [4])
            self.assertIsNone(next_id.sdlc_md.id_number("RETRO12345678"))

    def test_four_digit_ids_are_unaffected(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._write(root, "sdlc-studio/handoffs", ["HO0007-x", "HO-0009-y"])
            self.assertEqual(next_id.local_ids("handoff", root), [7, 9])
            self.assertEqual(next_id.allocate_number("handoff", root, remote=False), 10)


if __name__ == "__main__":
    unittest.main()
