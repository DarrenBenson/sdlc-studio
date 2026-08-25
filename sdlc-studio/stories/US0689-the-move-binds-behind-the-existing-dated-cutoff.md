# US0689: The move binds behind the existing dated cutoff, so a project that has not adopted it is unchanged and no backlog is retro-refused

> **Status:** Blocked
> **Delivers:** CR0555
> **Created:** 2026-08-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/reference-config.md
> **Epic:** EP0218
> **Blocked by:** a pre-code goal review, and then by a measurement that invalidated the request's premise. `transition.py:961` gates the two-role delivery review as story-and-Done only, so a bug pays no second review cycle for this batch to merge - and a further dry-run across all 23 open bugs found that NONE owes an independent review at all, because the entry gate never fires for a bug. CR0555 is narrowed to STORIES, where the two-cycle saving is real. These units are kept for their review record: eleven further findings, including that all twenty of their criteria were library tests rather than lane tests (LL0040). Re-groom against the narrowed request before building. Disposition: the dated cutoff - survives unchanged.
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The move binds behind the existing dated cutoff, so a project that has not adopted it is unchanged and no backlog is retro-refused
**So that** CR0555 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a unit whose date falls BEFORE the configured cutoff, when it transitions, then neither the entry demand nor the terminal demand fires - an existing backlog carrying no plans is not retro-refused, which is how a gate gets switched off wholesale
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::MoveCutoffTests::test_a_unit_before_the_cutoff_is_untouched
- [ ] **AC2** Given a unit at or after the cutoff, when it transitions, then the moved behaviour applies - the paired control, so the cutoff admits as well as exempts
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::MoveCutoffTests::test_a_unit_after_the_cutoff_gets_the_moved_behaviour
- [ ] **AC3** Given a project with NO cutoff configured, when a unit transitions, then behaviour is unchanged from today - an absent setting means not-adopted, never adopted-by-default, because a silent adoption changes a blocking gate under a project that never asked
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::MoveCutoffTests::test_an_absent_cutoff_means_not_adopted

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Created via `new` (deterministic) |
