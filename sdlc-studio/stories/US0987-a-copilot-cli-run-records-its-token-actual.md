# US0987: A Copilot CLI run records its token actual from the session events

> **Status:** Done
> **Delivers:** CR0611
> **Created:** 2026-10-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_copilot.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_copilot.py, .claude/skills/sdlc-studio/reference-sprint.md, changelog.d/US0987.md
> **Epic:** EP0274
> **Points:** 5
> **Depends on:** US0986
> **Persona:** Maya Okafor

## User Story

**As a** solo founder-engineer running a sprint from GitHub Copilot CLI (Maya)
**I want** the close to record the session's token spend from Copilot's own session events
**So that** the run's tokens-per-point is measured on the same basis as a Claude run's, instead of left blank

## Acceptance Criteria

- **AC1:** Given a fixture `events.jsonl` under `$COPILOT_HOME/session-state/<id>/` for a session recording this repo's directory, ending in a `session.shutdown` event whose `data.modelMetrics.<model>.usage` carries `inputTokens`, `outputTokens`, `cacheReadTokens`, `cacheWriteTokens` and `reasoningTokens`, where `inputTokens` already includes the cached tokens (a real session on 2026-11-06 recorded `inputTokens` 27582 with `cacheWriteTokens` 27578 and an uncached input of 4), when the Copilot reader runs, then `tokens` is the uncached input + output + cache write, cache reads are reported apart, reasoning is not added on top of output, and the model is that model's name; a session recording another repo is never read. Fails on: adding `reasoningTokens` to output, counting cache reads in `tokens`, or counting the cache write twice by taking `inputTokens` as uncached input
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_copilot.py::CopilotReaderTests::test_shutdown_aggregate_counts_one_basis
  - **Verified:** yes (2026-11-06)
- **AC2:** Given a live session with no `session.shutdown` yet, then the reading is the sum of its per-call `session.usage_record` events (each `data.usage`, on the same split basis), and per-call events already folded into a shutdown aggregate are never counted again, so a resumed session is not double-counted. Fails on: summing the per-call events and the aggregate for the same span
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_copilot.py::CopilotReaderTests::test_live_and_ended_sessions_are_never_double_counted
  - **Verified:** yes (2026-11-06)
- **AC3:** Given `session.usage_checkpoint` events, which carry running session totals, and a `modelMetrics` map naming two models, then the checkpoints are never added to the per-call records and the model reads as the mixed marker. Fails on: adding a running total to the records it totals, or picking the first model
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_copilot.py::CopilotReaderTests::test_occupancy_is_not_spend_and_two_models_read_mixed
  - **Verified:** yes (2026-11-06)
- **AC4:** Given no `COPILOT_HOME`, the reader looks under `~/.copilot`; a missing directory, an empty session or a malformed usage value returns tokens None with a named reason, never zero. Fails on: a malformed record skipped so the total is quietly short
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_copilot.py::CopilotReaderTests::test_missing_or_malformed_store_is_not_attributable
  - **Verified:** yes (2026-11-06)
- **AC5:** Given a fixture repository and Copilot store with `SDLC_STUDIO_HARNESS=copilot`, when `sprint.py plan --write` opens a run, then the baseline it stamps names copilot and the session's events file. Fails on: the reader passing its unit tests while the plan path never reaches it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_copilot.py::CopilotLaneTests::test_plan_write_stamps_a_copilot_baseline
  - **Verified:** yes (2026-11-06)

## Notes

- Depends on US0986, whose selection code is on main (D0405). The precondition D0355 set is met: a real Copilot CLI 1.0.91 session ran on this machine on 2026-11-06, so derive the fixture from `~/.copilot/session-state/<id>/events.jsonl`, scrubbed, never from the CR's description.
- Adds the Copilot line to the Token meters subsection in `reference-sprint.md` (shared with US0988 to US0990, so not built in parallel with them).

## Triage (2026-10-21)

Kept (D0387). To plan it:

- External precondition unmet: D0355 says the operator runs one Copilot CLI session on this machine before US0987 starts, so the events.jsonl shape is pinned from a real store; ~/.copilot does not exist on this machine today (ls 2026-10-21), so the fixture cannot be derived as the Notes require.
- Release note stale: the story says 'Release: 6.2' but D0382 (2026-10-20, supersedes D0381) sets the path to the 6.2.0 tag as run three plus run four's doc refreshes only, so this lands after 6.2.0; re-tag when a run takes it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-06 | Claude Opus 5.5 (engineering seat) | Groomed for the next skill sprint from CR0611 and D0346: Copilot session events, live and ended sessions told apart |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-06 | Claude Opus 5.5 | Groomed for run seven: AC1-AC3 corrected against a real Copilot CLI 1.0.91 session (per-call `session.usage_record`, cached tokens inside `inputTokens`, `session.usage_checkpoint` running totals) |
