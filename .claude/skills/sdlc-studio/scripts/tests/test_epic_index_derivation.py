"""The canonical epic-index columns and the cells derived from the tree (US0477 foundation).

Two consulted their own idea of what an epic row is: the shipped `templates/indexes/epic.md`
declared `Owner`/`Target` while every one of this repository's 191 live rows carries
`Deps`/`Created`/`Updated`. One importable answer now, so the derivation and the row writer cannot
disagree about the shape of a row.

The `Deps` cell has THREE states and the third is the point: "nobody said" is not "the epic says
there are none", and rewriting the first as the second invents a declaration.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

sdlc_md = loader.load_lib("sdlc_md") if hasattr(loader, "load_lib") else None
if sdlc_md is None:  # the loader exposes scripts; the shared library comes via one of them
    _mod = loader.load_script("readiness")
    sdlc_md = _mod.sdlc_md

REPO = Path(__file__).resolve().parents[5]


def _epic(root: Path, epic_id: str, deps_section: str | None) -> None:
    d = root / "sdlc-studio" / "epics"
    d.mkdir(parents=True, exist_ok=True)
    body = [f"# {epic_id}: an epic", "", "> **Status:** Ready", ""]
    if deps_section is not None:
        body += ["## Dependencies", "", "### Blocked By", "",
                 "| Dependency | Type | Status | Owner |", "| --- | --- | --- | --- |"]
        body += deps_section.splitlines()
    (d / f"{epic_id}-x.md").write_text("\n".join(body) + "\n", encoding="utf-8")


def _story(root: Path, story_id: str, epic_id: str) -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{story_id}-x.md").write_text(
        f"# {story_id}: a story\n\n> **Status:** Ready\n> **Epic:** {epic_id}\n",
        encoding="utf-8")


class CanonicalColumnsTests(unittest.TestCase):

    def test_the_derived_columns_are_a_subset_of_the_canonical_ones(self) -> None:
        """MUTANT: name a derived column the row does not have. The writer would then produce a
        cell with nowhere to go, silently dropped."""
        self.assertTrue(set(sdlc_md.EPIC_DERIVED_COLUMNS) <= set(sdlc_md.EPIC_INDEX_COLUMNS),
                        f"{sdlc_md.EPIC_DERIVED_COLUMNS} is not within "
                        f"{sdlc_md.EPIC_INDEX_COLUMNS}")

    def test_the_canonical_columns_match_the_repositorys_live_index(self) -> None:
        """The 191 live rows are the evidence. If the constant and the file disagree, the constant
        is a claim about a shape nothing uses."""
        text = (REPO / "sdlc-studio" / "epics" / "_index.md").read_text(encoding="utf-8")
        header = next(l for l in text.splitlines() if l.startswith("| ID |"))
        live = tuple(c.strip() for c in header.strip().strip("|").split("|"))
        self.assertEqual(sdlc_md.EPIC_INDEX_COLUMNS, live,
                         "the canonical column definition disagrees with the shipped index")

    def test_not_stated_and_declared_none_are_DIFFERENT_values(self) -> None:
        """MUTANT: collapse the two. `--` means nobody said; `None` means the epic declared it has
        no dependencies. One value for both facts turns an absence into a declaration."""
        self.assertNotEqual(sdlc_md.CELL_NOT_STATED, sdlc_md.DEPS_DECLARED_NONE)


class StoryCensusTests(unittest.TestCase):

    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="epicidx_"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def test_the_count_is_a_census_and_zero_is_an_answer(self) -> None:
        """AC1: zero is a DERIVED FACT, not a placeholder - so it is asserted as `"0"`, a value a
        row can carry, rather than as an absence."""
        _epic(self.root, "EP0001", None)
        for i in (1, 2, 3):
            _story(self.root, f"US000{i}", "EP0001")
        self.assertEqual(3, sdlc_md.epic_story_count(self.root, "EP0001"))
        self.assertEqual("3", sdlc_md.derive_epic_row_cells(self.root, "EP0001")["Stories"])

        _epic(self.root, "EP0002", None)
        self.assertEqual(0, sdlc_md.epic_story_count(self.root, "EP0002"))
        self.assertEqual("0", sdlc_md.derive_epic_row_cells(self.root, "EP0002")["Stories"],
                         "an epic with no stories must derive the string '0', not an absence")

    def test_a_story_naming_ANOTHER_epic_is_not_counted(self) -> None:
        """MUTANT: count every story file. Without this the census is just a directory listing."""
        _epic(self.root, "EP0001", None)
        _story(self.root, "US0001", "EP0001")
        _story(self.root, "US0002", "EP0999")
        self.assertEqual(1, sdlc_md.epic_story_count(self.root, "EP0001"))

    def test_the_index_file_is_not_counted_as_a_story(self) -> None:
        _epic(self.root, "EP0001", None)
        _story(self.root, "US0001", "EP0001")
        (self.root / "sdlc-studio" / "stories" / "_index.md").write_text(
            "# Index\n\n> **Epic:** EP0001\n", encoding="utf-8")
        self.assertEqual(1, sdlc_md.epic_story_count(self.root, "EP0001"))


class DepsThreeStatesTests(unittest.TestCase):

    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="epicdeps_"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def test_named_dependencies_come_back_in_FILE_ORDER(self) -> None:
        """MUTANT: sort them. File order is what the epic's author chose, and a sorted list is a
        different claim about sequence."""
        _epic(self.root, "EP0010",
              "| EP0009 | Epic | Done | X |\n| EP0002 | Epic | Done | X |")
        self.assertEqual(["EP0009", "EP0002"], sdlc_md.epic_declared_deps(self.root, "EP0010"))
        self.assertEqual("EP0009, EP0002",
                         sdlc_md.derive_epic_row_cells(self.root, "EP0010")["Deps"])

    def test_a_declared_but_EMPTY_section_derives_the_declared_none_value(self) -> None:
        _epic(self.root, "EP0011", "")
        self.assertEqual([], sdlc_md.epic_declared_deps(self.root, "EP0011"))
        self.assertEqual(sdlc_md.DEPS_DECLARED_NONE,
                         sdlc_md.derive_epic_row_cells(self.root, "EP0011")["Deps"])

    def test_NO_section_at_all_yields_no_Deps_cell_to_write(self) -> None:
        """AC2's third state, and the reason `epic_declared_deps` returns None rather than [].

        MUTANT: return `[]` when the section is absent. The cell would then be written as the
        declared-none value, turning "nobody has said" into "the epic says there are none" across
        the 181 rows of this repository that state no Dependencies section at all.
        """
        _epic(self.root, "EP0012", None)
        self.assertIsNone(sdlc_md.epic_declared_deps(self.root, "EP0012"))
        cells = sdlc_md.derive_epic_row_cells(self.root, "EP0012")
        self.assertNotIn("Deps", cells,
                         "an epic with no Dependencies section produced a Deps cell, so a caller "
                         "would overwrite whatever is there with an invented declaration")
        self.assertIn("Stories", cells, "the Stories cell is still derivable")

    def test_an_unknown_epic_id_is_not_treated_as_declared_none(self) -> None:
        self.assertIsNone(sdlc_md.epic_declared_deps(self.root, "EP9999"))

    def test_all_three_states_are_present_in_the_LIVE_repository(self) -> None:
        """So the states are exercised against real data and not only fixtures. Measured, because
        the counts are what make the third state load-bearing here."""
        named = empty = absent = 0
        for path in sorted((REPO / "sdlc-studio" / "epics").glob("EP*.md")):
            rec = sdlc_md.extract_record_id(path.stem)
            if not rec:
                continue
            deps = sdlc_md.epic_declared_deps(REPO, rec)
            if deps is None:
                absent += 1
            elif deps:
                named += 1
            else:
                empty += 1
        self.assertGreater(absent, 100,
                           "the no-section state is the majority of this repository's epics, and "
                           "it is the one a two-state implementation would corrupt")
        self.assertGreater(named + empty, 0, "no epic declares a Dependencies section at all")


if __name__ == "__main__":
    unittest.main()
