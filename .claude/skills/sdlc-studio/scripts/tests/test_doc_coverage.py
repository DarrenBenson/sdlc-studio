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


class HelpPageCoverageTests(unittest.TestCase):
    """A Type Reference command with no help page is a gap, and a waiver is CHECKED.

    Derived from the Type Reference rather than a hand-kept list of pages: a command added
    there without a page is exactly the gap this catches, and a second list would drift.
    """

    SKILL = Path(__file__).resolve().parents[1].parent

    def _mod(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "doc_coverage", Path(__file__).resolve().parent.parent / "doc_coverage.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["doc_coverage"] = mod
        spec.loader.exec_module(mod)
        return mod

    def test_refine_page_ships_in_invocation_form_and_is_not_waived(self) -> None:
        """MUTANT: delete help/refine.md, or waive it instead of writing it.

        `refine` is the command that MINTS ungroomed work, so the page an author lands on when
        they meet a grooming marker is the one that must exist.
        """
        mod = self._mod()
        page = self.SKILL / "help" / "refine.md"
        self.assertTrue(page.is_file(), "help/refine.md does not ship")
        self.assertNotIn("refine", mod.HELP_PAGE_WAIVERS,
                         "refine is waived rather than documented")
        body = page.read_text(encoding="utf-8")
        self.assertIn("/sdlc-studio refine", body,
                      "the page never states its invocation form")
        self.assertIn("not** priced by the story's points", body.replace("*", "*"),
                      "the page does not state that grooming is unpriced work")

    def test_missing_page_stale_waiver_and_unreadable_tree_all_fail_loud(self) -> None:
        """MUTANT: return [] on any of the three.

        All three are asserted, because each is a different way for the check to report clean
        over nothing - and a silent pass is what let a missing page ship in the first place.
        """
        mod = self._mod()
        with tempfile.TemporaryDirectory() as d:
            skill = Path(d) / "skill"
            (skill / "help").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "## Type Reference\n\n| `ghost` | a command |\n\n## Full Reference\n",
                encoding="utf-8")
            missing = mod.help_page_findings(skill)
            self.assertTrue(missing, "a command with no page reported clean")
            self.assertIn("ghost", missing[0]["detail"])

            # A STALE waiver: the page exists, so the waiver hides nothing.
            (skill / "help" / "ghost.md").write_text("# ghost\n", encoding="utf-8")
            mod.HELP_PAGE_WAIVERS["ghost"] = "temporarily"
            try:
                stale = mod.help_page_findings(skill)
            finally:
                del mod.HELP_PAGE_WAIVERS["ghost"]
            self.assertTrue(any("STALE" in f["detail"] for f in stale),
                            "a waiver for a command that now has a page reported clean")

        # An UNREADABLE tree must report the failure, never a clean pass.
        gone = mod.help_page_findings(Path("/nonexistent-skill-tree"))
        self.assertTrue(gone, "an unreadable tree reported clean")


class ProgressiveLoadingGuideTests(unittest.TestCase):
    """The guide routes a grooming author to files that exist."""

    SKILL = Path(__file__).resolve().parents[1].parent

    def test_grooming_row_exists_and_its_paths_resolve(self) -> None:
        """MUTANT: drop the grooming row, or point it at a file that is not there.

        An author meets the ungroomed marker and needs the SHAPE and the verifier guidance; a
        row naming a missing file sends them nowhere, which is worse than no row.
        """
        text = (self.SKILL / "SKILL.md").read_text(encoding="utf-8")
        rows = [ln for ln in text.splitlines()
                if ln.startswith("|") and "rooming a refined story" in ln]
        self.assertEqual(1, len(rows), "the guide has no grooming row")
        cells = [c.strip().strip("`") for c in rows[0].strip("|").split("|")]
        targets = [c for c in cells[1:] if c and c != "-"]
        self.assertTrue(targets, "the grooming row names no files")
        for target in targets:
            with self.subTest(target=target):
                self.assertTrue((self.SKILL / target).is_file(),
                                f"the grooming row routes to {target}, which does not exist")


if __name__ == "__main__":
    unittest.main()
