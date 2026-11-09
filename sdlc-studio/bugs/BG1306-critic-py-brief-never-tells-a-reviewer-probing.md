# BG1306: `critic.py brief` never tells a reviewer probing confinement or environment-isolation code to run its mutants with HOME set to a temporary directory, so a mutant can write outside the scratch tree

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** BG1300 (the ~/.gitconfig overwrite of 2026-11-08) and its Proposed Fix's third clause
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T12:35:57Z

## Summary

Split from BG1300's proposed fix, which reaches beyond BG1300's Affects. On 2026-11-08 a reviewer's mutation run against conftest's `_move_home` ran with HOME unmoved and overwrote the operator's ~/.gitconfig (BG1300). BG1300 fixes the harness; nothing in the review brief tells the next reviewer that a mutant of confinement code runs unconfined, so the same class of probe can still write to the real home directory.

## Steps to Reproduce

1. Run `critic.py brief` for a unit whose Affects include conftest.py or another file that sets HOME or `PRIVATE_HOME.`
2. Read the brief's mutation guidance: it says nothing about running mutants with HOME pointed at a temporary directory.

## Proposed Fix

When a unit's diff touches HOME, `PRIVATE_HOME` or conftest isolation, have the brief tell the reviewer to run every mutant and probe with HOME set to a fresh temporary directory, and add a test that such a unit's brief carries the instruction while an unrelated unit's brief does not.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Split from BG1300's proposed fix, which reaches beyond BG1300's Affects.
- [ ] **AC2** The proposed fix lands, pinned by a test: When a unit's diff touches HOME, `PRIVATE_HOME` or conftest isolation, have the brief tell the reviewer to run every mutant and probe with HOME set to a fresh...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
