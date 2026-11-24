# BG1269: `sprint plan` puts every unit in one shared-file cluster when they share a reference doc, so a collision in one code file is hidden and nothing keeps those units sequential

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-delivery.md, changelog.d/BG1269.md
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

- [ ] **AC1** Given a batch whose units all declare one reference doc and two of which also declare one code file, when `sprint.py plan` prints its shared-file report, then a line of its own names that pair and the code file they share. Fails on: the code file listed only inside the batch-wide cluster.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SharedFileClusterTests::test_a_pair_sharing_a_code_file_is_named_on_its_own_line
- [ ] **AC2** Given the same batch, when the lane partition is computed, then the two units sharing the code file sit in one lane or in strictly sequential waves. Fails on: both units placed in parallel lanes of one wave.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LanePartitionTests::test_units_sharing_a_code_file_are_never_parallel
- [ ] **AC3** Given units that share only a prose file, when the batch is planned, then the share is reported as advisory and the partition is unchanged. Fails on: a shared reference doc forcing the units sequential.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SharedFileClusterTests::test_a_shared_prose_file_stays_advisory

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
| 2026-11-24 | orchestrator (delegate under D0545) | Affects widened for run twenty-six's SPA lane: reference-sprint.md (the lane partition and cluster passages) and reference-delivery.md say lanes share no file at all, which after the fix holds for code files only |
