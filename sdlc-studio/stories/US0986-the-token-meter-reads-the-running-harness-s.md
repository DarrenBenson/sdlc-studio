# US0986: The token meter reads the running harness's store, chosen by SDLC_STUDIO_HARNESS or the environment, and never sums two

> **Status:** Draft
> **Delivers:** CR0611
> **Created:** 2026-10-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/lib/token_meters.py, .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/reference-sprint.md, changelog.d/US0986.md
> **Epic:** EP0274
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** solo founder-engineer running sprints from whichever agent harness the project uses (Maya)
**I want** the token meter to read the store of the harness that is actually running, and only that one
**So that** a sprint driven by Cursor, Copilot CLI or OpenCode can be measured instead of left blank, and a leftover store from another harness is never booked onto it

## Acceptance Criteria

- **AC1:** Given a fixture Claude transcript and either `SDLC_STUDIO_HARNESS=claude` or no selection with only Claude signalled, when the meter is read, then the reading equals today's `session_tokens` figure for that transcript (input + output + cache creation, cache reads excluded, the main-thread basis), and a malformed usage record still refuses the read. Fails on: the dispatcher re-implementing the Claude sum and counting cache reads, or skipping the malformed record
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py::HarnessSelectionTests::test_claude_reading_is_unchanged
- **AC2:** Given `SDLC_STUDIO_HARNESS` set to cursor, copilot or opencode and a readable Claude transcript in the same fixture, when the meter is read, then only the chosen harness's reader is consulted, the Claude transcript is never opened, and a harness with no reader installed returns tokens None with a reason naming the harness, never zero. Fails on: falling back to the Claude transcript when the chosen reader returns nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py::HarnessSelectionTests::test_a_chosen_harness_never_reads_another_store
- **AC3:** Given no `SDLC_STUDIO_HARNESS`, when exactly one harness is signalled by the environment (`CLAUDECODE`; `CURSOR_AGENT` or a Cursor run id; `COPILOT_HOME`; `OPENCODE` or `OPENCODE_DB`), then that harness is selected even when another harness's store sits on disk; when two are signalled, or none is and two stores are present, the reading is tokens None with a reason naming every candidate and no total is formed. Fails on: choosing by a fixed precedence order, a store on disk outranking an environment signal, or adding two readings
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py::HarnessSelectionTests::test_two_unselected_harnesses_name_the_candidates
- **AC4:** Given any reader's result, then the reading and every stamp `open_run` or `stamp_tokens` writes name the harness, carry cache reads as a separate figure outside `tokens` (D0346), and a run total never subtracts a reading of one harness from a reading of another. Fails on: stamps keyed by source alone with no harness recorded, or cache reads folded into the headline
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py::HarnessSelectionTests::test_readings_and_stamps_name_the_harness
- **AC5:** Given a fixture repository with an open run and `SDLC_STUDIO_HARNESS=opencode` where only a Claude transcript exists, when `retro.py accuracy --id <retro> --tokens-from-harness` runs, then no token figure is recorded and the output names opencode and the reason. Fails on: the library honouring the selection while the CLI path still reads the Claude transcript through the `harness_tokens` alias
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py::HarnessLaneTests::test_accuracy_names_the_harness_it_could_not_read

## Notes

- Design: `lib/token_meters.py` owns selection and dispatch. Each harness reader is its own module, `lib/meter_<harness>.py`, exposing one `read` function and loaded by name, so US0987 to US0990 each add a module without editing the dispatcher; a module that is not there reads as "no reader for <harness> yet". The Claude reader keeps `session_tokens`' body and its `SDLC_STUDIO_TRANSCRIPTS` override, and `session_tokens` becomes the dispatcher, so `open_run`, `stamp_tokens`, `retro.harness_tokens` and the report's legacy reading all inherit the selection unchanged.
- `reference-sprint.md` gains a short Token meters subsection: `SDLC_STUDIO_HARNESS`, the selection order, the never-sum rule and the one basis. Each reader story adds its own line there.
- Builds first: every other EP0274 story depends on it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-06 | Claude Opus 5.5 (engineering seat) | Groomed for the next skill sprint from CR0611 and D0346: retro.py and its tests move to US0991, which owns the basis wording |
