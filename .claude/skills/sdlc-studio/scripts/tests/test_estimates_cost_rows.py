"""US1151: the report's Estimates table shows forecast, actual and actual over forecast for the
Priced cost, Priced per point, Dollar cost, Dollars per point and Wall-clock span rows, from the
plan snapshot's priced, dollar and wall-clock forecasts, and a row with no rate reads
`not forecast: <reason>`. A page filed before the rule re-derives with its old rows.

Driven on US1091's fixture harness store (`test_meter_reads_true`) and US1123's typed price table
(`test_report_usd`), through `build_report`, `file_report`, `revalidate` and `render_markdown`.
The snapshot is written by `run_state.forecast_row`, the plan's own writer, at rates typed here.
"""
from __future__ import annotations

# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py

import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_meter_reads_true as meter  # noqa: E402 - US1091's harness store and workspace
import test_report_usd as usd_case  # noqa: E402 - US1123's typed price table and fixture run

#: The plan's rates. Each forecast differs from every other row's, so a ratio taken against the
#: wrong row cannot pass: tokens 2,000 a unit, minutes 20, priced 2,000,000, span 40.
PRICE_DATE = "2026-01-15"
RATES = {"tokens_per_point": {"value": 1_000, "source": "typed"},
         "minutes_per_point": {"value": 10.0, "source": "typed"},
         "priced_per_point": {"value": 1_000_000, "source": "measured: median of typed runs",
                              "retros": ["RETRO0091", "RETRO0092", "RETRO0093"]},
         "usd_per_million": {"value": 4.0, "model": meter.MODEL, "effective": PRICE_DATE,
                             "price_effective": PRICE_DATE, "source": "typed"},
         "points_per_elapsed_hour": {"value": 3.0, "source": "measured: typed reports",
                                     "reports": ["RPT0091", "RPT0092", "RPT0093"]}}
#: Two units of two points each: the run's forecasts.
PRICED_F, USD_F, SPAN_F, MINUTES_F = 4_000_000, 16.0, 80.0, 40.0


def _ratio(actual: float, forecast: float) -> str:
    return f"{round(actual / forecast, 2)}x"


class _Rows(meter._Case):
    """US1123's fixture run with the plan snapshot the plan writes, started three hours back so
    the wall-clock span is not zero."""
    table = usd_case.ReportUsdTests.table
    _run = usd_case.ReportUsdTests._run
    _whole = usd_case.ReportUsdTests._whole

    def setUp(self) -> None:
        super().setUp()
        self.sr = meter._live("sprint_report")
        self.prices = meter._live("lib.prices")
        self.table(dt.date.today())

    def planned(self, rates: dict | None = RATES):
        ws = self._run()
        start = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=3))
        snap = {"units": {uid: self.rs.forecast_row(2, rates or {}) for uid in meter.UNITS},
                "rates": rates or {}}
        self.rs.update(ws.root, plan_snapshot=snap,
                       started_at=start.strftime("%Y-%m-%dT%H:%M:%SZ"))
        return ws

    @staticmethod
    def cells(ws, page: dict, measure: str) -> tuple:
        row = ws.row(page, measure)
        return (row["est_forecast"]["value"], row["est_actual"]["value"],
                row["est_ratio"]["value"], row["est_basis"]["value"])


class PricedRowsTests(_Rows):

    def test_priced_rows_show_forecast_actual_ratio(self) -> None:
        """AC1. MUTANTS: `est_forecast` still the literal 'not forecast'; the ratio taken from the
        Tokens row; the ratio inverted (forecast over actual)."""
        ws = self.planned()
        page = self.sr.build_report(ws.root, meter.RETRO)
        forecast, actual, ratio, _ = self.cells(ws, page, "Priced cost")
        self.assertEqual(PRICED_F, forecast)
        self.assertIsInstance(actual, int)
        self.assertEqual(_ratio(actual, PRICED_F), ratio)
        self.assertNotEqual(_ratio(PRICED_F, actual), ratio)
        forecast, per, ratio, _ = self.cells(ws, page, "Priced per point")
        self.assertEqual(1_000_000, forecast)
        self.assertEqual(round(actual / 4), per)
        self.assertEqual(_ratio(per, 1_000_000), ratio)
        tokens = self.cells(ws, page, "Tokens")
        self.assertEqual(4_000, tokens[0], "control: the Tokens row keeps its own forecast")


class DollarRowsTests(_Rows):

    def test_dollar_rows_show_ratio_and_price_date(self) -> None:
        """AC2. MUTANTS: the Dollar rows keeping 'no ratio'; the ratio taken against the Priced
        row rather than the dollar forecast; the forecast's price date dropped from the basis."""
        ws = self.planned()
        page = self.sr.build_report(ws.root, meter.RETRO)
        whole = self._whole()
        forecast, actual, ratio, basis = self.cells(ws, page, "Dollar cost")
        self.assertEqual("$16.00", forecast)
        self.assertEqual(_ratio(whole, USD_F), ratio)
        self.assertIn(PRICE_DATE, basis)
        self.assertIn(meter.MODEL, basis)
        forecast, actual, ratio, basis = self.cells(ws, page, "Dollars per point")
        self.assertEqual("$4.00", forecast)
        self.assertEqual(_ratio(whole / 4, 4.0), ratio)
        self.assertIn(PRICE_DATE, basis)


class SpanRowTests(_Rows):

    def test_span_row_has_ratio_and_minutes_row_unchanged(self) -> None:
        """AC3. MUTANTS: the span's ratio taken against active minutes; the Minutes row's
        forecast replaced by the span forecast; the span left with 'no ratio'."""
        ws = self.planned()
        page = self.sr.build_report(ws.root, meter.RETRO)
        forecast, span, ratio, basis = self.cells(ws, page, "Wall-clock span")
        self.assertEqual(SPAN_F, forecast)
        self.assertGreater(span, 170, "premise: the run started three hours back")
        self.assertEqual(_ratio(span, SPAN_F), ratio)
        self.assertNotEqual(_ratio(span, MINUTES_F), ratio)
        self.assertIn("points per elapsed hour", basis)
        minutes = self.cells(ws, page, "Minutes")
        self.assertEqual(MINUTES_F, minutes[0])
        self.assertNotIn(str(round(span, 1)), str(minutes[1]))


class UnforecastRowTests(_Rows):

    def test_reason_text_descriptive_note_and_old_page_replay(self) -> None:
        """AC4, and LC-017's round-trip for the new mark. MUTANTS: a bare 'not forecast'; the
        descriptive note absent from the page; the mark left off the envelope or hard-wired on
        in `revalidate`, so a page filed before it moves on re-derivation."""
        sr = self.sr
        measures = ("Wall-clock span", "Priced cost", "Priced per point", "Dollar cost",
                    "Dollars per point")
        ws = self.planned(rates={"priced_per_point": {
            "value": None, "source": "not measured: 2 priced run(s) on record, 3 needed"}})
        page = sr.build_report(ws.root, meter.RETRO)
        for measure in measures:
            forecast, _a, ratio, _b = self.cells(ws, page, measure)
            self.assertRegex(forecast, r"^not forecast: \S", measure)
        self.assertIn("2 priced run(s)", self.cells(ws, page, "Priced cost")[0])
        self.assertIn(sr.FORECAST_NOTE, sr.render_markdown(page))
        self.assertEqual(sr.COST_FORECAST_STATED, page[sr.COST_FORECAST_RULE])

        before = sr.build_report(ws.root, meter.RETRO, cost_forecast_rule=False)
        self.assertNotIn(sr.COST_FORECAST_RULE, before)
        for measure in measures:
            forecast, _a, ratio, basis = self.cells(ws, before, measure)
            self.assertEqual(("not forecast", "no ratio"), (forecast, ratio), measure)
            self.assertNotIn(sr.FORECAST_NOTE, basis)
        check = sr.revalidate(ws.root, sr.file_report(ws.root, before))
        self.assertTrue(check["valid"], check["changes"])
        check = sr.revalidate(ws.root, sr.file_report(ws.root, page))
        self.assertTrue(check["valid"], check["changes"])
        dropped = {k: v for k, v in page.items() if k not in (sr.COST_FORECAST_RULE, "fingerprint")}
        check = sr.revalidate(ws.root, sr.file_report(ws.root, dropped))
        self.assertFalse(check["valid"], "the rule moves no figure on this fixture")


if __name__ == "__main__":
    unittest.main()
