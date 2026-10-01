"""US0973: the help, references and comments describe what the tools do today.

Each criterion reads the shipped text, or runs the shipped command, and checks it against what
the tool does: `status.py pillars` prints no weighted health score; the waiver example carries
the `--rationale` the verb requires; the close no longer refuses on `unanswered`; the build
render names no contract above it when nothing is above; no dead `ReviewLedgerError` handler
remains; `init` writes `.version`; the CI and hook snippets resolve their script through
`$CLAUDE_SKILL_DIR`; and `critic.py record --help` names the `\\;` escape.
"""
# test-census-subject: .claude/skills/sdlc-studio/help/gate.md
from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
SCRIPTS = SKILL / "scripts"


def _read(rel: str) -> str:
    return (SKILL / rel).read_text(encoding="utf-8")


def _run(*argv: str) -> str:
    r = subprocess.run([sys.executable, *argv], capture_output=True, text=True, timeout=120)
    return r.stdout + r.stderr


class DocsTellTruthTests(unittest.TestCase):

    def test_status_help_claims_no_health_score(self) -> None:
        """AC1. MUTANT: HEAD's `Health score: Weighted average` line in the pillar section."""
        text = _read("help/status.md")
        self.assertNotRegex(text, r"(?i)health score")
        self.assertNotRegex(text, r"(?i)weighted average")
        self.assertIn("per-type percentage", text)

    def test_examples_and_guides_match_the_tools(self) -> None:
        """AC2. MUTANTS: (1) the waiver example without `--rationale`; (2) help/sprint.md saying
        the close would have refused on `unanswered`; (3) the build render pointing at a
        contract above it; (4) a reading guide drifting from its reference."""
        self.assertIn("0 drift item(s)", _run(str(SCRIPTS / "docgen.py"), "reading-guides",
                                               "--check"))
        waive = re.search(r"`decisions\.py waive[^`]*`", _read("reference-sprint.md"))
        self.assertTrue(waive, "the waiver example is gone")
        self.assertIn("--rationale", waive.group(0))
        sprint_help = " ".join(_read("help/sprint.md").split())
        self.assertNotIn("the close would have refused on", sprint_help)
        render = _run(str(SCRIPTS / "persona_resolve.py"), "resolve", "--seat", "engineering",
                      "--render", "build", "--root", str(SKILL.parents[2]))
        self.assertIn("disposition layer ONLY", render, "premise: the build render printed")
        self.assertNotIn("contract above", render)

    def test_no_dead_ledger_error_handler_remains(self) -> None:
        """AC3. MUTANTS: (1) a `ReviewLedgerError` definition or catch left in place; (2) the
        project_upgrade docstring saying init writes no `.version`."""
        for rel in ("scripts/sprint.py", "scripts/lib/run_state.py"):
            self.assertNotIn("ReviewLedgerError", _read(rel), rel)
        upgrade = " ".join(_read("scripts/project_upgrade.py").split())
        self.assertNotIn("but no `.version`", upgrade)
        self.assertNotIn("has no `.version` yet", upgrade)
        self.assertIn("`init` writes `.version`", upgrade)

    def test_copied_snippets_run_and_the_escape_is_named(self) -> None:
        """AC4. MUTANTS: (1) a CI or hook snippet naming `.claude/skills/...` directly; (2) the
        `--issues` help silent on `\\;`."""
        gate = _read("help/gate.md")
        wiring = gate.split("## CI wiring", 1)[1]
        commands = [ln for ln in wiring.splitlines()
                    if re.search(r"python3 \S*scripts/(gate|engagement_floor)\.py", ln)]
        self.assertEqual(4, len(commands), commands)
        for ln in commands:
            self.assertIn("$CLAUDE_SKILL_DIR/scripts/", ln)
            self.assertNotIn(".claude/skills/", ln)
        help_text = " ".join(_run(str(SCRIPTS / "critic.py"), "record", "--help").split())
        self.assertIn("\\;", help_text)


if __name__ == "__main__":
    unittest.main()
