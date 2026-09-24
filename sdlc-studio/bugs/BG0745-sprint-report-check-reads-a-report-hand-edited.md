# BG0745: sprint_report check reads a report hand-edited after signing as VALID

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_integrity.py
> **Verification depth:** functional (the criteria edit a filed page's JSON figure, its Markdown twin, and sign it through the seal's own writer; the real RPT0006 reads VALID, and 12 reviewer mutants were killed)
> **Created:** 2026-09-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`sprint_report.py check` re-derives from the tree and never compares the filed page's own figures with its recorded fingerprint, so a report JSON or markdown edited after the seal still checks VALID. US0878 now refuses such an edit before the seal, but a signed page cannot be audited. Found by the US0878 round-2 review on RUN-01M36R3D.

## Steps to Reproduce

Close a run, sign it, then hand-edit a figure in the filed RPTxxxx.json and run `sprint_report.py check --report RPTxxxx`: it prints VALID.

## Proposed Fix

Have `check` compare the filed page's own figures with its recorded fingerprint, and report INVALID when they differ, not only when a re-derivation drifts.

## Acceptance Criteria

- [x] **AC1** The behaviour described is corrected: `sprint_report.py check` re-derives from the tree and never compares the filed page's own figures with its recorded fingerprint, so a report JSON or markdown...
- [x] **AC2** Following the recorded steps no longer reproduces the defect: Close a run, sign it, then hand-edit a figure in the filed RPTxxxx.json and run `sprint_report.py check --report RPTxxxx`: it prints VALID.
- [x] **AC3** The proposed fix lands, pinned by a test: Have `check` compare the filed page's own figures with its recorded fingerprint, and report INVALID when they differ, not only when a re-derivation drifts.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_integrity.py::PageIntegrityTests
  - **Verified:** yes (2026-09-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-23 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Fixed by US0883 (RUN-01M3891F): the story's criteria are this bug's proposed fix, and its selectors verify it here |
