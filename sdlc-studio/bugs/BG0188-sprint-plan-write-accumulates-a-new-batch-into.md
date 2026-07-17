# BG0188: sprint plan --write accumulates a new batch into a prior run left outcome=running, reusing its id and clobbering its verdict

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Verification depth:** functional (unit: a judged run left `outcome=running` is minted fresh, not accumulated; the verdict does not leak; a clean running run still accumulates)
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint.py
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`open_run` reuses an existing run-state whenever outcome==running. A prior sprint that was reviewed and signed off (goal-verdict recorded, retro committed) but whose run-state was NOT finalised to a terminal outcome stays outcome=running, so the next 'sprint plan --write' silently accumulates the new batch into the CLOSED run via _union, keeps the old `run_id` and `started_at`, and stamps the new --sprint-goal over the old (already-judged) verdict. Hit live planning EP0084: 'plan --write' opened RUN-01KXR6XS (the closed spec-truth sprint, RETRO0046, commit 31e1455) and merged US0258/US0259/US0260 onto its 17 terminal units (20-unit mixed batch), overwriting its achieved verdict. run-state is ephemeral (.local, gitignored) so no tracked history was lost, but a run's retro/telemetry would have been corrupted (batch, id and verdict all wrong) had it not been caught. Root: a run can hold a recorded `sprint_goal_verdict` while outcome is still 'running' - an inconsistent state `open_run` does not detect.

## Steps to Reproduce

1. Close a sprint but leave its run-state at outcome=running (e.g. the close chain stops before the handoff step that calls `close_run`, or the verdict is recorded via goal-verdict without completing 'sprint close'). 2. Run 'sprint plan --stories Ready --epic EPxxxx --goal plan --sprint-goal "..." --write'. 3. Observe: it prints 'opened run RUN-<old-id>' (not a fresh id), the run-state batch is the union of the old terminal units and the new ones, `started_at` is the old run's, and the new `sprint_goal` overwrites the prior `sprint_goal_verdict`'s run.

## Proposed Fix

Two-part. (1) The close ceremony must guarantee finalisation: a run carrying a recorded `sprint_goal_verdict` is closed - `close_run` must set a terminal outcome + `ended_at`, and 'sprint close' should not report success while outcome stays running. (2) Defensive guard in `open_run`/plan --write: a run-state that has a `sprint_goal_verdict` (or any close artefact: handoff, `ended_at)` but outcome==running is inconsistent; `open_run` must treat it as CLOSED (mint fresh) or refuse loudly, never accumulate. A judged run is history regardless of the outcome string.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Filed |
