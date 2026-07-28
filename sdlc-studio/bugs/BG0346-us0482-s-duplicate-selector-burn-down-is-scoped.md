# BG0346: US0482's duplicate-selector burn-down is scoped to stories while the ratchet it serves covers stories and bugs

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 2
> **Affects:** sdlc-studio/stories/US0482-the-baselined-duplicate-verify-groups-are-split-into.md, tools/tests/test_ratchet_story_agreement.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (independent adversarial review of the residue stories); agent; skill v5.0.0

## Summary

Measured: `verify_ac.duplicate_verifiers` over sdlc-studio/stories gives 19 groups, 13 intra-record. Over stories AND bugs - which is the scope US0461's ratchet declares, precisely so a shared selector cannot be parked in a bug - it gives 31 groups, 20 intra-record, with seven intra-record groups living in bugs. US0482 must shrink a baseline holding 31 while its Affects names only sdlc-studio/stories, and its AC1 claims the lint runs over the workspace. It also omits the baseline file it must edit, and its AC2 asserts 'the four groups unanswerable by collection' - a set named nowhere in the repository, so the test has no reference and either hardcodes four ids nobody recorded or passes vacuously.

## Steps to Reproduce

1. Run `verify_ac.duplicate_verifiers` over sdlc-studio/stories: 19 groups, 13 intra-record. 2. Run it over stories and bugs: 31 groups, 20 intra-record, seven of them in bugs. 3. Read US0461 AC1: the ratchet's scope is stories and bugs. 4. Read US0482's Affects: stories only, and no baseline file. 5. Search the repo for the four unanswerable groups: named nowhere.

## Proposed Fix

Widen US0482 to stories and bugs, add the baseline file to its Affects, resize from 5 to 8 for 20 groups, and replace the invented four with a criterion that identifies the unanswerable groups by running the resolver rather than by citing a count.

## Acceptance Criteria

### AC1: the burn-down story is scoped to the same corpus as the ratchet it serves

- **Given** the defect as filed in Steps to Reproduce
- **When** the repair is in place
- **Then** the behaviour is the one the Proposed Fix describes, proven by a test written red before the fix
- **Proven by:** pytest tools/tests/test_ratchet_story_agreement.py, written red before the fix and green after
- **Verified:** yes (2026-07-28, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (independent adversarial review of the residue stories) | Filed |
| 2026-07-28 | Claude Opus 5 | Fixed: US0482 widened to stories and bugs, baseline file declared, resized 5 to 8, and the invented four unanswerable groups replaced by a resolver-derived criterion. Counts re-measured (19/13 stories, 31/20 with bugs, 7 intra-record in bugs) and guarded by `tools/tests/test_ratchet_story_agreement.py`. The two evidence directories dropped from Affects - nothing in them changed |
