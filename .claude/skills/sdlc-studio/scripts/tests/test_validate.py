"""Unit tests for validate.py.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "validate.py"
_spec = importlib.util.spec_from_file_location("validate", SCRIPT_PATH)
assert _spec and _spec.loader
validate = importlib.util.module_from_spec(_spec)
sys.modules["validate"] = validate
_spec.loader.exec_module(validate)

GOOD_STORY = "# Login\n\n> **Status:** Done\n\n### AC1: Happy\n- **Verify:** file a.py\n"


def _write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


class ValidateFileTests(unittest.TestCase):
    def test_good_story_has_no_violations(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0001-login.md", GOOD_STORY)
            self.assertEqual(validate.validate_file(p, "story"), [])

    def test_bad_status_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0002-x.md",
                       "# X\n\n> **Status:** Frozen\n\n### AC1: y\n- **Verify:** file b\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertIn("status-vocab", rules)

    def test_missing_status_and_title(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0003-x.md", "no heading, no status\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertIn("no-status", rules)
            self.assertIn("no-title", rules)

    def test_story_without_ac_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0004-x.md",
                       "# X\n\n> **Status:** Draft\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertIn("no-ac", rules)

    def test_bad_id_format(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/login.md", GOOD_STORY)
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertIn("id-format", rules)

    def test_decorated_status_accepted(self) -> None:
        # `Done (v2.66.0)` canonicalises to `Done` — not a status-vocab error.
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0005-x.md",
                       "# X\n\n> **Status:** Done (v2.66.0)\n\n### AC1: y\n- **Verify:** file b\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertNotIn("status-vocab", rules)

    def test_bold_bullet_ac_accepted(self) -> None:
        # `- **AC1:**` compact bullet style satisfies the AC requirement.
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0006-x.md",
                       "# X\n\n> **Status:** Draft\n\n- **AC1:** login works\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertNotIn("no-ac", rules)

    def test_plain_ac_section_accepted(self) -> None:
        # A populated `## Acceptance Criteria` section (plain bullets, no ACn
        # ids) satisfies the AC requirement.
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0007-x.md",
                       "# X\n\n> **Status:** Draft\n\n## Acceptance Criteria\n\n- user can log in\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertNotIn("no-ac", rules)

    def test_empty_ac_section_still_flagged(self) -> None:
        # An AC heading with no content before the next heading is still no-ac.
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0008-x.md",
                       "# X\n\n> **Status:** Draft\n\n## Acceptance Criteria\n\n## Notes\n- something\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertIn("no-ac", rules)


class InferTypeTests(unittest.TestCase):
    def test_infer_from_dir(self) -> None:
        self.assertEqual(validate.infer_type(Path("sdlc-studio/epics/EP0001-x.md")), "epic")

    def test_infer_from_id_prefix(self) -> None:
        self.assertEqual(validate.infer_type(Path("/tmp/CR-0001-x.md")), "cr")


class CheckCmdTests(unittest.TestCase):
    def test_check_exit_nonzero_on_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _write(Path(d), "sdlc-studio/stories/US0001-bad.md", "# X\n\n> **Status:** Frozen\n")
            rc = validate.main(["check", "--type", "story", "--root", d])
            self.assertEqual(rc, 1)

    def test_check_exit_zero_when_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _write(Path(d), "sdlc-studio/stories/US0001-login.md", GOOD_STORY)
            rc = validate.main(["check", "--type", "story", "--root", d])
            self.assertEqual(rc, 0)


GOOD_AGENTS = (
    "# Proj\n\n"
    "Read `reference-doctrine.md`. Read `sdlc-studio/reviews/LATEST.md` first.\n"
    "IMPORTANT pre-release gate: `/sdlc-studio reconcile --verify` + the review legs.\n"
    "After `/compact` or a reset, re-read LATEST.md and run status.\n"
)


class InstructionsTests(unittest.TestCase):
    def test_missing_agents_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            v = validate.check_instructions(Path(d))
            self.assertIn("no-agents", {x["rule"] for x in v})
            self.assertTrue(any(x["severity"] == "error" for x in v))

    def test_good_agents_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "AGENTS.md").write_text(GOOD_AGENTS, encoding="utf-8")
            (root / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
            self.assertEqual(validate.check_instructions(root), [])

    def test_claude_not_pointer_warns(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "AGENTS.md").write_text(GOOD_AGENTS, encoding="utf-8")
            (root / "CLAUDE.md").write_text("# full instructions inline\n", encoding="utf-8")
            self.assertIn("claude-not-pointer", {x["rule"] for x in validate.check_instructions(root)})

    def test_missing_elements_warn(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "AGENTS.md").write_text("# Proj\n\nNothing useful here.\n", encoding="utf-8")
            rules = {x["rule"] for x in validate.check_instructions(root)}
            self.assertIn("no-doctrine-pointer", rules)
            self.assertIn("no-latest-pointer", rules)
            self.assertIn("no-release-gate", rules)
            self.assertIn("no-compaction-rule", rules)

    def test_cmd_exit_nonzero_when_no_agents(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(validate.main(["instructions", "--root", d]), 1)

    def test_cmd_exit_zero_when_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "AGENTS.md").write_text(GOOD_AGENTS, encoding="utf-8")
            self.assertEqual(validate.main(["instructions", "--root", d]), 0)


if __name__ == "__main__":
    unittest.main()
