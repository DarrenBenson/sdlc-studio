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
# gitutil is the TESTS' confined-git helper, so it sits beside this module, not in scripts/.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
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
        # A mid-run re-cut that KEEPS the open run's work and pulls one more unit in: an
        # overlapping re-plan, which accumulates (a disjoint one is refused - see
        # DisjointBatchIsRefusedTests).
        run_state.open_run(str(self.root), batch=["BG0001", "BG0002"])
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

    # -- the fallback, which was the one candidate nobody checked ---------------------
    def test_the_extended_fallback_is_checked_against_taken_too(self) -> None:
        """The Resolution claims "unique BY CONSTRUCTION, not by luck". It was luck: after 16
        clashes the mint returned `RUN-{new_ulid()[:12]}` with no check at all, so driving BOTH
        generators constant produced a duplicate. Found by the independent review of
        RUN-01KY3MFX."""
        from lib import sdlc_md
        with mock.patch.object(sdlc_md, "short_ulid", return_value="AAAA1111"), \
                mock.patch.object(sdlc_md, "new_ulid",
                                  side_effect=["BBBB2222CCCC"] * 1 + ["DDDD3333EEEE"] * 40):
            first, second = self._next_run(), self._next_run()
        self.assertEqual(first, "RUN-AAAA1111")
        self.assertEqual(second, "RUN-BBBB2222CCCC")
        self.assertNotEqual(second, first)

    def test_both_generators_constant_refuses_rather_than_returning_a_duplicate(self) -> None:
        """When even the extended suffix cannot produce a free id, that is a broken generator,
        not an unlucky one. Handing back a known duplicate would merge two runs' telemetry,
        archive and velocity records - the data problem this allocator exists to prevent - so it
        RAISES and names why."""
        from lib import sdlc_md
        # both generators pinned to the SAME value, so the extended suffix is no escape either
        with mock.patch.object(sdlc_md, "short_ulid", return_value="AAAA1111ZZZZ"), \
                mock.patch.object(sdlc_md, "new_ulid", return_value="AAAA1111ZZZZ"):
            self.assertEqual(self._next_run(), "RUN-AAAA1111ZZZZ")
            with self.assertRaises(RuntimeError) as ctx:
                self._next_run()
        self.assertIn("duplicate", str(ctx.exception))

    def test_the_outgoing_run_is_excluded_even_when_the_archive_missed_it(self) -> None:
        """`open_run` archives the outgoing run before minting, so passing it in is usually
        redundant - and a mutant replacing that line with `pass` killed nothing. It is kept for
        the case the redundancy does not cover: an archive write that did not happen (a
        read-only or full `.local`) leaves the register without the run being replaced, and this
        is then the only thing between the new run and its predecessor's identity. Pinned
        directly, since no path through `open_run` can reach it."""
        from lib import sdlc_md
        with mock.patch.object(sdlc_md, "short_ulid", return_value="AAAA1111"):
            minted = run_state._mint_run_id(str(self.root), {"run_id": "RUN-AAAA1111"})
        self.assertNotEqual(minted, "RUN-AAAA1111",
                            "the outgoing run's identity was handed to its successor")


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


class ReviewLedgerHonestyTests(unittest.TestCase):
    """BG0261: the round ledger cannot be contradicted at the moment it is written - a
    goal-verdict note naming a different round count, a round recorded after `ended_at`, and a
    reviewer label disagreeing with its own index are each refused, not written silently."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = str(Path(self.tmp.name))
        self.addCleanup(self.tmp.cleanup)
        run_state.open_run(self.root, batch=["BG0001"], goal="ship it")
        for _ in range(6):
            run_state.record_review_round(self.root, "REJECT", units=["BG0001"])

    def test_a_note_round_or_label_contradicting_the_ledger_is_refused(self):
        self.assertEqual(run_state.review_round_count(self.root), 6)

        # (label) a reviewer label naming a round other than its index (this is round 7) is refused
        with self.assertRaises(run_state.ReviewLedgerError):
            run_state.record_review_round(self.root, "REJECT", units=["BG0001"],
                                          reviewer="round 3")
        self.assertEqual(run_state.review_round_count(self.root), 6,
                         "the contradicting round must not have been written")
        # a label agreeing with its index (round 7) records
        rec = run_state.record_review_round(self.root, "REJECT", units=["BG0001"],
                                            reviewer="round 7")
        self.assertEqual(rec["round"], 7)

        # (note) a goal-verdict note naming a different round count is refused; the count is
        # DERIVED from the ledger, not restated beside it
        with self.assertRaises(run_state.ReviewLedgerError):
            run_state.record_goal_verdict(self.root, "ACHIEVED",
                                          note="three independent adversarial rounds converged")
        gv = run_state.record_goal_verdict(self.root, "ACHIEVED", note="all rounds converged")
        self.assertEqual(gv["rounds"], 7, "the round count must be derived from the ledger")

        # (ended) a round recorded against a run that already ended is refused
        run_state.close_run(self.root, run_state.GOAL_REACHED)
        self.assertTrue(run_state.read(self.root).get("ended_at"))
        with self.assertRaises(run_state.ReviewLedgerError):
            run_state.record_review_round(self.root, "APPROVE", units=["BG0001"])
        self.assertEqual(run_state.review_round_count(self.root), 7,
                         "no round may be recorded after the run ended")


class DisjointBatchIsRefusedTests(unittest.TestCase):
    """CR0401 / US0326: a `sprint plan --write` against an open run holding a DISJOINT batch is
    refused, not fused. One project holds one run slot; folding a second, unrelated batch into
    the open run strands its goal verdict. An OVERLAPPING re-plan still accumulates."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = str(Path(self.tmp.name))
        (Path(self.root) / "sdlc-studio" / ".local").mkdir(parents=True)
        self.addCleanup(self.tmp.cleanup)

    def _open_six(self) -> dict:
        return run_state.open_run(self.root, batch=[f"BG{n:04d}" for n in range(1, 7)],
                                  goal="evacuate the homeserver")

    def test_a_disjoint_plan_exits_non_zero_and_leaves_run_state_json_byte_identical(self) -> None:
        self._open_six()
        p = run_state.path(self.root)
        before = p.read_bytes()
        with self.assertRaises(run_state.DisjointBatchError):
            run_state.open_run(self.root, batch=["US0100", "US0101"], goal="a second sprint")
        self.assertEqual(p.read_bytes(), before,
                         "a refused disjoint plan must leave run-state.json byte-identical")

    def test_one_shared_unit_re_plans_and_zero_shared_units_refuses(self) -> None:
        opened = self._open_six()
        # one shared unit (BG0001) -> a genuine re-plan: accumulates, no new flag, same identity
        replanned = run_state.open_run(self.root, batch=["BG0001", "US0200"])
        self.assertEqual(replanned["run_id"], opened["run_id"])
        self.assertEqual(replanned["started_at"], opened["started_at"])
        self.assertIn("US0200", replanned["batch"])
        self.assertEqual(len(replanned["batch"]), 7)          # six accumulated the one new unit
        # zero shared units -> refused
        with self.assertRaises(run_state.DisjointBatchError):
            run_state.open_run(self.root, batch=["CR0400", "CR0401"])

    def test_a_refused_plan_archives_nothing_and_mints_no_run_id(self) -> None:
        opened = self._open_six()
        with self.assertRaises(run_state.DisjointBatchError):
            run_state.open_run(self.root, batch=["US0100"])
        self.assertEqual(run_state.archived(self.root), [],
                         "a refused plan must archive nothing")
        self.assertEqual(run_state.read(self.root)["run_id"], opened["run_id"],
                         "a refused plan must mint no new run id; the run keeps the one it had")

    def test_disjoint_refusal_is_none_for_a_closed_run_so_a_fresh_plan_is_not_blocked(self) -> None:
        # The guard is only against an OPEN run. Once a run is closed (spent), a fresh disjoint
        # batch is a new run, not a refusal - `disjoint_refusal` must return None so the plan pre
        # -check does not block the next sprint.
        self._open_six()
        run_state.close_run(self.root, run_state.GOAL_REACHED)
        self.assertIsNone(run_state.disjoint_refusal(self.root, ["US0100"]),
                          "a fresh plan after a run closed must not be refused as disjoint")


class RefusalNamesTheOpenRunTests(unittest.TestCase):
    """US0327: the refusal identifies the run standing in the way (id, outcome, batch size) and
    states both ways forward as commands, not as advice - and names no third route."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = str(Path(self.tmp.name))
        (Path(self.root) / "sdlc-studio" / ".local").mkdir(parents=True)
        self.addCleanup(self.tmp.cleanup)

    def _refusal(self) -> run_state.DisjointBatchError:
        opened = run_state.open_run(self.root, batch=[f"BG{n:04d}" for n in range(1, 7)],
                                    goal="g")
        self.run_id = opened["run_id"]
        with self.assertRaises(run_state.DisjointBatchError) as caught:
            run_state.open_run(self.root, batch=["US0100"])
        return caught.exception

    def test_refusal_states_the_open_run_id_outcome_and_batch_size(self) -> None:
        exc = self._refusal()
        text = str(exc)
        self.assertIn(self.run_id, text)                 # the run standing in the way, by id
        self.assertIn(run_state.RUNNING, text)           # its outcome
        self.assertIn("6", text)                         # its batch size
        self.assertEqual(exc.run_id, self.run_id)
        self.assertEqual(exc.outcome, run_state.RUNNING)
        self.assertEqual(exc.batch_size, 6)

    def test_refusal_states_both_ways_forward_as_runnable_commands(self) -> None:
        text = str(self._refusal())
        commands = [ln.strip() for ln in text.splitlines() if "sprint.py" in ln]
        self.assertEqual(len(commands), 2,
                         "exactly two ways forward are named, and no third route")
        joined = "\n".join(commands)
        self.assertIn("close", joined)                   # close the open run
        self.assertTrue(any("plan" in c and "--write" in c for c in commands),
                        "deliberately re-planning it, as a command that runs as printed")
        # each is a command (starts with the tool), not prose advice
        for c in commands:
            self.assertTrue(c.startswith("sprint.py "), c)


class FailedCloseAttemptIsProtectedTests(unittest.TestCase):
    """CR0401 / US0328: a run whose ONLY close artefact is a FAILED close attempt is
    open-and-protected, not absorbable - `close_attempts` is deliberately not in
    `_CLOSE_ARTEFACTS`. Protected is not finished: a truly closed run (ended_at) is still
    replaced."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = str(Path(self.tmp.name))
        (Path(self.root) / "sdlc-studio" / ".local").mkdir(parents=True)
        self.addCleanup(self.tmp.cleanup)

    def _open_with_failed_close(self) -> dict:
        opened = run_state.open_run(self.root, batch=[f"BG{n:04d}" for n in range(1, 7)],
                                    goal="g")
        # A recorded FAILED close attempt: nine items outstanding, and none of the true close
        # artefacts. The run is still `running`.
        run_state.update(self.root, close_attempts=[{"at": "2026-07-21T09:00:00Z",
                                                     "outstanding": 9, "stages": ["gate"]}])
        state = run_state.read(self.root)
        self.assertIsNone(state.get("sprint_goal_verdict"))
        self.assertIsNone(state.get("ended_at"))
        self.assertIsNone(state.get("handoff"))
        return opened

    def test_a_run_with_only_a_failed_close_attempt_refuses_a_disjoint_batch(self) -> None:
        opened = self._open_with_failed_close()
        with self.assertRaises(run_state.DisjointBatchError):
            run_state.open_run(self.root, batch=["US0100"])
        state = run_state.read(self.root)
        self.assertEqual(state["run_id"], opened["run_id"])
        self.assertEqual(state["batch"], [f"BG{n:04d}" for n in range(1, 7)],
                         "the mid-close run's batch is exactly what it held before")

    def test_close_attempts_protect_the_run_while_ended_at_still_replaces_it(self) -> None:
        # Run one: only a failed close attempt -> refused, everything intact.
        opened = self._open_with_failed_close()
        with self.assertRaises(run_state.DisjointBatchError) as caught:
            run_state.open_run(self.root, batch=["US0100"])
        self.assertEqual(caught.exception.run_id, opened["run_id"])
        self.assertEqual(caught.exception.batch_size, 6)
        self.assertEqual(caught.exception.outstanding, 9)
        self.assertEqual(run_state.read(self.root)["close_attempts"][-1]["outstanding"], 9)
        # Run two, a separate project, carries ended_at: it IS finished, so a disjoint plan
        # archives and replaces it at exit zero.
        other = tempfile.TemporaryDirectory()
        self.addCleanup(other.cleanup)
        oroot = str(Path(other.name))
        (Path(oroot) / "sdlc-studio" / ".local").mkdir(parents=True)
        first = run_state.open_run(oroot, batch=["BG0500"], goal="g")
        run_state.close_run(oroot, run_state.GOAL_REACHED)         # sets ended_at
        replaced = run_state.open_run(oroot, batch=["US0100"], goal="fresh")
        self.assertNotEqual(replaced["run_id"], first["run_id"],
                            "a truly closed run is replaced by a fresh run, never refused")
        self.assertTrue(run_state.read_archived(oroot, first["run_id"]),
                        "the finished run is archived, never silently discarded")

    def test_refusal_names_the_failed_close_attempt_and_its_outstanding_count(self) -> None:
        self._open_with_failed_close()
        with self.assertRaises(run_state.DisjointBatchError) as caught:
            run_state.open_run(self.root, batch=["US0100"])
        text = str(caught.exception)
        self.assertIn("close attempt", text.lower())
        self.assertIn("9", text)                          # the outstanding count it left
        self.assertIn("outstanding", text.lower())


class OverAppetiteTests(unittest.TestCase):
    """US0359 / CR0349: an over-appetite batch is recorded with BOTH the standing appetite and
    the accepted one, so raising the ceiling to make a batch fit does not erase the overage."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_both_the_standing_and_accepted_appetite_are_recorded(self) -> None:
        """AC1. A batch of 32 accepted against a standing 8 records both numbers."""
        run_state.record_appetite(self.root, accepted_units=32, accepted_minutes=960,
                                  standing_units=8, standing_minutes=240)
        ap = run_state.read(self.root)["appetite"]
        self.assertEqual(ap["units"], 32)             # the accepted one the breaker stops on
        self.assertEqual(ap["standing_units"], 8)     # the standing one it was measured against
        self.assertTrue(ap["over_appetite"])

    def test_the_plan_does_not_read_as_fitting(self) -> None:
        """AC2. The read-back reports 32 against a standing 8, never 32/32 - the record must not
        say the batch fitted when it was made to fit."""
        run_state.record_appetite(self.root, accepted_units=32, accepted_minutes=960,
                                  standing_units=8, standing_minutes=240)
        over = run_state.appetite_overage(self.root)
        self.assertIsNotNone(over)
        self.assertEqual(over["units"]["accepted"], 32)
        self.assertEqual(over["units"]["standing"], 8)
        self.assertNotEqual(over["units"]["accepted"], over["units"]["standing"])
        self.assertTrue(over["units"]["over"])

    def test_a_within_appetite_run_records_no_overage(self) -> None:
        """AC3. A batch inside the standing appetite records no overage - the field distinguishes
        an accepted overage from an ordinary run, or it means nothing."""
        run_state.record_appetite(self.root, accepted_units=6, accepted_minutes=180,
                                  standing_units=8, standing_minutes=240)
        self.assertFalse(run_state.read(self.root)["appetite"]["over_appetite"])
        self.assertIsNone(run_state.appetite_overage(self.root))

    def test_over_on_the_clock_alone_is_still_an_overage(self) -> None:
        """The overage is per-axis: a batch that fits the unit count but not the minutes was still
        accepted past its standing appetite, and only the axis over is flagged."""
        run_state.record_appetite(self.root, accepted_units=6, accepted_minutes=960,
                                  standing_units=8, standing_minutes=240)
        over = run_state.appetite_overage(self.root)
        self.assertIsNotNone(over)
        self.assertTrue(over["minutes"]["over"])
        self.assertFalse(over["units"]["over"])


class BatchMutationTests(unittest.TestCase):
    """`sprint batch drop/add` mutate an OPEN run's approved batch (CR0421 AC1-3).

    The batch chosen on day one bound the close on day five: there was no verb to drop a unit or
    add one, and `Deferred` (a status on the WORK) does not remove a unit from the batch the
    done-gate reads. Drop judges THIS BATCH - it removes the id from `batch` and records the
    change - which is the whole distinction from Deferred.
    """

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.root = str(Path(self._td.name))

    def tearDown(self) -> None:
        self._td.cleanup()

    def test_drop_removes_unit_and_records_the_change(self) -> None:
        run_state.open_run(self.root, batch=["US0001", "US0002"], goal="g")
        run_state.drop_from_batch(self.root, "US0002", reason="pulled - not started this sprint")
        state = run_state.read(self.root)
        self.assertEqual(state["batch"], ["US0001"], "the dropped unit is gone from the batch")
        changes = state.get("batch_changes") or []
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]["action"], "drop")
        self.assertEqual(changes[0]["id"], "US0002")
        self.assertEqual(changes[0]["reason"], "pulled - not started this sprint")
        self.assertTrue(changes[0]["at"], "the drop is timestamped")

    def test_a_drop_needs_a_reason(self) -> None:
        run_state.open_run(self.root, batch=["US0001"], goal="g")
        with self.assertRaises(run_state.RunStateError):
            run_state.drop_from_batch(self.root, "US0001", reason="  ")

    def test_dropping_a_unit_not_in_the_batch_is_refused(self) -> None:
        run_state.open_run(self.root, batch=["US0001"], goal="g")
        with self.assertRaises(run_state.RunStateError):
            run_state.drop_from_batch(self.root, "US0099", reason="typo")

    def test_a_drop_needs_an_open_run(self) -> None:
        # No run open: nothing to drop from, and a drop must not fabricate a run.
        with self.assertRaises(run_state.RunStateError):
            run_state.drop_from_batch(self.root, "US0001", reason="r")

    def test_add_appends_to_open_batch_and_records_the_change(self) -> None:
        run_state.open_run(self.root, batch=["US0001"], goal="g")
        run_state.add_to_batch(self.root, "US0002")
        state = run_state.read(self.root)
        self.assertEqual(state["batch"], ["US0001", "US0002"], "the added unit joins the batch")
        changes = state.get("batch_changes") or []
        self.assertEqual([c["action"] for c in changes], ["add"])
        self.assertEqual(changes[0]["id"], "US0002")
        self.assertTrue(changes[0]["at"])

    def test_adding_a_unit_already_in_the_batch_does_not_duplicate_it(self) -> None:
        run_state.open_run(self.root, batch=["US0001"], goal="g")
        run_state.add_to_batch(self.root, "US0001")
        state = run_state.read(self.root)
        self.assertEqual(state["batch"], ["US0001"], "no duplicate id")
        self.assertEqual(len(state.get("batch_changes") or []), 1, "but the call is still recorded")

    def test_drop_releases_the_done_gate_but_deferred_does_not(self) -> None:
        # The done-gate reads `state["batch"]`. Deferring a unit changes its STATUS, not the batch,
        # so it stays gated; dropping removes it from the batch the gate reads. This pins that only
        # a drop mutates batch membership - the WORK-vs-BATCH distinction the CR turns on.
        run_state.open_run(self.root, batch=["US0001", "US0002"], goal="g")
        # "Deferring" US0001 is a status change elsewhere; the batch is unaffected by it.
        run_state.drop_from_batch(self.root, "US0002", reason="out of scope for this batch")
        batch = run_state.read(self.root)["batch"]
        self.assertIn("US0001", batch, "the (would-be Deferred) unit is still in the gated batch")
        self.assertNotIn("US0002", batch, "only the dropped unit left the gated batch")


class DeliveryBatchSpanTests(unittest.TestCase):
    """The batch-span API shipped with ZERO tests of its own - it was covered only incidentally
    through `note_finding`, and four of its documented contracts were surviving mutants. Every
    contract these docstrings make a point of is pinned here."""

    def _root(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        # A run is OPENED first. These tests previously started a batch against no run at all,
        # which is what let the fabrication in `start_batch` go unnoticed: the fixture encoded
        # the buggy contract, so the guard that should have existed had nothing to fail.
        run_state.open_run(root, goal="a goal", batch=["US0001"])
        return root

    def test_starting_a_batch_with_no_run_open_is_REFUSED_and_writes_nothing(self) -> None:
        """BG0451. `state = state or _blank()` minted a run whose id was null - breaking `read`'s
        documented never-fabricated invariant - and `_is_spent` then read that null id as spent,
        so the next `open_run` (`sprint plan --write`) replaced the state and took the span with
        it. Silently. Every finding attributed to that span pointed at nothing afterwards.

        A batch is scoped to a run by definition, so this is a command to refuse, not a state to
        mint. Both halves asserted: the refusal, and that NOTHING was written - a guard that
        raises after writing would pass a test checking only the exception.
        """
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        self.assertEqual({}, run_state.read(root), "the fixture already had a run")
        with self.assertRaises(run_state.RunStateError) as ctx:
            run_state.start_batch(root, ["US0001", "US0002"])
        self.assertIn("no run is open", str(ctx.exception))
        self.assertEqual({}, run_state.read(root),
                         "a run state was fabricated despite the refusal")

    def test_a_span_SURVIVES_the_next_plan_of_the_same_run(self) -> None:
        """The data-loss half, which no test covered. The span must outlive a re-plan: a
        re-planned run is the same run, and the batch record is what every filed finding's
        `Raised-in-batch` key points at."""
        root = self._root()
        run_state.start_batch(root, ["US0001", "US0002"])
        before = [s.get("units") for s in (run_state.read(root).get("batches") or [])]
        run_state.open_run(root, goal="a goal", batch=["US0001", "US0003"])
        after = [s.get("units") for s in (run_state.read(root).get("batches") or [])]
        self.assertEqual(before, after, "the re-plan destroyed the batch span")

    def test_open_batch_returns_the_LAST_span_not_the_first(self) -> None:
        """Work lands in the current batch. Returning `spans[0]` would attribute every later
        finding to the first batch of the run - and survived, untested."""
        root = self._root()
        run_state.start_batch(root, ["US0001"])
        run_state.close_batch(root, reviewer="a", author="b", verdict="APPROVE")
        run_state.start_batch(root, ["US0002"])
        self.assertEqual(run_state.open_batch(root)["units"], ["US0002"])

    def test_start_batch_merges_into_an_open_span(self) -> None:
        """A batch that grows mid-flight is a batch, not a second one. Always appending would
        leave the first span open forever and split one batch's findings across two records."""
        root = self._root()
        run_state.start_batch(root, ["US0001"])
        run_state.start_batch(root, ["US0002"])
        self.assertEqual(len(run_state.batches(root)), 1, "a second span was opened")
        self.assertEqual(run_state.open_batch(root)["units"], ["US0001", "US0002"])

    def test_start_batch_opens_a_new_span_after_a_review(self) -> None:
        """The other half: merging must not swallow the NEXT batch into a reviewed one."""
        root = self._root()
        run_state.start_batch(root, ["US0001"])
        run_state.close_batch(root, reviewer="a", author="b", verdict="APPROVE")
        run_state.start_batch(root, ["US0002"])
        self.assertEqual(len(run_state.batches(root)), 2)

    def test_close_batch_normalises_the_verdict(self) -> None:
        """Readers compare against APPROVE/REJECT. Storing it un-uppercased made the comparison
        case-dependent, and survived."""
        root = self._root()
        run_state.start_batch(root, ["US0001"])
        run_state.close_batch(root, reviewer="a", author="b", verdict="approve")
        self.assertEqual(run_state.batches(root)[-1]["verdict"], "APPROVE")

    def test_close_batch_refuses_with_nothing_open(self) -> None:
        root = self._root()
        with self.assertRaises(ValueError):
            run_state.close_batch(root, reviewer="a", author="b", verdict="APPROVE")

    def test_note_finding_never_fabricates_a_run(self) -> None:
        # Builds its OWN runless root: `_root` now opens a run, because `start_batch` refuses
        # without one (BG0451). This test's whole subject is the no-run case, so it must not
        # inherit a fixture that has one - the two guards are siblings and both are needed.
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        self.assertIsNone(run_state.note_finding(root, "BG0001"))
        self.assertFalse(run_state.path(root).exists(),
                         "attributing a finding minted a run state in a project with no run")

    def test_units_are_deduped_and_keep_first_order(self) -> None:
        root = self._root()
        run_state.start_batch(root, ["US0002", "US0001", "US0002"])
        self.assertEqual(run_state.open_batch(root)["units"], ["US0002", "US0001"])


class BaseRefTests(unittest.TestCase):
    """The commit a run's delivery is measured FROM is stamped when the run opens.

    `sdlc-studio/.local/sprint-base-ref.txt` was written once and never rewritten, so it held a
    sha two weeks older than the run reading it. That ref decides whether a finding is a
    regression this unit caused or something already true: a fortnight early, unrelated work
    reads as new and blocks the review, and a defect the unit really introduced can read as
    pre-existing and be waved through.
    """

    def _repo(self, d):
        root = Path(d)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        gitutil.git(["init", "-q"], cwd=root)
        (root / "a.txt").write_text("x", encoding="utf-8")
        gitutil.git(["add", "-A"], cwd=root)
        gitutil.git(["commit", "-qm", "base"], cwd=root)
        return root

    def test_a_fresh_run_records_head_as_its_base_ref(self) -> None:
        """MUTANT: drop the BASE_REF stamp from the fresh-run branch."""
        mod = run_state
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            head = gitutil.git(["rev-parse", "HEAD"], cwd=root,
                               capture_output=True, text=True).stdout.strip()
            mod.open_run(root, batch=["US0001"])
            self.assertEqual(head, mod.base_ref(root),
                             "the run did not record the commit it is measured from")

    def test_a_replan_does_not_move_the_base_ref(self) -> None:
        """MUTANT: stamp the base ref on every open, not only a fresh one.

        Moving it mid-run would silently reclassify every finding raised so far - work already
        judged a regression would become pre-existing because the yardstick moved.
        """
        mod = run_state
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            mod.open_run(root, batch=["US0001"])
            first = mod.base_ref(root)
            (root / "b.txt").write_text("y", encoding="utf-8")
            gitutil.git(["add", "-A"], cwd=root)
            gitutil.git(["commit", "-qm", "more"], cwd=root)
            mod.open_run(root, batch=["US0001", "US0002"])   # a re-plan of the OPEN run
            self.assertEqual(first, mod.base_ref(root),
                             "a re-plan moved the base ref, reclassifying findings already made")

    def test_an_unrecorded_base_ref_reads_empty_not_a_guess(self) -> None:
        """MUTANT: fall back to HEAD when none was recorded.

        A consumer must be able to tell "not recorded" from a sha. The whole defect was a ref
        nobody owned being silently believed, and a fallback to HEAD would make every diff
        empty rather than obviously wrong.
        """
        mod = run_state
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            self.assertEqual("", mod.base_ref(root),
                             "an unrecorded base ref returned a value rather than nothing")


if __name__ == "__main__":
    unittest.main()
