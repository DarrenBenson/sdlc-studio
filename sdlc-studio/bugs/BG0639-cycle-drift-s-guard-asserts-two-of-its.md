# BG0639: cycle_drift's guard asserts two of its three buckets, so the unverifiable bucket is already non-empty on the shipped tree while the guard reports green

> **Status:** Superseded
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Created:** 2026-09-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

An adversarial review of US0569, US0572 and US0574 on 2026-07-31 found the guard failing open, recorded it as a REJECT, and it was never answered. `cycle_drift`returns THREE buckets and the verifier asserts TWO. The third -`unverifiable`- is already non-empty on the shipped tree, because`retro.py`builds its subparsers inline in`main()`so`retro validate`cannot be checked, leaving 2 of 18 rows unverifiable while the guard reports green. Adding`assertEqual(drift['unverifiable'], [])` goes RED on the unmutated tree today. Two ceremony-verb rename mutants SURVIVED the full 91-test suite and the criterion's own selector in isolation. The reverse check compounds it: it walks only sprint verbs, though 6 of 18 rows name critic, retro, lessons and handoff verbs.

## Steps to Reproduce

1. Add `assertEqual(drift['unverifiable'], [])` to the guard's assertions.
2. It goes RED on the unmutated tree - 2 of 18 rows are unverifiable today.
3. Rename a ceremony verb the reverse check does not walk; the full suite stays green.

## Proposed Fix

Assert all three buckets, or state in the criterion why the third is exempt - an unasserted bucket is a bucket nobody reads. Lift `retro.py`'s subparsers out of `main()`so its verbs are inspectable, which is what makes`retro validate` checkable at all. Widen the reverse check to every verb the rows actually name rather than sprint's alone: 6 of 18 rows name verbs it never walks, so a rename there cannot fail.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: An adversarial review of US0569, US0572 and US0574 on 2026-07-31 found the guard failing open, recorded it as a REJECT, and it was never answered.
- [ ] **AC2** The proposed fix lands, pinned by a test: Assert all three buckets, or state in the criterion why the third is exempt - an unasserted bucket is a bucket nobody reads.

## Impact

The guard exists to catch a documented verb drifting from a shipped one. It reports green while two rows cannot be checked and while a third of the rows name verbs it does not walk - so the class it exists to stop is open in exactly the places nobody looks. Two rename mutants survived the whole suite, which is the measurement rather than the argument.

## Resolution

**DUPLICATE of BG0461 (Fixed), closed 2026-09-02 without being worked.**

This was filed from an adversarial REJECT recorded against US0569, US0572 and US0574 on
2026-07-31 and never answered. The filer's own duplicate check named BG0461 at 50% similarity;
re-running the finding against HEAD shows every part of it is already closed:

- `cycle_drift`now lives in`sprint_report.py`:2235 and returns `unresolved: 0, uncovered: 0,
  unverifiable: 0` on the live tree - the third bucket the finding says is "ALREADY non-empty"
  is empty.
- The guard DOES assert it: `test_sprint_report.py`:1789 is
  `self.assertEqual(drift["unverifiable"], [])`.
- The reverse-check half is closed too, and the function's own docstring records both:
  *"`uncovered`walked`sprint`alone while six rows hold a stage in`critic`, `retro`,
  `lessons`or`handoff`. Both are closed, and the verifier asserts all three."*

Filed and closed the same day rather than quietly deleted, because the REJECT it came from was
real and unanswered for a month, and the record should show what happened to it: the work was
done under another id before anyone went back to the rejection.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-02 | sdlc-studio | Filed |
