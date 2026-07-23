"""Unit tests for review_prep.py.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "review_prep.py"
_spec = importlib.util.spec_from_file_location("review_prep", SCRIPT_PATH)
assert _spec and _spec.loader
review_prep = importlib.util.module_from_spec(_spec)
sys.modules["review_prep"] = review_prep
_spec.loader.exec_module(review_prep)


def _base(root: Path) -> Path:
    b = root / "sdlc-studio"
    b.mkdir(parents=True, exist_ok=True)
    return b


class StalenessTests(unittest.TestCase):
    def test_no_review_state_means_needs_review(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            b = _base(root)
            (b / "prd.md").write_text("# PRD\n", encoding="utf-8")
            stale = review_prep.staleness(root)
            self.assertIn("prd", stale)
            self.assertTrue(stale["prd"]["needs_review"])

    def test_recent_review_clears_staleness(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            b = _base(root)
            (b / "prd.md").write_text("# PRD\n", encoding="utf-8")
            (b / ".local").mkdir()
            # A review far in the future is necessarily after the file mtime.
            (b / ".local" / "review-state.json").write_text(
                json.dumps({"artifacts": {"prd": {"last_reviewed": "2999-01-01T00:00:00Z"}}}),
                encoding="utf-8",
            )
            stale = review_prep.staleness(root)
            self.assertFalse(stale["prd"]["needs_review"])


class PersonaUsageTests(unittest.TestCase):
    def test_defined_referenced_and_unused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            b = _base(root)
            (b / "personas.md").write_text(
                "# Personas\n\n## Sarah Chen\n\n## Tom Bradley\n", encoding="utf-8"
            )
            (b / "prd.md").write_text("# PRD\n\nSarah Chen is the PM.\n", encoding="utf-8")
            pu = review_prep.persona_usage(root)
            self.assertEqual(sorted(pu["defined"]), ["Sarah Chen", "Tom Bradley"])
            self.assertEqual(pu["referenced_in_prd"], ["Sarah Chen"])
            self.assertEqual(pu["unused"], ["Tom Bradley"])


class InputsTests(unittest.TestCase):
    def test_counts_and_ac_summary(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            b = _base(root)
            sd = b / "stories"
            sd.mkdir()
            (sd / "US0001-x.md").write_text("# X\n\n> **Status:** Done\n", encoding="utf-8")
            (b / ".local").mkdir()
            (b / ".local" / "verify-report.json").write_text(
                json.dumps({"stories": {"US0001-x": {"verified": 2, "failed": 1}}}),
                encoding="utf-8",
            )
            ins = review_prep.inputs(root)
            self.assertEqual(ins["counts"]["story"], 1)
            self.assertEqual(ins["ac_verification"], {"stories": 1, "verified": 2, "failed": 1})


class RequiredLegsTests(unittest.TestCase):
    """Leg absence is machine-visible: for each of the four required document legs, whether
    the artefact is present and, if not, the waiver decision id (or null). An absent-and-unwaived
    leg is no longer invisible in the prep JSON - the enabler of the BG0110 prose downgrade."""

    def test_absent_leg_is_visible_and_unwaived(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            b = _base(root)
            (b / "prd.md").write_text("# PRD\n", encoding="utf-8")
            legs = review_prep.required_legs(root)
            self.assertEqual(set(legs), {"prd", "trd", "tsd", "personas"})
            self.assertTrue(legs["prd"]["present"])
            self.assertFalse(legs["tsd"]["present"])
            self.assertIsNone(legs["tsd"]["waiver"])
            self.assertTrue(legs["prd"]["path"].endswith("prd.md"))

    def test_waived_leg_carries_decision_id(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _base(root)
            import decisions
            r = decisions.record_waiver(root, "leg:tsd", "single-repo project")
            legs = review_prep.required_legs(root)
            self.assertFalse(legs["tsd"]["present"])
            self.assertEqual(legs["tsd"]["waiver"], r["id"])

    def test_personas_directory_counts_as_present(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            b = _base(root)
            pdir = b / "personas"
            pdir.mkdir()
            (pdir / "maya.md").write_text("# Maya\n", encoding="utf-8")
            self.assertTrue(review_prep.required_legs(root)["personas"]["present"])

    def test_personas_md_fallback_counts_as_present(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            b = _base(root)
            (b / "personas.md").write_text("## Maya\n", encoding="utf-8")
            self.assertTrue(review_prep.required_legs(root)["personas"]["present"])

    def test_prep_json_carries_required_legs(self) -> None:
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _base(root)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                review_prep.main(["prep", "--root", str(root), "--format", "json"])
            payload = json.loads(out.getvalue())
            self.assertIn("required_legs", payload)
            self.assertFalse(payload["required_legs"]["tsd"]["present"])


class CmdTests(unittest.TestCase):
    def test_prep_runs_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _base(Path(d))
            self.assertEqual(review_prep.main(["prep", "--root", d, "--format", "json"]), 0)


class PersonaIndexNotCountedTests(unittest.TestCase):
    """BG0129: the persona dir uses `index.md`; the filter excluded only `_index.md`, so the
    index was parsed as a phantom persona ('Persona Index'). Both index spellings are now
    excluded, in both the usage and required-legs passes."""

    def _dir(self, d: Path) -> None:
        pdir = d / "sdlc-studio" / "personas"
        pdir.mkdir(parents=True)
        (pdir / "index.md").write_text("# Persona Index\n")
        (pdir / "maya.md").write_text("# Maya Okafor\n")
        (d / "sdlc-studio" / "prd.md").write_text("# PRD\nMaya Okafor is our user.\n")

    def test_index_md_is_not_a_persona(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._dir(Path(d))
            usage = review_prep.persona_usage(Path(d))
            self.assertNotIn("Persona Index", usage["defined"])
            self.assertEqual(usage["defined"], ["Maya Okafor"])

    def test_underscore_index_still_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pdir = Path(d) / "sdlc-studio" / "personas"; pdir.mkdir(parents=True)
            (pdir / "_index.md").write_text("# Index\n")
            (pdir / "sam.md").write_text("# Sam Rivera\n")
            (Path(d) / "sdlc-studio" / "prd.md").write_text("# PRD\n")
            self.assertEqual(review_prep.persona_usage(Path(d))["defined"], ["Sam Rivera"])


import json  # noqa: E402


def _review_workspace(root: Path, *, with_rv: bool = True) -> None:
    sd = root / "sdlc-studio"
    for doc in ("prd.md", "trd.md", "tsd.md"):
        (sd / doc).parent.mkdir(parents=True, exist_ok=True)
        (sd / doc).write_text(f"# {doc}\n", encoding="utf-8")
    (sd / "personas").mkdir(exist_ok=True)
    (sd / "personas" / "maya.md").write_text("# Maya\n", encoding="utf-8")
    if with_rv:
        rv = sd / "reviews"
        rv.mkdir(exist_ok=True)
        (rv / "RV0042-unified-review.md").write_text(
            "# RV-0042: Unified Review\n\n> **Status:** N/A\n> **Date:** 2026-07-17\n",
            encoding="utf-8")


class CloseStampTests(unittest.TestCase):
    """US0186: `close` stamps review-state.json deterministically - the CRITICAL
    hand-step the workflow spelled out and nobody performed until 2026-07-16."""

    def test_close_stamps_state_for_every_leg(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _review_workspace(root)
            rc = review_prep.close(root, "RV0042")
            self.assertEqual(rc["stamped"], ["persona", "prd", "trd", "tsd"])
            state = json.loads(
                (root / "sdlc-studio" / ".local" / "review-state.json").read_text())
            for leg in ("prd", "trd", "tsd", "persona"):
                self.assertEqual(state["artifacts"][leg]["review_findings_ref"], "RV0042")
                self.assertTrue(state["artifacts"][leg]["last_reviewed"])
            self.assertIn("RV0042", state["reviews"])
            self.assertIn("RV0042-unified-review.md",
                          state["reviews"]["RV0042"]["findings_file"])

    def test_close_preserves_foreign_state_keys(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _review_workspace(root)
            local = root / "sdlc-studio" / ".local"
            local.mkdir(parents=True)
            (local / "review-state.json").write_text(
                json.dumps({"version": 1, "artifacts": {"custom": {"x": 1}},
                            "reviews": {"RV0001": {"artifact": "old"}}}), encoding="utf-8")
            review_prep.close(root, "RV0042")
            state = json.loads((local / "review-state.json").read_text())
            self.assertEqual(state["artifacts"]["custom"], {"x": 1})
            self.assertIn("RV0001", state["reviews"])


class AnchorRefusalTests(unittest.TestCase):
    """US0186: the anchor is derived from a record or not at all."""

    def test_close_refuses_without_the_dated_rv(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _review_workspace(root, with_rv=False)
            with self.assertRaises(ValueError) as ctx:
                review_prep.close(root, "RV0042")
            self.assertIn("RV0042", str(ctx.exception))
            self.assertFalse(
                (root / "sdlc-studio" / ".local" / "review-state.json").exists())

    def test_latest_write_requires_rv_reference_in_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _review_workspace(root)
            body = "# Unified Review anchor\n\nno reference to the record here\n"
            with self.assertRaises(ValueError) as ctx:
                review_prep.close(root, "RV0042", latest_body=body)
            self.assertIn("RV0042", str(ctx.exception))
            self.assertFalse((root / "sdlc-studio" / "reviews" / "LATEST.md").exists())

    def test_latest_written_when_body_references_the_record(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _review_workspace(root)
            body = "# RV0042 - Unified Review anchor\n\ncontent\n"
            review_prep.close(root, "RV0042", latest_body=body)
            latest = (root / "sdlc-studio" / "reviews" / "LATEST.md").read_text()
            self.assertEqual(latest, body)
class CloseIndexRowTests(unittest.TestCase):
    """US0214: the close writes the RV's own index row.

    Before this, `close` stamped review-state and derived LATEST but left the RV out of
    `reviews/_index.md`. The very next step of the close chain - reconcile - then caught
    the missing row as drift and stopped the ceremony for a mechanical fix that
    `reconcile apply` performed anyway (CR0335). The write belongs where the record is
    created.
    """

    def _rows(self, root):
        p = root / "sdlc-studio" / "reviews" / "_index.md"
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def test_close_writes_the_index_row(self) -> None:
        """AC1: the row exists after the close."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _review_workspace(root)
            review_prep.close(root, "RV0042")
            self.assertIn("RV0042", self._rows(root))

    def test_no_missing_row_drift_after_close(self) -> None:
        """AC2: the close chain's reconcile has nothing to stop for."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _review_workspace(root)
            review_prep.close(root, "RV0042")
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "reconcile", Path(review_prep.__file__).parent / "reconcile.py")
            rec = importlib.util.module_from_spec(spec)
            sys.modules["reconcile"] = rec
            spec.loader.exec_module(rec)
            missing = [x for x in rec.apply_meta(root, dry_run=True)["missing_unapplied"]
                       if "RV0042" in str(x)]
            self.assertEqual(missing, [])

    def test_existing_row_is_not_duplicated(self) -> None:
        """AC3: a re-run appends nothing - the close is idempotent."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _review_workspace(root)
            review_prep.close(root, "RV0042")
            first = self._rows(root)
            r2 = review_prep.close(root, "RV0042")
            self.assertEqual(self._rows(root), first)
            self.assertFalse(r2["indexed"])          # nothing new appended
            self.assertEqual(first.count("RV0042"), 1)

    def test_indexing_failure_still_stamps(self) -> None:
        """AC4: the stamp is the close; indexing is a convenience on top of it."""
        import io
        from contextlib import redirect_stderr
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _review_workspace(root)
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "reconcile", Path(review_prep.__file__).parent / "reconcile.py")
            rec = importlib.util.module_from_spec(spec)
            sys.modules["reconcile"] = rec
            spec.loader.exec_module(rec)
            original = rec.apply_meta
            self.addCleanup(setattr, rec, "apply_meta", original)

            def _boom(*_a, **_k):
                raise OSError("index is read-only")
            rec.apply_meta = _boom
            with redirect_stderr(io.StringIO()) as err:
                r = review_prep.close(root, "RV0042")
            self.assertFalse(r["indexed"])
            self.assertIn("reconcile.py apply", err.getvalue())   # remedy named
            state = json.loads(
                (root / "sdlc-studio" / ".local" / "review-state.json").read_text())
            self.assertIn("RV0042", state["reviews"])             # the close still happened


class ClaimPassOrderTests(unittest.TestCase):
    """US0322 (EP0109): the claim pass is ordered before the logic review, and the two kinds of
    finding are reported separately so a prose-only round is visibly a different kind of round."""

    def test_a_round_with_logic_findings_and_no_claim_pass_is_incomplete(self) -> None:
        order = review_prep.review_phase_order()
        self.assertLess(order.index("claim-pass"), order.index("logic-review"))
        # logic findings recorded with no claim pass run: incomplete, not accepted
        r = review_prep.assess_review_round(claim_pass_ran=False, logic_findings=["bug at x:1"])
        self.assertFalse(r["complete"])
        # the same round WITH the claim pass run first is complete
        r2 = review_prep.assess_review_round(claim_pass_ran=True, logic_findings=["bug at x:1"])
        self.assertTrue(r2["complete"])

    def test_prose_and_logic_findings_are_counted_separately(self) -> None:
        r = review_prep.assess_review_round(
            claim_pass_ran=True, prose_findings=["false claim a", "false claim b"],
            logic_findings=[])
        self.assertEqual(r["prose_findings"], 2)
        self.assertEqual(r["logic_findings"], 0)
        self.assertEqual(r["kind"], "prose-only")       # a different kind of round
        # a round carrying a logic defect is a different kind, counted apart
        r2 = review_prep.assess_review_round(
            claim_pass_ran=True, prose_findings=[], logic_findings=["real bug"])
        self.assertEqual((r2["prose_findings"], r2["logic_findings"]), (0, 1))
        self.assertNotEqual(r2["kind"], r["kind"])


if __name__ == "__main__":
    unittest.main()
