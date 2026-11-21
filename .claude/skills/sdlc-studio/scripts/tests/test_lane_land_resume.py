"""`sprint lane land --resume` takes a stopped landing up from the step its land record names.

Every case drives `sprint.py lane land` through its entry point against the throwaway repository
`test_lane_land` builds: a stub pre-commit hook that logs the checkout it ran in and refuses any
commit staging a file under `src/refuse`, and units real enough for `critic.py self-check record`
and `critic.py brief --seat qa` to run under `review.author_self_check: block`. A hook is
"cleared" by rewriting it to pass, as a repair would leave it.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/lanes.py
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import test_lane_land as lane_land  # noqa: E402 - the fixture repository, its hook and its lane

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from lib import lanes  # noqa: E402

A, B, LANE, REFUSAL = lane_land.A, lane_land.B, lane_land.LANE, lane_land.REFUSAL
_git, _write, critic = lane_land._git, lane_land._write, lane_land.critic
#: the hook a repair leaves: it still logs the checkout it ran in, and refuses nothing
CLEARED = "#!/bin/sh\ngit rev-parse --show-toplevel >> \"{log}\"\nexit 0\n"


class LaneLandResumeTests(lane_land._LaneFixture):

    def _resume(self, *units: str, worktree: Path | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-B", str(lane_land.SPRINT), "lane", "land", "--resume",
             "--worktree", str(worktree or self.wt), "--units", *units, "--root", str(self.root)],
            capture_output=True, text=True, timeout=600, cwd=str(self.root), env=self._env(),
            check=False)

    def _clear_the_hook(self) -> None:
        hook = self.root.parent / "hooks" / "pre-commit"
        hook.write_text(CLEARED.format(log=self.log), encoding="utf-8")

    def _keep(self, wt: Path | None = None) -> Path:
        return self.root / lanes.LANDED / (wt or self.wt).name

    def _record(self, wt: Path | None = None) -> dict:
        path = self.root / lanes.LANDED / lanes.LAND_RECORD.format(name=(wt or self.wt).name)
        return json.loads(path.read_text(encoding="utf-8"))

    def _brief(self, unit: str) -> Path:
        return self.root / lanes.BRIEFS / f"{unit}-qa.txt"

    def _snapshot(self) -> dict:
        """main's head, every kept file's bytes and every brief's bytes and inode."""
        landed = self.root / lanes.LANDED
        files = {str(p.relative_to(landed)): p.read_bytes()
                 for p in sorted(landed.rglob("*")) if p.is_file()} if landed.is_dir() else {}
        briefs = self.root / lanes.BRIEFS
        held = {p.name: (p.read_bytes(), p.stat().st_ino)
                for p in sorted(briefs.glob("*"))} if briefs.is_dir() else {}
        return {"head": _git(self.root, "rev-parse", "HEAD"), "landed": files, "briefs": held}

    def _refused_first(self) -> str:
        """A lane whose first landing the hook refused: main's head before it."""
        head = _git(self.root, "rev-parse", "HEAD")
        self._stage("src/a.py", "A = 2\n")
        self._stage("src/refuse.py", "X = 1\n")
        self._hand_in()
        r = self._land(A)
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn(REFUSAL, r.stderr)
        return head

    def test_a_refused_commit_resumes_with_one_commit_and_the_kept_hand_in(self) -> None:
        head = self._refused_first()
        keep = self._keep()
        kept = {p.name: p.read_bytes() for p in keep.iterdir() if p.name != "commit.log"}
        # a copy made again would empty the kept hand-in and take these from the worktree
        marker = keep / "kept.marker"
        marker.write_text("the first attempt's\n", encoding="utf-8")
        for name in lanes.hand_in_names(A):
            (self.wt / LANE / name).unlink()
        self._clear_the_hook()
        r = self._resume(A)
        out = r.stdout + r.stderr
        self.assertEqual(0, r.returncode, out)
        self.assertNotIn("hand-in copied", out, "the resume copied the hand-in again")
        self.assertEqual("1", _git(self.root, "rev-list", "--count", f"{head}..HEAD"),
                         "the resume did not land exactly one commit")
        self.assertEqual(f"feat({A}): a is two", _git(self.root, "log", "-1", "--format=%s"))
        self.assertTrue(marker.is_file(), "the resume emptied the kept hand-in")
        for name, body in kept.items():
            self.assertEqual(body, (keep / name).read_bytes(), f"the kept {name} was rewritten")
        rows = critic.read_self_checks(self.root)
        self.assertEqual([A], [row["unit"] for row in rows], out)
        self.assertTrue(_git(self.root, "rev-parse", "HEAD").startswith(rows[0]["commit"]))
        self.assertTrue(self._brief(A).is_file(), "no QA brief was written from the kept hand-in")
        self.assertFalse((self.root / lanes.BRIEFS / lanes.NO_BRIEF.format(unit=A)).exists())
        self.assertFalse(self.wt.exists(), "the resumed landing did not remove the worktree")

    def test_a_landing_stopped_after_the_fast_forward_resumes_without_its_worktree(self) -> None:
        for rel, body in (("src/a.py", "A = 2\n"), (f"changelog.d/{A}.md", "a is two\n"),
                          ("src/b.py", "B = 2\n"), (f"changelog.d/{B}.md", "b is two\n")):
            self._stage(rel, body)
        self._hand_in(units=(A, B), message=f"feat({A}): a and b are two")
        claims = self.wt / LANE / f"{B}-claims.json"
        whole = claims.read_text(encoding="utf-8")
        # B's hand-in carries no claims file: a self-check the critic would refuse is refused
        # before the commit, so the one stop left after the fast-forward is a self-check the
        # landing could not record at all
        claims.unlink()
        r = self._land(A, B)
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"{B}: self-check NOT RECORDED", r.stderr)
        self.assertEqual("self-check", self._record()["stopped_at"])
        self.assertFalse(self.wt.exists(), "the first landing did not remove the worktree")
        head, briefed = _git(self.root, "rev-parse", "HEAD"), self._brief(A).stat()
        self.assertFalse(self._brief(B).exists())
        (self._keep() / f"{B}-claims.json").write_text(whole, encoding="utf-8")
        r = self._resume(A, B)
        out = r.stdout + r.stderr
        self.assertEqual(0, r.returncode, out)
        self.assertEqual(head, _git(self.root, "rev-parse", "HEAD"), "the resume committed again")
        rows = [row["unit"] for row in critic.read_self_checks(self.root)]
        self.assertEqual([A, B], rows, "a unit's self-check was not recorded exactly once")
        self.assertTrue(self._brief(B).is_file(), f"{B}'s QA brief was not written")
        self.assertFalse((self.root / lanes.BRIEFS / lanes.NO_BRIEF.format(unit=B)).exists())
        now = self._brief(A).stat()
        self.assertEqual((briefed.st_ino, briefed.st_mtime_ns), (now.st_ino, now.st_mtime_ns),
                         f"{A}'s brief, already written, was rewritten")

    def test_a_resume_with_no_stopped_landing_is_refused(self) -> None:
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        r = self._land(A)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        before = self._snapshot()
        for wt in (self.wt, self.wt.parent / "lane-never-landed"):
            with self.subTest(worktree=wt.name):
                r = self._resume(A, worktree=wt)
                self.assertEqual(2, r.returncode, r.stdout + r.stderr)
                self.assertIn(f"there is no stopped landing of {wt.name} to resume", r.stderr)
                self.assertEqual(before, self._snapshot(), "a refused resume changed something")
        fresh = self.wt.parent / "lane-us0102"
        gitutil.git(["worktree", "add", "-q", "-b", "lane-us0102", str(fresh), "main"],
                    self.root)
        self.wt = fresh
        self._stage("src/b.py", "B = 2\n")
        self._hand_in(units=(B,), message=f"feat({B}): b is two")
        r = self._land(B)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual("B = 2\n", (self.root / "src/b.py").read_text(encoding="utf-8"))

    def test_each_landing_records_the_steps_it_completed(self) -> None:
        self._refused_first()
        record = self._record()
        self.assertEqual(([self.wt.name], [A], ["hand-in"], "commit", None),
                         (record["worktrees"], record["units"], record["completed"],
                          record["stopped_at"], record["commit"]))
        self._clear_the_hook()
        r = self._resume(A)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"resuming the landing of {self.wt.name} from its commit step", r.stdout)
        record = self._record()
        self.assertEqual((list(lanes.LAND_STEPS), None, _git(self.root, "rev-parse", "HEAD")),
                         (record["completed"], record["stopped_at"], record["commit"]))
        fresh = self.wt.parent / "lane-us0102"
        gitutil.git(["worktree", "add", "-q", "-b", "lane-us0102", str(fresh), "main"],
                    self.root)
        self.wt = fresh
        self._stage("src/b.py", "B = 2\n")
        self._hand_in(units=(B,), message=f"feat({B}): b is two")
        r = self._land(B)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        record = self._record(fresh)
        self.assertEqual(([fresh.name], [B], list(lanes.LAND_STEPS), None,
                          _git(self.root, "rev-parse", "HEAD")),
                         (record["worktrees"], record["units"], record["completed"],
                          record["stopped_at"], record["commit"]))

    def test_a_refused_landing_of_two_worktrees_resumes_as_one_commit(self) -> None:
        """The resume of a landing of several worktrees: the refused commit took the second
        worktree's change back out of the first, so the resume combines them again and commits
        once, each unit briefed from its own kept hand-in."""
        head = _git(self.root, "rev-parse", "HEAD")
        second = self.wt.parent / "lane-us0102"
        gitutil.git(["worktree", "add", "-q", "-b", "lane-us0102", str(second), "main"],
                    self.root)
        self._stage("src/a.py", "A = 2\n")
        self._stage("src/refuse.py", "X = 1\n")
        self._hand_in()
        first, self.wt = self.wt, second
        self._stage("src/b.py", "B = 2\n")
        self._stage(f"changelog.d/{B}.md", "b is two\n")
        self._hand_in(units=(B,), message=f"feat({B}): b is two")
        self.wt = first
        both = ["--worktree", str(first), "--worktree", str(second), "--units", A, B,
                "--root", str(self.root)]

        def land(*extra: str) -> subprocess.CompletedProcess:
            return subprocess.run([sys.executable, "-B", str(lane_land.SPRINT), "lane", "land",
                                   *extra, *both], capture_output=True, text=True, timeout=600,
                                  cwd=str(self.root), env=self._env(), check=False)

        r = land()
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertEqual("commit", self._record()["stopped_at"])
        self._clear_the_hook()
        r = land("--resume")
        out = r.stdout + r.stderr
        self.assertEqual(0, r.returncode, out)
        self.assertEqual("1", _git(self.root, "rev-list", "--count", f"{head}..HEAD"), out)
        self.assertEqual([A, B], _git(self.root, "log", "-1",
                                      "--format=%(trailers:key=Refs,valueonly)").splitlines())
        self.assertEqual(sorted([A, B]), sorted(row["unit"]
                                                for row in critic.read_self_checks(self.root)))
        for unit in (A, B):
            self.assertTrue(self._brief(unit).is_file(), f"no QA brief for {unit}")
        for wt in (first, second):
            self.assertFalse(wt.exists(), f"{wt.name} was not removed")


if __name__ == "__main__":
    unittest.main()
