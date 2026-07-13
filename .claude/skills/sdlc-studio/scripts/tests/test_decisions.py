"""Unit tests for decisions.py - the project decisions log (CR0080)."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))


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
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            decisions.record_waiver(root, "rule:engagement-floor-v2", "later")
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


if __name__ == "__main__":
    unittest.main()
