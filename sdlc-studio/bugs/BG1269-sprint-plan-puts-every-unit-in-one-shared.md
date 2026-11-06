# BG1269: `sprint plan` puts every unit in one shared-file cluster when they share a reference doc, so a collision in one code file is hidden and nothing keeps those units sequential

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** the orchestrator's friction log (R8-F12), from run eight (RUN-01M6RZQZ)'s plan and the BG1254 and US1132 landings
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:38:33Z

## Summary

Run eight's plan printed one shared-file cluster holding all 13 units of lane 2, joined by `reference-config.md` and `reference-sprint.md`, with `lib/cost_anatomy.py` listed third and the rest as '(+13 more)' (`_shared_file_clusters`, `.claude/skills/sdlc-studio/scripts/sprint.py:1954`). A cluster spanning the batch gives a wave split nothing to use, so BG1254 (the run window) and US1132 (the subagent start budget) were built from the same base though both changed `cost_anatomy.build`; the groomer flagged the shared file, and the second landing hit a code conflict the 3-way apply could not resolve. Prose files most units append to merge cleanly; a shared code file is what conflicts, and the report does not tell the two apart.

## Steps to Reproduce

Run `sprint.py plan` on a batch whose units all declare a shared reference doc and two of which also declare one code file: one cluster names every unit and the code file is not singled out.

## Proposed Fix

Rank each cluster's files by kind and print the pairs sharing a code file on a line of their own (for example 'BG1254, US1132 share `lib/cost_anatomy.py`'), and have the lane partition keep units that share a code file in one lane or in strictly sequential waves, the later built on the earlier's landed tree; leave a shared prose file that each unit appends to as advisory.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Run eight's plan printed one shared-file cluster holding all 13 units of lane 2, joined by `reference-config.md` and `reference-sprint.md`, with...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Run `sprint.py plan` on a batch whose units all declare a shared reference doc and two of which also declare one code file: one cluster names every unit and...
- [ ] **AC3** The proposed fix lands, pinned by a test: Rank each cluster's files by kind and print the pairs sharing a code file on a line of their own (for example 'BG1254, US1132 share `lib/cost_anatomy.py`')...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
