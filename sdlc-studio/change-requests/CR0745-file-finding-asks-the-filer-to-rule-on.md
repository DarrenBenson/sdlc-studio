# CR-0745: file_finding asks the filer to rule on a close duplicate before it writes, instead of warning after

> **Status:** In Progress
> **Decomposed-into:** EP0378
> **Priority:** Medium
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, changelog.d/CR0745.md
> **Evidence:** the website's RUN-01M7R7KN, 2026-11-19: orchestrator; artifact.duplicate_candidates scores the pair 0.77, sharing README.md
> **Date:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T07:45:35Z

## Summary

When `file_finding.py file` finds an open or terminal artefact of the same type that shares every Affects path with the new finding and scores at or above a bar on the duplicate lens, refuse before allocating an id unless the filer passes `--distinct-from <id>` (recorded on the new artefact) or chooses to add evidence to the existing one. Today the lens runs, but its warning prints after the artefact is written and the id minted, so an agent filing mid-task reads `filed <id>` and moves on.

## Impact

On 2026-11-19 the website's deploy filed a High bug for the runbook's rsync failure that an inbox bug filed three days earlier already described, with the same Affects and a duplicate-lens score of 0.77. The warning came after the write, the orchestrator missed it, and the duplicate went on to be triaged, groomed and added to the run before anyone noticed. The repository's own failure mode is a rule read and not followed (LL0027), and a warning printed after the fact is that rule.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Raised |
| 2026-11-23 | Claude Opus 5.5 (run twenty-three orchestrator) | Triaged by the product seat during run twenty-three planning: Approved (D0595) |
