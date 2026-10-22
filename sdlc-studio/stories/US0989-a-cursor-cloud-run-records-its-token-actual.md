# US0989: A Cursor cloud run records its token actual from the usage API when a key is present

> **Status:** Draft
> **Delivers:** CR0611
> **Created:** 2026-10-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_cursor.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py, .claude/skills/sdlc-studio/reference-sprint.md, changelog.d/US0989.md
> **Epic:** EP0274
> **Points:** 5
> **Depends on:** US0986
> **Persona:** Maya Okafor

## User Story

**As a** solo founder-engineer running a sprint as a Cursor cloud agent (Maya)
**I want** the close to record the run's token spend from Cursor's usage API when a key is available
**So that** a Cursor sprint such as a consuming project's RUN-01M48BNK publishes a measured token actual instead of NOT MEASURED

## Acceptance Criteria

- **AC1:** Given a Cursor API key and a run id in the environment and a stub endpoint returning `totalUsage` with `inputTokens`, `outputTokens`, `cacheWriteTokens`, `cacheReadTokens` and `totalTokens`, when the Cursor reader runs, then `tokens` is input + output + cache write, cache reads are reported apart, and the source names the agent id. Fails on: taking `totalTokens`, which includes cache reads (D0346)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py::CursorCloudTests::test_usage_payload_counts_one_basis
- **AC2:** Given no key or no run id, then no request is made; given an HTTP error, a timeout or a run with no usage recorded yet, then the reading is tokens None with a named reason, never zero, and the request is bounded by a short timeout so the close is never held. Fails on: a request issued without a key, an unbounded wait, or an empty usage read as zero
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py::CursorCloudTests::test_no_key_no_call_and_failures_not_attributable
- **AC3:** Given a successful or failed call, then the key never appears in the reading, a stamp, the run state, a reason string or the report. Fails on: an error message that echoes the request headers, or a source built from the authenticated URL
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py::CursorCloudTests::test_the_key_is_never_recorded
- **AC4:** Given a fixture repository, a local stub server and `SDLC_STUDIO_HARNESS=cursor`, when `sprint.py plan --write` opens a run, then the baseline it stamps names cursor and the agent id. Fails on: the reader passing its unit tests while the plan path never reaches it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py::CursorCloudLaneTests::test_plan_write_stamps_a_cursor_baseline

## Notes

- Depends on US0986. Stdlib only (`urllib.request`), with the endpoint base overridable by an environment variable so tests use a local stub and never the network.
- Pin the names of the key and run-id environment variables a Cursor cloud agent actually sets at implementation, from a real cloud run.
- US0990 shares `lib/meter_cursor.py`, so the two build in sequence, this one first.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- AC1/AC2 depend on 'a Cursor API key and a run id in the environment' whose variable names are not pinned (Notes: 'Pin the names ... from a real cloud run'); a real Cursor cloud run is needed before the build, or the criteria should name the variables.
- Release note stale: the story says 'Release: 6.2' but D0382 (2026-10-20, supersedes D0381) sets the path to the 6.2.0 tag as run three plus run four's doc refreshes only, so this lands after 6.2.0; re-tag when a run takes it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-06 | Claude Opus 5.5 (engineering seat) | Groomed for the next skill sprint from CR0611 and D0346: Cursor cloud usage API, opt-in by key with a short timeout (D0346) |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
