"""BG1030: prose after `BLOCKING: none`, and a `RULINGS:` line, record unedited.

`_block_field` read BLOCKING to the next contract token, so a sentence after `none`, or a
`RULINGS:` line the contract did not list, was read as BLOCKING items and refused as quoting
no ISSUES finding. Each test drives `critic.py record --from-verdict` in a throwaway root.

MUTANTS, each of which a test here fails on: (1) `RULINGS` dropped from the block's tokens, so
the line is read into BLOCKING again; (2) the trailing prose after `none` dropped instead of
kept; (3) the rulings item read by `parse_findings` as a finding again; (4) a tagged item after
`none` swallowed into the prose; (5) the RULINGS line cut from the return contract; (6) a
carried REJECT's rulings item carried as one more finding.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "critic.py"


def _critic():
    spec = importlib.util.spec_from_file_location("critic_trailing_prose", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["critic_trailing_prose"] = mod
    spec.loader.exec_module(mod)
    return mod


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True, timeout=60, check=False)


class TrailingProseTests(unittest.TestCase):
    def _record(self, root: Path, block: str, name: str = "verdict.txt",
                unit: str = "US0001") -> subprocess.CompletedProcess:
        verdict = root / name
        verdict.write_text(block, encoding="utf-8")
        return _run("record", "--unit", unit, "--reviewer", "QA seat", "--author", "builder",
                    "--from-verdict", str(verdict), "--root", str(root))

    def _row(self, root: Path, unit: str = "US0001") -> dict:
        row = _critic().verdict_for(root, unit)
        self.assertIsNotNone(row, "nothing was recorded")
        return row

    def test_prose_after_blocking_none_records(self) -> None:
        mod = _critic()
        sentence = "The AC2 test is thin, but AC1's test carries the claim."
        for sep in (". ", "\n", "; ", " - ", ", "):
            block = ("VERDICT: APPROVE\nISSUES: [pre-existing] BG0123 the gate is slow\n"
                     f"BLOCKING: none{sep}{sentence}\n")
            with self.subTest(sep=sep), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                r = self._record(root, block)
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                issues = self._row(root)["issues"]
                self.assertEqual(["pre-existing"],
                                 [f["origin"] for f in mod.parse_findings(issues)], issues)
                self.assertEqual([], mod.blocking_findings(issues), issues)
                self.assertNotIn("BLOCKING:", issues, "a sentence after none was read as blocking")
                self.assertIn(sentence, mod.row_rulings(issues), "the sentence was lost")

    def test_a_tag_after_none_is_still_blocking(self) -> None:
        """Positive control: only untagged prose is kept as a remark; a tagged item after
        `none` is a finding and is never swallowed into it. `nonexistent` is not `none`."""
        mod = _critic()
        cases = (("ISSUES: none\nBLOCKING: none\n[new] the crash in x.py:3\n", "new"),
                 ("ISSUES: [new] nonexistent config crashes (c.py:1)\n"
                  "BLOCKING: nonexistent config crashes\n", "new"))
        for body, origin in cases:
            with self.subTest(body=body), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                r = self._record(root, "VERDICT: REJECT\n" + body)
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                issues = self._row(root)["issues"]
                self.assertEqual([origin], [f["origin"] for f in mod.blocking_findings(issues)],
                                 issues)
                self.assertEqual("", mod.row_rulings(issues), issues)

    def test_a_ruling_is_never_carried_as_a_finding(self) -> None:
        """A REJECT at the cap carries its findings as criteria; its rulings item is not one."""
        row = {"round": 2, "issues": "[new] the defect moved (y.py:4); "
                                     "RULINGS: 1. [new] vacuous test: MOVED to y.py:4"}
        acs, _verify = _critic().carried_criteria("US0001", "", row)
        self.assertEqual(1, len(acs), acs)
        self.assertIn("the defect moved", acs[0])

    def test_a_rulings_line_records(self) -> None:
        mod = _critic()
        self.assertIn("RULINGS:", mod._RETURN_CONTRACT, "the contract names no RULINGS line")
        blocks = (
            ("VERDICT: APPROVE\nISSUES: none\nBLOCKING: none\n"
             "RULINGS: AC2 is satisfied by the CLI test\n", [],
             "AC2 is satisfied by the CLI test"),
            ("VERDICT: APPROVE\nISSUES: [pre-existing] BG0123 slow (g.py:1)\n"
             "RULINGS: AC1 holds; AC2 holds (t.py:4)\nBLOCKING: none\n", ["pre-existing"],
             "AC1 holds; AC2 holds (t.py:4)"),
        )
        for block, origins, rulings in blocks:
            with self.subTest(block=block), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                r = self._record(root, block)
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                issues = self._row(root)["issues"]
                self.assertEqual(origins, [f["origin"] for f in mod.parse_findings(issues)],
                                 issues)
                self.assertEqual(rulings, mod.row_rulings(issues))

    def test_the_rejoinder_contract_names_rulings_and_they_record_as_rulings(self) -> None:
        mod = _critic()
        prior = ("VERDICT: REJECT\nISSUES: [new] vacuous killing test at test_x.py:10; "
                 "[new] docstring overclaims\nBLOCKING: the vacuous killing test\n")
        rulings = ("1. [new] vacuous killing test at test_x.py:10: CLOSED, the mutant now "
                   "fails it\n   2. [new] docstring overclaims: OVER-CLAIMED; it still says "
                   "always\n   3. [pre-existing] the slow gate: MOVED to g.py:9")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            stories = root / "sdlc-studio" / "stories"
            stories.mkdir(parents=True)
            (stories / "US0001-widget.md").write_text(
                "# US0001: widget frobnicates\n\n> **Status:** Review\n> **Points:** 5\n"
                "> **Affects:** widget.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
                "- **Verify:** shell echo ok\n", encoding="utf-8")
            seats = root / "sdlc-studio" / "personas" / "seats"
            seats.mkdir(parents=True)
            (seats / "qa.md").write_text("# QA seat\n<!-- role: qa -->\n", encoding="utf-8")
            (root / "prior.txt").write_text(prior, encoding="utf-8")
            b = _run("brief", "--unit", "US0001", "--seat", "qa", "--rejoinder",
                     str(root / "prior.txt"), "--root", str(root))
            self.assertEqual(0, b.returncode, b.stdout + b.stderr)
            contract = " ".join(b.stdout.split("Then return the SAME contract as before:")[-1]
                                .split())
            self.assertIn("RULINGS:", contract, "the rejoinder's contract names no RULINGS line")
            self.assertIn("Rule each finding of your prior verdict on the RULINGS line", b.stdout)
            for word in mod.REPAIR_RULINGS:
                self.assertIn(word, contract)
            self.assertEqual(0, self._record(root, prior, "r1.txt").returncode)
            r = self._record(root, "VERDICT: APPROVE\nISSUES: none\nBLOCKING: none\n"
                             f"RULINGS:\n{rulings}\n", "r2.txt")
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            row = self._row(root)
            self.assertEqual("APPROVE", row["verdict"])
            self.assertEqual([], mod.parse_findings(row["issues"]),
                             "a ruling quoting a [new] finding was recorded as a finding")
            kept = mod.row_rulings(row["issues"])
            self.assertEqual(" ".join(rulings.split()), kept)
            self.assertEqual(2, len(mod.delivery_rounds(root, "US0001")))


if __name__ == "__main__":
    unittest.main()
