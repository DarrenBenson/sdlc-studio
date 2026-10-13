"""BG1003: `critic.py record` takes a review round past the cap that an accepted operator ruling
authorises, and only that.

An operator may rule a further round on a unit (this repository's D0352 and D0353 for BG0993),
but record refused every round past `review.max_rounds`, so the ledger's last word stayed a
REJECT the unit had moved past. `--ruling D0xxx` now admits one round, when the decision is
standing and accepted, names the unit as its subject (the first artefact id in its text, read
with the shared id grammar), and has not already authorised a round on that unit. The check
lives in `round_refusal`, which every writer of a delivery verdict asks.

Each test seeds a ledger with the unit at the cap of 2 and a decisions log, then drives the
shipped CLI.

MUTANTS: the ruling ignored, so the cap refuses it (AC1). AC2: a decision accepted whatever its
status (superseded, revisited, or superseded by a later row's Supersedes cell); the subject read
by a narrower id pattern than the shared grammar (a v3, dashed, five-digit or lower-case id
unseen, so a decision naming one first reads as about the unit it names second) or by any
mention of the unit; a missing decision admitted; one ruling admitting every later round; the
record's fields written raw, so a reviewer id forges one; the ruling keyed by the row's position
rather than its identity; a ruling spent, or refused, below the cap. AC3: `round_refusal`
admitting any ruling at the cap, with the check moved into record's argument handling.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "critic.py"

DECISIONS = """# Decisions

| ID | Decision | Rationale | Status | Supersedes | Date |
| --- | --- | --- | --- | --- | --- |
| D0001 | BG0001 gets a third review round past the cap. | The fix is specified. | accepted | -- | 2026-10-13 |
| D0002 | BG0002 ships first; BG0001 is mentioned only in passing. | Order. | accepted | -- | 2026-10-13 |
| D0003 | BG0001 gets another round. | Withdrawn. | superseded | -- | 2026-10-13 |
| D0004 | BG0001 gets another round, pending a revisit. | Revisit. | revisited | -- | 2026-10-13 |
| D0005 | BG0001 gets a round, as first ruled. | Replaced. | accepted | -- | 2026-10-13 |
| D0006 | BG0002 is planned again, replacing the earlier ruling. | Lineage. | accepted | D0005 | 2026-10-13 |
| D0007 | CR-0007 ships before BG0001 is reviewed again. | Order. | accepted | -- | 2026-10-13 |
| D0008 | BG-01JQK3F8 ships before BG0001 is reviewed again. | Order. | accepted | -- | 2026-10-13 |
| D0009 | BG-01JQK3F8 gets a third round. | Schema v3. | accepted | -- | 2026-10-13 |
| D0010 | CR-0007 gets a third round. | Dashed. | accepted | -- | 2026-10-13 |
| D0011 | BG10001 gets a third round. | Five digits. | accepted | -- | 2026-10-13 |
| D0012 | bg0001 gets a third round. | Lower case. | accepted | -- | 2026-10-13 |
"""


def _critic():
    spec = importlib.util.spec_from_file_location("critic_past_cap", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["critic_past_cap"] = mod
    spec.loader.exec_module(mod)
    return mod


class RecordPastTheCapTests(unittest.TestCase):
    def _root(self, unit: str = "BG0001",
              rows: tuple[tuple[str, str], ...] = (("REJECT", "qa seat"),) * 2) -> Path:
        """A project whose ledger holds `rows` (verdict, reviewer) on `unit`, oldest first."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "sdlc-studio").mkdir()
        (root / "sdlc-studio" / "decisions.md").write_text(DECISIONS, encoding="utf-8")
        mod = _critic()
        with unittest.mock.patch.object(mod, "round_refusal", lambda *a, **k: None):
            for verdict, reviewer in rows:
                mod._write_verdict(root, unit, verdict, reviewer, "builder",
                                   "[new] it does not work (a.py:1)", "delivery", "", None, False)
        return root

    def _record(self, root: Path, ruling: str | None, reviewer: str = "qa seat",
                verdict: str = "APPROVE", unit: str = "BG0001") -> subprocess.CompletedProcess:
        argv = [sys.executable, str(SCRIPT), "record", "--unit", unit, "--verdict", verdict,
                "--reviewer", reviewer, "--author", "builder", "--issues", "none",
                "--root", str(root)]
        if ruling:
            argv += ["--ruling", ruling]
        return subprocess.run(argv, capture_output=True, text=True, timeout=60, check=False)

    def _rows(self, root: Path) -> list[dict]:
        return [r for r in _critic().read_verdicts(root) if r["unit"] == "BG0001"]

    def test_a_round_authorised_by_a_ruling_naming_the_unit_is_recorded(self) -> None:
        root = self._root()
        r = self._record(root, "D0001")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        rows = self._rows(root)
        self.assertEqual(3, len(rows))
        self.assertEqual("APPROVE", rows[-1]["verdict"])
        self.assertEqual(3, rows[-1]["round"])
        self.assertEqual("D0001", rows[-1].get("ruling"), "the row does not carry its ruling")
        self.assertNotIn("ruling", rows[0], "a ruling was read onto a round it did not authorise")
        record = _critic().read_round_rulings(root)
        self.assertEqual([("BG0001", "3", "D0001", "qa seat")],
                         [(r["unit"], r["round"], r["ruling"], r["reviewer"]) for r in record])

    def test_the_subject_is_read_by_the_shared_id_grammar(self) -> None:
        for unit, ruling in (("BG-01JQK3F8", "D0009"), ("CR-0007", "D0010"),
                             ("BG10001", "D0011"), ("BG0001", "D0012")):
            with self.subTest(unit=unit, ruling=ruling):
                root = self._root(unit)
                r = self._record(root, ruling, unit=unit)
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        for ruling, first in (("D0007", "CR0007"), ("D0008", "BG01JQK3F8")):
            with self.subTest(case="a decision naming another id first", ruling=ruling):
                root = self._root()
                r = self._record(root, ruling)
                self.assertNotEqual(0, r.returncode, r.stdout)
                self.assertIn(f"is about {first}, not BG0001", r.stdout + r.stderr)
                self.assertEqual(2, len(self._rows(root)), "a refused round was written")

    def test_a_ruling_that_does_not_authorise_this_unit_is_refused(self) -> None:
        root = self._root()
        for ruling, why in ((None, "at the cap of 2"),
                            ("D9999", "is not a decision"),
                            ("D0003", "is superseded, not accepted"),
                            ("D0004", "is revisited, not accepted"),
                            ("D0005", "is superseded, not accepted"),
                            ("D0002", "is about BG0002, not BG0001")):
            with self.subTest(ruling=ruling):
                r = self._record(root, ruling)
                self.assertNotEqual(0, r.returncode, r.stdout)
                self.assertIn(why, r.stdout + r.stderr)
                self.assertEqual(2, len(self._rows(root)), "a refused round was written")
        with self.subTest(case="another reviewer than the one who rejected"):
            r = self._record(root, "D0001", reviewer="someone else")
            self.assertNotEqual(0, r.returncode, r.stdout)
            self.assertIn("must be recorded by qa seat", r.stdout + r.stderr)
        self.assertEqual(0, self._record(root, "D0001", verdict="REJECT").returncode)
        with self.subTest(case="the same ruling again"):
            r = self._record(root, "D0001")
            self.assertNotEqual(0, r.returncode, r.stdout)
            self.assertIn("already authorised round 3 of BG0001", r.stdout + r.stderr)
            self.assertEqual(3, len(self._rows(root)))

    def test_every_verdict_writer_honours_the_same_ruling(self) -> None:
        root = self._root()
        mod = _critic()
        self.assertIsNotNone(mod.round_refusal(root, "BG0001", "qa seat", "APPROVE"))
        self.assertIsNone(mod.round_refusal(root, "BG0001", "qa seat", "APPROVE", "D0001"),
                          "round_refusal, the one authority every writer asks, ignores a ruling")
        for bad in ("D9999", "D0002", "D0003", "D0004", "D0005"):
            with self.subTest(ruling=bad):
                self.assertIsNotNone(mod.round_refusal(root, "BG0001", "qa seat", "APPROVE", bad),
                                     "round_refusal admitted a ruling that authorises nothing")
                with self.assertRaises(ValueError):
                    mod.record_verdict(root, "BG0001", "APPROVE", "qa seat", "builder", "none",
                                       ruling=bad)
        path, _row = mod._write_verdict(root, "BG0001", "APPROVE", "qa seat", "builder", "none",
                                        "delivery", "", None, False, "D0001")
        self.assertTrue(path.exists())
        self.assertEqual("D0001", self._rows(root)[-1].get("ruling"))


    def test_a_ruling_below_the_cap_is_noted_and_not_spent(self) -> None:
        root = self._root(rows=(("REJECT", "qa seat"),))
        r = self._record(root, "D0001", verdict="REJECT")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("BG0001 was below the review cap, so ruling D0001 was not needed", r.stderr)
        self.assertEqual([], _critic().read_round_rulings(root), "a ruling was spent below the cap")
        r = self._record(root, "D0001")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual("D0001", self._rows(root)[-1].get("ruling"))

    def test_a_reviewer_id_cannot_forge_a_ruling_field(self) -> None:
        forger = "qa seat unit=BG0002 round=9 recorded=1999-01-01"
        root = self._root(rows=(("REJECT", forger),) * 2)
        self.assertEqual(0, self._record(root, "D0001", reviewer=forger, verdict="REJECT").returncode)
        [record] = _critic().read_round_rulings(root)
        self.assertEqual(("BG0001", "3"), (record["unit"], record["round"]), record)
        self.assertNotEqual("1999-01-01", record["recorded"], "the reviewer id forged a field")
        self.assertIn("BG0002", record["reviewer"], "the reviewer id was cut at an embedded key")
        self.assertTrue(record["reviewer"].startswith("qa seat"), record)
        r = self._record(root, "D0001", reviewer=forger)
        self.assertNotEqual(0, r.returncode, "one ruling authorised two rounds")
        self.assertIn("already authorised round 3 of BG0001", r.stdout + r.stderr)

    def test_the_ruling_stays_with_its_row_and_names_the_delivery_round(self) -> None:
        mod = _critic()
        root = self._root(rows=(("REJECT", "first seat"), ("REJECT", "qa seat")))
        self.assertEqual(0, self._record(root, "D0001").returncode)
        # superseding an earlier row AFTER the ruling moves the ruled row from round 3 to 2
        mod.record_supersession(root, "BG0001", mod.sdlc_md.now_date(), "the pass never ran",
                                "operator", "test boundary", reviewer="first seat")
        ruled = [r for r in self._rows(root) if r.get("ruling")]
        self.assertEqual([("APPROVE", "D0001")], [(r["verdict"], r["ruling"]) for r in ruled],
                         "the ruling moved off the row it authorised when an earlier row was "
                         "superseded")
        # a unit's earlier delivery is not counted: the round is the one record prints
        root = self._root(rows=(("REJECT", "qa seat"), ("APPROVE", "qa seat"),
                                ("REJECT", "qa seat"), ("REJECT", "qa seat")))
        self.assertEqual(0, self._record(root, "D0001").returncode)
        self.assertEqual("3", mod.read_round_rulings(root)[0]["round"])
        r = self._record(root, "D0001")
        self.assertIn("already authorised round 3 of BG0001", r.stdout + r.stderr)

    def test_the_section_introduction_speaks_of_ruling_records(self) -> None:
        mod = _critic()
        root = self._root()
        self.assertEqual(0, self._record(root, "D0001").returncode)
        section = mod.verdicts_path(root, "delivery").read_text(encoding="utf-8").split(
            mod.SUPERSEDE_HEADING, 1)[1]
        self.assertIn("a RULING record names", section)
        self.assertNotIn("Each record retires one verdict row above", section)
        # a section the supersession writer opened gets one note before its first ruling record
        root = self._root(rows=(("REJECT", "first seat"), ("REJECT", "qa seat"),
                                ("REJECT", "qa seat")))
        mod.record_supersession(root, "BG0001", mod.sdlc_md.now_date(), "the pass never ran",
                                "operator", "test boundary", reviewer="first seat")
        self.assertEqual(0, self._record(root, "D0001").returncode)
        section = mod.verdicts_path(root, "delivery").read_text(encoding="utf-8").split(
            mod.SUPERSEDE_HEADING, 1)[1]
        note = section.find("A RULING record names")
        self.assertGreater(note, section.find("Each record retires one verdict row above"))
        self.assertLess(note, section.find("RULING unit="))


if __name__ == "__main__":
    unittest.main()
