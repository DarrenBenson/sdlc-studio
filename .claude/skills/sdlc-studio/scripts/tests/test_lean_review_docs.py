"""US0924: the shipped docs teach only the surviving review path.

One independent reviewer's verdict decides a unit, green `Verify:` selectors are the evidence,
and mutation testing and line coverage are opt-in probes. Every test reads THIS repository's
shipped skill, as the criteria name it; the retired surface is `retired_surface`, the one list
the other doc units import.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import retired_surface  # noqa: E402

# parents: [0] tests [1] scripts [2] the shipped skill.
SKILL = Path(__file__).resolve().parents[2]


def _shipped_docs() -> list[Path]:
    """Every file AC1 scans: SKILL.md, help/, reference-*.md, best-practices/, templates/."""
    return ([SKILL / "SKILL.md"]
            + sorted((SKILL / "help").rglob("*.md"))
            + sorted(SKILL.glob("reference-*.md"))
            + sorted((SKILL / "best-practices").rglob("*.md"))
            + sorted(p for p in (SKILL / "templates").rglob("*") if p.is_file()))


def _read(rel: str) -> str:
    return (SKILL / rel).read_text(encoding="utf-8")


class ReviewDocsTests(unittest.TestCase):

    def test_no_shipped_doc_instructs_a_retired_surface(self) -> None:
        """AC1. MUTANTS: HEAD dee380d9 (about 64 live lines over 27 files); a hand verb list
        missing a registry entry; a ban on the bare phrase 'verification depth'."""
        pats = retired_surface.surfaces()
        # The verbs are the registries' own, not a hand copy that misses a later entry.
        for label in retired_surface.migrate._retired_verbs():
            self.assertIn(label, pats, "a registry verb is missing from the derived surface")
        for key in list(retired_surface.sdlc_md.RETIRED_CONFIG_KEYS) + list(
                retired_surface.sdlc_md.RETIRED_CHECK_IDS):
            self.assertIn(key, pats)
        # The flags are the CHANGELOG's own table rows, each pattern matching its own label.
        flags = retired_surface.flags()
        self.assertTrue(flags, "no retired flag was read from the CHANGELOG")
        for label in flags:
            self.assertRegex(f"`{label}`", pats[label], "a flag pattern misses its own row")
        # Positive controls: the scan catches a live mention and excuses a retired one.
        self.assertTrue(retired_surface.live_mentions(
            "Run `verify_ac.py testplan probe --unit US0001`."))
        self.assertTrue(retired_surface.live_mentions("- **Verification target:** soak"))
        # An unrelated refusal or deletion in the same sentence excuses nothing.
        for leak in ("Brief the seat with `critic.py brief --phase plan-review`; `--tier` is "
                     "refused there.",
                     "Run `verify_ac.py testplan probe --unit <id>` before planning; the gate "
                     "refuses a red criterion.",
                     "Hold a plan review with the seats; nothing is deleted.",
                     "Run `sprint.py close --apply-signoff`, and the gate refuses a red unit."):
            self.assertTrue(retired_surface.live_mentions(leak), leak)
        self.assertFalse(retired_surface.live_mentions(
            "`verify_ac.py testplan` is refused by name."))
        self.assertFalse(retired_surface.live_mentions(
            "These verbs are retired:\n`critic.py signoff` and `sprint.py preflight`."))
        # The tier vocabulary is advice, not a retired surface.
        self.assertFalse(retired_surface.live_mentions(
            "Pick a verification depth tier (smoke, functional, conversational, soak, live): "
            "see reference-test-best-practices.md#verification-depth-tiers."))
        tiers = _read("reference-test-best-practices.md")
        self.assertIn("{#verification-depth-tiers}", tiers, "the tier anchor six docs link")
        for tier in ("smoke", "functional", "conversational", "soak", "live"):
            self.assertIn(f"| **{tier}** |", tiers, "the tier vocabulary is kept as advice")

        found = []
        for path in _shipped_docs():
            text = path.read_text(encoding="utf-8", errors="replace")
            found += [f"{path.relative_to(SKILL)}:{n}: [{label}] {line.strip()[:120]}"
                      for n, label, line in retired_surface.live_mentions(text, pats)]
        self.assertEqual(found, [], f"{len(found)} shipped lines teach a retired surface:\n"
                                    + "\n".join(found))

    def test_the_mutation_help_is_opt_in(self) -> None:
        """AC2. MUTANT: HEAD, titled 'the executable mutation-check gate', whose line 18 says
        'this gate proves they can fail'."""
        text = _read("help/mutation.md")
        title = next(line for line in text.splitlines() if line.startswith("# "))
        body = text.split(title, 1)[1]
        opening = body.split("\n## Quick Reference", 1)[0]
        self.assertNotRegex(title, r"(?i)\bgate\b")
        self.assertIn("opt-in", title + opening)
        self.assertRegex(opening, r"no gate(?: lane)? reads")
        self.assertNotRegex(opening, r"(?i)\bthis gate\b")
        for verb in ("run", "yield", "window", "prefilter"):
            self.assertRegex(text, rf"mutation\.py {verb}\b", f"`{verb}` is undocumented")

    def test_the_templates_carry_no_retired_section(self) -> None:
        """AC3. MUTANTS: HEAD story.md 65-103, story-planning.md 34-44, bug.md 93 and
        definition-of-done.md 38; the fields gone while the tier legends remain."""
        retired = {
            "a Verification target or depth field": r"(?i)verification[ _](?:target|depth)\b"
                                                   r"(?![- ]tiers?\b)|verification_(?:target|depth)",
            "a tier legend telling the author to pick one": r"(?i)verification (?:target|depth) tiers",
            "a Mutation-checked field": r"(?i)mutation[-_]checked|mutation_check_note",
            "a Test Plan section": r"(?im)^#+\s*Test Plan\b",
            "a mutation-evidence section": r"(?i)mutation[- ]evidence",
            "a per-unit sign-off section": r"(?i)^#+.*sign-?off|reviewer of record",
            "a Done criterion requiring a later batch review": r"(?i)batch review",
        }
        for rel in ("templates/core/story.md", "templates/core/story-planning.md",
                    "templates/core/bug.md", "templates/core/definition-of-done.md"):
            text = _read(rel)
            for what, rx in retired.items():
                with self.subTest(template=rel, retired=what):
                    hits = [line for line in text.splitlines() if re.search(rx, line)]
                    self.assertEqual(hits, [], f"{rel} still carries {what}")

    def test_the_epic_help_names_no_missing_verb(self) -> None:
        """AC4. MUTANT: HEAD help/epic.md 159 (`/sdlc-studio test-plan`, a verb SKILL.md never
        routes) and 129 ('Test Plan link')."""
        text = _read("help/epic.md")
        self.assertNotIn("/sdlc-studio test-plan", text)
        self.assertNotIn("/sdlc-studio test-plan", _read("SKILL.md"), "premise: never routed")
        sections = text.split("\n## Examples", 1)[0]
        self.assertIn("- Test Spec link", sections)
        self.assertNotIn("Test Plan link", text)

    def test_no_index_points_at_depth_tiers(self) -> None:
        """AC5. MUTANT: HEAD help/references.md 38 ('choosing **verification depth**') and
        reference-persona-generate.md 361 ('.config.yaml (quality bar, depth tiers)')."""
        for rel in ("help/references.md", "reference-persona-generate.md"):
            text = _read(rel)
            with self.subTest(doc=rel):
                self.assertNotRegex(text, r"(?i)choos\w*\W+(?:a\W+)?verification[- ]depth")
                self.assertNotRegex(text, r"(?i)\.config\.yaml[^\n]*depth tiers?")


if __name__ == "__main__":
    unittest.main()
