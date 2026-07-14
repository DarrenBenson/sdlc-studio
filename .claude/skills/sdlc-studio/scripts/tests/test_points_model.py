"""The POINTS cost model, pinned to the evidence that established it.

This replaces the pinning tests of the estimator that died. That one forecast a flat per-unit
base plus a per-complexity slope times the blast-radius cognitive complexity, and nobody had
ever checked whether that complexity predicts anything. It does not: across 18 units with actuals
correlated with measured cost at r = +0.03. You cannot scale zero, and two recalibrations of the
coefficient were fitting a slope through noise.

What replaced it is the first predictor this project has found that works, and it was established
BLIND (RFC0038): 21 delivered units were recovered AS FILED, their declared size stripped, and
sized in modified Fibonacci by three independent estimators with no access to the outcomes.

    Points (median of 3)      r = +0.68 pooled, +0.78 on units of 8 or below
                              POSITIVE within every one of the four sprints
    declared Effort (S/M/L)   r = +0.35   a second size vocabulary, and worse. Retired
    max_cognitive             r = +0.03   dead - and it was still ordering the batch (BG0147)

The bar was set BEFORE the numbers were seen, which is the only reason a negative result was
possible (LL0036), and points cleared all four rungs of it.

These tests pin the model and the measurement it rests on. The numbers are MEASUREMENTS, not
targets: if a later reading moves them, the model is what should move.
"""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sprint  # noqa: E402
from lib import sdlc_md  # noqa: E402

# ---------------------------------------------------------------------------
# A POINT IS A STABLE UNIT OF COST - up to 8, and not beyond.
# ---------------------------------------------------------------------------
# Measured tokens per point, per band, over the 19 blind-sized units that had actuals. This is
# the whole cost model, and the whole case for the split ceiling, in five numbers.
TOKENS_PER_POINT_BY_BAND = {
    2: 22_370,
    3: 26_153,
    5: 27_396,
    8: 25_171,
    13: 14_144,   # 1.9x cheaper per point: the estimate BROKE here, exactly as predicted
}
#: The bands where a point behaved like a unit of cost. This is what the gate protects.
STABLE_BANDS = (2, 3, 5, 8)
#: The band where it did not. All three estimators returned these units with LOW confidence and
#: the words "should be split", unprompted - before anyone had looked at what they cost.
BROKEN_BAND = 13

#: Pooled correlation of the blind point estimates against measured token cost, and the same
#: correlation restricted to the units at or below the split ceiling.
POINTS_R_POOLED = 0.682
POINTS_R_AT_OR_BELOW_CEILING = 0.782
#: What the same 19 units scored against the signals points replaced.
EFFORT_R = 0.35
MAX_COGNITIVE_R = 0.03
#: The bar, declared before the data was seen.
BAR_R = 0.50


def _mean(xs) -> float:
    return sum(xs) / len(xs)


STABLE_RATE = _mean([TOKENS_PER_POINT_BY_BAND[b] for b in STABLE_BANDS])


class APointIsAStableUnitOfCost(unittest.TestCase):
    """The finding the cost model rests on. If this stops being true the model must MOVE, not
    be re-argued: the rate is a measurement, and so is its range of validity."""

    def test_the_bands_up_to_the_ceiling_agree_with_each_other(self) -> None:
        for band in STABLE_BANDS:
            rate = TOKENS_PER_POINT_BY_BAND[band]
            drift = abs(rate - STABLE_RATE) / STABLE_RATE
            self.assertLess(drift, 0.15,
                            f"the {band}-point band measured {rate:,} tokens per point against a "
                            f"pooled {STABLE_RATE:,.0f} - a point is no longer a stable unit of "
                            f"cost across the legal range, and the flat rate is not defensible")

    def test_it_breaks_above_the_ceiling_which_is_why_the_gate_refuses_there(self) -> None:
        """The 13s were systematically OVER-estimated. A forecast in that range is not an
        estimate, it is a triage failure with a number attached."""
        broken = TOKENS_PER_POINT_BY_BAND[BROKEN_BAND]
        self.assertLess(broken, STABLE_RATE / 1.5,
                        f"the {BROKEN_BAND}-point band measured {broken:,} tokens per point "
                        f"against {STABLE_RATE:,.0f} in the stable range")

    def test_the_gate_stands_exactly_where_the_evidence_stops(self) -> None:
        """The ceiling is not a round number somebody liked. It is the top of the measured
        stable region, and moving it means forecasting where the model is known to break."""
        self.assertEqual(sdlc_md.POINTS_SPLIT_ABOVE, max(STABLE_BANDS))
        self.assertGreater(BROKEN_BAND, sdlc_md.POINTS_SPLIT_ABOVE)
        # every band measured is a rung of the one scale - nothing here is off it
        for band in TOKENS_PER_POINT_BY_BAND:
            self.assertIn(band, sdlc_md.POINTS_SCALE)


class PointsClearedTheBarAndNothingElseDid(unittest.TestCase):
    """The comparison, as recorded. A future change that re-introduces a computed size signal
    has to confront these numbers rather than re-guess."""

    def test_points_clear_the_bar_that_was_set_before_the_data_was_seen(self) -> None:
        self.assertGreater(POINTS_R_POOLED, BAR_R)
        self.assertGreater(POINTS_R_AT_OR_BELOW_CEILING, POINTS_R_POOLED)  # sharper in range

    def test_they_beat_the_signals_they_replaced_by_a_clear_margin(self) -> None:
        self.assertGreater(POINTS_R_POOLED, EFFORT_R * 1.5)   # not merely a renamed S/M/L
        self.assertLess(MAX_COGNITIVE_R, 0.15)                # and the computed one was nothing
        self.assertLess(EFFORT_R, BAR_R)                      # neither predecessor ever cleared it


class TheRateIsMeasuredNotFitted(unittest.TestCase):
    """ATTACK the model, do not read it. A forecast that ignores the project's own evidence, or
    that quietly grows a base term, has not changed axis whatever its comments say."""

    def _evidence(self, root: Path, rows) -> None:
        ev = root / "sdlc-studio" / "retros" / "evidence"
        ev.mkdir(parents=True, exist_ok=True)
        (ev / "forecasts-2026-01-01.jsonl").write_text(
            "".join(json.dumps({"id": i, "points": p}) + "\n" for i, p, _ in rows),
            encoding="utf-8")
        (ev / "actuals-2026-01-01.jsonl").write_text(
            "".join(json.dumps({"id": i, "type": "cr", "tokens": t}) + "\n" for i, _, t in rows),
            encoding="utf-8")

    def test_the_seed_is_the_measured_rate_of_the_stable_bands(self) -> None:
        """The one number in a fresh project's model is a MEASUREMENT, and this is where it
        came from."""
        drift = abs(sprint.POINTS_RATE_SEED - STABLE_RATE) / STABLE_RATE
        self.assertLess(drift, 0.10,
                        f"the seed rate ({sprint.POINTS_RATE_SEED:,}) has drifted from the "
                        f"measured {STABLE_RATE:,.0f} tokens per point it declares it came from")
        self.assertIn("blind re-estimation", sprint.POINTS_RATE_SEED_BASIS)

    def test_a_project_measures_its_own_rate_from_its_own_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # 19 points delivered for 570,000 tokens: this project's point costs 30,000
            self._evidence(root, [("BG0001", 1, 30_000), ("BG0002", 2, 60_000),
                                  ("BG0003", 3, 90_000), ("BG0004", 5, 150_000),
                                  ("BG0005", 8, 240_000)])
            rate = sprint.tokens_per_point(root)
            self.assertEqual(rate["source"], "measured")
            self.assertEqual(rate["rate"], 30_000)      # NOT the seed - its own measurement wins
            self.assertEqual(rate["points"], 19)
            self.assertEqual(rate["units"], 5)

    def test_the_rate_is_total_over_total_not_the_mean_of_the_ratios(self) -> None:
        """A mean of per-unit ratios over-weights the small units, where a fixed overhead is
        proportionally largest. Tokens over points is what 'tokens per point' means."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._evidence(root, [("BG0001", 1, 50_000),   # 50,000/pt on its own
                                  ("BG0002", 8, 160_000),  # 20,000/pt
                                  ("BG0003", 8, 160_000),
                                  ("BG0004", 8, 160_000),
                                  ("BG0005", 8, 160_000)])
            rate = sprint.tokens_per_point(root)
            self.assertEqual(rate["rate"], round(690_000 / 33))     # 20,909, total over total
            self.assertNotEqual(rate["rate"], round(_mean([50_000, 20_000, 20_000,
                                                           20_000, 20_000])))

    def test_an_unmeasured_unit_never_enters_the_rate(self) -> None:
        """A unit that was forecast but never measured, and a unit measured but never forecast,
        are both SILENT. Neither may be counted as a zero at either end."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ev = root / "sdlc-studio" / "retros" / "evidence"
            ev.mkdir(parents=True, exist_ok=True)
            (ev / "forecasts-2026-01-01.jsonl").write_text(
                "".join(json.dumps(r) + "\n" for r in [
                    {"id": "BG0001", "points": 2}, {"id": "BG0002", "points": 3},
                    {"id": "BG0003", "points": 5}, {"id": "BG0004", "points": 8},
                    {"id": "BG0005", "points": 2}, {"id": "BG0006", "points": 13},
                    {"id": "BG0007", "tokens": 120_000}]),      # forecast by the OLD model
                encoding="utf-8")
            (ev / "actuals-2026-01-01.jsonl").write_text(
                "".join(json.dumps(r) + "\n" for r in [
                    {"id": "BG0001", "tokens": 40_000}, {"id": "BG0002", "tokens": 60_000},
                    {"id": "BG0003", "tokens": 100_000}, {"id": "BG0004", "tokens": 160_000},
                    {"id": "BG0005", "tokens": 40_000},
                    {"id": "BG0006", "type": "bug"},            # never measured
                    {"id": "BG0007", "tokens": 999_999},        # never sized
                    {"id": "BG0008", "tokens": 500_000}]),      # neither
                encoding="utf-8")
            rate = sprint.tokens_per_point(root)
            self.assertEqual(rate["units"], 5)                  # the five with BOTH
            self.assertEqual(rate["points"], 20)
            self.assertEqual(rate["rate"], 20_000)              # the wild rows moved it not at all
            self.assertNotIn("BG0006", rate["ids"])
            self.assertNotIn("BG0007", rate["ids"])

    def test_a_wild_single_unit_cannot_move_next_sprints_rate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._evidence(root, [("BG0001", 1, 900_000)])
            rate = sprint.tokens_per_point(root)
            self.assertEqual(rate["source"], "seed")            # below the minimum, it does not
            self.assertEqual(rate["rate"], sprint.POINTS_RATE_SEED)
            self.assertEqual(rate["units"], 1)                  # ...and it is still COUNTED

    def test_no_evidence_at_all_still_plans(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rate = sprint.tokens_per_point(Path(d))
            self.assertEqual(rate["rate"], sprint.POINTS_RATE_SEED)
            self.assertEqual(rate["source"], "seed")


class TheModelIsStrictlyLinearInPoints(unittest.TestCase):
    """NO BASE TERM. A least-squares fit adds one (8,043) and does WORSE - 11/19 units inside the
    band, 9/19 leave-one-out, against 12/19 for the flat rate with no fitting at all. The simple
    model won on the evidence, and these tests stop it being quietly re-complicated."""

    def _cr(self, root: Path, num: int, points: int) -> None:
        d = root / "sdlc-studio" / "change-requests"
        d.mkdir(parents=True, exist_ok=True)
        src = root / f"src{num}.py"
        src.write_text("def f():\n    return 1\n", encoding="utf-8")
        (d / f"CR{num:04d}-x.md").write_text(
            f"# CR-{num:04d}: c\n\n> **Status:** Proposed\n> **Priority:** Medium\n"
            f"> **Affects:** src{num}.py\n> **Points:** {points}\n", encoding="utf-8")

    def test_doubling_the_points_doubles_the_forecast_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root, 1, 1)
            self._cr(root, 2, 2)
            self._cr(root, 3, 8)
            fc = sprint.build_plan(root, "cr", "Proposed",
                                   skip_personas=True)["token_forecast"]["per_unit"]
            self.assertEqual(fc["CR0002"], 2 * fc["CR0001"])
            self.assertEqual(fc["CR0003"], 8 * fc["CR0001"])   # a base term would compress this

    def test_the_batch_total_is_the_sum_of_the_points_times_the_rate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for num, pts in ((1, 2), (2, 3), (3, 5)):
                self._cr(root, num, pts)
            fc = sprint.build_plan(root, "cr", "Proposed",
                                   skip_personas=True)["token_forecast"]
            self.assertEqual(fc["points"], 10)
            self.assertEqual(fc["tokens"], 10 * fc["rate"])


class TheOldModelWouldHaveFailedThisSuite(unittest.TestCase):
    """The regression this replaces, stated as behaviour. The old estimator priced every unit
    the same, so it could not tell a 1-point job from an 8-point one - and it missed every
    single unit it ever forecast, monotonically."""

    def _cr(self, root: Path, num: int, points: int) -> None:
        d = root / "sdlc-studio" / "change-requests"
        d.mkdir(parents=True, exist_ok=True)
        (root / f"src{num}.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        (d / f"CR{num:04d}-x.md").write_text(
            f"# CR-{num:04d}: c\n\n> **Status:** Proposed\n> **Priority:** Medium\n"
            f"> **Affects:** src{num}.py\n> **Points:** {points}\n", encoding="utf-8")

    def test_a_small_unit_and_a_big_one_no_longer_forecast_the_same_number(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root, 1, 1)
            self._cr(root, 2, 8)
            fc = sprint.build_plan(root, "cr", "Proposed",
                                   skip_personas=True)["token_forecast"]["per_unit"]
            self.assertEqual(fc["CR0002"], 8 * fc["CR0001"])

    def test_the_plan_names_the_evidence_its_rate_came_from(self) -> None:
        """A number an operator cannot trace is a number they have to take on trust, and this
        project has burned that trust twice."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root, 1, 3)
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                rc = sprint.main(["plan", "--crs", "Proposed", "--root", str(root),
                                  "--no-fetch", "--skip-personas"])
            self.assertEqual(rc, 0)
            text = out.getvalue()
            self.assertIn("tokens per point", text)
            self.assertIn("blind re-estimation", text)
            self.assertIn("seed", text)      # and it says the rate is NOT yet this project's own


if __name__ == "__main__":
    unittest.main()
