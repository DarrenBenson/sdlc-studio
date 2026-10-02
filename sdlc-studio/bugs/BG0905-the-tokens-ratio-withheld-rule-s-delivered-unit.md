# BG0905: The tokens-ratio withheld rule's delivered-unit half is untested, and its help text says briefed where the code counts any span

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_delegated_tokens.py, .claude/skills/sdlc-studio/help/sprint.md
> **Evidence:** US0980 QA review round 2 (RUN-01M3Y7DP)
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T13:34:10Z

## Summary

US0980's `_tokens_ratio_withheld` withholds the ratio when any delivered or spanned unit lacks an agent total, but every test delivers through a lane (which opens a span), so a mutant checking spanned units only survives all 27 tests while a delivered unit with no span and no total would then print a ratio. help/sprint.md and the CR0606 fragment say 'briefed' or 'a span a lane brief opened', narrower than the code, which counts any span.

## Steps to Reproduce

1. US0101 delivered with --tokens; US0102 set Done without a brief (no span, no total). 2. A mutant checking spanned units only prints 0.64x; the suite stays green.

## Proposed Fix

Add the control (a delivered unit with no span and no total withholds the ratio) and word the help and fragment as the code reads.

## Acceptance Criteria

- [ ] **AC1** Given US0101 delivered with an agent total and US0102 moved to Done with no span and no total, when the page is derived, then the tokens ratio reads withheld naming US0102. Fails on: a spanned-only check, which prints 0.64x
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_ratio_withheld_delivered.py::RatioWithheldDeliveredTests::test_a_delivered_unit_with_no_span_withholds_the_ratio

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
