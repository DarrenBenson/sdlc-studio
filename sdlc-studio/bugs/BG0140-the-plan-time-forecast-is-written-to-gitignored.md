# BG0140: The plan-time forecast is written to gitignored .local/, so BG0133 fix does not survive a clone

> **Status:** Fixed
> **Severity:** High
> **Effort:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/telemetry.py, .claude/skills/sdlc-studio/scripts/retro.py, .gitignore
> **Verification depth:** functional - proven by ATTACK. A tree was built from `git ls-files` alone (a real fresh clone, with no `.local/` directory present at all) and `retro.py accuracy --id RETRO0026` reported 5 of 5 measured, 5 of 5 forecast at plan time, batch 0.39x - and `velocity` reproduced all three sprints (3.34x in-sample, 0.55x, 0.39x) exactly. Before the fix every unit in that tree read UNFORECAST and the history read as no-evidence.
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

BG0133 made the plan-time forecast the authoritative record - the number a sprint is judged against, and the thing that makes the estimator falsifiable at all. It is written to sdlc-studio/.local/forecasts.jsonl, which is gitignored (**/.local/). So it is user-local runtime state on one machine: on a fresh clone, on CI, or for any other team member, every forecast is absent and every unit reads UNFORECAST. The fix defeats itself. This is the exact trap retro.py already documents and avoids for the velocity history - its own comment says VELOCITY.md is committed because "a gitignored .local/ file would not survive a fresh clone, and history the team cannot read is not history" - and then the forecast log went into .local/ anyway. The derived records (VELOCITY.md, the retro accuracy block) ARE committed, so the headline ratios survive; what does not survive is the per-unit evidence underneath them, which is what any future recalibration decision has to be made from. The same defect covers telemetry.jsonl: 361 measured records, 15 of them carrying real token/model data, none of it in git.

## Steps to Reproduce

1. git check-ignore -v sdlc-studio/.local/forecasts.jsonl -> .gitignore:91:**/.local/. 2. Same for sdlc-studio/.local/telemetry.jsonl. 3. Clone the repo fresh, or check out on another machine. 4. Run retro.py accuracy --id RETRO0025: every unit is UNFORECAST and the batch ratio is None, because the forecasts that were recorded at plan time are not in the repository.

## Proposed Fix

The forecast and the actuals are project evidence, not user-local runtime state, and must be committed. Move both out of .local/ to a tracked location beside the retros (retros/ already holds the committed VELOCITY.md and is the precedent), or un-ignore them explicitly. Append-only JSONL merges badly on conflict, so decide the merge story deliberately: one file per sprint keyed by retro id is the obvious shape and matches how VELOCITY.md already rows up. Whatever is chosen, the rule is the one already written in retro.py: evidence the team cannot read on a fresh clone is not evidence.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
