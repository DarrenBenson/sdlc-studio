# US1097: A run whose open stamp was taken under an earlier counting basis has that reading re-derived from the transcript, never subtracted from a reading on the current basis

> **Status:** Ready
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_reads_true.py, changelog.d/US1097.md, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_velocity_row_model.py
> **Epic:** EP0292
> **Points:** 3
> **Depends on:** US1091
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, reading what a run cost
**I want** a run opened before the meter's counting changed to have its open reading re-derived under the current counting
**So that** the run's cost is one figure on one basis, never the difference of two

## Acceptance Criteria

- **AC1:** Given a run whose open stamp was taken under an earlier counting basis (a stamp that names no basis, as every stamp before BG1111 and this story does), when the run's total is formed at the close or by the report, then the open reading is re-derived from the transcript records up to the stamp's time under the current basis, and the basis says so; where the transcript no longer holds those records, the total is reported not attributable naming the basis change. It is never the difference of two bases
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_reads_true.py::OpenStampBasisTests::test_an_open_stamp_on_an_earlier_basis_is_re_derived_not_subtracted

## Notes

- Serves: Maya Okafor, End goal 3.
- Split from US1091 (its AC5) on 2026-10-22.
- AC1 must fail on: the old-basis open stamp subtracted from a new-basis reading (RUN-01M5EM9N's open stamp is 48,420,326 counted per record; the same point counted once per message is 19,227,104, BG1111's builder, 2026-10-22); the re-derivation reading past the stamp's time.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-22 | sdlc | Affects gains retro.py, its test module and help/sprint.md: US1091's held AC5 patch re-derives the retro's baseline and documents the rule there |
| 2026-10-22 | sdlc | Affects gains three test modules whose fixtures hand-write a basis-less baseline or stamp beside a current-basis reading, the case AC1 forbids; each is marked current-basis, which is what it means (builder's finding) |
