"""A warning at an APPROVE's accept under `sprint.py drive step` names a resume that resumes.

The accept has recorded the verdict and moved the unit when its WARNING stops the step, so the
`lane accept` the record used to name exits 2 ('a verdict file is recorded once'). The record
names what `sprint.py drive` names at the same stop: the unit's paperwork commit, then the same
step again, which takes up the recorded accept rather than recording it twice. The fixture is
`test_sprint_drive_step`'s; one case wraps the step runner to add a WARNING to a green accept.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/drive.py
from __future__ import annotations

import json
import re
import shlex
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_sprint_drive_step as stepped
from lib import drive, sdlc_md

A, B, C = stepped.A, stepped.B, stepped.C
WARNING = "WARNING the verdict was taken against an earlier Affects scope"


def _warn(real, root, script, *args, **kw):
    done = real(root, script, *args, **kw)
    if args[:2] == ("lane", "accept") and A in args and done.returncode == 0:
        done = subprocess.CompletedProcess(done.args, 0, done.stdout,
                                           done.stderr + WARNING + "\n")
    return done


class DriveStepAcceptResumeTests(stepped._StepFixture):  # noqa: SLF001

    def _warned(self) -> str:
        """A's APPROVE accepted under a WARNING; the resume its record names."""
        self.builder("a1", A, "A = 2\n")
        rc, out, err = self.step("a1")
        self.assertEqual(0, rc, out + err)
        self.verdict(A, stepped.APPROVE, by="ra")
        rc, out, err = self.run_sprint("drive", "step", "--after", "ra", wrap=_warn)
        self.assertEqual(1, rc, out + err)
        text = "\n".join(self.record_of(out))
        self.assertIn(f"DRIVE STOPPED: {A} at accept, {drive.WARNED}", text)
        self.assertIn(WARNING, text)
        self.assertEqual(1, len(self.rows(A)), "the APPROVE was not recorded")
        self.assertEqual(self.STATUS, self.status_at(A), "the move was committed past the warning")
        return re.search(r"^  resume: (.+)$", text, re.M).group(1)

    def _run(self, part: str) -> tuple[int, str, str]:
        """One command of a resume, as the operator runs it: a `sprint.py` command through its
        entry point, anything else in the shell, in the root."""
        if part.startswith("sprint.py "):
            return self.run_sprint(*shlex.split(part)[1:])
        done = subprocess.run(part, shell=True, cwd=self.root, env=self.env,
                              capture_output=True, text=True, check=False)
        return done.returncode, done.stdout, done.stderr

    def test_the_printed_resume_resumes_from_the_recorded_accept(self) -> None:
        resume = self._warned()
        for part in resume.split(", then "):
            rc, out, err = self._run(part)
            self.assertEqual(0, rc, f"`{part}` failed:\n{out}{err}")
        # the step took up the recorded accept: nothing recorded twice, the paperwork at HEAD,
        # and the step ended as an APPROVE's does, on the wave's next builder prompt
        self.assertEqual(1, len(self.rows(A)), self.rows(A))
        self.assertEqual("Done", self.status_at(A))
        self.assertEqual([], [ln for ln in self.dirty() if A in ln])
        self.assertEqual("done", self.lanes()[sdlc_md.norm_id(A)]["stage"])
        prompt = Path(self.last(out))
        self.assertTrue(prompt.is_file(), out)
        self.assertIn(f"Unit: {B} ", prompt.read_text(encoding="utf-8"))

    def test_a_refused_accept_beside_a_warning_still_names_lane_accept(self) -> None:
        """Only an accept that exited 0 has recorded its verdict: one that refused, WARNING or
        not, is resumed by `lane accept` itself and leaves nothing marked accepted."""
        def refuse(real, root, script, *args, **kw):
            done = real(root, script, *args, **kw)
            if args[:2] == ("lane", "accept") and A in args:
                done = subprocess.CompletedProcess(done.args, 1, done.stdout,
                                                   done.stderr + WARNING + "\n")
            return done

        self.builder("a1", A, "A = 2\n")
        rc, out, err = self.step("a1")
        self.assertEqual(0, rc, out + err)
        self.verdict(A, stepped.APPROVE, by="ra")
        rc, out, err = self.run_sprint("drive", "step", "--after", "ra", wrap=refuse)
        self.assertEqual(1, rc, out + err)
        text = "\n".join(self.record_of(out))
        self.assertIn(f"DRIVE STOPPED: {A} at accept, {drive.REFUSAL}", text)
        self.assertRegex(text, rf"resume: sprint\.py lane accept --unit {A} --verdict ")
        entry = self.lanes()[sdlc_md.norm_id(A)]
        self.assertEqual(("review", None), (entry["stage"], entry["reviewer"]), entry)

    def test_a_rerun_before_the_paperwork_commit_holds_as_drive_does(self) -> None:
        resume = self._warned()
        command = resume.split(", then ")[0]
        self.assertTrue(command.startswith("git add -- "), resume)
        # the step alone, the warning unanswered: it holds, records nothing again
        rc, out, err = self.step("ra")
        self.assertEqual(1, rc, out + err)
        text = "\n".join(self.record_of(out))
        self.assertIn(f"DRIVE STOPPED: {A} at paperwork, {drive.REFUSAL}", text)
        self.assertIn("uncommitted", text)
        self.assertIn(command, text)
        # naming the unit takes up the same recorded accept, and holds the same way
        rc, out, err = self.run_sprint("drive", "step", "--after", "ra", "--unit", A)
        self.assertEqual(1, rc, out + err)
        self.assertIn(f"DRIVE STOPPED: {A} at paperwork, {drive.REFUSAL}", out)
        self.assertEqual(1, len(self.rows(A)), self.rows(A))
        self.assertEqual(self.STATUS, self.status_at(A))
        self.assertFalse(list((self.root / drive.PROMPTS).glob("*-build.txt")), out)

    def test_only_the_recorded_reviewer_takes_up_the_recorded_accept(self) -> None:
        """A recorded accept is A's reviewer's to resume: another unit's reviewer handing back
        has its own unit accepted, and naming A it is refused. The lane record and A's move are
        written as a warned accept and a landing leave them, and `lane accept` and `lane brief`
        are stood in for by their move and their output's first line, so the case runs in
        seconds."""
        story = lambda unit: self.root / f"sdlc-studio/stories/{unit}-drive.md"  # noqa: E731

        def move(unit: str) -> None:
            text = story(unit).read_text(encoding="utf-8")
            story(unit).write_text(text.replace(f"**Status:** {self.STATUS}", "**Status:** Done"),
                                   encoding="utf-8")

        def entry(unit: str, stage: str, builder: str, reviewer) -> dict:
            verdict = self.root / f"sdlc-studio/reviews/verdicts/{unit}/{unit}-qa.txt"
            verdict.parent.mkdir(parents=True, exist_ok=True)
            prompt = drive.PROMPTS / f"{sdlc_md.norm_id(unit)}-review-r1.txt"
            stepped.walk._write(self.root, prompt.as_posix(),  # noqa: SLF001
                                f"Review {unit}.\n{verdict}\nUNIT: {unit}\nBRIEF: {unit}-qa\n")
            return {"unit": unit, "stage": stage, "round": 1, "builder": builder,
                    "reviewer": reviewer, "verdict": str(verdict), "prompt": prompt.as_posix()}

        def lane(real, root, script, *args, **kw):
            if args[:2] == ("lane", "accept") and args[3] == B:
                move(B)
                return subprocess.CompletedProcess(args, 0, f"{B}: moved to Done\n", "")
            if args[:2] == ("lane", "brief"):
                return subprocess.CompletedProcess(args, 0, f"Unit: {args[-1]} - build it\n", "")
            raise AssertionError(f"drive ran {args}, which this case does not answer")

        stepped.walk._write(self.root, drive.LANES.as_posix(), json.dumps({  # noqa: SLF001
            sdlc_md.norm_id(A): entry(A, "accepted", "a1", "ra"),
            sdlc_md.norm_id(B): entry(B, "review", "b1", None)}))
        self.verdict(A, stepped.APPROVE, by="ra")
        move(A)  # A's accept moved it under the warning; its paperwork commit is unmade
        self.verdict(B, stepped.APPROVE, by="rb")
        rc, out, err = self.run_sprint("drive", "step", "--after", "rb", "--unit", A, wrap=lane)
        self.assertEqual(2, rc, out + err)
        self.assertIn(f"{A} awaits no verdict", err)
        rc, out, err = self.run_sprint("drive", "step", "--after", "rb", wrap=lane)
        self.assertEqual(0, rc, out + err)
        self.assertIn(f"{B} accept: {B}: moved to Done", out)
        self.assertEqual(("Done", self.STATUS), (self.status_at(B), self.status_at(A)))
        record = self.lanes()
        self.assertEqual(("accepted", "ra"), (record[sdlc_md.norm_id(A)]["stage"],
                                              record[sdlc_md.norm_id(A)]["reviewer"]), record)
        self.assertEqual("done", record[sdlc_md.norm_id(B)]["stage"], record)
        self.assertTrue(self.last(out).endswith(f"{sdlc_md.norm_id(C)}-build.txt"), out)


if __name__ == "__main__":
    unittest.main()
