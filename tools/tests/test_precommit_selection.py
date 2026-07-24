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
