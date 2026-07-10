"""Unit tests for tools/eval_run.py - the deterministic spine of the two-Claude eval gate."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "eval_run.py"
_spec = importlib.util.spec_from_file_location("eval_run", TOOLS)
eval_run = importlib.util.module_from_spec(_spec)
sys.modules["eval_run"] = eval_run
_spec.loader.exec_module(eval_run)


def _scenario(with_fixture: bool = True) -> dict:
    sc = {
        "id": "99-test", "title": "t", "prompt": "do the thing",
        "expected_behaviours": [
            {"id": "EB1", "description": "a", "severity": "blocking"},
            {"id": "EB2", "description": "b", "severity": "advisory"},
        ],
        "setup": "prose setup text",
    }
    if with_fixture:
        sc["fixture"] = {"files": {
            "sdlc-studio/.config.yaml": "schema_version: 3\n",
            "sdlc-studio/bugs/_index.md": "# Bugs\n",
        }}
    return sc


class EvalRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        (root / "scenarios").mkdir()
        (root / ".results").mkdir()
        self._old = (eval_run.SCENARIOS, eval_run.RESULTS)
        eval_run.SCENARIOS = root / "scenarios"
        eval_run.RESULTS = root / ".results"
        self.fx = root / "fx"

    def tearDown(self) -> None:
        eval_run.SCENARIOS, eval_run.RESULTS = self._old
        self._tmp.cleanup()

    def _write(self, sc: dict) -> None:
        (eval_run.SCENARIOS / f"{sc['id']}.json").write_text(
            json.dumps(sc), encoding="utf-8")

    def _main(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = eval_run.main(list(argv))
        return rc, out.getvalue(), err.getvalue()

    def test_setup_builds_fixture_and_prints_prompt(self) -> None:
        self._write(_scenario())
        rc, out, _ = self._main("setup", "--scenario", "99-test", "--dir", str(self.fx))
        self.assertEqual(rc, 0)
        self.assertIn("do the thing", out)
        self.assertIn("EB1 (blocking)", out)
        self.assertEqual((self.fx / "sdlc-studio" / ".config.yaml").read_text(encoding="utf-8"),
                         "schema_version: 3\n")

    def test_setup_without_fixture_spec_degrades_honestly(self) -> None:
        self._write(_scenario(with_fixture=False))
        rc, _, err = self._main("setup", "--scenario", "99-test", "--dir", str(self.fx))
        self.assertEqual(rc, 1)
        self.assertIn("prose setup text", err)
        self.assertFalse(self.fx.exists())

    def test_record_rejects_unknown_behaviour(self) -> None:
        self._write(_scenario())
        rc, _, err = self._main("record", "--scenario", "99-test", "--run", "r1",
                                "--behaviour", "EB9", "--verdict", "pass", "--evidence", "x")
        self.assertEqual(rc, 2)
        self.assertIn("EB9", err)

    def test_report_gates_on_blocking_and_ungraded(self) -> None:
        self._write(_scenario())
        self._main("record", "--scenario", "99-test", "--run", "r1",
                   "--behaviour", "EB1", "--verdict", "pass", "--evidence", "ok")
        # EB2 (advisory) ungraded -> not a gate failure
        rc, out, _ = self._main("report", "--run", "r1")
        self.assertEqual(rc, 0, out)
        self.assertIn("gate pass", out)
        # now a blocking FAIL flips the gate
        self._main("record", "--scenario", "99-test", "--run", "r1",
                   "--behaviour", "EB1", "--verdict", "fail", "--evidence", "broke")
        rc, out, _ = self._main("report", "--run", "r1")
        self.assertEqual(rc, 1)
        self.assertIn("GATE FAIL", out)

    def test_ungraded_blocking_behaviour_fails_the_gate(self) -> None:
        self._write(_scenario())
        self._main("record", "--scenario", "99-test", "--run", "r1",
                   "--behaviour", "EB2", "--verdict", "pass", "--evidence", "ok")
        rc, out, _ = self._main("report", "--run", "r1")   # EB1 (blocking) never graded
        self.assertEqual(rc, 1)
        self.assertIn("UNGRADED", out)

    def test_unknown_scenario_errors(self) -> None:
        rc, _, err = self._main("setup", "--scenario", "nope", "--dir", str(self.fx))
        self.assertEqual(rc, 2)
        self.assertIn("no scenario", err)


if __name__ == "__main__":
    unittest.main()
