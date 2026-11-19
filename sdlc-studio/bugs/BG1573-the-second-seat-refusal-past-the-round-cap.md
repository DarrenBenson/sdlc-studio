# BG1573: The second-seat refusal past the round cap names a seat that does not exist when the reviewer id carries no seat word

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_second_seat.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG1573.md
> **Evidence:** BG1523 QA verdict, sdlc-studio/reviews/verdicts/BG1523/cdda89988311-0990e453.txt
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T00:41:40Z

## Summary

BG1523 (run sixteen) made critic.py refuse a second seat's verdict past the round cap in plain words. The refusal reads the seat from the reviewer id, so an id with no seat word in it (for example a bare agent id) produces a sentence naming a seat no charter defines. The QA review (APPROVE, round 1) recorded it as non-blocking.

## Steps to Reproduce

Record two verdicts for one unit past the cap, the second under a reviewer id such as 'agent-abc123' with no '(qa)' or '(engineering)' part; read the refusal.

## Proposed Fix

When no seat can be read from the reviewer id, say so and print the id as given.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG1523 (run sixteen) made critic.py refuse a second seat's verdict past the round cap in plain words.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Record two verdicts for one unit past the cap, the second under a reviewer id such as 'agent-abc123' with no '(qa)' or '(engineering)' part; read the refusal.
- [ ] **AC3** The proposed fix lands, pinned by a test: When no seat can be read from the reviewer id, say so and print the id as given.

## Impact

The operator reads a seat name that does not exist and cannot tell which seat was refused.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
