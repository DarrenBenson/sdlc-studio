# BG1152: artifact.py batch writes a list-valued affects as a Python repr, so the Affects line reads ['hooks/pre-push']

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, changelog.d/BG1152.md
> **Evidence:** US1080 APPROVE by qa-seat-US1080-r1, [pre-existing] finding.
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T03:58:22Z

## Summary

qa-seat-US1080-r1 (2026-11-01) found that a `batch` spec whose `affects` is a JSON list renders the Affects line as `> **Affects:** ['hooks/pre-push']`. That line is not a path list. Every reader that parses Affects (the planner's clusters, the review brief's diff scope, the interface router) then sees one bracketed token, so the unit mints against the first Primary and its scope is wrong. This predates US1080, and no open bug records it.

## Steps to Reproduce

1. `artifact.py batch` with a spec item `{"type": "story", "title": "x", "affects": ["hooks/pre-push"]}`.
2. Read the minted file's Affects line: `['hooks/pre-push']`.

## Proposed Fix

Join a list-valued affects with ', ' before rendering, as a string affects is written, and refuse any other non-string type by name.

## Acceptance Criteria

- [ ] **AC1** A batch spec item with a list-valued affects renders `> **Affects:** a, b`, and the minted unit's Affects parses to those paths.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py

## Impact

A unit minted from a JSON spec carries an Affects line that no reader parses as paths.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
