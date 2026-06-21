"""Unit tests for telemetry.py - run telemetry recorder (CR0050)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "telemetry.py"


def _load():
    spec = importlib.util.spec_from_file_location("telemetry", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["telemetry"] = mod
    spec.loader.exec_module(mod)
    return mod


tel = _load()


class RecordTests(unittest.TestCase):
    def test_record_omits_none_fields(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rec = tel.record(d, {"id": "US0001", "type": "story", "iterations": 3,
                                 "wall_time_s": None, "tokens": None})
            self.assertEqual(rec, {"id": "US0001", "type": "story", "iterations": 3})
            self.assertNotIn("tokens", rec)

    def test_appends_not_overwrites(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tel.record(d, {"id": "US0001"})
            tel.record(d, {"id": "US0002"})
            recs = tel.read_all(d)
            self.assertEqual([r["id"] for r in recs], ["US0001", "US0002"])

    def test_writes_to_gitignored_state_dir(self) -> None:
        # Must land under sdlc-studio/.local/ (the gitignored state dir), not repo-root .local/.
        with tempfile.TemporaryDirectory() as d:
            tel.record(d, {"id": "X"})
            self.assertTrue((Path(d) / "sdlc-studio" / ".local" / "telemetry.jsonl").exists())
            self.assertFalse((Path(d) / ".local" / "telemetry.jsonl").exists())

    def test_unknown_field_dropped(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rec = tel.record(d, {"id": "U1", "secret": "hunter2", "cwd": "/x"})
            self.assertEqual(rec, {"id": "U1"})  # only whitelisted FIELDS are written
            self.assertNotIn("hunter2", (Path(d) / "sdlc-studio" / ".local" / "telemetry.jsonl").read_text())

    def test_read_all_skips_malformed_lines(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tel.record(d, {"id": "good"})
            p = Path(d) / "sdlc-studio" / ".local" / "telemetry.jsonl"
            with p.open("a", encoding="utf-8") as fh:
                fh.write("{ not json\n\n")
            tel.record(d, {"id": "good2"})
            self.assertEqual([r["id"] for r in tel.read_all(d)], ["good", "good2"])

    def test_read_all_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(tel.read_all(d), [])

    def test_record_never_raises_on_unwritable(self) -> None:
        # telemetry is advisory - a write failure must be swallowed, returning the record.
        rec = tel.record("/proc/nonexistent-rootlevel-xyz", {"id": "Z"})
        self.assertEqual(rec["id"], "Z")

    def test_tokens_recorded_when_supplied(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rec = tel.record(d, {"id": "T", "tokens": 1234})
            self.assertEqual(rec["tokens"], 1234)


if __name__ == "__main__":
    unittest.main()
