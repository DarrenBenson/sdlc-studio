"""Unit tests for the v3 spec-edit guard (US0092/CR0195): a deterministic pre-check that
surfaces edits to a requirements/spec document so the critic can judge whether they were
requested. An untraced semantic spec edit is the worst propagation of a bad plan (it poisons
every later reader). Dormant under schema_version 2.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, DIR / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sg = _load("spec_guard", "spec_guard.py")


def _repo(root: Path, v3: bool = True, cfg_extra: str = "") -> Path:
    sd = root / "sdlc-studio"
    sd.mkdir(parents=True, exist_ok=True)
    if v3:
        (sd / ".config.yaml").write_text("schema_version: 3\n" + cfg_extra, encoding="utf-8")
    return root


class MatchTests(unittest.TestCase):
    """AC2: spec_edits reports which changed files match a spec glob, deterministically."""

    def test_spec_document_edits_are_detected(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            changed = ["src/app.py", "docs/prd.md", "requirements/r5.md",
                       "specs/api.md", "README.md"]
            edits = sg.spec_edits(root, changed)
            self.assertIn("docs/prd.md", edits)
            self.assertIn("requirements/r5.md", edits)
            self.assertIn("specs/api.md", edits)
            self.assertNotIn("src/app.py", edits)
            self.assertNotIn("README.md", edits)

    def test_deterministic_same_input_same_output(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            changed = ["docs/trd.md", "x.py"]
            self.assertEqual(sg.spec_edits(root, changed), sg.spec_edits(root, changed))

    def test_dormant_under_v2(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), v3=False)
            self.assertEqual(sg.spec_edits(root, ["docs/prd.md"]), [])   # no-op on v2

    def test_root_spec_file_detected(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            edits = sg.spec_edits(root, ["SPEC.md", "product.spec.md", "src/app.py"])
            self.assertIn("SPEC.md", edits)                 # root spec files are covered
            self.assertIn("product.spec.md", edits)
            self.assertNotIn("src/app.py", edits)

    def test_configured_spec_paths_honoured(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra="review:\n  spec_paths:\n    - \"*.contract.md\"\n")
            edits = sg.spec_edits(root, ["a.contract.md", "docs/prd.md"])
            self.assertIn("a.contract.md", edits)
            self.assertNotIn("docs/prd.md", edits)      # not in the custom list


class TraceTests(unittest.TestCase):
    """AC4: an edited spec doc the story never references is untraced; matching is PER FILE."""

    def test_untraced_spec_edit_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            story = ("## Acceptance Criteria\n\n### AC1: add a retry to the client\n"
                     "- **Then** the client retries\n")           # no spec reference at all
            res = sg.check(root, ["docs/prd.md", "src/client.py"], story)
            self.assertEqual(res["spec_edits"], ["docs/prd.md"])
            self.assertEqual(res["untraced_files"], ["docs/prd.md"])
            self.assertTrue(res["untraced"])                       # -> blocking finding for critic

    def test_referenced_spec_edit_is_not_untraced(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            story = ("## Acceptance Criteria\n\n### AC1: correct the rule in docs/prd.md\n"
                     "- **Then** docs/prd.md states the real quiet-hours rule\n")
            res = sg.check(root, ["docs/prd.md"], story)
            self.assertEqual(res["referenced_files"], ["docs/prd.md"])
            self.assertFalse(res["untraced"])                      # story references THIS file

    def test_cite_file_a_edit_file_b_is_untraced(self) -> None:
        # The MAJOR under-flag: an edit to trd.md must NOT ride on an AC that cites prd.md.
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            story = ("## Acceptance Criteria\n\n### AC1: correct the rule in docs/prd.md\n"
                     "- **Then** docs/prd.md is right\n")
            res = sg.check(root, ["docs/trd.md"], story)          # edited a DIFFERENT spec
            self.assertEqual(res["untraced_files"], ["docs/trd.md"])
            self.assertTrue(res["untraced"])

    def test_affects_mention_of_other_spec_does_not_trace_the_edit(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            story = ("> **Affects:** requirements/api.md\n\n## Acceptance Criteria\n\n"
                     "### AC1: an unrelated code change\n- **Then** x\n")
            res = sg.check(root, ["specs/design.md"], story)      # edited spec not in Affects
            self.assertTrue(res["untraced"])
            self.assertEqual(res["untraced_files"], ["specs/design.md"])

    def test_mixed_one_referenced_one_untraced(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            story = "## Acceptance Criteria\n\n### AC1: update docs/prd.md\n- **Then** ok\n"
            res = sg.check(root, ["docs/prd.md", "docs/trd.md"], story)
            self.assertEqual(res["referenced_files"], ["docs/prd.md"])
            self.assertEqual(res["untraced_files"], ["docs/trd.md"])
            self.assertTrue(res["untraced"])                       # any untraced -> flagged

    def test_no_spec_edit_is_never_untraced(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            res = sg.check(root, ["src/app.py"], "## Acceptance Criteria\n\n### AC1: x\n")
            self.assertEqual(res["spec_edits"], [])
            self.assertFalse(res["untraced"])

    def test_untraced_dormant_under_v2(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), v3=False)
            res = sg.check(root, ["docs/prd.md"], "no spec ref")
            self.assertFalse(res["untraced"])                      # gate dormant on v2


if __name__ == "__main__":
    unittest.main()
