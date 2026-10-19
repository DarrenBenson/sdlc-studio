# BG1066: The product seat approves only stories that serve a Primary persona's goal, so a declared Secondary's stories have no approving lens

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/templates/personas/amigos/product.md, sdlc-studio/personas/seats/product.md, .claude/skills/sdlc-studio/scripts/tests/test_seat_admits_secondary.py, changelog.d/BG1066.md
> **Evidence:** RV0028 finding PER-3; templates/personas/amigos/product.md:21,:48,:78; personas/index.md:11-15; prd.md:104-106.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T07:49:57Z

## Summary

The shipped product amigo (templates/personas/amigos/product.md:21, :48, :78) and this project's card (sdlc-studio/personas/seats/product.md:23, :42, :50, :80) approve 'a story [that] serves a Primary-persona goal'. A project may declare a Secondary with goals of its own: this one declares Jonah Reyes, with PRD outcomes O6-O8, eight stories and RPT0012's goal 'Jonah's team installs v6', and the goal-review brief already lists Secondary End goals (US0928). The seat's lens excludes a declared cast role.

## Steps to Reproduce

Read templates/personas/amigos/product.md:78 'Approves: a story serves a Primary-persona goal'; brief the product seat on a story whose Persona is the declared Secondary -> its charter gives it no ground to approve.

## Proposed Fix

Reword both cards: 'a Primary or Secondary persona's End goal, a Secondary never at the Primary's expense'.

## Acceptance Criteria

- [ ] **AC1** The shipped and project product seat cards approve a story that serves a declared Secondary persona's End goal
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_seat_admits_secondary.py -k product_seat_admits_a_secondary_goal

## Impact

Every consuming project with a Secondary persona has a product seat whose approval criterion cannot be met by that persona's work.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
