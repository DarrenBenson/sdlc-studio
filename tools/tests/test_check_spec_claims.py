"""Guards over what the repo's own documents claim: SKILL.md's sections and the lint chain. The
AGENTS.md lane roster pins went with the roster (US0901): the hooks list their own lanes
(`--list`). The doctrine's repair-evidence guards went with the repair gate they named (US0935).

The module is named for `tools/check_spec_claims.py`, which US0879 deleted with its commit lane:
it checked the specs' countable and timing claims against a census, caught nothing, and its
timing claims deadlocked every fresh worktree (BG0746). The tests of the checker itself went
with it, and the criteria that named them are retired.
"""
# test-census-subject: .claude/skills/sdlc-studio/SKILL.md
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class LintAggregateTests(unittest.TestCase):
    """US0655 AC2: the `lint` CHAIN calls `lint:disclosure`, which it did not."""

    def test_the_lint_chain_calls_disclosure(self) -> None:
        """`lint:disclosure` has existed as a script KEY all along; only the aggregate omitted
        it, so a checker with 28 advisory findings was one line from being read and was not.
        Asserting the key exists is green today with nothing changed, which is a criterion that
        cannot fail.

        Mutant: leave `lint:disclosure` defined as a key but absent from the `lint` chain.
        """
        import json
        pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["scripts"]
        self.assertIn("lint:disclosure", pkg, "the disclosure lane is not defined at all")
        self.assertIn("lint:disclosure", pkg["lint"],
                      "the `lint` chain does not call `lint:disclosure`, so the checker runs "
                      "nowhere and reports nothing however good it is")


class SkillSectionTests(unittest.TestCase):
    """US0659 AC1/AC2: SKILL.md carries the sections its own checklist requires."""

    def test_skill_md_carries_the_sections_its_own_checklist_requires(self) -> None:
        """`best-practices/claude-skill.md` requires a "See Also" section and gives a single
        vague sentence as its BAD trigger example - labelled "Too vague, no trigger keywords",
        so the fault it names is VAGUENESS. The assertion is on trigger phrases being present,
        which is the rule, rather than on the shape of a list, which is a proxy that would
        outlive the reason for it.

        Mutant: remove the `## See Also` section.
        Mutant: revert `When to Use` to a single vague sentence with no trigger phrases.
        """
        skill = (ROOT / ".claude/skills/sdlc-studio/SKILL.md").read_text(encoding="utf-8")
        checklist = (ROOT / ".claude/skills/sdlc-studio/best-practices/claude-skill.md"
                     ).read_text(encoding="utf-8")
        self.assertIn("See Also", checklist, "the checklist no longer requires this section")
        self.assertIn("## See Also", skill,
                      "SKILL.md fails the checklist it ships - the cheapest possible finding "
                      "and the most embarrassing to leave")
        when = skill[skill.index("## When to Use"):]
        when = when[:when.index("\n## ", 5)]
        phrases = [ln for ln in when.splitlines() if ln.strip().startswith("- ")]
        self.assertGreaterEqual(len(phrases), 5,
                                "`When to Use` names no trigger phrases, which is the shape "
                                "the skill's own guidance gives as its bad example")

    def test_the_four_top_level_documents_are_in_the_loading_guide(self) -> None:
        """The doctrine calls the PRD, TRD, TSD and story the top-level human levers, and an
        agent following the Progressive Loading Guide was told about none of them.

        Mutant: drop one of the four rows.
        """
        skill = (ROOT / ".claude/skills/sdlc-studio/SKILL.md").read_text(encoding="utf-8")
        guide = skill[skill.index("## Progressive Loading Guide"):]
        guide = guide[:guide.index("\n## ", 5)]
        for ref in ("reference-prd.md", "reference-trd.md", "reference-tsd.md",
                    "reference-story.md"):
            with self.subTest(reference=ref):
                self.assertIn(ref, guide,
                              f"{ref} is a top-level document the loading guide never names")


if __name__ == "__main__":
    unittest.main()
