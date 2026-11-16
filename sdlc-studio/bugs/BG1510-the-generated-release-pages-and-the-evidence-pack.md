# BG1510: The generated release pages and the evidence pack lag every signature and filing after the cut, and the release-gate workflow names no step to regenerate them before the tag

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/templates/workflows/release-gate.md, .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T17:51:50Z

## Summary

docs/evidence.md, docs/known-issues.md and the release notes' disclosed-defect line are generated at the cut, but the release run's own report is always signed after the cut and findings keep being filed. For 6.4 they named RPT0032 as the last report and an older defect count until D0500 regenerated them by hand (cd0e478e), and the evidence pack had not been written at all.

## Steps to Reproduce

1. Cut a release, then sign the release run's report or file a finding.
2. Read docs/evidence.md and docs/known-issues.md: they still name the earlier last report and the earlier open-defect count.

## Proposed Fix

Add a pre-tag step to the release-gate workflow, or a tag-check refusal, that compares the generated pages and the evidence pack with the records at the tagged commit and names the regenerating command when they differ.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: docs/evidence.md, docs/known-issues.md and the release notes' disclosed-defect line are generated at the cut, but the release run's own report is always signed...
- [ ] **AC2** The proposed fix lands, pinned by a test: Add a pre-tag step to the release-gate workflow, or a tag-check refusal, that compares the generated pages and the evidence pack with the records at the tagged...

## Impact

A tag can ship pages that misstate the signed evidence and the open-defect disclosure the release is judged on.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
