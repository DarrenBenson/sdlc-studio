"""Unit tests for deploy.py - the orchestrate-only deploy last-mile (RFC0013)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import unittest.mock as mock
from datetime import datetime
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
_spec = importlib.util.spec_from_file_location("deploy", SCR / "deploy.py")
assert _spec and _spec.loader
deploy = importlib.util.module_from_spec(_spec)
sys.modules["deploy"] = deploy
_spec.loader.exec_module(deploy)

GREEN = {"ok": True, "checks": []}
RED = {"ok": False, "checks": [
    {"check": "conformance", "blocking": True, "status": "fail", "detail": "3 non-conformant"}]}


class PreflightTests(unittest.TestCase):
    def _proj(self, d):
        (Path(d) / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        return d

    def test_ready_when_gate_green_and_never_executes(self):
        with tempfile.TemporaryDirectory() as d:
            self._proj(d)
            with mock.patch.object(deploy.gate, "run_gate", return_value=GREEN):
                r = deploy.preflight(d)
            self.assertTrue(r["ready"])
            self.assertFalse(r["executes"])          # the skill never deploys

    def test_not_ready_when_gate_red(self):
        with tempfile.TemporaryDirectory() as d:
            self._proj(d)
            with mock.patch.object(deploy.gate, "run_gate", return_value=RED):
                r = deploy.preflight(d)
            self.assertFalse(r["ready"])
            self.assertEqual(len(r["gate_fails"]), 1)
            self.assertEqual(r["gate_fails"][0]["check"], "conformance")

    def test_handoff_surfaces_configured_command_and_rollback(self):
        cfg = {"command": "./deploy.sh", "smoke": "http GET /h", "soak_minutes": 5,
               "rollback": "./rollback.sh"}
        with tempfile.TemporaryDirectory() as d:
            self._proj(d)
            with mock.patch.object(deploy, "deploy_config", return_value=cfg), \
                 mock.patch.object(deploy.gate, "run_gate", return_value=GREEN):
                r = deploy.preflight(d)
            joined = " ".join(r["handoff"])
            self.assertIn("./deploy.sh", joined)
            self.assertIn("./rollback.sh", joined)
            self.assertIn("5 min", joined)

    def test_handoff_notes_absent_config(self):
        with tempfile.TemporaryDirectory() as d:
            self._proj(d)
            with mock.patch.object(deploy, "deploy_config",
                                   return_value={"command": "", "smoke": "", "soak_minutes": 0, "rollback": ""}), \
                 mock.patch.object(deploy.gate, "run_gate", return_value=GREEN):
                r = deploy.preflight(d)
            joined = " ".join(r["handoff"])
            self.assertIn("no deploy.command", joined)
            self.assertIn("no deploy.rollback", joined)


class RecordTests(unittest.TestCase):
    def test_appends_timestamped_row(self):
        with tempfile.TemporaryDirectory() as d:
            deploy.record(d, "rolled-out", "v1.2.3", now=datetime(2026, 1, 2, 3, 4))
            log = (Path(d) / "sdlc-studio" / "deploy-log.md").read_text()
            self.assertIn("2026-01-02 03:04", log)
            self.assertIn("rolled-out", log)
            self.assertIn("v1.2.3", log)

    def test_rejects_unknown_status(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                deploy.record(d, "shipped-it")

    def test_sanitises_pipe_and_newline(self):
        with tempfile.TemporaryDirectory() as d:
            deploy.record(d, "failed", "a|b\nc", now=datetime(2026, 1, 1, 0, 0))
            log = (Path(d) / "sdlc-studio" / "deploy-log.md").read_text()
            self.assertIn("a/b c", log)             # pipe -> /, newline -> space (table-safe)

    def test_one_header_many_rows(self):
        with tempfile.TemporaryDirectory() as d:
            deploy.record(d, "rolled-out", "one", now=datetime(2026, 1, 1, 0, 0))
            deploy.record(d, "verified", "two", now=datetime(2026, 1, 1, 0, 1))
            log = (Path(d) / "sdlc-studio" / "deploy-log.md").read_text()
            self.assertEqual(log.count("| When | Status | Detail |"), 1)
            self.assertIn("one", log)
            self.assertIn("two", log)


class SafetyGuardTests(unittest.TestCase):
    def test_deploy_never_shells_out(self):
        # the orchestrate-only contract in code: deploy.py must contain NO execution primitives
        src = (SCR / "deploy.py").read_text()
        for forbidden in ("subprocess", "os.system", "Popen", "os.popen", "exec(", "eval("):
            self.assertNotIn(forbidden, src, f"deploy.py must not use {forbidden}")

    def test_cmd_preflight_exit_codes(self):
        import argparse
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "sdlc-studio").mkdir()
            ns = argparse.Namespace(root=d, format="text")
            with mock.patch.object(deploy.gate, "run_gate", return_value=GREEN):
                self.assertEqual(deploy.cmd_preflight(ns), 0)
            with mock.patch.object(deploy.gate, "run_gate", return_value=RED):
                self.assertEqual(deploy.cmd_preflight(ns), 1)


if __name__ == "__main__":
    unittest.main()
