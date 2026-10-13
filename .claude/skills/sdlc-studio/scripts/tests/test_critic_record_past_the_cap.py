"""BG1003: `critic.py record` takes a review round past the cap that an accepted operator ruling
authorises, and only that.

An operator may rule a further round on a unit (this repository's D0352 and D0353 for BG0993),
but record refused every round past `review.max_rounds`, so the ledger's last word stayed a
REJECT the unit had moved past. `--ruling D0xxx` now admits one round, when the decision is
accepted, names the unit as its subject (the first work-item id in its text), and has not
already authorised a round on that unit. The check lives in `round_refusal`, which every writer
of a delivery verdict asks.

Each test seeds a ledger with two rounds on BG0001 (the cap of 2) and a decisions log, then
drives the shipped CLI.

MUTANTS: the ruling ignored, so the cap refuses it (AC1); a decision accepted whatever its status,
read by any mention of the unit rather than its subject, missing ones admitted, or one ruling
admitting every later round (AC2); the check kept in record's argument handling rather than in
`round_refusal` (AC3).
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
"""


def _critic():
    spec = importlib.util.spec_from_file_location("critic_past_cap", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["critic_past_cap"] = mod
    spec.loader.exec_module(mod)
    return mod


class RecordPastTheCapTests(unittest.TestCase):
    def _root(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "sdlc-studio").mkdir()
        (root / "sdlc-studio" / "decisions.md").write_text(DECISIONS, encoding="utf-8")
        mod = _critic()
        with unittest.mock.patch.object(mod, "round_refusal", lambda *a, **k: None):
            for _ in range(2):
                mod._write_verdict(root, "BG0001", "REJECT", "qa seat", "builder",
                                   "[new] it does not work (a.py:1)", "delivery", "", None, False)
        return root

    def _record(self, root: Path, ruling: str | None, reviewer: str = "qa seat",
                verdict: str = "APPROVE") -> subprocess.CompletedProcess:
        argv = [sys.executable, str(SCRIPT), "record", "--unit", "BG0001", "--verdict", verdict,
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

    def test_a_ruling_that_does_not_authorise_this_unit_is_refused(self) -> None:
        root = self._root()
        for ruling, why in ((None, "at the cap of 2"),
                            ("D9999", "is not a decision"),
                            ("D0003", "is superseded, not accepted"),
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
        path, _row = mod._write_verdict(root, "BG0001", "APPROVE", "qa seat", "builder", "none",
                                        "delivery", "", None, False, "D0001")
        self.assertTrue(path.exists())
        self.assertEqual("D0001", self._rows(root)[-1].get("ruling"))


if __name__ == "__main__":
    unittest.main()
