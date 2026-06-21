"""Unit tests for doc_coverage.py - the documentation-coverage check (CR0053)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "doc_coverage.py"


def _load():
    spec = importlib.util.spec_from_file_location("doc_coverage", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["doc_coverage"] = mod
    spec.loader.exec_module(mod)
    return mod


dc = _load()


def _skill(repo: Path, *, type_ref_cmds=("foo",), help_cmds=("foo",),
           scripts=("foo",), ref_scripts=("foo",), changelog="- a change\n") -> None:
    sd = repo / ".claude" / "skills" / "sdlc-studio"
    (sd / "help").mkdir(parents=True, exist_ok=True)
    (sd / "scripts").mkdir(parents=True, exist_ok=True)
    rows = "\n".join(f"| `{c}` | desc |" for c in type_ref_cmds)
    (sd / "SKILL.md").write_text(
        f"# SKILL\n\n## Type Reference\n\n| Type | Description |\n| --- | --- |\n{rows}\n\n"
        "## Full Reference\n\nx\n", encoding="utf-8")
    (sd / "help" / "help.md").write_text(
        "# help\n\n## All Commands\n\n" + "\n".join(f"| `/sdlc-studio {c}` | d |" for c in help_cmds) + "\n",
        encoding="utf-8")
    (sd / "reference-scripts.md").write_text(
        "# scripts\n\n" + "\n".join(f"### `{s}.py`\n\ndesc\n" for s in ref_scripts), encoding="utf-8")
    for s in scripts:
        (sd / "scripts" / f"{s}.py").write_text("x = 1\n", encoding="utf-8")
    # decoys that must be ignored
    (sd / "scripts" / "test_foo.py").write_text("x = 1\n", encoding="utf-8")
    (sd / "scripts" / "__init__.py").write_text("", encoding="utf-8")
    if changelog is not None:
        (repo / "CHANGELOG.md").write_text(f"# CL\n\n## [Unreleased]\n\n{changelog}\n## [1.0.0] - x\n", encoding="utf-8")


class DocCoverageTests(unittest.TestCase):
    def test_all_covered_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d))
            r = dc.check(d)
            self.assertTrue(r["ok"] and r["applicable"])
            self.assertEqual(r["findings"], [])

    def test_command_not_in_catalogue_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), type_ref_cmds=("foo", "bar"), help_cmds=("foo",))  # bar missing
            r = dc.check(d)
            self.assertFalse(r["ok"])
            self.assertEqual([f["name"] for f in r["findings"] if f["kind"] == "command-uncatalogued"], ["bar"])

    def test_script_not_in_reference_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), scripts=("foo", "baz"), ref_scripts=("foo",))  # baz undocumented
            r = dc.check(d)
            self.assertFalse(r["ok"])
            self.assertIn("baz", [f["name"] for f in r["findings"] if f["kind"] == "script-undocumented"])

    def test_test_and_init_scripts_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d))  # creates test_foo.py + __init__.py decoys
            names = [f["name"] for f in dc.check(d)["findings"]]
            self.assertNotIn("test_foo", names)
            self.assertNotIn("__init__", names)

    def test_changelog_empty_is_advisory(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), changelog="")  # empty [Unreleased]
            r = dc.check(d)
            self.assertTrue(r["ok"])  # advisory only - does not block
            self.assertTrue(any(f["kind"] == "changelog-empty" and not f["blocking"] for f in r["findings"]))


    def test_prose_backtick_not_catalogued(self) -> None:
        # HIGH regression: a command present only as a prose `cmd` mention (no /sdlc-studio
        # cmd catalogue row) must FAIL, not be falsely marked documented.
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), type_ref_cmds=("foo",), help_cmds=())  # no /sdlc-studio foo row
            hp = Path(d) / ".claude" / "skills" / "sdlc-studio" / "help" / "help.md"
            hp.write_text(hp.read_text() + "\nUse the `foo` thing (prose only).\n", encoding="utf-8")
            r = dc.check(d)
            self.assertFalse(r["ok"])
            self.assertIn("foo", [f["name"] for f in r["findings"] if f["kind"] == "command-uncatalogued"])

    def test_non_skill_repo_is_no_op(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            r = dc.check(d)  # no .claude/skills/sdlc-studio/SKILL.md
            self.assertTrue(r["ok"])
            self.assertFalse(r["applicable"])


if __name__ == "__main__":
    unittest.main()
