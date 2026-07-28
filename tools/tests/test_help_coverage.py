"""Behaviour an operator must be able to discover from `help/`, not from the hook.

A policy that lives only in a shell script is a policy nobody can look up. The gate's
boundary rule is the first of these: it decides when a commit pays for the whole suite and
when it pays for a selection, and an operator who cannot read that anywhere will either
distrust the fast commits or assume the slow ones are broken.

These tests pin the DOC against the CODE, not against a phrase: the moments the gate treats
as boundaries are read out of `gate.py` and each one must appear in the help page, so adding
a boundary without documenting it fails here.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
GATE = SKILL / "scripts" / "gate.py"
HELP = SKILL / "help" / "gate.md"


def _gate():
    sys.path.insert(0, str(GATE.parent))
    spec = importlib.util.spec_from_file_location("gate_for_help_coverage", GATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class GatePolicyDocsTests(unittest.TestCase):
    """US0495 AC2: the boundary policy is stated where an operator reads it."""

    def test_the_boundary_policy_is_documented(self) -> None:
        text = HELP.read_text(encoding="utf-8")
        lowered = text.lower()
        self.assertIn("boundary", lowered,
                      "help/gate.md must state that some moments run the full suite")
        for moment in _gate().BOUNDARIES:
            self.assertIn(moment, lowered,
                          f"{moment} is a boundary in gate.py but is not named in "
                          f"help/gate.md - a policy only the hook knows is undiscoverable")
        # Both halves, or the page states only the expensive one and a reader still cannot
        # tell what a plain commit costs.
        self.assertIn("--suite-decision", text,
                      "the command that answers the question must be documented")
        self.assertTrue(
            "selection" in lowered or "selected" in lowered,
            "the page must say that a non-boundary run tests a SELECTION, not everything")
        self.assertIn("--boundary", text,
                      "the flag that declares a boundary must be documented, or the "
                      "policy cannot be invoked deliberately")


if __name__ == "__main__":
    unittest.main()
