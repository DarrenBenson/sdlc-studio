# US0882: Mutation evidence that is switched off stops blocking commits

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_off.py
> **Epic:** EP0261
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** developer committing a change
**I want** switched-off mutation evidence to stop refusing commits, and re-registration to keep rows it did not move
**So that** a disabled ceremony costs nothing and evidence is never silently lost (BG0747)

## Acceptance Criteria

- **AC1:** Given `review.mutation_evidence` off, when a commit drifts a registered mutant row, then the evidence-drift lane reports it and does not refuse
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_off.py::EvidenceDriftTests::test_off_means_reported_not_refused
- **AC2:** Given `review.mutation_evidence` block, when the same commit runs, then it is still refused
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_off.py::EvidenceDriftTests::test_block_still_refuses
- **AC3:** Given a target holding anchored rows whose sites did not move, when another row on that target is re-registered, then the anchored rows are kept, not dropped
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_off.py::EvidenceDriftTests::test_register_keeps_anchored_rows_that_did_not_move

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `new` (deterministic) |
