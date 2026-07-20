# CR-0363: the mutation gate should report the coverage its test command actually reaches

> **Status:** Complete
> **Decomposed-into:** EP0091
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/help/mutation.md
> **Date:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

A mutation run scoped below its target's real test coverage manufactures survivors, and nothing in the output says so. Pointed at one test file, the gate reports 10 survivors for audit.py; pointed at that module's actual tests, the same code and the same mutants report 4. Six of the ten were artefacts of the command rather than gaps in the tests. This is not hypothetical: it produced BG0203, whose two named survivors were both already pinned, and the same error was repeated while investigating that bug before being caught by widening the command. A narrow test command does not under-report coverage, it OVER-REPORTS ABSENCE - and a survivor is trusted, filed as a bug, and paid for twice. The gate has the information needed to warn: it knows the target file and the test command, and can tell whether test files that exercise that module fall outside the command's selection.

## Impact

Every consumer of the mutation gate. A false survivor costs a filed bug, an investigation, and a correction to the record - several times the cost of the finding being right. Worse, it erodes trust in a real survivor, which is the signal the gate exists to produce.

## Acceptance Criteria

- [ ] the run reports which test files its test command selects, alongside the survivor list
- [ ] a test file that references the target module but falls outside the command's selection is named as a warning, since that is the manufactured-survivor condition
- [ ] the test command is recorded in the JSON output beside the result, so a survivor cannot be read without knowing what was run against it
- [ ] the warning is advisory and never blocks: a deliberately narrow run stays legal and stays honest about what it covered

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Raised |
