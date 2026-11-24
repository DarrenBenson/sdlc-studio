"""A criterion heading carrying text after its id still opens its own criterion."""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib import sdlc_md  # noqa: E402
import verify_ac  # noqa: E402

STORY = """# US9999: x

> **Status:** Draft

## Acceptance Criteria

### AC1: first

- **Verify:** file a.txt

### AC2: second

- **Verify:** file b.txt

### AC3 (DEFERRED)

- **Verify:** manual
"""

TEN = """# US9999: x

> **Status:** Draft

## Acceptance Criteria

### AC1: one

- **Verify:** file a.txt

### AC10: ten

- **Verify:** file b.txt
"""

WITHDRAWN = """# BG9998: x

> **Status:** Fixed

## Acceptance Criteria

### AC4

- **Verify:** file a.txt

### AC5

- **Verify:** file b.txt

### AC5 and AC6 were WITHDRAWN, and this is why

Prose, with no Verify line of its own.
"""

TEST_PLAN = """# US9998: x

> **Status:** Done

## Acceptance Criteria

### AC1: the plan

- **Verify:** file a.txt

## Test Plan

### AC1 - exactly one row per criterion, count enforced not intended

- **Verify:** file never-run.txt
"""


class AcHeadingWithSuffixTests(unittest.TestCase):
    def test_a_suffixed_heading_opens_its_own_criterion(self):
        blocks = {b.ac_id: b for b in verify_ac.parse_story(STORY)}
        self.assertEqual(list(blocks), ["AC1", "AC2", "AC3"])
        self.assertEqual(blocks["AC3"].verifier, "manual")
        self.assertEqual(blocks["AC3"].title, "(DEFERRED)")
        self.assertEqual(blocks["AC2"].verifier, "file b.txt")
        self.assertEqual(blocks["AC1"].verifier, "file a.txt")
        # the shared reader agrees with the verifier
        self.assertEqual(sdlc_md.extract_ac_id("### AC3 (DEFERRED)"), ("AC3", "(DEFERRED)"))

    def test_ac10_is_not_ac1_with_a_suffix(self):
        blocks = verify_ac.parse_story(TEN)
        self.assertEqual([b.ac_id for b in blocks], ["AC1", "AC10"])
        self.assertEqual(sdlc_md.extract_ac_id("### AC10: title"), ("AC10", "title"))
        self.assertEqual(sdlc_md.extract_ac_id("### AC1: title"), ("AC1", "title"))
        self.assertEqual(sdlc_md.extract_ac_id("### AC1"), ("AC1", ""))
        # a lettered id keeps its letter, with or without a suffix
        self.assertEqual(sdlc_md.extract_ac_id("### AC1a: title"), ("AC1a", "title"))
        self.assertEqual(sdlc_md.extract_ac_id("### AC2b (DEFERRED)"), ("AC2b", "(DEFERRED)"))

    def test_prose_headings_that_start_with_an_id_are_not_criteria(self):
        # the real headings that the first widening read as criteria: US0629's Test Plan rows
        # and BG0573's withdrawal note inside its Acceptance Criteria section
        for line in ("### AC1 - exactly one row per criterion, count enforced not intended",
                     "### AC2 - UNBLOCKED: BG0525 restated the criterion in decidable terms",
                     "### AC3 - the plan lives in the unit's file; idempotent",
                     "### AC5 and AC6 were WITHDRAWN, and this is why",
                     "### AC4 (DEFERRED) and more prose", "### AC4 (DEFERRED"):
            with self.subTest(line=line):
                self.assertIsNone(sdlc_md.extract_ac_id(line))
        blocks = verify_ac.parse_story(WITHDRAWN)
        self.assertEqual([b.ac_id for b in blocks], ["AC4", "AC5"])
        plan = verify_ac.parse_story(TEST_PLAN)
        self.assertEqual([b.ac_id for b in plan], ["AC1"])

    def test_a_heading_that_only_starts_like_an_id_opens_nothing(self):
        for line in ("### AC1xyz", "### AC", "### ACE: heading", "### ACs"):
            with self.subTest(line=line):
                self.assertIsNone(sdlc_md.extract_ac_id(line))


if __name__ == "__main__":
    unittest.main()
