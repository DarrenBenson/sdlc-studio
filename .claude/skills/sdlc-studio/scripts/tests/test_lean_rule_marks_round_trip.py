"""BG0919: each page-format rule mark round-trips through filing and revalidation.

BG0898 (minutes like-for-like), BG0901 (partial agent minutes) and BG0904 (cancelled-run DORA)
each added an envelope mark, so a page filed before the rule re-derives as it was signed and a
page filed under it re-derives under it. Nothing filed such a page and revalidated it: dropping
a mark from the envelope, or hard-wiring the rule on in `revalidate`, passed every test while
the page it filed re-derived INVALIDATED.

Each rule's page is derived on that rule's own fixture, borrowed from its test module, filed
through `sprint_report.file_report` and judged by `sprint_report.revalidate`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import contextlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_dora_cancelled_runs as cancelled  # noqa: E402 - BG0904's fixture
import test_lean_report_minutes_like_for_like as like  # noqa: E402 - BG0898's fixture
import test_lean_report_partial_agent_minutes as partial  # noqa: E402 - BG0901's fixture

sr = like.sr


@contextlib.contextmanager
def _borrowed(case: type[unittest.TestCase]):
    """`case`'s fixture, set up on an instance of its own and torn down on leaving."""
    inst = case()
    inst.setUp()
    try:
        yield inst
    finally:
        inst.doCleanups()


@contextlib.contextmanager
def _minutes():
    """BG0898: 120 measured minutes against a 600-minute span."""
    with _borrowed(like.MinutesLikeForLikeTests) as t:
        yield t.root, like.lean.RETRO


@contextlib.contextmanager
def _agent_minutes():
    """BG0901: a builder's 40 agent minutes beside a reviewer's total that gave none."""
    with _borrowed(partial.PartialAgentMinutesTests) as t:
        t.ws.deliver("US0101", "--tokens", "250000", "--minutes", "40", minutes=7)
        partial.lane._live("lib.run_state").record_delegated_tokens(
            t.ws.root, 50_000, agent="reviewer", unit="US0101")
        yield t.ws.root, partial.lane.RETRO


@contextlib.contextmanager
def _cancelled():
    """BG0904: a cancelled run on main between two successes."""
    with tempfile.TemporaryDirectory() as d:
        root, run = Path(d), cancelled._run
        cancelled.dora.lean._fixture(root, ended_at="2026-09-24T00:00:00Z", ci_runs={
            "source": "gh run list", "runs": [run(3, "14:00", "success"),
                                              run(2, "13:00", "cancelled"),
                                              run(1, "12:00", "success")]})
        yield root, cancelled.dora.RETRO


RULES = (("minutes like-for-like", sr.MINUTES_RULE, "minutes_rule", _minutes),
         ("partial agent minutes", sr.AGENT_MINUTES_RULE, "agent_minutes_rule", _agent_minutes),
         ("cancelled-run DORA", sr.CANCELLED_RULE, "cancelled_rule", _cancelled))


class RuleMarksRoundTripTests(unittest.TestCase):
    def _check(self, root: Path, page: dict) -> dict:
        return sr.revalidate(root, sr.file_report(root, page))

    def test_each_rule_mark_round_trips(self) -> None:
        """AC1. MUTANTS: drop any one rule's mark from the envelope (`build_report`), so a page
        filed under the rule re-derives with it off and reads INVALIDATED; hard-wire the rule on
        in `revalidate`, so a page filed before it re-derives under it. The control: the same
        page with its mark removed by hand reads INVALIDATED, so the rule moves a figure on
        each fixture and the VALID beside it is not vacuous."""
        for name, mark, flag, fixture in RULES:
            with self.subTest(rule=name), fixture() as (root, retro):
                page = sr.build_report(root, retro)
                self.assertIn(mark, page, "premise: the page carries the mark")
                check = self._check(root, page)
                self.assertTrue(check["valid"], check["changes"])
                before = sr.build_report(root, retro, **{flag: False})
                self.assertNotIn(mark, before)
                check = self._check(root, before)
                self.assertTrue(check["valid"], check["changes"])
                dropped = {k: v for k, v in page.items() if k not in (mark, "fingerprint")}
                check = self._check(root, dropped)
                self.assertFalse(check["valid"], "the rule moves no figure on this fixture")
                self.assertTrue(check["changes"], check)
                self.assertEqual([], check["edited"], "INVALIDATED, not an edited page")


if __name__ == "__main__":
    unittest.main()
