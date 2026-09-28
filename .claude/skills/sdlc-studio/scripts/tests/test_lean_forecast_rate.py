"""BG0798: the forecast rate re-fits from the newest VELOCITY rows, and an operator can pin it.

The re-fit was wired but starved: the rolling median preferred the work model's own rows however
old, so rows that record no model - every lean-loop sprint on this repository - never moved it.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
import retro  # noqa: E402
import sprint  # noqa: E402

_HEADER = ("| Retro | Date | Units | Measured | Points | Actual (tokens) | Wall (s) | Model |\n"
           "| --- | --- | --- | --- | --- | --- | --- | --- |\n")
_MODEL = "claude-opus-5"
# This repository's shape, with its own figures: an early row recording no model, the work
# model's three rows (median 353,810) and, after them, rows that record no model
# (RETRO0123-RETRO0125, median 184,233).
_OLD = (("RETRO0090", 10, 9_000_000, "-"),
        ("RETRO0094", 14, 4_953_336, _MODEL), ("RETRO0119", 2, 4_400_606, _MODEL),
        ("RETRO0120", 36, 9_807_942, _MODEL))
_NEW = (("RETRO0123", 32, 11_610_466, "-"), ("RETRO0124", 111, 19_797_023, "-"),
        ("RETRO0125", 102, 18_791_718, "-"))


def _history(root: Path, rows) -> None:
    p = retro.velocity_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(_HEADER + "".join(
        f"| {rid} | 2026-09-01 | 3 | 0 | {pts} | {tokens:,} | - | {model} |\n"
        for rid, pts, tokens, model in rows), encoding="utf-8")


def _story(root: Path, points: int) -> list[dict]:
    f = root / "sdlc-studio" / "stories" / "US0001-x.md"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(f"# US0001: x\n\n> **Status:** Draft\n> **Points:** {points}\n"
                 "> **Affects:** scripts/x.py\n", encoding="utf-8")
    return [{"id": "US0001", "path": str(f), "points": points}]


class ForecastRateTests(unittest.TestCase):
    def test_a_stale_model_s_rows_do_not_outrank_newer_rows(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _history(root, _OLD + _NEW)
            self.assertEqual(retro.work_model(root), _MODEL)   # the old rows name the work model
            rate = retro.measured_rate(root)
            self.assertEqual(rate["tokens_per_point"], 184_233)          # not 353,810
            self.assertEqual(rate["sprints"], ["RETRO0123", "RETRO0124", "RETRO0125"])
            self.assertIn("name no single model", rate["source"])
            self.assertNotIn("RETRO0123", rate["skipped"])     # used rows are not called skipped
            # the plan reads the same rate, and its basis carries the same words
            tpp = sprint.tokens_per_point(root)
            self.assertEqual((tpp["rate"], tpp["source"]), (184_233, sprint.RATE_VELOCITY))
            self.assertIn("name no single model", tpp["basis"])
            self.assertEqual(sprint.plan_rates(root)["tokens_per_point"]["value"], 184_233)
            # boundary: fewer than RATE_MIN_ROWS newer rows do not displace the model's own
            _history(root, _OLD + _NEW[:retro.RATE_MIN_ROWS - 1])
            rate = retro.measured_rate(root)
            self.assertEqual(rate["tokens_per_point"], 353_810)
            self.assertTrue(rate["source"].startswith(f"measured on {_MODEL}"), rate["source"])
            # rows naming several models are never newer evidence: the model's rows stand
            _history(root, _OLD + tuple((rid, pts, tok, "mixed") for rid, pts, tok, _ in _NEW))
            self.assertEqual(retro.measured_rate(root)["tokens_per_point"], 353_810)
            # seven newer rows: the newest RATE_WINDOW (5) of them, not the oldest, not three
            seven = tuple((f"RETRO02{n:02}", 10, n * 100_000, "-") for n in range(1, 8))
            _history(root, _OLD + seven)
            rate = retro.measured_rate(root)
            self.assertEqual(rate["sprints"], [f"RETRO02{n:02}" for n in range(3, 8)])
            self.assertEqual(rate["tokens_per_point"], 50_000)

    def test_an_operator_rate_overrides_and_is_named(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _history(root, _OLD + _NEW)
            batch = _story(root, 5)
            measured = sprint._token_forecast(root, batch)
            self.assertEqual(measured["tokens"], 5 * 184_233)            # positive control
            self.assertNotIn("override", measured["rate_basis"])
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "estimate:\n  tokens_per_point: 120000\n", encoding="utf-8")
            fc = sprint._token_forecast(root, batch)
            self.assertEqual((fc["rate"], fc["tokens"]), (120_000, 600_000))
            self.assertEqual(fc["rate_source"], sprint.RATE_OVERRIDE)
            self.assertIn("operator override", fc["rate_basis"])
            self.assertIn("estimate.tokens_per_point", fc["rate_basis"])
            self.assertIn("184,233", fc["rate_basis"])       # the measured rate it replaced
            self.assertEqual(sprint.plan_rates(root)["tokens_per_point"],
                             {"value": 120_000, "source": sprint.RATE_OVERRIDE})
            # a value that is not a finite number rounding to 1 or more is not applied, the plan
            # still forecasts, and the basis names the ignored value
            for bad in ("lots", ".nan", ".inf", "-.inf", "0", "0.4", "-5", "true", "1e5"):
                with self.subTest(value=bad):
                    (root / "sdlc-studio" / ".config.yaml").write_text(
                        f"estimate:\n  tokens_per_point: {bad}\n", encoding="utf-8")
                    fc = sprint._token_forecast(root, batch)
                    self.assertEqual((fc["rate"], fc["rate_source"], fc["tokens"]),
                                     (184_233, sprint.RATE_VELOCITY, 5 * 184_233))
                    self.assertIn("estimate.tokens_per_point", fc["rate_basis"])
                    self.assertIn("ignored", fc["rate_basis"])
            # the smallest value that rounds to 1 token is applied
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "estimate:\n  tokens_per_point: 0.6\n", encoding="utf-8")
            self.assertEqual(sprint.tokens_per_point(root)["rate"], 1)


if __name__ == "__main__":
    unittest.main()
