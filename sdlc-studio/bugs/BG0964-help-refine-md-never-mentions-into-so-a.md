# BG0964: help/refine.md never mentions `--into`, so a story added to an already-refined epic is made with `artifact.py new` and carries no Delivers link

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/help/refine.md, .claude/skills/sdlc-studio/reference-scripts-create.md, changelog.d/BG0964.md
> **Evidence:** Found 2026-10-06/07 during the triage session that filed BG0955-BG0963 in this repository. US0991.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:36:02Z

## Summary

`refine.py add --into EPxxxx` (and `apply --into`) adds stories to an existing open epic and wires each story's `Epic:` and `Delivers:`. help/refine.md describes `add` only as 'a second epic against an already-decomposed request'. Splitting US0986 on 2026-10-06, the author found no documented way to add a story to EP0274, used `artifact.py new --type story --epic EP0274`, and US0991 was created without `Delivers: CR0611`, which was then added by hand.

## Steps to Reproduce

Read help/refine.md for adding a story to an existing refined epic: only a second epic is described; `refine.py add --help` shows `--into`.

## Proposed Fix

Document `apply --into` and `add --into` in help/refine.md and the scripts catalogue, with the case they serve: a story split out of one already refined.

## Acceptance Criteria

- [ ] **AC1** help/refine.md documents `--into` for both `apply` and `add`, and the doc-coverage check passes
  - **Verify:** shell grep -q -- '--into' .claude/skills/sdlc-studio/help/refine.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Filed |
