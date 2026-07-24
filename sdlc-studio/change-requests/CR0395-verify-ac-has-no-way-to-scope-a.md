# CR-0395: verify_ac has no way to scope a run to a sprint's batch, so verifying 23 stories re-runs every AC in the workspace

> **Status:** Complete
> **Decomposed-into:** EP0147
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

At RUN-01KY3MFX's build I needed the 23 stories of the batch in the verify report, which the close gate reads. `verify_ac.py run` takes `--id` for ONE story or nothing for the whole workspace; there is no batch form. Running it whole took over nine minutes of wall clock and shelled out to pytest for hundreds of ACs that no part of the sprint had touched. The alternative, 23 separate `--id` invocations, pays process startup 23 times and is what an agent will reach for once it has been burned by the nine minutes. Neither is right. The sprint plan already knows exactly which units are in the batch, and the run state records them, so the information to scope this exists and is not offered.

## Impact

Any sprint close on a workspace with more than a few dozen stories, and it gets worse as a project accumulates them - the cost of verifying THIS sprint grows with the size of every sprint before it. Wall clock rather than correctness, but nine minutes is long enough that an agent under time pressure will skip the run or scope it by hand and get the scope wrong.

## Acceptance Criteria

- [ ] `verify_ac run` accepts a batch: a list of ids, a worklist file, or the current run state's batch.
- [ ] The report it writes MERGES with the existing report rather than replacing it, so a scoped run does not blank the verdicts for stories outside the scope.
- [ ] The scoped and unscoped runs produce identical verdicts for the stories they share.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Raised |
