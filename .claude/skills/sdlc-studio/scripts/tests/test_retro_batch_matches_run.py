"""A retro's Batch field is compared with the batch of the run its `Run` field names.

The close scaffolds the retro with the batch as it stands, and `sprint batch add` later adds
units (a carried unit re-added, a repair joining the run) without touching the retro. The
validator checked the Batch field only against the retro's own `Delivered: N / M` header, so a
stale field read as valid, and everything downstream (accuracy, the report's delivery count,
`close_owed`) measured a subset of the run without saying so. RETRO0134 named 16 units while
its run's batch held 18.

Each case writes a throwaway project, records the run where the close keeps it (the live run
state, or the run archive once it has closed) and asks `retro.py validate` and the close's
retro-validate step.
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import retro  # noqa: E402
import sprint  # noqa: E402
from lib import run_state  # noqa: E402

RUN = "RUN-01BATCHRUN1"
RID = "RETRO9999"


def _three_line(batch: str, run: str | None = RUN) -> str:
    """A Keep/Stop/Try retro the validator otherwise passes, naming `run` and `batch`."""
    run_line = f"> **Run:** {run}\n" if run is not None else ""
    return (f"# RETRO-9999: a run\n\n> **Date:** 2026-11-22\n{run_line}"
            f"> **Batch:** {batch}\n\n"
            "## Keep\n\n- the gate caught the regression\n\n"
            "## Stop\n\n- skipping the preflight\n\n"
            "## Try\n\n- run the preflight before the land\n")


def _older_shape(batch: str) -> str:
    """A retro in the older required-sections shape the validator otherwise passes."""
    return (f"# RETRO-9999: a sprint\n\n> **Run:** {RUN}\n> **Batch:** {batch}\n\n"
            "## Delivered\n- US0001 - shipped it\n"
            "## What went well\n- the gate caught it\n"
            "## What was hard / what stalled\n- the deploy was slow\n"
            "## Lessons\n- deploys need a preflight check\n"
            "## Actions raised\n| Finding | Disposition |\n| --- | --- |\n"
            "| the deploy was slow | BG0125 |\n")


class _Project(unittest.TestCase):

    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="retro_batch_"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        (self.root / "sdlc-studio" / "retros").mkdir(parents=True)

    def _retro(self, text: str) -> None:
        (self.root / "sdlc-studio" / "retros" / f"{RID}-a-run.md").write_text(
            text, encoding="utf-8")

    def _live(self, batch, run_id: str = RUN) -> dict:
        state = {"run_id": run_id, "outcome": run_state.RUNNING,
                 "started_at": "2026-11-22T09:00:00Z", "batch": batch}
        run_state.write(self.root, state)
        return state

    def _validate(self) -> tuple[int, str, dict]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = retro.main(["--root", str(self.root), "validate", "--id", RID])
        return rc, out.getvalue(), retro.validate(str(self.root), RID)

    def _close_step(self, state: dict) -> tuple:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            return sprint._close_retro_validate(self.root, RID, state)


class BatchMatchesRunTests(_Project):

    def test_omitted_unit_is_refused_by_validate(self) -> None:
        """AC1, the validator. MUTANT: drop the comparison - the field naming two of the run's
        three units validates, as it did for RETRO0134."""
        self._live(["US0001", "BG0002", "BG0003"])
        self._retro(_three_line("US0001, BG0002"))
        rc, out, res = self._validate()
        self.assertEqual(1, rc, out)
        self.assertFalse(res["ok"])
        omitted = [e for e in res["errors"] if "omits" in e]
        self.assertEqual(1, len(omitted), res["errors"])
        self.assertIn("BG0003", omitted[0])
        self.assertIn(RUN, omitted[0])
        self.assertNotIn("US0001", omitted[0], "a unit the field names is not omitted")
        self.assertIn("BG0003", out, "the refusal names the omitted id on the command's output")

    def test_omitted_unit_is_refused_by_the_close_step(self) -> None:
        """AC1, the close. The retro-validate step runs the validator, so it refuses too and its
        detail, which the close hands over, names the omitted id."""
        state = self._live(["US0001", "BG0002", "BG0003"])
        self._retro(_three_line("US0001, BG0002"))
        ok, detail, remedy = self._close_step(state)
        self.assertFalse(ok, detail)
        self.assertIn("BG0003", detail)
        self.assertIn(RID, remedy)

    def test_omitted_unit_is_refused_from_the_archived_run(self) -> None:
        """Once the run has closed it is read from the run archive. MUTANT: read the live state
        alone - a later run is open, the named run is only archived, and the stale field passes."""
        run_state.archive(self.root, {"run_id": RUN, "batch": ["US0001", "BG0002", "BG0003"]})
        self._live(["US0005"], run_id="RUN-01LATERRUN1")
        self._retro(_three_line("US0001, BG0002"))
        rc, out, res = self._validate()
        self.assertEqual(1, rc, out)
        self.assertTrue(any("BG0003" in e for e in res["errors"]), res["errors"])

    def test_omitted_unit_is_refused_in_the_older_shape(self) -> None:
        """A retro in the older shape is validated by its own branch, and is compared too.
        MUTANT: compare only in the Keep/Stop/Try branch."""
        self._live(["US0001", "BG0002"])
        self._retro(_older_shape("US0001"))
        rc, out, res = self._validate()
        self.assertEqual(1, rc, out)
        self.assertTrue(any("omits" in e and "BG0002" in e for e in res["errors"]),
                        res["errors"])

    def test_a_field_naming_every_unit_of_the_run_passes(self) -> None:
        """The positive control: the same project with every unit named, in another order and
        spelling, validates and the close step passes, in both shapes."""
        state = self._live(["US0001", "BG0002", "BG0003"])
        self._retro(_three_line("bg0003, US0001, BG0002"))
        rc, out, res = self._validate()
        self.assertEqual(0, rc, out)
        self.assertTrue(res["ok"], res["errors"])
        ok, detail, _remedy = self._close_step(state)
        self.assertTrue(ok, detail)
        self._retro(_older_shape("US0001, BG0002, BG0003"))
        self.assertTrue(self._validate()[2]["ok"])

    def test_a_unit_the_field_adds_is_not_refused(self) -> None:
        """Only an omission refuses: a unit the field names that the batch does not (carried
        out, or named by hand) is the author's statement, and the batch keeps no record of it."""
        self._live(["US0001"])
        self._retro(_three_line("US0001, US0009"))
        res = self._validate()[2]
        self.assertTrue(res["ok"], res["errors"])

    def test_a_retro_naming_no_run_is_not_compared(self) -> None:
        """A retro made outside a run (`-`), one with no Run line, and one whose Run slot is
        still the template's placeholder name no batch to compare with."""
        self._live(["US0001", "BG0002"])
        for run in ("-", None):
            with self.subTest(run=run):
                self._retro(_three_line("US0001", run=run))
                res = self._validate()[2]
                self.assertTrue(res["ok"], res["errors"])
        self.assertIsNone(retro.retro_run_id("> **Run:** {{run_id}}\n"))
        self.assertIsNone(retro.retro_run_id("> **Run:** -\n"))
        self.assertEqual(RUN, retro.retro_run_id(f"> **Run:** {RUN}\n"))

    def test_a_run_with_no_record_is_not_compared(self) -> None:
        """A run neither open nor archived here (another clone's) has no batch to read, so the
        field is left as written rather than refused on nothing."""
        self._live(["US0001", "BG0002"], run_id="RUN-01OTHERRUN1")
        self._retro(_three_line("US0001"))
        res = self._validate()[2]
        self.assertTrue(res["ok"], res["errors"])

    def test_a_batch_that_is_not_a_list_is_not_read_as_units(self) -> None:
        """A damaged record whose batch is a string is not iterated character by character into
        units the field 'omits', and a blank or non-string entry in a list is not a unit."""
        self._live("BG0002")
        self._retro(_three_line("US0001"))
        res = self._validate()[2]
        self.assertTrue(res["ok"], res["errors"])
        # An entry that is blank or not an id string is no unit either.
        self._live(["US0001", "", None, 7])
        res = self._validate()[2]
        self.assertTrue(res["ok"], res["errors"])

    def test_an_unreadable_run_state_is_refused_by_name(self) -> None:
        """An unreadable run state is not an absent one: the comparison cannot be made, and the
        validator says so rather than passing the field unread."""
        p = run_state.path(self.root)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("{not json", encoding="utf-8")
        self._retro(_three_line("US0001"))
        rc, out, res = self._validate()
        self.assertEqual(1, rc, out)
        self.assertTrue(any("cannot be compared" in e and RUN in e for e in res["errors"]),
                        res["errors"])


SKILL = Path(__file__).resolve().parents[2]


class BatchCheckDocumentedTests(unittest.TestCase):
    """An operator whose close stops on a stale Batch field finds the check where the close
    gate's checks are listed, not only in the error text."""

    def test_the_close_gate_list_names_the_batch_check(self) -> None:
        """The retro reference's numbered list of what the close gate checks carries the check,
        with its rules: read from the live run state, else the archive; an unreadable run state
        refusing; a unit the field adds left as written. MUTANT: the list as it stood, four
        checks with no Batch item."""
        text = (SKILL / "reference-retro.md").read_text(encoding="utf-8")
        gate = text.split("## What the close gate checks", 1)[1].split("\n## ", 1)[0]
        found = re.search(r"(?ms)^5\. (.*?)(?=^\d+\. |\n\n|\Z)", gate)
        item = found.group(0) if found else ""
        flat = " ".join(item.split())
        for words in ("**The Batch field omits no unit of the run's batch**", "`> **Run:**`",
                      "`sprint.py batch add`", "live run state", "run archive",
                      "cannot be read refuses", "left as written"):
            with self.subTest(words=words):
                self.assertIn(words, flat, item)

    def test_the_catalogue_names_the_batch_check(self) -> None:
        """The script catalogue's `retro.py` entry lists what `validate` checks. MUTANT: the
        entry as it stood, naming sections, a lesson and dispositions only."""
        entry = next(line for line in (SKILL / "reference-scripts.md").read_text(
            encoding="utf-8").splitlines() if line.startswith("- `retro.py` - "))
        self.assertIn("a Batch field that omits no unit of the batch of the run it names",
                      entry)

    def test_the_help_page_names_the_batch_check(self) -> None:
        """The retro help page's `retro validate` row lists what the check reads. MUTANT: the
        row as it stood, naming the three lines, the Try limit, placeholders and class tags."""
        row = next(line for line in (SKILL / "help" / "retro.md").read_text(
            encoding="utf-8").splitlines() if line.startswith("| `/sdlc-studio retro validate` |"))
        self.assertIn("the Batch field omits no unit of the batch of the run its `Run` field "
                      "names", row)


if __name__ == "__main__":
    unittest.main()
