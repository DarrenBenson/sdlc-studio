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


def _index_rows(repo: Path, type_: str) -> list[str]:
    """Every epic row in the corpus: the live index UNIONED with its `archive/**` sub-indexes.

    Reading only `_index.md` would make this sweep's population "whatever has not been archived
    yet", and `archive.py` is the maintenance step `reconcile detect` advises on every run once an
    index passes `indexes.archive_after`. Taking that advice moved 177 epic rows out of the live
    table and dropped the floors below to 30, reporting a corrupt index where there was none
    (BG0504). `reconcile.parse_index` performs exactly this union, and for the same reason.
    """
    rel = sdlc_md.ARTIFACT_TYPES[type_][0]
    paths = [repo / rel / "_index.md", *sorted((repo / rel / "archive").rglob("*.md"))]
    return [ln for p in paths if p.is_file()
            for ln in p.read_text(encoding="utf-8").splitlines()
            if reconcile._EPIC_ROW_RE.match(ln)]


def _index_rows_live(repo: Path) -> list[str]:
    """Only the live epic index - the table `reconcile apply` rewrites, and so the scope of the
    detectors that feed it. Kept separate from `_index_rows` so the difference is deliberate."""
    p = repo / "sdlc-studio" / "epics" / "_index.md"
    return [ln for ln in p.read_text(encoding="utf-8").splitlines()
            if reconcile._EPIC_ROW_RE.match(ln)] if p.is_file() else []


def _mutate_one_row_and_sweep(copy: Path) -> tuple[str, list[dict]]:
    """Blank one derived Stories cell in the tree under `copy` and sweep it.

    The row is taken from the live index. A live index with no epic row (every row archived, the
    state `archive.py` leaves a mature project in) would leave nothing to mutate, so the row is
    then taken from the archive sub-indexes and written into the live table, which is the table
    the sweep reads. Either way a row is mutated and the sweep must report exactly it.
    """
    target = copy / "sdlc-studio" / "epics" / "_index.md"
    text = target.read_text(encoding="utf-8")

    def usable(line: str) -> bool:
        # A row whose cell is a real derived count, so blanking it creates a placeholder.
        match = reconcile._EPIC_ROW_RE.match(line)
        return bool(match and reconcile._split_row_cells(line)[3].isdigit()
                    and f"{match.group(1)}.Stories" not in UNCORROBORATED)

    def blanked(line: str) -> str:
        cells = reconcile._split_row_cells(line)
        cells[3] = sdlc_md.CELL_NOT_STATED
        return "| " + " | ".join(cells) + " |"

    live = [ln for ln in text.splitlines() if usable(ln)]
    if live:
        victim = live[0]
        mutated = text.replace(victim, blanked(victim), 1)
    else:
        victim = next(ln for ln in _index_rows(copy, "epic") if usable(ln))
        lines = text.splitlines()
        # The row goes under the live table's separator row, so it sits in a table whose
        # columns the sweep can resolve.
        sep = next(i for i, ln in enumerate(lines) if re.match(r"^\|\s*-{3}", ln)
                   and "Stories" in lines[i - 1])
        lines.insert(sep + 1, blanked(victim))
        mutated = "\n".join(lines) + "\n"
    target.write_text(mutated, encoding="utf-8")
    rec = reconcile._EPIC_ROW_RE.match(victim).group(1)
    return rec, reconcile.epic_index_derivable_drift(copy)


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
        cls.rows = _index_rows(REPO, "epic")

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
            rec, found = _mutate_one_row_and_sweep(copy)
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
        record is a lane that gets switched off.

        Two halves, because archiving moves a row without changing it. The advisory reads the LIVE
        index, since that is the table `apply` would rewrite, so its scope is the live subset. The
        numbers themselves are pinned over the whole corpus instead: what this guard exists to
        protect is that the six recorded counts survive, and an archived row that lost its value
        would fail here whether or not the advisory can still see it.
        """
        live_ids = {reconcile._EPIC_ROW_RE.match(l).group(1) for l in _index_rows_live(REPO)}
        expected = {k: v for k, v in UNCORROBORATED.items() if k.split(".", 1)[0] in live_ids}
        advisory = {f"{a['id']}.{a['column']}": (a["current"], a["expected"])
                    for a in reconcile.epic_index_uncorroborated_advisory(REPO)}
        self.assertEqual(expected, advisory,
                         "the uncorroborated set changed - update it deliberately, by hand")
        drift_ids = {f"{d['id']}.{d['column']}" for d in reconcile.epic_index_derivable_drift(REPO)}
        self.assertEqual(set(), drift_ids & set(UNCORROBORATED),
                         "an uncorroborated row was also reported as mechanical drift")
        for a in reconcile.epic_index_uncorroborated_advisory(REPO):
            with self.subTest(row=a["id"]):
                self.assertIn("left alone", a["note"])

        # The recorded numbers, wherever the row now lives. Without this, archiving the six would
        # empty `expected` above and the guard would pass over a corpus that had lost them.
        by_id = {reconcile._EPIC_ROW_RE.match(l).group(1): reconcile._split_row_cells(l)
                 for l in self.rows}
        for key, (current, _expected) in UNCORROBORATED.items():
            rec, column = key.split(".", 1)
            with self.subTest(row=key):
                self.assertIn(rec, by_id, f"{rec}'s row is in neither the live index nor an "
                                          f"archive sub-index - the record is gone")
                cell = by_id[rec][sdlc_md.EPIC_INDEX_COLUMNS.index(column)]
                self.assertEqual(current, cell,
                                 f"{rec}'s recorded {column} count was rewritten from "
                                 f"`{current}` to `{cell}`")

    def test_the_kind_is_registered_and_carries_a_remediation_hint(self) -> None:
        self.assertIn("epic-index-derivable", reconcile.DRIFT_KINDS)
        hint = sdlc_md.REMEDIATION["reconcile"]["epic-index-derivable"]
        self.assertIn("PLACEHOLDER", hint)
        self.assertIn("left alone", hint,
                      "the hint must say that a contradicted value is held, not rewritten")

    def test_the_sweep_reads_archived_rows_and_not_only_the_live_table(self) -> None:
        """BG0504. The mutant this kills is `_index_rows` reading `_index.md` alone.

        Every floor in this file was calibrated against an index nobody had archived, so a
        live-only read makes them track the live table's size instead of the corpus - and
        `reconcile detect` advises archiving on every run once the table passes
        `indexes.archive_after`. Taking that advice once dropped the sweep from 207 rows to 30 and
        reported a corrupt index where there was none.

        Asserted against the archive as it is, so this holds before the first sweep too: with no
        archive on disk the two reads agree and only the shared floor applies.
        """
        live, whole = _index_rows_live(REPO), self.rows
        archived = len(whole) - len(live)
        self.assertGreaterEqual(archived, 0, "the union dropped a live row")
        self.assertGreater(len(whole), 150,
                           "the corpus sweep reads almost nothing - the floor every other test "
                           "here rests on")
        if (REPO / "sdlc-studio" / "epics" / "archive").is_dir():
            self.assertGreater(archived, 0,
                               "an epic archive exists and the sweep found no row in it, so it is "
                               "reading the live table only")

    def test_the_index_header_matches_the_canonical_column_definition(self) -> None:
        header = next(l for l in self.text.splitlines() if l.startswith("| ID |"))
        live = tuple(c.strip() for c in re.split(r"(?<!\\)\|", header.strip().strip("|")))
        self.assertEqual(sdlc_md.EPIC_INDEX_COLUMNS, live)



class EpicIndexNegativeControlTests(unittest.TestCase):

    def test_an_emptied_live_index_still_has_a_target(self) -> None:
        """With every epic row archived the control still mutates a row, and the sweep reports it.

        A fixture, because the repository's own live index is not empty today: the control must
        keep a target on the day archiving empties it, not fail with an exhausted search.
        """
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            copy = Path(d)
            epics = copy / "sdlc-studio" / "epics"
            (epics / "archive" / "v1").mkdir(parents=True)
            (copy / "sdlc-studio" / "stories").mkdir()
            head = ("| ID | Title | Status | Stories | Deps | Created | Updated |\n"
                    "| --- | --- | --- | --- | --- | --- | --- |\n")
            (epics / "_index.md").write_text("# Epic Index\n\n" + head, encoding="utf-8")
            # The first archived row carries no count, so it is no target; the second is.
            rows = ("| [EP0899](../../EP0899-w.md) | W | Done | -- | -- | 2026-01-01 | 2026-01-01 |\n"
                    "| [EP0900](../../EP0900-x.md) | T | Done | 0 | -- | 2026-01-01 | 2026-01-01 |\n")
            (epics / "archive" / "v1" / "epic.md").write_text("# archive\n\n" + head + rows,
                                                              encoding="utf-8")
            (epics / "EP0900-x.md").write_text("# EP0900: T\n\n> **Status:** Done\n",
                                               encoding="utf-8")
            self.assertEqual([], [ln for ln in (epics / "_index.md").read_text().splitlines()
                                  if reconcile._EPIC_ROW_RE.match(ln)],
                             "the fixture's live index is not empty")
            (epics / "EP0899-w.md").write_text("# EP0899: W\n\n> **Status:** Done\n",
                                               encoding="utf-8")
            self.assertEqual([], reconcile.epic_index_derivable_drift(copy),
                             "the unmutated fixture already drifts, so the control proves nothing")
            rec, found = _mutate_one_row_and_sweep(copy)
        self.assertEqual("EP0900", rec)
        self.assertEqual([("EP0900", "Stories")], [(f["id"], f["column"]) for f in found])

    def test_a_live_row_is_blanked_in_place_and_no_row_is_added(self) -> None:
        """With a live row present the control blanks that row where it stands.

        The live index holds one usable row and the archive another. The mutated live index must
        still hold exactly one row, the original, with its Stories cell blanked: a second row
        copied in from elsewhere would be a different mutation and leave the original intact.
        """
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            copy = Path(d)
            epics = copy / "sdlc-studio" / "epics"
            (epics / "archive" / "v1").mkdir(parents=True)
            (copy / "sdlc-studio" / "stories").mkdir()
            head = ("| ID | Title | Status | Stories | Deps | Created | Updated |\n"
                    "| --- | --- | --- | --- | --- | --- | --- |\n")
            live_row = "| [EP0900](../../EP0900-x.md) | T | Done | 0 | -- | 2026-01-01 | 2026-01-01 |\n"
            arch_row = "| [EP0901](../../EP0901-y.md) | U | Done | 0 | -- | 2026-01-01 | 2026-01-01 |\n"
            (epics / "_index.md").write_text("# Epic Index\n\n" + head + live_row, encoding="utf-8")
            (epics / "archive" / "v1" / "epic.md").write_text("# archive\n\n" + head + arch_row,
                                                              encoding="utf-8")
            for n, t in (("0900-x", "EP0900: T"), ("0901-y", "EP0901: U")):
                (epics / f"EP{n}.md").write_text(f"# {t}\n\n> **Status:** Done\n", encoding="utf-8")
            rec, found = _mutate_one_row_and_sweep(copy)
            after = _index_rows_live(copy)
        self.assertEqual("EP0900", rec)
        self.assertEqual(1, len(after), "a row was added to the live index instead of blanking one")
        self.assertEqual(sdlc_md.CELL_NOT_STATED, reconcile._split_row_cells(after[0])[3])
        self.assertEqual([("EP0900", "Stories")], [(f["id"], f["column"]) for f in found])


if __name__ == "__main__":
    unittest.main()
