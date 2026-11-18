"""US1313: this repository's config declares the D0520 component map, and each gate script is high.

D0520 rules the classes: high for gate.py, critic.py, transition.py, sprint.py, verify_ac.py and
the hooks under `.githooks`; elevated for the rest of the skill's scripts; standard for everything
else. The map is `risk.components` in `sdlc-studio/.config.yaml`, keyed by the repository-relative
paths a unit's Affects names, so the criteria's `scripts/gate.py` is
`.claude/skills/sdlc-studio/scripts/gate.py` here. Without the map every unit here reads as
standard, and the high-risk review trigger (D0511) never acts. This module reads the repository's
own config, so it lives here, where nothing installs.

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
# test-census-subject: sdlc-studio/.config.yaml
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"

sys.path.insert(0, str(SCRIPTS))
import critic  # noqa: E402
from lib import risk_class  # noqa: E402

SKILL_SCRIPTS = ".claude/skills/sdlc-studio/scripts"

#: The gates D0520 names, each a file the tree holds today. HAND-MAINTAINED ON PURPOSE: this list
#: is the assertion D0520 makes about which scripts are high, not a mirror of a set the tree owns.
HIGH = tuple(f"{SKILL_SCRIPTS}/{name}" for name in
             ("gate.py", "critic.py", "transition.py", "sprint.py", "verify_ac.py")) + (
    ".githooks/pre-push", ".githooks/pre-commit", ".githooks/commit-msg")
#: The rest of the skill's scripts. `sprint_report.py` shares the stem of `sprint.py`, so a
#: prefix that matched a sibling path would read it as high.
ELEVATED = (f"{SKILL_SCRIPTS}/refine.py", f"{SKILL_SCRIPTS}/sprint_report.py",
            f"{SKILL_SCRIPTS}/lib/risk_class.py")
#: Everything else, including the skill's own pages and this repository's CI guards.
STANDARD = ("docs/evidence.md", ".claude/skills/sdlc-studio/help/sprint.md",
            "tools/gate_timing.py", "sdlc-studio/.config.yaml")

_BUG = ("# BG9999: a gate passes work it never judged\n\n> **Status:** Open\n"
        "> **Severity:** High\n> **Affects:** {affects}\n\n## Summary\n\nA summary.\n")


class RepoRiskMapTests(unittest.TestCase):

    def test_the_gate_scripts_are_high_and_the_other_scripts_elevated(self) -> None:
        """AC1. Mutants: a gate script mapped elevated or left out of the map; a misspelt class,
        which the reader keeps as standard with a note; a prefix wide enough to reach the skill's
        pages or a sibling of `sprint.py`; a prefix naming a path the tree no longer holds."""
        rmap = risk_class.load_map(REPO)
        self.assertTrue(rmap.declared, "sdlc-studio/.config.yaml declares no risk.components")
        self.assertEqual((), rmap.notes, "the map reads with notes, so an entry is not honoured")
        for prefix in rmap.components:
            with self.subTest(prefix=prefix):
                self.assertTrue((REPO / prefix).exists(),
                                f"the map names {prefix}, which this tree does not hold")
        for expected, paths in (("high", HIGH), ("elevated", ELEVATED), ("standard", STANDARD)):
            for path in paths:
                with self.subTest(path=path):
                    self.assertEqual(expected, rmap.classify([path])[0],
                                     f"{path} is not classed {expected}")

    def test_a_bug_touching_a_gate_reads_high(self) -> None:
        """AC2. A bug carries no Risk-class stamp, so its class is the map's. Mutants: critic.py
        mapped below high, or no map at all, which reads every unit here as standard. The same
        bug touching only another script, or only a page, is the control on each side."""
        gate_bug = _BUG.format(affects=f"{SKILL_SCRIPTS}/critic.py, "
                                       f"{SKILL_SCRIPTS}/tests/test_critic.py")
        self.assertEqual("high", critic.unit_risk_class(REPO, gate_bug))
        self.assertEqual("elevated", critic.unit_risk_class(
            REPO, _BUG.format(affects=f"{SKILL_SCRIPTS}/refine.py")))
        self.assertEqual("standard", critic.unit_risk_class(
            REPO, _BUG.format(affects="docs/evidence.md")))


if __name__ == "__main__":
    unittest.main()
