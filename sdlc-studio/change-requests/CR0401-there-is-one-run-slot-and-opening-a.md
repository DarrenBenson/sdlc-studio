# CR-0401: There is one run slot, and opening a second sprint silently merges its batch into the run already open

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint.py
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** agent (homelab session); human; v1

## Summary

`run_state.py` holds exactly one run. `sprint plan --write` calls `open_run()`, which treats an already-open run as a re-plan and UNIONs the new batch into it (`run_state.py`:489, `state["batch"] = _union(state.get("batch"), batch)`). There is no `--run-id`, no run-name argument, and no concurrent-run support anywhere on the command. So an operator who asks for a second, separate sprint while one is open does not get one, does not get a refusal, and does not get a warning - they get their new batch fused into the previous run under the previous Sprint Goal.

Found while an operator asked, in plain words, to leave an open run alone and run a bug tranche as a separate sprint. The honest answer turned out to be that the tool cannot do it, and the command that looks like it does something else instead.

The near-miss is specific. The open run was a 6-unit homeserver-evacuation batch with a Sprint Goal about ingress, photos, plex and the VPN. The requested batch was 22 bugs. Running the obvious command would have produced a 28-unit run whose Sprint Goal described a fifth of it, and whose closing goal-verdict is then unjudgeable - `achieved`, `partial` and `missed` are all defensible for a batch that is really two sprints, which means the verdict carries no information.

What makes this worse than a missing feature is the interaction with `_is_spent()` (`run_state.py`:356). A run counts as finished only if it carries `sprint_goal_verdict`, `ended_at` or `handoff` (`_CLOSE_ARTEFACTS`, line 309). A run that has been through one or more FAILED close attempts has none of those - `close_attempts` is not in the tuple - so it is still `running` and still absorbs. The run in question had a recorded close attempt from the day before that left 9 items outstanding. Precisely the run an operator is most likely to want to set aside and work around is precisely the one that silently absorbs the next batch.

This is the same class as L-0045 in the consuming project ('close the old run before opening the new one, or the goal verdict is stranded'), which was recorded after it bit, and then bit again the same day. That lesson is currently the only thing standing between an operator and this behaviour. A lesson is not a control.

## Impact

Every operator running more than one workstream in a repository. The failure is silent and it corrupts the sprint record rather than blocking work, so it is found late - at the close, when the goal verdict cannot be given honestly, by which point the two batches cannot be separated. Velocity, token-per-point rate and estimate-versus-actual are all measured per run and all become meaningless for a fused run: the forecast recorded at plan time was for one batch and the actual covers two. Because those measurements feed the NEXT sprint's forecast, one fused run degrades planning for every run after it.

The workarounds available today are all bad. Hand-archiving the open run to `.local/run-archive/` and restoring it later is the manoeuvre that produced L-0045. Closing the open run early to free the slot forces a premature, dishonest verdict on unstarted work. Working the second batch with no run state at all - what this operator chose - is safe but silently forfeits the ceremony: no goal verdict, no retro, no velocity row, no telemetry, so the sprint is invisible to every measurement the tool exists to produce.

## Acceptance Criteria

- [ ] Planning a batch with --write, against a repository whose open run holds a disjoint batch, refuses: it exits non-zero and run-state.json is byte-identical afterwards. Today it succeeds and the two batches are fused.
- [ ] The refusal names the open run's id, its outcome and its current batch size, and states both ways forward - close that run, or re-plan it deliberately - so the operator can act without reading the source.
- [ ] A genuine re-plan, where the incoming batch overlaps the open run's, still accumulates exactly as it does today, and needs no new flag to do so.
- [ ] A run whose only close artefact is a FAILED close attempt is treated as open-and-protected rather than absorbable. A recorded close attempt currently leaves a run fully absorbable, which is the case most likely to be hit.
- [ ] help/sprint.md states that there is a single run slot, and says what happens when a second batch is planned while a run is open.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | agent (homelab session) | Raised |
