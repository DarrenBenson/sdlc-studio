"""`loop_guard budget` stops a run on spend as well as on minutes and units.

Spend is the run's priced input-equivalent tokens, read as a first close reads it: a meter
reading taken now and held beside the run's stamps, never written. Each test drives the shipped
`loop_guard.py budget` entry point over a fixture run whose session transcript
`SDLC_STUDIO_TRANSCRIPTS` names, so the opening stamp `open_run` takes and the reading the
breaker takes are two readings of one meter.
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

import yaml

SCRIPTS = Path(__file__).resolve().parent.parent
SKILL = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

import loop_guard  # noqa: E402
from lib import run_state  # noqa: E402

STORY = "# US0001: a unit in flight\n\n> **Status:** In Progress\n> **Points:** 1\n"


class LoopGuardSpendTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "proj"
        (self.root / "sdlc-studio" / "stories").mkdir(parents=True)
        self.story = self.root / "sdlc-studio" / "stories" / "US0001-a-unit-in-flight.md"
        self.story.write_text(STORY, encoding="utf-8")
        self.tx = Path(tmp.name) / "transcripts"
        self.tx.mkdir()
        env = mock.patch.dict(os.environ, {run_state.TRANSCRIPTS_ENV: str(self.tx)})
        env.start()
        self.addCleanup(env.stop)

    # -- fixture -------------------------------------------------------------------------

    def _use(self, tokens: int) -> None:
        """Append one message of `tokens` input tokens, which price at `tokens` (weight 1)."""
        with (self.tx / "s1.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"message": {"model": "m9",
                                             "usage": {"input_tokens": tokens}}}) + "\n")

    def _open(self, appetite: dict, opening: int | None = 1000) -> None:
        """Open the run, its open stamp read from the transcript when `opening` is a count."""
        if opening is not None:
            self._use(opening)
        run_state.open_run(str(self.root), batch=["US0001"], goal="g")
        run_state.update(str(self.root), appetite=appetite)

    def _budget(self, *extra: str, fmt: str = "json") -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            rc = loop_guard.main(["budget", "--root", str(self.root), "--format", fmt, *extra])
        return rc, out.getvalue()

    def _verdict(self, *extra: str) -> tuple[int, dict]:
        rc, out = self._budget(*extra)
        return rc, json.loads(out)

    def _config(self, text: str) -> None:
        (self.root / "sdlc-studio" / ".config.yaml").write_text(text, encoding="utf-8")

    # -- AC1 -----------------------------------------------------------------------------

    def test_spend_at_the_appetite_stops_the_run_and_marks_nothing(self) -> None:
        """AC1. MUTANTS: `>=` made `>` on the spend axis (exact spend continues); the spend
        axis dropped from `reason`; the reading written to the run state; the stop's text
        naming no spend."""
        n = 4000
        self._open({"minutes": 0, "units": 0, "spend": n})
        self._use(n - 1)
        state_before = run_state.path(self.root).read_bytes()
        rc, v = self._verdict()
        self.assertEqual(0, rc, v)
        self.assertFalse(v["exhausted"])
        self.assertEqual("", v["reason"])
        self.assertEqual(n - 1, v["spend"])
        self._use(1)
        rc, v = self._verdict()
        self.assertEqual(loop_guard.BUDGET_EXIT, rc, v)
        self.assertEqual(4, rc)
        self.assertTrue(v["exhausted"])
        self.assertEqual("spend", v["reason"])
        self.assertEqual(n, v["spend"])
        self.assertEqual(n, v["appetite_spend"])
        self.assertIsNone(v["spend_unread"])
        rc, text = self._budget(fmt="text")
        self.assertEqual(4, rc, text)
        self.assertIn("appetite SPENT (reason=spend)", text)
        self.assertIn(f"spend {n:,}/{n:,} {run_state.PRICED_LABEL}", text)
        self.assertIn("units already dispatched finish and no further unit starts", text)
        self.assertFalse([ln for ln in text.splitlines() if ln.startswith("WARNING")],
                         "a stop is not also a warning")
        # Marks nothing: no unit's Status moves and the reading is held, never written.
        self.assertEqual(STORY, self.story.read_text(encoding="utf-8"))
        self.assertEqual(state_before, run_state.path(self.root).read_bytes())

    def test_a_minutes_and_spend_stop_names_both_axes(self) -> None:
        """MUTANT: the spend axis judged only when minutes and units are not spent."""
        self._open({"minutes": 1, "units": 0, "spend": 100})
        run_state.update(str(self.root), started_at="2026-01-01T00:00:00Z")
        self._use(100)
        rc, v = self._verdict()
        self.assertEqual(4, rc)
        self.assertEqual("minutes+spend", v["reason"])

    def test_a_spend_with_no_appetite_fires_nothing_in_the_pure_verdict(self) -> None:
        """MUTANT: the spend axis judged against an appetite of 0, which is unbounded."""
        v = loop_guard.budget_verdict(0, 0, 0.0, 0, appetite_spend=0, spend=5)
        self.assertEqual((False, "", None), (v["exhausted"], v["reason"], v["spend_warning"]))

    def test_the_reading_leaves_the_state_it_was_given_as_it_was(self) -> None:
        """MUTANT: the probe stamp appended to the caller's own state."""
        self._open({"minutes": 0, "units": 0, "spend": 10})
        self._use(5)
        state = run_state.read(self.root)
        stamps = list(state[run_state.TOKEN_STAMPS])
        self.assertEqual(5, run_state.spend_now(self.root, state)["priced"])
        self.assertEqual(stamps, state[run_state.TOKEN_STAMPS])

    def test_a_meter_with_no_usage_yet_is_unread_with_its_own_reason(self) -> None:
        """MUTANT: a transcript holding no usage judged as zero spend, or its reason replaced."""
        self._open({"minutes": 0, "units": 0, "spend": 10}, opening=None)
        self._use(0)
        rc, v = self._verdict()
        self.assertEqual(0, rc, v)
        self.assertIsNone(v["spend"])
        self.assertEqual("transcript s1.jsonl carries no usage records", v["spend_unread"])

    def test_a_reading_of_zero_with_no_reason_is_still_named(self) -> None:
        """MUTANT: the fallback reason dropped, so a meter that reads 0 and gives no reason
        leaves spend unjudged in silence."""
        self._open({"minutes": 0, "units": 0, "spend": 10})
        with mock.patch.object(run_state, "session_tokens", return_value={"tokens": 0}):
            rc, v = self._verdict()
        self.assertEqual(0, rc, v)
        self.assertEqual("the meter returned no reading", v["spend_unread"])

    def test_a_total_with_no_priced_components_names_why(self) -> None:
        """MUTANT: the total's `priced_reason` dropped for its `reason`, which a measured
        total with an unpriced reading leaves None, so spend goes unjudged in silence."""
        self._open({"minutes": 0, "units": 0, "spend": 10})
        state = run_state.read(self.root)
        bare = [{k: s[k] for k in s if k != "components"}
                for s in state[run_state.TOKEN_STAMPS]]
        run_state.update(str(self.root), **{run_state.TOKEN_STAMPS: bare})
        self._use(5)
        rc, v = self._verdict()
        self.assertEqual(0, rc, v)
        self.assertIsNone(v["spend"])
        self.assertIn("before the meter priced each component", v["spend_unread"])

    # -- AC2 -----------------------------------------------------------------------------

    def test_spend_warns_at_75_and_95_per_cent(self) -> None:
        """AC2. MUTANTS: either band's threshold moved by one per cent; the share rounded
        rather than compared exactly (749 of 1,000 warning); the WARNING line printed below 75
        or not at all; the 95 band read as 75; a warning that stops the run."""
        appetite = 1000
        self._open({"minutes": 0, "units": 0, "spend": appetite})
        used = 0
        for spend, band in ((740, None), (749, None), (750, 75), (940, 75), (949, 75),
                            (950, 95), (999, 95)):
            self._use(spend - used)
            used = spend
            rc, v = self._verdict()
            self.assertEqual(0, rc, (spend, v))
            self.assertFalse(v["exhausted"], spend)
            self.assertEqual(spend, v["spend"])
            self.assertEqual(band, v["spend_warning"], spend)
            rc, text = self._budget(fmt="text")
            self.assertEqual(0, rc, text)
            warnings = [ln for ln in text.splitlines() if ln.startswith("WARNING")]
            if band is None:
                self.assertEqual([], warnings, spend)
                continue
            self.assertEqual(1, len(warnings), text)
            self.assertIn(f"passed {band}% of its appetite", warnings[0])
            self.assertIn(f"{spend:,} of {appetite:,} {run_state.PRICED_LABEL}", warnings[0])
            self.assertIn(f"({spend * 100 // appetite}%)", warnings[0])

    # -- AC3 -----------------------------------------------------------------------------

    def test_an_unreadable_meter_is_named_and_minutes_still_stop_the_run(self) -> None:
        """AC3. MUTANTS: an unread meter read as zero spend, or as a spent appetite; the
        meter's reason replaced or dropped; the unread note printed only when the run
        continues; the minutes axis skipped once spend is unread."""
        self._open({"minutes": 60, "units": 0, "spend": 1000}, opening=None)
        why = run_state.session_tokens(self.root)["reason"]
        self.assertIn(str(self.tx), why)
        rc, v = self._verdict()
        self.assertEqual(0, rc, v)
        self.assertFalse(v["exhausted"])
        self.assertIsNone(v["spend"])
        self.assertEqual(why, v["spend_unread"])
        self.assertIsNone(v["spend_warning"])
        rc, text = self._budget(fmt="text")
        self.assertEqual(0, rc, text)
        self.assertIn(f"spend: NOT JUDGED at this boundary - {why}", text)
        self.assertIn("appetite OK", text)
        self.assertIsNone(v["spend_includes_subagents"])
        self.assertNotIn("main thread only", text, "an unread meter holds no thread at all")
        run_state.update(str(self.root), started_at="2026-01-01T00:00:00Z")
        rc, v = self._verdict()
        self.assertEqual(4, rc, v)
        self.assertEqual("minutes", v["reason"])
        self.assertEqual(why, v["spend_unread"])
        rc, text = self._budget(fmt="text")
        self.assertEqual(4, rc, text)
        self.assertIn("appetite SPENT (reason=minutes)", text)
        self.assertIn(f"spend: NOT JUDGED at this boundary - {why}", text)

    def test_a_reading_with_no_opening_stamp_is_unread_with_the_totals_reason(self) -> None:
        """MUTANT: a reading that forms no priced total judged as zero spend, or its reason
        replaced. The run opened before any transcript existed, so one reading covers no
        delta."""
        self._open({"minutes": 0, "units": 0, "spend": 10}, opening=None)
        self._use(5000)
        rc, v = self._verdict()
        self.assertEqual(0, rc, v)
        self.assertIsNone(v["spend"])
        self.assertIn("carry no closing meter reading", v["spend_unread"])

    def test_a_meter_that_raises_is_unread_and_named_by_its_type(self) -> None:
        """MUTANT: the raise let through, so the breaker crashes instead of judging minutes."""
        self._open({"minutes": 0, "units": 1, "spend": 10})
        with mock.patch.object(run_state, "session_tokens",
                               side_effect=OSError("secret-token in the message")):
            rc, v = self._verdict()
        self.assertEqual(0, rc, v)
        self.assertIn("OSError", v["spend_unread"])
        self.assertNotIn("secret-token", v["spend_unread"])

    def test_a_reading_without_subagents_says_so_and_one_with_them_does_not(self) -> None:
        """MUTANTS: the flag dropped from the verdict, inverted, or the text note printed
        whatever the reading held."""
        self._open({"minutes": 0, "units": 0, "spend": 100_000})
        self._use(10)
        rc, v = self._verdict()
        self.assertIs(False, v["spend_includes_subagents"])
        rc, text = self._budget(fmt="text")
        self.assertIn("main thread only", text)
        sub = self.tx / "s1" / run_state.SUBAGENTS_DIR
        sub.mkdir(parents=True)
        (sub / "agent-a.jsonl").write_text(json.dumps(
            {"message": {"model": "m9", "usage": {"input_tokens": 7}}}) + "\n", encoding="utf-8")
        self._use(1)  # the main transcript stays the newest file
        rc, v = self._verdict()
        self.assertIs(True, v["spend_includes_subagents"], v)
        rc, text = self._budget(fmt="text")
        self.assertNotIn("main thread only", text)

    # -- AC4 -----------------------------------------------------------------------------

    def test_the_spend_appetite_resolves_flag_then_run_then_config_and_ships_unbounded(
            self) -> None:
        """AC4. MUTANTS: any rung of the order swapped or skipped; `capacity.spend` not read;
        the meter read, or a stop or warning formed, with no spend appetite; either key
        shipped non-zero or left out; the page dropping a key, the unit, a band, the unread
        rule or the lower bound."""
        self._open({"minutes": 0, "units": 0})
        self._assert_unbounded()
        self._assert_shipped_and_documented()
        self._config("capacity:\n  spend: 1000\n")
        self.assertEqual(1000, self._verdict()[1]["appetite_spend"])
        self._config("capacity:\n  spend: 1000\nappetite:\n  spend: 500\n")
        self.assertEqual(500, self._verdict()[1]["appetite_spend"])
        run_state.update(str(self.root), appetite={"minutes": 0, "units": 0, "spend": 300})
        self.assertEqual(300, self._verdict()[1]["appetite_spend"])
        rc, v = self._verdict("--appetite-spend", "200")
        self.assertEqual(200, v["appetite_spend"])
        self.assertEqual((4, "spend"), (rc, v["reason"]), "the 10,000,000 spent is judged")
        rc, v = self._verdict("--appetite-spend", "0")
        self.assertEqual(0, v["appetite_spend"], "an explicit 0 is unbounded, not a fall-through")
        run_state.update(str(self.root), appetite={"minutes": 0, "units": 0, "spend": 0})
        self.assertEqual(0, self._verdict()[1]["appetite_spend"],
                         "a run that stamped 0 is unbounded, whatever config says now")

    def _assert_unbounded(self) -> None:
        """Nothing set anywhere: appetite 0, the meter never read, no stop and no warning."""
        self._use(10_000_000)
        with mock.patch.object(run_state, "session_tokens",
                               wraps=run_state.session_tokens) as meter:
            rc, v = self._verdict()
        self.assertEqual(0, rc, v)
        self.assertEqual(0, v["appetite_spend"])
        self.assertFalse(v["exhausted"])
        self.assertIsNone(v["spend_warning"])
        self.assertIsNone(v["spend"])
        self.assertIsNone(v["spend_unread"])
        self.assertEqual(0, meter.call_count, "an unbounded spend axis read the meter")
        rc, text = self._budget(fmt="text")
        self.assertIn("no appetite declared - run is unbounded", text)
        self.assertNotIn("spend", text)

    def _assert_shipped_and_documented(self) -> None:
        defaults = yaml.safe_load((SKILL / "templates" / "config-defaults.yaml")
                                  .read_text(encoding="utf-8"))
        self.assertEqual(0, defaults["capacity"]["spend"])
        self.assertEqual(0, defaults["appetite"]["spend"])
        page = (SKILL / "reference-config.md").read_text(encoding="utf-8")
        start = page.index("## Sprint Capacity {#capacity}")
        section = " ".join(page[start:page.index("## Cost Baseline", start)].split())
        for said in ("`capacity.spend`", "`appetite.spend`", run_state.PRICED_LABEL,
                     "75 and 95 per cent", "unjudged at that boundary and says why",
                     "a lower bound, so the breaker can fire late but never early"):
            self.assertIn(said, section)


if __name__ == "__main__":
    unittest.main()
