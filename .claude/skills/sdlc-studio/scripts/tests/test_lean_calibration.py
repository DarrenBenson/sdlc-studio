"""US0869: estimates are calibrated from the project's own runs, not a seed constant (EP0260).

The token rate is the rolling median tokens per point of the most recent usable VELOCITY rows
for the model doing the work; rows with no model or several are skipped, never fatal; a thin
history falls back to any single-model rows before the seed. Minutes per point follow the same
rule over rows that record active (worker) time.
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
from lib import run_state  # noqa: E402

REPO = SCR.parents[3]
_HEADER = ("| Retro | Date | Units | Measured | Points | Actual (tokens) | Wall (s) | Model |\n"
           "| --- | --- | --- | --- | --- | --- | --- | --- |\n")


def _row(rid: str, points: int, actual: int, model: str = "-", wall: int | None = None,
         measured: int | None = None) -> str:
    # A row carrying per-unit worker time is fully measured (3 of 3) unless `measured` says
    # otherwise; one without is a sprint-level harness total (0 of 3). Both cover their points.
    measured = (3 if wall is not None else 0) if measured is None else measured
    return (f"| {rid} | 2026-09-01 | 3 | {measured} | {points} | {actual:,} | "
            f"{'-' if wall is None else f'{wall:,}'} | {model} |\n")


def _history(root: Path, *rows: str) -> None:
    p = retro.velocity_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(_HEADER + "".join(rows), encoding="utf-8")


class TokenRateTests(unittest.TestCase):
    def test_a_mixed_model_history_yields_the_current_models_rolling_median(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _history(root,
                     _row("RETRO0001", 10, 100_000, "new"),        # 10k/pt, outside the window
                     _row("RETRO0002", 10, 200_000, "new"),
                     _row("RETRO0003", 10, 9_990_000),             # no model: skipped
                     _row("RETRO0004", 10, 300_000, "new"),
                     _row("RETRO0005", 10, 8_880_000, "mixed"),    # several models: skipped
                     _row("RETRO0006", 10, 400_000, "new"),
                     _row("RETRO0007", 10, 7_770_000, "old"),      # another model
                     _row("RETRO0008", 10, 500_000, "new"),
                     _row("RETRO0009", 10, 6_000_000, "new"))    # outlier: 600k/pt
            rate = retro.measured_rate(root, model="new")
            # median of 20k, 30k, 40k, 50k, 600k; the mean would be 148k
            self.assertEqual(rate["tokens_per_point"], 40_000)
            self.assertEqual(rate["sprints"],
                             ["RETRO0002", "RETRO0004", "RETRO0006", "RETRO0008", "RETRO0009"])
            self.assertTrue(rate["source"].startswith("measured"), rate["source"])
            for rid in rate["sprints"]:
                self.assertIn(rid, rate["source"])
            self.assertNotIn("RETRO0003", rate["source"])
            self.assertIsNone(rate.get("refused"))
            self.assertEqual(sorted(rate["skipped"]), ["RETRO0003", "RETRO0005"])
            # with no model named, the model doing the work is the latest single-model row's
            self.assertEqual(retro.measured_rate(root)["tokens_per_point"], 40_000)
            self.assertEqual(sprint.tokens_per_point(root)["rate"], 40_000)

    def test_a_thin_history_falls_back_before_the_seed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _history(root,
                     _row("RETRO0001", 10, 100_000, "old"),
                     _row("RETRO0002", 10, 200_000, "old"),
                     _row("RETRO0003", 10, 300_000, "new"),
                     _row("RETRO0004", 10, 9_000_000),             # no model: skipped
                     _row("RETRO0005", 10, 400_000, "old"),
                     _row("RETRO0006", 10, 500_000, "new"),
                     _row("RETRO0007", 10, 600_000, "old"))
            rate = retro.measured_rate(root, model="new")        # 2 rows for "new": too thin
            self.assertEqual(rate["sprints"],
                             ["RETRO0002", "RETRO0003", "RETRO0005", "RETRO0006", "RETRO0007"])
            self.assertEqual(rate["tokens_per_point"], 40_000)
            self.assertTrue(rate["source"].startswith("fallback"), rate["source"])
            self.assertIn("new", rate["source"])
            tpp = sprint.tokens_per_point(root)
            self.assertNotEqual(tpp["source"], sprint.RATE_SEED)
            # exactly RATE_MIN_ROWS rows for "new" is enough: measured, not a fallback
            p = retro.velocity_path(root)
            p.write_text(p.read_text(encoding="utf-8")
                         + _row("RETRO0008", 10, 700_000, "new"), encoding="utf-8")
            rate = retro.measured_rate(root, model="new")
            self.assertEqual(rate["sprints"], ["RETRO0003", "RETRO0006", "RETRO0008"])
            self.assertEqual(rate["tokens_per_point"], 50_000)
            self.assertTrue(rate["source"].startswith("measured on new"), rate["source"])
            # no usable row at all: only then the seed (a row naming several models is never one)
            _history(root, _row("RETRO0001", 10, 100_000, "mixed"),
                     _row("RETRO0002", 10, 200_000, "mixed"))
            self.assertIsNone(retro.measured_rate(root, model="new")["tokens_per_point"])
            tpp = sprint.tokens_per_point(root)
            self.assertEqual((tpp["rate"], tpp["source"]),
                             (sprint.POINTS_RATE_SEED, sprint.RATE_SEED))

    def test_unrecorded_model_rows_are_the_last_resort_before_the_seed(self) -> None:
        # D0256: rows naming no model are measured only when no single-model row exists
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _history(root,
                     _row("RETRO0001", 10, 100_000),
                     _row("RETRO0002", 10, 8_000_000, "mixed"),    # several models: never used
                     _row("RETRO0003", 10, 300_000),
                     _row("RETRO0004", 10, 9_000_000))              # outlier: 900k/pt
            rate = retro.measured_rate(root)
            self.assertEqual(rate["tokens_per_point"], 30_000)     # median, not the 313k mean
            self.assertEqual(rate["sprints"], ["RETRO0001", "RETRO0003", "RETRO0004"])
            self.assertTrue(rate["source"].startswith(
                "measured on unrecorded-model rows: median of"), rate["source"])
            self.assertEqual(rate["skipped"], ["RETRO0002"])
            tpp = sprint.tokens_per_point(root)
            self.assertEqual((tpp["rate"], tpp["source"]), (30_000, sprint.RATE_VELOCITY))
            # the cell is windowed like any other: its latest RATE_WINDOW rows
            p = retro.velocity_path(root)
            p.write_text(p.read_text(encoding="utf-8") + _row("RETRO0005", 10, 400_000)
                         + _row("RETRO0006", 10, 500_000) + _row("RETRO0007", 10, 600_000),
                         encoding="utf-8")
            rate = retro.measured_rate(root)
            self.assertEqual(rate["sprints"],
                             ["RETRO0003", "RETRO0004", "RETRO0005", "RETRO0006", "RETRO0007"])
            self.assertEqual(rate["tokens_per_point"], 50_000)
            # one single-model row anywhere: the unrecorded rows are ignored
            p.write_text(p.read_text(encoding="utf-8")
                         + _row("RETRO0008", 10, 50_000, "old"), encoding="utf-8")
            rate = retro.measured_rate(root, model="new")
            self.assertEqual((rate["tokens_per_point"], rate["sprints"]), (5_000, ["RETRO0008"]))
            self.assertTrue(rate["source"].startswith("fallback"), rate["source"])
            self.assertEqual(sorted(rate["skipped"]), [f"RETRO000{i}" for i in range(1, 8)])

    def test_the_work_model_is_the_open_runs_latest_stamp_else_the_latest_row(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _history(root,
                     _row("RETRO0001", 10, 100_000, "old"),
                     _row("RETRO0002", 10, 200_000, "new"),
                     _row("RETRO0003", 10, 300_000),                # no model
                     _row("RETRO0004", 10, 400_000, "mixed"))       # several models
            self.assertEqual(retro.work_model(root), "new")        # latest naming one model
            stamps = [{"model": "new"}, {"model": "old"}, {"model": "mixed"}, {"model": None}]
            run_state.update(root, run_id="RUN-TEST", **{run_state.TOKEN_STAMPS: stamps})
            self.assertEqual(retro.work_model(root), "old")        # the open run's latest stamp
            self.assertEqual(retro.measured_rate(root)["model"], "old")
            run_state.update(root, outcome=run_state.GOAL_REACHED)
            self.assertEqual(retro.work_model(root), "new")        # a closed run's stamps do not

    def test_this_repository_plans_on_a_measured_rate(self) -> None:
        self.assertTrue(retro.velocity_path(REPO).is_file(), "the corpus record is missing")
        rate = sprint.tokens_per_point(REPO)
        self.assertNotEqual(rate["source"], sprint.RATE_SEED, rate.get("basis"))
        self.assertGreater(rate["rate"], 0)


class MinuteRateTests(unittest.TestCase):
    def test_minutes_per_point_is_measured_or_says_not_measured(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _history(root,
                     _row("RETRO0001", 10, 100_000, "new", wall=6_000),     # 10 min/pt
                     _row("RETRO0002", 10, 100_000, "new"),                 # no minutes: skipped
                     _row("RETRO0003", 10, 100_000, "new", wall=18_000),    # 30 min/pt
                     _row("RETRO0004", 10, 100_000, wall=99_000),           # no model: skipped
                     _row("RETRO0005", 10, 100_000, "new", wall=12_000),    # 20 min/pt
                     # partly measured (2 of 3 units): its wall covers too few points, skipped
                     _row("RETRO0006", 10, 100_000, "new", wall=360_000, measured=2))
            got = retro.minutes_per_point(root)
            self.assertEqual(got["value"], 20.0)
            self.assertTrue(got["source"].startswith("measured"), got["source"])
            for rid in ("RETRO0001", "RETRO0003", "RETRO0005"):
                self.assertIn(rid, got["source"])
            _history(root, _row("RETRO0001", 10, 100_000, "new"))
            self.assertEqual(retro.minutes_per_point(root),
                             {"value": None, "source": "not measured"})


if __name__ == "__main__":
    unittest.main()
