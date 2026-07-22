"""BG0236: the run's session-token baseline - the reading `open_run` stamps so a close can
report what THIS run spent rather than what the session has spent.

The harness transcript is one cumulative meter per session. Without a baseline the second
sprint closed in a session books the first sprint's tokens as its own, and the third books
both; that shipped 341,450 and then 472,691 tokens per point against a measured ~25,000/pt
rate, twice corrected by hand afterwards.

The properties pinned here are the writer's half:

* a FRESH run is stamped with the meter reading and the session it was read from;
* a RE-PLAN of the open run leaves that reading alone (moving it forward mid-run would
  discount everything spent before the re-cut);
* every later write PRESERVES it - `update`, a review round, `close_run`, the archive
  (L-0156: an upsert that rewrites a whole record erases the field it was told to keep);
* an unreadable session leaves it ABSENT rather than zero, and never fails the plan.

The reading half - what a close does with a missing baseline - is pinned in `test_retro.py`
(`TokenCaptureIsAttributedToTheRun`).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k run_state
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import run_state  # noqa: E402


class TokenBaselineTests(unittest.TestCase):
    """The baseline `open_run` stamps, and everything that must not lose it."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.transcripts = self.root / "transcripts"
        self.transcripts.mkdir()
        env = mock.patch.dict(os.environ, {"SDLC_STUDIO_TRANSCRIPTS": str(self.transcripts)})
        env.start()
        self.addCleanup(env.stop)
        self.addCleanup(self.tmp.cleanup)

    def _meter(self, tokens: int, name: str = "s1.jsonl") -> Path:
        """Append `tokens` to a session transcript - the harness meter running on."""
        p = self.transcripts / name
        with p.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"message": {"usage": {"input_tokens": tokens}}}) + "\n")
        return p

    def _baseline(self) -> dict | None:
        return run_state.read(str(self.root)).get(run_state.TOKEN_BASELINE)

    def test_run_state_open_run_stamps_the_session_meter_and_its_source(self) -> None:
        src = self._meter(120_000)
        run_state.open_run(str(self.root), batch=["BG0001"], goal="g")
        base = self._baseline()
        self.assertEqual(base["tokens"], 120_000)
        self.assertEqual(base["source"], str(src))
        self.assertTrue(base["at"], "the reading is timestamped")

    def test_run_state_replanning_an_open_run_leaves_its_baseline_alone(self) -> None:
        self._meter(100_000)
        run_state.open_run(str(self.root), batch=["BG0001"], goal="g")
        self._meter(400_000)                       # the run spends while it is open
        run_state.open_run(str(self.root), batch=["BG0002"])   # a mid-run re-cut
        self.assertEqual(self._baseline()["tokens"], 100_000,
                         "a re-plan must not discount what the run has already spent")
        self.assertEqual(run_state.read(str(self.root))["batch"], ["BG0001", "BG0002"])

    def test_run_state_the_next_run_takes_a_fresh_baseline(self) -> None:
        self._meter(100_000)
        run_state.open_run(str(self.root), batch=["BG0001"], goal="g")
        self._meter(900_000)                       # the first run's spend
        run_state.close_run(str(self.root), run_state.GOAL_REACHED)
        run_state.open_run(str(self.root), batch=["BG0002"], goal="g2")
        self.assertEqual(self._baseline()["tokens"], 1_000_000,
                         "the second run starts from where the first one left the meter")

    def test_run_state_the_baseline_survives_every_later_write(self) -> None:
        # L-0156: `update` and `close_run` rewrite the whole record. Each is a chance to drop
        # the field, and a dropped baseline reads exactly like a run opened before it existed.
        self._meter(250_000)
        run_state.open_run(str(self.root), batch=["BG0001"], goal="g")
        run_state.update(str(self.root), appetite={"minutes": 90, "units": 6})
        self.assertEqual(self._baseline()["tokens"], 250_000, "update dropped it")
        run_state.record_review_round(str(self.root), "APPROVE", units=["BG0001"])
        self.assertEqual(self._baseline()["tokens"], 250_000, "a review round dropped it")
        run_state.record_ceiling_override(str(self.root), at_round=2, ceiling=1)
        self.assertEqual(self._baseline()["tokens"], 250_000, "a ceiling override dropped it")
        closed = run_state.close_run(str(self.root), run_state.GOAL_REACHED, handoff="HO0001")
        self.assertEqual(self._baseline()["tokens"], 250_000, "the close dropped it")
        self.assertEqual(closed[run_state.TOKEN_BASELINE]["tokens"], 250_000)
        archived = run_state.read_archived(str(self.root), closed["run_id"])
        self.assertEqual(archived[run_state.TOKEN_BASELINE]["tokens"], 250_000,
                         "the archived record carries the baseline too")

    def test_run_state_an_unreadable_session_leaves_the_baseline_absent(self) -> None:
        # No transcript at all: the plan must still open its run, and the baseline must be
        # None rather than 0 - a zero baseline would make the close publish the whole
        # session total as the sprint's own cost, which is the defect.
        with mock.patch.dict(os.environ, {"SDLC_STUDIO_TRANSCRIPTS": str(self.root / "nope")}):
            state = run_state.open_run(str(self.root), batch=["BG0001"], goal="g")
        self.assertTrue(state["run_id"], "the run still opens")
        self.assertIsNone(state[run_state.TOKEN_BASELINE])

    def test_run_state_a_session_with_no_usage_yet_leaves_the_baseline_absent(self) -> None:
        # A deliberate false negative, stated where it is made: a transcript that exists but
        # carries no usage has a true baseline of zero, and this refuses to assume it. The
        # sprint then reports NOT ATTRIBUTABLE - a lost measurement, never a wrong one.
        (self.transcripts / "s1.jsonl").write_text('{"type": "meta"}\n', encoding="utf-8")
        run_state.open_run(str(self.root), batch=["BG0001"], goal="g")
        self.assertIsNone(self._baseline())

    def test_run_state_a_run_nobody_opened_has_no_baseline(self) -> None:
        self._meter(700_000)
        run_state.update(str(self.root), goal="g")
        self.assertIsNone(self._baseline(), "no fabricated baseline on a blank record")

    def test_run_state_the_baseline_field_is_declared_in_fields(self) -> None:
        # FIELDS documents the record; a field the module writes but does not list there is
        # a field the next reader of this module does not know exists.
        self.assertIn(run_state.TOKEN_BASELINE, run_state.FIELDS)


class DelegatedSpendIsSuppliedNotMeasured(unittest.TestCase):
    """BG0252: the session transcript records the MAIN THREAD only.

    Measured on one live transcript: 6,624,813 tokens of usage, of which sidechain records
    accounted for zero. So a fan-out sprint's delegated agents are invisible to the meter, and
    the run that published 439,982 had spent at least 1,227,816. A delegated total therefore
    cannot be measured here; it can only be SUPPLIED - each agent reports its own total when it
    finishes - and the record keeps that distinction, exactly as the mutation ledger separates a
    registered claim from a re-run measurement.
    """

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "sdlc-studio" / ".local").mkdir(parents=True)
        self.addCleanup(self.tmp.cleanup)

    def _open(self) -> dict:
        return run_state.open_run(str(self.root), batch=["BG0001"], goal="g")

    def test_a_delegated_total_is_recorded_against_the_run_and_marked_supplied(self) -> None:
        self._open()
        rec = run_state.record_delegated_tokens(str(self.root), 198_734, agent="cluster-1")
        self.assertEqual(rec["tokens"], 198_734)
        self.assertEqual(rec["agent"], "cluster-1")
        self.assertEqual(rec["provenance"], run_state.SUPPLIED,
                         "a figure an agent reported is a claim, never a meter reading")
        state = run_state.read(str(self.root))
        self.assertEqual(run_state.delegated_total(state), 198_734)

    def test_delegated_totals_accumulate_rather_than_overwrite(self) -> None:
        # the live shape: four cluster agents finish one after another, each reporting its own
        self._open()
        for n, tokens in enumerate((198_734, 220_109, 163_373, 205_618)):
            run_state.record_delegated_tokens(str(self.root), tokens, agent=f"a{n}")
        state = run_state.read(str(self.root))
        self.assertEqual(len(run_state.delegated_records(state)), 4)
        self.assertEqual(run_state.delegated_total(state), 787_834)

    def test_a_total_nobody_can_attribute_to_a_run_is_not_recorded(self) -> None:
        self.assertIsNone(run_state.record_delegated_tokens(str(self.root), 1_000),
                          "a spend counted against no run cannot be joined to anything later")

    def test_a_non_positive_total_is_refused_rather_than_recorded_as_zero(self) -> None:
        self._open()
        for bad in (0, -5, None, "lots", True):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                run_state.record_delegated_tokens(str(self.root), bad)
        self.assertEqual(run_state.delegated_total(run_state.read(str(self.root))), 0)

    def test_the_records_survive_a_close_and_the_archive(self) -> None:
        # L-0156 again: every whole-record rewrite is a chance to drop the field
        self._open()
        run_state.record_delegated_tokens(str(self.root), 300_000, agent="reviewer")
        run_state.update(str(self.root), appetite={"minutes": 90})
        closed = run_state.close_run(str(self.root), run_state.GOAL_REACHED, handoff="HO0001")
        self.assertEqual(run_state.delegated_total(closed), 300_000)
        archived = run_state.read_archived(str(self.root), closed["run_id"])
        self.assertEqual(run_state.delegated_total(archived), 300_000)

    def test_a_malformed_entry_is_skipped_rather_than_poisoning_the_total(self) -> None:
        self._open()
        run_state.record_delegated_tokens(str(self.root), 100_000)
        run_state.update(str(self.root), **{run_state.DELEGATED: [
            {"tokens": 100_000}, "not a record", {"tokens": "lots"}, {"tokens": 50_000}]})
        state = run_state.read(str(self.root))
        self.assertEqual(run_state.delegated_total(state), 150_000)

    def test_the_delegated_field_is_declared_in_fields(self) -> None:
        self.assertIn(run_state.DELEGATED, run_state.FIELDS)


class ARunIdIsUniqueByConstructionNotByLuck(unittest.TestCase):
    """BG0253: the RUN id was minted with no collision check at all.

    `short_ulid` is 6 timestamp characters - roughly a 17-minute bucket - plus 2 random ones, so
    two mints milliseconds apart collide about once in 1,024, and its own docstring says the
    allocator's glob-retry is the real backstop. The RUN id path never went through one, so the
    commit gate failed at random on an unchanged tree (`'RUN-01KY38CE' == 'RUN-01KY38CE'`), and
    the underlying risk is worse than a flaky test: two runs sharing an identity in the telemetry
    and velocity records.

    The generator cannot provide uniqueness, so the ALLOCATOR does - checked against the runs
    this project has already recorded. That is what makes "two consecutive mints differ" a
    property rather than a 1-in-1,024 bet, and it is the reason these tests drive the generator
    with a CONSTANT: an inequality test that only passes because a random suffix happened to
    differ would also pass a generator returning the same id every time.
    """

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "sdlc-studio" / ".local").mkdir(parents=True)
        self.addCleanup(self.tmp.cleanup)

    def _next_run(self) -> str:
        """Close the open run and open the next one, as a cycle boundary does."""
        if run_state.read(str(self.root)).get("run_id"):
            run_state.close_run(str(self.root), run_state.GOAL_REACHED)
        return run_state.open_run(str(self.root), batch=["BG0001"], goal="g")["run_id"]

    def test_a_constant_generator_still_mints_two_different_run_ids(self) -> None:
        from lib import sdlc_md
        with mock.patch.object(sdlc_md, "short_ulid", return_value="AAAA1111"):
            first, second = self._next_run(), self._next_run()
        self.assertEqual(first, "RUN-AAAA1111")
        self.assertNotEqual(second, first,
                            "the second run took an id the first one already holds")

    def test_the_clashing_mint_is_retried_rather_than_extended_immediately(self) -> None:
        """The cheap path first, exactly as `mint_v3_id` does: retry the generator, and only
        extend the suffix when it keeps clashing."""
        from lib import sdlc_md
        with mock.patch.object(sdlc_md, "short_ulid",
                               side_effect=["AAAA1111", "AAAA1111", "BBBB2222"]):
            self.assertEqual(self._next_run(), "RUN-AAAA1111")
            self.assertEqual(self._next_run(), "RUN-BBBB2222")

    def test_an_archived_run_s_id_is_never_minted_again(self) -> None:
        """The archive is the register of every run this project has opened, and it outlives the
        live file - so it, not the live record alone, is what the mint is checked against."""
        from lib import sdlc_md
        with mock.patch.object(sdlc_md, "short_ulid", return_value="AAAA1111"):
            first = self._next_run()
            self._next_run()                      # first is now archived
            third = self._next_run()
        self.assertNotIn(first, {third}, "an archived run's identity was handed out twice")
        self.assertEqual(len({r["run_id"] for r in run_state.archived(str(self.root))}), 2)

    def test_an_ordinary_mint_is_not_disturbed_by_the_check(self) -> None:
        ids = {self._next_run() for _ in range(5)}
        self.assertEqual(len(ids), 5)
        self.assertTrue(all(i.startswith("RUN-") for i in ids))


class SessionTokenReaderTests(unittest.TestCase):
    """`session_tokens` is the ONE meter reader, shared by the baseline stamp and the close.
    Its own contract - cache reads excluded, a stated reason when it cannot read - is pinned
    through `retro.harness_tokens` in `test_retro.py`; what matters here is that the two are
    literally the same function, so they cannot drift apart."""

    def test_run_state_reader_is_the_same_object_retro_exposes(self) -> None:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        import retro
        self.assertIs(retro.harness_tokens, run_state.session_tokens)
        self.assertEqual(retro.TRANSCRIPTS_ENV, run_state.TRANSCRIPTS_ENV)


class MalformedTranscriptTests(unittest.TestCase):
    """A malformed transcript record must not abort the plan, and must not produce a short total.

    Found by the adversarial review of RUN-01KY2K5R. The reader summed `int(usage.get(k) or 0)`
    under a clause catching only OSError, so one non-numeric usage value raised TypeError out of
    `session_tokens`, through `_session_baseline` (which also caught only OSError) and out of
    `open_run` - so `sprint plan --write` minted no run at all and wrote no run-state.json. Both
    docstrings claimed otherwise: "Never raises: a plan must not fail because a transcript was
    unreadable", and a documented return shape of {"tokens": None, "reason"}.

    The transcript format is the harness's, not this project's, and it has moved before - the
    reader already probes two shapes. So the clause is the whole family, matching what
    `archived()._index` in the same module learned from its own repairs.
    """

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "sdlc-studio" / ".local").mkdir(parents=True)
        self.transcripts = self.root / "transcripts"
        self.transcripts.mkdir()
        env = mock.patch.dict(os.environ, {"SDLC_STUDIO_TRANSCRIPTS": str(self.transcripts)})
        env.start()
        self.addCleanup(env.stop)
        self.addCleanup(self.tmp.cleanup)

    def _write(self, *records: str) -> None:
        (self.transcripts / "s1.jsonl").write_text("".join(r + "\n" for r in records),
                                                   encoding="utf-8")

    def test_a_malformed_usage_value_reports_a_reason_instead_of_raising(self) -> None:
        self._write(json.dumps({"message": {"usage": {"input_tokens": ["oops"],
                                                      "output_tokens": 5}}}))
        cap = run_state.session_tokens(str(self.root))          # must not raise
        self.assertIsNone(cap["tokens"])
        self.assertIn("malformed", cap["reason"])

    def test_every_malformed_shape_is_handled_not_just_the_one_that_was_reported(self) -> None:
        """The clause is the family, not the shape that prompted it. A list, a dict and a
        non-numeric string each reach `int()` by a different route."""
        for bad in (["oops"], {"a": 1}, "not-a-number"):
            with self.subTest(bad=bad):
                self._write(json.dumps({"message": {"usage": {"input_tokens": bad}}}))
                cap = run_state.session_tokens(str(self.root))
                self.assertIsNone(cap["tokens"], f"{bad!r} produced a number")

    def test_a_malformed_record_refuses_the_total_rather_than_returning_a_short_one(self) -> None:
        """Skipping the bad record would return a quietly SHORT total, and a short baseline
        inflates the delta measured against it - a wrong number, which is the expensive failure.
        The good record's 900,000 must NOT come back on its own."""
        self._write(json.dumps({"message": {"usage": {"input_tokens": 900000}}}),
                    json.dumps({"message": {"usage": {"input_tokens": ["oops"]}}}))
        cap = run_state.session_tokens(str(self.root))
        self.assertIsNone(cap["tokens"])
        self.assertNotIn("900000", json.dumps(cap))

    def test_the_plan_still_mints_a_run_and_stamps_no_baseline(self) -> None:
        """The consequence that made this MAJOR: `sprint plan --write` could not open a run."""
        self._write(json.dumps({"message": {"usage": {"input_tokens": ["oops"]}}}))
        rec = run_state.open_run(str(self.root), batch=["BG0001"], goal="g")   # must not raise
        self.assertTrue(rec.get("run_id"))
        self.assertTrue((self.root / "sdlc-studio" / ".local" / "run-state.json").exists(),
                        "the run state was never written, so the run does not exist")
        self.assertIsNone(rec.get(run_state.TOKEN_BASELINE),
                          "an untrustworthy meter must leave the baseline absent, not zero")

    def test_the_baseline_backstop_holds_even_if_the_reader_starts_raising(self) -> None:
        """`_session_baseline`'s own clause, pinned DIRECTLY because nothing else reaches it.

        Reverting it to OSError-only was a SURVIVING mutant: `session_tokens` now returns rather
        than raising, so the backstop is unreachable through the public path and read as coverage
        while pinned by nothing (L-0159). It is kept rather than deleted because it enforces the
        stated contract - a plan must not fail because a transcript was unreadable - against a
        future change to the reader, which is exactly what happened here. So it is tested against
        a reader that DOES raise.
        """
        with mock.patch.object(run_state, "session_tokens",
                               side_effect=TypeError("reader started raising")):
            self.assertIsNone(run_state._session_baseline(str(self.root)))
            rec = run_state.open_run(str(self.root), batch=["BG0001"], goal="g")
            self.assertTrue(rec.get("run_id"), "the plan failed on an unreadable transcript")
            self.assertIsNone(rec.get(run_state.TOKEN_BASELINE))


if __name__ == "__main__":
    unittest.main()
