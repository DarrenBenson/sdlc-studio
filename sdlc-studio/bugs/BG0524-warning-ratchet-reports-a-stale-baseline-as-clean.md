# BG0524: warning-ratchet reports a stale baseline as clean and exits 0, contradicting US0480 AC4 and its own docstring

> **Status:** Fixed
> **Severity:** Medium
> **Verification depth:** functional
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Evidence:** Engineering review seat, RUN-01KZ79C1 boundary, through the shipped CLI on an isolated fixture.
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0480 AC4 requires four untrustworthy-baseline states, each non-zero, and forbids reporting clean on a reference the ratchet could not establish. It names `stale` as one of the four. `validate.py`'s own docstring for `read_warning_baseline` says the same: `Four untrustworthy states, each distinct and each non-zero`.

The shipped behaviour differs. On a baseline recording an instance no artefact still carries, `warning-ratchet` exits 0 and prints `warning-ratchet: clean. 1 recorded instance(s), none new.` The stale entries are listed below that line, but the headline says clean and the exit code agrees.

AC2 asks for the opposite: a repaired instance must be reported as removable WITHOUT holding the gate, because refusing the commit that repaired something teaches an author to stop repairing. The code follows AC2. So AC2 and AC4 contradict each other, and one of them has to change - this is a specification defect as much as a code one.

## Steps to Reproduce

1. Stamp a baseline, then delete the artefact carrying one of its instances.
2. `validate.py warning-ratchet` - redirect, do not pipe.
3. Exit 0, headline `clean`, stale entries listed underneath.

## Proposed Fix

Decide which criterion is right and make the other follow. The AC2 behaviour is the defensible one - a repaired instance is good news and must not refuse the commit that repaired it - so AC4's enumeration should drop `stale` from the non-zero set, and the docstring with it. If instead stale should refuse, AC2's rationale needs answering, not overriding. Either way the headline must stop saying `clean` while listing entries the ratchet could not verify.

## Acceptance Criteria

> **PREMISE CORRECTED before any code.** This bug's title says a stale baseline "reports clean
> and exits 0", and treats both halves as the defect. Only the first half is. `validate.py`
> carries a deliberate, reasoned decision that stale does NOT hold the gate - "a repaired
> instance is good news, and refusing the commit that repaired it would teach an author to stop
> repairing" - and that reasoning is better than US0480 AC4's, which lumped stale in with the
> untrustworthy states. The criterion over-specified.
>
> What IS wrong is the WORD. A baseline carrying entries no artefact still holds is not `clean`;
> it is ok-with-removable-entries, and printing `clean` is what contradicts the docstring's
> "four untrustworthy states". Separately, US0480 AC4's verifier asserts the stale ENTRIES and
> never the exit code, so it passes while the code contradicts the criterion it verifies - which
> is BG0523's class, found here rather than by it.

### AC1: a stale baseline is not reported as `clean`, and still does not hold the gate

- **Given** a warning baseline the ratchet cannot establish against the current tree
- **When** `validate.py warning-ratchet` runs
- **Then** it exits non-zero and names the state, rather than printing `clean` - it names the state and does NOT exit non-zero, because STALE alone must not refuse the commit that repaired an instance, which is the deliberate design three paragraphs above and was never carried into this clause
- **Mutant:** restore `ok = not new`, so a stale baseline leaves the verdict untouched. A seat showed the not-baselined and corrupt states ALREADY exit non-zero, so a mutant worded around them is survived - only this edit reddens this criterion
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::RatchetStatesTests::test_a_stale_baseline_is_not_clean
- **Verified:** yes (2026-08-06)

### AC2: the four untrustworthy states are DISTINCT and each non-zero

- **Given** the four states the docstring already declares - stale, missing, corrupt, unreadable
- **When** each is produced
- **Then** each exits non-zero with its own message, because they have different fixes and one message for four sends the reader to the wrong one
- **Mutant:** collapse them to one message - the assertion that they are distinct is what makes the docstring's claim true rather than decorative
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::RatchetStatesTests::test_each_untrustworthy_state_is_distinct
- **Verified:** yes (2026-08-06)

### AC3: the positive control - a genuinely clean ratchet still exits 0

- **Given** a baseline that IS established and holds
- **When** the lane runs
- **Then** it reports clean and exits 0, because this lane is in the per-commit `npm run lint` chain and a guard that refuses everything gets switched off within a day
- **Mutant:** exit non-zero unconditionally - AC1 and AC2 pass while every commit is blocked. The control must include the FRESH workspace (not-baselined with zero live instances), which is where AC1's edit bites and which every consuming project hits on its first commit of the per-commit lint chain
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::RatchetStatesTests::test_a_clean_ratchet_still_passes
- **Verified:** yes (2026-08-06)

## Impact

A criterion is marked Verified against behaviour the code does not have, and the module docstring states a rule the module does not follow - so the next reader trusts a four-state guarantee that is three.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in validate.py, return 0 when the baseline could not be established | a stale baseline exits NON-ZERO and says which state it is in |
| AC2 | in validate.py, collapse the four untrustworthy states into one shared message | the four untrustworthy states are DISTINCT and each non-zero |
| AC3 | in validate.py, replace the clean-path return with a non-zero exit | the positive control - a genuinely clean ratchet still exits 0 |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Filed |
| 2026-08-06 | sdlc-studio | Groomed for the v5 release sprint: tool-derived criteria replaced with decidable ones naming their mutants, authored in the shape verify_ac actually parses |
