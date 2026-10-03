"""BG0898: the Minutes ratio compares measured active minutes with the active-minute forecast.

The forecast is active work minutes per point; the Minutes row's actual was the run's wall-clock
span, start to end, so waiting counted on one side only and RPT0014 read 1.38x over unlike
measures. The ratio now compares the units' measured minutes (their spans or agent minutes)
with their forecast, and the wall-clock span stands on its own line with no ratio. A page filed
before the rule carries no mark and re-derives as it was signed.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_report as lean  # noqa: E402 - the report fixture, shared

sr = lean.sr


class MinutesLikeForLikeTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        lean.lean_run(self.root)                       # 08:00 to 18:00: a 600-minute span
        path = self.root / "sdlc-studio" / ".local" / "run-state.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        units = state["plan_snapshot"]["units"]
        for uid, minutes in (("US0001", 40.0), ("US0002", 30.0), ("US0004", 30.0),
                             ("US0005", None)):
            units[uid]["forecast_minutes"] = minutes   # 100 forecast over the live units
        for uid, minutes in (("US0001", 70.0), ("US0002", 30.0), ("US0004", 20.0)):
            state["unit_actuals"][uid]["minutes"] = minutes   # 120 measured
        path.write_text(json.dumps(state), encoding="utf-8")

    def _rows(self, **kw) -> dict:
        rep = sr.build_report(self.root, lean.RETRO, **kw)
        return {r["est_measure"]["value"]: r for r in lean._sections(rep)["estimates"]["rows"]}

    def test_the_minutes_ratio_compares_measured_with_forecast(self) -> None:
        """AC1. MUTANT: HEAD, whose Minutes actual is the wall-clock span, so the row reads
        600 against 100, 6.0x. The controls: the span still appears, on its own line with no
        ratio; and a page filed before the rule re-derives the 6.0x it was signed with."""
        rows = self._rows()
        mins = rows["Minutes"]
        self.assertEqual((100.0, 120.0),
                         (mins["est_forecast"]["value"], mins["est_actual"]["value"]))
        self.assertEqual("1.2x", mins["est_ratio"]["value"])
        self.assertIn("measured", mins["est_basis"]["value"])
        span = rows["Wall-clock span"]
        self.assertEqual(600.0, span["est_actual"]["value"])
        self.assertNotRegex(str(span["est_ratio"]["value"]), r"\d+(\.\d+)?x")
        md = lean._md_section(sr.render_markdown(sr.build_report(self.root, lean.RETRO)),
                              "Estimates")
        self.assertRegex(md, r"\| Minutes \| 100\.0 \| 120\.0 \| 1\.2x \|")
        self.assertRegex(md, r"\| Wall-clock span \| [^|]+ \| 600\.0 \| no ratio \|")
        before = self._rows(minutes_rule=False)
        self.assertEqual("6.0x", before["Minutes"]["est_ratio"]["value"])
        self.assertNotIn("Wall-clock span", before)

    def test_the_estimates_prose_follows_the_page_s_own_minutes_rule(self) -> None:
        """BG0898 round 1. MUTANT: one wording for every page - the span sentence (the page under
        the rule says no per-unit figure is summed, above a Minutes actual that sums them) or the
        measured sentence (a signed page filed before the rule re-renders a sentence it was
        never signed with). Both renders, Markdown twin and HTML page, read their own."""
        span_says = ("minutes and tokens over the whole run, its span and its meter",
                     "so no per-unit figure is added up into the run's figures above")
        measured_says = ("minutes over the units' own measured minutes",
                         "The actual on the Minutes row above sums these minutes")
        for rule, own, other in ((True, measured_says, span_says),
                                 (False, span_says, measured_says)):
            rep = sr.build_report(self.root, lean.RETRO, minutes_rule=rule)
            self.assertTrue(lean._sections(rep)["estimates"].get("unit_rows"), "fixture: no unit rows")
            for page in (lean._md_section(sr.render_markdown(rep), "Estimates"),
                         sr.render_html(rep)):
                flat = " ".join(page.split())
                with self.subTest(rule=rule):
                    for sentence in own:
                        self.assertIn(sentence, flat)
                    for sentence in other:
                        self.assertNotIn(sentence, flat)


if __name__ == "__main__":
    unittest.main()
