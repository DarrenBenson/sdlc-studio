"""`sprint drive step --after <agent id>` performs the whole chain after one hand-back and prints
the next prompt's path.

The fixture is `test_sprint_drive`'s repository, open run and stub hook, with a temporary harness
store in place of the operator's: each builder works in a worktree named `agent-<id>`, as the
harness names one, stages its change and hand-in there, and spends tokens in its own transcript
under the orchestrating session's subagents directory, which the landing prices. A reviewer
writes its verdict to the file its prompt names. `lane land`, `critic.py`, `lane accept`,
`lane brief --repair`, `verify_ac.py` and the paperwork commit all run for real.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/drive.py
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil
import test_meter_reads_true as meter
import test_sprint_drive as walk
from lib import drive, run_state, sdlc_md

A, B, C, D = walk.A, walk.B, walk.C, "US0104"
APPROVE = "VERDICT: APPROVE\nISSUES: none\nBLOCKING: none\n"
FINDING = "the gate lets a red unit through"
REJECT = f"VERDICT: REJECT\nISSUES: [new] {FINDING}\nBLOCKING: [new] {FINDING}\n"
BUILD = meter._usage(40, 400, 5_000, 0, 120_000)  # noqa: SLF001
_VERDICT_AT = re.compile(r"^(/.*/sdlc-studio/reviews/verdicts/.+\.txt)\nUNIT: (\S+)\nBRIEF: (\S+)\s*$",
                         re.M)


class _StepFixture(walk._DriveFixture):  # noqa: SLF001
    UNITS = {A: ["src/a.py"], B: ["src/b.py"], C: ["src/c.py"], D: ["src/shared.py"]}
    WAVES = [[A, B, C], [D]]

    def setUp(self) -> None:
        super().setUp()
        self.tx = meter._Transcripts(self.home / ".claude" / "projects"  # noqa: SLF001
                                     / run_state.harness_project_slug(self.root))
        meter._Transcripts._append(self.tx.main, self.tx._records(  # noqa: SLF001
            "msg_main", meter.MAIN_1, None, str(self.root)))
        # from here the meter reads the fixture store under HOME, as a session's own does
        self.env.pop(run_state.TRANSCRIPTS_ENV)

    def builder(self, agent: str, unit: str, body: str) -> Path:
        """A builder agent's worktree `agent-<agent>`, holding `unit`'s staged change and
        hand-in, and the agent's transcript."""
        wt = self.base / f"agent-{agent}"
        gitutil.git(["worktree", "add", "-q", "-b", f"agent-{agent}", str(wt), "main"], self.root)
        rel = self.UNITS[unit][0]
        for path, text in ((rel, body), (f"changelog.d/{unit}.md", f"{body}")):
            walk._write(wt, path, text)  # noqa: SLF001
            gitutil.git(["add", "--", path], wt)
        lane = "sdlc-studio/.local/lane"
        walk._write(wt, f"{lane}/commit-msg.txt", f"feat({unit}): {body.strip()}\n")  # noqa: SLF001
        claims = [{"surface": "commit message", "claim": "it lands", "ruling": "TRUE"},
                  {"surface": f"changelog.d/{unit}.md", "claim": "it lands", "ruling": "TRUE"}]
        walk._write(wt, f"{lane}/{unit}-claims.json", json.dumps(claims))  # noqa: SLF001
        walk._write(wt, f"{lane}/{unit}-mutants.json", "[]")  # noqa: SLF001
        meter._Transcripts._append(self.tx.subagents / f"agent-{agent}.jsonl",  # noqa: SLF001
                                   self.tx._records(f"msg_{agent}", BUILD, None, str(wt)))  # noqa: SLF001
        return wt

    def step(self, agent: str) -> tuple[int, str, str]:
        return self.run_sprint("drive", "step", "--after", agent)

    def lanes(self) -> dict:
        path = self.root / drive.LANES
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}

    def briefed(self, agent: str, prompt: str) -> None:
        """Agent `agent`'s transcript, as the harness keeps it, opening on the prompt it was
        given."""
        meter._Transcripts._append(  # noqa: SLF001
            self.tx.subagents / f"agent-{agent}.jsonl",
            [json.dumps({"type": "user", "message": {"role": "user", "content": prompt}})])

    def verdict(self, unit: str, text: str, by: str) -> Path:
        """Reviewer agent `by`, briefed with `unit`'s prompt, writes `text` to the verdict file
        that prompt names."""
        entry = self.lanes()[sdlc_md.norm_id(unit)]
        prompt = (self.root / entry["prompt"]).read_text(encoding="utf-8")
        self.briefed(by, prompt)
        path, uid, stem = _VERDICT_AT.findall(prompt)[-1]
        Path(path).write_text(f"UNIT: {uid}\nBRIEF: {stem}\n{text}", encoding="utf-8")
        return Path(path)

    def rows(self, unit: str) -> list[str]:
        text = walk.critic.verdicts_path(self.root).read_text(encoding="utf-8")
        return [ln for ln in text.splitlines() if ln.startswith(f"| {unit} |")]

    def priced(self, unit: str) -> list[dict]:
        return [r for r in run_state.read(self.root).get(run_state.DELEGATED) or []
                if r.get("unit") == unit and r.get("priced") is not None]

    @staticmethod
    def last(out: str) -> str:
        return out.strip().splitlines()[-1]

    def round_one_reject(self) -> None:
        self.builder("a1", A, "A = 2\n")
        rc, out, err = self.step("a1")
        self.assertEqual(0, rc, out + err)
        self.verdict(A, REJECT, by="ra")
        rc, out, err = self.step("ra")
        self.assertEqual(0, rc, out + err)

    def repair_landed(self) -> tuple[str, str]:
        self.round_one_reject()
        self.builder("a2", A, "A = 3\n")
        rc, out, err = self.step("a2")
        self.assertEqual(0, rc, out + err)
        return out, err


class _CapOfOne(_StepFixture):
    def config(self) -> str:
        return "review:\n  author_self_check: block\n  max_rounds: 1\n"


class SprintDriveStepTests(_StepFixture):

    def test_a_builders_hand_back_is_landed_briefed_and_the_review_prompt_named(self) -> None:
        wt = self.builder("a1", A, "A = 2\n")
        rc, out, err = self.step("a1")
        self.assertEqual(0, rc, out + err)
        self.assertEqual(f"feat({A}): A = 2", self.subjects()[0])
        self.assertFalse(wt.exists(), "the landed worktree was not removed")
        self.assertTrue([r for r in walk.critic.read_self_checks(self.root)
                         if sdlc_md.norm_id(r["unit"]) == A], "no self-check was recorded")
        self.assertIn(f"{A}'s return priced from agent-a1's transcript", out)
        self.assertTrue(self.priced(A), "the return was not priced")
        prompt = Path(self.last(out))
        self.assertTrue(prompt.is_file(), f"the last line names no file: {prompt}")
        brief = (self.root / "sdlc-studio/.local/briefs" / f"{A}-qa.txt").read_text(
            encoding="utf-8")
        self.assertEqual(brief.strip(), prompt.read_text(encoding="utf-8").strip())
        self.assertRegex(brief, rf"\nUNIT: {A}\nBRIEF: ")

    def test_a_reviewers_hand_back_is_accepted_and_the_next_prompt_named(self) -> None:
        for agent, unit, body in (("a1", A, "A = 2\n"), ("b1", B, "B = 2\n")):
            self.builder(agent, unit, body)
            rc, out, err = self.step(agent)
            self.assertEqual(0, rc, out + err)
        self.verdict(A, APPROVE, by="ra")
        rc, out, err = self.step("ra")
        self.assertEqual(0, rc, out + err)
        self.assertEqual("Done", self.status_at(A))
        self.assertTrue(self.subjects()[0].startswith(f"docs({A}): record {A}'s review"))
        self.assertIn("qa-seat-US0101-ra", self.rows(A)[-1])
        # the next prompt is the next unit's builder's, never B's, which is built already
        prompt = Path(self.last(out))
        self.assertTrue(prompt.is_file(), out)
        self.assertIn(f"Unit: {C} ", prompt.read_text(encoding="utf-8"))
        self.assertFalse((self.root / drive.PROMPTS / f"{B}-build.txt").exists())
        # with every other unit of the wave Done, the wave has ended and the next wave waits
        story = self.root / "sdlc-studio" / "stories" / f"{C}-drive.md"
        story.write_text(story.read_text(encoding="utf-8").replace(
            "**Status:** Ready", "**Status:** Done"), encoding="utf-8")
        gitutil.git(["commit", "-q", "-am", f"chore: {C} is done"], self.root)
        self.verdict(B, APPROVE, by="rb")
        rc, out, err = self.step("rb")
        self.assertEqual(0, rc, out + err)
        self.assertEqual("Done", self.status_at(B))
        self.assertIn("wave 1 of 2 has ended", self.last(out))
        self.assertFalse((self.root / drive.PROMPTS / f"{D}-build.txt").exists())

    def test_a_unit_briefed_outside_drive_is_given_no_second_builder_prompt(self) -> None:
        # the wave's builders are started the usual way, by `lane brief`, which drive's own
        # lane record never sees
        rc, out, err = self.run_sprint("lane", "brief", "--units", A, B, C)
        self.assertEqual(0, rc, out + err)
        self.builder("a1", A, "A = 2\n")
        rc, out, err = self.step("a1")
        self.assertEqual(0, rc, out + err)
        self.verdict(A, APPROVE, by="ra")
        rc, out, err = self.step("ra")
        self.assertEqual(0, rc, out + err)
        self.assertEqual("Done", self.status_at(A))
        # B's and C's builders were briefed and never returned: neither is briefed again
        self.assertFalse(list((self.root / drive.PROMPTS).glob("*-build.txt")), out)
        self.assertFalse(Path(self.last(out)).is_file(), out)
        self.assertIn("waits on", self.last(out))

    def test_a_landing_stopped_after_its_commit_is_resumed_by_the_next_step(self) -> None:
        self.builder("a1", A, "A = 2\n")
        rc, out, err = self.step("a1")
        self.assertEqual(0, rc, out + err)
        # B's commit hook leaves a file no commit carries, made after the check that refuses a
        # builder's leftover: its landing commits, lands and then cannot remove the worktree
        # unforced
        wt = self.builder("b1", B, "B = 2\n")
        walk._write(self.late.parent, self.late.name, "x\n")  # noqa: SLF001
        rc, out, err = self.step("b1")
        self.assertEqual(1, rc, out + err)
        self.assertIn(f"DRIVE STOPPED: {B} at land, {drive.REFUSAL}", out)
        self.assertEqual(f"feat({B}): B = 2", self.subjects()[0])
        # A's APPROVE names no builder prompt for B, which is landed
        self.verdict(A, APPROVE, by="ra")
        rc, out, err = self.step("ra")
        self.assertEqual(0, rc, out + err)
        self.assertFalse((self.root / drive.PROMPTS / f"{B}-build.txt").exists(), out)
        # the repair the record names, then the step it names: the landing is resumed
        (wt / "src" / "loose.py").unlink()
        rc, out, err = self.step("b1")
        self.assertEqual(0, rc, out + err)
        self.assertFalse(wt.exists(), "the resumed landing did not remove the worktree")
        prompt = Path(self.last(out))
        self.assertEqual(f"{sdlc_md.norm_id(B)}-review-r1.txt", prompt.name)
        # and B's reviewer's hand-back is taken
        self.verdict(B, APPROVE, by="rb")
        rc, out, err = self.step("rb")
        self.assertEqual(0, rc, out + err)
        self.assertEqual("Done", self.status_at(B))
        self.assertEqual(1, self.subjects().count(f"feat({B}): B = 2"))

    def test_a_landing_stopped_after_its_worktree_went_is_resumed_from_its_record(self) -> None:
        wt = self.builder("a1", A, "A = 2\n")
        (wt / "sdlc-studio" / ".local" / "lane" / f"{A}-claims.json").unlink()
        rc, out, err = self.step("a1")
        self.assertEqual(1, rc, out + err)
        self.assertEqual(f"feat({A}): A = 2", self.subjects()[0])
        self.assertFalse(wt.exists())
        # the claims are handed in where the landing kept the hand-in, and the step resumes it
        kept = self.root / drive.lanes.LANDED / "agent-a1"
        claims = [{"surface": "commit message", "claim": "it lands", "ruling": "TRUE"},
                  {"surface": f"changelog.d/{A}.md", "claim": "it lands", "ruling": "TRUE"}]
        walk._write(kept, f"{A}-claims.json", json.dumps(claims))  # noqa: SLF001
        rc, out, err = self.step("a1")
        self.assertEqual(0, rc, out + err)
        self.assertEqual(f"{sdlc_md.norm_id(A)}-review-r1.txt", Path(self.last(out)).name)
        self.assertEqual("review", self.lanes()[sdlc_md.norm_id(A)]["stage"])

    def test_a_refused_step_prints_a_decision_record_and_no_prompt_path(self) -> None:
        self.refuse.write_text("on\n", encoding="utf-8")
        self.builder("a1", A, "A = 2\n")
        rc, out, err = self.step("a1")
        self.assertNotEqual(0, rc, out + err)
        self.assertIn(f"DRIVE STOPPED: {A} at land, {drive.REFUSAL}", out)
        self.assertFalse(Path(self.last(out)).is_file())
        self.assertFalse((self.root / drive.PROMPTS).exists(), "a prompt was written")
        self.assertEqual(["chore: the fixture"], self.subjects())
        # an agent the run has no lane for changes nothing
        head = walk._git(self.root, "rev-parse", "HEAD")  # noqa: SLF001
        before = (self.root / drive.LANES).exists()
        rc, out, err = self.step("nobody7")
        self.assertEqual(2, rc, out + err)
        self.assertIn("nobody7", err)
        self.assertEqual("", out)
        self.assertEqual(head, walk._git(self.root, "rev-parse", "HEAD"))  # noqa: SLF001
        self.assertEqual(before, (self.root / drive.LANES).exists())

    def test_a_reject_hand_back_briefs_the_repair_and_names_its_prompt(self) -> None:
        self.builder("a1", A, "A = 2\n")
        rc, out, err = self.step("a1")
        self.assertEqual(0, rc, out + err)
        self.verdict(A, REJECT, by="ra")
        rc, out, err = self.step("ra")
        self.assertEqual(0, rc, out + err)
        self.assertIn("| REJECT |", self.rows(A)[-1])
        self.assertEqual(self.STATUS, self.status_at(A))
        prompt = Path(self.last(out))
        self.assertTrue(prompt.is_file(), out)
        text = prompt.read_text(encoding="utf-8")
        self.assertIn(f"Unit: {A} ", text)
        # the repair brief, carrying the REJECT's blocking finding verbatim
        self.assertIn(f"--- REPAIR: what this repair of {A} answers, quoted verbatim ---", text)
        self.assertRegex(text, rf"\nBLOCKING \(every finding[^\n]*\n\[new\] {FINDING}\n")
        self.assertIn("by qa-seat-US0101-ra (qa)", text)
        self.assertFalse((self.root / drive.PROMPTS / f"{B}-build.txt").exists())

    def test_a_repair_hand_back_is_landed_and_the_round_two_prompt_named(self) -> None:
        out, err = self.repair_landed()
        self.assertEqual(f"feat({A}): A = 3", self.subjects()[0])
        self.assertIn(f"{A}'s return priced from agent-a2's transcript", out)
        prompt = Path(self.last(out))
        self.assertTrue(prompt.is_file(), out)
        text = prompt.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("For reviewer agent ra, resumed for round 2"), text[:200])
        self.assertIn("RE-REVIEW (rejoinder)", text)
        self.assertIn(FINDING, text)
        self.assertIn("resume reviewer agent ra", out)
        # the reviewer who rejected is resumed, and its round-two APPROVE is accepted
        self.verdict(A, APPROVE, by="ra")
        rc, out, err = self.step("ra")
        self.assertEqual(0, rc, out + err)
        self.assertEqual("Done", self.status_at(A))
        self.assertEqual(["REJECT", "APPROVE"],
                         [re.search(r"\| (APPROVE|REJECT) \|", r).group(1) for r in self.rows(A)])

    def test_a_reject_at_the_round_cap_stops_with_a_decision_record(self) -> None:
        self.repair_landed()
        self.verdict(A, REJECT, by="ra")
        rc, out, err = self.step("ra")
        self.assertNotEqual(0, rc, out + err)
        self.assertIn(f"DRIVE STOPPED: {A} at accept, {drive.REJECTED}", out)
        self.assertIn("at the review round cap of 2", out)
        self.assertIn("operator's ruling", out)
        self.assertFalse(Path(self.last(out)).is_file())
        self.assertFalse(list((self.root / drive.PROMPTS).glob(f"{A}-repair-r2*")))
        # the cap is the project's own `review.max_rounds`, not a fixed two
        case = _CapOfOne("run")
        case.setUp()
        self.addCleanup(case.tearDown)
        case.builder("a1", A, "A = 2\n")
        rc, out, err = case.step("a1")
        self.assertEqual(0, rc, out + err)
        case.verdict(A, REJECT, by="ra")
        rc, out, err = case.step("ra")
        self.assertNotEqual(0, rc, out + err)
        self.assertIn("at the review round cap of 1", out)
        self.assertFalse(list((case.root / drive.PROMPTS).glob(f"{A}-repair-*")))

    def test_a_reject_sharing_a_held_round_is_not_at_the_cap(self) -> None:
        """BG1661: the cap is judged on the round a REJECT took, not on the rows recorded. An
        APPROVE held for a second seat (`critic.hold_for_second_seat`, as `lane accept` holds a
        high-risk unit's first seat) shares its round with the next seat's REJECT, so that
        REJECT is round 1 and its repair is briefed, not stopped at the cap of 2. MUTANT: count
        the delivery's rows (`len`), which reads two rounds and stops the unit."""
        self.builder("a1", A, "A = 2\n")
        rc, out, err = self.step("a1")
        self.assertEqual(0, rc, out + err)
        walk.critic.record_verdict(self.root, A, "APPROVE", "dani (engineering)", "builder")
        walk.critic.hold_for_second_seat(self.root, A)
        self.verdict(A, REJECT, by="ra")
        rc, out, err = self.step("ra")
        self.assertEqual(0, rc, out + err)
        self.assertEqual([1, 1], [r["round"] for r in walk.critic.delivery_rounds(self.root, A)])
        self.assertNotIn("round cap", out)
        prompt = Path(self.last(out))
        self.assertTrue(prompt.is_file(), out)
        self.assertEqual(f"{A}-repair-r1.txt".lower(), prompt.name.lower())
        self.assertIn(f"--- REPAIR: what this repair of {A} answers, quoted verbatim ---",
                      prompt.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
