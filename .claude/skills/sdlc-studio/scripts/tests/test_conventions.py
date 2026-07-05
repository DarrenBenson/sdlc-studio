"""Unit tests for lib/conventions.py - the tolerant convention layer (RFC-0023).

Policy under test (D0010): config-declared conventions are primary; normalised
matching only where a synonym is unambiguous; an unconfigured project behaves
identically to v3.4.0; a wrong-shaped conventions block fails loud, never guesses.
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from lib import conventions  # noqa: E402


def _yaml_available() -> bool:
    try:
        import yaml  # noqa: F401
        return True
    except ImportError:
        return False


def _repo(d: Path, config: str | None = None) -> Path:
    (d / "sdlc-studio").mkdir(parents=True, exist_ok=True)
    if config is not None:
        (d / "sdlc-studio" / ".config.yaml").write_text(config, encoding="utf-8")
    return d


class DefaultsTests(unittest.TestCase):
    """Config-absent: every knob reads today's literal behaviour."""

    def test_companion_suffixes_default(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(conventions.companion_suffixes(_repo(Path(d))),
                             ["consultations"])

    def test_status_aliases_default_empty(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(conventions.status_aliases(_repo(Path(d))), [])

    def test_template_for_default_none(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(conventions.template_for("bug", _repo(Path(d))))


class IsArtifactTests(unittest.TestCase):
    """Header-based companion detection: an artifact carries a Status line or
    an `# <ID>:` title block; a companion/note carries neither."""

    def test_status_line_is_artifact(self):
        self.assertTrue(conventions.is_artifact(
            "# EP0244: workerbot model ladder policy\n\n> **Status:** Draft\n"))

    def test_id_title_block_alone_is_artifact(self):
        # a malformed real artifact (title, Status line lost) must still count,
        # so validate keeps flagging its missing Status rather than skipping it
        self.assertTrue(conventions.is_artifact("# CR-0042: rework the gate\n\nprose\n"))

    def test_statusless_companion_is_not(self):
        self.assertFalse(conventions.is_artifact(
            "# EP0244 workerbot ladder - frozen design decisions\n\n"
            "1. The ladder stays three-tier.\n"))

    def test_prose_note_is_not(self):
        self.assertFalse(conventions.is_artifact("Some consultation notes.\n"))


class SectionPresentTests(unittest.TestCase):
    """Bug-readiness vocabularies: unambiguous synonyms match by normalised
    word-set; word order and parentheticals never matter; containment never counts."""

    HOUSE = ("# BG1: x\n\n## Symptom\n\nwrong colour\n\n## Root cause\n\nbad map\n\n"
             "## Fix (proposed)\n\nremap\n\n## Verify\n\ntest\n")
    SKILL = ("# BG2: y\n\n## Steps to Reproduce\n\n1. go\n\n## Proposed Fix\n\npatch\n")
    EMPTY = "# BG3: z\n\n## Summary\n\nbroken\n"

    def test_skill_template_still_ready(self):
        self.assertTrue(conventions.section_present(self.SKILL, "repro"))
        self.assertTrue(conventions.section_present(self.SKILL, "fix"))

    def test_house_template_ready_by_default(self):
        self.assertTrue(conventions.section_present(self.HOUSE, "repro"))
        self.assertTrue(conventions.section_present(self.HOUSE, "fix"))

    def test_word_order_insensitive(self):
        self.assertTrue(conventions.section_present(
            "## Fix (proposed)\n", "fix"))
        self.assertTrue(conventions.section_present(
            "## Proposed fix\n", "fix"))

    def test_containment_does_not_count(self):
        # 'Won't Fix rationale' contains the word fix; it is not a fix section
        self.assertFalse(conventions.section_present(
            "## Won't Fix rationale\n", "fix"))

    def test_negating_supersets_do_not_count(self):
        # blanket containment would mark both of these READY - a bug that
        # explicitly documents CANNOT-reproduce and NO-accepted-fix
        self.assertFalse(conventions.section_present(
            "## Unable to Reproduce - Steps Tried\n", "repro"))
        self.assertFalse(conventions.section_present(
            "## Won't Fix - Description\n", "fix"))

    def test_trailing_decoration_still_counts(self):
        # suffix tolerance is a PREFIX rule: entry words open the heading
        self.assertTrue(conventions.section_present(
            "## Steps to Reproduce the crash\n", "repro"))
        self.assertTrue(conventions.section_present(
            "## Proposed Fix for the mapper\n", "fix"))

    def test_empty_bug_not_ready(self):
        # strict bool contract (not merely falsy) - the value lands in JSON reports
        self.assertIs(conventions.section_present(self.EMPTY, "repro"), False)
        self.assertIs(conventions.section_present(self.EMPTY, "fix"), False)
        self.assertIs(conventions.section_present(self.SKILL, "fix"), True)

    def test_combo_requires_all_parts(self):
        self.assertFalse(conventions.section_present(
            "# B\n\n## Symptom\n\nonly the symptom\n", "repro"))

    def test_config_declared_vocabulary_wins(self):
        if not _yaml_available():
            self.skipTest("PyYAML absent")
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d),
                         "conventions:\n  bug_ready_sections:\n"
                         "    repro:\n      - Observed Behaviour\n")
            self.assertTrue(conventions.section_present(
                "## Observed Behaviour\n", "repro", repo_root=root))
            self.assertFalse(conventions.section_present(
                self.SKILL, "repro", repo_root=root))  # declared set replaces default


class ConfigDeclaredTests(unittest.TestCase):
    def test_extra_companion_suffix(self):
        if not _yaml_available():
            self.skipTest("PyYAML absent")
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d),
                         "conventions:\n  companion_suffixes:\n"
                         "    - consultations\n    - decisions\n")
            self.assertEqual(conventions.companion_suffixes(root),
                             ["consultations", "decisions"])

    def test_status_alias_declared(self):
        if not _yaml_available():
            self.skipTest("PyYAML absent")
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d),
                         "conventions:\n  status_column:\n    - Effective Status\n")
            self.assertEqual(conventions.status_aliases(root), ["effective status"])

    def test_template_override_declared(self):
        if not _yaml_available():
            self.skipTest("PyYAML absent")
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d),
                         "conventions:\n  templates:\n"
                         "    bug: sdlc-studio/templates/bug.md\n")
            got = conventions.template_for("bug", root)
            self.assertEqual(got, root / "sdlc-studio" / "templates" / "bug.md")


class FailLoudTests(unittest.TestCase):
    """A wrong-shaped conventions value raises ConventionsError - the layer
    never silently guesses what a project meant."""

    def test_suffixes_wrong_shape_raises(self):
        if not _yaml_available():
            self.skipTest("PyYAML absent")
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), "conventions:\n  companion_suffixes: decisions\n")
            with self.assertRaises(conventions.ConventionsError):
                conventions.companion_suffixes(root)

    def test_sections_wrong_shape_raises(self):
        if not _yaml_available():
            self.skipTest("PyYAML absent")
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), "conventions:\n  bug_ready_sections: 7\n")
            with self.assertRaises(conventions.ConventionsError):
                conventions.section_present("## x\n", "fix", repo_root=root)


if __name__ == "__main__":
    unittest.main()
