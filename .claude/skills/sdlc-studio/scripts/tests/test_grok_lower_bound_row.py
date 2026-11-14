"""BG1391: the report's Dollar cost row labels a Grok figure a lower bound whenever any part of
it was priced from a session total, even where that total is summed with a split booked request
by request, which names the long-context id and so reads as exact on its own.

Two sums hid the label: the report adding a delegated agent's Grok session total to the meter's
booked split (`sprint_report._run_usd`), and the run total summing a booked session with a
session read as a total (`run_state._priced_delta`). Each case drives the shipped functions over
readings typed here, with prices typed here: grok-4.7 short 2.00 input, 6.00 output, 0.50 cache
read, long 4.00, 12.00, 1.00 from a 200,000-token prompt. The expected dollars are formed here
from those typed prices, never from the code under test.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import prices, run_state  # noqa: E402
import sprint_report  # noqa: E402

GROK, LONG_ID, OPUS = "grok-4.7", "grok-4.7" + prices.LONG_CONTEXT_ID, "claude-opus-5-5"
SHORT = {"input": 2.0, "output": 6.0, "cache_read": 0.5, "cache_write_5m": 2.0,
         "cache_write_1h": 2.0}
LONG = {"input": 4.0, "output": 12.0, "cache_read": 1.0, "cache_write_5m": 4.0,
        "cache_write_1h": 4.0}
OPUS_PRICE = {"input": 5.0, "output": 25.0, "cache_read": 0.5, "cache_write_5m": 6.25,
              "cache_write_1h": 10.0}
LABEL = f"a lower bound for {GROK}"


def comps(inp: int = 0, out: int = 0, read: int = 0) -> dict:
    return {"input": inp, "output": out, "cache_write_5m": 0, "cache_write_1h": 0,
            "cache_read": read}


def dollars(rate: dict, c: dict) -> float:
    return sum(c[k] * rate[k] for k in c) / 1e6


#: A Cursor session booked request by request: short requests under the base id, one long one
#: under the long-context id.
BOOKED_SHORT, BOOKED_LONG = comps(10_000, 2_000, 50_000), comps(250_000, 4_000, 0)
#: A Grok session read as one total: no request can be told from another.
TOTAL = comps(300_000, 8_000, 100_000)


def reading(split: dict, tokens: int) -> dict:
    whole = comps()
    for c in split.values():
        for k in whole:
            whole[k] += c[k]
    return {"tokens": tokens, "components": whole, run_state.BY_MODEL: split,
            "subagents": True}


def booked_session() -> list[dict]:
    return [reading({GROK: comps(), LONG_ID: comps()}, 1),
            reading({GROK: BOOKED_SHORT, LONG_ID: BOOKED_LONG}, 2)]


def total_session() -> list[dict]:
    return [reading({GROK: comps()}, 1), reading({GROK: TOTAL}, 2)]


class GrokLowerBoundRowTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        typed = {"effective": dt.date.today().isoformat(), "source": "typed in the test"}
        path = Path(tmp.name) / "prices.json"
        path.write_text(json.dumps({"models": [
            {"model": OPUS, **OPUS_PRICE, **typed},
            {"model": GROK, **SHORT, **typed,
             "long_context": {**LONG, "from_prompt_tokens": 200_000, **typed}}]}),
            encoding="utf-8")
        self.usd = {"table": prices.load(path=path, pricing={}), "error": None,
                    "today": dt.date.today()}

    def row(self, run_tokens: dict, delegated: dict | None) -> dict:
        rows = sprint_report._usd_rows(run_tokens, [{"points": 2}], "state", self.usd,
                                       delegated)
        return {r["est_measure"]["value"]: r for r in rows}

    def delegated(self, *splits: dict) -> dict:
        state = {run_state.DELEGATED: [{"tokens": 1, "agent": f"a{i}", "unit": "US0001",
                                        run_state.BY_MODEL: s} for i, s in enumerate(splits)]}
        return run_state.delegated_split(state)

    def test_a_delegated_session_total_merged_into_a_booked_split_is_labelled(self) -> None:
        """MUTANTS: `_run_usd` dropping the delegated split's from-total models, or `usd`
        ignoring them, so the merged split names the long-context id and reads as exact."""
        run_tokens = run_state._priced_delta([booked_session()])
        rows = self.row(run_tokens, self.delegated({GROK: TOTAL}))
        basis = rows["Dollar cost"]["est_basis"]["value"]
        self.assertIn(f"{LABEL}: its provider bills a request whose prompt is 200,000 tokens "
                      f"or more", basis)
        self.assertIn("a lower bound, as the Dollar cost row says",
                      rows["Dollars per point"]["est_basis"]["value"])
        whole = (dollars(SHORT, BOOKED_SHORT) + dollars(LONG, BOOKED_LONG)
                 + dollars(SHORT, TOTAL))
        self.assertEqual(sprint_report._usd_text(whole),
                         rows["Dollar cost"]["est_actual"]["value"])

    def test_a_booked_delegated_split_stays_exact(self) -> None:
        """The positive control: every part booked request by request, so no label."""
        run_tokens = run_state._priced_delta([booked_session()])
        rows = self.row(run_tokens, self.delegated({GROK: BOOKED_SHORT, LONG_ID: BOOKED_LONG}))
        self.assertNotIn(LABEL, rows["Dollar cost"]["est_basis"]["value"])
        self.assertNotIn("a lower bound", rows["Dollars per point"]["est_basis"]["value"])

    def test_a_booked_and_a_total_delegated_record_sum_labelled(self) -> None:
        """MUTANT: `delegated_split` reading from-total models off its summed split, where the
        booked record's long-context id hides the total beside it."""
        run_tokens = run_state._priced_delta([booked_session()])
        rows = self.row(run_tokens, self.delegated({GROK: BOOKED_SHORT, LONG_ID: BOOKED_LONG},
                                                   {GROK: TOTAL}))
        self.assertIn(LABEL, rows["Dollar cost"]["est_basis"]["value"])

    def test_a_run_total_over_a_booked_and_a_total_session_is_labelled(self) -> None:
        """MUTANTS: `_priced_delta` or `_split_delta` losing which session was a total, so the
        run-level sum names the long-context id and reads as exact."""
        run_tokens = run_state._priced_delta([booked_session(), total_session()])
        self.assertEqual([GROK], run_tokens[run_state.FROM_TOTAL])
        rows = self.row(run_tokens, None)
        self.assertIn(LABEL, rows["Dollar cost"]["est_basis"]["value"])
        whole = (dollars(SHORT, BOOKED_SHORT) + dollars(LONG, BOOKED_LONG)
                 + dollars(SHORT, TOTAL))
        self.assertEqual(sprint_report._usd_text(whole),
                         rows["Dollar cost"]["est_actual"]["value"])

    def test_a_run_total_over_booked_sessions_stays_exact(self) -> None:
        """The positive control: two booked sessions sum to an exact figure."""
        run_tokens = run_state._priced_delta([booked_session(), booked_session()])
        self.assertEqual([], run_tokens[run_state.FROM_TOTAL])
        self.assertNotIn(LABEL, self.row(run_tokens, None)["Dollar cost"]["est_basis"]["value"])

    def test_a_model_with_no_priced_tokens_is_no_total(self) -> None:
        """MUTANT: `from_total` naming a model a split holds at zero, as a session that never
        used it does, so the run total says it read a total it never read."""
        self.assertEqual(set(), run_state.from_total({GROK: comps(), OPUS: comps()}))
        self.assertEqual({OPUS}, run_state.from_total({GROK: comps(), OPUS: comps(1)}))

    def test_a_session_booked_whole_under_its_model_is_a_total(self) -> None:
        """MUTANT: `_split_delta`'s fallback, which books a session with no split under the one
        model its readings name, left out of the from-total models."""
        bare = [{"tokens": 1, "components": comps(), "model": GROK, "subagents": True},
                {"tokens": 2, "components": TOTAL, "model": GROK, "subagents": True}]
        run_tokens = run_state._priced_delta([booked_session(), bare])
        self.assertEqual([GROK], run_tokens[run_state.FROM_TOTAL])
        self.assertIn(LABEL, self.row(run_tokens, None)["Dollar cost"]["est_basis"]["value"])

    def test_a_run_total_without_the_field_keeps_the_split_s_own_rule(self) -> None:
        """A run total formed before the field (no `FROM_TOTAL`) is read as it was: its own
        split's from-total models, with the delegated ones added. MUTANT: the fallback reading
        an absent field as no model at all, so a meter split of a Grok total merged with a
        booked delegated split reads as exact."""
        run_tokens = {run_state.BY_MODEL: {GROK: TOTAL}}
        rows = self.row(run_tokens, self.delegated({GROK: BOOKED_SHORT, LONG_ID: BOOKED_LONG}))
        self.assertIn(LABEL, rows["Dollar cost"]["est_basis"]["value"])


if __name__ == "__main__":
    unittest.main()
