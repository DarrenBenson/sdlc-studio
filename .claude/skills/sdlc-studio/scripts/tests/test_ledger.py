"""Unit tests for ledger.py (RED first - the script does not exist yet)."""
from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "ledger.py"


def _load():
    spec = importlib.util.spec_from_file_location("ledger", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ledger"] = mod
    spec.loader.exec_module(mod)
    return mod


class AppendTests(unittest.TestCase):
    def test_creates_and_appends(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _load().append_decision(root, "CR0020", "drop PL files", "evidence 0.27%")
            f = root / "sdlc-studio" / "decisions" / "CR0020.md"
            self.assertTrue(f.exists())
            text = f.read_text(encoding="utf-8")
            self.assertIn("drop PL files", text)
            self.assertIn("evidence 0.27%", text)
            self.assertIn("Decision", text)  # table header present

    def test_append_only_preserves(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.append_decision(root, "CR0020", "first", "r1")
            mod.append_decision(root, "CR0020", "second", "r2")
            mod.append_decision(root, "CR0020", "third", "r3")
            rows = mod.read_ledger(root, "CR0020")
            self.assertEqual([r["decision"] for r in rows], ["first", "second", "third"])

    def test_pipe_and_newline_do_not_drop_the_row(self) -> None:
        # A decision containing a table-breaking pipe or newline must still
        # round-trip as exactly one ruling (no silent data loss). Guards _clean.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.append_decision(root, "CR0020", "use A | B | C", "line1\nline2")
            rows = mod.read_ledger(root, "CR0020")
            self.assertEqual(len(rows), 1)
            self.assertNotIn("|", rows[0]["decision"])
            self.assertNotIn("\n", rows[0]["rationale"])


class ReadTests(unittest.TestCase):
    def test_reads_rows(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.append_decision(root, "CR0020", "dec", "rat")
            rows = mod.read_ledger(root, "CR0020")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["decision"], "dec")
            self.assertEqual(rows[0]["rationale"], "rat")
            self.assertIn("at", rows[0])

    def test_missing_ledger_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(_load().read_ledger(Path(d), "CRXXXX"), [])


class CliTests(unittest.TestCase):
    def test_record_then_show(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            rc = mod.main(["record", "--tranche", "CR0020", "--decision", "d",
                           "--rationale", "r", "--root", str(root)])
            self.assertEqual(rc, 0)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc2 = mod.main(["show", "--tranche", "CR0020", "--root", str(root)])
            self.assertEqual(rc2, 0)
            self.assertIn("d", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
