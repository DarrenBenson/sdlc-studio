"""BG1393: a project whose `pricing.models` replaces grok-4.7 whole, with no long-context price,
still has every token of a Cursor ledger priced. The ledger books each long response under
grok-4.7's long-context id by the shipped table (`meter_cursor.read_ledger` through
`token_meters.book`), and the project's table no longer lists that id, so `run_state.usd`
priced the short responses alone and listed the long ones as not priced.

The split is booked here by `token_meters.book` over the shipped fixture table, as the ledger
reader books it; prices are typed here and the expected dollars formed from them, never from
the code under test.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import prices, run_state, token_meters  # noqa: E402

GROK = "grok-4.7"
LONG_ID = GROK + prices.LONG_CONTEXT_ID
SHIPPED_SHORT = {"input": 2.0, "output": 6.0, "cache_read": 0.5, "cache_write_5m": 2.0,
                 "cache_write_1h": 2.0}
SHIPPED_LONG = {"input": 4.0, "output": 12.0, "cache_read": 1.0, "cache_write_5m": 4.0,
                "cache_write_1h": 4.0}
#: The project's own grok-4.7 rates, differing from both shipped ones in every component.
PROJECT = {"input": 3.0, "output": 9.0, "cache_read": 0.75, "cache_write_5m": 3.0,
           "cache_write_1h": 3.0}
PROJECT_LONG = {"input": 7.0, "output": 21.0, "cache_read": 1.75, "cache_write_5m": 7.0,
                "cache_write_1h": 7.0}
TYPED = {"effective": dt.date.today().isoformat(), "source": "typed in the test"}


def comps(inp: int, out: int) -> dict:
    return {"input": inp, "output": out, "cache_write_5m": 0, "cache_write_1h": 0,
            "cache_read": 0}


SHORT_REQ, LONG_REQ = comps(10_000, 2_000), comps(250_000, 4_000)


def dollars(rate: dict, *parts: dict) -> float:
    return sum(p[k] * rate[k] for p in parts for k in p) / 1e6


class ReplacedGrokLongContextTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "prices.json"
        self.path.write_text(json.dumps({"models": [
            {"model": GROK, **SHIPPED_SHORT, **TYPED,
             "long_context": {**SHIPPED_LONG, "from_prompt_tokens": 200_000, **TYPED}}]}),
            encoding="utf-8")
        shipped = prices.load(path=self.path, pricing={})
        self.split = token_meters.book([{"model": GROK, "components": SHORT_REQ},
                                        {"model": GROK, "components": LONG_REQ}], shipped)
        self.assertIn(LONG_ID, self.split, "premise: the ledger books the long response apart")

    def project(self, entry: dict):
        return prices.load(path=self.path, pricing={"models": {GROK: entry}})

    def test_a_replaced_entry_prices_the_whole_reading_at_its_one_rate(self) -> None:
        """MUTANTS: `usd` pricing the long-context id the project's table no longer lists, so it
        is listed not priced and the figure covers part of the reading; the folded tokens
        priced at the shipped long rate the project replaced."""
        table = self.project({**PROJECT, **TYPED})
        self.assertNotIn(LONG_ID, table.models, "premise: the replaced entry drops its long rate")
        got = run_state.usd(self.split, table)
        self.assertEqual([], got["unpriced"])
        self.assertEqual(1.0, got["covered"])
        self.assertAlmostEqual(dollars(PROJECT, SHORT_REQ, LONG_REQ), got["usd"], places=9)
        self.assertEqual([GROK], [m["model"] for m in got["models"]])
        self.assertIsNone(got["lower_bound"], "the project's entry bills one rate")

    def test_a_replaced_entry_with_its_own_long_rate_prices_each_at_its_rate(self) -> None:
        """The positive control: a project entry carrying a long-context price keeps the long
        responses at that price. MUTANT: the fold taking an id the table still lists."""
        table = self.project({**PROJECT, **TYPED, "long_context": {
            **PROJECT_LONG, "from_prompt_tokens": 200_000, **TYPED}})
        got = run_state.usd(self.split, table)
        self.assertEqual([], got["unpriced"])
        self.assertAlmostEqual(dollars(PROJECT, SHORT_REQ) + dollars(PROJECT_LONG, LONG_REQ),
                               got["usd"], places=9)
        self.assertEqual([GROK, LONG_ID], [m["model"] for m in got["models"]])

    def test_a_long_context_id_whose_base_no_table_prices_is_named_unpriced(self) -> None:
        """A long-context id whose base the table does not list either is said plainly to be
        unpriced, under its own id, never priced at a guess."""
        split = {"grok-9" + prices.LONG_CONTEXT_ID: LONG_REQ, GROK: SHORT_REQ}
        got = run_state.usd(split, self.project({**PROJECT, **TYPED}))
        self.assertEqual(["grok-9" + prices.LONG_CONTEXT_ID],
                         [u["model"] for u in got["unpriced"]])
        self.assertAlmostEqual(dollars(PROJECT, SHORT_REQ), got["usd"], places=9)


if __name__ == "__main__":
    unittest.main()
