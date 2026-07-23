# CR-0360: the doc-freshness line-budget refusal names the count but not the gap, so trimming is guesswork

> **Status:** In Progress
> **Decomposed-into:** EP0127
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/doc_freshness.py
> **Date:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`doc_freshness` refuses LATEST.md over its line ceiling with the current count and the limit, but not how many lines must go, and it re-checks only on a full re-run. Trimming the anchor for this close took five edit-and-recheck cycles (113, 85, 84, 82, 82, 80) with two of them netting zero because the edits landed inside wrapped paragraphs. The remedy text advises moving past-sprint paragraphs to their retros, which is the right advice, but nothing indicates the size of the cut needed.

## Impact

A cheap mechanical fix becomes an iteration loop against a gate that blocks the close. Small on its own, but it sits directly on the close path where the cost is paid under time pressure.

## Acceptance Criteria

- [ ] the refusal states the overage explicitly, for example 2 lines over the 80-line ceiling
- [ ] the message names the longest sections by line count so the trim can be aimed rather than guessed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Raised |
