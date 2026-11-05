# BG1226: Generated-doc drift is found only by unit suites after the full selected run, never by a cheap pre-commit lane

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .githooks/pre-commit, tools/tests/test_pre_commit_docgen.py, changelog.d/BG1226.md
> **Evidence:** Run six landing logs for US1117 and US1118, scratchpad run6/hand-US1118/commit.log.
> **Created:** 2026-11-05
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-05T11:07:29Z

## Summary

2026-11-05, run six. US1117 and US1118 each added CLI surface to sprint.py without regenerating reference-scripts-surface.md. The pre-commit hook has no docgen lane, so the drift surfaced only as three `test_lean_`* assertions ('docgen surface: 0 drift item(s)') after the selected suites ran for 1,016 s and over 1,500 s. `docgen.py surface --check` takes seconds. Each such refusal costs a whole hook run of wall-clock and a second commit.

## Steps to Reproduce

1. Add a flag to a sprint.py subcommand and stage it without regenerating reference-scripts-surface.md.
2. Commit: the hook runs every selected suite, then refuses on the docgen assertions.

## Proposed Fix

Add a cheap pre-commit lane that runs the three `docgen.py ... --check` lanes (surface, references, reading-guides) when a staged path is a script, a reference or a help file, before the suites are decided, naming the regenerate command in its refusal.

## Acceptance Criteria

- [ ] **AC1** Given a staged script change whose CLI surface drifts from reference-scripts-surface.md, the pre-commit hook refuses in its cheap guards before any suite runs, naming docgen and the regenerate command; with the regenerated file staged the lane passes, and a commit staging no script, reference or help file skips the lane.
  - **Verify:** pytest tools/tests/test_pre_commit_docgen.py

## Impact

A commit to a hub script pays 15 to 25 minutes of suites to learn what a few seconds of docgen would have said.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | claude | Filed |
