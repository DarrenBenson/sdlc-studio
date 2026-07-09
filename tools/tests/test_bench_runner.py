"""Unit tests for tools/bench/runner.py (US0074/CR0178)."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "bench" / "runner.py"
FIXTURES_DIR = SCRIPT.parent / "fixtures"


def _load():
    spec = importlib.util.spec_from_file_location("bench_runner", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["bench_runner"] = mod
    spec.loader.exec_module(mod)
    return mod


runner = _load()


class ListFixturesTests(unittest.TestCase):
    def test_discovers_all_registered_fixtures(self) -> None:
        self.assertEqual(runner.list_fixtures(), [
            "brownfield-lru-cache", "brownfield-pagination",
            "change-request-ledger-drift", "greenfield-csv-dedupe",
            "multifile-notify-digest"])

    def test_empty_dir_returns_empty_list(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(runner.list_fixtures(Path(d)), [])


class PrepareWorkspaceTests(unittest.TestCase):
    def test_copies_visible_files_only_never_hidden(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            dest = Path(d) / "ws"
            runner.prepare_workspace("greenfield-csv-dedupe", "A", dest)
            self.assertTrue((dest / "cli.py").exists())
            self.assertTrue((dest / "TICKET.md").exists())
            self.assertFalse((dest / "test_hidden.py").exists())
            self.assertFalse((dest / "hidden").exists())

    def test_arm_a_gets_pipeline_claude_md(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            dest = Path(d) / "ws"
            runner.prepare_workspace("brownfield-pagination", "A", dest)
            text = (dest / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn("sdlc-studio", text)

    def test_arm_b_gets_baseline_claude_md(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            dest = Path(d) / "ws"
            runner.prepare_workspace("brownfield-pagination", "B", dest)
            text = (dest / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn("Working style", text)
            self.assertNotIn("sdlc-studio", text)

    def test_unknown_arm_raises(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                runner.prepare_workspace("brownfield-pagination", "C", Path(d) / "ws")

    def test_unknown_fixture_raises(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                runner.prepare_workspace("does-not-exist", "A", Path(d) / "ws")


class ScoreTests(unittest.TestCase):
    def test_seeded_bug_fails_and_reports_defect_escape(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d)
            runner.prepare_workspace("brownfield-pagination", "A", ws)
            r = runner.score("brownfield-pagination", ws)
            self.assertFalse(r["passed"])
            self.assertTrue(r["defect_escape"])

    def test_correct_fix_passes_and_reports_no_defect_escape(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d)
            runner.prepare_workspace("brownfield-pagination", "A", ws)
            (ws / "paginate.py").write_text(
                "def paginate(items, page, page_size):\n"
                "    start = (page - 1) * page_size\n"
                "    return items[start:start + page_size]\n",
                encoding="utf-8")
            r = runner.score("brownfield-pagination", ws)
            self.assertTrue(r["passed"])
            self.assertFalse(r["defect_escape"])

    def test_scoring_never_writes_into_the_fixture_hidden_dir(self) -> None:
        # scoring copies hidden/ into a tempdir, never runs pytest from the fixture itself
        hidden_dir = FIXTURES_DIR / "brownfield-pagination" / "hidden"
        before = sorted(p.name for p in hidden_dir.iterdir())
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d)
            runner.prepare_workspace("brownfield-pagination", "A", ws)
            runner.score("brownfield-pagination", ws)
        after = sorted(p.name for p in hidden_dir.iterdir())
        self.assertEqual(before, after)


class RecordAndSummarizeTests(unittest.TestCase):
    def test_record_requires_fixture_arm_run_id(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "runs.jsonl"
            with self.assertRaises(ValueError):
                runner.record({"fixture": "x"}, results_path=path)

    def test_record_then_read_all_roundtrips(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "runs.jsonl"
            runner.record({"fixture": "f", "arm": "A", "run_id": "1", "tokens": 100}, path)
            runner.record({"fixture": "f", "arm": "A", "run_id": "2", "tokens": 200}, path)
            rows = runner.read_all(path)
            self.assertEqual([r["run_id"] for r in rows], ["1", "2"])

    def test_summarize_groups_by_fixture_and_arm_and_omits_absent_fields(self) -> None:
        rows = [
            {"fixture": "f", "arm": "A", "run_id": "1", "tokens": 100, "defect_escape": False},
            {"fixture": "f", "arm": "A", "run_id": "2", "tokens": 300, "defect_escape": True},
            {"fixture": "f", "arm": "B", "run_id": "1", "defect_escape": False},
        ]
        s = runner.summarize(rows)
        self.assertEqual(s["f::A"]["n"], 2)
        self.assertEqual(s["f::A"]["mean_tokens"], 200.0)
        self.assertEqual(s["f::A"]["defect_escape_rate"], 0.5)
        self.assertEqual(s["f::B"]["n"], 1)
        self.assertIsNone(s["f::B"]["mean_tokens"])  # no run in B carried tokens

    def test_summarize_min_max(self) -> None:
        rows = [
            {"fixture": "f", "arm": "A", "run_id": "1", "tokens": 100, "wall_time_s": 40},
            {"fixture": "f", "arm": "A", "run_id": "2", "tokens": 300, "wall_time_s": 60},
        ]
        s = runner.summarize(rows)
        self.assertEqual((s["f::A"]["min_tokens"], s["f::A"]["max_tokens"]), (100, 300))
        self.assertEqual((s["f::A"]["min_wall_time_s"], s["f::A"]["max_wall_time_s"]), (40, 60))


class SubdirScoringTests(unittest.TestCase):
    """v2 harness: hidden/ trees with subdirectories score correctly."""

    def test_hidden_subdirectories_copied_for_scoring(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            fixtures = Path(d) / "fixtures"
            f = fixtures / "sub-fixture"
            (f / "visible").mkdir(parents=True)
            (f / "visible" / "mod.py").write_text("X = 1\n", encoding="utf-8")
            hidden = f / "hidden"
            (hidden / "pkg").mkdir(parents=True)
            (hidden / "pkg" / "helper.py").write_text("HELP = 2\n", encoding="utf-8")
            (hidden / "conftest.py").write_text(
                "import sys\nfrom pathlib import Path\nimport pytest\n"
                "def pytest_addoption(parser):\n"
                "    parser.addoption('--workspace', action='store', required=True)\n"
                "@pytest.fixture\n"
                "def workspace(request):\n"
                "    return Path(request.config.getoption('--workspace'))\n",
                encoding="utf-8")
            (hidden / "test_hidden.py").write_text(
                "import sys, importlib.util\nfrom pathlib import Path\n"
                "def test_subdir_present_and_workspace_readable(workspace):\n"
                "    here = Path(__file__).parent\n"
                "    assert (here / 'pkg' / 'helper.py').exists()\n"
                "    assert (workspace / 'mod.py').exists()\n",
                encoding="utf-8")
            ws = Path(d) / "ws"
            runner.prepare_workspace("sub-fixture", "B", ws, fixtures_dir=fixtures)
            r = runner.score("sub-fixture", ws, fixtures_dir=fixtures)
            self.assertTrue(r["passed"], r["output"])


class EnvironmentalIsolationTests(unittest.TestCase):
    """v2 harness: arms A/R get the skill copied IN; arm B's workspace has no skill at all."""

    def test_arm_a_workspace_contains_the_skill(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d) / "ws"
            runner.prepare_workspace("brownfield-pagination", "A", ws)
            self.assertTrue((ws / ".claude" / "skills" / "sdlc-studio" / "SKILL.md").exists())

    def test_arm_b_workspace_contains_no_skill(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d) / "ws"
            runner.prepare_workspace("brownfield-pagination", "B", ws)
            self.assertFalse((ws / ".claude").exists())

    def test_arm_r_gets_skill_plus_routing_config(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d) / "ws"
            runner.prepare_workspace("brownfield-pagination", "R", ws)
            self.assertTrue((ws / ".claude" / "skills" / "sdlc-studio" / "SKILL.md").exists())
            cfg = (ws / "sdlc-studio" / ".config.yaml").read_text(encoding="utf-8")
            self.assertIn("enabled: true", cfg)
            text = (ws / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn("routing", text)

    def test_hidden_audit_reference_never_copied(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d) / "ws"
            runner.prepare_workspace("brownfield-pagination", "A", ws)
            for held_back in ("test_hidden.py", "hidden", "audit", "reference"):
                self.assertFalse((ws / held_back).exists(), held_back)


class MetricsCaptureTests(unittest.TestCase):
    """v2 harness: automatic token/time capture with the manual fallback disclosed."""

    def test_record_metrics_json_stamps_parsed_source(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            metrics = Path(d) / "m.json"
            metrics.write_text('{"tokens": 12345, "wall_time_s": 61.5}', encoding="utf-8")
            results = Path(d) / "runs.jsonl"
            import contextlib, io
            real = runner.RESULTS_PATH
            runner.RESULTS_PATH = results
            try:
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc = runner.main(["record", "--fixture", "f", "--arm", "A",
                                      "--run-id", "1", "--metrics-json", str(metrics)])
            finally:
                runner.RESULTS_PATH = real
            self.assertEqual(rc, 0)
            row = runner.read_all(results)[0]
            self.assertEqual(row["tokens"], 12345)
            self.assertEqual(row["metrics_source"], "parsed")

    def test_manual_flags_stamp_manual_source(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            results = Path(d) / "runs.jsonl"
            import contextlib, io
            real = runner.RESULTS_PATH
            runner.RESULTS_PATH = results
            try:
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc = runner.main(["record", "--fixture", "f", "--arm", "B",
                                      "--run-id", "1", "--tokens", "500"])
            finally:
                runner.RESULTS_PATH = real
            self.assertEqual(rc, 0)
            row = runner.read_all(results)[0]
            self.assertEqual(row["metrics_source"], "manual")


class CostIndexTests(unittest.TestCase):
    """v2 harness: arm R's cost index from an operator-supplied price map."""

    def test_cost_index_arithmetic(self) -> None:
        prices = runner.parse_price_map("tiny=0.25,medium=1,large=5")
        mix = runner.parse_model_mix("tiny:2,medium:1")
        self.assertEqual(runner.cost_index(mix, prices), 1.5)

    def test_no_prices_means_no_cost_column(self) -> None:
        rows = [{"fixture": "f", "arm": "R", "run_id": "1",
                 "model_mix": {"tiny": 2}, "defect_escape": False}]
        s = runner.summarize(rows)  # no price map supplied
        self.assertNotIn("mean_cost_index", s["f::R"])

    def test_missing_tier_price_yields_none_not_zero(self) -> None:
        self.assertIsNone(runner.cost_index({"tiny": 1, "xlarge": 1}, {"tiny": 0.25}))

    def test_summarize_with_prices(self) -> None:
        rows = [{"fixture": "f", "arm": "R", "run_id": "1",
                 "model_mix": {"tiny": 2, "medium": 1}, "defect_escape": False}]
        s = runner.summarize(rows, prices={"tiny": 0.25, "medium": 1})
        self.assertEqual(s["f::R"]["mean_cost_index"], 1.5)


class TranscriptMetricsTests(unittest.TestCase):
    def _load_tm(self):
        import importlib.util
        script = Path(__file__).resolve().parents[1] / "bench" / "transcript_metrics.py"
        spec = importlib.util.spec_from_file_location("transcript_metrics", script)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["transcript_metrics"] = mod
        spec.loader.exec_module(mod)
        return mod

    def test_extract_agent_tool_blob(self) -> None:
        tm = self._load_tm()
        m = tm.extract({"subagent_tokens": 42242, "duration_ms": 52636})
        self.assertEqual(m, {"tokens": 42242, "wall_time_s": 52.6})

    def test_extract_usage_object(self) -> None:
        tm = self._load_tm()
        m = tm.extract({"usage": {"input_tokens": 100, "output_tokens": 50}, "duration_s": 7})
        self.assertEqual(m, {"tokens": 150, "wall_time_s": 7.0})

    def test_unrecognisable_file_raises_not_nulls(self) -> None:
        tm = self._load_tm()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.json"
            p.write_text('{"irrelevant": true}', encoding="utf-8")
            with self.assertRaises(ValueError):
                tm.parse_file(p)


class PhaseFieldTests(unittest.TestCase):
    """US0093/CR0196 AC1: record stamps a phase (default measured); classify + backfill
    stamp existing rows (v2n1 = calibration, everything else = measured)."""

    def test_record_defaults_phase_measured(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rp = Path(d) / "runs.jsonl"
            runner.record({"fixture": "f", "arm": "A", "run_id": "n2"}, results_path=rp)
            self.assertEqual(runner.read_all(rp)[0]["phase"], "measured")

    def test_record_keeps_explicit_calibration_phase(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rp = Path(d) / "runs.jsonl"
            runner.record({"fixture": "f", "arm": "A", "run_id": "v2n1",
                           "phase": "calibration"}, results_path=rp)
            self.assertEqual(runner.read_all(rp)[0]["phase"], "calibration")

    def test_classify_phase_v2n1_is_calibration_else_measured(self) -> None:
        self.assertEqual(runner.classify_phase({"run_id": "v2n1"}), "calibration")
        self.assertEqual(runner.classify_phase({"run_id": "n2"}), "measured")
        self.assertEqual(runner.classify_phase({"run_id": "n1"}), "measured")

    def test_backfill_stamps_only_rows_missing_phase(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rp = Path(d) / "runs.jsonl"
            # two legacy rows without phase (one v2n1 calibration, one measured) + one already stamped
            for e in ({"fixture": "f", "arm": "A", "run_id": "v2n1"},
                      {"fixture": "f", "arm": "A", "run_id": "n3"}):
                rp.parent.mkdir(parents=True, exist_ok=True)
                with rp.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(e) + "\n")
            runner.record({"fixture": "f", "arm": "A", "run_id": "n4",
                           "phase": "measured"}, results_path=rp)
            stamped = runner.backfill_phases(rp)
            self.assertEqual(stamped, 2)                     # only the two legacy rows
            by = {r["run_id"]: r["phase"] for r in runner.read_all(rp)}
            self.assertEqual(by["v2n1"], "calibration")
            self.assertEqual(by["n3"], "measured")
            self.assertEqual(runner.backfill_phases(rp), 0)  # idempotent


class SummaryPhaseTests(unittest.TestCase):
    """US0093/CR0196 AC2: summary excludes calibration unless opted back in."""

    ROWS = [
        {"fixture": "f", "arm": "A", "run_id": "n2", "phase": "measured", "tokens": 100},
        {"fixture": "f", "arm": "A", "run_id": "n3", "phase": "measured", "tokens": 200},
        {"fixture": "f", "arm": "A", "run_id": "v2n1", "phase": "calibration", "tokens": 9000},
    ]

    def test_summary_excludes_calibration_by_default(self) -> None:
        s = runner.summarize(self.ROWS)
        self.assertEqual(s["f::A"]["n"], 2)
        self.assertEqual(s["f::A"]["mean_tokens"], 150.0)

    def test_include_phase_opts_calibration_back_in(self) -> None:
        s = runner.summarize(self.ROWS, include_phases={"measured", "calibration"})
        self.assertEqual(s["f::A"]["n"], 3)

    def test_missing_phase_counts_as_measured(self) -> None:
        s = runner.summarize([{"fixture": "f", "arm": "A", "run_id": "n2", "tokens": 100}])
        self.assertEqual(s["f::A"]["n"], 1)


class IncludePhaseValidationTests(unittest.TestCase):
    """US0093/CR0196: a mistyped --include-phase errors rather than silently excluding."""

    def test_unknown_include_phase_raises(self) -> None:
        with self.assertRaises(ValueError):
            runner.main(["summary", "--include-phase", "calibraton"])  # typo

    def test_record_does_not_mutate_caller_dict(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            e = {"fixture": "f", "arm": "A", "run_id": "n2"}
            runner.record(e, results_path=Path(d) / "runs.jsonl")
            self.assertNotIn("phase", e)                     # caller's dict untouched


class CalibrationIsolationTests(unittest.TestCase):
    """US0093/CR0196 AC3: a calibration row cannot move a measured aggregate."""

    def test_calibration_row_leaves_measured_aggregate_identical(self) -> None:
        measured = [
            {"fixture": "f", "arm": "A", "run_id": "n2", "phase": "measured",
             "tokens": 100, "wall_time_s": 10},
            {"fixture": "f", "arm": "A", "run_id": "n3", "phase": "measured",
             "tokens": 200, "wall_time_s": 20},
        ]
        base = runner.summarize(measured)
        with_cal = runner.summarize(measured + [
            {"fixture": "f", "arm": "A", "run_id": "v2n1", "phase": "calibration",
             "tokens": 9999, "wall_time_s": 999}])
        self.assertEqual(base["f::A"], with_cal["f::A"])


if __name__ == "__main__":
    unittest.main()
