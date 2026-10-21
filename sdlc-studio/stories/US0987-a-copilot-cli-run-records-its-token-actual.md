# US0987: A Copilot CLI run records its token actual from the session events

> **Status:** Draft
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

- **AC1:** Given a fixture `events.jsonl` under `$COPILOT_HOME/session-state/<id>/` for a session recording this repo's directory, ending in a `session.shutdown` event whose `data.modelMetrics.<model>.usage` carries input, output, cache read, cache write and reasoning tokens, when the Copilot reader runs, then `tokens` is input + output + cache write, cache reads are reported apart, reasoning is not added on top of output, and the model is that model's name; a session recording another repo is never read. Fails on: adding `reasoningTokens` to output, or counting cache reads in `tokens`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_copilot.py::CopilotReaderTests::test_shutdown_aggregate_counts_one_basis
- **AC2:** Given a live session with no `session.shutdown` yet, then the reading is the sum of its per-call `assistant.usage` events, and per-call events already folded into a shutdown aggregate are never counted again, so a resumed session is not double-counted. Fails on: summing the per-call events and the aggregate for the same span
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_copilot.py::CopilotReaderTests::test_live_and_ended_sessions_are_never_double_counted
- **AC3:** Given `session.usage_info` events and a `modelMetrics` map naming two models, then `currentTokens` is ignored and the model reads as the mixed marker. Fails on: reading context-window occupancy as spend, or picking the first model
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_copilot.py::CopilotReaderTests::test_occupancy_is_not_spend_and_two_models_read_mixed
- **AC4:** Given no `COPILOT_HOME`, the reader looks under `~/.copilot`; a missing directory, an empty session or a malformed usage value returns tokens None with a named reason, never zero. Fails on: a malformed record skipped so the total is quietly short
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_copilot.py::CopilotReaderTests::test_missing_or_malformed_store_is_not_attributable
- **AC5:** Given a fixture repository and Copilot store with `SDLC_STUDIO_HARNESS=copilot`, when `sprint.py plan --write` opens a run, then the baseline it stamps names copilot and the session's events file. Fails on: the reader passing its unit tests while the plan path never reaches it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_copilot.py::CopilotLaneTests::test_plan_write_stamps_a_copilot_baseline

## Notes

- Depends on US0986. There is no Copilot session store on the development machine today: pin the event shape from a real Copilot CLI session at implementation and derive the fixture from it, rather than from the CR's description.
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
