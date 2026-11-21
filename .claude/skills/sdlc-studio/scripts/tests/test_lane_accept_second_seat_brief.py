"""BG1614: lane accept records a second seat's verdict against the brief that seat answered.

A high-risk unit takes two independent seats. `sprint lane land` saves the unit's QA brief and
`lane accept` records the qa seat's verdict against it; the second seat is briefed with
`critic.py brief --unit <id> --seat engineering`, whose verdict file opens with a `BRIEF:` line
naming the file that brief issued. `lane accept` recorded that verdict against the saved qa
brief, ignoring the header. Now it records it against the brief the header names, and refuses a
header that names no brief noted for the unit, or one noted before the landing that saved the
QA brief, which a later re-brief of the same scope is not. A saved brief naming no file it
issued, as one saved before verdict files does, is dated by the last note of its
fingerprint, and one naming a file no note records refuses a verdict tied to another brief.

The cases run on `test_lane_accept`'s throwaway repository, with a component map that puts the
unit's Affects in the top risk class: `sprint.py lane land` lands each round for real, and
`critic.py brief`, `critic.py record`, `verify_ac.py run`, `transition.py set` and `sprint.py lane
return` run through their entry points.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/lanes.py
from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import test_lane_accept as base  # noqa: E402 - the lane accept fixture and its helpers

GREEN, RED, APPROVE, SCRIPTS = base.GREEN, base.RED, base.APPROVE, base.SCRIPTS
critic = base.critic
ENGINEER = "agent-x (engineering)"


class LaneAcceptSecondSeatBriefTests(unittest.TestCase):

    # the fixture and helpers of `test_lane_accept`, without collecting its cases a second time
    _accept = base.LaneAcceptTests._accept
    _rows = base.LaneAcceptTests._rows
    _land_round = base.LaneAcceptTests._land_round
    _brief = base.LaneAcceptTests._brief
    _landed_fp = base.LaneAcceptTests._landed_fp
    tearDown = base.LaneAcceptTests.tearDown

    def setUp(self) -> None:
        base.LaneAcceptTests.setUp(self)
        base._write(self.root, "sdlc-studio/personas/seats/engineering.md",
                    "<!-- role: engineering -->\n# Dani\n\ncharter\n\n## Lens\n\nx\n\n"
                    "## Pushes Back When\n\nx\n\n## Shadow\n\nx\n")
        config = base._write(self.root, "sdlc-studio/.config.yaml",
                             "risk:\n  components:\n    src/: high\n")
        gitutil.git(["add", "--", str(config)], self.root)
        gitutil.git(["commit", "-q", "-m", "chore: src is high risk"], self.root)

    def _seat_brief(self, uid: str = GREEN, seat: str = "engineering") -> tuple[Path, str, str]:
        """Brief `seat` with `critic.py brief` through its entry point: the verdict file it
        issued, and the fingerprint and tier its footer printed."""
        done = subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / "critic.py"), "brief", "--unit", uid, "--seat",
             seat, "--root", str(self.root)], capture_output=True, text=True, timeout=300,
            cwd=str(self.root), env=gitutil.git_env(), check=False)
        self.assertEqual(done.returncode, 0, done.stderr)
        path = Path(re.search(r"^(/\S+\.txt)\nUNIT: ", done.stdout, re.M).group(1))
        fp = re.search(r"^brief fingerprint: (\S+)$", done.stderr, re.M).group(1)
        tier = re.search(r"^review tier: (\S+)", done.stderr, re.M).group(1)
        return path, fp, tier

    def _qa_recorded(self) -> str:
        """Land round one and record the qa seat's APPROVE against its saved brief."""
        landed = self._land_round("A = 2\n", f"feat({GREEN}): a is two")
        self.assertEqual(landed.returncode, 0, landed.stdout + landed.stderr)
        saved = self._landed_fp(landed)
        rc, out, err = self._accept(GREEN, APPROVE)
        self.assertIn(f"{GREEN}: APPROVE recorded, round 1, against brief {saved}", out, err)
        self.assertEqual(self._rows(GREEN)[-1][1:6:4], ["APPROVE", saved])
        return saved

    def _refused(self, verdict: str, at: Path | None = None) -> str:
        """`lane accept` of `verdict` from the second seat, refused before anything ran."""
        rows = self._rows(GREEN)
        self.calls.clear()
        rc, out, err = self._accept(GREEN, verdict, at=at, reviewer=ENGINEER)
        self.assertEqual(rc, 2, out + err)
        self.assertEqual(self.calls, [], "lane accept ran a script for a refused verdict")
        self.assertEqual(self._rows(GREEN), rows, "a verdict was recorded")
        return err

    def test_a_second_seat_verdict_records_against_the_brief_its_header_names(self) -> None:
        """AC1. MUTANT: the BRIEF header ignored (the row takes the saved qa brief's
        fingerprint, as before the fix)."""
        saved = self._qa_recorded()
        path, fp, tier = self._seat_brief()
        self.assertNotEqual(fp, saved, "the engineering brief shares the qa brief's fingerprint")
        self.calls.clear()
        rc, out, err = self._accept(GREEN, f"UNIT: {GREEN}\nBRIEF: {path.stem}\n{APPROVE}",
                                    at=path, reviewer=ENGINEER)
        self.assertRegex(out, rf"(?m)^{GREEN}: APPROVE recorded, round \d+, against brief "
                              rf"{fp} at the {tier} tier$", err)
        row = self._rows(GREEN)[-1]
        self.assertEqual([row[1], row[2], row[5], row[6]], ["APPROVE", ENGINEER, fp, tier])
        self.assertEqual(critic.recorded_seat(row[2]), "engineering")
        # bound to the file the engineering brief issued, not transcribed
        self.assertEqual(row[7].split()[1:2], [path.name], row)
        self.assertEqual(self.calls[0][0], "critic.py")

    def test_a_header_naming_no_saved_brief_for_the_unit_is_refused(self) -> None:
        """AC1's refusal. MUTANT: a header naming no noted brief falls back to the saved qa
        brief (the verdict is recorded against a brief its reviewer never read). The engineering
        seat is briefed for the unit first, so the reviewer's seat is one it was briefed for and
        only the header is wrong."""
        saved = self._qa_recorded()
        self._seat_brief()
        with self.subTest("a stem no brief issued"):
            err = self._refused(f"UNIT: {GREEN}\nBRIEF: 0123456789ab-deadbeef\n{APPROVE}")
            self.assertIn("opens with BRIEF: 0123456789ab-deadbeef, which names no brief noted "
                          f"for {GREEN}", err)
        with self.subTest("a brief issued for another unit"):
            other, _, _ = self._seat_brief(RED)
            err = self._refused(f"UNIT: {GREEN}\nBRIEF: {other.stem}\n{APPROVE}")
            self.assertIn(f"opens with BRIEF: {other.stem}, which names no brief noted for "
                          f"{GREEN}", err)
        # positive control: a file with no header is recorded against the saved brief, as before
        rc, out, err = self._accept(GREEN, APPROVE, reviewer="qa-seat")
        self.assertIn(f"{GREEN}: APPROVE recorded, round ", out, err)
        self.assertEqual(self._rows(GREEN)[-1][1:6:4], ["APPROVE", saved])

    def test_a_second_seat_brief_written_before_the_latest_landing_is_refused(self) -> None:
        """MUTANT: the header's brief taken whenever it was noted (a verdict on the round
        before the repair is recorded against the repair)."""
        self._qa_recorded()
        early, _, _ = self._seat_brief()
        landed = self._land_round("A = 3\n", f"fix({GREEN}): a is three")
        self.assertEqual(landed.returncode, 0, landed.stdout + landed.stderr)
        saved = self._landed_fp(landed)
        err = self._refused(f"UNIT: {GREEN}\nBRIEF: {early.stem}\n{APPROVE}", at=early)
        self.assertIn(f"{early} was issued by a brief written before the landing that saved "
                      f"sdlc-studio/.local/briefs/{GREEN}-qa.txt (fingerprint {saved})", err)
        self.assertIn(f"brief the seat again with `critic.py brief --unit {GREEN} --seat "
                      f"engineering` and record the file that brief names", err)
        # positive control: the seat briefed again after that landing is recorded
        path, fp, _ = self._seat_brief()
        rc, out, err = self._accept(GREEN, f"UNIT: {GREEN}\nBRIEF: {path.stem}\n{APPROVE}",
                                    at=path, reviewer=ENGINEER)
        self.assertIn(f"against brief {fp}", out, err)

    def test_a_re_brief_after_the_landing_reads_as_no_landing(self) -> None:
        """MUTANT: the latest plain note of the saved brief's fingerprint is taken as the
        landing, so a qa re-brief of the same scope after it reads as one, and the verdicts on
        the saved brief and on a seat briefed between the two are refused."""
        landed = self._land_round("A = 2\n", f"feat({GREEN}): a is two")
        self.assertEqual(landed.returncode, 0, landed.stdout + landed.stderr)
        saved = self._landed_fp(landed)
        issued = Path(re.findall(r"^(/\S+\.txt)\nUNIT: ", self._brief().read_text(
            encoding="utf-8"), re.M)[-1])
        between, between_fp, _ = self._seat_brief()
        again, again_fp, _ = self._seat_brief(seat="qa")
        self.assertEqual(again_fp, saved, "the qa re-brief is not of the saved brief's scope")
        self.assertNotEqual(again, issued)
        rc, out, err = self._accept(GREEN, f"UNIT: {GREEN}\nBRIEF: {issued.stem}\n{APPROVE}",
                                    at=issued)
        self.assertIn(f"{GREEN}: APPROVE recorded, round 1, against brief {saved}", out, err)
        self.assertEqual(self._rows(GREEN)[-1][1:6:4], ["APPROVE", saved])
        rc, out, err = self._accept(GREEN, f"UNIT: {GREEN}\nBRIEF: {between.stem}\n{APPROVE}",
                                    at=between, reviewer=ENGINEER)
        self.assertIn(f"against brief {between_fp}", out, err)
        self.assertEqual(self._rows(GREEN)[-1][1:6:4], ["APPROVE", between_fp])

    def test_a_verdict_file_that_is_not_utf8_is_refused(self) -> None:
        """A verdict file the reader cannot decode is a refusal naming it, not a traceback."""
        self._qa_recorded()
        bad = self.root / "verdicts" / "latin1.txt"
        bad.parent.mkdir(parents=True, exist_ok=True)
        rows = self._rows(GREEN)
        bad.write_bytes(b"UNIT: " + GREEN.encode() + b"\nBRIEF: caf\xe9\n" + APPROVE.encode())
        out, err = base.io.StringIO(), base.io.StringIO()
        with base.contextlib.redirect_stdout(out), base.contextlib.redirect_stderr(err):
            rc = base.sprint.main(["lane", "accept", "--unit", GREEN, "--verdict", str(bad),
                                   "--reviewer", "qa-seat", "--root", str(self.root)])
        self.assertEqual(rc, 2, out.getvalue() + err.getvalue())
        self.assertIn("the verdict file cannot be read", err.getvalue())
        self.assertEqual(self._rows(GREEN), rows, "a verdict was recorded")


class SavedBriefDatingTests(unittest.TestCase):
    """The landing a saved QA brief is dated by when no note names a file it issued: one that
    names none, saved before verdict files, is dated by the last note of its fingerprint, and one
    naming a file no note records cannot be dated. A class of its own, beside the criterion's, so
    the criterion's selector stays inside the verifier's bound, on that class's fixture."""

    setUp = LaneAcceptSecondSeatBriefTests.setUp
    tearDown = LaneAcceptSecondSeatBriefTests.tearDown
    _accept = LaneAcceptSecondSeatBriefTests._accept
    _rows = LaneAcceptSecondSeatBriefTests._rows
    _land_round = LaneAcceptSecondSeatBriefTests._land_round
    _brief = LaneAcceptSecondSeatBriefTests._brief
    _landed_fp = LaneAcceptSecondSeatBriefTests._landed_fp
    _seat_brief = LaneAcceptSecondSeatBriefTests._seat_brief

    _rejoinder = base.LaneAcceptTests._rejoinder
    _round_one_rejected = base.LaneAcceptTests._round_one_rejected

    def _saved_stem(self) -> str:
        return re.findall(r"^BRIEF: (\S+)$", self._brief().read_text(encoding="utf-8"),
                          re.M)[-1]

    def test_a_saved_brief_naming_no_file_still_takes_a_rejoinder_after_its_landing(self):
        """MUTANT: a saved brief with no `BRIEF:` line, as a landing before verdict files left
        one, dated by no note (every rejoinder verdict is refused, the remedy too). As before
        verdict files, the last note of its fingerprint dates its landing: a rejoinder briefed
        before it is refused and one briefed after it is recorded."""
        _, prior = self._round_one_rejected()
        early, _, _ = self._rejoinder(prior)
        landed = self._land_round("A = 3\n", f"fix({GREEN}): a is three")
        self.assertEqual(landed.returncode, 0, landed.stdout + landed.stderr)
        saved = self._landed_fp(landed)
        older = critic.strip_verdict_file(self._brief().read_text(encoding="utf-8"))
        self._brief().write_text(older, encoding="utf-8")
        self.assertNotRegex(older, r"(?m)^BRIEF: ")
        self.assertEqual(critic.brief_fingerprint(older), saved)
        rows = self._rows(GREEN)
        rc, out, err = self._accept(GREEN, APPROVE, at=early)
        self.assertEqual((rc, self._rows(GREEN)), (2, rows), out + err)
        self.assertIn(f"{early} was issued by a rejoinder brief written before the last brief "
                      f"noted with sdlc-studio/.local/briefs/{GREEN}-qa.txt's fingerprint "
                      f"{saved}, taken as its landing since it names no file it issued", err)
        path, fp, tier = self._rejoinder(prior, "--tier", "full")
        rc, out, err = self._accept(GREEN, APPROVE, at=path)
        self.assertIn(f"{GREEN}: APPROVE recorded, round 2, against brief {fp} at the {tier} "
                      f"tier", out, err)
        self.assertEqual(self._rows(GREEN)[-1][1:6:4], ["APPROVE", fp])

    def test_a_saved_brief_naming_a_file_no_note_records_is_refused(self) -> None:
        """MUTANT: the issuing brief taken when no note names the file the saved brief issued
        (`landed_at is not None and n < landed_at`), so which round it answers is a guess. The
        landing's note is lost and a qa re-brief noted the saved brief's fingerprint since: the
        refusal says so, not that the seat's brief came before the landing, and the remedy it
        names records the verdict."""
        landed = self._land_round("A = 2\n", f"feat({GREEN}): a is two")
        self.assertEqual(landed.returncode, 0, landed.stdout + landed.stderr)
        saved = self._landed_fp(landed)
        stem, notes = self._saved_stem(), self.root / critic.BRIEF_NOTES_REL
        kept = [ln for ln in notes.read_text(encoding="utf-8").splitlines()
                if f"{stem}.txt" not in ln]
        self.assertLess(len(kept), len(notes.read_text(encoding="utf-8").splitlines()))
        notes.write_text("".join(f"{ln}\n" for ln in kept), encoding="utf-8")
        self.assertEqual(self._seat_brief(seat="qa")[1], saved, "the re-brief is of another scope")
        path, _, _ = self._seat_brief()
        rc, out, err = self._accept(GREEN, f"UNIT: {GREEN}\nBRIEF: {path.stem}\n{APPROVE}",
                                    at=path, reviewer=ENGINEER)
        self.assertEqual(rc, 2, out + err)
        self.assertFalse(critic.verdicts_path(self.root).exists(), "a verdict was recorded")
        rel = f"sdlc-studio/.local/briefs/{GREEN}-qa.txt"
        self.assertIn(f"{rel} names the brief file {stem}, which no note in "
                      f"{critic.BRIEF_NOTES_REL} records, so the landing that saved it cannot "
                      f"be placed before or after the brief that issued {path}", err)
        self.assertNotIn("written before", err)
        self.assertIn(f"run `critic.py brief --unit {GREEN} --seat qa` and save its output at "
                      f"{rel}, then brief the seat again with `critic.py brief --unit {GREEN} "
                      f"--seat engineering`", err)
        # positive control: the remedy it names
        done = subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / "critic.py"), "brief", "--unit", GREEN, "--seat",
             "qa", "--root", str(self.root)], capture_output=True, text=True, timeout=300,
            cwd=str(self.root), env=gitutil.git_env(), check=False)
        self.assertEqual(done.returncode, 0, done.stderr)
        self._brief().write_text(done.stdout, encoding="utf-8")
        path, fp, _ = self._seat_brief()
        rc, out, err = self._accept(GREEN, f"UNIT: {GREEN}\nBRIEF: {path.stem}\n{APPROVE}",
                                    at=path, reviewer=ENGINEER)
        self.assertIn(f"against brief {fp}", out, err)


if __name__ == "__main__":
    unittest.main()
