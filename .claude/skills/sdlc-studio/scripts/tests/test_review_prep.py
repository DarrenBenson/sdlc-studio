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


if __name__ == "__main__":
    unittest.main()
