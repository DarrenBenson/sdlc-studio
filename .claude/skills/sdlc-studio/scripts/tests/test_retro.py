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
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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


WRAPPED = """# RETRO-9999: a sprint
## Delivered
- US0001 - shipped it
## What went well
- fine
## What was hard / what stalled
- nothing
## Lessons
- A plausible story fitted to a real pattern is not a finding. This retro originally recorded that
  the estimator was mis-calibrated, which was a story, not a measurement - the seed correlates
  with cost at r = +0.03.
- deploys need a preflight check

Some prose after the list, which is not a lesson.
## Actions raised
| Finding | Disposition |
| --- | --- |
| nothing | declined: clean sprint |
"""


class ALessonIsTitledFromItsSentenceNotItsLine(RetroBase):
    """A lesson wrapped across three lines was read as its FIRST LINE - so the store held a
    third of it, and the headline stopped mid-clause ("...This retro originally recorded that").
    Those headlines are what `sprint plan` prints as the lessons digest at the top of every plan:
    the surface the whole learning loop exists to serve, and the one an agent under effort
    pressure reads instead of opening the file. A headline that stops mid-clause is skimmed past.

    The defect is invisible unless a lesson happens to be long, which is why it survived - so the
    fixture here is deliberately a WRAPPED one.
    """

    def test_a_wrapped_lesson_is_read_whole_not_to_the_first_line_break(self) -> None:
        found = retro.lessons_in(WRAPPED)
        self.assertEqual(len(found), 2)
        self.assertIn("r = +0.03", found[0], "the rest of the lesson was lost at the wrap")
        self.assertNotIn("\n", found[0])

    def test_the_title_is_the_complete_first_sentence(self) -> None:
        title = retro.lesson_title(retro.lessons_in(WRAPPED)[0])
        self.assertEqual(title, "A plausible story fitted to a real pattern is not a finding.")

    def test_the_title_does_not_depend_on_where_the_author_wrapped(self) -> None:
        """The load-bearing property. Re-wrap the same lesson anywhere and the headline is the
        same headline."""
        one = "- One sentence that is long. And a second one here.\n"
        two = "- One sentence that\n  is long. And a second one here.\n"
        self.assertEqual(retro.lesson_title(retro.lessons_in(f"## Lessons\n{one}")[0]),
                         retro.lesson_title(retro.lessons_in(f"## Lessons\n{two}")[0]))

    def test_prose_after_the_list_is_not_folded_into_the_last_lesson(self) -> None:
        self.assertNotIn("Some prose", " ".join(retro.lessons_in(WRAPPED)))

    def test_an_abbreviation_or_a_decimal_does_not_end_the_sentence(self) -> None:
        self.assertEqual(retro.lesson_title("Check the seed, e.g. max_cognitive, first. Then fit."),
                         "Check the seed, e.g. max_cognitive, first.")
        self.assertEqual(retro.lesson_title("It scored r = 0.03. Not weak - nothing."),
                         "It scored r = 0.03.")

    def test_a_single_sentence_lesson_is_its_own_title_so_the_store_does_not_churn(self) -> None:
        self.assertEqual(retro.lesson_title("deploys need a preflight check"),
                         "deploys need a preflight check")

    def test_the_stored_body_keeps_the_whole_lesson(self) -> None:
        """The headline is a headline. The record is not truncated to it."""
        self.write(WRAPPED)
        args = mock.Mock(root=str(self.root), id="RETRO9999", dry_run=False, format="text")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(retro.cmd_extract(args), 0)
        import lessons as lessons_mod
        text = lessons_mod.default_project_file(str(self.root)).read_text(encoding="utf-8")
        self.assertIn("## L-0001: A plausible story fitted to a real pattern is not a finding.",
                      text)
        self.assertIn("r = +0.03", text, "the body must keep the full text, not just the title")


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

    #: The estimator that forecast these fixtures. A LITERAL, not sprint's live constants: a
    #: test that read the constants would move with them, which is the defect under test.
    CONSTANTS = {"BASE_TOKEN_BUDGET": 50_000, "TOKENS_PER_COGNITIVE": 600}
    EST = 50_000  # the forecast recorded for each fixture unit

    def telemetry(self, *records: dict) -> None:
        path = self.root / "sdlc-studio" / ".local" / "telemetry.jsonl"
        path.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")

    def forecast(self, *unit_ids: str, tokens: int | None = None,
                 points: dict[str, int] | None = None) -> None:
        """The plan-time forecast, as `sprint plan` records it. A unit without one is
        UNFORECAST and has no prediction to judge - which is a case in its own right.

        `points` is the SIZE the plan recorded. A unit with no recorded points is unsized, and
        nothing invents one for it from the artefact as it stands today."""
        import telemetry as tel
        tel.record_forecasts(str(self.root), [
            {"id": uid, "tokens": tokens if tokens is not None else self.EST,
             "points": (points or {}).get(uid),
             "seed": 0, "seed_source": "none", "constants": dict(self.CONSTANTS),
             "planned_at": "2026-07-14T09:00:00+00:00"} for uid in unit_ids])

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
        """The estimate is the forecast the PLAN recorded, read back verbatim."""
        self.forecast("BG0001", "CR0001", "CR0002")
        self.telemetry(
            {"id": "BG0001", "type": "bug", "tokens": 50_000, "wall_time_s": 100},
            {"id": "CR0001", "type": "cr", "tokens": 25_000, "wall_time_s": 50},
            {"id": "CR0002", "type": "cr", "tokens": 100_000, "wall_time_s": 250},
        )
        res = self.accuracy()
        est = self.EST
        self.assertEqual(self.unit(res, "BG0001")["estimate"], est)
        self.assertEqual(self.unit(res, "BG0001")["ratio"], round(est / 50_000, 2))
        self.assertEqual(self.unit(res, "CR0001")["ratio"], round(est / 25_000, 2))
        self.assertEqual(self.unit(res, "CR0002")["ratio"], round(est / 100_000, 2))
        self.assertEqual(self.unit(res, "BG0001")["wall_time_s"], 100)

    def test_batch_ratio_is_the_summed_estimate_over_the_summed_actual(self) -> None:
        self.forecast("BG0001", "CR0001", "CR0002")
        self.telemetry(
            {"id": "BG0001", "type": "bug", "tokens": 50_000, "wall_time_s": 100},
            {"id": "CR0001", "type": "cr", "tokens": 25_000, "wall_time_s": 50},
            {"id": "CR0002", "type": "cr", "tokens": 100_000, "wall_time_s": 250},
        )
        res = self.accuracy()
        self.assertEqual(res["batch"]["estimate"], 3 * self.EST)
        self.assertEqual(res["batch"]["actual_tokens"], 175_000)
        self.assertEqual(res["batch"]["ratio"], round(3 * self.EST / 175_000, 2))
        self.assertEqual(res["batch"]["wall_time_s"], 400)
        self.assertEqual((res["n_measured"], res["n_unmeasured"]), (3, 0))
        self.assertEqual(res["n_forecast"], 3)

    def test_a_later_bare_close_record_does_not_erase_the_measurement(self) -> None:
        """The loop appends a bare `{id, type}` record on close. Reading the LAST record
        wholesale would throw away the tokens the run actually reported."""
        self.forecast("BG0001")
        self.telemetry(
            {"id": "BG0001", "type": "bug", "tokens": 50_000, "wall_time_s": 100},
            {"id": "BG0001", "type": "bug"},
        )
        self.assertEqual(self.unit(self.accuracy(), "BG0001")["actual_tokens"], 50_000)


class SilenceIsNotAMeasurement(AccuracyBase):
    """The load-bearing case. A unit with no telemetry must be reported UNMEASURED - never
    dropped from the list, never folded into the ratio. A silent skip lets a batch of three
    units with one measurement report as a fully measured, accurate sprint."""

    def setUp(self) -> None:
        super().setUp()
        # Every unit WAS forecast at plan time. What varies here is whether it was measured.
        self.forecast("BG0001", "CR0001", "CR0002")

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
        self.telemetry({"id": "BG0001", "type": "bug", "tokens": 50_000})
        res = self.accuracy()
        self.assertEqual(res["batch"]["estimate"], self.EST,
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
    def setUp(self) -> None:
        super().setUp()
        self.forecast("BG0001", "CR0001", "CR0002")

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

    def setUp(self) -> None:
        super().setUp()
        self.forecast("BG0001", "CR0001", "CR0002")

    def test_a_row_is_appended_and_read_back(self) -> None:
        self.telemetry({"id": "BG0001", "type": "bug", "tokens": 50_000, "wall_time_s": 100})
        retro.record_velocity(str(self.root), self.accuracy())
        hist = retro.velocity_history(str(self.root))
        self.assertEqual(len(hist), 1)
        row = hist[0]
        self.assertEqual(row["id"], "RETRO9000")
        self.assertEqual(row["date"], "2026-07-14")
        self.assertEqual((row["units"], row["measured"]), (3, 1))
        self.assertEqual(row["estimate"], self.EST)
        self.assertEqual(row["actual_tokens"], 50_000)
        self.assertEqual(row["ratio"], 1.0)

    def test_the_row_records_the_constants_that_produced_the_forecast(self) -> None:
        """Without them the row cannot say WHICH estimator its ratio judges, and a reader is
        left to assume it was the one in force - which is how training error gets quoted as
        validation."""
        self.telemetry({"id": "BG0001", "type": "bug", "tokens": 50_000})
        retro.record_velocity(str(self.root), self.accuracy())
        row = retro.velocity_history(str(self.root))[0]
        self.assertEqual(row["constants"], self.CONSTANTS)
        self.assertEqual(row["forecast"], 3, "the coverage of the ESTIMATE side is recorded too")

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


# ---------------------------------------------------------------------------
# VELOCITY IS MEASURED IN POINTS, and the rate is DERIVED from that history.
# ---------------------------------------------------------------------------
# The load-bearing pair. A rate that is written down as a constant decays into an article of
# faith the moment the project changes; this one is a QUOTIENT of two things the history
# records, so it is re-measured every sprint and cannot drift away from the evidence.

class VelocityIsMeasuredInPoints(AccuracyBase):
    """Points delivered per sprint - the number an agile team actually plans with - and the
    tokens-per-point rate read back OUT of that history, never a constant."""

    def test_points_delivered_are_recorded_and_the_rate_is_derived_from_them(self) -> None:
        self.forecast("BG0001", "CR0001", "CR0002", points={"BG0001": 2, "CR0001": 3,
                                                            "CR0002": 5})
        self.telemetry(
            {"id": "BG0001", "type": "bug", "tokens": 50_000, "model": "m1"},
            {"id": "CR0001", "type": "cr", "tokens": 75_000, "model": "m1"},
            {"id": "CR0002", "type": "cr", "tokens": 125_000, "model": "m1"},
        )
        res = self.accuracy()
        self.assertEqual(res["batch"]["points"], 10)
        retro.record_velocity(str(self.root), res)

        row = retro.velocity_history(str(self.root))[0]
        self.assertEqual(row["points"], 10, "the sprint's velocity, in points")
        self.assertEqual(row["actual_tokens"], 250_000)

        # The rate is a quotient of the history, and it matches the measured actuals exactly.
        rate = retro.measured_rate(str(self.root))
        self.assertEqual(rate["by_model"]["m1"]["tokens_per_point"], 25_000)
        self.assertEqual(rate["by_model"]["m1"]["points"], 10)
        self.assertEqual(rate["tokens_per_point"], 25_000)
        self.assertEqual(res["batch"]["oversized"], [],
                         "every unit was at or below the threshold - nothing to flag")

    def test_a_history_with_no_points_yields_no_rate_and_invents_nothing(self) -> None:
        """The whole guard against a hardcoded constant: with nothing measured there is no
        rate, and the report says so rather than quoting a number from somewhere else."""
        self.forecast("BG0001")
        self.telemetry({"id": "BG0001", "type": "bug", "tokens": 50_000, "model": "m1"})
        retro.record_velocity(str(self.root), self.accuracy())
        rate = retro.measured_rate(str(self.root))
        self.assertIsNone(rate["tokens_per_point"])
        self.assertEqual(rate["by_model"], {})

    def test_the_rate_is_never_pooled_across_models(self) -> None:
        self.forecast("BG0001", "CR0001", points={"BG0001": 2, "CR0001": 2})
        self.telemetry(
            {"id": "BG0001", "type": "bug", "tokens": 40_000, "model": "small"},
            {"id": "CR0001", "type": "cr", "tokens": 40_000, "model": "large"},
        )
        retro.record_velocity(str(self.root), self.accuracy())
        rate = retro.measured_rate(str(self.root))
        self.assertIsNone(rate["tokens_per_point"],
                          "a rate pooled across two models describes neither of them")
        self.assertTrue(rate["refused"])

    def test_the_rate_is_tagged_with_the_project_its_cell_belongs_to(self) -> None:
        """CR0270: the rate is a per-(project, model) quantity. A single VELOCITY.md is one
        project, resolved from the repo and stamped on the result and every cell, so a figure
        lifted out of here is never mistaken for a different project's."""
        import telemetry as tel
        self.forecast("BG0001", "CR0001", points={"BG0001": 2, "CR0001": 3})
        self.telemetry(
            {"id": "BG0001", "type": "bug", "tokens": 50_000, "model": "m1"},
            {"id": "CR0001", "type": "cr", "tokens": 75_000, "model": "m1"},
        )
        retro.record_velocity(str(self.root), self.accuracy())
        rate = retro.measured_rate(str(self.root))
        project = tel.project_name(str(self.root))
        self.assertEqual(rate["project"], project)
        self.assertEqual(rate["by_model"]["m1"]["project"], project)

    def test_an_old_row_survives_the_points_columns(self) -> None:
        """LL0028: the migration is ATTACKED, not re-read. A VELOCITY.md written before points
        existed must keep every number it recorded when a new row is appended beside it."""
        legacy = (
            "# Velocity history\n\n"
            "| Retro | Date | Units | Measured | Forecast | Estimate (tokens, plan-time) | "
            "Actual (tokens) | Ratio (est/actual) | Wall (s) | Constants | Sample | Model |\n"
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
            "| RETRO0024 | 2026-07-14 | 6 | 6 | 6 | 1,285,000 | 384,278 | 3.34x | 1,848 | "
            "base=50000 tpc=5000 | in-sample | claude-opus-4-8 |\n")
        retro.velocity_path(str(self.root)).write_text(legacy, encoding="utf-8")

        self.forecast("BG0001", points={"BG0001": 2})
        self.telemetry({"id": "BG0001", "type": "bug", "tokens": 50_000, "model": "m1"})
        retro.record_velocity(str(self.root), self.accuracy())

        rows = {r["id"]: r for r in retro.velocity_history(str(self.root))}
        old = rows["RETRO0024"]
        self.assertEqual((old["units"], old["measured"], old["forecast"]), (6, 6, 6))
        self.assertEqual((old["estimate"], old["actual_tokens"]), (1_285_000, 384_278))
        self.assertEqual(old["ratio"], 3.34)
        self.assertEqual(old["wall_time_s"], 1848)
        self.assertEqual(old["constants"],
                         {"BASE_TOKEN_BUDGET": 50_000, "TOKENS_PER_COGNITIVE": 5_000})
        self.assertEqual(old["model"], "claude-opus-4-8")
        self.assertIsNone(old["points"], "a sprint that recorded no points reports none")
        self.assertEqual(rows["RETRO9000"]["points"], 2)


class AUnitAboveTheSplitThresholdIsFlagged(AccuracyBase):
    """A 13 is a legal estimate and a TRIAGE failure. The retro says so, with the evidence:
    its tokens-per-point against the rest of the batch. That is what makes the decomposition
    rule answerable each sprint instead of an article of faith."""

    def setUp(self) -> None:
        super().setUp()
        self.forecast("BG0001", "CR0001", "CR0002",
                      points={"BG0001": 3, "CR0001": 5, "CR0002": 13})
        self.telemetry(
            {"id": "BG0001", "type": "bug", "tokens": 75_000, "model": "m1"},
            {"id": "CR0001", "type": "cr", "tokens": 125_000, "model": "m1"},
            {"id": "CR0002", "type": "cr", "tokens": 130_000, "model": "m1"},
        )

    def test_the_oversized_unit_is_named_with_its_rate(self) -> None:
        b = self.accuracy()["batch"]
        over = b["oversized"]
        self.assertEqual([u["id"] for u in over], ["CR0002"])
        self.assertEqual(over[0]["points"], 13)
        self.assertEqual(over[0]["tokens_per_point"], 10_000)
        # And the rate of everything else, to price the miss against.
        self.assertEqual(b["tokens_per_point_within"], 25_000)

    def test_the_written_retro_says_it_should_have_been_split(self) -> None:
        block = retro.accuracy_block(self.accuracy())
        self.assertIn("CR0002", block)
        self.assertIn("should have been split", block.lower())
        self.assertIn("10,000", block, "its tokens-per-point is stated, not merely asserted")
        self.assertIn("25,000", block, "against the rate of the units at or below the threshold")

    def test_the_oversized_unit_still_counts_toward_the_velocity(self) -> None:
        """It is flagged, not disqualified. The team delivered 21 points; the sprint's rate is
        dragged by the 13, and the row says which units dragged it."""
        res = self.accuracy()
        self.assertEqual(res["batch"]["points"], 21)
        retro.record_velocity(str(self.root), res)
        self.assertEqual(retro.velocity_history(str(self.root))[0]["oversized"], 1)


# ---------------------------------------------------------------------------
# BG0133: the estimate is what was PREDICTED, never what is now computed.
# ---------------------------------------------------------------------------

PLANNED_RETRO = """# RETRO-9100: a planned sprint

> **Date:** 2026-07-15
> **Batch:** CR0101, CR0102

## Delivered
- CR0101 - shipped
## What went well
- it was planned and measured
## What was hard / what stalled
- nothing
## Lessons
- record the forecast when it is made
## Actions raised
| Finding | Disposition |
| --- | --- |
| nothing to raise | declined: clean sprint |
"""

# A source file the groomed CR points its Affects at, so the batch has something to touch.
COMPLEX_SRC = """def f(a, b, c):
    for i in range(a):
        if i > b:
            while c:
                if i % 2:
                    c -= 1
                else:
                    break
        elif i < c:
            try:
                b += i
            except ValueError:
                b = 0
    return b
"""

GROOMED_CR = """# CR-{num}: a unit

> **Status:** Proposed
> **Priority:** Medium
> **Affects:** src/{name}.py
> **Points:** 3

## Summary
A unit of work.
"""


class TheEstimateIsTheOneThatWasPredicted(unittest.TestCase):
    """BG0133, the load-bearing case.

    Plan a batch through the PUBLIC path, then CHANGE the forecast constants, then run
    `accuracy`. The reported estimate must be UNMOVED. If moving the constants moves a past
    sprint's estimate, the loop is re-deriving the forecast at judgement time from the very
    constants it is meant to be judging, and it can never falsify its own estimator - which is
    exactly how a recorded 5.2x miss was erased by the recalibration it caused.
    """

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        (self.root / "sdlc-studio" / "retros").mkdir(parents=True)
        (self.root / "sdlc-studio" / ".local").mkdir(parents=True)
        crs = self.root / "sdlc-studio" / "change-requests"
        crs.mkdir(parents=True)
        src = self.root / "src"
        src.mkdir()
        for num, name in (("0101", "a"), ("0102", "b")):
            (src / f"{name}.py").write_text(COMPLEX_SRC, encoding="utf-8")
            (crs / f"CR{num}-x.md").write_text(
                GROOMED_CR.format(num=num, name=name), encoding="utf-8")
        (self.root / "sdlc-studio" / "retros" / "RETRO9100-t.md").write_text(
            PLANNED_RETRO, encoding="utf-8")

    def plan(self) -> int:
        """The public path: `sprint plan`, exactly as an operator runs it."""
        import sprint
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sprint.main(["plan", "--crs", "Proposed", "--root", str(self.root),
                              "--order", "wsjf", "--no-fetch", "--skip-personas"])
        self.assertEqual(rc, 0, err.getvalue())
        return rc

    def measure(self) -> None:
        path = self.root / "sdlc-studio" / ".local" / "telemetry.jsonl"
        path.write_text(
            json.dumps({"id": "CR0101", "type": "cr", "tokens": 90_000, "wall_time_s": 300})
            + "\n"
            + json.dumps({"id": "CR0102", "type": "cr", "tokens": 60_000, "wall_time_s": 200})
            + "\n", encoding="utf-8")

    def accuracy(self) -> dict:
        return retro.accuracy(str(self.root), "RETRO9100")

    def test_changing_the_constants_does_not_move_a_recorded_forecast(self) -> None:
        import sprint
        self.plan()          # the forecast is RECORDED here, by the plan that made it
        self.measure()
        before = self.accuracy()
        self.assertEqual(before["n_measured"], 2)
        self.assertGreater(before["batch"]["estimate"], 0)

        # Now RECALIBRATE - move the tokens-per-point rate the estimator forecasts with. Every
        # past sprint's estimate must be unmoved: it is a record of what was predicted, not a
        # function of today's rate.
        with mock.patch.object(sprint, "POINTS_RATE_SEED", 60_000):
            after = self.accuracy()

        self.assertEqual(after["batch"]["estimate"], before["batch"]["estimate"],
                         "the recorded plan-time forecast moved when the constants changed - "
                         "the report is re-deriving the estimate, so it can never falsify it")
        self.assertEqual(after["batch"]["ratio"], before["batch"]["ratio"])
        for uid in ("CR0101", "CR0102"):
            a = next(u for u in after["units"] if u["id"] == uid)
            b = next(u for u in before["units"] if u["id"] == uid)
            self.assertEqual(a["estimate"], b["estimate"])
            self.assertEqual(a["ratio"], b["ratio"])

    def test_the_recorded_forecast_is_the_one_the_plan_actually_quoted(self) -> None:
        """Not merely stable - CORRECT. The estimate the retro reports must equal the number
        the planner forecast for that unit at plan time."""
        import sprint
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            sprint.main(["plan", "--crs", "Proposed", "--root", str(self.root),
                         "--order", "wsjf", "--no-fetch", "--skip-personas",
                         "--format", "json"])
        planned = json.loads(out.getvalue())["token_forecast"]["per_unit"]
        self.measure()
        res = self.accuracy()
        for u in res["units"]:
            self.assertEqual(u["estimate"], planned[u["id"]])
        self.assertEqual(res["batch"]["estimate"], sum(planned.values()))

    def test_the_forecast_is_recorded_without_write(self) -> None:
        """`--write` persists the plan artefact. The FORECAST is not optional: a forecast that
        is only recorded when someone remembers a flag is a forecast that does not exist.

        And it is recorded where git can see it. A forecast written only to the gitignored
        `.local/` state dir does not exist for anyone but the machine that planned the sprint."""
        import telemetry as tel
        self.plan()
        recorded = tel.forecasts_path(self.root)
        self.assertTrue(recorded.exists(),
                        "sprint plan must record its forecast whenever a plan is made")
        self.assertNotIn(".local", recorded.parts)
        self.assertEqual(set(tel.forecasts(self.root)), {"CR0101", "CR0102"})
        self.assertFalse((self.root / "sdlc-studio" / ".local" / "sprint-plan.json").exists())

    def test_a_replan_after_the_fact_cannot_rewrite_what_was_predicted(self) -> None:
        """First wins. Re-planning a batch once the work is done must not let the estimator
        re-forecast it with hindsight (or with new constants)."""
        import sprint
        self.plan()
        self.measure()
        first = self.accuracy()["batch"]["estimate"]
        self.assertGreater(first, 0)
        with mock.patch.object(sprint, "POINTS_RATE_SEED", 60_000):
            self.plan()  # a second plan, with a different rate, after the work is done
        self.assertEqual(self.accuracy()["batch"]["estimate"], first,
                         "a later plan overwrote what was predicted before the work started")


class SilenceOnTheEstimateSideIsNotEvidenceEither(unittest.TestCase):
    """The mirror of SilenceIsNotAMeasurement. A unit whose plan-time forecast was never
    recorded is UNFORECAST: named, excluded from BOTH sides of the ratio, and counted in the
    coverage line. It is never quietly re-derived, and never counted as accurate."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        for d in ("retros", "bugs", "change-requests", ".local"):
            (self.root / "sdlc-studio" / d).mkdir(parents=True, exist_ok=True)
        (self.root / "sdlc-studio" / "retros" / "RETRO9000-t.md").write_text(
            BATCH_RETRO, encoding="utf-8")
        (self.root / "sdlc-studio" / "bugs" / "BG0001-a.md").write_text(
            UNIT.format(prefix="BG", num="0001"), encoding="utf-8")
        for n in ("0001", "0002"):
            (self.root / "sdlc-studio" / "change-requests" / f"CR{n}-a.md").write_text(
                UNIT.format(prefix="CR", num=n), encoding="utf-8")
        self.telemetry(
            {"id": "BG0001", "type": "bug", "tokens": 50_000, "wall_time_s": 100},
            {"id": "CR0001", "type": "cr", "tokens": 40_000, "wall_time_s": 80},
            {"id": "CR0002", "type": "cr", "tokens": 30_000, "wall_time_s": 60},
        )

    def telemetry(self, *records: dict) -> None:
        (self.root / "sdlc-studio" / ".local" / "telemetry.jsonl").write_text(
            "".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")

    def forecast(self, *records: dict) -> None:
        import telemetry as tel
        tel.record_forecasts(str(self.root), list(records))

    def accuracy(self) -> dict:
        return retro.accuracy(str(self.root), "RETRO9000")

    def unit(self, res: dict, uid: str) -> dict:
        return next(u for u in res["units"] if u["id"] == uid)

    def test_a_unit_with_no_recorded_forecast_is_reported_unforecast(self) -> None:
        self.forecast({"id": "BG0001", "tokens": 50_000, "seed": 0,
                       "constants": {"BASE_TOKEN_BUDGET": 50_000,
                                     "TOKENS_PER_COGNITIVE": 600}})
        res = self.accuracy()
        self.assertEqual(res["n_units"], 3, "an unforecast unit must not vanish from the batch")
        self.assertEqual(res["n_forecast"], 1)
        self.assertEqual(res["unforecast"], ["CR0001", "CR0002"])
        for uid in ("CR0001", "CR0002"):
            u = self.unit(res, uid)
            self.assertEqual(u["state"], "unforecast")
            self.assertIsNone(u["estimate"], "an unforecast unit must not be handed an estimate")
            self.assertIsNone(u["ratio"])
            self.assertTrue(u["reason"])

    def test_an_unforecast_unit_is_excluded_from_both_sides_of_the_ratio(self) -> None:
        self.forecast({"id": "BG0001", "tokens": 50_000, "seed": 0,
                       "constants": {"BASE_TOKEN_BUDGET": 50_000,
                                     "TOKENS_PER_COGNITIVE": 600}})
        b = self.accuracy()["batch"]
        self.assertEqual(b["estimate"], 50_000)
        self.assertEqual(b["actual_tokens"], 50_000,
                         "a measured-but-unforecast unit's ACTUAL must stay out too - it has "
                         "no prediction to judge")
        self.assertEqual(b["ratio"], 1.0)

    def test_a_wholly_unforecast_batch_reports_no_ratio(self) -> None:
        res = self.accuracy()
        self.assertEqual(res["n_forecast"], 0)
        self.assertIsNone(res["batch"]["ratio"],
                          "zero recorded forecasts must not report an accuracy")

    def test_the_written_block_says_unforecast_out_loud(self) -> None:
        block = retro.accuracy_block(self.accuracy())
        self.assertIn("UNFORECAST", block)
        self.assertIn("0 of 3", block)


class TrainingErrorIsNotEvidence(unittest.TestCase):
    """A sprint whose actuals the constants in force were FITTED to cannot validate them. Its
    ratio lands near 1.0x by construction. It must be labelled IN-SAMPLE and kept out of every
    accuracy figure quoted to the operator as evidence."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        (self.root / "sdlc-studio" / "retros").mkdir(parents=True)

    def velocity(self, *rows: str) -> None:
        import sprint
        # Rendered through the PUBLIC cell writer, not a hand-built string: the estimator's
        # shape has changed twice, and a test that spells its keys out re-breaks every time.
        c = sprint.forecast_constants(self.root)
        head = ("| Retro | Date | Units | Measured | Forecast | Estimate (tokens, plan-time) | "
                "Actual (tokens) | Ratio (est/actual) | Wall (s) | Constants | Sample |\n"
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")
        body = "".join(r.format(cur=retro.constants_cell(c)) for r in rows)
        (self.root / "sdlc-studio" / "retros" / "VELOCITY.md").write_text(
            head + body, encoding="utf-8")

    def test_an_in_sample_row_is_excluded_from_the_reported_accuracy(self) -> None:
        import sprint
        fitted = sprint.CALIBRATION_FIT_RETROS[0]
        self.velocity(
            "| " + fitted + " | 2026-07-14 | 6 | 6 | 6 | 418,800 | 384,278 | 1.09x | 1,848 | "
            "{cur} | in-sample |\n")
        cal = sprint.calibration(self.root)
        self.assertEqual(cal["sprints"], 0, "a training-error row is not an out-of-sample sprint")
        self.assertEqual(cal["ratios"], [])
        self.assertEqual(cal["in_sample"], 1)
        self.assertEqual((cal["low"], cal["high"]),
                         (round(1 - sprint.FORECAST_BAND, 2), round(1 + sprint.FORECAST_BAND, 2)),
                         "an in-sample ratio must not even widen the band")

    def test_the_planner_quotes_the_out_of_sample_figure_not_the_training_fit(self) -> None:
        import sprint
        fitted = sprint.CALIBRATION_FIT_RETROS[0]
        self.velocity(
            "| " + fitted + " | 2026-07-14 | 6 | 6 | 6 | 1,285,000 | 384,278 | 3.34x | 1,848 | "
            "base=50000 tpc=5000 | in-sample |\n",
            "| RETRO9001 | 2026-07-15 | 5 | 5 | 5 | 352,600 | 642,358 | 0.55x | 3,157 | "
            "{cur} | out-of-sample |\n")
        cal = sprint.calibration(self.root)
        self.assertEqual(cal["ratios"], [0.55],
                         "only the sprint forecast BEFORE the fit, by the constants in force, "
                         "is evidence about the estimator")
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            sprint.main(["plan", "--crs", "Proposed", "--root", str(self.root),
                         "--no-fetch", "--skip-personas"])
        line = next(ln for ln in out.getvalue().splitlines() if "Calibration:" in ln)
        self.assertIn("0.55x", line)
        self.assertNotIn("1.09x", line)
        self.assertIn("out-of-sample", line)

    def test_with_no_out_of_sample_row_the_planner_says_so_rather_than_quoting_the_fit(self) -> None:
        import sprint
        fitted = sprint.CALIBRATION_FIT_RETROS[0]
        self.velocity(
            "| " + fitted + " | 2026-07-14 | 6 | 6 | 6 | 418,800 | 384,278 | 1.09x | 1,848 | "
            "{cur} | in-sample |\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            sprint.main(["plan", "--crs", "Proposed", "--root", str(self.root),
                         "--no-fetch", "--skip-personas"])
        line = next(ln for ln in out.getvalue().splitlines() if "Calibration:" in ln)
        self.assertIn("no out-of-sample evidence", line)
        self.assertNotIn("1.09x", line)

    def test_a_legacy_row_with_no_recorded_constants_is_not_evidence(self) -> None:
        """The old VELOCITY.md carried a re-derived estimate and no record of what produced it.
        It cannot be read as a forecast, so it cannot be read as evidence."""
        import sprint
        (self.root / "sdlc-studio" / "retros" / "VELOCITY.md").write_text(
            "| Retro | Date | Units | Measured | Estimate | Actual | Ratio | Wall |\n"
            "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            "| RETRO9002 | 2026-07-14 | 6 | 6 | 418,800 | 384,278 | 1.09x | 1,848 |\n",
            encoding="utf-8")
        cal = sprint.calibration(self.root)
        self.assertEqual(cal["sprints"], 0)
        self.assertEqual(cal["unforecast"], 1)


class CollateRateAcrossProjects(unittest.TestCase):
    """CR0270: the multi-project tuning read. Evidence is pooled from several project dirs and the
    tokens-per-point rate is computed WITHIN each (project, model) cell, never summed across two.
    The cell is read off the RECORD's own project - the whole reason it is stamped on the row."""

    def _seed(self, root, actuals, forecasts):
        import telemetry as tel
        ap = tel.actuals_path(str(root), "0000-migrated")
        ap.parent.mkdir(parents=True, exist_ok=True)
        ap.write_text("".join(json.dumps(r) + "\n" for r in actuals), encoding="utf-8")
        fp = tel.forecasts_path(str(root), "0000-migrated")
        fp.write_text("".join(json.dumps(r) + "\n" for r in forecasts), encoding="utf-8")

    def test_one_project_one_model_is_one_cell_with_the_right_rate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._seed(
                Path(d),
                [{"id": "US0001", "type": "story", "tokens": 50_000, "model": "m1",
                  "project": "alpha"},
                 {"id": "US0002", "type": "story", "tokens": 100_000, "model": "m1",
                  "project": "alpha"}],
                [{"id": "US0001", "tokens": 40_000, "points": 2, "project": "alpha",
                  "constants": {}},
                 {"id": "US0002", "tokens": 80_000, "points": 3, "project": "alpha",
                  "constants": {}}])
            rep = retro.collate_rate([d])
            self.assertEqual(len(rep["cells"]), 1)
            c = rep["cells"][0]
            self.assertEqual((c["project"], c["model"]), ("alpha", "m1"))
            self.assertEqual(c["points"], 5)
            self.assertEqual(c["actual_tokens"], 150_000)
            self.assertEqual(c["tokens_per_point"], 30_000)
            self.assertIsNone(rep["refused"])

    def test_a_rate_across_two_projects_is_segmented_and_refused_never_averaged(self) -> None:
        """THE LOAD-BEARING TEST. Two projects, same model, wildly different cost per point. A
        pooled average (72,500/pt) describes neither - so no cell ever holds it, each project's
        rate stands alone, and the pooled figure is refused."""
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            self._seed(
                Path(d1),
                [{"id": "US0001", "type": "story", "tokens": 50_000, "model": "m1",
                  "project": "alpha"}],
                [{"id": "US0001", "tokens": 40_000, "points": 2, "project": "alpha",
                  "constants": {}}])
            self._seed(
                Path(d2),
                [{"id": "US0001", "type": "story", "tokens": 300_000, "model": "m1",
                  "project": "beta"}],
                [{"id": "US0001", "tokens": 250_000, "points": 2, "project": "beta",
                  "constants": {}}])
            rep = retro.collate_rate([d1, d2])
            self.assertEqual(rep["projects"], ["alpha", "beta"])
            self.assertEqual(len(rep["cells"]), 2)
            self.assertTrue(rep["refused"], "a rate spanning two projects must be refused")
            rates = {c["project"]: c["tokens_per_point"] for c in rep["cells"]}
            self.assertEqual(rates["alpha"], 25_000)
            self.assertEqual(rates["beta"], 150_000)
            self.assertNotIn(72_500, [c["tokens_per_point"] for c in rep["cells"]],
                             "the naive pooled average must appear nowhere")

    def test_two_models_in_one_project_are_two_cells_and_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._seed(
                Path(d),
                [{"id": "US0001", "type": "story", "tokens": 40_000, "model": "small",
                  "project": "alpha"},
                 {"id": "US0002", "type": "story", "tokens": 200_000, "model": "large",
                  "project": "alpha"}],
                [{"id": "US0001", "tokens": 40_000, "points": 2, "project": "alpha",
                  "constants": {}},
                 {"id": "US0002", "tokens": 200_000, "points": 2, "project": "alpha",
                  "constants": {}}])
            rep = retro.collate_rate([d])
            self.assertEqual(len(rep["cells"]), 2)
            self.assertEqual(rep["models"], ["large", "small"])
            self.assertTrue(rep["refused"])

    def test_a_record_with_no_project_reads_as_its_own_unknown_cell(self) -> None:
        """Additive tolerance: an old record predating the project field is not invalidated, and
        it is never folded into a named project - it is its own `unknown` cell."""
        import telemetry as tel
        with tempfile.TemporaryDirectory() as d:
            self._seed(
                Path(d),
                [{"id": "US0001", "type": "story", "tokens": 50_000, "model": "m1"}],  # no project
                [{"id": "US0001", "tokens": 40_000, "points": 2, "constants": {}}])
            rep = retro.collate_rate([d])
            self.assertEqual(rep["cells"][0]["project"], tel.PROJECT_UNKNOWN)
            self.assertEqual(rep["cells"][0]["tokens_per_point"], 25_000)


if __name__ == "__main__":
    unittest.main()
