# BG0644: the test-noise ratchet compares a selected subset against a whole-suite baseline

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** tools/skill-tests.sh, tools/test_noise.py
> **Created:** 2026-09-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The test-noise ratchet is an absolute count checked against a SELECTED subset, so a commit that adds leaks passes the gate it is supposed to fail. tools/skill-tests.sh says of its baseline: "Frozen here, the gate fails the moment a change adds one." That is true only of a full run. The commit-msg hook passes a selection (.githooks/commit-msg:268), the check is `count <= baseline` over whatever that subset printed, and a subset almost always prints fewer than 119 lines whatever it added.

## Steps to Reproduce

Commit 8f808b0c..9260c513 added two shipped warnings - `file_finding.report_unverifiable_criteria` (BG0636) and `critic`'s unreadable-closure report (BG0631). They leak 37 lines across 24 uncaptured call sites in ten test modules. Every one of those commits passed the pre-commit and commit-msg gates, because each selected subset stayed under 119. The full run in CI printed 142 against the baseline of 119 and failed - after the push, with nobody reading it (BG0642). Reproduce with: `bash tools/skill-tests.sh test_file_finding.py` (green, leaks 13) then `bash tools/skill-tests.sh` (red at 142).

## Proposed Fix

Make the ratchet measure what the run can be held to. Either scale the baseline to the selection (a per-module leak budget summed over the selected set), or compare against the SAME selection at the base ref so the check is a delta rather than an absolute. A per-module budget is the honest shape: it is the only one under which a subset that adds a leak cannot pass.

## Acceptance Criteria

- [ ] **AC1** Running the selected subset that contains a newly-leaking module refuses, where today it passes: the check compares like with like rather than a subset total against a whole-suite baseline.
- [ ] **AC2** The comment in tools/skill-tests.sh states the guarantee the check actually provides - a claim the selected path can satisfy, not one only a full run can.
- [ ] **AC3** A full run still refuses at the recorded total, so the existing whole-suite protection is not traded away for the new one.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-03 | sdlc-studio | Filed |
