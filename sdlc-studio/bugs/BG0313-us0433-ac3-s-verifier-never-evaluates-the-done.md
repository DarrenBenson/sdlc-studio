# BG0313: US0433 AC3's verifier never evaluates the done-gate nor transitions anything to Deferred: it asserts a run-state proxy f

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** sdlc-studio/stories/US0433-sprint-batch-drop-and-add-mutate-an-open.md
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

The verifier for 'the Deferred unit still blocks the done-gate while the dropped unit does not' performs neither the Given nor the When: no unit is transitioned to Deferred and the done-gate is never invoked - the test only asserts batch-list membership in run-state.json. If the gate were changed to skip Deferred units or stop reading state['batch'] (the exact regressions the AC exists to rule out), the test stays green; no test in `test_sprint.py` couples Deferred or dropped units to the gate either.

## Steps to Reproduce

Evidence (AC3 (line 39); `test_run_state.py` lines 730-739; sprint.py `_done_gate_preflight` (~line 4509)): `test_run_state.py`:730-739 asserts only assertIn/assertNotIn on `run_state.read()`'s batch, with the gate linkage present only as a comment; grep of `test_sprint.py` finds no test pairing Deferred with the done-gate; story is Done, Verified: yes 2026-07-26.

## Proposed Fix

Replace or supplement the verifier with a test that builds a batch containing one Deferred and one dropped unit and asserts `_done_gate_preflight`'s refusal set directly, then re-run `verify_ac` for the story.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
