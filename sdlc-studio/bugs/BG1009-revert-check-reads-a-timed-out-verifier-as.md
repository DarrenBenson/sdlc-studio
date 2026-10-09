# BG1009: revert-check reads a timed-out verifier as red and an empty revert as green, so it passes a unit it never measured and refuses one it never reverted

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_revert_check_unmeasurable.py, .claude/skills/sdlc-studio/help/verify.md, changelog.d/BG1009.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** verify_ac.py `revert_check`: the red/unmeasured split reads `res.kind in ('invalid','blocked') or res.vacuous`; a timeout (`VerifierResult(False, kind, 124, '', 'timeout', ...)`) falls to red. No byte comparison precedes the run. Executed by the G7 drafter in throwaway fixtures.
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T08:32:20Z

## Summary

Two defects in `verify_ac.revert_check`, confirmed by the code path at 31f63fae and executed by the G7 breakdown of CR0624/CR0616 (D0355). (1) A verifier that times out returns `ok=False` with its runner's kind (`run_verifier` sets the timeout as the error text, not the kind), which is not `invalid`, `blocked` or vacuous, so it is counted `red`: proof the tests reach the change. With `--timeout 1`, a unit whose criteria never reach its change printed PASSES. (2) Nothing checks that reverting changes any byte: when the base equals HEAD (every unit built but not yet closed in a run planned from HEAD), the revert writes identical files, every criterion stays green, and the unit is refused with 'A test that passes without the change never reached it' about a change that was never removed. The command is on demand today; CR0624 and CR0626 would make it a gate, where both defects decide units.

## Steps to Reproduce

(1) `verify_ac.py revert-check --unit <id> --timeout 1` on a unit whose verifiers take longer than a second and never touch its production file -> PASSES. (2) `verify_ac.py revert-check --unit <id> --base HEAD` on any unit with a production file in Affects -> REFUSED, naming criteria that do reach the change.

## Proposed Fix

Count a timed-out verifier `unmeasured`, never `red`; and before running anything, compare each reverted file's base bytes with its current bytes, reporting a revert that changes nothing as not judged (exit 3), never refusing it.

## Acceptance Criteria

- [ ] **AC1** A revert-check whose verifier times out reports that criterion as not measured, and never passes a unit on it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_revert_check_unmeasurable.py::UnmeasurableRevertTests::test_a_timed_out_verifier_is_not_red
- [ ] **AC2** A revert-check whose revert changes no byte reports the unit as not judged and never refuses it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_revert_check_unmeasurable.py::UnmeasurableRevertTests::test_an_empty_revert_is_not_judged
- [ ] **AC3** help/verify.md states revert-check's verdicts and exit codes (pass 0, refused 1, not judged 3, error 1), including that a directory in Affects reads as no production file and the unit is not judged, and each example command it shows returns the code it states
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_revert_check_unmeasurable.py::UnmeasurableRevertTests::test_the_help_verdicts_match_the_exit_codes
- [ ] **AC4** A paired control: the same unit, judged from an earlier base whose file differs, is still refused or passed as it was before the fix, so a change that reports every unit as not judged cannot pass AC2
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_revert_check_unmeasurable.py::UnmeasurableRevertTests::test_a_differing_base_is_still_judged

## Triage notes (from the G7 breakdown, D0355)

- AC3 and AC4 are carried from the G7 story this bug replaced. Decide red by an allow-list: red means the verifier ran to a verdict and reported a failure (a `ran` flag on `VerifierResult`, LL0042), so a timeout, an unstartable runner, a vacuous run and any `partial` state BG1005 adds all read as unmeasured by construction. If the deny-list stays, whichever of BG1005 and BG1009 lands second must map `partial` to unmeasured.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Filed |
| 2026-10-09 | Claude Opus 5.5 (triage) | AC3 and AC4 added from the G7 breakdown (D0355); the allow-list note for BG1005 |
