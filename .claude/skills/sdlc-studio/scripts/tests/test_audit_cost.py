"""Tests for the audit cost estimator (audit_cost.py) - CR0276 / US0159.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCRIPTS))
_spec = importlib.util.spec_from_file_location("audit_cost", _SCRIPTS / "audit_cost.py")
audit_cost = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit_cost)


class EstimateTests(unittest.TestCase):
    def test_reference_run_is_in_the_right_ballpark(self) -> None:
        # measured reference: 7 lenses -> 192 agents, ~6.9M tokens, ~29 min. The estimate is
        # order-of-magnitude; assert it lands within a sane band, not on the nose.
        est = audit_cost.estimate(7)
        self.assertTrue(150 <= est["agents"] <= 230)
        self.assertTrue(5_000_000 <= est["tokens"] <= 9_000_000)
        self.assertTrue(20 <= est["wall_minutes"] <= 50)
        self.assertTrue(est["large"])

    def test_small_scoped_audit_is_not_large(self) -> None:
        est = audit_cost.estimate(2, rounds=1, candidates_per_lens=3)
        self.assertFalse(est["large"])
        self.assertLess(est["agents"], audit_cost.LARGE_AGENTS)

    def test_single_lens_at_defaults_is_not_large(self) -> None:
        # the "no ceremony" path the docs promise: one lens at the default knobs must be small
        est = audit_cost.estimate(1)
        self.assertFalse(est["large"])

    def test_breakdown_adds_up(self) -> None:
        est = audit_cost.estimate(5, rounds=2, votes=3, candidates_per_lens=4)
        b = est["breakdown"]
        self.assertEqual(b["finders"], 5 * 2)
        self.assertEqual(b["candidates_est"], 5 * 4)
        self.assertEqual(b["refuters"], 5 * 4 * 3)
        self.assertEqual(est["agents"], b["finders"] + b["refuters"] + b["merge"])
        self.assertEqual(est["tokens"], est["agents"] * audit_cost.TOKENS_PER_AGENT)

    def test_zero_lenses_is_zero(self) -> None:
        est = audit_cost.estimate(0)
        self.assertEqual(est["agents"], 0)
        self.assertFalse(est["large"])

    def test_large_threshold_on_tokens_alone(self) -> None:
        # even a modest agent count crosses "large" if the token budget does
        est = audit_cost.estimate(3, candidates_per_lens=10, tokens_per_agent=60_000)
        self.assertTrue(est["tokens"] >= audit_cost.LARGE_TOKENS)
        self.assertTrue(est["large"])

    def test_cli_json(self) -> None:
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = audit_cost.main(["--lenses", "7", "--format", "json"])
        import json
        self.assertEqual(rc, 0)
        self.assertIn("agents", json.loads(buf.getvalue()))


if __name__ == "__main__":
    unittest.main()
