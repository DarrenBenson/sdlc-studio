# BG1200: mutation.changed_lines reports no lines when git's color.ui or color.diff is always, because the +++ b/ header arrives wrapped in ANSI codes

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, changelog.d/BG1200.md
> **Evidence:** BG0958 builder report, 2026-11-04, outside-the-units item 1.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T12:17:18Z

## Summary

2026-11-04, BG0958's build (run five). BG0958 made `changed_lines` pass explicit `--src-prefix=a/ --dst-prefix=b/`, so mnemonicprefix and noprefix no longer break it. With `color.ui=always` (or `color.diff=always`) git wraps the `+++ b/<path>` header in escape codes, no header matches, and every file reads as unchanged.

## Steps to Reproduce

1. In a fixture repository, `git config color.ui always`.
2. Change one line of a tracked file and call `mutation.changed_lines(root)`: it returns {}.

## Proposed Fix

Pass `--no-color --no-ext-diff` to the diff `changed_lines` runs, as critic.py:3401 already does. BG0958's review found `diff.external` empties the map the same way.

## Acceptance Criteria

- [ ] **AC1** With color.ui=always in the repository config, `changed_lines` still reports the changed lines.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py

## Impact

A mutation run on a machine with colour forced on finds nothing to mutate and reports a clean result it never tested.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
| 2026-11-04 | Claude Opus 5.5 (orchestrator) | BG0958's review: diff.external empties the map too; the fix adds --no-ext-diff |
