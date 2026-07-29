# BG0364: Two more modules hand-roll the strict timestamp parser BG0353 just fixed in telemetry

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/loop_guard.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

transition.py and `loop_guard.py` each carry their own Z-only stamp parser, so the offset-bearing timestamps BG0353 made telemetry accept are still rejected there. One rule, three implementations, two of them now wrong - the class the carried lesson about enumerated rules covers.

## Steps to Reproduce

Reported by a delivery lane during RUN-01KYKVZM; see the summary for the measurement.

## Proposed Fix

See the summary; the remedy is stated with the defect.

## Acceptance Criteria

### AC1: the stamp rule has one implementation

- **Given** every module that reads an ISO-8601 stamp
- **When** it is checked
- **Then** none carries its own `%Y-%m-%dT%H:%M:%SZ` pattern - the rule had four implementations and three refused the offset-bearing stamps the standard library writes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py::OneStampReaderTests::test_no_module_hand_rolls_the_pattern
- **Verified:** yes (2026-07-29)

### AC2: each reader accepts an offset stamp through its own entry point

- **Given** an offset-bearing stamp handed to telemetry, transition and the loop guard
- **When** it is checked
- **Then** each parses it, because a shared helper nothing calls would leave every one of them still refusing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py::OneStampReaderTests::test_each_reader_accepts_an_offset_stamp
- **Verified:** yes (2026-07-29)

### AC3: a naive stamp is still refused

- **Given** a stamp with no offset
- **When** it is checked
- **Then** it is unreadable, because it names no instant and calling it UTC would invent the one fact it is missing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py::OneStampReaderTests::test_the_shared_reader_accepts_both_forms_and_refuses_a_naive_one
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction) | Filed |
