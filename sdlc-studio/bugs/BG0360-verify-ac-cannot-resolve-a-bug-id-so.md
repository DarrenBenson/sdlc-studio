# BG0360: verify_ac cannot resolve a bug id, so no bug can prove its own acceptance criteria

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; the runner's prefix set mutation-killed)
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

Three lanes hit this independently. `verify_ac run --id` resolves stories only, so a bug carrying authored acceptance criteria cannot run them. This sprint's own return rule - a lane verifies its unit before returning - is therefore unrunnable for every bug in the batch, and BG0352's lane correctly returned BLOCKED rather than claim a verification it could not perform. It also means the AC-verify Done gate, the release lane's unspecified-AC refusal and the close reconcile all speak only for stories.

## Steps to Reproduce

Reported by a delivery lane during RUN-01KYKVZM; see the summary for the measurement.

## Proposed Fix

See the summary; the remedy is stated with the defect.

## Acceptance Criteria

### AC1: A bug in an open run's batch is verified alongside the stories rather than skipped

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RunStateScopeTests::test_batch_units_run_including_bugs
- **Verified:** yes (2026-07-28)

### AC2: A batch id with no unit file behind it REFUSES, so the fix does not become a silent skip the completion gate reads as nothing to fail

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RunStateScopeTests::test_a_batch_id_with_no_unit_file_refuses
- **Verified:** yes (2026-07-28)

### AC3: A run whose batch resolves to no verifiable unit still refuses rather than falling back to a whole-workspace run

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RunStateScopeTests::test_batch_stories_run_and_no_open_run_exits_2
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction) | Filed |
| 2026-07-28 | Claude Opus 5 | Criteria authored at delivery. This bug was filed by the audit with `See the summary` in place of a contract, which is the shape the criteria floor refuses - and it refused this one at the commit. The Verify lines are EXECUTABLE because of the change this bug pair makes: before it, a bug could not carry one. |
