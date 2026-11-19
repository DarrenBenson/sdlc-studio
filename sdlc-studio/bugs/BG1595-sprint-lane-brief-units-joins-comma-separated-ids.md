# BG1595: sprint lane brief --units joins comma-separated ids into one id and refuses it, instead of splitting on commas or saying the ids are space-separated

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG1595.md
> **Evidence:** .local/run17/lane-meta.err, 2026-11-18.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T16:20:04Z

## Summary

`sprint lane brief --units US1315,US1319,US1320` refused with 'REFUSED US1315US1319US1320: no artefact on disk resolves to this id': the commas are stripped and the ids run together. Space-separated ids work. Commit subjects and Affects use comma lists, so a comma list is the natural thing to type.

## Steps to Reproduce

Run `sprint.py lane brief --units US1315,US1319,US1320`: it refuses 'US1315US1319US1320'.

## Proposed Fix

Split --units values on commas as well as spaces, or refuse a comma list by naming the space-separated form.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `sprint lane brief --units US1315,US1319,US1320` refused with 'REFUSED US1315US1319US1320: no artefact on disk resolves to this id': the commas are stripped...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Run `sprint.py lane brief --units US1315,US1319,US1320`: it refuses 'US1315US1319US1320'.
- [ ] **AC3** The proposed fix lands, pinned by a test: Split --units values on commas as well as spaces, or refuse a comma list by naming the space-separated form.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
