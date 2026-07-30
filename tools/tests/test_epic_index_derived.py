"""The committed epic index holds derived data, over EVERY row (US0477 AC5).

A fixture cannot show this. The sweep runs over the shipped `sdlc-studio/epics/_index.md`, and the
point of doing it here rather than in a fixture is that a real index accumulates states nobody
would think to write: 182 rows that had never been filled, 157 epics with no `## Dependencies`
section at all, and eight rows claiming a count the census falls short of.

Repo-only, like every other workspace-state check under `tools/tests/`.

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
INDEX = REPO / "sdlc-studio" / "epics" / "_index.md"


def _mod(name: str):
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


reconcile = _mod("reconcile")
sdlc_md = reconcile.sdlc_md

#: The rows whose count the census FALLS SHORT of, pinned with both numbers.
#:
#: WHY they are held, corrected after an independent review falsified the first explanation. It is
#: NOT that their story files were deleted: `git log --diff-filter=DR` over `sdlc-studio/stories/`
#: shows no story file has ever been deleted or renamed. Each of these six numbers equals its
#: epic's `**Estimated Story Count:**` and the count of its unlinked `- [x] US:` breakdown stubs,
#: which EP0001's own file documents as "early placeholder stubs from before stories were
#: individually tracked - complete in the implementation, not as separate story artefacts". So the
#: row records an ESTIMATE from before individual tracking, not a count of files. The hold is right;
#: the reason first written for it was wrong, in this comment and in three other places.
#:
#: EP0005, EP0007 and EP0008 were in this set and should never have been. They were held because
#: the census could not read the `> **Epic:** [EP0008: Title](../epics/...)` link form that the
#: shipped story template writes and 34 story files here use. EP0008's row was written as `7`
#: against a true count of 18 - a wrong number committed to the tracked index, justified by a
#: census that could not see two thirds of the evidence.
UNCORROBORATED = {
    "EP0001.Stories": ("6", "0"), "EP0002.Stories": ("4", "0"), "EP0003.Stories": ("4", "0"),
    "EP0004.Stories": ("4", "0"), "EP0006.Stories": ("4", "1"), "EP0009.Stories": ("5", "0"),
}


class EpicIndexRepoTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = INDEX.read_text(encoding="utf-8")
        cls.rows = [l for l in cls.text.splitlines() if reconcile._EPIC_ROW_RE.match(l)]

    def test_every_row_is_derived_and_a_mutated_row_fails(self) -> None:
        """AC5, over all rows and shown able to go red.

        The negative control is the half that makes this mean anything: a sweep that silently
        matched nothing would satisfy the first assertion exactly as a clean tree does. So one
        row's Stories cell is mutated in a copy of the tree and the sweep must find it.
        """
        self.assertGreater(len(self.rows), 150, "the index parsed to almost nothing")
        self.assertEqual([], reconcile.epic_index_derivable_drift(REPO),
                         "a derivable epic index cell is unfilled in the committed tree")

        # ...and it can go red. Mutate one cell in a COPY of the tree (never the live index) and
        # assert the sweep reports that row and no other.
        import shutil
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            copy = Path(d)
            (copy / "sdlc-studio").mkdir()
            for sub in ("epics", "stories"):
                shutil.copytree(REPO / "sdlc-studio" / sub, copy / "sdlc-studio" / sub)
            target = copy / "sdlc-studio" / "epics" / "_index.md"
            text = target.read_text(encoding="utf-8")
            # A row whose cell is a real derived count, so blanking it creates a placeholder.
            victim = next(l for l in text.splitlines()
                          if reconcile._EPIC_ROW_RE.match(l)
                          and reconcile._split_row_cells(l)[3].isdigit()
                          and f"{reconcile._EPIC_ROW_RE.match(l).group(1)}.Stories"
                          not in UNCORROBORATED)
            rec = reconcile._EPIC_ROW_RE.match(victim).group(1)
            cells = reconcile._split_row_cells(victim)
            cells[3] = sdlc_md.CELL_NOT_STATED
            target.write_text(text.replace(victim, "| " + " | ".join(cells) + " |", 1),
                              encoding="utf-8")
            found = reconcile.epic_index_derivable_drift(copy)
        self.assertEqual([(rec, "Stories")], [(f["id"], f["column"]) for f in found],
                         f"the mutated {rec} row was not reported, so a clean result above is "
                         f"equally consistent with a sweep that reads nothing")

    def test_every_epic_with_stories_on_disk_shows_its_censused_count(self) -> None:
        """Read from the census rather than from the detector, so this cannot agree with the code
        under test by construction."""
        checked = 0
        for line in self.rows:
            rec = reconcile._EPIC_ROW_RE.match(line).group(1)
            cells = reconcile._split_row_cells(line)
            key = f"{rec}.Stories"
            if key in UNCORROBORATED:
                continue
            census = str(sdlc_md.epic_story_count(REPO, rec))
            self.assertEqual(census, cells[3],
                             f"{rec} row says `{cells[3]}`, the story census counts {census}")
            checked += 1
        self.assertGreater(checked, 150, f"only {checked} rows were actually compared")

    def test_no_epic_lacking_a_dependencies_section_has_an_invented_Deps_cell(self) -> None:
        """The 157-row state. A Deps cell written from an absent section is a declaration the epic
        never made, and it would be indistinguishable from one it did."""
        absent = written = 0
        for line in self.rows:
            rec = reconcile._EPIC_ROW_RE.match(line).group(1)
            cells = reconcile._split_row_cells(line)
            if sdlc_md.epic_declared_deps(REPO, rec) is not None:
                continue
            absent += 1
            if cells[4] not in (sdlc_md.CELL_NOT_STATED, "-", "", "–", "—"):
                written += 1
        self.assertGreater(absent, 100,
                           "the no-section state is the majority of this repository's epics and is "
                           "the one a two-state implementation corrupts")
        self.assertEqual(0, written,
                         f"{written} row(s) carry a Deps value for an epic that declares no "
                         f"Dependencies section")

    def test_the_uncorroborated_rows_are_ADVISORY_and_untouched(self) -> None:
        """Eight rows whose count the census falls short of. They are reported, never rewritten,
        and never counted as drift - a blocking lane that can only be cleared by destroying a
        record is a lane that gets switched off."""
        advisory = {f"{a['id']}.{a['column']}": (a["current"], a["expected"])
                    for a in reconcile.epic_index_uncorroborated_advisory(REPO)}
        self.assertEqual(UNCORROBORATED, advisory,
                         "the uncorroborated set changed - update it deliberately, by hand")
        drift_ids = {f"{d['id']}.{d['column']}" for d in reconcile.epic_index_derivable_drift(REPO)}
        self.assertEqual(set(), drift_ids & set(UNCORROBORATED),
                         "an uncorroborated row was also reported as mechanical drift")
        for a in reconcile.epic_index_uncorroborated_advisory(REPO):
            with self.subTest(row=a["id"]):
                self.assertIn("left alone", a["note"])

    def test_the_kind_is_registered_and_carries_a_remediation_hint(self) -> None:
        self.assertIn("epic-index-derivable", reconcile.DRIFT_KINDS)
        hint = sdlc_md.REMEDIATION["reconcile"]["epic-index-derivable"]
        self.assertIn("PLACEHOLDER", hint)
        self.assertIn("left alone", hint,
                      "the hint must say that a contradicted value is held, not rewritten")

    def test_the_index_header_matches_the_canonical_column_definition(self) -> None:
        header = next(l for l in self.text.splitlines() if l.startswith("| ID |"))
        live = tuple(c.strip() for c in re.split(r"(?<!\\)\|", header.strip().strip("|")))
        self.assertEqual(sdlc_md.EPIC_INDEX_COLUMNS, live)


if __name__ == "__main__":
    unittest.main()
