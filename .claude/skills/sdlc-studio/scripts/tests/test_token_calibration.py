"""The token forecast, pinned to the evidence that killed its predecessor.

The forecast was `BASE + max_cognitive x TOKENS_PER_COGNITIVE`. Nobody had ever checked whether
max_cognitive predicts anything. It does not: across the 18 units below - every unit that had a
recorded actual - it correlates with measured token cost at r = +0.03. Not weak. Nothing. Both
recalibrations of the coefficient (5,000, then 600) were fitting a slope through noise, which is
why the model over-forecast by 3.3x and then under-forecast by 0.55x and 0.39x on consecutive
sprints. You cannot scale zero.

Every other plan-time signal was then measured against the same units, and a bar was set BEFORE
the numbers were computed: a per-unit seed had to reach leave-one-out r >= 0.50 and beat
files_affected alone. The best composite reached LOO r = +0.415 - with its coefficients refitted
inside every fold AND its feature subset chosen with hindsight, both of which flatter it. It
missed. So the per-unit forecast was DROPPED (CR0262 AC3) rather than re-seeded, and the model is
now unit-count x a measured rate, with the batch history carrying the planning weight.

These tests pin THAT, and they pin the correlations it rests on, so a future change to the model
has to confront the data rather than re-guess. The numbers below are measurements, not targets:
if a later reading moves them, the model is what should move.
"""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sprint  # noqa: E402

# (unit, max_cognitive, files_affected, test_impact, effort 1/3/8, measured actual tokens)
#
# Every unit with a recorded actual at the time the rate was set - three sprints, one model, one
# repo, all delivered by instrumented subagents and recorded in sdlc-studio/retros/evidence/.
# `effort` imputes the neutral M (3) where none was declared: scoring an absent estimate as 0
# manufactures correlation out of a calendar, because the early, cheap units predate the field.
MEASURED = [
    # id        cog  files  tests  eff   actual
    ("BG0126",   43,     1,     5,   3,  46_792),
    ("BG0127",   65,     3,    14,   3,  65_625),
    ("BG0130",   30,     1,     2,   3,  42_687),
    ("CR0248",   65,     2,    10,   3,  84_302),
    ("CR0249",   43,     3,    11,   1,  98_513),
    ("CR0250",    0,     2,     9,   1,  46_359),
    ("CR0257",   24,     3,    14,   3,  97_863),
    ("CR0258",   45,     3,     6,   8, 107_623),
    ("BG0132",   61,     3,     9,   3, 129_957),
    ("CR0259",   24,     2,     9,   3, 144_711),
    ("CR0260",   24,     3,    12,   8, 162_204),
    ("BG0133",   30,     2,     7,   3, 217_139),
    ("BG0134",    0,     1,     2,   1,  71_935),
    ("BG0135",   65,     2,    10,   3, 173_804),
    ("BG0136",   43,     3,    11,   3, 234_091),
    ("CR0252",    0,     3,    16,   8, 205_534),  # docs-only: seeded 0, forecast 80k, cost 205k
    ("BG0137",   25,     2,     4,   3,  80_982),
    ("BG0140",   45,     2,     6,   1, 150_139),
]

#: The bar, set before the candidates were measured. A per-unit seed had to clear BOTH.
LOO_BAR = 0.50
#: What the best per-unit composite actually reached, leave-one-out. It missed the bar.
BEST_COMPOSITE_LOO_R = 0.415


def pearson(xs, ys) -> float:
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return sxy / math.sqrt(sxx * syy)


def _col(i: int) -> list:
    return [row[i] for row in MEASURED]


ACTUALS = _col(5)


class TheSeedThatWasInUseCarriesNoSignal(unittest.TestCase):
    """The finding the whole change rests on. If this ever stops being true, the axis is worth
    revisiting - but it must be RE-MEASURED, not assumed."""

    def test_max_cognitive_does_not_predict_cost(self) -> None:
        r = pearson(_col(1), ACTUALS)
        self.assertLess(abs(r), 0.15,
                        f"max_cognitive correlates with actual cost at r = {r:+.3f}. It was "
                        f"~0.00 when the seed was removed; a real signal here means the axis "
                        f"deserves another look")

    def test_it_is_beaten_by_the_crudest_alternative(self) -> None:
        """Counting the files a unit names beats the entire complexity apparatus."""
        self.assertGreater(pearson(_col(2), ACTUALS), abs(pearson(_col(1), ACTUALS)))

    def test_no_plan_time_signal_clears_the_bar_so_none_of_them_price_a_unit(self) -> None:
        """Why there is no per-unit forecast. The best SINGLE signal is moderate, and the best
        COMPOSITE (fitted per fold, subset chosen with hindsight) reached only 0.415."""
        singles = {"files_affected": pearson(_col(2), ACTUALS),
                   "test_impact": pearson(_col(3), ACTUALS),
                   "effort": pearson(_col(4), ACTUALS)}
        for name, r in singles.items():
            self.assertLess(r, LOO_BAR, f"{name} reached r = {r:+.3f}, which clears the "
                                        f"{LOO_BAR} bar - a per-unit forecast may now be "
                                        f"defensible. Re-run the leave-one-out validation")
        self.assertLess(BEST_COMPOSITE_LOO_R, LOO_BAR)


class TheForecastIsARateNotAnEstimate(unittest.TestCase):
    """ATTACK the model, do not read it. A forecast that still moves with a falsified seed has
    not changed axis, whatever its comments say."""

    def test_complexity_multiplies_by_nothing(self) -> None:
        self.assertEqual(sprint.TOKENS_PER_COGNITIVE, 0)
        self.assertEqual(sprint._token_budget(0, None), sprint.BASE_TOKEN_BUDGET)
        self.assertEqual(sprint._token_budget(500, None), sprint.BASE_TOKEN_BUDGET)

    def test_effort_multiplies_by_nothing_either(self) -> None:
        for effort in ("S", "M", "L", None):
            self.assertEqual(sprint._token_budget(0, effort), sprint.BASE_TOKEN_BUDGET)

    def test_the_rate_is_the_measured_mean_of_the_units_it_was_fitted_to(self) -> None:
        """The one number in the model is a MEASUREMENT, and this is where it came from."""
        mean = sum(ACTUALS) / len(ACTUALS)
        self.assertLess(abs(sprint.BASE_TOKEN_BUDGET - mean) / mean, 0.10,
                        f"the rate ({sprint.BASE_TOKEN_BUDGET:,}) has drifted from the measured "
                        f"mean ({mean:,.0f}) of the units it declares it was fitted to")

    def test_the_training_set_is_declared_so_it_can_never_be_quoted_as_validation(self) -> None:
        """A model's fit against its own training data lands near 1.0x by construction. The
        units the rate was read from are NAMED, so every one of them is excluded from the
        accuracy the planner reports."""
        declared = set(sprint.CALIBRATION_FIT_UNITS)
        self.assertEqual({row[0] for row in MEASURED}, declared,
                         "the units this rate was fitted to must be exactly the units declared "
                         "in CALIBRATION_FIT_UNITS - otherwise a sprint that trained the model "
                         "goes on being quoted back as evidence that it works")


class TheOldModelWouldHaveFailedThisSuite(unittest.TestCase):
    """The regression this replaces, stated as a test: the previous constants priced the two
    units furthest apart in complexity almost 3x apart, and they cost within 10% of each other.
    """

    def test_the_old_seed_would_have_split_two_units_that_cost_the_same(self) -> None:
        old_base, old_slope = 50_000, 600
        # BG0130 (cognitive 30) cost 42,687; CR0250 (cognitive 0, docs) cost 46,359 - within 9%
        old = {u: old_base + old_slope * cog for u, cog, *_ in MEASURED}
        self.assertGreater(old["BG0130"] / old["CR0250"], 1.3)   # the old model split them 1.36x
        actual = {u: a for u, *_rest, a in MEASURED}
        self.assertLess(actual["BG0130"] / actual["CR0250"], 1.1)  # reality did not
        # the model in force prices them identically, which is all anyone can honestly claim
        self.assertEqual(sprint._token_budget(30, None), sprint._token_budget(0, None))


if __name__ == "__main__":
    unittest.main()
