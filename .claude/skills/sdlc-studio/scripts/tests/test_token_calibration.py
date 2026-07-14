"""The token forecast's constants, pinned to the actuals they were fitted to.

The forecast was `BASE + complexity x 5,000` and nothing had ever checked it against reality.
Six units were then measured end-to-end and it over-forecast the batch by 3.3x - which was not
harmless: a 10-unit batch was cut to 5 on the belief it was too big, when it was not.

These tests pin the constants to the evidence, so changing one means confronting the data
rather than re-guessing. They are NOT a claim that the calibration is settled - it is fitted to
6 units, one model, one repo, and the next sprint is its falsification test.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sprint  # noqa: E402

# (unit, blast-radius complexity, measured actual tokens) - one sprint, six units, all
# delivered by instrumented subagents and recorded in telemetry.
MEASURED = [
    ("CR0250", 0, 46_359),   # docs only - the pure fixed cost
    ("BG0130", 15, 42_687),
    ("BG0126", 39, 46_792),
    ("CR0249", 39, 98_513),  # same complexity as BG0126, 2.1x the cost
    ("BG0127", 52, 65_625),
    ("CR0248", 52, 84_302),
]


def _forecast(cx: int) -> int:
    return sprint.BASE_TOKEN_BUDGET + cx * sprint.TOKENS_PER_COGNITIVE


class TheBatchForecastMatchesReality(unittest.TestCase):
    def test_batch_forecast_is_within_25_percent_of_the_measured_batch(self) -> None:
        """The forecast is a BATCH tool. Across the six measured units it must land close;
        the old 5,000 coefficient was 3.3x out, which caused a real planning error."""
        forecast = sum(_forecast(cx) for _, cx, _ in MEASURED)
        actual = sum(a for _, _, a in MEASURED)
        ratio = forecast / actual
        self.assertLess(ratio, 1.25, f"batch forecast {forecast:,} is {ratio:.2f}x actual {actual:,}")
        self.assertGreater(ratio, 0.75, f"batch forecast {forecast:,} is {ratio:.2f}x actual {actual:,}")

    def test_the_fixed_floor_is_the_measured_one(self) -> None:
        """A complexity-0 unit costs the base and nothing more. The docs-only unit measured
        46,359, so a ~50k floor is real - the cost of taking on the task at all."""
        docs_only = next(a for u, cx, a in MEASURED if cx == 0)
        self.assertLess(abs(_forecast(0) - docs_only) / docs_only, 0.20)


class ComplexityIsAWeakPerUnitPredictor(unittest.TestCase):
    """Recorded as a test so it cannot be quietly forgotten: this forecast must not be sold as
    per-unit accurate. Two units of IDENTICAL complexity cost 2.1x apart."""

    def test_identical_complexity_produced_very_different_actuals(self) -> None:
        same = [a for _, cx, a in MEASURED if cx == 39]
        self.assertEqual(len(same), 2)
        self.assertGreater(max(same) / min(same), 2.0,
                           "if this ever tightens, complexity became a better predictor - "
                           "revisit whether the model should use a work-based input instead")


if __name__ == "__main__":
    unittest.main()
