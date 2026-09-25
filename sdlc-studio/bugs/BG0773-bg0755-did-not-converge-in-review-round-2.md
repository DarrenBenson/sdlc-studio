# BG0773: BG0755 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_batch_story_fields.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/help/artifact.md, changelog.d/BG0755.md, .claude/skills/sdlc-studio/help/help.md, .claude/skills/sdlc-studio/reference-scripts-create.md
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T16:22:32Z

## Summary

BG0755 was rejected at round 2, the review cap, by qa-rev-BG0755, so it was carried as a known issue rather than reviewed again. The findings still open: [regression] US0081's Verify -k now selects 2 of its former 3 tests and none on the full template while its AC1 names the full-template story header, because the rename orphaned batch\_defaults\_to\_full\_template and the default flip moved test\_batch\_creates\_wires\_and\_keeps\_drift\_zero to minimal, fix 1 line [LC-002]; [pre-existing] non-blocking: verify\_ac stamps --staged does not see a -k term that no longer matches; [pre-existing] non-blocking: the dropped-content probe passes a value that appears elsewhere in the render

## Steps to Reproduce

1. Read the round 2 REJECT of BG0755 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG0755 again in a later run.

## Acceptance Criteria

- [ ] **AC1** Given BG0755's carried work (sdlc-studio/.local/BG0755-carried-r2.patch) applied onto main, then BG0755's four criteria pass through their own Verify selectors. Fails on: a landing that drops the carried refusal of non-text user-story values or the lean batch default
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_batch_story_fields.py
- [ ] **AC2** Given the carried work, when US0081's stamped selector runs, then at least one selected test renders a story from the FULL template and asserts its header against templates/core/story.md. Fails on: the carried patch as it stood, where `test_batch_creates_wires_and_keeps_drift_zero` moved to the minimal default and the renamed `batch_defaults_to_full_template` term matches nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::BatchTests::test_batch_creates_wires_and_keeps_drift_zero

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
| 2026-09-25 | Engineering seat | Groomed: two criteria for landing BG0755's carried work with US0081's full-template selection restored on the test side, so US0081's criterion fingerprint does not move |
