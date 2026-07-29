# BG0369: The conformance waiver report is blanked when the diff contains no stories, hiding a waived unit rather than reporting it

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (RUN-01KYKVZM review carry-forward); agent; skill v5.0.0

## Summary

US0525 has the conformance lane read recorded waivers and report a waived unit as waived, naming the waiver. The report is emitted from a story-scoped path, so a diff containing no story emits nothing at all - a waiver covering a bug or a change request is silently in force with no line saying so, which is the outcome the story exists to prevent.

## Steps to Reproduce

Observed during the RUN-01KYKVZM review, alongside BG0336's related over-narrowing to stories. Run the lane over a diff of bugs only and the waiver section is absent rather than empty-with-reason.

## Proposed Fix

Scope the waiver report to the units in the diff whatever their type, and emit an explicit none-in-force line when there are no waivers, so absence of output is never the same as absence of waivers.

## Acceptance Criteria

### AC1: a waiver no judged unit carries is reported

- **Given** a waiver scoped to a bug, while this lane judges stories
- **When** the conformance lane reports
- **Then** it is reported as in force and unattributed, rather than producing no line at all and sitting silently active
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::WaiverInForceIsAlwaysReportedTests::test_a_waiver_no_judged_unit_carries_is_reported
- **Verified:** yes (2026-07-29)

### AC2: the printed report names it, with its decision

- **Given** the same waiver and a text report
- **When** the conformance lane reports
- **Then** the line names the stage, the decision and the fact that no judged unit carries it, so a reader can go and read the decision
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::WaiverInForceIsAlwaysReportedTests::test_the_report_names_it
- **Verified:** yes (2026-07-29)

### AC3: a waiver already attributed per unit is not reported twice

- **Given** a waiver a judged story does carry
- **When** the conformance lane reports
- **Then** it appears in the per-unit report only, because a line that fires on every run becomes noise and gets read past
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::WaiverInForceIsAlwaysReportedTests::test_a_waiver_a_judged_unit_does_carry_is_not_double_reported
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (RUN-01KYKVZM review carry-forward) | Filed |
