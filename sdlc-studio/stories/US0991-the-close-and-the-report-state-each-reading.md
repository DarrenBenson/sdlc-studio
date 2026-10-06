# US0991: The close and the report state each reading's own basis, and add delegated tokens only when the reading excludes subagent spend

> **Status:** Draft
> **Delivers:** CR0611
> **Created:** 2026-10-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, changelog.d/US0991.md
> **Epic:** EP0274
> **Points:** 3
> **Depends on:** US0986
> **Persona:** Maya Okafor

## User Story

**As a** solo founder-engineer reading a sprint report from a non-Claude harness (Maya)
**I want** the close and the report to state what that harness's meter counted, and whether subagent spend is already in it
**So that** I am not told "main thread only" about a figure that includes subagents, and delegated spend is never counted twice

## Acceptance Criteria

- **AC1:** Given a reading whose basis says it includes subagent spend and a supplied delegated total on the run, when `run_attributed_tokens` forms the run's figure, then the delegated total is not added and the basis says why. Fails on: adding `delegated_tokens` unconditionally, which counts subagent spend twice
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::HarnessBasisTests::test_delegated_not_added_when_the_reading_includes_subagents
- **AC2:** Given a Claude reading (main thread only) and a supplied delegated total, then the delegated total is still added and the figure is still a lower bound, as today. Fails on: dropping the delegated path for every harness
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::HarnessBasisTests::test_delegated_still_added_for_a_main_thread_reading
- **AC3:** Given a report filed for a run metered by a non-Claude harness, then the cost section names the harness and the reading's own basis, and says "main thread" only when the reading does. Fails on: the fixed main-thread prose in `run_attributed_tokens`, `TOKEN_TOTAL_BASIS` or the report's cost section
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::HarnessBasisReportTests::test_cost_section_states_the_readings_basis
- **AC4:** Given a report filed before this change for a Claude-metered run, then it still re-derives to its filed fingerprint and checks VALID. Fails on: rewording the Claude basis so every earlier signed page re-derives differently
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::HarnessBasisReportTests::test_a_claude_report_rederives_unchanged

## Notes

- Depends on US0986, which puts the harness and the includes-subagents flag on every reading.
- AC4 guards the signed pages: the Claude wording is kept byte for byte, and only a reading that says otherwise changes the sentence.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-06 | Claude Opus 5.5 (engineering seat) | Groomed for the next skill sprint from CR0611 and D0346: split from US0986 so the selection and the wording are sized apart |
