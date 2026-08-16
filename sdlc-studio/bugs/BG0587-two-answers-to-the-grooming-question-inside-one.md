# BG0587: two answers to the grooming question inside one close

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-08-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`grooming_report` filters to story units only and asks `conformance.story_is_ungroomed`; `_rung_product_blockers`, three hundred lines away in the same file and running in the same close, asks `conformance.unit_is_ungroomed` across every type the deliverer verifies. So a design batch made of bugs prints 'no story units in this batch' from one and blocks on those same bugs from the other. Both are reporting the same fact to the same reader in the same invocation, and they disagree about which units the question even applies to. AGENTS.md's own rule is one definition, never a second.

## Steps to Reproduce

Read at 7697ee36 plus the BG0582 repair. `grooming_report` (sprint.py:5861) contains `if not hit or hit[1] != "story": continue` and calls `story_is_ungroomed`. `_rung_product_blockers` iterates the whole batch and calls `unit_is_ungroomed`, which conformance.py documents as type-agnostic on purpose because 'nine bugs reached a plannable batch unjudgeable' under the story-only predecessor. RUN-01M05A5M's batch carried BG0490 and BG0493 among twelve units, so the divergence is reachable on the run that prompted this filing.

## Proposed Fix

Point `grooming_report` at `unit_is_ungroomed` and drop its story-only filter, so the printed report and the blocking check answer the same question. Check the callers of the report first: its counts appear in the close output and a widened denominator changes them, which is a reporting change worth stating rather than slipping in. Pin the agreement with a test over a MIXED batch - the shape that distinguishes them - rather than over stories, which cannot.

## Acceptance Criteria

- [ ] **AC1** Given a design batch containing both a story and a bug, when the close runs, then the grooming report and the pre-flight name the same set of ungroomed units
- [ ] **AC2** Given a batch of bugs only, when the grooming report renders, then it does not report 'no story units in this batch' while the pre-flight blocks on those bugs

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-16 | sdlc-studio | Filed |
