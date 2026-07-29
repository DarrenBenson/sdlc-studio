# BG0373: The review-currency carve-out repaired in BG0336 remains story-shaped, so a bug or change request takes a different path

> **Status:** Fixed
> **Verification depth:** functional (premise re-measured across types)
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (RUN-01KYKVZM review carry-forward); agent; skill v5.0.0

## Summary

BG0336 fixed the direction-blindness of the review-currency close-bookkeeping carve-out. The repaired path still reasons in stories: a bug or change request in the same diff is judged by the pre-existing route, so the class of hand-edited status change the bug was filed about is still reachable through a non-story unit.

## Steps to Reproduce

Observed during the RUN-01KYKVZM review of BG0336's repair. The fix is correct for the type it covers; the coverage is the defect.

## Proposed Fix

Apply the carve-out rule by unit rather than by story, so every delivery type takes one path, and assert the property across types rather than for a story fixture.

## Acceptance Criteria

### AC1: the carve-out reads every delivery type's own vocabulary

- **Given** a story, a bug and a change request, each with its own in-flight and terminal statuses
- **When** the review-currency carve-out judges it
- **Then** each close-recorded transition is exempt and each hand-flip is not, judged against the type's own vocabulary rather than a story's
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::CloseCarveOutIsTypeGeneralTests::test_the_carve_out_reads_every_delivery_type
- **Verified:** yes (2026-07-29)

### AC2: every declared type resolves from its directory

- **Given** each entry of the shipped type table
- **When** the review-currency carve-out judges it
- **Then** its directory resolves to that type, because an unresolved type yields no vocabulary and the exemption then stops working for it silently
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::CloseCarveOutIsTypeGeneralTests::test_every_declared_type_resolves_from_its_directory
- **Verified:** yes (2026-07-29)

### AC3: a reopen is never exempt, for any type

- **Given** a move out of a terminal status
- **When** the review-currency carve-out judges it
- **Then** it is judged, for every type - terminal to anything is a reopen and terminal to terminal is a re-labelling, and both are changes a reviewer judges
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::CloseCarveOutIsTypeGeneralTests::test_a_reopen_is_never_exempt_for_any_type
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (RUN-01KYKVZM review carry-forward) | Filed |
| 2026-07-29 | Claude Opus 5 | DID NOT REPRODUCE as a coverage gap in the CODE, and recorded as such. `_artifact_type_of` derives the type from the shipped table and `_close_recorded_transition` reads the vocabulary, terminal set and in-flight states per type, so a bug and a change request already take the same path a story does - measured across all three before any repair was attempted. What the finding's own Proposed Fix asked for and was genuinely missing is the assertion: the property was pinned by a story fixture only, which cannot tell a type-general rule from one that happens to work for stories. That assertion is the delivery. |
