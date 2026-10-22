# CR-0652: critic.py self-check record has no surface for a documentation unit's own prose, so the claims a doc unit makes in the file it changes cannot be recorded under that file

> **Status:** Proposed
> **Priority:** Low
> **Type:** Feature
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** US1090 build, 2026-10-22.
> **Date:** 2026-10-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-22T06:57:22Z

## Summary

US1088's record accepts claims on the commit message, each changelog fragment the unit's Affects declares, and the brief's named optional surfaces (docstrings, comments, Resolutions, CHANGELOG). A documentation unit's main claims live in the prose file it changes: US1090's 23 claims were mostly about the AGENTS.md paragraph it rewrote, and its builder had to file them under the commit message, since a surface naming AGENTS.md is refused as one the self-check does not name.

## Impact

A doc unit's self-check record misattributes its claims, so a reviewer cannot tell which surface each was checked against.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Recommendation

Accept each non-test file the unit's Affects declares as a named optional surface, so a claim made in a changed reference page or AGENTS.md is recorded against that file; keep the commit message and the fragments required.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | Claude Opus 5.5 | Raised |
