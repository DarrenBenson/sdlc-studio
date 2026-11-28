"""`sprint drive` runs a wave's independent units in parallel and stops at a warning, a conflict
or the wave end.

The fixture is `test_sprint_drive`'s: a throwaway repository with an open run, a stub pre-commit
hook and a stub `claude` that builds and reviews, logging when each session starts and ends. The
plan's waves are written where `sprint plan --write` keeps them. Three cases wrap the step runner,
`drive.run_script`, to add a WARNING line to one unit's green `lane accept`.

Two cases ask real git whether a root read takes `.git/index.lock`: git rewrites the index after
a read such as `git status` only while it holds that lock, so a read made after a tracked file's
mtime moved rewrites the index exactly when it took the lock.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/drive.py
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import threading
import time
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_sprint_drive as walk
from lib import drive, lanes

A, B, C = walk.A, walk.B, walk.C
SKILL = walk.SKILL
#: a tracked file under `sdlc-studio/`, in no unit's Affects, whose mtime a lock probe moves
TOUCH = "sdlc-studio/personas/seats/qa.md"
#: seconds a parked step waits for the other unit before it goes on regardless
WAIT = 60
#: a `claude` in front of the fixture's stub: each session first reads the root with the git
#: environment it was given and logs whether that read rewrote the root's index
PROBE = """#!__PYTHON__
import json, os, re, subprocess, sys, time
from pathlib import Path
root, log, stub = Path(__ROOT__), Path(__LOG__), __STUB__
genv = {k: v for k, v in os.environ.items() if k not in __LOCATING__}
prompt = sys.argv[sys.argv.index("-p") + 1]
role = "control" if prompt == "control" else "review" \\
    if re.search(r"^/.*/sdlc-studio/reviews/verdicts/.+[.]txt$", prompt, re.M) else "build"
index, at = root / ".git" / "index", time.time_ns() + 5_000_000_000
os.utime(root / __TOUCH__, ns=(at, at))
before = index.stat()
subprocess.run(["git", "-C", str(root), "status", "--porcelain"], env=genv, check=True,
               capture_output=True)
after = index.stat()
with log.open("a") as fh:
    fh.write(json.dumps({"role": role, "rewrote_index": (before.st_ino, before.st_mtime_ns)
                         != (after.st_ino, after.st_mtime_ns)}) + "\\n")
if role == "control":
    sys.exit(0)
os.execv(stub, [stub, *sys.argv[1:]])
"""


def _rewrites_index(root: Path, run):
    """(what `run` returned, whether it rewrote `root`'s index): `TOUCH`'s mtime is moved first,
    so a git read that takes the index's optional lock refreshes it and writes the index back."""
    index, at = root / ".git" / "index", time.time_ns() + 5_000_000_000
    os.utime(root / TOUCH, ns=(at, at))
    before = index.stat()
    said = run()
    after = index.stat()
    return said, (before.st_ino, before.st_mtime_ns) != (after.st_ino, after.st_mtime_ns)


def _sessions(case, unit: str, event: str) -> list[dict]:
    return [s for s in case.sessions() if s["unit"] == unit and s.get("event") == event]


def _files(unit: str, *rels: str) -> dict:
    return {**{rel: f"{unit} = 2\n" for rel in rels}, f"changelog.d/{unit}.md": "x\n"}


class _Parallel(walk._DriveFixture):  # noqa: SLF001
    UNITS = {A: ["src/a.py"], B: ["src/b.py"], C: ["src/a.py", "src/c.py"]}
    WAVES = [[A, B, C]]


class _Pair(walk._DriveFixture):  # noqa: SLF001
    UNITS = {A: ["src/a.py"], B: ["src/b.py"]}
    WAVES = [[A, B]]


class _SlowPair(_Pair):
    #: every commit takes a while, so the second build is done while the first still lands
    HOOK_SLEEP = 2


class SprintDriveWaveTests(walk._DriveFixture):  # noqa: SLF001
    UNITS = {A: ["src/a.py"], B: ["src/b.py"]}
    WAVES = [[A], [B]]

    def _case(self, fixture: type, name: str) -> walk._DriveFixture:
        case = fixture(name)
        case.setUp()
        self.addCleanup(case.tearDown)
        return case

    def test_disjoint_units_build_together_and_a_shared_file_waits(self) -> None:
        case = self._case(_Parallel, "run")
        case.spec({A: {"files": _files(A, "src/a.py"), "sleep": 2},
                   B: {"files": _files(B, "src/b.py"), "sleep": 2},
                   C: {"files": _files(C, "src/c.py"), "probe": "src/a.py"}})
        rc, out, err = case.drive()
        self.assertEqual(0, rc, out + err)
        start = {u: _sessions(case, u, "start")[0] for u in (A, B, C)}
        end = {u: _sessions(case, u, "end")[0]["at"] for u in (A, B, C)}
        # the two disjoint builds overlap in time
        self.assertLess(start[A]["at"], end[B], "B's build ended before A's began")
        self.assertLess(start[B]["at"], end[A], "A's build ended before B's began")
        # the unit sharing src/a.py started after A's build, from a worktree holding A's landing
        self.assertGreaterEqual(start[C]["at"], end[A])
        self.assertEqual(f"{A} = 2\n", start[C]["probe"],
                         "C was built from a tree without A's landing")
        landed = case.subjects()
        for unit in (A, B, C):
            self.assertIn(f"feat({unit}): {unit} lands", landed)
            self.assertEqual("Done", case.status_at(unit))

    def test_a_warning_on_a_green_step_stops_the_unit(self) -> None:
        case = self._case(_Pair, "run")
        warning = "WARNING the verdict was taken against an earlier Affects scope"

        def warn(real, root, script, *args, **kw):
            done = real(root, script, *args, **kw)
            if args[:2] == ("lane", "accept") and B in args and done.returncode == 0:
                done = subprocess.CompletedProcess(done.args, 0, done.stdout,
                                                   done.stderr + warning + "\n")
            return done

        rc, out, err = case.drive(wrap=warn)
        self.assertNotEqual(0, rc, out + err)
        text = "\n".join(case.record_of(out))
        self.assertIn(f"DRIVE STOPPED: {B} at accept, {drive.WARNED}", text)
        self.assertIn(warning, text)
        self.assertNotIn(f"{B} return: ", out)
        self.assertNotIn(f"{B} paperwork: ", out)
        subjects = case.subjects()
        self.assertFalse([s for s in subjects if s.startswith(f"docs({B})")], subjects)
        self.assertNotEqual("Done", case.status_at(B), "B's move was committed past the warning")
        # the wave's other unit is not left half landed: it walked to its paperwork
        self.assertIn(f"{A} paperwork: committed", out)
        self.assertEqual("Done", case.status_at(A))
        self.assertTrue([s for s in subjects if s.startswith(f"docs({A})")], subjects)

    def test_a_root_read_beside_a_paperwork_commit_holds_no_index_lock(self) -> None:
        """B's green accept warns, so B's walk reads the root's status for the resume it names,
        outside the root lock, while A walks on to its paperwork commit. A read that took the
        index's lock is made to hold it until A's walk ends, as one under load can; a read that
        took none holds nothing, and A's commit must land."""
        case = self._case(_Pair, "run")
        warning = "WARNING the verdict was taken against an earlier Affects scope"
        lock = case.root / ".git" / "index.lock"
        read, ended, seen = threading.Event(), threading.Event(), []
        real_git, real_review, real_walk = lanes._git, drive._review, drive._walk  # noqa: SLF001

        def warn(real, root, script, *args, **kw):
            done = real(root, script, *args, **kw)
            if args[:2] == ("lane", "accept") and B in args and done.returncode == 0:
                done = subprocess.CompletedProcess(done.args, 0, done.stdout,
                                                   done.stderr + warning + "\n")
            return done

        def git(cwd, *args, **kw):
            if (threading.current_thread().name != f"drive-{B}" or "status" not in args
                    or read.is_set()):
                return real_git(cwd, *args, **kw)
            said, locked = _rewrites_index(case.root, lambda: real_git(cwd, *args, **kw))
            seen.append(locked)
            held = False
            if locked:
                os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
                held = True
            read.set()
            try:
                ended.wait(WAIT)
            finally:
                if held:
                    lock.unlink()
            return said

        def review(w, unit, ctx):
            if unit == A:  # A's review waits for B's read, so A commits while B reads
                read.wait(WAIT)
            return real_review(w, unit, ctx)

        def walked(w, unit):
            try:
                real_walk(w, unit)
            finally:
                if unit == A:
                    ended.set()

        with unittest.mock.patch.object(lanes, "_git", git), \
                unittest.mock.patch.object(drive, "_review", review), \
                unittest.mock.patch.object(drive, "_walk", walked):
            rc, out, err = case.drive(wrap=warn)
        self.assertIn(f"{A} paperwork: committed", out, out + err)
        self.assertEqual([False], seen, "B's root read took the index lock")
        self.assertNotEqual(0, rc, out + err)
        self.assertIn(f"DRIVE STOPPED: {B} at accept, {drive.WARNED}", out)
        self.assertEqual("Done", case.status_at(A))
        self.assertFalse(lock.exists())
        # the control: the same read with git's optional locks on rewrites the index
        env = {k: v for k, v in case.env.items() if k != "GIT_OPTIONAL_LOCKS"}
        _, locked = _rewrites_index(case.root, lambda: subprocess.run(
            ["git", "status", "--porcelain", "--", "sdlc-studio"], cwd=case.root, env=env,
            check=True, capture_output=True))
        self.assertTrue(locked, "the probe cannot see a read that takes the index lock")

    def test_the_build_and_review_sessions_read_the_root_without_its_index_lock(self) -> None:
        stub = self.base / "bin" / "claude-stub"
        (self.base / "bin" / "claude").rename(stub)
        log = self.base / "locks.log"
        probe = PROBE
        for key, value in (("__PYTHON__", sys.executable), ("__ROOT__", repr(str(self.root))),
                           ("__LOG__", repr(str(log))), ("__STUB__", repr(str(stub))),
                           ("__LOCATING__", repr(walk.gitutil.REPO_LOCATING_GIT_VARS)),
                           ("__TOUCH__", repr(TOUCH))):
            probe = probe.replace(key, value)
        walk._write(self.base, "bin/claude", probe).chmod(0o755)  # noqa: SLF001
        rc, out, err = self.drive()
        self.assertEqual(0, rc, out + err)
        said = [json.loads(ln) for ln in log.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([{"role": "build", "rewrote_index": False},
                          {"role": "review", "rewrote_index": False}], said)
        # the control: the probe's own read, with git's optional locks on, rewrites the index
        env = {k: v for k, v in self.env.items() if k != "GIT_OPTIONAL_LOCKS"}
        subprocess.run([str(self.base / "bin" / "claude"), "-p", "control"], env=env,
                       check=True, capture_output=True)
        self.assertEqual({"role": "control", "rewrote_index": True},
                         json.loads(log.read_text(encoding="utf-8").splitlines()[-1]),
                         "the probe cannot see a read that takes the index lock")

    def test_a_warning_at_accept_holds_the_drive_until_it_is_answered(self) -> None:
        warning = "WARNING the verdict was taken against an earlier Affects scope"

        def warn(real, root, script, *args, **kw):
            done = real(root, script, *args, **kw)
            if args[:2] == ("lane", "accept") and A in args and done.returncode == 0:
                done = subprocess.CompletedProcess(done.args, 0, done.stdout,
                                                   done.stderr + warning + "\n")
            return done

        rc, out, err = self.drive(wrap=warn)
        self.assertEqual(1, rc, out + err)
        text = "\n".join(self.record_of(out))
        self.assertIn(f"DRIVE STOPPED: {A} at accept, {drive.WARNED}", text)
        resume = re.search(r"^  resume: (.+)$", text, re.M).group(1)
        self.assertNotIn("lane accept", resume, "the record names an accept already made")
        self.assertEqual(self.STATUS, self.status_at(A))
        # re-run unanswered, the drive stops on the same unit and starts no later wave
        rc, out, err = self.drive()
        self.assertEqual(1, rc, out + err)
        self.assertIn(f"DRIVE STOPPED: {A} at paperwork, {drive.REFUSAL}", out)
        self.assertIn("uncommitted", out)
        self.assertEqual([], _sessions(self, B, "start"), "the next wave drove past the stop")
        self.assertEqual(self.STATUS, self.status_at(A))
        # the answer is the command the first record named, which commits only the unit's
        # paperwork; the drive then resumes
        command = resume.split(", then ")[0]
        walk._write(self.root, "src/c.py", "C = 9\n")  # noqa: SLF001
        walk.gitutil.git(["add", "--", "src/c.py"], self.root)
        subprocess.run(command, shell=True, cwd=self.root, env=self.env, check=True,
                       capture_output=True)
        self.assertEqual("Done", self.status_at(A))
        self.assertEqual([], [ln for ln in self.dirty() if A in ln])
        self.assertNotIn("src/c.py", walk._git(  # noqa: SLF001
            self.root, "show", "--name-only", "--format=", "HEAD").splitlines())
        walk.gitutil.git(["reset", "-q", "--", "src/c.py"], self.root)
        walk.gitutil.git(["checkout", "--", "src/c.py"], self.root)
        rc, out, err = self.drive()
        self.assertEqual(0, rc, out + err)
        self.assertIn(f"DRIVE STOPPED: wave 2 of 2 ended, {drive.WAVE_END}", out)
        self.assertEqual("Done", self.status_at(B))

    def test_a_rebase_conflict_stops_the_wave_and_keeps_the_first_landing(self) -> None:
        case = self._case(_SlowPair, "run")
        case.spec({A: {"files": _files(A, "src/a.py", "src/shared.py")},
                   B: {"files": _files(B, "src/b.py", "src/shared.py"), "sleep": 1}})
        rc, out, err = case.drive()
        self.assertNotEqual(0, rc, out + err)
        text = "\n".join(case.record_of(out))
        self.assertIn(f"DRIVE STOPPED: {B} at land, {drive.CONFLICT}", text)
        self.assertIn("conflicting files: src/shared.py", text)
        self.assertLessEqual(len(case.record_of(out)), drive.RECORD_LINES + 2)
        # the first landing stands, and the root's branch is as that landing left it: the
        # first unit is held before its accept, or, accepted already, has its paperwork
        # committed; never moved and left uncommitted, and nothing of the second unit landed
        subjects = case.subjects()
        self.assertNotIn(f"feat({B}): {B} lands", subjects)
        if f"{A}: held before its" in out:
            self.assertEqual(f"feat({A}): {A} lands", subjects[0])
            self.assertEqual(case.STATUS, case.status_at(A, "HEAD"))
        else:
            self.assertEqual([f"docs({A}): record {A}'s review and its move to Done",
                              f"feat({A}): {A} lands"], subjects[:2])
        self.assertEqual([], [ln for ln in case.dirty() if f"{A}-drive.md" in ln])
        git_dir = Path(walk._git(case.root, "rev-parse", "--absolute-git-dir"))  # noqa: SLF001
        for left in ("rebase-merge", "rebase-apply"):
            self.assertFalse((git_dir / left).exists(), f"the root was left mid-rebase: {left}")
            self.assertFalse(list(git_dir.glob(f"worktrees/*/{left}")),
                             f"the lane was left mid-rebase: {left}")
        self.assertEqual("", walk._git(case.root, "status", "--porcelain", "--", "src"))  # noqa: SLF001
        # the second lane's conflict is met replaying its staged change, before its commit: it
        # stays staged and uncommitted in its worktree; nothing was retried or forced
        wt = case.root / lanes.RUN_WORKTREES / f"lane-{B.lower()}"
        self.assertTrue(wt.is_dir())
        self.assertNotEqual(f"feat({B}): {B} lands", walk._git(wt, "log", "-1", "--format=%s"))  # noqa: SLF001
        self.assertIn("src/shared.py", walk._git(wt, "diff", "--cached", "--name-only").split())  # noqa: SLF001
        self.assertEqual(1, len(_sessions(case, B, "start")))
        # the conflict halts the wave, and a halted wave starts no unit still waiting, even one
        # whose earlier unit has landed
        said = "rebasing x onto main failed ... Conflicting files: src/shared.py. The lane stays"
        with self.assertRaises(drive._Stop) as stopped:  # noqa: SLF001
            drive._stop_for(case.root, B, "land", subprocess.CompletedProcess(  # noqa: SLF001
                ["land"], 1, "", said), "resume")
        self.assertTrue(stopped.exception.halt)
        wave, started = drive._Wave(case.root, "claude", None, None, [A, B]), []  # noqa: SLF001

        def first_lands_then_conflicts(w, unit):
            started.append(unit)
            w.halt.set()
            w.mark_landed(unit)

        with unittest.mock.patch.object(drive, "_walk", first_lands_then_conflicts), \
                unittest.mock.patch.object(drive, "_affects", lambda root, unit: {"src/x.py"}):
            never = drive._run_wave(wave)  # noqa: SLF001
        self.assertEqual(([A], [B]), (started, never))

    def test_the_wave_end_stops_drive_and_the_doctrine_names_the_stops(self) -> None:
        rc, out, err = self.drive()
        self.assertEqual(0, rc, out + err)
        record = self.record_of(out)
        self.assertEqual(f"DRIVE STOPPED: wave 1 of 2 ended, {drive.WAVE_END}", record[0])
        self.assertIn(f"  {A}: Done", record)
        self.assertLessEqual(len(record), drive.RECORD_LINES)
        self.assertEqual([], _sessions(self, B, "start"), "a unit of the next wave was built")
        self.assertFalse((self.root / lanes.RUN_RECORDS / B).exists())
        self.assertFalse((self.root / lanes.RUN_WORKTREES / f"lane-{B.lower()}").exists())
        self.assertNotEqual("Done", self.status_at(B))
        doctrine = (SKILL / "reference-doctrine.md").read_text(encoding="utf-8")
        habit = next(p for p in doctrine.split("\n1") if "sprint.py drive" in p)
        self.assertEqual(set(drive.STOPS), walk.stops_named(habit),
                         "the doctrine names other stops than the loop makes")
        # a record carries only a stop the loop makes
        with self.assertRaises(ValueError):
            drive.decision_record(A, "land", "a timeout")


if __name__ == "__main__":
    unittest.main()
