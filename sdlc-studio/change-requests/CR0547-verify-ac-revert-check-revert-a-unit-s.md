# CR-0547: verify_ac revert-check: revert a unit's production files and REQUIRE its own verifiers to go red

> **Status:** In Progress
> **Decomposed-into:** EP0217
> **Priority:** High
> **Type:** enhancement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .githooks/pre-commit
> **Evidence:** RUN-01M0CT8P delivery review, 2026-08-19: BG0593's production change deleted, 916 tests still green.
> **Date:** 2026-08-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Nothing currently asks the one question that finds an unexercised fix: if the production change were removed, would this unit's own tests notice? A unit can have every criterion green, every declared mutant recorded as killed, and a production change no test reaches - because the tests rebuilt the thing under test in a fixture, or pinned a construct one step away from the defect. The mutation lane cannot see it: a mutant applied to a call site dies against a test that never exercises the function behind it, and the ledger records that as evidence.

## Impact

This is the gate for the failure class this project keeps paying for - LL0040 (a library test is not a lane test), LL0020 (a fixture that supplies the thing under test proves nothing) and LL0017 (a function only ever seen inside patch() is untested) are three registry entries describing the same hole from three angles, and none of them is enforced by anything. A reviewer currently finds it by hand, once, if they think to try.

## Acceptance Criteria

- [ ] Given a unit whose production change is reverted to the run's base ref, when only that unit's own `Verify:` selectors run, then they FAIL - green after the revert is the refusal, because a test that passes without the fix is pinned to something other than the fix
- [ ] Given a unit whose tests genuinely exercise the shipped path, when the same revert-and-run happens, then they fail and the unit passes the check - the control, so the gate discriminates rather than refusing everything
- [ ] Given a unit whose `Affects` names no production file at all, when the check runs, then it REPORTS that rather than passing: nothing to revert is not evidence that the tests reach anything
- [ ] Given the revert, when the check completes or is interrupted, then the working tree is byte-identical to how it started - the check must not be able to leave a unit's production change reverted
- [ ] Given BG0593 as it stood on 2026-08-19 - four criteria green, four mutants recorded killed, and a production change no test reached - when the check runs against that commit, then it REFUSES

## Steps to Reproduce

Measured on RUN-01M0CT8P, 2026-08-19. BG0593 had four criteria green and four mutants recorded killed. Deleting its ENTIRE production change - the scratch-construction loop in `sprint.close_dry_run` - left all four of its tests green AND all 916 tests in `test_sprint.py` green, hash-verified before and after. Its tests had rebuilt the scratch in a private helper, so they pinned a copy of the fix rather than the fix. An independent review found it by deleting the code and running the suite; no lane, no gate and no mutation run had. In the same batch BG0594's AC6 mutant was applied to the call site while the function behind it still returned the wrong series - `from-plan` reported `every one executed and killed` throughout.

## Recommendation

Wire it into the `transition -> Fixed/Done` gate beside the planned-mutant check, not into a document. It is the cheapest possible form of the question every review in this repository ends up asking by hand, and the one that found the most expensive defect of the run. Report-only at first, with the yield measured, because a new blocking check on a gate already over its ceiling earns its place on a number rather than on assertion.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-19 | sdlc-studio | Raised |
