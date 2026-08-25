# US0687: The terminal transition demands the independent plan-review approval and refuses without one exactly as entry does today

> **Status:** Blocked
> **Delivers:** CR0555
> **Created:** 2026-08-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0218
> **Blocked by:** a pre-code goal review, and then by a measurement that invalidated the request's premise. `transition.py:961` gates the two-role delivery review as story-and-Done only, so a bug pays no second review cycle for this batch to merge - and a further dry-run across all 23 open bugs found that NONE owes an independent review at all, because the entry gate never fires for a bug. CR0555 is narrowed to STORIES, where the two-cycle saving is real. These units are kept for their review record: eleven further findings, including that all twenty of their criteria were library tests rather than lane tests (LL0040). Re-groom against the narrowed request before building. Disposition: terminal approval demand - survives, but must add the REJECT branch, `--force` pinning, the named terminal status set and an approval-staleness pin.
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The terminal transition demands the independent plan-review approval and refuses without one exactly as entry does today
**So that** CR0555 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a unit reaching a terminal status with no independent plan-review approval on record, when the gate runs, then it is REFUSED, naming the unit and the missing approval - the demand moved, it did not disappear
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::TerminalApprovalTests::test_terminal_refuses_a_unit_with_no_approval
- [ ] **AC2** Given a unit reaching terminal WITH an independent approval on record, when the gate runs, then it PASSES - the paired control, so the gate discriminates rather than refusing everything
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::TerminalApprovalTests::test_terminal_passes_a_unit_with_an_approval
- [ ] **AC3** Given a plan-review APPROVE by a seat the AUTHOR controls, when the terminal gate runs, then it is REFUSED - independence is the property being bought, and the existing independence check must still be consulted here
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::TerminalApprovalTests::test_a_non_independent_approval_does_not_satisfy_the_terminal_gate
- [ ] **AC4** Given a verdict ledger that cannot be read at all, when the terminal gate runs, then it FAILS LOUD rather than passing - on the same terms as the two sibling gates in this file, because an independent seat once made a refusal exit 0 by chmod-ing that ledger
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::TerminalApprovalTests::test_an_unreadable_ledger_fails_loud

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Created via `new` (deterministic) |
