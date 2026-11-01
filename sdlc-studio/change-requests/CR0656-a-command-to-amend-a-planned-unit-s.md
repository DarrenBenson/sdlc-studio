# CR-0656: A command to amend a planned unit's Affects or a criterion in flight, recording why, so a builder's scope finding is not a hand edit

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Enhancement
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/help/sprint.md
> **Date:** 2026-10-31
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-31T23:59:53Z

## Summary

In RUN-01M6A3K2, BG0963's builder found that its own AC1 needed seven test files outside the unit's declared Affects. The builder brief rightly stops a builder from widening scope, but nothing then widens it on the record. The toolchain runbook's in-flight section covers trading, dropping and adding units and resizing the appetite, but not amending a unit's Affects or narrowing a criterion. The orchestrator hand-edited the Affects line and AC1, with a revision row (2026-10-31). The runbook says a step with no command is a finding to file.

## Impact

Every in-flight scope correction is a hand edit of a planned unit, outside the plan's record. The close and the review brief, whose diff scope is the Affects, then read a field nobody can trace to a decision.

## Acceptance Criteria

- [ ] `sprint.py batch amend <id> --affects-add <paths> --reason <why>` widens a batch unit's Affects, writes a revision row naming the reason, and records the amendment on the run so the close's report lists it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
- [ ] Narrowing or rewording a criterion of a batch unit goes through the same command (`--criterion ACn --text ...`), and is refused for a unit already reviewed in this run.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-31 | claude | Raised |
