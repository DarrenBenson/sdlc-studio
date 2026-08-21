# BG0603: Stacked Verify lines are refused at Draft and Ready but not on an Open bug

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`lint_stacked_verifiers` refuses a criterion carrying more than one `Verify:` line, but `verify_ac.py` applies it only at Draft and Ready. A bug sits at Open for its whole delivery, so the shipped command never refuses the shape while it is being authored - the only thing that catches it is a repo-only census in `tools/tests/test_known_issues.py`, which does not ship and does not run in a consuming project. A stacked criterion cannot report which of its claims failed, which is why the rule exists.

## Steps to Reproduce

Author an Open bug with two `Verify:` lines under one criterion. Run `verify_ac.py lint --unit <id>`: it passes. Move the same artefact to Ready and it refuses. The repo census catches it here only because this repo happens to ship one.

## Proposed Fix

Apply `lint_stacked_verifiers` at Open as well. The status gate was presumably meant to spare half-written drafts, but Open is the status a bug occupies while its criteria are final, so it is the wrong status to exempt. Pin the new status set in a test - LL0027, gate the rule in the command people actually run.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `lint_stacked_verifiers` refuses a criterion carrying more than one `Verify:` line, but `verify_ac.py` applies it only at Draft and Ready.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Author an Open bug with two `Verify:` lines under one criterion.
- [ ] **AC3** The proposed fix lands, pinned by a test: Apply `lint_stacked_verifiers` at Open as well.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Filed |
