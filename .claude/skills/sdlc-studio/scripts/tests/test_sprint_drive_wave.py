"""`sprint drive` runs a wave's independent units in parallel and stops at a warning, a conflict
or the wave end.

The fixture is `test_sprint_drive`'s: a throwaway repository with an open run, a stub pre-commit
hook and a stub `claude` that builds and reviews, logging when each session starts and ends. The
plan's waves are written where `sprint plan --write` keeps them. One case wraps the step runner,
`drive.run_script`, to add a WARNING line to one unit's green `lane accept`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/drive.py
from __future__ import annotations

import subprocess
import sys
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_sprint_drive as walk
from lib import drive, lanes

A, B, C = walk.A, walk.B, walk.C
SKILL = walk.SKILL


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
        # the second lane stays committed in its worktree; nothing was retried or forced
        wt = case.root / lanes.RUN_WORKTREES / f"lane-{B.lower()}"
        self.assertTrue(wt.is_dir())
        self.assertEqual(f"feat({B}): {B} lands", walk._git(wt, "log", "-1", "--format=%s"))  # noqa: SLF001
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
