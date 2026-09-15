# BG0677: critic.py repair cannot close a finding whose text carries the closure separator early, so the rejection raising it can never be retired

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** RUN-01M2JA6J 2026-09-15: US0627's third-round plan review APPROVED, yet `transition.py set --id US0627 --status 'In Progress'` refuses and `critic.py repair` refuses the closure; BG0665, BG0674, US0625 and US0628 cleared the same gate the same way minutes earlier.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`closures_from_document` claims structured input needs no delimiter, so nothing a reviewer writes can be read as one - but it serialises each item back to `<finding> -> <evidence>` text and escapes only the semicolon, and `parse_closures` then splits at the FIRST `->`. A finding whose own text contains `->` (a reviewer writing a status transition, `Fixed->Verified`) is cut at that arrow. The closure then carries only the text before it; when that is shorter than the 24-character prefix minimum, or the finding belongs to a non-standing rejection (where ordinals are refused), no closure can name it. The repair stays PARTIAL for ever and `_test_plan_gate` refuses In Progress on a unit whose repaired plan an independent seat has APPROVED. Hit on US0627 in RUN-01M2JA6J: its round-1 REJECT raised `AC2 - Fixed->Verified and Fixed->Closed on a bug already at Fixed are unpinned`.

## Steps to Reproduce

1. Record a plan-review REJECT on a unit whose ISSUES include a finding beginning `AC2 - Fixed->Verified and ...`, then a second REJECT under a different brief, then an APPROVE.
2. Write a --closed-file JSON naming every raised finding by its exact text.
3. Run `critic.py repair --unit <id> --phase plan-review --closed-file <doc>`.
4. It refuses: closure 'AC2 - Fixed' names no finding. Quoting the text after the arrow is not a prefix; `#n` is scoped to the standing verdict, so the round-1 finding cannot be named at all.

## Proposed Fix

Carry the structured closures from the JSON path to `record_repair` without the text round trip, or escape `->` inside a finding the way the semicolon is escaped and unescape it in `parse_closures`. Either way pin: a finding carrying `->` in its first 24 characters, raised by a non-standing rejection, is closeable through --closed-file.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `closures_from_document` claims structured input needs no delimiter, so nothing a reviewer writes can be read as one - but it serialises each item back to...
- [ ] **AC2** The proposed fix lands, pinned by a test: Carry the structured closures from the JSON path to `record_repair` without the text round trip, or escape `->` inside a finding the way the semicolon is...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-15 | Claude Opus 5 (authoring session) | Second consequence measured the same day on US0628: a finding 'AC2 - no row covers a direct Verified close or Fixed->Verified->Closed ...' resolved by its pre-arrow prefix, but the rest of its text became the head of the closure's EVIDENCE, so the explicit fixed: token no longer led it and the closure was classified filed. The split corrupts dispositions as well as refusing closures. |
