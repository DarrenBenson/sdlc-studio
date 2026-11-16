# BG1504: The sdlc-builder agent card does not confine a builder's clean-up to paths it created, so a builder deleted every tmp.* directory in the shared test temp directory

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/templates/agents/sdlc-builder.md, .claude/agents/sdlc-builder.md, .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py, changelog.d/BG1504.md
> **Evidence:** Run fifteen (RUN-01M7HA6R) BG1498 builder report, 2026-11-16.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T08:20:41Z

## Summary

In run fifteen the BG1498 builder ran `rm -rf ~/.cache/sdlc-tmp/tmp.*` to clean up after a refused mktemp, although it had created nothing there. That directory is the TMPDIR every lane and the commit hook's tests share, so the same command in a parallel wave deletes another lane's live fixtures and fails its tests for no reason of its own. No other lane was running then, so nothing was lost. The builder card (templates/agents/sdlc-builder.md and its installed copy) says nothing about clean-up; the builder only learned the rule when the orchestrator told it afterwards.

## Steps to Reproduce

1. Spawn two sdlc-builder lanes in one wave.
2. Have one clean up with a glob over the shared TMPDIR.
3. The other lane's tmp.* fixtures vanish mid-test.

## Proposed Fix

Add a rule to the builder card: remove only paths you created and recorded, never a glob over a shared directory such as TMPDIR, and pin the sentence with a test that reads the card.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: In run fifteen the BG1498 builder ran `rm -rf ~/.cache/sdlc-tmp/tmp.*` to clean up after a refused mktemp, although it had created nothing there.
- [ ] **AC2** The proposed fix lands, pinned by a test: Add a rule to the builder card: remove only paths you created and recorded, never a glob over a shared directory such as TMPDIR, and pin the sentence with a...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
