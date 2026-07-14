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



# ---------------------------------------------------------------------------
# Estimate vs actual: the loop only closes if an unmeasured unit says so.
# ---------------------------------------------------------------------------

BATCH_RETRO = """# RETRO-9000: a measured sprint

> **Date:** 2026-07-14
> **Batch:** BG0001, CR0001, CR0002
> **Goal:** close the loop

## Delivered
- BG0001 - fixed it
## What went well
- it was measured
## What was hard / what stalled
- nothing
## Lessons
- measure the units
## Actions raised
| Finding | Disposition |
| --- | --- |
| nothing to raise | declined: clean sprint |
"""

UNIT = """# {prefix}-{num}: a unit

> **Status:** Open
> **Severity:** Medium

## Summary
A unit of work.
"""


class AccuracyBase(unittest.TestCase):
    """A FIXTURE telemetry file, never the live one - a test that reads the project's own
    telemetry would pass or fail on what the project happened to do that day."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for d in ("retros", "bugs", "change-requests", ".local"):
            (self.root / "sdlc-studio" / d).mkdir(parents=True, exist_ok=True)
        (self.root / "sdlc-studio" / "retros" / "RETRO9000-t.md").write_text(
            BATCH_RETRO, encoding="utf-8")
        (self.root / "sdlc-studio" / "bugs" / "BG0001-a.md").write_text(
            UNIT.format(prefix="BG", num="0001"), encoding="utf-8")
        for n in ("0001", "0002"):
            (self.root / "sdlc-studio" / "change-requests" / f"CR{n}-a.md").write_text(
                UNIT.format(prefix="CR", num=n), encoding="utf-8")
        self.addCleanup(self.tmp.cleanup)

    def telemetry(self, *records: dict) -> None:
        import json as _json
        path = self.root / "sdlc-studio" / ".local" / "telemetry.jsonl"
        path.write_text("".join(_json.dumps(r) + "\n" for r in records), encoding="utf-8")

    def accuracy(self) -> dict:
        return retro.accuracy(str(self.root), "RETRO9000")

    def unit(self, res: dict, uid: str) -> dict:
        return next(u for u in res["units"] if u["id"] == uid)


class TheBatchIsMeasuredAgainstThePlan(AccuracyBase):
    def test_the_batch_field_names_the_units(self) -> None:
        self.assertEqual(retro.batch_ids(BATCH_RETRO), ["BG0001", "CR0001", "CR0002"])

    def test_an_unfilled_batch_placeholder_names_nothing(self) -> None:
        self.assertEqual(retro.batch_ids("> **Batch:** {{batch}}\n"), [])

    def test_per_unit_ratio_is_estimate_over_actual(self) -> None:
        """The estimate is the PLAN's model (sprint's constants), not a second copy of it."""
        import sprint
        self.telemetry(
            {"id": "BG0001", "type": "bug", "tokens": 50_000, "wall_time_s": 100},
            {"id": "CR0001", "type": "cr", "tokens": 25_000, "wall_time_s": 50},
            {"id": "CR0002", "type": "cr", "tokens": 100_000, "wall_time_s": 250},
        )
        res = self.accuracy()
        est = sprint.BASE_TOKEN_BUDGET  # no Affects -> complexity 0 -> the fixed floor
        self.assertEqual(self.unit(res, "BG0001")["estimate"], est)
        self.assertEqual(self.unit(res, "BG0001")["ratio"], round(est / 50_000, 2))
        self.assertEqual(self.unit(res, "CR0001")["ratio"], round(est / 25_000, 2))
        self.assertEqual(self.unit(res, "CR0002")["ratio"], round(est / 100_000, 2))
        self.assertEqual(self.unit(res, "BG0001")["wall_time_s"], 100)

    def test_batch_ratio_is_the_summed_estimate_over_the_summed_actual(self) -> None:
        import sprint
        self.telemetry(
            {"id": "BG0001", "type": "bug", "tokens": 50_000, "wall_time_s": 100},
            {"id": "CR0001", "type": "cr", "tokens": 25_000, "wall_time_s": 50},
            {"id": "CR0002", "type": "cr", "tokens": 100_000, "wall_time_s": 250},
        )
        res = self.accuracy()
        self.assertEqual(res["batch"]["estimate"], 3 * sprint.BASE_TOKEN_BUDGET)
        self.assertEqual(res["batch"]["actual_tokens"], 175_000)
        self.assertEqual(res["batch"]["ratio"],
                         round(3 * sprint.BASE_TOKEN_BUDGET / 175_000, 2))
        self.assertEqual(res["batch"]["wall_time_s"], 400)
        self.assertEqual((res["n_measured"], res["n_unmeasured"]), (3, 0))

    def test_a_later_bare_close_record_does_not_erase_the_measurement(self) -> None:
        """The loop appends a bare `{id, type}` record on close. Reading the LAST record
        wholesale would throw away the tokens the run actually reported."""
        self.telemetry(
            {"id": "BG0001", "type": "bug", "tokens": 50_000, "wall_time_s": 100},
            {"id": "BG0001", "type": "bug"},
        )
        self.assertEqual(self.unit(self.accuracy(), "BG0001")["actual_tokens"], 50_000)


class SilenceIsNotAMeasurement(AccuracyBase):
    """The load-bearing case. A unit with no telemetry must be reported UNMEASURED - never
    dropped from the list, never folded into the ratio. A silent skip lets a batch of three
    units with one measurement report as a fully measured, accurate sprint."""

    def test_a_unit_with_no_telemetry_is_reported_unmeasured(self) -> None:
        self.telemetry({"id": "BG0001", "type": "bug", "tokens": 50_000})
        res = self.accuracy()
        self.assertEqual(res["n_units"], 3, "an unmeasured unit must not vanish from the batch")
        self.assertEqual(res["n_measured"], 1)
        self.assertEqual(res["n_unmeasured"], 2)
        self.assertEqual(res["unmeasured"], ["CR0001", "CR0002"])
        for uid in ("CR0001", "CR0002"):
            u = self.unit(res, uid)
            self.assertEqual(u["state"], "unmeasured")
            self.assertIsNone(u["ratio"])
            self.assertIsNone(u["actual_tokens"])
            self.assertTrue(u["reason"])

    def test_an_unmeasured_unit_is_excluded_from_the_batch_ratio(self) -> None:
        """Not counted as accurate, and not counted as a miss either: its estimate must not
        land in the numerator with nothing under it."""
        import sprint
        self.telemetry({"id": "BG0001", "type": "bug", "tokens": 50_000})
        res = self.accuracy()
        self.assertEqual(res["batch"]["estimate"], sprint.BASE_TOKEN_BUDGET,
                         "the unmeasured units' estimates must stay out of the ratio")
        self.assertEqual(res["batch"]["actual_tokens"], 50_000)

    def test_a_record_with_no_token_value_is_not_a_measurement(self) -> None:
        """330 telemetry records exist with wall-clock and no tokens. A record is not a token
        measurement just because it exists."""
        self.telemetry({"id": "BG0001", "type": "bug", "wall_time_s": 100})
        u = self.unit(self.accuracy(), "BG0001")
        self.assertEqual(u["state"], "unmeasured")

    def test_a_wholly_unmeasured_batch_reports_no_ratio(self) -> None:
        self.telemetry()
        res = self.accuracy()
        self.assertEqual(res["n_measured"], 0)
        self.assertIsNone(res["batch"]["ratio"], "zero measurements must not report an accuracy")

    def test_the_written_block_says_unmeasured_out_loud(self) -> None:
        self.telemetry({"id": "BG0001", "type": "bug", "tokens": 50_000})
        block = retro.accuracy_block(self.accuracy())
        self.assertIn("UNMEASURED", block)
        self.assertIn("1 of 3 unit(s) measured", block)


class TheRetroCarriesTheReport(AccuracyBase):
    def test_write_inserts_the_section_and_is_idempotent(self) -> None:
        self.telemetry({"id": "BG0001", "type": "bug", "tokens": 50_000})
        res = self.accuracy()
        path = retro.write_accuracy(str(self.root), res)
        first = path.read_text(encoding="utf-8")
        self.assertIn("## Estimate vs actual", first)
        self.assertIn("| BG0001 |", first)
        self.assertIn("## Actions raised", first, "the rest of the retro must survive")
        retro.write_accuracy(str(self.root), retro.accuracy(str(self.root), "RETRO9000"))
        second = path.read_text(encoding="utf-8")
        self.assertEqual(first.count(retro.ACCURACY_BEGIN), 1)
        self.assertEqual(second.count(retro.ACCURACY_BEGIN), 1, "a refresh must not duplicate")

    def test_a_refresh_keeps_the_authors_prose(self) -> None:
        """The section holds the human's reading of the numbers. A tool that ate the analysis
        on every refresh would teach people not to run it."""
        self.telemetry({"id": "BG0001", "type": "bug", "tokens": 50_000})
        retro.write_accuracy(str(self.root), self.accuracy())
        path = self.root / "sdlc-studio" / "retros" / "RETRO9000-t.md"
        path.write_text(path.read_text(encoding="utf-8").replace(
            retro.ACCURACY_END, retro.ACCURACY_END + "\n\n- the estimator is too generous\n"),
            encoding="utf-8")
        retro.write_accuracy(str(self.root), retro.accuracy(str(self.root), "RETRO9000"))
        self.assertIn("- the estimator is too generous", path.read_text(encoding="utf-8"))

    def test_validate_still_passes_a_retro_carrying_the_new_section(self) -> None:
        """The new section is not a required one: adding it must not fail every retro that
        predates it, and carrying it must not fail the gate."""
        self.telemetry({"id": "BG0001", "type": "bug", "tokens": 50_000})
        retro.write_accuracy(str(self.root), self.accuracy())
        self.assertTrue(retro.validate(str(self.root), "RETRO9000")["ok"])


class TheVelocityHistoryAccumulates(AccuracyBase):
    """The history the next plan reads. One row per sprint, keyed by retro id."""

    def test_a_row_is_appended_and_read_back(self) -> None:
        import sprint
        self.telemetry({"id": "BG0001", "type": "bug", "tokens": 50_000, "wall_time_s": 100})
        retro.record_velocity(str(self.root), self.accuracy())
        hist = retro.velocity_history(str(self.root))
        self.assertEqual(len(hist), 1)
        row = hist[0]
        self.assertEqual(row["id"], "RETRO9000")
        self.assertEqual(row["date"], "2026-07-14")
        self.assertEqual((row["units"], row["measured"]), (3, 1))
        self.assertEqual(row["estimate"], sprint.BASE_TOKEN_BUDGET)
        self.assertEqual(row["actual_tokens"], 50_000)
        self.assertEqual(row["ratio"], 1.0)

    def test_re_running_a_sprint_corrects_its_row_rather_than_duplicating_it(self) -> None:
        self.telemetry({"id": "BG0001", "type": "bug", "tokens": 50_000})
        retro.record_velocity(str(self.root), self.accuracy())
        self.telemetry(
            {"id": "BG0001", "type": "bug", "tokens": 50_000},
            {"id": "CR0001", "type": "cr", "tokens": 50_000},
        )
        retro.record_velocity(str(self.root), self.accuracy())
        hist = retro.velocity_history(str(self.root))
        self.assertEqual(len(hist), 1, "a sprint must not be counted twice")
        self.assertEqual(hist[0]["measured"], 2)

    def test_two_sprints_accumulate(self) -> None:
        self.telemetry({"id": "BG0001", "type": "bug", "tokens": 50_000})
        retro.record_velocity(str(self.root), self.accuracy())
        other = BATCH_RETRO.replace("RETRO-9000", "RETRO-9001")
        (self.root / "sdlc-studio" / "retros" / "RETRO9001-t.md").write_text(
            other, encoding="utf-8")
        retro.record_velocity(str(self.root), retro.accuracy(str(self.root), "RETRO9001"))
        self.assertEqual([r["id"] for r in retro.velocity_history(str(self.root))],
                         ["RETRO9000", "RETRO9001"])

    def test_no_history_yet_is_an_empty_list_not_a_crash(self) -> None:
        self.assertEqual(retro.velocity_history(str(self.root)), [])

if __name__ == "__main__":
    unittest.main()
