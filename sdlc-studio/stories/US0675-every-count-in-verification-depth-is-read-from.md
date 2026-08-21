# US0675: Every COUNT in Verification depth is read from the mutation ledger, and an unexecuted row SAYS so

> **Status:** Draft
> **Delivers:** CR0548
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Epic:** EP0217
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** Every COUNT in Verification depth is read from the mutation ledger, and an unexecuted row SAYS so
**So that** CR0548 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a unit with a Test Plan and a mutation ledger, when its `Verification depth` is rendered, then every COUNT in it - criteria, declared rows, executed, killed, survived - is read from the ledger, and a figure the ledger does not support cannot appear
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DerivedDepthTests::test_every_count_is_read_from_the_ledger
- [ ] **AC2** Given a unit whose ledger says a row was never executed, when the field is rendered, then it SAYS so by naming the criterion and row - a derived field that can only report success is the defect this replaces, and BG0592 AC13 row 3 is the live case
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DerivedDepthTests::test_an_unexecuted_row_is_named_not_omitted
- [ ] **AC3** Given BG0592 as it stood on 2026-08-19, whose depth field claimed shipped-CLI coverage that did not exist, when the field is derived instead of authored, then that claim is ABSENT - because nothing in the ledger supports it. The regression case, so the change is shown to remove a specific false claim rather than to reformat a true one
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DerivedDepthTests::test_the_bg0592_false_coverage_claim_is_absent_when_derived
- [ ] **AC4** Given a unit with NO ledger entries at all, when the field is rendered, then it reports that the evidence is absent rather than rendering zeros - nought executed and nothing recorded are different facts, and a reader who cannot tell them apart cannot judge the unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DerivedDepthTests::test_an_absent_ledger_is_reported_not_rendered_as_zero

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
