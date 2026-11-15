"""SECURITY.md: the Supported Versions table names the skill's current major.

The policy says support tracks the current major and is restated at each major release. This
test reads the current version from the skill's own SKILL.md frontmatter (through
tools/check_versions.py, the version-consistency checker) rather than hard-coding a major, so
the next major release cannot leave the table stale: the first row must name the current major
as supported, the row below it the previous major as security fixes only, and the last row
everything older as unsupported. Each check runs on the live page and on planted tables beside
it.
"""
# test-census-subject: SECURITY.md
from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PAGE = REPO / "SECURITY.md"

_spec = importlib.util.spec_from_file_location(
    "check_versions", REPO / "tools" / "check_versions.py")
assert _spec and _spec.loader
check_versions = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("check_versions", check_versions)
_spec.loader.exec_module(check_versions)

def current_version(root: Path = REPO) -> str | None:
    """The skill's current version, from its SKILL.md frontmatter under ``root``."""
    return check_versions.from_skill_md(root)


_ROW = re.compile(r"^\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$")


def support_rows(text: str) -> list[tuple[str, str]]:
    """The (version, supported) rows of the Supported Versions table, header excluded."""
    m = re.search(r"^## Supported Versions\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return []
    rows = [r.groups() for r in map(_ROW.match, m.group(1).splitlines()) if r]
    return [(v, s) for v, s in rows[1:] if not set(v) <= set("- :")]


def problems(text: str, version: str) -> list[str]:
    """Each way the table disagrees with ``version``; empty when it states it."""
    major = int(version.split(".", 1)[0])
    want = [(f"{major}.x", "Yes"), (f"{major - 1}.x", "Security fixes only"),
            (f"< {major - 1}.0", "No")]
    rows = support_rows(text)
    if len(rows) != len(want):
        return [f"table has {len(rows)} rows, want {len(want)}: {rows}"]
    return [f"row {i + 1} is {got}, want {exp}"
            for i, (got, exp) in enumerate(zip(rows, want)) if got != exp]


def _table(*rows: tuple[str, str]) -> str:
    body = "\n".join(f"| {v} | {s} |" for v, s in rows)
    return ("# Security Policy\n\n## Supported Versions\n\nSupport tracks the current major.\n\n"
            f"| Version | Supported |\n| --- | --- |\n{body}\n\n## Reporting\n\n| a | b |\n")


class LivePolicyTests(unittest.TestCase):
    def test_current_version_is_read_from_the_skill(self):
        self.assertRegex(current_version() or "", r"^\d+\.\d+\.\d+")
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / check_versions.SKILL_DIR
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                '---\nname: x\nmetadata:\n  version: "7.1.0"\n---\n\n# X\n', encoding="utf-8")
            self.assertEqual(current_version(Path(tmp)), "7.1.0")

    def test_table_names_the_skills_current_major(self):
        version = current_version()
        self.assertEqual(problems(PAGE.read_text(encoding="utf-8"), version), [])


class PlantedTableTests(unittest.TestCase):
    """The check refuses a stale table and passes a current one, for any major."""

    def test_a_current_table_passes(self):
        text = _table(("6.x", "Yes"), ("5.x", "Security fixes only"), ("< 5.0", "No"))
        self.assertEqual(problems(text, "6.3.0"), [])
        self.assertEqual(support_rows(text)[0], ("6.x", "Yes"))

    def test_an_older_major_named_current_is_refused(self):
        text = _table(("4.x", "Yes"), ("3.x", "Security fixes only"), ("< 3.0", "No"))
        self.assertTrue(problems(text, "6.3.0"))

    def test_the_table_follows_the_next_major(self):
        text = _table(("6.x", "Yes"), ("5.x", "Security fixes only"), ("< 5.0", "No"))
        self.assertTrue(problems(text, "7.0.0"))
        later = _table(("7.x", "Yes"), ("6.x", "Security fixes only"), ("< 6.0", "No"))
        self.assertEqual(problems(later, "7.0.0-rc.1"), [])

    def test_a_wrong_previous_major_row_is_refused(self):
        text = _table(("6.x", "Yes"), ("4.x", "Security fixes only"), ("< 4.0", "No"))
        self.assertTrue(problems(text, "6.3.0"))
        swapped = _table(("6.x", "Yes"), ("5.x", "Yes"), ("< 5.0", "No"))
        self.assertTrue(problems(swapped, "6.3.0"))

    def test_a_missing_table_is_refused(self):
        self.assertEqual(support_rows("# Security Policy\n\n## Reporting\n"), [])
        self.assertTrue(problems("# Security Policy\n", "6.3.0"))


if __name__ == "__main__":
    unittest.main()
