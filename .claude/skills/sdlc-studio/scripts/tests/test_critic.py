"""Unit tests for critic.py - committed critic-verdict record (CR0023). RED first."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "critic.py"


def _load():
    spec = importlib.util.spec_from_file_location("critic", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["critic"] = mod
    spec.loader.exec_module(mod)
    return mod


class RecordTests(unittest.TestCase):
    def test_record_and_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0017", "approve")
            v = mod.verdict_for(root, "US0017")
            self.assertIsNotNone(v)
            self.assertEqual(v["verdict"], "APPROVE")
            self.assertEqual(mod.verdict_for(root, "US9999"), None)

    def test_latest_wins_and_append_only(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0017", "reject", issues="bug")
            mod.record_verdict(root, "US0017", "approve")
            self.assertEqual(len(mod.read_verdicts(root)), 2)        # append-only
            self.assertEqual(mod.verdict_for(root, "US0017")["verdict"], "APPROVE")  # latest

    def test_pipe_in_issues_does_not_break_row(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0017", "approve", issues="a | b")
            self.assertEqual(len(mod.read_verdicts(root)), 1)


class CliTests(unittest.TestCase):
    def test_cli_record(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            rc = mod.main(["record", "--unit", "US0017", "--verdict", "approve", "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertEqual(mod.verdict_for(root, "US0017")["verdict"], "APPROVE")

    def test_underscores_escaped_to_avoid_md037(self):
        # BG0023: underscored identifiers in the issues text must be escaped so they cannot
        # pair into markdown emphasis (markdownlint MD037).
        with tempfile.TemporaryDirectory() as d:
            mod = _load()
            mod.record_verdict(d, "US0001", "approve",
                               issues="fixed _read and _index_row and gate.run_gate")
            text = mod.verdicts_path(d).read_text(encoding="utf-8")
            self.assertNotIn(" _read", text)        # no bare underscore-led token
            self.assertIn(r"\_read", text)          # escaped instead
            self.assertTrue(any(v["unit"] == "US0001" for v in mod.read_verdicts(d)))


if __name__ == "__main__":
    unittest.main()
