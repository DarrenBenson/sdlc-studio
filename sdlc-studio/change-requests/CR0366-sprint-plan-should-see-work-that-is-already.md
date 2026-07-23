# CR-0366: sprint plan should see work that is already built and committed

> **Status:** Complete
> **Decomposed-into:** EP0130
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/reconcile.py
> **Date:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

EP0087 (US0269-US0271) was built, committed and had every AC passing while its stories sat at Draft with no run ever opened. sprint plan therefore read three delivered stories as unbuilt work and forecast 675k tokens for a batch that was roughly 40 per cent already delivered. The planner has no way to notice that a story's ACs are green and its code is on main.

## Impact

Anyone planning a sprint in a repo where work landed outside a run - which includes any session that built first and opened paperwork later. The forecast is inflated, the batch looks larger than it is, and the close is under-forecast because the review of already-built work still has to happen.

## Acceptance Criteria

- [ ] Given a Draft story whose executable ACs all pass, when sprint plan selects a batch containing it, then the plan flags it as built-not-closed rather than forecasting it as new work
- [ ] Given a Draft story with failing or unrun ACs, when sprint plan runs, then it is forecast as ordinary unbuilt work (the flag does not fire on unverified stories)
- [ ] Given a batch where every unit is built-not-closed, when sprint plan runs, then it says so plainly and points at the close path instead of a build

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Raised |
