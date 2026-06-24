"""Unit tests for decisions.py - the project decisions log (CR0080)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


decisions = _load("decisions")


class DecisionsTests(unittest.TestCase):
    def test_add_auto_numbers_and_appends(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            r1 = decisions.add(repo, "Anonymous-first, accounts in M2", "avoid a sign-up wall")
            r2 = decisions.add(repo, "Stored-hash tokens", "no signed-token secret to manage")
            self.assertEqual(r1["id"], "D0001")
            self.assertEqual(r2["id"], "D0002")        # auto-incremented
            rows = decisions.list_decisions(repo)
            self.assertEqual([x["id"] for x in rows], ["D0001", "D0002"])
            self.assertEqual(rows[0]["status"], "accepted")

    def test_list_filters_by_status(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            decisions.add(repo, "a", "r")
            decisions.add(repo, "b", "r", status="superseded")
            self.assertEqual(len(decisions.list_decisions(repo, status="superseded")), 1)
            self.assertEqual(len(decisions.list_decisions(repo)), 2)

    def test_pipe_in_text_is_escaped(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            decisions.add(repo, "use a | b shape", "round-trips")
            rows = decisions.list_decisions(repo)
            self.assertEqual(len(rows), 1)             # the pipe did not split into extra columns

    def test_promote_records_backlink(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            r = decisions.promote(repo, "PRD-OQ3", "Anonymous-first", "avoid a sign-up wall")
            rows = decisions.list_decisions(repo)
            self.assertEqual(r["id"], "D0001")
            self.assertIn("[from PRD-OQ3]", rows[0]["rationale"])   # back-linked, one record

    def test_ensure_log_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            self.assertTrue(decisions.ensure_log(repo))
            self.assertFalse(decisions.ensure_log(repo))   # second call is a no-op


if __name__ == "__main__":
    unittest.main()
