"""Unit tests for tools/bench/runner.py (US0074/CR0178)."""
from __future__ import annotations

import importlib.util
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
    def test_discovers_all_three_approved_fixtures(self) -> None:
        self.assertEqual(runner.list_fixtures(), [
            "brownfield-lru-cache", "brownfield-pagination", "greenfield-csv-dedupe"])

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


if __name__ == "__main__":
    unittest.main()
