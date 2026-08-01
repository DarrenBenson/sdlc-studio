# BG0473: The stop's awaiting-signoff rule reads one half of a two-half gate, so a stop exits clean over work the session could still do

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Verification depth:** functional (13 criteria green, including two new controls: a unit still owing its adversarial pass stays in the stop's refusal, and sprint-level coverage counts as that pass. Four mutants applied singly, purged, restored byte-identical - the evidence half dropped, sprint coverage discounted, per-unit evidence discounted, and the corrected rule itself: all KILLED. The fixtures now record the adversarial pass, so the class asserts the state it is named for rather than pinning the defect)
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Found by an independent seat briefed from the SHIPPED `critic.py brief`, unit-scoped to the unit's own `Affects` against base `edb9fdf0`, with findings classified by execution. Repaired in the same session; recorded here because the repair is post-close work on a unit already at Fixed, and must be a filed unit rather than an ad-hoc edit.

`_awaits_signoff` consulted only the sign-off half of the two-role bar. The bar has two halves, and only the SIGNATURE is beyond the authoring session: `record_evidence` accepts an authoring-session reviewer while `record_signoff` refuses that same id. So a unit still owing its adversarial pass is work the run could dispatch, and classifying it as 'awaiting a sign-off this session cannot give' dropped it from `cmd_stop`'s refusal - the silent-loss direction the parent bug was filed to end, returning through its own repair. The operator-facing message 'they are finished bar an independent reviewer-of-record signature' was false whenever the evidence half was also unmet, and the two states were indistinguishable.

The owning test class PINNED the defect: every fixture omitted the evidence row, and one test was named for a state its own fixture never created. Proven by applying the CORRECT rule as a mutant, which failed 5 of the class's 10 tests - recorded as LL0051.

## Steps to Reproduce

1. Fixture: a unit at Review past the cutoff with NEITHER half met.
2. `_awaits_signoff` -> True; `blocked_by_pending` unblocked -> []; `cmd_stop` rc=0.
3. transition's own gate on the same unit reports TWO halves unmet.
4. `critic.record_evidence` with an authoring-session reviewer is ACCEPTED, while `record_signoff` with that id is REFUSED - so the evidence half is session-doable.

## Proposed Fix

Read BOTH halves the way `transition._two_role_gate` reads them: the evidence half is satisfied by a per-unit evidence row OR sprint-level coverage, and only when it is met and the signature is not does the unit count as awaiting a signature. Rebuild the test fixtures to record the adversarial pass, so the class asserts the state it is named for.

## Acceptance Criteria

- [x] The behaviour described is corrected: Found by an independent seat briefed from the SHIPPED `critic.py brief`, unit-scoped to the unit's own `Affects` against base `edb9fdf0`, with findings...
- [x] The proposed fix lands, pinned by a test: Read BOTH halves the way `transition._two_role_gate` reads them: the evidence half is satisfied by a per-unit evidence row OR sprint-level coverage, and only...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Filed |
