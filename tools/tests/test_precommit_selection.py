"""The pre-commit gate's unit-suite selection rule (US0220).

The hook skips the ~2,800-test unit run for a change that cannot alter a test outcome.
Two ways that goes wrong, and both are tested here: skipping something that CAN break a
test (a false green), and skipping SILENTLY (indistinguishable from having run and
passed - the state in which a real regression ships unnoticed).

The rule is one grep pattern in the hook. These tests read the shipped hook and exercise
that pattern directly, so a change to the hook that widens or narrows the skip has to
come here first - the hook is the artefact, not a copy of it.
"""
from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

GITHOOKS = Path(__file__).resolve().parents[2] / ".githooks"
HOOK = GITHOOKS / "pre-commit"
#: The suites themselves run in `commit-msg`, behind the message rules (US0372): git runs
#: `pre-commit` before the commit message exists, so nothing inside it can check the
#: message. `pre-commit` still owns the SELECTION rule tested here and hands its verdict
#: over; the wiring tests below therefore read whichever hook now carries each half.
MSG_HOOK = GITHOOKS / "commit-msg"


def _pattern() -> str:
    """The `test_relevant` regex as the hook actually defines it."""
    text = HOOK.read_text(encoding="utf-8")
    m = re.search(r"^test_relevant='([^']+)'", text, re.M)
    assert m, "the hook must define test_relevant='<regex>' - selection rule not found"
    return m.group(1)


def _selects(path: str) -> bool:
    """True when `path` would trigger the unit suites, via the same grep the hook runs."""
    proc = subprocess.run(["grep", "-qE", _pattern()], input=path + "\n",
                          text=True, capture_output=True)
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


class SkipTests(unittest.TestCase):
    """AC1: only files that genuinely cannot alter a test outcome may skip."""

    def test_readme_skips(self) -> None:
        self.assertFalse(_selects("README.md"))

    def test_changelog_skips(self) -> None:
        self.assertFalse(_selects("CHANGELOG.md"))

    def test_reference_doc_skips(self) -> None:
        self.assertFalse(_selects(".claude/skills/sdlc-studio/reference-sprint.md"))

    def test_help_doc_skips(self) -> None:
        self.assertFalse(_selects(".claude/skills/sdlc-studio/help/sprint.md"))

    def test_artefact_skips(self) -> None:
        self.assertFalse(_selects("sdlc-studio/stories/US0220-x.md"))

    def test_the_skip_is_announced(self) -> None:
        """A silent skip is indistinguishable from a pass - it must be printed."""
        text = HOOK.read_text(encoding="utf-8")
        self.assertRegex(text, r"SKIP.*unit suites")
        self.assertIn("no test-relevant file staged", text)


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
