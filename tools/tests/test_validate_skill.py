"""Unit tests for tools/validate_skill.py (frontmatter spec validator).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

# tools/ lives at the repo root, six parents up from this test file.
TOOLS = Path(__file__).resolve().parents[1] / "validate_skill.py"
_spec = importlib.util.spec_from_file_location("validate_skill", TOOLS)
assert _spec and _spec.loader
validate_skill = importlib.util.module_from_spec(_spec)
sys.modules["validate_skill"] = validate_skill
_spec.loader.exec_module(validate_skill)

VALID = """\
---
name: my-skill
description: "Does a thing. Use when asked about things."
license: MIT
metadata:
  version: "2.0.0"
allowed-tools: Read, Bash
---

# Body
"""


def _skill_dir(parent: Path, name: str, skill_md: str) -> Path:
    d = parent / name
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(skill_md, encoding="utf-8")
    return d


class ParseTests(unittest.TestCase):
    def test_parses_flat_and_nested_fields(self) -> None:
        fields = validate_skill.parse_frontmatter(VALID)
        self.assertEqual(fields["name"], "my-skill")
        self.assertEqual(fields["metadata"], {"version": "2.0.0"})

    def test_no_frontmatter_returns_none(self) -> None:
        self.assertIsNone(validate_skill.parse_frontmatter("# Just a heading\n"))

    def test_unterminated_block_returns_none(self) -> None:
        self.assertIsNone(validate_skill.parse_frontmatter("---\nname: x\n"))


class ValidateTests(unittest.TestCase):
    def test_valid_skill_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _skill_dir(Path(d), "my-skill", VALID)
            self.assertEqual(validate_skill.validate(root), [])

    def test_name_directory_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _skill_dir(Path(d), "other-dir", VALID)
            errors = validate_skill.validate(root)
            self.assertTrue(any("does not match directory" in e for e in errors))

    def test_bad_name_pattern_fails(self) -> None:
        bad = VALID.replace("name: my-skill", "name: My_Skill")
        with tempfile.TemporaryDirectory() as d:
            root = _skill_dir(Path(d), "My_Skill", bad)
            errors = validate_skill.validate(root)
            self.assertTrue(any("fails" in e for e in errors))

    def test_missing_description_fails(self) -> None:
        bad = VALID.replace('description: "Does a thing. Use when asked about things."\n', "")
        with tempfile.TemporaryDirectory() as d:
            root = _skill_dir(Path(d), "my-skill", bad)
            errors = validate_skill.validate(root)
            self.assertTrue(any(e.startswith("description: missing") for e in errors))

    def test_overlong_description_fails(self) -> None:
        bad = VALID.replace("Does a thing. Use when asked about things.", "x" * 1100)
        with tempfile.TemporaryDirectory() as d:
            root = _skill_dir(Path(d), "my-skill", bad)
            errors = validate_skill.validate(root)
            self.assertTrue(any("exceeds 1024" in e for e in errors))

    def test_claude_extension_field_fails_strict_spec(self) -> None:
        # skills-ref rejects any field outside the spec's closed set; tool
        # extensions like argument-hint belong under metadata:.
        bad = VALID.replace("license: MIT", 'license: MIT\nargument-hint: "[x]"')
        with tempfile.TemporaryDirectory() as d:
            root = _skill_dir(Path(d), "my-skill", bad)
            errors = validate_skill.validate(root)
            self.assertTrue(any("argument-hint" in e for e in errors))

    def test_unknown_field_fails(self) -> None:
        bad = VALID.replace("license: MIT", "license: MIT\nbanana: yes")
        with tempfile.TemporaryDirectory() as d:
            root = _skill_dir(Path(d), "my-skill", bad)
            errors = validate_skill.validate(root)
            self.assertTrue(any("unknown frontmatter field: banana" in e for e in errors))

    def test_non_semver_version_fails(self) -> None:
        bad = VALID.replace('version: "2.0.0"', 'version: "2.0"')
        with tempfile.TemporaryDirectory() as d:
            root = _skill_dir(Path(d), "my-skill", bad)
            errors = validate_skill.validate(root)
            self.assertTrue(any("not X.Y.Z semver" in e for e in errors))

    def test_real_skill_passes(self) -> None:
        repo_skill = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "sdlc-studio"
        self.assertEqual(validate_skill.validate(repo_skill), [])


if __name__ == "__main__":
    unittest.main()
