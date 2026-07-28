# BG0393: goal_panel returns a verdict when no seat answered, and silently discards a verdict under a mismatched clause key

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** adversarial review of RUN-01KYMJEM, reproduced by the reviewer
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

A panel where nothing was answered returns overall `partial` rather than None - the function raises on an empty seat list precisely because 'an empty panel returns a verdict nobody gave', then does exactly that. Worse, `supplied.get(clause)` is keyed by the stripped clause, so a key differing by case or whitespace drops a seat's verdict without error and a `missed` becomes `partial`.

## Steps to Reproduce

`goal_panel(`'.',['c1','c2'],['qa','arch'],'author') -> verdict 'partial' with no answers given.

## Proposed Fix

Overall None when no clause is answered; raise on a verdicts key matching no clause, as an unrecognised verdict word already does.

## Acceptance Criteria

- [ ] A panel nobody answered returns no verdict.
- [ ] A verdicts key matching no clause is refused rather than dropped.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
