# BG1346: The first verdict recorded after the ledger gained its Source column pads every row, and the commit-msg hook credits that change to every unit the subject names

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_binding.py, changelog.d/BG1346.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** RUN-01M77177, 2026-11-12: f65ac0bd; qa-seat-US1012-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:19:30Z

## Summary

US1012's Source column pads all 1,814 existing rows on the next record. `engagement_floor` then treats every unit with a row as owning that commit, so a multi-id subject credits them all; the run worked round it with a single-id commit.

## Steps to Reproduce

Record any verdict on a ledger written before US1012 and commit with a two-id subject.

## Proposed Fix

Migrate the ledger in a dedicated step, or teach `engagement_floor` to ignore cell-only padding.

## Acceptance Criteria

- [ ] **AC1** Given a ledger of eight-cell rows, when the first nine-cell record is written, then the padding is applied as one migration the hook attributes to no delivery unit. Fails on: every padded row read as an added row.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_binding.py::LedgerMigrationTests::test_padding_is_a_migration_not_an_addition

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
