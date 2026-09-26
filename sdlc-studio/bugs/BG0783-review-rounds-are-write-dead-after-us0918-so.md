# BG0783: Review rounds are write-dead after US0918, so the ceiling and repair-regression readers of run-state rounds read nothing

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-09-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-26T11:37:33Z

## Summary

US0918 retired critic.py sprint-review, the only writer of `run_state` review rounds (`record_sprint_review).` The ceiling guard, `next_round_offer` and repair-regression machinery that read run-state review rounds now read an empty record. The per-unit delivery cap reads the verdict ledger (`critic.delivery_rounds)` and is unaffected. Found by US0918's builder.

## Steps to Reproduce

grep `record_review_round` callers after US0918: none in production.

## Proposed Fix

Delete the run-state review-round readers and their config, or re-point them at `critic.delivery_rounds`; one test that no production reader of run-state rounds remains.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US0918 retired critic.py sprint-review, the only writer of `run_state` review rounds (`record_sprint_review).` The ceiling guard, `next_round_offer` and...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: grep `record_review_round` callers after US0918: none in production.
- [ ] **AC3** The proposed fix lands, pinned by a test: Delete the run-state review-round readers and their config, or re-point them at `critic.delivery_rounds`; one test that no production reader of run-state...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-26 | sdlc-studio | Filed |
