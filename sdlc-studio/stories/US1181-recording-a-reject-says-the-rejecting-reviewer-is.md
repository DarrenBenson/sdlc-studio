# US1181: Recording a REJECT says the rejecting reviewer is needed for round 2, and the runbook row says how to keep it resumable

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0639
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/scripts/tests/test_critic_record_reject_round2.py
> **Epic:** EP0320
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Recording a REJECT says the rejecting reviewer is needed for round 2, and the runbook row says how to keep it resumable
**So that** CR0639 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Recording a REJECT says the rejecting reviewer is needed for round 2

- **Given** a unit in an open run and a reviewer's REJECT verdict for it
- **When** the verdict is recorded with `critic.py record`, and an APPROVE is recorded for a second unit
- **Then** the REJECT's output carries a line saying the reviewer who rejected is needed for round 2 and to keep that reviewer resumable until round 2 is recorded, and the APPROVE's output carries no such line. Fails on: a REJECT recorded with nothing said about round 2, or the line printed on every verdict
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_record_reject_round2.py::RejectRoundTwoTests::test_reject_names_the_reviewer_needed_for_round_two

### AC2: The runbook's review step has a row for keeping the rejecting reviewer

- **Given** the table under 'Review a unit' in `reference-sprint-toolchain.md`
- **When** its rows are read as cells
- **Then** one row's step cell is about keeping a rejecting reviewer until round 2 is recorded, its command cell carries `critic.py brief --unit <id> --seat <seat> --rejoinder` as what to run on a fresh instance of the same seat when the reviewer's worktree is gone, and its last cell names removing the worktree between rounds as what the row replaces. Fails on: a review step with no such row, or the rule stated only in prose outside the table
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_record_reject_round2.py::RejectRoundTwoTests::test_the_runbook_row_says_how_to_keep_the_reviewer_resumable

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
