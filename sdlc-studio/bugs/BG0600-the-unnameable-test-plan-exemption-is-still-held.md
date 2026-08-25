# BG0600: the `unnameable` test-plan exemption is still held to the four mutant rules, so a well-formed declared exemption cannot be written

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** Found while authoring the RUN-01M0CT8P test plans, 2026-08-19; both functions run directly against the same row to confirm they disagree.
> **Created:** 2026-08-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`testplan_unnameable` exists so a criterion no production change can falsify costs a written declaration rather than a free pass - its docstring says so: 'a state that costs nothing to enter is free, and free is what every criterion with an awkward mutant will choose'. But `testplan_derive` applies `testplan_row_faults` to EVERY row whose cell is not the placeholder, `unnameable` rows included. So a declared exemption is refused unless it also names a path from the unit's `Affects` and carries an edit verb - two properties a row asserting that NO production change exists cannot honestly have. The exemption is reachable only by writing a reason that mentions a file and a verb it does not mean, which is the opposite of what the mechanism is for.

## Steps to Reproduce

Measured 2026-08-19. `testplan_row_faults('unnameable: this criterion constrains the harness and nothing in production can falsify it', <then>, ['scripts/verify_ac.py'])` returns two faults: 'names no path from this unit's Affects' and 'carries no edit verb'. `testplan_unnameable` parses the SAME row correctly and reports `malformed: False`, so the two functions disagree about whether it is a valid row. Hit while authoring the RUN-01M0CT8P test plans: BG0595 AC4 is a rule about the test harness with no production mutant, and its declared exemption was refused until the reason was reworded to mention `test_commit_msg_hook.py` and the word `change` - neither of which it is about. The check is applied at `verify_ac.py`:2610-2613, inside the `if mutant != _TESTPLAN_PLACEHOLDER` branch, which does not ask whether the cell is an exemption.

## Proposed Fix

Ask `testplan_unnameable`'s question before the fault rules: a row whose cell begins `unnameable` is judged by ITS contract - a reason with enough substance not to be malformed - and not by the four mutant rules, which are about mutants. A bare `unnameable` must still be refused, because that is the control that keeps the exemption costly. The two functions should read one classifier rather than each deciding independently what a row is.

## Acceptance Criteria

- [ ] **AC1** Given a row whose cell begins `unnameable` and carries a reason with substance, when the row rules run, then it is judged by the `unnameable` contract and NOT by the four mutant rules - a declaration that no production change can falsify the criterion cannot also be required to name one
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::UnnameableRowTests::test_an_unnameable_row_is_not_held_to_the_mutant_rules
- [ ] **AC2** Given a row beginning `unnameable` whose reason is empty or junk, when the row rules run, then it is REFUSED - the marker costs a written declaration, and a free pass is what it exists to prevent
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::UnnameableRowTests::test_an_unnameable_row_with_no_reason_is_refused
- [ ] **AC3** Given an ordinary row that does NOT begin `unnameable`, when the row rules run, then all four mutant rules still apply to it exactly as today - the paired control, so the exemption is shown to be narrow
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::UnnameableRowTests::test_an_ordinary_row_is_unaffected

## Impact

The one escape valve the test-plan gate ships is unusable as documented, so the author of an unfalsifiable criterion has three options: write a dishonest exemption, write a dishonest mutant, or drop the criterion. All three are worse than the declaration the mechanism was built to collect, and the third silently shrinks what the plan covers. It also means the count of declared exemptions - the number that would show whether this bar is being gamed - is measuring reluctance to fight the tool rather than genuine unfalsifiability.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-19 | sdlc-studio | Filed |
