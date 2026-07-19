# US0268: Order the pre-commit lanes cheapest-first so a reworded comment does not cost a full unit-suite run

> **Status:** Ready
> **Delivers:** CR0361
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/pre-commit
> **Epic:** EP0086
> **Points:** 3

## User Story

**As an** agent committing a unit
**I want** the cheap guards to report before the expensive ones run
**So that** a one-line markdown or style error costs seconds instead of a full unit suite

## Context

Measured on this repo, not assumed. In `.githooks/pre-commit` the unit suites run at lines
117-136 and the markdown lanes at 142-164, so a markdown error is reported only after
`skill-tests` and `tool-tests` have completed. The hook itself announces the cost up front:
"expect ~132s from the last 10 run(s)".

This fired twice in one session. An MD028 (blank line inside a blockquote) and an MD024
(duplicate heading) each cost a full suite run before the hook said what was wrong. Neither
error could have been affected by any test.

Note `CR0361` names `tools/pre-commit.sh`, which does not exist; the hook is
`.githooks/pre-commit`, installed via `core.hooksPath` by `tools/enable-hooks.sh`.

## Acceptance Criteria

### AC1: the markdown lanes run before the unit suites

- **Given** the tracked pre-commit hook
- **When** its lane order is read
- **Then** both markdown lanes are invoked before `skill-tests`
- **Verify:** shell test "$(grep -n 'run \"markdown\"' .githooks/pre-commit | head -1 | cut -d: -f1)" -lt "$(grep -n 'run \"skill-tests\"' .githooks/pre-commit | head -1 | cut -d: -f1)"

### AC2: a markdown-only failure never reaches the unit suites

- **Given** a staged commit whose only defect is a markdown-mechanics error
- **When** the hook runs
- **Then** it fails on the markdown lane and the unit suites never execute, so the failure
  reports in seconds rather than after ~132s
- **Verify:** shell bash tools/tests/test_hook_lane_order.sh

### AC3: the skip path still announces what did not run

- **Given** a docs-only commit, where the hook already skips the unit suites
- **When** the hook completes
- **Then** it still names the lanes that ran, so a reordering does not silently drop a lane
  from a docs-only commit's coverage
- **Verify:** grep "Docs-only commit: style, links, budgets, markdown and the artefact gate still ran" .githooks/pre-commit

### AC4: no lane is lost in the reorder

- **Given** the hook before and after the change
- **When** the set of lane names is compared
- **Then** it is identical - this story changes ORDER only, never coverage
- **Verify:** shell bash tools/tests/test_hook_lane_order.sh

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-19 | sdlc-studio | Groomed: ACs written from the measured lane order and two real refusals |
