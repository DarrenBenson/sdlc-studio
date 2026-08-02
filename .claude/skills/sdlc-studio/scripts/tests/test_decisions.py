"""Unit tests for decisions.py - the project decisions log (CR0080)."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import threading
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
from lib import sdlc_md  # noqa: E402


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


decisions = _load("decisions")


class DecisionsTests(unittest.TestCase):
    def test_add_auto_numbers_and_appends(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            r1 = decisions.add(repo, "Anonymous-first, accounts in M2", "avoid a sign-up wall")
            r2 = decisions.add(repo, "Stored-hash tokens", "no signed-token secret to manage")
            self.assertEqual(r1["id"], "D0001")
            self.assertEqual(r2["id"], "D0002")        # auto-incremented
            rows = decisions.list_decisions(repo)
            self.assertEqual([x["id"] for x in rows], ["D0001", "D0002"])
            self.assertEqual(rows[0]["status"], "accepted")

    def test_list_filters_by_status(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            decisions.add(repo, "a", "r")
            decisions.add(repo, "b", "r", status="superseded")
            self.assertEqual(len(decisions.list_decisions(repo, status="superseded")), 1)
            self.assertEqual(len(decisions.list_decisions(repo)), 2)

    def test_pipe_in_text_is_escaped(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            decisions.add(repo, "use a | b shape", "round-trips")
            rows = decisions.list_decisions(repo)
            self.assertEqual(len(rows), 1)             # the pipe did not split into extra columns

    def test_promote_records_backlink(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            r = decisions.promote(repo, "PRD-OQ3", "Anonymous-first", "avoid a sign-up wall")
            rows = decisions.list_decisions(repo)
            self.assertEqual(r["id"], "D0001")
            self.assertIn("[from PRD-OQ3]", rows[0]["rationale"])   # back-linked, one record

    def test_ensure_log_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            self.assertTrue(decisions.ensure_log(repo))
            self.assertFalse(decisions.ensure_log(repo))   # second call is a no-op


def _status_of(root, did):
    return next(r["status"] for r in decisions.list_decisions(root) if r["id"] == did)


class SupersedeStatusTests(unittest.TestCase):
    """BG0068: --supersedes flips the named row to superseded; unknown id fails loud."""

    def test_supersede_flips_the_target_row(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            a = decisions.add(root, "A", "r", today="2026-07-09")
            decisions.add(root, "B", "r", supersedes=a["id"], today="2026-07-09")
            self.assertEqual(_status_of(root, a["id"]), "superseded")   # was accepted

    def test_new_row_records_lineage_and_stays_current(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            a = decisions.add(root, "A", "r", today="2026-07-09")
            b = decisions.add(root, "B", "r", supersedes=a["id"], today="2026-07-09")
            rec = next(r for r in decisions.list_decisions(root) if r["id"] == b["id"])
            self.assertEqual(rec["supersedes"], a["id"])
            self.assertEqual(rec["status"], "accepted")                 # the new one is current

    def test_unknown_supersedes_id_raises(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            decisions.add(root, "A", "r", today="2026-07-09")
            with self.assertRaises(ValueError):
                decisions.add(root, "B", "r", supersedes="D9999", today="2026-07-09")

    def test_supersede_stray_digit_typo_fails_loud(self) -> None:
        # a value that merely contains a number is not an id - it must raise, not silently
        # flip a plausible-but-wrong row (fail-loud is the whole point of the fix)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dec_a = decisions.add(root, "A", "r", today="2026-07-09")
            for bad in ("the 5th one", "D00121", "D12x"):
                with self.assertRaises(ValueError):
                    decisions.add(root, "B", "r", supersedes=bad, today="2026-07-09")
            self.assertEqual(_status_of(root, dec_a["id"]), "accepted")   # untouched

    def test_supersede_accepts_bare_number(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            a = decisions.add(root, "A", "r", today="2026-07-09")       # D0001
            decisions.add(root, "B", "r", supersedes="1", today="2026-07-09")
            self.assertEqual(_status_of(root, a["id"]), "superseded")

    def test_pipe_cell_not_corrupted_by_the_flip(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            a = decisions.add(root, "A with a | pipe", "why | here", today="2026-07-09")
            decisions.add(root, "B", "r", supersedes=a["id"], today="2026-07-09")
            rec = next(r for r in decisions.list_decisions(root) if r["id"] == a["id"])
            self.assertEqual(rec["status"], "superseded")
            self.assertIn("pipe", rec["decision"])                      # cell content intact


class BackfillTests(unittest.TestCase):
    """BG0068: one-time backfill flips rows named in a later Supersedes column but still
    marked accepted (the pre-fix shape, e.g. D0012/D0013 in this repo)."""

    def _wire_supersedes(self, root, target_did, superseding_did):
        p = decisions._log_path(root)
        lines = p.read_text(encoding="utf-8").splitlines()
        for i, ln in enumerate(lines):
            if ln.strip().startswith(f"| {superseding_did} |"):
                lines[i] = ln.replace("| -- |", f"| {target_did} |", 1)
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_backfill_flips_stale_accepted_rows_idempotently(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            a = decisions.add(root, "A", "r", today="2026-07-09")
            b = decisions.add(root, "B", "r", today="2026-07-09")       # accepted, no flip
            self._wire_supersedes(root, a["id"], b["id"])               # pre-fix contradiction
            self.assertEqual(_status_of(root, a["id"]), "accepted")     # stale
            self.assertEqual(decisions.backfill_superseded(root), 1)
            self.assertEqual(_status_of(root, a["id"]), "superseded")
            self.assertEqual(decisions.backfill_superseded(root), 0)    # idempotent


class WaiverTests(unittest.TestCase):
    """A waiver is a machine-detectable decision row (`waiver: <subject>`) recording that a
    rule is intentionally out of scope here. General over any subject - a review leg
    (`leg:tsd`) or a rule (`rule:engagement-floor`) - so the primitive is reusable."""

    def test_absent_waiver_is_none(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(decisions.waiver_for(Path(d), "leg:tsd"))

    def test_record_then_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            r = decisions.record_waiver(root, "leg:tsd", "single-repo; Verify: discipline instead")
            self.assertTrue(r["id"].startswith("D"))
            self.assertEqual(decisions.waiver_for(root, "leg:tsd"), r["id"])
            self.assertIsNone(decisions.waiver_for(root, "leg:trd"))   # a different leg is unmatched

    def test_lookup_is_anchored_not_substring(self) -> None:
        # a decision that merely MENTIONS the leg is not a waiver for it (the BG0110 defect)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            decisions.add(root, "TSD leg is optional polish, not a gap", "we said so")
            self.assertIsNone(decisions.waiver_for(root, "leg:tsd"))

    def test_lookup_is_full_match_not_prefix(self) -> None:
        # a waiver of a LONGER subject must not satisfy a lookup for a prefix of it: `leg:tsd`
        # is a prefix of the token `waiver: rule:engagement-floor-v2`? no - but a substring match
        # on the shared stem would; full-cell equality is the only correct rule.
        # Written through `add`, not `record_waiver`: this pins the LOOKUP rule, and the subject
        # is deliberately one no checker declares (which record-time validation now refuses).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            decisions.add(root, f"{decisions.WAIVER_PREFIX} rule:engagement-floor-v2", "later")
            self.assertIsNone(decisions.waiver_for(root, "rule:engagement-floor"))
            self.assertIsNotNone(decisions.waiver_for(root, "rule:engagement-floor-v2"))

    def test_subject_is_case_and_space_insensitive(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            decisions.record_waiver(root, "  LEG:TSD  ", "x")
            self.assertIsNotNone(decisions.waiver_for(root, "leg:tsd"))

    def test_superseded_waiver_no_longer_holds(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            r = decisions.record_waiver(root, "leg:tsd", "out of scope for now")
            decisions.add(root, "TSD now required", "changed our mind", supersedes=r["id"])
            self.assertIsNone(decisions.waiver_for(root, "leg:tsd"))   # only accepted waivers hold

    def test_empty_subject_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                decisions.record_waiver(Path(d), "  ", "x")

    def test_cli_waive_leg(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with contextlib.redirect_stdout(io.StringIO()):
                rc = decisions.main(["waive", "--leg", "tsd", "--rationale", "single-repo",
                                     "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertIsNotNone(decisions.waiver_for(root, "leg:tsd"))

    def test_cli_waive_rejects_out_of_scope_code_leg(self) -> None:
        # CODE is out of scope (D0022): --leg choices are the four document legs only
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(SystemExit):
                with contextlib.redirect_stderr(io.StringIO()):
                    decisions.main(["waive", "--leg", "code", "--rationale", "x", "--root", d])

    def test_cli_waive_general_subject_is_reusable(self) -> None:
        # CR0229 reuse: a general rule waiver, not a leg
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with contextlib.redirect_stdout(io.StringIO()):
                decisions.main(["waive", "--subject", "rule:engagement-floor",
                                "--rationale", "spike, no floor yet", "--root", str(root)])
            self.assertIsNotNone(decisions.waiver_for(root, "rule:engagement-floor"))

    def test_cli_waive_requires_exactly_one_of_leg_or_subject(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(SystemExit):
                with contextlib.redirect_stderr(io.StringIO()):
                    decisions.main(["waive", "--rationale", "x", "--root", d])   # neither given


class WaiverValidationTests(unittest.TestCase):
    """US0526: a waiver that will do nothing is refused when it is WRITTEN, not discovered
    when it fails to help. Two ways a waiver does nothing: it names a rule no checker
    declares, or it carries no reason and so cannot be audited later."""

    def test_an_unknown_rule_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with self.assertRaises(ValueError) as cm:
                decisions.record_waiver(root, "rule:no-such-checker", "seemed reasonable")
            msg = str(cm.exception)
            # it names the rules that DO exist, derived from the checkers themselves
            self.assertIn("rule:engagement-floor", msg)
            self.assertIn("rule:conformance:critiqued", msg)
            self.assertEqual(decisions.list_decisions(root), [])   # nothing was recorded

    def test_a_waiver_without_a_reason_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for empty in ("", "   ", None):
                with self.assertRaises(ValueError):
                    decisions.record_waiver(root, "rule:engagement-floor", empty)
            self.assertEqual(decisions.list_decisions(root), [])

    def test_a_declared_rule_and_its_scope_tail_still_record(self) -> None:
        # the guard must not refuse the legitimate shapes: the bare rule, a per-unit scope
        # tail, and a leg. Over-refusal would be the same defect pointing the other way.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for subject in ("rule:engagement-floor", "rule:engagement-floor:US0100",
                            "rule:conformance:critiqued:US0103-US0310", "leg:tsd"):
                self.assertIsNotNone(decisions.record_waiver(root, subject, "recorded reason"))
                self.assertIsNotNone(decisions.waiver_for(root, subject), subject)

    def test_the_known_rules_are_derived_from_the_checkers(self) -> None:
        # LL: an enumerated list silently exempts what it forgot. The rule vocabulary is read
        # off the checker modules, so a stage added to conformance.STAGES is waivable without
        # a second list here remembering to grow.
        subjects, unreadable = decisions.waivable_subjects()
        self.assertEqual(unreadable, [], f"scripts unreadable for their declared rules: {unreadable}")
        import importlib
        conf = importlib.import_module("conformance")
        for stage in conf.STAGES:
            self.assertIn(f"rule:conformance:{stage}", subjects)


class ConcurrencySafetyTests(unittest.TestCase):
    """BG0154: the decisions ledger is a load-bearing shared file, so its writes must go
    through sdlc_md.atomic_write and its id allocation + insert must be serialised by
    sdlc_md.allocation_lock - the same guarantee trd.md rule 5 makes for every shared file."""

    def test_add_takes_the_allocation_lock(self) -> None:
        entered = []
        real_lock = sdlc_md.allocation_lock

        @contextlib.contextmanager
        def _spy(root, *a, **k):
            entered.append(root)
            with real_lock(root, *a, **k):
                yield

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            orig = sdlc_md.allocation_lock
            sdlc_md.allocation_lock = _spy
            try:
                decisions.add(root, "A", "r")
            finally:
                sdlc_md.allocation_lock = orig
        self.assertTrue(entered, "add must take sdlc_md.allocation_lock around allocate+insert")

    def test_add_writes_atomically(self) -> None:
        # a crash mid-write must leave the previous ledger intact, not a truncated file.
        wrote = []
        real_atomic = sdlc_md.atomic_write

        def _spy(path, text, *a, **k):
            wrote.append(str(path))
            return real_atomic(path, text, *a, **k)

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            decisions.add(root, "A", "r")           # seed the ledger
            orig = sdlc_md.atomic_write
            sdlc_md.atomic_write = _spy
            try:
                decisions.add(root, "B", "r")
            finally:
                sdlc_md.atomic_write = orig
        self.assertTrue(any(decisions.LOG_REL.split("/")[-1] in w for w in wrote),
                        "add must route the ledger write through sdlc_md.atomic_write")

    def test_concurrent_add_mints_distinct_ids(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            decisions.ensure_log(root)
            ids: list[str] = []
            errors: list[Exception] = []
            lock = threading.Lock()

            def worker(i: int) -> None:
                try:
                    r = decisions.add(root, f"decision {i}", "r")
                    with lock:
                        ids.append(r["id"])
                except Exception as e:  # noqa: BLE001 - collect for the assertion
                    with lock:
                        errors.append(e)

            threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            self.assertEqual(errors, [], f"concurrent add raised: {errors}")
            self.assertEqual(len(set(ids)), 8, f"duplicate D-ids minted: {sorted(ids)}")
            rows = decisions.list_decisions(root)
            self.assertEqual(len(rows), 8, "a concurrent write clobbered a row")


class WaiverScopeTailTests(unittest.TestCase):
    """BG0361. `record_waiver` validated the RULE half of a subject and not the scope tail, so
    `rule:conformance:critiqued:pre-two-role` recorded clean and covered NOTHING - the sprint
    close it was written to unblock stayed blocked, while the log said the question was settled.
    A waiver that silently exempts nobody is worse than a refused one: the refusal is visible."""

    RATIONALE = "the cohort predates the gate and is being paid down under BG0350"

    def _root(self, d) -> Path:
        root = Path(d)
        (root / "sdlc-studio").mkdir(parents=True)
        return root

    def test_a_scope_naming_no_unit_is_refused_at_record_time(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            with self.assertRaises(ValueError) as caught:
                decisions.record_waiver(
                    root, "rule:conformance:critiqued:pre-two-role", self.RATIONALE)
            self.assertIn("pre-two-role", str(caught.exception))
            self.assertIn("no unit", str(caught.exception))

    def test_a_range_and_a_single_id_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            for scope in ("US0103-US0310", "US0288"):
                with self.subTest(scope=scope):
                    r = decisions.record_waiver(
                        root, f"rule:conformance:critiqued:{scope}", self.RATIONALE)
                    self.assertTrue(r["id"])

    def test_a_bare_rule_with_no_tail_still_waives_the_stage(self) -> None:
        """The carve-out must not become a refusal of every waiver: an absent tail waives the
        stage outright, which is a deliberate and legitimate form."""
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            r = decisions.record_waiver(root, "rule:conformance:critiqued", self.RATIONALE)
            self.assertTrue(r["id"])

    def test_the_check_agrees_with_the_consumer_that_resolves_it(self) -> None:
        """The record-time refusal and the run-time matcher must answer the same question. Two
        readings of one grammar diverge, and the looser one accepts what the other rejects -
        which is exactly how a waiver covering nothing came to be recorded."""
        import conformance
        for scope in ("pre-two-role", "US0103-US0310", "US0288", "everything"):
            with self.subTest(scope=scope):
                refused = conformance.scope_tail_error(scope) is not None
                covers_any = any(conformance._scope_covers(scope, rid)
                                 for rid in ("US0103", "US0288", "US0310", "US9999"))
                self.assertEqual(refused, not covers_any,
                                 f"{scope!r}: refused={refused} but covers_any={covers_any}")


class TableCellTests(unittest.TestCase):
    """A rationale is prose; a row is a table. The writer reconciles them, not the caller.

    A multi-paragraph rationale pasted straight into a cell splits the row, and the table stops
    being a table (markdownlint MD055/MD056). It happened to this project's own decision log and
    had to be repaired by hand.
    """

    def test_a_multi_paragraph_rationale_stays_on_one_row(self) -> None:
        """MUTANT: paste the rationale in unchanged.

        The fixture is the shape that actually broke the log - two paragraphs separated by a
        blank line - and the assertion is on the TABLE's integrity, not on the text, because a
        cell that merely looks tidy can still have split the row above it.
        """
        mod = _load("decisions")
        rationale = ("The first paragraph explains the decision.\n\n"
                     "The second adds the evidence it rests on.\nAnd a third line.")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            mod.add(root, "a decision", rationale)
            text = (root / "sdlc-studio" / "decisions.md").read_text(encoding="utf-8")
        rows = [ln for ln in text.splitlines() if ln.startswith("|")]
        widths = {ln.count("|") for ln in rows}
        self.assertEqual(1, len(widths),
                         f"the table has rows of differing cell counts {widths} - the rationale "
                         f"split the row")
        self.assertIn("The second adds the evidence", text,
                      "the rationale's content was lost rather than collapsed")

    def test_a_pipe_in_the_rationale_is_still_escaped(self) -> None:
        """The other half of cell safety. MUTANT: collapse newlines but stop escaping pipes.

        An unescaped pipe adds a column to that row alone, which is the same defect by another
        route.
        """
        mod = _load("decisions")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            mod.add(root, "a decision", "uses `a | b` as a separator")
            text = (root / "sdlc-studio" / "decisions.md").read_text(encoding="utf-8")
        rows = [ln for ln in text.splitlines() if ln.startswith("|")]
        self.assertEqual(1, len({ln.count("|") - ln.count("\\|") for ln in rows}),
                         "an unescaped pipe added a column to one row")


if __name__ == "__main__":
    unittest.main()
