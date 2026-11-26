"""`sprint plan` stamps the spend appetite on the run; raising it mid-run names a decision.

The plan resolves the spend appetite once with minutes and units and `--write` stamps it beside
its standing value, so `loop_guard budget` judges the number the plan was sized against whatever
`.config.yaml` says later. `sprint appetite resize --spend N` raises it only with `--decision`
naming a row `decisions.md` records. Each test runs the shipped `sprint.py` entry point.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

import loop_guard  # noqa: E402
import sprint  # noqa: E402
from lib import run_state  # noqa: E402

AC = ("\n## Acceptance Criteria\n\n### AC1: it behaves as recorded\n\n"
      "- **Given** the recorded state\n- **Verify:** shell true\n")
DECISIONS = ("# Decisions\n\n| ID | Decision | Why | Status | Supersedes | Date |\n"
             "| --- | --- | --- | --- | --- | --- |\n"
             "| D0001 | Raise the spend ceiling | the epic grew | accepted | -- | 2026-11-26 |\n"
             "| D0003 | Not D0002, which is only mentioned | x | accepted | -- | 2026-11-26 |\n")
LABEL = run_state.PRICED_LABEL


class AppetiteSpendTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        empty = self.tmp / "no-transcripts"
        empty.mkdir()
        env = mock.patch.dict(os.environ, {run_state.TRANSCRIPTS_ENV: str(empty)})
        env.start()
        self.addCleanup(env.stop)

    # -- fixture -------------------------------------------------------------------------

    def _project(self, name: str, config: str) -> Path:
        root = self.tmp / name
        stories = root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        for n in (1, 2):
            (root / "src").mkdir(exist_ok=True)
            (root / "src" / f"u{n}.py").write_text("", encoding="utf-8")
            (stories / f"US000{n}-x.md").write_text(
                f"# US000{n}: s\n\n> **Status:** Ready\n> **Affects:** src/u{n}.py\n"
                f"> **Points:** 1\n{AC}", encoding="utf-8")
        self._config(root, config)
        return root

    def _config(self, root: Path, text: str) -> None:
        (root / "sdlc-studio" / ".config.yaml").write_text(text, encoding="utf-8")

    def _run_open(self, appetite: dict) -> Path:
        root = self.tmp / "run"
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        (root / "sdlc-studio" / "decisions.md").write_text(DECISIONS, encoding="utf-8")
        run_state.path(root).write_text(json.dumps(
            {"run_id": "RUN-T", "batch": ["US0001"], "outcome": "running",
             "appetite": appetite}), encoding="utf-8")
        return root

    def _sprint(self, root: Path, *argv: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = sprint.main([*argv, "--root", str(root)])
        return rc, out.getvalue()

    def _plan(self, root: Path, *extra: str) -> tuple[int, str]:
        return self._sprint(root, "plan", "--stories", "Ready", "--skip-personas", "--no-fetch",
                            "--write", *extra)

    def _resize(self, root: Path, *argv: str) -> tuple[int, str]:
        return self._sprint(root, "appetite", "resize", *argv)

    def _appetite(self, root: Path) -> dict:
        return run_state.read(root)["appetite"]

    # -- AC1 -----------------------------------------------------------------------------

    def test_the_plan_stamps_the_spend_appetite_it_resolved(self) -> None:
        """AC1. MUTANTS: the plan stamping no spend, or the standing one in its place; the
        flag not reaching the resolution; the capacity line naming no spend or no source; the
        breaker re-reading config over the stamp."""
        root = self._project("a", "capacity:\n  spend: 1000\n")
        rc, out = self._plan(root)
        self.assertEqual(0, rc, out)
        ap = self._appetite(root)
        self.assertEqual((1000, 1000, False), (ap["spend"], ap["standing_spend"], ap["over_spend"]))
        self.assertIn("the run BREAKER is wall-clock/unit-count/spend", out)
        self.assertIn(f"spend 1,000 {LABEL} (config capacity.spend)", out)
        self._config(root, "capacity:\n  spend: 5\n")
        with contextlib.redirect_stdout(io.StringIO()) as got:
            rc = loop_guard.main(["budget", "--root", str(root), "--format", "json"])
        self.assertEqual(1000, json.loads(got.getvalue())["appetite_spend"])
        fresh = self._project("b", "capacity:\n  spend: 1000\n")
        rc, out = self._plan(fresh, "--appetite-spend", "400")
        self.assertEqual(0, rc, out)
        ap = self._appetite(fresh)
        self.assertEqual((400, 1000, False), (ap["spend"], ap["standing_spend"], ap["over_spend"]))
        self.assertIn(f"spend 400 {LABEL} (--appetite-spend)", out)

    def test_the_plan_resolves_appetite_spend_over_capacity_and_ships_unbounded(self) -> None:
        """MUTANTS: `appetite.spend` skipped for `capacity.spend`; a shipped default other
        than 0; an unbounded spend printed as a number."""
        root = self._project("a", "capacity:\n  spend: 1000\nappetite:\n  spend: 700\n")
        rc, out = self._plan(root)
        self.assertEqual(0, rc, out)
        self.assertEqual((700, 1000), (self._appetite(root)["spend"],
                                       self._appetite(root)["standing_spend"]))
        self.assertIn("(config appetite.spend)", out)
        bare = self._project("b", "{}\n")
        rc, out = self._plan(bare)
        self.assertEqual(0, rc, out)
        self.assertEqual((0, 0, False), (self._appetite(bare)["spend"],
                                         self._appetite(bare)["standing_spend"],
                                         self._appetite(bare)["over_spend"]))
        self.assertIn("spend unbounded (config capacity.spend)", out)

    # -- AC2 -----------------------------------------------------------------------------

    def test_a_spend_raise_needs_a_recorded_decision(self) -> None:
        """AC2. MUTANTS: a raise accepted with no decision, or with one decisions.md only
        mentions; the refusal writing the run state; the change entry's spend or decision
        dropped; the overage not reported; a lowering asked for a decision."""
        root = self._run_open({"units": 9, "minutes": 0.0, "standing_units": 9,
                               "standing_minutes": 0.0, "over_appetite": False, "spend": 1000})
        before = run_state.path(root).read_bytes()
        rc, out = self._resize(root, "--spend", "1500", "--reason", "r")
        self.assertEqual(2, rc, out)
        self.assertIn("--decision", out)
        self.assertEqual(before, run_state.path(root).read_bytes())
        rc, out = self._resize(root, "--spend", "1500", "--reason", "r", "--decision", "D0002")
        self.assertEqual(2, rc, out)
        self.assertIn("D0002", out)
        self.assertIn("decisions.md", out)
        self.assertEqual(before, run_state.path(root).read_bytes())
        rc, out = self._resize(root, "--spend", "1500", "--reason", "r", "--decision", "D0001")
        self.assertEqual(0, rc, out)
        state = run_state.read(root)
        self.assertEqual(1500, state["appetite"]["spend"])
        entry = state["appetite_changes"][-1]
        self.assertEqual((1000, 1500), (entry["from"]["spend"], entry["to"]["spend"]))
        self.assertEqual("D0001", entry["decision"])
        self.assertIn(f"OVER APPETITE - this batch was allowed spend 1,500 {LABEL} against a "
                      f"standing 1,000", out)
        self.assertIn("spend 1,500 (standing 1,000; 0 is unbounded).", out)
        rc, out = self._resize(root, "--spend", "800", "--reason", "r")
        self.assertEqual(0, rc, out)
        self.assertNotIn("OVER APPETITE", out, "800 is under the standing 1,000")
        state = run_state.read(root)
        self.assertEqual(800, state["appetite"]["spend"])
        entry = state["appetite_changes"][-1]
        self.assertEqual(("r", 1500, 800), (entry["reason"], entry["from"]["spend"],
                                            entry["to"]["spend"]))
        self.assertNotIn("decision", entry)

    def test_lifting_a_ceiling_is_a_raise_and_setting_one_is_not(self) -> None:
        """MUTANTS: 0 (unbounded) compared as a number, so lifting the ceiling to 0 passes with
        no decision, or setting one on an unbounded run is refused."""
        root = self._run_open({"units": 9, "minutes": 0.0, "spend": 1000,
                               "standing_spend": 1000})
        rc, out = self._resize(root, "--spend", "0", "--reason", "r")
        self.assertEqual(2, rc, out)
        rc, out = self._resize(root, "--spend", "0", "--reason", "r", "--decision", "D0001")
        self.assertEqual(0, rc, out)
        self.assertTrue(self._appetite(root)["over_spend"], "an unbounded spend is over 1,000")
        self.assertIn("allowed an unbounded spend against a standing 1,000", out)
        rc, out = self._resize(root, "--spend", "600", "--reason", "r")
        self.assertEqual(0, rc, out)
        self.assertEqual(600, self._appetite(root)["spend"])

    def test_a_run_that_recorded_no_spend_measures_a_raise_against_the_config(self) -> None:
        """MUTANT: a run opened before the spend key read as unbounded, so a raise past the
        configured ceiling needs no decision."""
        root = self._run_open({"units": 9, "minutes": 0.0})
        self._config(root, "capacity:\n  spend: 1000\n")
        rc, out = self._resize(root, "--spend", "1500", "--reason", "r")
        self.assertEqual(2, rc, out)
        rc, out = self._resize(root, "--spend", "900", "--reason", "r")
        self.assertEqual(0, rc, out)
        entry = run_state.read(root)["appetite_changes"][-1]
        self.assertEqual((1000, 900), (entry["from"]["spend"], entry["to"]["spend"]))

    def test_a_named_decision_must_be_recorded_even_on_a_lowering(self) -> None:
        """MUTANT: an unrecorded decision id written to the ledger on a resize that needed
        none."""
        root = self._run_open({"units": 9, "minutes": 0.0, "spend": 1000})
        rc, out = self._resize(root, "--units", "3", "--reason", "r", "--decision", "D0002")
        self.assertEqual(2, rc, out)
        rc, out = self._resize(root, "--units", "3", "--reason", "r", "--decision", "D0001")
        self.assertEqual(0, rc, out)
        self.assertEqual("D0001", run_state.read(root)["appetite_changes"][-1]["decision"])

    # -- AC3 -----------------------------------------------------------------------------

    def test_a_units_resize_keeps_the_spend_appetite(self) -> None:
        """AC3. MUTANTS: a units or minutes resize rebuilding the appetite from those two
        alone; the change entry's spend left out or moved."""
        root = self._run_open({"units": 8, "minutes": 60.0, "standing_units": 8,
                               "standing_minutes": 60.0, "over_appetite": False,
                               "spend": 1000, "standing_spend": 1000})
        rc, out = self._resize(root, "--units", "9", "--reason", "r")
        self.assertEqual(0, rc, out)
        ap = self._appetite(root)
        self.assertEqual((9, 1000, 1000), (ap["units"], ap["spend"], ap["standing_spend"]))
        entry = run_state.read(root)["appetite_changes"][-1]
        self.assertEqual((1000, 1000), (entry["from"]["spend"], entry["to"]["spend"]))
        rc, out = self._resize(root, "--minutes", "90", "--reason", "r")
        self.assertEqual(0, rc, out)
        ap = self._appetite(root)
        self.assertEqual((90.0, 1000, 1000), (ap["minutes"], ap["spend"], ap["standing_spend"]))

    def test_a_resize_keeps_a_standing_spend_apart_from_the_accepted_one(self) -> None:
        """MUTANT: the standing spend rebuilt from the accepted one on a units resize."""
        root = self._run_open({"units": 8, "minutes": 0.0, "spend": 1500,
                               "standing_spend": 1000})
        rc, out = self._resize(root, "--units", "9", "--reason", "r")
        self.assertEqual(0, rc, out)
        ap = self._appetite(root)
        self.assertEqual((1500, 1000, True), (ap["spend"], ap["standing_spend"], ap["over_spend"]))

    def test_a_recorded_unbounded_spend_is_kept_and_not_read_from_config(self) -> None:
        """MUTANT: a recorded spend of 0 read as no spend, so a units resize drops it and a
        first ceiling is measured against the config's as a raise."""
        root = self._run_open({"units": 8, "minutes": 0.0, "spend": 0, "standing_spend": 0})
        self._config(root, "capacity:\n  spend: 1000\n")
        rc, out = self._resize(root, "--units", "9", "--reason", "r")
        self.assertEqual(0, rc, out)
        self.assertEqual(0, self._appetite(root)["spend"])
        rc, out = self._resize(root, "--spend", "1500", "--reason", "r")
        self.assertEqual(0, rc, out)
        self.assertEqual(1500, self._appetite(root)["spend"])

    def test_a_run_with_no_spend_keeps_its_old_shape_on_a_units_resize(self) -> None:
        """MUTANT: a spend invented on a run that recorded none."""
        root = self._run_open({"units": 8, "minutes": 0.0})
        rc, out = self._resize(root, "--units", "9", "--reason", "r")
        self.assertEqual(0, rc, out)
        self.assertNotIn("spend", self._appetite(root))
        self.assertNotIn("spend", run_state.read(root)["appetite_changes"][-1]["to"])
        self.assertNotIn("spend", out)


if __name__ == "__main__":
    unittest.main()
