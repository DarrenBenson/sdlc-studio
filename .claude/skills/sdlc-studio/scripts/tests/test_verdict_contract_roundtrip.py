"""BG0950: a verdict written to `critic.py brief`'s own return contract records through
`critic.py record --from-verdict` without the author touching it.

Each test drives the shipped CLI in a throwaway root. MUTANTS, each of which a test here fails on:
(1) the BLOCKING section is folded into ISSUES as one more `BLOCKING: <text>` item again, so its
untagged items are refused and a tagged one is recorded twice; (2) findings are split on every
unescaped `;` again, so a reviewer's semicolon inside one finding's parenthesised evidence
splits it and the second half is refused as untagged; (3) a BLOCKING item that quotes no ISSUES finding and carries
no tag is recorded under a guessed origin instead of being refused; (4) quoting is matched
by exact text only, so a reviewer's paraphrase with an article is refused.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "critic.py"


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT.parent / file)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _critic():
    spec = importlib.util.spec_from_file_location("critic_roundtrip", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["critic_roundtrip"] = mod
    spec.loader.exec_module(mod)
    return mod


#: Exactly the shape `_RETURN_CONTRACT` asks for: tagged ISSUES with file:line evidence, and an
#: untagged BLOCKING subset of two items, each quoting the start of its ISSUES finding.
CONTRACT_BLOCK = """\
VERDICT: REJECT
ISSUES: [new] AC1 is false: the gate never reads the flag (gate.py:10);
        [new] the doc names a command that does not exist (D.md:94);
        [pre-existing] BG0123 the gate is slow
BLOCKING: AC1 is false; the doc names a command that does not exist
"""


class VerdictContractRoundTripTests(unittest.TestCase):
    def _record(self, root: Path, block: str) -> subprocess.CompletedProcess:
        verdict = root / "verdict.txt"
        verdict.write_text(block, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), "record", "--unit", "US0001", "--reviewer", "QA seat",
             "--author", "builder", "--from-verdict", str(verdict), "--root", str(root)],
            capture_output=True, text=True, timeout=60, check=False)

    def _issues(self, root: Path) -> str:
        row = _critic().verdict_for(root, "US0001")
        self.assertIsNotNone(row, "nothing was recorded")
        return row["issues"]

    def test_a_contract_block_records_without_edits(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            r = self._record(root, CONTRACT_BLOCK)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            findings = _critic().parse_findings(self._issues(root))
            self.assertEqual(["new", "new", "pre-existing"], [f["origin"] for f in findings],
                             findings)

    def test_a_blocking_finding_is_blocking_recorded_once_and_marked(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.assertEqual(0, self._record(root, CONTRACT_BLOCK).returncode)
            issues = self._issues(root)
            self.assertEqual(1, issues.count("AC1 is false"), issues)
            self.assertEqual(1, issues.count("the doc names a command"), issues)
            marked = [f["text"] for f in _critic().parse_findings(issues)]
            self.assertEqual(3, len(marked), marked)
            self.assertEqual(2, issues.count("BLOCKING:"), issues)
            self.assertNotIn("BLOCKING: [pre-existing]", issues,
                             "a finding the reviewer did not list as blocking was marked")

    def test_a_semicolon_in_finding_evidence_stays_in_it(self) -> None:
        block = ("VERDICT: REJECT\n"
                 "ISSUES: [new] the mode file is read twice (`study_work_mode.json`:69; also in "
                 "the parent commit); [pre-existing] BG0123 the gate is slow\n"
                 "BLOCKING: the mode file is read twice\n")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            r = self._record(root, block)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            findings = _critic().parse_findings(self._issues(root))
            self.assertEqual(2, len(findings), findings)
            self.assertIn("`study_work_mode.json`:69; also in the parent commit", findings[0]["text"],
                          "the reviewer's words did not survive unchanged")

    def test_an_untagged_blocking_item_quoting_no_finding_is_refused(self) -> None:
        block = CONTRACT_BLOCK.replace("BLOCKING: AC1 is false;", "BLOCKING: something else entirely;")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            r = self._record(root, block)
            self.assertNotEqual(0, r.returncode)
            self.assertIn("something else entirely", r.stderr)
            self.assertIsNone(_critic().verdict_for(root, "US0001"), "a refused block was recorded")

    def test_a_paraphrased_blocking_item_marks_its_finding(self) -> None:
        block = CONTRACT_BLOCK.replace("BLOCKING: AC1 is false;", "BLOCKING: the flag the gate never reads;")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            r = self._record(root, block)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertIn("BLOCKING: [new] AC1 is false", self._issues(root))

    def test_a_blocking_item_two_findings_answer_is_refused(self) -> None:
        block = CONTRACT_BLOCK.replace("BLOCKING: AC1 is false;", "BLOCKING: the gate;")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            r = self._record(root, block)
            self.assertNotEqual(0, r.returncode)
            self.assertIn("quotes 2 ISSUES findings", r.stderr)

    def test_a_bulleted_list_records_one_finding_per_bullet(self) -> None:
        block = ("VERDICT: REJECT\n"
                 "ISSUES:\n"
                 "- [new] the lane skips a module [see gate.py:40; and gate.py:52]\n"
                 "  when it is marked serial\n"
                 "- [pre-existing] BG0123 the gate is slow\n"
                 "BLOCKING: the lane skips a module\n")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            r = self._record(root, block)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            findings = _critic().parse_findings(self._issues(root))
            self.assertEqual(["new", "pre-existing"], [f["origin"] for f in findings], findings)
            self.assertIn("[see gate.py:40; and gate.py:52]", findings[0]["text"])

    def test_a_bare_semicolon_before_untagged_text_is_still_refused(self) -> None:
        """Fail-closed kept: outside brackets and code spans, `;` still ends a finding, so an
        untagged tail is its own finding and refused, never absorbed into the tagged one."""
        block = "VERDICT: REJECT\nISSUES: [regression] a real one; the gate feels slow\nBLOCKING: none\n"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            r = self._record(root, block)
            self.assertNotEqual(0, r.returncode)
            self.assertIn("the gate feels slow", r.stdout + r.stderr)

    def _only(self, issues: str) -> str:
        return f"VERDICT: REJECT\nISSUES: {issues}\nBLOCKING: none\n"

    def _origins(self, root: Path) -> list:
        return [f["origin"] for f in _critic().parse_findings(self._issues(root))]

    def test_an_unclosed_bracket_does_not_swallow_the_next_finding(self) -> None:
        block = self._only("[pre-existing] BG0123 the gate is slow (see gate.py:10; "
                           "[regression] verify_ac crashes on empty Affects (verify_ac.py:88)")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            r = self._record(root, block)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertEqual(["pre-existing", "regression"], self._origins(root))
            self.assertEqual(1, len(_critic().blocking_findings(self._issues(root))))

    def test_a_trailing_backslash_does_not_swallow_the_next_finding(self) -> None:
        block = self._only("[new] the path separator is a backslash \\ ; "
                           "[regression] the gate crashes (g.py:1)")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            r = self._record(root, block)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertEqual(["new", "regression"], self._origins(root))
            self.assertTrue(_critic().parse_findings(self._issues(root))[0]["text"].endswith("\\"))

    def test_a_semicolon_in_finding_records_with_blocking_none(self) -> None:
        block = self._only("[new] the mode file is read twice (`study_work_mode.json`:69; also in "
                           "the parent commit); [pre-existing] BG0123 the gate is slow")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            r = self._record(root, block)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            findings = _critic().parse_findings(self._issues(root))
            self.assertEqual(2, len(findings), findings)
            self.assertIn(":69; also in the parent commit", findings[0]["text"])

    def test_a_code_span_and_an_escape_keep_their_semicolons(self) -> None:
        block = self._only("[new] the parser reads `a; b` as two; [new] write x\\; y in prose; "
                           "[pre-existing] BG0123 slow")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            r = self._record(root, block)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            texts = [f["text"] for f in _critic().parse_findings(self._issues(root))]
            self.assertEqual(3, len(texts), texts)
            self.assertIn("`a; b`", texts[0])
            self.assertIn("x; y", texts[1])

    def test_a_tagged_blocking_item_is_blocking_recorded_once(self) -> None:
        block = CONTRACT_BLOCK.replace("BLOCKING: AC1 is false;", "BLOCKING: [new] AC1 is false;")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.assertEqual(0, self._record(root, block).returncode)
            issues = self._issues(root)
            self.assertEqual(1, issues.count("AC1 is false"), issues)
            self.assertIn("BLOCKING: [new] AC1 is false", issues)

    def test_a_partial_word_quote_marks_its_finding(self) -> None:
        block = ("VERDICT: REJECT\nISSUES: [new] the lane skips a module (g.py:1); "
                 "[new] the doc is wrong (D.md:4)\nBLOCKING: lane skip\n")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            r = self._record(root, block)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertIn("BLOCKING: [new] the lane skips", self._issues(root))

    def test_an_untagged_bulleted_blocking_list_marks_each_item(self) -> None:
        block = CONTRACT_BLOCK.replace(
            "BLOCKING: AC1 is false; the doc names a command that does not exist",
            "BLOCKING:\n- AC1 is false\n- the doc names a command that does not exist")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            r = self._record(root, block)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertEqual(2, self._issues(root).count("BLOCKING:"))

    def test_each_finding_starts_outside_any_bracket(self) -> None:
        block = self._only("[new] a (x; [new] b; then c")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            r = self._record(root, block)
            self.assertNotEqual(0, r.returncode, "an untagged tail was absorbed into a finding")
            self.assertIn("then c", r.stdout + r.stderr)

    def test_a_rejoinder_checks_a_loose_prior_verdict_for_form_only(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            stories = root / "sdlc-studio" / "stories"
            stories.mkdir(parents=True)
            (stories / "US0101-widget.md").write_text(
                "# US0101: widget frobnicates\n\n> **Status:** Review\n> **Points:** 5\n"
                "> **Affects:** widget.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
                "- **Verify:** shell echo ok\n", encoding="utf-8")
            seats = root / "sdlc-studio" / "personas" / "seats"
            seats.mkdir(parents=True)
            (seats / "qa.md").write_text("# QA seat\n<!-- role: qa -->\n", encoding="utf-8")
            prior = root / "prior.txt"
            prior.write_text("VERDICT: REJECT\nISSUES: [new] it does not work\n"
                             "BLOCKING: the failing case\n", encoding="utf-8")
            r = subprocess.run([sys.executable, str(SCRIPT), "brief", "--unit", "US0101", "--seat",
                                "qa", "--rejoinder", str(prior), "--root", str(root)],
                               capture_output=True, text=True, timeout=60, check=False)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)

    def test_the_brief_history_reads_an_escaped_semicolon_whole(self) -> None:
        block = self._only("[pre-existing] BG0123 slow (x.py:1; also in the parent commit); "
                           "[new] the doc is wrong (D.md:4)")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.assertEqual(0, self._record(root, block).returncode)
            rows = [{"unit": "US0001", "verdict": "REJECT", "issues": self._issues(root)}]
            history = _load("reconcile_roundtrip", "reconcile.py").blocking_findings(rows, "US0001")
            self.assertEqual(1, len(history), history)
            self.assertIn("the doc is wrong", history[0])

    def test_readers_split_a_stored_row_as_before(self) -> None:
        mod = _critic()
        self.assertEqual(["a", "b"], [f["text"] for f in mod.parse_findings("a; b")])
        self.assertEqual([None], [f["origin"] for f in mod.parse_findings("[pre-existing] x; y")][1:],
                         "an untagged item beside a pre-existing one stopped being its own finding")
        self.assertEqual(["keep ; this"], [f["text"] for f in mod.parse_findings(r"[new] keep \; this")])

if __name__ == "__main__":
    unittest.main()
