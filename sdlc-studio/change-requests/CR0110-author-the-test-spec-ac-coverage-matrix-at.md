# CR-0110: Author the test-spec AC Coverage Matrix at --goal design (shift the AC-to-test bridge left)

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-06-24
> **Created-by:** sdlc-studio file

## Summary

The --goal design breakdown produces Ready stories + story points but never authors the test-spec; it only runs ts-check 'where a test-spec exists' (reference-sprint.md). So the AC-to-test bridge (CR0085) is built at IMPLEMENT, not design: a field agent delivering the sprint spent a large part of the run reverse-engineering the AC->test mapping, finding AC-coverage gaps (US0016: 8 ACs / 4 tests; US0012 missing AC2/3/6), and repointing ~48 prose Verify lines to real jest titles. Have --goal design author the epic's test-spec AC Coverage Matrix (each AC -> a planned test case/title) so Verify lines are executable-by-construction and implement is mechanical. Pairs with epic-ts (CR0096), which already requires the TS at Done - produce it at design instead of discovering its absence at Done.

## Acceptance Criteria

- [x] --goal design authors (or requires) the epic's test-spec with an AC Coverage Matrix mapping every story AC to a planned test case/title, at epic scope (single-story exempt, per CR0096)
- [x] Verify lines produced/repointed at design are executable (runner-targeted DSL) or explicitly 'manual' - no prose-curl placeholders; the CR0109 audit lint passes on the designed backlog
- [x] the TS that the Done-gate / epic-ts (CR0096) requires is produced at design, not discovered missing at implement/Done; ts-check passes on the produced matrix
- [x] documented in reference-sprint.md (the design rung) + reference-test-spec.md; degrades for single-story scope; CHANGELOG entry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | audit | Raised |
