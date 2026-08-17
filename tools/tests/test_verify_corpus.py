"""The corpus verification lane compares against its baseline in BOTH directions (BG0535/D0137).

`tools/verify-corpus.sh` asks the two questions the per-commit gate cannot afford - a criterion
stamped `Verified: yes` whose selector now selects nothing, and a criterion that FAILS when
executed - and compares each count against `tools/verify-corpus-baseline.txt`.

The lane's own logic is exercised here with a STUBBED runner, so the ~28-minute release gate is
not the price of testing the comparison that wraps it. A lane whose logic can only be exercised by
paying its full cost is one whose logic never gets exercised - and the first version of this
script counted rows containing `::` and reported 3 for a corpus of 5, because two dead selectors
were a `-k` pattern and a bare file target.

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LANE = REPO / "tools" / "verify-corpus.sh"

#: Five dead stamps, of which only THREE carry `::`. This is the real corpus shape as of
#: 2026-08-11 - a `-k` pattern and a bare file target have no node address - and it is what makes
#: "read the tool's own total" distinguishable from "count the rows that look like nodes".
_STAMPS_OUT = textwrap.dedent("""\
    verify-stamps: 5 stamped AC(s) resting on a selector that resolves to nothing - the stamp is STALE, not green
    US0063 AC2: stamped verified, but its verifier selects nothing
        pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_check.py
    US0273 AC2: stamped verified, but its verifier selects nothing
        pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_preflight_writes_nothing
    US0473 AC4: stamped verified, but its verifier selects nothing
        pytest tools/tests/test_check_budgets.py::ReferenceSprintCeilingTests::test_x
    BG0357 AC4: stamped verified, but its verifier selects nothing
        pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::KilledMutantsCarryTheirKillerTests::test_y
    BG0357 AC5: stamped verified, but its verifier selects nothing
        pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::KilledMutantsCarryTheirKillerTests::test_z
""")


class CorpusVerifyBaselineTests(unittest.TestCase):

    def _run(self, stamps_out: str, baseline: str, arg: str = "stamps"):
        """Drive the lane with a stub standing in for the Python runner it shells."""
        tmp = Path(tempfile.mkdtemp(prefix="verify_corpus_"))
        stub = tmp / "stub.py"
        # The stub ignores its arguments and prints the supplied output. It stands in for
        # `python3 <script> stamps ...`, which is how the lane invokes the real runner.
        stub.write_text("import sys\nsys.stdout.write(%r)\n" % stamps_out)
        runner = tmp / "runner.sh"
        runner.write_text(f'#!/usr/bin/env bash\nexec {sys.executable} "{stub}"\n')
        runner.chmod(0o755)
        bfile = tmp / "baseline.txt"
        bfile.write_text(baseline)
        env = {**os.environ, "PYTHON": str(runner), "VERIFY_CORPUS_BASELINE": str(bfile)}
        return subprocess.run(["bash", str(LANE), arg], capture_output=True, text=True,
                              env=env, cwd=str(REPO), check=False, timeout=300)

    def test_the_count_is_the_tools_own_total_not_a_count_of_node_shaped_rows(self) -> None:
        """The bug this lane shipped with. Five dead stamps, three of which carry `::` - a reader
        that counts rows reports 3 against a baseline of 5 and blocks on a defect nobody has."""
        r = self._run(_STAMPS_OUT, "dead-stamps|5|the stamps\n")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("dead-stamps: 5 (baseline 5)", r.stdout)

    def test_a_count_above_the_baseline_blocks(self) -> None:
        r = self._run(_STAMPS_OUT, "dead-stamps|4|the stamps\n")
        self.assertNotEqual(0, r.returncode)
        self.assertIn("NEW one(s)", r.stdout + r.stderr)

    def test_a_count_below_the_baseline_also_blocks(self) -> None:
        """A baseline that only ever tolerates is one that never empties, so good news must be
        BANKED in the same commit rather than left as credit that could admit a later defect."""
        r = self._run(_STAMPS_OUT, "dead-stamps|6|the stamps\n")
        self.assertNotEqual(0, r.returncode)
        self.assertIn("BANKED", r.stdout + r.stderr)

    def test_a_missing_total_is_refused_rather_than_read_as_zero(self) -> None:
        """A sweep that died before reporting and a sweep that found nothing are different facts.
        Collapsing them into 0 would turn every crash into a passing lane."""
        r = self._run("Traceback (most recent call last):\n  ImportError: no module\n",
                      "dead-stamps|5|the stamps\n")
        self.assertNotEqual(0, r.returncode)
        self.assertIn("did not complete", r.stdout + r.stderr)

    def test_a_baseline_row_that_is_missing_is_refused(self) -> None:
        """A metric with no row must not silently pass - that is how a lane ends up tolerating
        everything it forgot to record."""
        r = self._run(_STAMPS_OUT, "# only a comment\n")
        self.assertNotEqual(0, r.returncode)
        self.assertIn("no baseline row", r.stdout + r.stderr)

    # --- the red-criteria half, which no test reached until an independent pass ran the lane ---

    def _run_full(self, gate_out: str, baseline: str):
        """Drive `verify-corpus.sh full`, discriminating the two runners the lane shells.

        `full` calls `verify_ac.py stamps` and then `gate.py --release` through the same `$PYTHON`,
        so a stub that ignores its arguments answers both with one string and the red half is
        never really exercised. That is exactly how the red half shipped with two defects and a
        green suite: every test here passed `stamps` and none passed `full`.
        """
        tmp = Path(tempfile.mkdtemp(prefix="verify_corpus_full_"))
        stub = tmp / "stub.py"
        stub.write_text(
            "import sys\n"
            "argv = ' '.join(sys.argv)\n"
            "sys.stdout.write(%r if 'verify_ac' in argv else %r)\n" % (_STAMPS_OUT, gate_out))
        runner = tmp / "runner.sh"
        runner.write_text(f'#!/usr/bin/env bash\nexec {sys.executable} "{stub}" "$@"\n')
        runner.chmod(0o755)
        bfile = tmp / "baseline.txt"
        bfile.write_text(baseline)
        env = {**os.environ, "PYTHON": str(runner), "VERIFY_CORPUS_BASELINE": str(bfile)}
        return subprocess.run(["bash", str(LANE), "full"], capture_output=True, text=True,
                              env=env, cwd=str(REPO), check=False, timeout=300)

    #: The shape `gate.py` actually renders when the corpus is clean. The lane read `[ OK ] verify`,
    #: a string that occurs nowhere in the tree, so its green path was unreachable.
    _GATE_PASS = "  [PASS] verify [2145.0s]: 0 red AC(s) [669 stories, 1899 executable AC(s)]\n"

    #: A red run whose detail carries the unspecified clause FIRST. That clause contains colons of
    #: its own (`no Verify: line`, `Verify: manual`), which is what defeated the anchored parse.
    _GATE_RED_WITH_UNSPECIFIED = (
        "  [FAIL] verify [2145.0s]: 3 story/stories with an unspecified AC (no Verify: line - an "
        "omitted verifier is not a passed one; author one or mark it `Verify: manual`): US0001, "
        "US0002, US0003; 58 red AC(s): US0063 AC2, US0273 AC2 [669 stories, 1899 executable "
        "AC(s) in 2145s (batched)]\n")

    _GATE_RED_PLAIN = "  [FAIL] verify [2145.0s]: 58 red AC(s): US0063 AC2 [669 stories]\n"

    #: The shape BG0592 introduced: an exclusion clause carrying its own "red count"-adjacent
    #: wording and a comma-separated ledger, printed AFTER the red clause. This suite exists
    #: because this parse broke once already on a clause it had not been shown, so a new clause
    #: arrives with a fixture rather than with a hope.
    _GATE_RED_WITH_EXCLUSIONS = (
        "  [FAIL] verify [2145.0s]: 58 red AC(s): US0063 AC2, US0273 AC2; 67 failing AC(s) on "
        "stories claiming NO completion - unbuilt or abandoned, not a regression, so outside the "
        "corpus red count: US0625::AC1 (pytest x) [Ready], US0482::AC2 (pytest y) [Superseded] "
        "[670 stories, 1943 executable AC(s) in 2145s (batched)]\n")

    def test_a_clean_verify_lane_is_read_as_zero_rather_than_as_a_crash(self) -> None:
        """The end state the baseline exists to force. Reading a marker the gate never prints made
        the green path unreachable: at `red-criteria|0` the lane could only ever have refused."""
        r = self._run_full(self._GATE_PASS, "dead-stamps|5|s\nred-criteria|0|r\n")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("red-criteria: 0 (baseline 0)", r.stdout)

    def test_the_red_count_is_read_when_an_unspecified_clause_precedes_it(self) -> None:
        """The live shape. An anchored walk from the lane name cannot cross the first clause's own
        colons, so it returned empty and the lane refused as 'did not complete' with the real
        count sitting in the output it had just printed."""
        r = self._run_full(self._GATE_RED_WITH_UNSPECIFIED, "dead-stamps|5|s\nred-criteria|58|r\n")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("red-criteria: 58 (baseline 58)", r.stdout)

    def test_the_red_count_is_read_from_a_plain_detail_too(self) -> None:
        """The positive control. Without it, a parser that matched nothing at all would pass the
        test above for the wrong reason."""
        r = self._run_full(self._GATE_RED_PLAIN, "dead-stamps|5|s\nred-criteria|58|r\n")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("red-criteria: 58 (baseline 58)", r.stdout)

    def test_the_red_count_is_read_past_an_exclusion_clause(self) -> None:
        """MUTANT: let the red-count walk run to the end of the detail instead of stopping at the
        first `N red AC` match.

        The exclusion clause BG0592 added sits AFTER the red clause and contains the words
        "corpus red count" plus a second per-AC list. A greedy or last-match read picks up the
        wrong number, and the failure mode is the worst available: the lane reports a plausible
        count and nobody re-derives it.
        """
        r = self._run_full(self._GATE_RED_WITH_EXCLUSIONS, "dead-stamps|5|s\nred-criteria|58|r\n")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("red-criteria: 58 (baseline 58)", r.stdout)

    def test_the_exclusion_count_is_never_mistaken_for_the_red_count(self) -> None:
        """THE DISCRIMINATOR. The exclusion clause's own number (67) must not be readable as the
        metric. Baselined at 67, this run must BLOCK rather than report a tidy match."""
        r = self._run_full(self._GATE_RED_WITH_EXCLUSIONS, "dead-stamps|5|s\nred-criteria|67|r\n")
        self.assertNotEqual(0, r.returncode, r.stdout + r.stderr)

    def test_a_rise_in_red_criteria_blocks(self) -> None:
        r = self._run_full(self._GATE_RED_PLAIN, "dead-stamps|5|s\nred-criteria|57|r\n")
        self.assertNotEqual(0, r.returncode)
        self.assertIn("NEW one(s)", r.stdout + r.stderr)

    def test_a_gate_that_died_before_reporting_is_refused_not_read_as_zero(self) -> None:
        """A crash and a clean corpus must not collapse into the same number."""
        r = self._run_full("Traceback (most recent call last):\n  RuntimeError\n",
                           "dead-stamps|5|s\nred-criteria|58|r\n")
        self.assertNotEqual(0, r.returncode)
        self.assertIn("did not complete", r.stdout + r.stderr)

    def test_the_committed_baseline_names_both_metrics(self) -> None:
        """The shipped baseline must carry a row per metric the lane reads, or the scheduled run
        fails on its first invocation for a reason that looks like a defect in the corpus."""
        text = (REPO / "tools" / "verify-corpus-baseline.txt").read_text(encoding="utf-8")
        rows = {ln.split("|")[0] for ln in text.splitlines()
                if ln.strip() and not ln.startswith("#")}
        self.assertEqual({"red-criteria", "dead-stamps"}, rows)


if __name__ == "__main__":
    unittest.main()
