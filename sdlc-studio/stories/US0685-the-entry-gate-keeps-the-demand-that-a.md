# US0685: The entry gate keeps the demand that a test plan EXISTS and drops the demand that a seat has approved it

> **Status:** Blocked
> **Delivers:** CR0555
> **Created:** 2026-08-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0218
> **Blocked by:** a pre-code goal review, and then by a measurement that invalidated the request's premise. `transition.py:961` gates the two-role delivery review as story-and-Done only, so a bug pays no second review cycle for this batch to merge - and a further dry-run across all 23 open bugs found that NONE owes an independent review at all, because the entry gate never fires for a bug. CR0555 is narrowed to STORIES, where the two-cycle saving is real. These units are kept for their review record: eleven further findings, including that all twenty of their criteria were library tests rather than lane tests (LL0040). Re-groom against the narrowed request before building. Disposition: entry gate split - SURVIVES for stories, and is the core of the narrowed request.
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The entry gate keeps the demand that a test plan EXISTS and drops the demand that a seat has approved it
**So that** CR0555 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a unit entering implementation with no `## Test Plan`, when the gate runs, then it is REFUSED exactly as it is today - the authoring-time rule that a criterion names a production change its test dies on is untouched, and it is the half that costs nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::EntryGateSplitTests::test_entry_still_refuses_a_unit_with_no_test_plan
- [ ] **AC2** Given a unit entering implementation WITH a test plan and no independent approval on record, when the gate runs, then it PASSES - the approval is no longer demanded here, which is the whole move
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::EntryGateSplitTests::test_entry_no_longer_demands_the_independent_approval
- [ ] **AC3** Given a unit entering implementation with a test plan and a REJECT plan-review verdict on record, when the gate runs, then it still PASSES - the entry gate reads the plan's EXISTENCE and nothing about its judgement, so a half-moved gate that still consults the verdict is caught
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::EntryGateSplitTests::test_entry_ignores_the_verdict_entirely
- [ ] **AC4** Given the two demands now separated, when the gate module is exercised, then each can be called alone - one function guarding two rules is how a change silently reaches a gate nobody meant to touch
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::EntryGateSplitTests::test_the_two_demands_are_separately_callable

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Created via `new` (deterministic) |
