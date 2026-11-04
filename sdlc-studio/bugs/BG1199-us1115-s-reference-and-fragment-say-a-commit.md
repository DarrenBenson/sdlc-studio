# BG1199: US1115's reference and fragment say a commit whose every id is a mention is attributed no files, but a one-id subject whose only id is a Mentions: id is attributed its files

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-scripts-verify.md, CHANGELOG.md, changelog.d/BG1199.md
> **Evidence:** US1115 round-1 verdict, scratchpad run5/US1115-verdict-r1.txt.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T11:23:17Z

## Summary

2026-11-04, US1115's review (qa-seat-US1115-r1, APPROVE, non-blocking). reference-scripts-verify.md:244 says a commit whose every id is a mention is skipped by the floor, and changelog.d/US1115.md:15 says it is attributed to no id. In a fixture, subject `docs: file BG0989 for the lane` with body `Mentions: BG0989` gives `_git_touched_by_id` {BG0989: {a.py}}. The sentence before each states the true one-id rule, so each pair contradicts itself on this shape.

## Steps to Reproduce

1. A fixture repository with one commit touching a.py, subject `docs: file BG0989 for the lane`, body `Mentions: BG0989`.
2. `engagement_floor._git_touched_by_id(root)` returns {BG0989: {a.py}}.

## Proposed Fix

Scope both sentences to a commit whose subject names several ids, each only a mention.

## Acceptance Criteria

- [ ] **AC1** reference-scripts-verify.md states the every-id-a-mention rule only for a subject naming several ids.
  - **Verify:** shell ! grep -n 'whose every id is a mention is skipped' .claude/skills/sdlc-studio/reference-scripts-verify.md

## Impact

A reader relies on a Mentions: line to keep a one-id commit's files off that id, and the floor counts them anyway.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
