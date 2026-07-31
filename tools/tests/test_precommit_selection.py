"""The pre-commit gate's unit-suite selection rule (US0220).

The hook skips the ~2,800-test unit run for a change that cannot alter a test outcome.
Two ways that goes wrong, and both are tested here: skipping something that CAN break a
test (a false green), and skipping SILENTLY (indistinguishable from having run and
passed - the state in which a real regression ships unnoticed).

The rule was one grep pattern in the hook, naming scripts/, templates/ and tools/ by
hand. US0368 replaced it with a set MEASURED from what the suites read, because a hand
list is a lower bound - the suites also read the hooks, the workflow file, install.sh,
package.json, reference docs, help pages and the shipped artefacts. These tests drive the
shipped hook's own selector, so a change that widens or narrows the skip has to come here
first - the hook is the artefact, not a copy of it.
"""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GITHOOKS = REPO / ".githooks"
HOOK = GITHOOKS / "pre-commit"
GATE = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts" / "gate.py"
#: The suites themselves run in `commit-msg`, behind the message rules (US0372): git runs
#: `pre-commit` before the commit message exists, so nothing inside it can check the
#: message. `pre-commit` still owns the SELECTION rule tested here and hands its verdict
#: over; the wiring tests below therefore read whichever hook now carries each half.
MSG_HOOK = GITHOOKS / "commit-msg"


def _selects(path: str) -> bool:
    """True when `path` would trigger the unit suites, via the call the hook makes."""
    proc = subprocess.run([sys.executable, str(GATE), "--root", str(REPO),
                           "--test-relevant"],
                          input=path + "\n", text=True, capture_output=True)
    assert proc.returncode in (0, 1), (
        f"the selector failed rather than answering: {proc.stderr.strip()}")
    return proc.returncode == 0


class RunTests(unittest.TestCase):
    """AC2: anything that can change a test outcome must force the full suite."""

    def test_script_change_runs_the_suite(self) -> None:
        self.assertTrue(_selects(".claude/skills/sdlc-studio/scripts/gate.py"))

    def test_skill_test_change_runs_the_suite(self) -> None:
        self.assertTrue(_selects(".claude/skills/sdlc-studio/scripts/tests/test_gate.py"))

    def test_template_change_runs_the_suite(self) -> None:
        # several skill tests assert over the shipped templates
        self.assertTrue(_selects(".claude/skills/sdlc-studio/templates/core/story.md"))

    def test_tools_change_runs_the_suite(self) -> None:
        self.assertTrue(_selects("tools/check_links.py"))

    def test_tools_test_change_runs_the_suite(self) -> None:
        self.assertTrue(_selects("tools/tests/test_gate_timing.py"))

    def test_a_doc_a_test_reads_runs_the_suite(self) -> None:
        """US0368: the hand list stopped at scripts/templates/tools, so a reference doc a
        test asserts over took the docs-only fast path and skipped that test. Now measured:
        `reference-sprint.md` is read by test_docs_single_writer.py, so it selects."""
        self.assertTrue(_selects(".claude/skills/sdlc-studio/reference-sprint.md"))
        self.assertTrue(_selects(".claude/skills/sdlc-studio/help/sprint.md"))

    def test_a_hook_a_test_reads_runs_the_suite(self) -> None:
        """The hooks assert over themselves - a change to one can break its own suite, and
        the old regex named none of them."""
        self.assertTrue(_selects(".githooks/pre-commit"))


class SkipTests(unittest.TestCase):
    """AC1: only files that genuinely cannot alter a test outcome may skip."""

    def test_readme_skips(self) -> None:
        self.assertFalse(_selects("README.md"))

    def test_changelog_skips(self) -> None:
        self.assertFalse(_selects("CHANGELOG.md"))

    def test_a_reference_doc_no_test_reads_skips(self) -> None:
        # reference-philosophy.md is asserted over by no shipped suite, so it stays skippable.
        self.assertFalse(_selects(".claude/skills/sdlc-studio/reference-philosophy.md"))

    def test_a_help_doc_no_test_reads_skips(self) -> None:
        self.assertFalse(_selects(".claude/skills/sdlc-studio/help/cr.md"))

    def test_the_skip_is_announced(self) -> None:
        """A silent skip is indistinguishable from a pass - it must be printed."""
        text = HOOK.read_text(encoding="utf-8")
        self.assertRegex(text, r"SKIP.*unit suites")
        self.assertIn("no test-relevant file staged", text)

    def test_the_hook_calls_the_measured_selector(self) -> None:
        """The selection rule is the measurement, not a regex the hook keeps of its own -
        that regex is exactly the hand enumeration US0368 removed."""
        self.assertIn("--test-relevant", HOOK.read_text(encoding="utf-8"))


class SelectionReachesTheRunnersTests(unittest.TestCase):
    """The selection was COMPUTED and then discarded, for the whole life of the mechanism.

    `commit-msg` deleted the pre-commit handover and read the selectors out of that same file
    forty lines later, so `selectors` was always empty, every run recorded `verdict-mode full`,
    and `total.tests` in the recorded timing history read the full suite on every commit. The
    selection logic - `select_tests`, `suite_read_map`, `_import_graph`, `test_relevant_paths` -
    ran, produced an answer, and nothing consumed it. The suites are 86% of the gate.

    These pin the two halves that made it inert: the ordering, and whether a runner handed a
    selection actually narrows what it runs."""

    def test_the_handover_is_READ_before_it_is_deleted(self) -> None:
        text = MSG_HOOK.read_text(encoding="utf-8")
        read_at = text.index("suite-selector=")
        del_at = text.index('rm -f "$handoff"')
        self.assertLess(read_at, del_at,
                        "commit-msg deletes the handover before reading the selection out of "
                        "it, so `selectors` is always empty and every commit runs everything")

    def test_the_selection_is_PASSED_to_the_skill_runner(self) -> None:
        text = MSG_HOOK.read_text(encoding="utf-8")
        self.assertIn("bash tools/skill-tests.sh \"$skill\" $skill_sel", text,
                      "the skill lane is invoked with no selection argument, so a computed "
                      "selection cannot narrow it however correct it is")

    def test_a_selected_run_runs_FEWER_tests_than_the_full_suite(self) -> None:
        """The behaviour, not the wiring. Driving the shipped runner both ways is the only
        thing that distinguishes a selection that is passed from one that is passed and
        ignored - which is the state this whole class exists to catch."""
        skill = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
        one = skill / "tests" / "test_provenance.py"
        # FAIL rather than skip on an absent module. The first version of this test named a
        # module that lives under tools/tests, so it skipped - and a skip reads as a pass, so
        # it reported green against the very mutant it was written to kill.
        self.assertTrue(one.is_file(),
                        f"{one} is not present, so this test proves nothing - point it at a "
                        f"module that exists rather than letting it skip")
        proc = subprocess.run(["bash", str(REPO / "tools" / "skill-tests.sh"),
                               str(skill), str(one)],
                              cwd=REPO, text=True, capture_output=True)
        ran = [ln for ln in proc.stdout.splitlines() + proc.stderr.splitlines()
               if ln.startswith("Ran ")]
        self.assertTrue(ran, f"the runner reported no test count: {proc.stderr[-400:]}")
        count = int(ran[-1].split()[1])
        self.assertGreater(count, 0, "a selected run collected nothing")
        self.assertLess(count, 1000,
                        f"a one-module selection ran {count} tests - the selection reached "
                        f"the runner and was ignored, which is the defect this pins")


class WiringTests(unittest.TestCase):
    """AC3: US0219's measurement must actually be called by the hook pair, not merely exist."""

    def test_hook_estimates_before_running(self) -> None:
        self.assertIn("gate_timing.py estimate", MSG_HOOK.read_text(encoding="utf-8"))

    def test_hook_records_both_suites(self) -> None:
        text = MSG_HOOK.read_text(encoding="utf-8")
        self.assertIn("record --suite skill-tests", text)
        self.assertIn("record --suite tool-tests", text)

    def test_timing_never_blocks_the_commit(self) -> None:
        """Every gate_timing call must swallow its own failure: an advisory
        measurement that can fail a commit is worse than no measurement."""
        for hook in (HOOK, MSG_HOOK):
            for line in hook.read_text(encoding="utf-8").splitlines():
                if "gate_timing.py" in line:
                    self.assertIn("2>/dev/null", line,
                                  f"unguarded timing call in {hook.name}: {line.strip()}")


if __name__ == "__main__":
    unittest.main()
