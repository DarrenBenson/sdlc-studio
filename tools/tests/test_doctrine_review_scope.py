#!/usr/bin/env python3
"""The shipped doctrine states the review SCOPE rule, not only the review ceremony."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import doctrine_review_scope as drs  # noqa: E402

DOCTRINE = REPO / drs.DOCTRINE_REL


class DoctrineTests(unittest.TestCase):

    def test_the_scope_rule_is_stated(self) -> None:
        """MUTANT: delete rule 19 from reference-doctrine.md. This must go red.

        Verified: with the rule removed the guard fails and restores byte-identical.
        """
        missing = drs.missing_claims(DOCTRINE.read_text(encoding="utf-8"))
        self.assertEqual(
            [], missing,
            f"the doctrine's rules never state {missing} - a consuming project inherits the "
            f"review ceremony without the bound on what it may judge")

    def test_deleting_the_passage_reddens_the_guard(self) -> None:
        """The guard must not be satisfiable by prose ABOUT the change.

        Builds the adversarial case directly: the stating passage removed, and a Revision
        History row describing this very change left in place. A whole-file substring check
        goes green on that row. This one must not, or it pins nothing (BG0457).
        """
        text = DOCTRINE.read_text(encoding="utf-8")
        gutted = text.replace(
            drs.rules_section(text),
            "## The rules\n\n1. **The skill is the operating system.** All work flows "
            "through it.\n")
        gutted += (
            "\n## Revision History\n\n"
            "| Date | Author | Change |\n| --- | --- | --- |\n"
            "| 2026-08-01 | US0582 | State the review scope rule: a review judges the unit's "
            "own `Affects` against the run's base ref, and only a regression or a newly "
            "introduced defect blocks; a pre-existing finding does not block. |\n")
        missing = drs.missing_claims(gutted)
        self.assertEqual(
            sorted(name for name, _ in drs.CLAIMS), sorted(missing),
            "the guard found scope-rule claims outside the rules section - a Revision History "
            "row describing the change would turn it green")

    def test_the_command_exits_non_zero_when_the_rule_is_absent(self) -> None:
        """The guard is a runnable CHECK, not only a test. MUTANT: return 0 unconditionally.

        A rule that matters is enforced by something that can run in a gate, rather than
        living only where a test runner happens to look (`lessons/LL0027`).
        """
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            target = root / drs.DOCTRINE_REL
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("## The rules\n\n1. **Something else.**\n", encoding="utf-8")
            self.assertEqual(1, drs.main(["--root", str(root)]),
                             "a doctrine missing the scope rule exited zero")
            target.write_text(DOCTRINE.read_text(encoding="utf-8"), encoding="utf-8")
            self.assertEqual(0, drs.main(["--root", str(root)]),
                             "the shipped doctrine was refused by its own guard")


if __name__ == "__main__":
    unittest.main()
