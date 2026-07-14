"""Attribution: WHO sized a unit, WHAT model delivered it, and what an unrecorded size means.

Three defects, one schema.

1. The loop recorded a forecast and an actual but never WHO made the size call, so it could
   only ever quote a population average from a study of other people back at an operator. It
   could not tell them whether THEIR judgement was any good.

2. The model that delivered a unit was captured in telemetry and went nowhere durable: not on
   the artefact, not in the committed velocity history. The moment a second model is used, a
   mean across the two describes neither of them.

3. A size nobody recorded was scored as though it were a size. Scoring an UNDECLARED size as 0
   made the field appear predictive here (r = +0.58) because the field only EXISTED on the
   later, larger units: the PRESENCE of the field correlated with cost. Treated honestly as
   missing, the same values score +0.48.

The load-bearing tests, and the ones to read first:

  `AnUnsizedUnitIsExcludedNeverCoerced` - a unit the plan never sized is named and excluded from
  every figure, and the size sitting on the artefact today is never read back to fill the gap.

  `AFigureAcrossTwoModelsIsSegmentedOrRefused` - never silently averaged.

Everything is asserted through BEHAVIOUR - the value a function returns, the state a report
gives a unit, the number a ratio comes out at. No test here greps a source file.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import retro  # noqa: E402
import telemetry  # noqa: E402


BUG = """# BG{num}: a unit

> **Status:** Open
> **Severity:** Medium
> **Points:** {points}
> **Affects:** src/bg{num}.py
{extra}
## Summary

A unit of work.
"""

RETRO_TEXT = """# RETRO-9100: a measured sprint

> **Date:** 2026-07-14
> **Batch:** {batch}

## Delivered
- shipped
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


class Fixture(unittest.TestCase):
    """A fixture workspace, never the live one: a test that read the project's own evidence
    would pass or fail on what the project happened to do that day."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for d in ("bugs", "change-requests", "retros", "retros/evidence", ".local"):
            (self.root / "sdlc-studio" / d).mkdir(parents=True, exist_ok=True)
        self.addCleanup(self.tmp.cleanup)

    def bug(self, num: str, points: int | str = 3, extra: str = "") -> None:
        (self.root / "sdlc-studio" / "bugs" / f"BG{num}-a.md").write_text(
            BUG.format(num=num, points=points, extra=extra), encoding="utf-8")

    def retro(self, *batch: str, rid: str = "RETRO9100") -> None:
        (self.root / "sdlc-studio" / "retros" / f"{rid}-t.md").write_text(
            RETRO_TEXT.format(batch=", ".join(batch)), encoding="utf-8")

    def forecast(self, uid: str, **fields) -> None:
        rec = {"id": uid, "tokens": 120_000,
               "constants": {"TOKENS_PER_POINT": 25_000},
               "planned_at": "2026-07-14T09:00:00+00:00"}
        rec.update(fields)
        telemetry.record_forecasts(str(self.root), [rec])

    def actual(self, uid: str, tokens: int, model: str | None = None, type_: str = "bug") -> None:
        telemetry.record(str(self.root), {"id": uid, "type": type_, "tokens": tokens,
                                          "model": model})


# ---------------------------------------------------------------------------
# A unit the plan never sized is UNSIZED - named, excluded, never coerced.
# ---------------------------------------------------------------------------

class AnUnsizedUnitIsExcludedNeverCoerced(Fixture):
    """The contaminant this whole schema exists to prevent, and it is not hypothetical: scoring
    an UNDECLARED size as 0 once made the size field look predictive here (r = +0.58) purely
    because the field only EXISTED on the later, larger units. The PRESENCE of the field
    correlated with cost. Treated honestly as missing, the same values scored +0.48.

    So a unit whose PLAN recorded no Points is UNSIZED: named, counted, and excluded from every
    figure - exactly as UNMEASURED and UNFORECAST already are. It is never coerced to a number,
    and the size on the artefact today is never read back to fill the gap, because a size
    written down after the outcome was known is not an estimate.
    """

    def test_a_unit_the_plan_never_sized_is_excluded_from_every_accuracy_figure(self) -> None:
        self.bug("0001")
        self.bug("0002")
        self.forecast("BG0001", estimator="dani")               # no points recorded at plan time
        self.forecast("BG0002", points=3, estimator="dani")
        self.actual("BG0001", 200_000, model="model-a")
        self.actual("BG0002", 100_000, model="model-a")

        rep = retro.estimator_report(self.root)
        states = {u["id"]: u["state"] for u in rep["units"]}
        self.assertEqual(states["BG0001"], "unsized")
        self.assertEqual(states["BG0002"], "rated")
        self.assertEqual(rep["unsized"], ["BG0001"])

        seg = rep["by_model"]["model-a"]["estimators"]["dani"]
        self.assertEqual(seg["n"], 1, "the unsized unit must not be counted")
        self.assertEqual(seg["units"], ["BG0002"])
        # and the mean is the mean of the RATED unit alone - 200,000 never entered it
        self.assertEqual(seg["mean_actual"], 100_000)

    def test_the_size_on_the_artefact_today_is_not_read_back_to_fill_the_gap(self) -> None:
        """BG0001 carries `Points: 3` on the file right now. That is not what the plan
        predicted, and hindsight is not a forecast."""
        self.bug("0001", points=3)
        self.forecast("BG0001", estimator="dani")               # the PLAN recorded no size
        self.actual("BG0001", 200_000, model="model-a")
        rep = retro.estimator_report(self.root)
        self.assertEqual(rep["unsized"], ["BG0001"])
        self.assertIsNone(next(u for u in rep["units"] if u["id"] == "BG0001")["points"])


# ---------------------------------------------------------------------------
# CR0261: an accuracy figure across two models is SEGMENTED or REFUSED.
# ---------------------------------------------------------------------------

class AFigureAcrossTwoModelsIsSegmentedOrRefused(Fixture):
    """A sprint delivered by a smaller model must not land in the same mean as one delivered
    by a larger. The mean of the two describes neither."""

    def _two_model_batch(self) -> dict:
        self.bug("0001")
        self.bug("0002")
        self.retro("BG0001", "BG0002")
        self.forecast("BG0001")
        self.forecast("BG0002")
        self.actual("BG0001", 60_000, model="small")
        self.actual("BG0002", 240_000, model="large")
        return retro.accuracy(str(self.root), "RETRO9100")

    def test_the_pooled_batch_ratio_is_refused_when_two_models_delivered_it(self) -> None:
        res = self._two_model_batch()
        self.assertEqual(res["models"], ["large", "small"])
        self.assertTrue(res["mixed_models"])
        self.assertIsNone(res["batch"]["ratio"],
                          "one ratio across two models is not a ratio about either of them")
        self.assertIn("more than one model", res["batch"]["refused"])

    def test_it_is_segmented_instead_so_the_number_is_not_simply_lost(self) -> None:
        """Refusing to average is not refusing to report. Each model gets its own figure."""
        res = self._two_model_batch()
        by = res["by_model"]
        self.assertEqual(by["small"]["ratio"], round(120_000 / 60_000, 2))
        self.assertEqual(by["large"]["ratio"], round(120_000 / 240_000, 2))
        self.assertEqual(by["small"]["units"], ["BG0001"])
        self.assertEqual(by["large"]["units"], ["BG0002"])

    def test_one_model_still_produces_the_pooled_ratio(self) -> None:
        """The refusal must fire on the hazard, not on the ordinary case."""
        self.bug("0001")
        self.bug("0002")
        self.retro("BG0001", "BG0002")
        self.forecast("BG0001")
        self.forecast("BG0002")
        self.actual("BG0001", 60_000, model="small")
        self.actual("BG0002", 240_000, model="small")
        res = retro.accuracy(str(self.root), "RETRO9100")
        self.assertFalse(res["mixed_models"])
        self.assertIsNone(res["batch"]["refused"])
        self.assertEqual(res["batch"]["ratio"], round(240_000 / 300_000, 2))

    def test_the_written_block_says_the_ratio_was_refused_out_loud(self) -> None:
        res = self._two_model_batch()
        block = retro.accuracy_block(res)
        self.assertIn("REFUSED", block)
        self.assertIn("small", block)
        self.assertIn("large", block)

    def test_the_velocity_row_carries_the_model_and_says_mixed_when_it_was(self) -> None:
        """The committed history is where a model change would otherwise vanish."""
        res = self._two_model_batch()
        retro.record_velocity(self.root, res)
        rows = retro.velocity_history(self.root)
        self.assertEqual(rows[0]["model"], "mixed")
        self.assertIsNone(rows[0]["ratio"], "a mixed-model sprint records no pooled ratio")

    def test_the_estimator_report_refuses_a_pooled_correlation_across_models(self) -> None:
        for n, (tokens, model) in enumerate(
                ((60_000, "small"), (90_000, "small"), (200_000, "large")), 1):
            uid = f"BG000{n}"
            self.bug(f"000{n}")
            self.forecast(uid, points=3, estimator="dani")
            self.actual(uid, tokens, model=model)
        rep = retro.estimator_report(self.root)
        self.assertIsNone(rep["pooled"],
                          "a correlation computed across two models is not a correlation")
        self.assertIn("segmented", rep["refused"])
        self.assertEqual(sorted(rep["by_model"]), ["large", "small"])


# ---------------------------------------------------------------------------
# CR0263: the estimate records WHO made it, and the report is segmented per estimator.
# ---------------------------------------------------------------------------

class TheEstimateRecordsWhoMadeIt(Fixture):
    def test_an_unnamed_estimator_is_unattributed_and_never_inferred(self) -> None:
        """Nobody's accuracy is attributed to them by guesswork. With no `Estimated-by`, the
        estimate belongs to nobody - which is a fact, not a gap to be filled."""
        self.bug("0001")
        self.forecast("BG0001", points=3)
        self.actual("BG0001", 100_000, model="model-a")
        rep = retro.estimator_report(self.root)
        self.assertEqual(rep["units"][0]["estimator"], retro.ESTIMATOR_UNATTRIBUTED)

    def test_accuracy_is_segmented_per_estimator(self) -> None:
        """The whole point: 'your point calls run at r = 0.9, the auto-estimate at 0.1 - trust
        yours'. A pooled figure cannot say that, and a population average from a study of other
        people cannot say it either."""
        # dani calls it right: bigger size, bigger cost.
        for n, (pts, tokens) in enumerate(((2, 50_000), (5, 120_000), (8, 300_000)), 1):
            uid = f"BG010{n}"
            self.bug(f"010{n}", points=pts)
            self.forecast(uid, points=pts, estimator="dani")
            self.actual(uid, tokens, model="model-a")
        # the auto-estimate calls it backwards.
        for n, (pts, tokens) in enumerate(((8, 50_000), (5, 120_000), (2, 300_000)), 1):
            uid = f"BG020{n}"
            self.bug(f"020{n}", points=pts)
            self.forecast(uid, points=pts, estimator="auto")
            self.actual(uid, tokens, model="model-a")

        rep = retro.estimator_report(self.root)
        seg = rep["by_model"]["model-a"]["estimators"]
        self.assertEqual(seg["dani"]["n"], 3)
        self.assertGreater(seg["dani"]["r"], 0.9)
        self.assertLess(seg["auto"]["r"], -0.5)
        self.assertEqual(rep["by_model"]["model-a"]["best_estimator"], "dani")

    def test_the_report_names_the_classes_an_estimator_systematically_under_calls(self) -> None:
        """Directional bias is CORRECTABLE; a bare correlation is not. An estimator whose 2s
        cost far more than their own scale implies is told so, by name."""
        # Every 2 this estimator calls blows up; their 5s and 8s are on scale.
        rows = [("0301", 2, 300_000), ("0302", 2, 280_000),
                ("0303", 5, 120_000), ("0304", 5, 110_000),
                ("0305", 8, 300_000), ("0306", 8, 320_000)]
        for num, pts, tokens in rows:
            self.bug(num, points=pts)
            self.forecast(f"BG{num}", points=pts, estimator="dani")
            self.actual(f"BG{num}", tokens, model="model-a")
        seg = retro.estimator_report(self.root)["by_model"]["model-a"]["estimators"]["dani"]
        bias = {b["class"]: b["direction"] for b in seg["bias"]}
        self.assertEqual(bias["2-point"], "under-calls")
        self.assertNotEqual(bias["8-point"], "under-calls")

    def test_a_class_of_one_claims_no_direction(self) -> None:
        """One unit is an anecdote. The report says so rather than calling a bias off n=1."""
        self.bug("0401", points=2)
        self.forecast("BG0401", points=2, estimator="dani")
        self.actual("BG0401", 300_000, model="model-a")
        seg = retro.estimator_report(self.root)["by_model"]["model-a"]["estimators"]["dani"]
        self.assertEqual({b["direction"] for b in seg["bias"]}, {"not enough units"})
        self.assertIsNone(seg["r"], "a correlation needs more than one point")


# ---------------------------------------------------------------------------
# CR0261: the model that delivered a unit reaches the ARTEFACT.
# ---------------------------------------------------------------------------

class TheDeliveredModelReachesTheArtefact(Fixture):
    def test_recording_an_actual_stamps_the_model_on_the_unit(self) -> None:
        """You can read the bug and see what built it, without the telemetry log."""
        self.bug("0001")
        telemetry.record(str(self.root), {"id": "BG0001", "type": "bug", "tokens": 1000,
                                          "model": "model-a"})
        text = (self.root / "sdlc-studio" / "bugs" / "BG0001-a.md").read_text(encoding="utf-8")
        self.assertIn("> **Delivered-by:** model-a", text)

    def test_the_stamp_is_idempotent_and_the_last_model_wins(self) -> None:
        self.bug("0001")
        for model in ("model-a", "model-a", "model-b"):
            telemetry.record(str(self.root), {"id": "BG0001", "type": "bug", "model": model})
        text = (self.root / "sdlc-studio" / "bugs" / "BG0001-a.md").read_text(encoding="utf-8")
        self.assertEqual(text.count("Delivered-by"), 1)
        self.assertIn("> **Delivered-by:** model-b", text)

    def test_a_record_with_no_model_stamps_nothing(self) -> None:
        self.bug("0001")
        telemetry.record(str(self.root), {"id": "BG0001", "type": "bug", "tokens": 1000})
        text = (self.root / "sdlc-studio" / "bugs" / "BG0001-a.md").read_text(encoding="utf-8")
        self.assertNotIn("Delivered-by", text)

    def test_an_unknown_id_never_breaks_the_recording_path(self) -> None:
        """Telemetry is advisory. A stamp that cannot land must not cost the measurement."""
        rec = telemetry.record(str(self.root), {"id": "BG9999", "type": "bug", "tokens": 1000,
                                                "model": "model-a"})
        self.assertEqual(rec["id"], "BG9999")
        self.assertEqual(telemetry.actuals(self.root)["BG9999"]["tokens"], 1000)


# ---------------------------------------------------------------------------
# CR0263 AC4: the coercion hazard, answered with evidence rather than opinion.
# ---------------------------------------------------------------------------

class TheCoercionHazardIsAnsweredNotAsserted(Fixture):
    """The grooming gate makes a size COMPULSORY at filing. If sizing is a chore, a compulsory
    estimate is a CARELESS estimate - and a careless number is worse than none, because it looks
    like data.

    This is testable, and the test must be able to come out EITHER WAY. What it may never do is
    claim a finding it cannot support: before/after is itself a cohort split, so a difference
    between the eras is confounded with everything else that changed over the same period.
    """

    VOLUNTARY = "voluntary"
    COMPULSORY = "compulsory"

    def _era(self, uid: str, num: str, era: str, points: int, tokens: int) -> None:
        self.bug(num, points=points)
        self.forecast(uid, points=points, estimator="dani", size_gate=era)
        self.actual(uid, tokens, model="model-a")

    def test_the_two_eras_are_compared_and_never_pooled(self) -> None:
        for n, (pts, tok) in enumerate(((2, 50_000), (5, 120_000), (8, 300_000),
                                        (5, 130_000), (2, 60_000)), 1):
            self._era(f"BG050{n}", f"050{n}", self.VOLUNTARY, pts, tok)
        for n, (pts, tok) in enumerate(((8, 50_000), (5, 120_000), (2, 300_000),
                                        (5, 130_000), (2, 60_000)), 1):
            self._era(f"BG060{n}", f"060{n}", self.COMPULSORY, pts, tok)
        coercion = retro.estimator_report(self.root)["coercion"]
        self.assertEqual(coercion["by_era"]["voluntary"]["n"], 5)
        self.assertEqual(coercion["by_era"]["compulsory"]["n"], 5)
        self.assertGreater(coercion["by_era"]["voluntary"]["r"],
                           coercion["by_era"]["compulsory"]["r"])
        self.assertTrue(coercion["answered"])
        self.assertIn("cohort", coercion["caveat"],
                      "the answer must carry its own confound: before/after IS a cohort split")

    def test_a_cohort_too_small_to_separate_the_effects_says_so(self) -> None:
        """The required outcome when the data cannot answer. Silence, or a confident r off
        n = 1, would both be worse than the refusal."""
        self._era("BG0701", "0701", self.VOLUNTARY, 5, 120_000)
        self._era("BG0702", "0702", self.COMPULSORY, 2, 60_000)
        coercion = retro.estimator_report(self.root)["coercion"]
        self.assertFalse(coercion["answered"])
        self.assertIn("cannot", coercion["answer"].lower())
        self.assertIsNone(coercion["by_era"]["voluntary"]["r"])

    def test_an_era_the_record_never_stamped_is_unknown_not_guessed(self) -> None:
        """The units already measured were recorded before the planner stamped the era. They
        are an UNKNOWN cohort, and they are not quietly filed on one side of the split."""
        self.bug("0801", points=5)
        self.forecast("BG0801", points=5, estimator="dani")   # no size_gate stamp
        self.actual("BG0801", 120_000, model="model-a")
        coercion = retro.estimator_report(self.root)["coercion"]
        self.assertEqual(coercion["by_era"]["unknown"]["n"], 1)
        self.assertEqual(coercion["by_era"]["voluntary"]["n"], 0)
        self.assertEqual(coercion["by_era"]["compulsory"]["n"], 0)

    def test_the_pre_rename_gate_field_is_still_understood(self) -> None:
        """The field was `effort_gate` when the size was an Effort. Evidence already on disk
        carries that name, and a rename that quietly dropped it would delete history."""
        self.bug("0802", points=5)
        self.forecast("BG0802", points=5, estimator="dani", effort_gate=self.COMPULSORY)
        self.actual("BG0802", 120_000, model="model-a")
        coercion = retro.estimator_report(self.root)["coercion"]
        self.assertEqual(coercion["by_era"]["compulsory"]["n"], 1)
        self.assertEqual(coercion["by_era"]["unknown"]["n"], 0)


# ---------------------------------------------------------------------------
# The contaminant this whole change exists to prevent, pinned as a test.
# ---------------------------------------------------------------------------

class ScoringAMissingEstimateAsZeroManufacturesCorrelation(unittest.TestCase):
    """This already happened. Scoring an UNDECLARED Effort as 0 made the field look
    predictive - but the field only existed on units filed after it was introduced, and those
    happen to be the later, larger ones. The PRESENCE of the field correlated with cost.

    The numbers below are this project's own 20 measured units. They are here so the rule
    ("unknown is excluded, never coerced") has a measurement behind it and not just a comment.
    """

    #: (effort points at filing or None, measured actual tokens)
    MEASURED = [
        (3, 84_302), (1, 98_513), (1, 46_359), (3, 97_863), (3, 107_623), (3, 144_711),
        (8, 162_204), (3, 217_139), (1, 71_935), (3, 173_804), (3, 234_091), (8, 205_534),
        (3, 80_982), (1, 77_762), (1, 150_139), (3, 223_308),
        (None, 46_792), (None, 65_625), (None, 42_687), (None, 129_957),   # no Effort at all
    ]

    @staticmethod
    def _pearson(xs, ys) -> float:
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        sxx = sum((x - mx) ** 2 for x in xs)
        syy = sum((y - my) ** 2 for y in ys)
        return sxy / (sxx * syy) ** 0.5

    def test_coercing_the_missing_value_to_zero_inflates_the_correlation(self) -> None:
        coerced = self._pearson([(p or 0) for p, _ in self.MEASURED],
                                [a for _, a in self.MEASURED])
        honest = self._pearson([p for p, _ in self.MEASURED if p is not None],
                               [a for p, a in self.MEASURED if p is not None])
        self.assertGreater(coerced, honest,
                           "if this ever stops holding, re-read the evidence - but the RULE "
                           "does not move: a value nobody supplied is not a zero")
        self.assertGreater(coerced - honest, 0.05)

    def test_the_honest_correlation_is_the_one_the_project_quotes(self) -> None:
        """0.50 is the bar declared before any of this was measured (see
        test_token_calibration). The human Effort does not clear it even when read honestly:
        it RANKS work, it does not price it - which is why the forecast no longer reads it."""
        honest = self._pearson([p for p, _ in self.MEASURED if p is not None],
                               [a for p, a in self.MEASURED if p is not None])
        self.assertLess(honest, 0.50,
                        "the human Effort still does not clear the bar set for a per-unit "
                        "forecast - it ranks, it does not price")


if __name__ == "__main__":
    unittest.main()
