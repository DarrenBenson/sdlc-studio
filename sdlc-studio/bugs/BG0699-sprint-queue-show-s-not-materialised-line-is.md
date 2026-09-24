# BG0699: sprint queue show's not-materialised line is pinned by no test, and next, plan and queue show hold the discovery partition in separate copies

> **Status:** Won't Fix
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), RETIRE
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/BG0674-delivery-qa.txt (qa seat); verdicts/BG0674-delivery-engineering.txt (engineering seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md. Queued in findings/todo.txt (BG0674 queue-show mirror unpinned, M17 survives).
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

queue show prints the not-materialised line (sprint.py:10928-10929 at review). Deleting it (mutant M17) leaves the whole `test_sprint` module green (965 tests), so only the unit's Coverage Ruling stands behind the changelog's 'queue show reports the head the same way, so the two cannot disagree', which the CLI confirms today for a discovery-only head, a mixed head and a head during an open run. The decompose remedy is written three times - plan's `_refuse_requests` (sprint.py:4106), the `_DISCOVERY_REMEDY` constant (sprint.py:1480-1483) and an inline copy in `_discovery_left_out` (sprint.py:1491) that does not use the constant - and the partition repeats plan's gate (sprint.py:1460-1463 against 9412-9413). plan and next agree today on five enforce spellings because two copies match, not because they share code. A kept unit that depends on a held CR loses that dependency without comment: BG0001 declaring Depends on CR0001 under a mixed charter is materialised by next and placed in wave 1 by plan --worklist BG0001 with no mention of it. The not-materialised line does name CR0001, and AC3 allows this outcome.

## Steps to Reproduce

1. In a copy, delete the queue show print of the not-materialised line and run `test_sprint.py` - green. 2. In a charter fixture with a mixed head where BG0001 declares Depends on CR0001, a discovery item: sprint.py next, then sprint.py plan --worklist BG0001 - wave 1 holds BG0001 and nothing names the held dependency.

## Proposed Fix

Pin queue show's line through the CLI on a discovery-only and a mixed head. Route next, plan and queue show through one partition helper and one remedy constant. Name a held dependency when a kept unit declares one.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: queue show prints the not-materialised line (sprint.py:10928-10929 at review).
- [ ] **AC2** The proposed fix lands, pinned by a test: Pin queue show's line through the CLI on a discovery-only and a mixed head.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): RETIRE - surviving mutant on a correct queue-show line: evidence-only finding, behaviour confirmed by CLI |
