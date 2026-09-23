# BG0745: sprint_report check reads a report hand-edited after signing as VALID

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
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

- [ ] **AC1** The behaviour described is corrected: `sprint_report.py check` re-derives from the tree and never compares the filed page's own figures with its recorded fingerprint, so a report JSON or markdown...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Close a run, sign it, then hand-edit a figure in the filed RPTxxxx.json and run `sprint_report.py check --report RPTxxxx`: it prints VALID.
- [ ] **AC3** The proposed fix lands, pinned by a test: Have `check` compare the filed page's own figures with its recorded fingerprint, and report INVALID when they differ, not only when a re-derivation drifts.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-23 | sdlc-studio | Filed |
