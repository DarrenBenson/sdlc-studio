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
sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the git helper
import gitutil  # noqa: E402 - confined git for the fixture repos below
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


import datetime as dt  # noqa: E402


def _git(cwd, *args):
    gitutil.git(list(args), cwd=cwd)


def _ledger(root: Path, rows) -> None:
    sd = root / "sdlc-studio"
    sd.mkdir(parents=True, exist_ok=True)
    body = ("# Deploy Log\n\nAppend-only record of deploy outcomes.\n\n"
            "| When | Status | Detail |\n| --- | --- | --- |\n")
    body += "".join(f"| {when} | {status} | {detail} |\n" for when, status, detail in rows)
    (sd / "deploy-log.md").write_text(body, encoding="utf-8")


def _high_bug(root: Path, num: int, created: str, fixed_rev: str | None) -> Path:
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    rev = ""
    if fixed_rev:
        rev = ("\n## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
               f"| {created} | t | Raised |\n| {fixed_rev} | t | Fixed |\n")
    p = d / f"BG{num:04d}-x.md"
    p.write_text(f"# BG{num:04d}: b\n\n> **Status:** Fixed\n> **Severity:** High\n"
                 f"> **Created:** {created}\n> **Points:** 2\n{rev}", encoding="utf-8")
    return p


# ASYMMETRIC by design: 3 deploy events, 1 failure, 4 rows. A symmetric fixture
# (2 events = 2 failures) let a failures-numerator-swap mutant pass green - the
# QA critic ran that mutant; this shape makes the classifier itself falsifiable.
LEDGER_ROWS = [("2026-07-01 10:00", "verified", "v4.0"),
               ("2026-07-05 10:00", "rolled-out", "v4.1"),
               ("2026-07-08 10:00", "failed", "v4.2 attempt"),
               ("2026-07-10 10:00", "verified", "v4.2 retry ok")]


class DoraKeysTests(unittest.TestCase):
    def test_four_keys_computed_with_windows_stated(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _git(root, "init", "-q")
            _git(root, "config", "user.email", "t@t")
            _git(root, "config", "user.name", "t")
            (root / "a.txt").write_text("1", encoding="utf-8")
            _git(root, "add", "-A")
            _git(root, "commit", "-q", "-m", "c1", "--date", "2026-07-03T10:00:00")
            (root / "a.txt").write_text("2", encoding="utf-8")
            _git(root, "add", "-A")
            _git(root, "commit", "-q", "-m", "c2", "--date", "2026-07-04T10:00:00")
            _ledger(root, LEDGER_ROWS)
            _high_bug(root, 1, "2026-07-01", "2026-07-03")
            m = deploy.metrics(root)
            self.assertTrue(m["applicable"])
            self.assertEqual(m["deployment_frequency"]["events"], 3)  # verified x2 + rolled-out
            self.assertIn("window", m["deployment_frequency"])
            self.assertEqual(m["change_failure_rate"]["rate"], 0.25)  # exactly 1 failed of 4
            self.assertEqual(m["change_failure_rate"]["failures"], 1)
            # commits c1/c2 precede the 07-05 rolled-out: leads 2d and 1d -> median 1.5
            self.assertEqual(m["lead_time_days"]["median"], 1.5)
            self.assertEqual(m["mttr_days"]["mean"], 2)               # 07-01 -> 07-03

    def test_cli_parser_accepts_root_after_subcommand(self):
        # the family convention: --root valid before OR after the subcommand
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            _ledger(Path(d), LEDGER_ROWS)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = deploy.main(["metrics", "--root", d, "--format", "json"])
            self.assertEqual(rc, 0)
            import json as _j
            self.assertTrue(_j.loads(buf.getvalue())["applicable"])


class DoraRefusalTests(unittest.TestCase):
    def test_lead_time_refused_without_git_others_still_compute(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ledger(root, LEDGER_ROWS)
            _high_bug(root, 1, "2026-07-01", "2026-07-03")
            m = deploy.metrics(root)
            self.assertTrue(m["applicable"])
            self.assertIn("unmeasurable", m["lead_time_days"])
            self.assertEqual(m["deployment_frequency"]["events"], 3)
            self.assertEqual(m["change_failure_rate"]["rate"], 0.25)
            self.assertEqual(m["mttr_days"]["mean"], 2)

    def test_cfr_unmeasurable_on_ledger_with_no_parseable_rows(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio"
            sd.mkdir(parents=True)
            (sd / "deploy-log.md").write_text("# Deploy Log\n\nprose only, no rows\n",
                                              encoding="utf-8")
            m = deploy.metrics(root)
            self.assertTrue(m["applicable"])
            self.assertIn("unmeasurable", m["change_failure_rate"])

    def test_mttr_refused_without_resolved_high_bugs(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ledger(root, LEDGER_ROWS)
            m = deploy.metrics(root)
            self.assertIn("unmeasurable", m["mttr_days"])
            self.assertIn("High", m["mttr_days"]["unmeasurable"])


class DoraNotApplicableTests(unittest.TestCase):
    def test_no_ledger_is_cleanly_not_applicable(self):
        with tempfile.TemporaryDirectory() as d:
            m = deploy.metrics(Path(d))
            self.assertFalse(m["applicable"])

    def test_cli_not_applicable_exits_zero_without_nagging(self):
        import argparse
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            ns = argparse.Namespace(root=str(d), format="text")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = deploy.cmd_metrics(ns)
            self.assertEqual(rc, 0)
            self.assertIn("not applicable", buf.getvalue().lower())
            self.assertNotIn("adopt", buf.getvalue().lower())


if __name__ == "__main__":
    unittest.main()
