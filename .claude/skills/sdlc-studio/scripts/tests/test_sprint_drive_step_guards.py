"""The guards of `sprint drive` and `sprint drive step` that nothing pinned.

`drive step --after <id>` takes a reviewer's hand-back only from an agent that is not the unit's
builder and whose transcript names the verdict file its brief named. A re-run of `drive` after a
refused paperwork commit stops and names that commit. A review that cannot start exits 2 after
the build and the landing ran, and the help says so. The order of the steps, the return-step
stop, the landing lock and the hold on a unit sharing a file with one building each fail a test
here. The fixtures are `test_sprint_drive`'s and `test_sprint_drive_step`'s.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/drive.py
from __future__ import annotations

import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_sprint_drive as walk
import test_sprint_drive_step as stepped
from lib import drive, sdlc_md

A, B, C, D = stepped.A, stepped.B, stepped.C, stepped.D
#: The doctrine's order, written out, not read from `drive.STEPS`: a reorder there would
#: otherwise reorder this too.
ORDER = ("build", "land", "brief", "review", "accept", "return", "paperwork")


class DriveStepReviewerTests(stepped._StepFixture):  # noqa: SLF001

    def _landed_with_a_verdict(self) -> str:
        """A landed by builder a1, its verdict written by reviewer ra; the review prompt."""
        self.builder("a1", A, "A = 2\n")
        rc, out, err = self.step("a1")
        self.assertEqual(0, rc, out + err)
        self.verdict(A, stepped.APPROVE, by="ra")
        return (self.root / self.lanes()[sdlc_md.norm_id(A)]["prompt"]).read_text(
            encoding="utf-8")

    def _nothing_recorded(self, rc: int, out: str, err: str) -> None:
        self.assertNotEqual(0, rc, out + err)
        entry = self.lanes()[sdlc_md.norm_id(A)]
        self.assertEqual(("review", None), (entry["stage"], entry["reviewer"]), entry)
        ledger = walk.critic.verdicts_path(self.root)
        self.assertFalse(ledger.is_file() and self.rows(A), "a verdict was recorded")
        self.assertEqual(self.STATUS, self.status_at(A))

    def test_the_units_builder_is_refused_as_its_reviewer(self) -> None:
        prompt = self._landed_with_a_verdict()
        # even briefed with the review prompt, the author is no reviewer of its own unit: its
        # transcript names the verdict file, so only the builder check can refuse it
        self.briefed("a1", prompt)
        verdict = self.lanes()[sdlc_md.norm_id(A)]["verdict"]
        with unittest.mock.patch.dict(os.environ, self.env, clear=True):
            self.assertIsNone(drive._briefed(self.root, "a1", verdict))  # noqa: SLF001
        for extra in ((), ("--unit", A)):
            with self.subTest(extra=extra):
                rc, out, err = self.run_sprint("drive", "step", "--after", "a1", *extra)
                self.assertEqual(2, rc, out + err)
                self.assertIn("a1", err)
                self.assertIn("builder", err)
                self._nothing_recorded(rc, out, err)

    def test_a_transcript_is_read_for_the_verdict_files_own_name(self) -> None:
        """The plain path or its JSON-escaped form, in a transcript that need not be UTF-8; no
        verdict file at all is named by nothing."""
        verdict = self.root / "sdlc-studio" / "reviews" / "verdicts" / A / "café.txt"
        transcript = self.base / "agent-x.jsonl"
        with unittest.mock.patch.object(drive.run_state, "agent_transcript_tokens",
                                        return_value={"priced": 1, "source": str(transcript)}):
            transcript.write_bytes(b"\xff" + json.dumps({"content": str(verdict)}).encode())
            self.assertIsNone(drive._briefed(self.root, "x", str(verdict)))  # noqa: SLF001
            transcript.write_bytes(str(verdict).encode("utf-8"))
            self.assertIsNone(drive._briefed(self.root, "x", str(verdict)))  # noqa: SLF001
            for missing in ("", None):
                self.assertIn("does not name",
                              drive._briefed(self.root, "x", missing))  # noqa: SLF001

    def test_an_id_no_brief_names_is_refused(self) -> None:
        self._landed_with_a_verdict()
        # an agent of the session given some other prompt, which names no verdict file of A's
        self.briefed("other3", f"Unit: {B} - build it\n")
        for agent in ("nobody7", "other3"):
            with self.subTest(agent=agent):
                rc, out, err = self.step(agent)
                self.assertEqual(2, rc, out + err)
                self.assertIn(agent, err)
                self.assertIn("verdict file", err)
                self._nothing_recorded(rc, out, err)
        # the reviewer the brief reached is taken
        rc, out, err = self.step("ra")
        self.assertEqual(0, rc, out + err)
        self.assertIn("qa-seat-US0101-ra", self.rows(A)[-1])
        self.assertEqual("Done", self.status_at(A))


class DriveRerunAfterRefusedPaperworkTests(walk._DriveFixture):  # noqa: SLF001

    def test_a_rerun_after_a_refused_paperwork_commit_stops_naming_it(self) -> None:
        def refuse_after_accept(real, root, script, *args, **kw):
            done = real(root, script, *args, **kw)
            if args[:2] == ("lane", "accept"):
                self.refuse.write_text("on\n", encoding="utf-8")  # the next commit is refused
            return done

        rc, out, err = self.drive(wrap=refuse_after_accept)
        self.assertEqual(1, rc, out + err)
        self.assertIn(f"DRIVE STOPPED: {A} at paperwork, {drive.REFUSAL}", out)
        resume = re.search(r"^  resume: repair what the hook names, then (.+)$", out,
                           re.M).group(1)
        kept = (drive.DRIVE / A / "paperwork.log").as_posix()
        # run again with the commit still unmade: a stop naming the refused commit, never 0
        for _ in range(2):
            rc, out, err = self.drive()
            self.assertEqual(1, rc, out + err)
            text = "\n".join(self.record_of(out))
            self.assertIn(f"DRIVE STOPPED: {A} at paperwork, {drive.REFUSAL}", text)
            self.assertIn("its paperwork commit was refused (exit 1)", text)
            self.assertIn(f"whole output: {kept}", text)
            self.assertIn(resume, text)
            self.assertEqual(self.STATUS, self.status_at(A))
        # the commit the record names, then a drive: the wave ends
        self.refuse.unlink()
        subprocess.run(resume, shell=True, cwd=self.root, env=self.env, check=True,
                       capture_output=True)
        rc, out, err = self.drive()
        self.assertEqual(0, rc, out + err)
        self.assertEqual("Done", self.status_at(A))
        self.assertIn("nothing is left to drive", out)

    def test_a_later_stop_at_accept_is_not_named_a_refused_commit(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            folder = root / drive.DRIVE / A
            folder.mkdir(parents=True)
            self.assertIsNone(drive._refused_paperwork(root, A))  # noqa: SLF001
            log = folder / "paperwork.log"
            log.write_text("$ git commit\nexit 1\n--- stdout\n", encoding="utf-8")
            self.assertEqual(("exit 1", log.relative_to(root).as_posix()),
                             drive._refused_paperwork(root, A))  # noqa: SLF001
            accept = folder / "accept.log"
            accept.write_text("$ sprint.py lane accept\nexit 0\n", encoding="utf-8")
            os.utime(log, ns=(1_000_000_000, 1_000_000_000))
            os.utime(accept, ns=(2_000_000_000, 2_000_000_000))
            self.assertIsNone(drive._refused_paperwork(root, A),  # noqa: SLF001
                              "a stop at accept after the refused commit is named as that commit")
            os.utime(accept, ns=(500_000_000, 500_000_000))
            self.assertEqual("exit 1", drive._refused_paperwork(root, A)[0])  # noqa: SLF001
            # a log cut short, or not UTF-8, still names the refused commit
            log.write_bytes(b"")
            self.assertEqual("exit unknown", drive._refused_paperwork(root, A)[0])  # noqa: SLF001
            log.write_bytes(b"$ git commit \xff\nexit 128\n")
            self.assertEqual("exit 128", drive._refused_paperwork(root, A)[0])  # noqa: SLF001


class _SharingStep(stepped._StepFixture):  # noqa: SLF001
    UNITS = {A: ["src/a.py"], B: ["src/b.py"], C: ["src/b.py", "src/c.py"],
             D: ["src/shared.py"]}


class _Lanes:
    """Stands in for the `sprint.py lane` commands drive runs, each doing only what drive reads
    of it: a session that staged its change, a landing that wrote the QA brief naming a verdict
    file, an accept that moved the unit to Done, and a builder brief. The review, the paperwork
    commit and drive's own walk run for real. A case that ran every command for real took 14
    to 31 s on a loaded host, so the class ran past the criterion's 120 s ceiling; these take
    seconds."""

    ACCEPTED = "{unit}: moved to Done\n  lane return: {unit} cleared\n"

    def __init__(self, accepted: str = ACCEPTED) -> None:
        self.accepted, self.calls = accepted, []

    @staticmethod
    def move(root: Path, unit: str) -> None:
        story = root / f"sdlc-studio/stories/{unit}-drive.md"
        text = story.read_text(encoding="utf-8")
        story.write_text(text.replace("**Status:** Ready", "**Status:** Done"), encoding="utf-8")

    def __call__(self, real, root, script, *args, **kw) -> subprocess.CompletedProcess:
        unit = args[args.index("--units" if "--units" in args else "--unit") + 1]
        self.calls.append((args[1], unit))
        out = None
        if args[:2] == ("lane", "run"):
            out = "  staged: its change\n"
        elif args[:2] == ("lane", "land"):
            verdict = Path(root) / "sdlc-studio" / "reviews" / "verdicts" / unit / f"{unit}-qa.txt"
            brief = (drive.lanes.BRIEFS / f"{unit}-qa.txt").as_posix()
            walk._write(Path(root), brief,  # noqa: SLF001
                        f"Unit: {unit} - review it\n{verdict}\nUNIT: {unit}\nBRIEF: {unit}-qa\n")
            out = f"{unit}: fast-forwarded to main\n"
        elif args[:2] == ("lane", "accept"):
            self.move(Path(root), unit)
            out = self.accepted.format(unit=unit)
        elif args[:2] == ("lane", "brief"):
            out = f"Unit: {unit} - build it\n"
        if out is None:
            raise AssertionError(f"drive ran {args}, which this case does not answer")
        return subprocess.CompletedProcess(args, 0, out, "")


class DriveGuardCoverageTests(walk._DriveFixture):  # noqa: SLF001

    def _case(self, fixture: type) -> walk._DriveFixture:
        case = fixture("run")
        case.setUp()
        self.addCleanup(case.tearDown)
        return case

    def test_a_review_that_cannot_start_exits_2_after_work_ran_as_the_help_says(self) -> None:
        lane = _Lanes()
        with unittest.mock.patch.object(drive.lanes, "BRIEF_MAX_BYTES", 10):
            rc, out, err = self.drive(wrap=lane)
        self.assertEqual(2, rc, out + err)
        self.assertIn(f"{A} build: ", out)
        self.assertIn(f"{A} land: ", out)
        self.assertIn(f"DRIVE STOPPED: {A} at review, {drive.REFUSAL}", out)
        self.assertIn("the brief is over 10 bytes", out)
        self.assertEqual([("run", A), ("land", A)], lane.calls, "the build and landing ran")
        said = io.StringIO()
        with contextlib.redirect_stdout(said), self.assertRaises(SystemExit):
            walk.sprint.main(["drive", "--help"])
        page = (walk.SKILL / "help" / "sprint.md").read_text(encoding="utf-8")
        section = re.search(r"^## Driving a wave.*?(?=^## |\Z)", page, re.M | re.S).group(0)
        for name, text in (("--help", said.getvalue()), ("help/sprint.md", section)):
            with self.subTest(page=name):
                self.assertIn("Exit 2 is a refusal before anything ran, or a review that could "
                              "not start after the unit's build and landing ran (its brief over "
                              "the size limit", " ".join(text.split()))

    def test_the_steps_run_in_the_doctrine_order(self) -> None:
        rc, out, err = self.drive(wrap=_Lanes())
        self.assertEqual(0, rc, out + err)
        lines = out.splitlines()
        at = [next((n for n, ln in enumerate(lines) if ln.startswith(f"{A} {step}: ")), None)
              for step in ORDER]
        self.assertNotIn(None, at, out)
        self.assertEqual(sorted(at), at, f"the steps ran out of the doctrine's order:\n{out}")
        self.assertEqual("Done", self.status_at(A), "the paperwork commit was not made")

    def test_a_return_the_accept_did_not_print_stops_the_unit(self) -> None:
        rc, out, err = self.drive(wrap=_Lanes(accepted="{unit}: moved to Done\n"))
        self.assertEqual(1, rc, out + err)
        text = "\n".join(self.record_of(out))
        self.assertIn(f"DRIVE STOPPED: {A} at return, {drive.REFUSAL}", text)
        self.assertIn("lane accept printed no lane return after the move", text)
        self.assertIn(f"resume: sprint.py lane return --units {A}", text)
        self.assertNotIn(f"{A} paperwork: ", out, "the paperwork ran past the return's stop")
        self.assertEqual(self.STATUS, self.status_at(A))

    def test_landings_take_the_root_one_at_a_time(self) -> None:
        case = self._case(_Pair)
        lane = _Lanes()
        cond, built = threading.Condition(), set()
        seen = {"inside": 0, "most": 0, "entries": 0}

        def watch(real, root, script, *args, **kw):
            if args[:2] == ("lane", "run"):
                done = lane(real, root, script, *args, **kw)
                with cond:
                    built.add(args[3])
                    cond.notify_all()
                return done
            if args[:2] != ("lane", "land"):
                return lane(real, root, script, *args, **kw)
            with cond:
                seen["inside"] += 1
                seen["entries"] += 1
                seen["most"] = max(seen["most"], seen["inside"])
                cond.notify_all()
                if seen["entries"] == 1:
                    # both builds done, the other landing has had its chance to start beside
                    # this one, which it takes unless the root is held
                    cond.wait_for(lambda: len(built) == 2, timeout=60)
                    cond.wait_for(lambda: seen["inside"] > 1, timeout=3)
            try:
                return lane(real, root, script, *args, **kw)
            finally:
                with cond:
                    seen["inside"] -= 1

        # each unit stops once landed, at a review that cannot start: only the landings matter
        with unittest.mock.patch.object(drive.lanes, "BRIEF_MAX_BYTES", 10):
            rc, out, err = case.drive(wrap=watch)
        self.assertEqual(2, rc, out + err)
        self.assertEqual({A, B}, built, "the two lanes did not both build")
        self.assertEqual(2, seen["entries"], out + err)
        self.assertEqual(1, seen["most"], "two landings held the root at once")
        self.assertEqual({A, B}, {u for verb, u in lane.calls if verb == "land"},
                         "both lanes did not land")

    def test_a_unit_sharing_a_file_with_one_building_is_given_no_prompt(self) -> None:
        case = self._case(_SharingStep)
        # A landed and awaits the verdict reviewer ra writes; drive gave B its builder prompt,
        # and B is building: C shares src/b.py with it
        verdict = case.root / "sdlc-studio" / "reviews" / "verdicts" / A / f"{A}-qa.txt"
        verdict.parent.mkdir(parents=True)
        prompt = drive.PROMPTS / f"{sdlc_md.norm_id(A)}-review-r1.txt"
        walk._write(case.root, prompt.as_posix(),  # noqa: SLF001
                    f"Review {A}.\n{verdict}\nUNIT: {A}\nBRIEF: {A}-qa\n")
        walk._write(case.root, drive.LANES.as_posix(), json.dumps({  # noqa: SLF001
            sdlc_md.norm_id(A): {"unit": A, "stage": "review", "round": 1, "builder": "a1",
                                 "reviewer": None, "verdict": str(verdict),
                                 "prompt": prompt.as_posix()},
            sdlc_md.norm_id(B): {"unit": B, "stage": "build",
                                 "prompt": (drive.PROMPTS / f"{B}-build.txt").as_posix()}}))
        case.verdict(A, stepped.APPROVE, by="ra")
        rc, out, err = case.run_sprint("drive", "step", "--after", "ra", wrap=_Lanes())
        self.assertEqual(0, rc, out + err)
        self.assertEqual("Done", case.status_at(A))
        self.assertFalse((case.root / drive.PROMPTS / f"{C}-build.txt").exists(), out)
        self.assertIn(f"waits on {B} (build), {C} (not started)", case.last(out))


class _Pair(walk._DriveFixture):  # noqa: SLF001
    UNITS = {A: ["src/a.py"], B: ["src/b.py"]}
    WAVES = [[A, B]]


if __name__ == "__main__":
    unittest.main()
