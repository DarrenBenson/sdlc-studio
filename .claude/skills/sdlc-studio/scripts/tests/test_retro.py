"""The retro spine: content validation, disposition, and lesson extraction.

BG0123: the gate's retro leg globbed for a filename, so a 0-byte `RETRO9999.md` returned
`[PASS] retro: batch retro RETRO9999 present`. The one gate that made the retrospective
un-skippable was the one an agent could satisfy with `touch`.

The tests that matter here are NOT the empty-file one. A guard that only catches the total
case is not a guard (LL0015), and the total case is the one that never happens - people who
skip a ceremony under a gate produce the artefact, they do not omit it. So the load-bearing
tests are the partial dodges: a retro that looks complete but left its `{{placeholder}}` in,
left a finding undecided, or declined without giving a reason.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import retro  # noqa: E402

FULL = """# RETRO-9999: a sprint
## Delivered
- US0001 - shipped it
## What went well
- the gate caught it
## What was hard / what stalled
- the deploy was slow
## Lessons
- deploys need a preflight check
## Actions raised
| Finding | Disposition |
| --- | --- |
| the deploy was slow | BG0125 |
| flaky test in CI | declined: tracked upstream, not ours to fix |
"""


class RetroBase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "sdlc-studio" / "retros").mkdir(parents=True)
        self.addCleanup(self.tmp.cleanup)

    def write(self, text: str, rid: str = "RETRO9999") -> None:
        (self.root / "sdlc-studio" / "retros" / f"{rid}-t.md").write_text(text, encoding="utf-8")

    def validate(self, rid: str = "RETRO9999") -> dict:
        return retro.validate(str(self.root), rid)


class ContentIsChecked(RetroBase):
    def test_missing_file_fails(self) -> None:
        self.assertFalse(self.validate()["ok"])

    def test_empty_file_fails(self) -> None:
        """BG0123 itself: the 0-byte file that used to PASS."""
        self.write("")
        res = self.validate()
        self.assertFalse(res["ok"])
        self.assertTrue(any("Actions raised" in e for e in res["errors"]))

    def test_a_complete_retro_passes(self) -> None:
        """The guard must also let the good case through - one that never passes is not a
        gate, it is a wall."""
        self.write(FULL)
        res = self.validate()
        self.assertTrue(res["ok"], res["errors"])
        self.assertEqual(res["lessons"], ["deploys need a preflight check"])
        self.assertEqual(res["filed"], ["BG0125"])
        self.assertEqual(len(res["declined"]), 1)

    def test_a_dropped_section_fails(self) -> None:
        self.write(FULL.replace("## Lessons\n- deploys need a preflight check\n", ""))
        res = self.validate()
        self.assertFalse(res["ok"])
        self.assertTrue(any("'## Lessons'" in e for e in res["errors"]))


class TheDodgesAreCaught(RetroBase):
    """The cases that actually happen: the ceremony performed, the question dodged."""

    def test_placeholder_lesson_is_not_a_lesson(self) -> None:
        self.write(FULL.replace("- deploys need a preflight check", "- {{lesson}}"))
        res = self.validate()
        self.assertFalse(res["ok"])
        self.assertTrue(any("no lesson recorded" in e for e in res["errors"]))

    def test_undecided_finding_blocks(self) -> None:
        self.write(FULL.replace("| BG0125 |", "| {{BG0123 / CR0456 / declined: why not}} |"))
        res = self.validate()
        self.assertFalse(res["ok"])
        self.assertTrue(any("not dispositioned" in e for e in res["errors"]))

    def test_bare_declined_without_a_reason_blocks(self) -> None:
        """Decline is first-class, but it must carry a reason. 'declined' alone is silence
        wearing a decision's clothes."""
        self.write(FULL.replace("| BG0125 |", "| declined |"))
        res = self.validate()
        self.assertFalse(res["ok"])
        self.assertTrue(any("not dispositioned" in e for e in res["errors"]))

    def test_declined_with_a_reason_is_green(self) -> None:
        """Honesty must cost exactly what noise costs, or the gate teaches people to file
        rubbish to get green (RFC0032 D1)."""
        self.write(FULL.replace("| BG0125 |", "| declined: not worth an artefact this sprint |"))
        self.assertTrue(self.validate()["ok"])

    def test_empty_actions_table_blocks(self) -> None:
        """The question must be ANSWERED. An empty table is not 'no'."""
        self.write(FULL.split("## Actions raised")[0] + "## Actions raised\n\n| Finding | Disposition |\n| --- | --- |\n")
        res = self.validate()
        self.assertFalse(res["ok"])
        self.assertTrue(any("no rows" in e for e in res["errors"]))


class Extraction(RetroBase):
    def test_lessons_are_lifted_from_the_retro(self) -> None:
        self.write(FULL)
        self.assertEqual(retro.lessons_in(FULL), ["deploys need a preflight check"])

    def test_placeholder_bullets_are_not_lessons(self) -> None:
        self.assertEqual(retro.lessons_in("## Lessons\n- {{lesson}}\n"), [])

    def test_html_comment_guidance_is_not_a_lesson(self) -> None:
        """The template's own inline guidance must not be extracted as content."""
        self.assertEqual(retro.lessons_in("## Lessons\n- <!-- record it: lessons add -->\n"), [])


class GateUsesTheContentCheck(RetroBase):
    """The fix must hold at the PUBLIC path, not just in the helper (LL0024)."""

    def test_gate_leg_fails_the_empty_retro(self) -> None:
        import gate
        self.write("")
        res = gate._retro_present(str(self.root), "RETRO9999")
        self.assertGreater(res["count"], 0, "the 0-byte retro must FAIL the gate leg (BG0123)")

    def test_gate_leg_passes_a_complete_retro(self) -> None:
        import gate
        self.write(FULL)
        res = gate._retro_present(str(self.root), "RETRO9999")
        self.assertEqual(res["count"], 0, res["detail"])


class TheOptOutIsHonoured(unittest.TestCase):
    """`lessons.loop: judgement` mirrors the engagement floor's opt-out: the lane still
    REPORTS, it just does not block. A documented setting that nothing reads would be the very
    disease this loop exists to cure."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "sdlc-studio" / "retros").mkdir(parents=True)
        (self.root / "sdlc-studio" / "retros" / "RETRO0001-t.md").write_text("", encoding="utf-8")
        self.addCleanup(self.tmp.cleanup)

    def _leg(self) -> dict:
        import gate
        return gate._retro_present(str(self.root), "RETRO0001")

    def test_enforce_is_the_default_and_blocks(self) -> None:
        leg = self._leg()
        self.assertTrue(leg["blocking"])
        self.assertGreater(leg["count"], 0)

    def test_judgement_reports_but_does_not_block(self) -> None:
        (self.root / "sdlc-studio" / ".config.yaml").write_text(
            "lessons:\n  loop: judgement\n", encoding="utf-8")
        leg = self._leg()
        self.assertFalse(leg["blocking"], "the documented opt-out must actually opt out")
        self.assertGreater(leg["count"], 0, "advisory must still REPORT - silence is not an opt-out")

class ALessonIsAValidDisposition(RetroBase):
    """Some findings are not tickets. The right outcome is a habit, and a habit's durable form
    is a recorded lesson - so an `LL` id disposes of a finding.

    Found by dogfooding: the first retro written with this tool disposed of a finding by
    recording LL0024, and the gate refused it. Refusing would push such findings toward a
    decline (which loses the lesson) or a make-work CR (which is the noise the decline path
    exists to prevent). It is no cheaper to game than declining, which is already free.
    """

    def test_a_lesson_id_disposes_of_a_finding(self) -> None:
        self.write(FULL.replace("| BG0125 |", "| LL0024 - recorded as a cross-project lesson |"))
        res = self.validate()
        self.assertTrue(res["ok"], res["errors"])
        self.assertIn("LL0024", res["filed"])

    def test_declined_for_now_is_not_declined(self) -> None:
        """A disposition must be machine-verifiable. 'declined for now:' reads like a decision
        to a human and is not one to the gate - which is the point: prose that only looks like
        an answer is how findings rot."""
        self.write(FULL.replace("| BG0125 |", "| declined for now: we might revisit |"))
        self.assertFalse(self.validate()["ok"])


class AnExplicitDeclineBeatsAnIdInItsReason(RetroBase):
    """A decline routinely cites the work it defers to: 'declined: belongs to RFC0034
    (CR0257)'. Classifying that as FILED because it contains an id reports the finding as
    ticketed when it was deliberately not - the tally lies in exactly the direction that
    flatters the sprint. The explicit prefix must win.

    Found by dogfooding: the first retro run reported '2 filed, 1 declined' for what was
    1 filed and 2 declined.
    """

    def test_a_decline_citing_an_artefact_id_is_declined_not_filed(self) -> None:
        rows = retro.dispositions_in(
            FULL.replace("| BG0125 |", "| declined: belongs to RFC0034 (CR0257) |"))
        row = next(r for r in rows if r["finding"] == "the deploy was slow")
        self.assertEqual(row["state"], "declined", row)
        self.assertEqual(row["detail"], "belongs to RFC0034 (CR0257)")

    def test_the_tally_counts_it_as_declined(self) -> None:
        """The fix must hold at the PUBLIC path, not just in the helper (LL0024)."""
        self.write(FULL.replace("| BG0125 |", "| declined: belongs to RFC0034 (CR0257) |"))
        res = self.validate()
        self.assertTrue(res["ok"], res["errors"])
        self.assertEqual(res["filed"], [])
        self.assertEqual(len(res["declined"]), 2)

    def test_a_bare_artefact_id_is_still_filed(self) -> None:
        rows = retro.dispositions_in(FULL)
        row = next(r for r in rows if r["finding"] == "the deploy was slow")
        self.assertEqual(row["state"], "filed")
        self.assertEqual(row["detail"], "BG0125")

    def test_an_id_with_prose_is_still_filed(self) -> None:
        rows = retro.dispositions_in(
            FULL.replace("| BG0125 |", "| LL0024 - recorded as a lesson |"))
        row = next(r for r in rows if r["finding"] == "the deploy was slow")
        self.assertEqual(row["state"], "filed")
        self.assertEqual(row["detail"], "LL0024")

    def test_a_bare_declined_is_still_undecided(self) -> None:
        rows = retro.dispositions_in(FULL.replace("| BG0125 |", "| declined |"))
        row = next(r for r in rows if r["finding"] == "the deploy was slow")
        self.assertEqual(row["state"], "undecided")

    def test_a_plain_decline_is_still_declined(self) -> None:
        rows = retro.dispositions_in(
            FULL.replace("| BG0125 |", "| declined: not worth an artefact this sprint |"))
        row = next(r for r in rows if r["finding"] == "the deploy was slow")
        self.assertEqual(row["state"], "declined")
        self.assertEqual(row["detail"], "not worth an artefact this sprint")

    def test_a_placeholder_is_still_undecided(self) -> None:
        rows = retro.dispositions_in(
            FULL.replace("| BG0125 |", "| {{BG0123 / declined: why not}} |"))
        row = next(r for r in rows if r["finding"] == "the deploy was slow")
        self.assertEqual(row["state"], "undecided")


if __name__ == "__main__":
    unittest.main()
