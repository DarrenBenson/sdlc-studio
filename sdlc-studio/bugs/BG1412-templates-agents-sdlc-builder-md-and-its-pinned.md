# BG1412: templates/agents/sdlc-builder.md and its pinned .claude/agents copy still tell a builder to run verify_ac without --dry-run

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/templates/agents/sdlc-builder.md, .claude/agents/sdlc-builder.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_builder_dry_run.py, changelog.d/BG1412.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: review land
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:13:11Z

## Summary

A plain run writes into the unit's artefact outside its Affects.

## Steps to Reproduce

grep `verify_ac` in both files.

## Proposed Fix

Add --dry-run.

## Acceptance Criteria

- [ ] **AC1** Given the builder agent files, when read, then `verify_ac` is run with --dry-run. Fails on: a bare `verify_ac` run.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_builder_dry_run.py::BuilderDryRunTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
