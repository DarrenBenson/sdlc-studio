# US0904: Each lane's refusals are counted against the defects they caught

> **Status:** Done
> **Findings-filed-to:** BG0761
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/pre-commit, .githooks/commit-msg, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, tools/tests/test_lean_refusal_log.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_yield.py, changelog.d/US0904.md
> **Epic:** EP0262
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator reading the sprint report
**I want** to see, per commit lane, how many refusals led to a code change and how many only to paperwork
**So that** a lane that costs commit cycles without catching defects is named for deletion from evidence, not argued over

## Acceptance Criteria

- **AC1:** Given a commit refused by any lane of either hook, the gate block and the unit suites included, then one JSON line with the lane, a timestamp and the staged paths is appended to sdlc-studio/.local/refusals.jsonl; a commit that passes appends nothing, and writing the line never trips the repo-writes lane
  - **Verify:** pytest tools/tests/test_lean_refusal_log.py::RefusalLogTests::test_a_refused_commit_logs_its_lane_and_a_clean_one_logs_nothing
  - **Verified:** yes (2026-09-25)
- **AC2:** Given a logged refusal followed by a commit, when `sprint close` runs, then the refusal is classed a candidate catch only when that next commit writes a path that is not an artefact, baseline, index, changelog fragment or doc to a blob other than the one the refused commit staged for it, and paperwork otherwise - a retry carrying the refused blob unchanged is paperwork
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_yield.py::LaneYieldTests::test_a_refusal_is_classed_by_the_commit_that_followed_it
  - **Verified:** yes (2026-09-25)
- **AC3:** Given the close, then the report appendix carries a lane yield table giving, per lane, this run's refusals, candidate catches and paperwork
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_yield.py::LaneYieldTests::test_the_appendix_shows_lane_yield
  - **Verified:** yes (2026-09-25)
- **AC4:** Given a lane with refusals but no candidate catch across the last three runs, then the table lists it for deletion, and the close files nothing, refuses nothing and exits exactly as it would without it - the measure is not a new gate
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_yield.py::LaneYieldTests::test_a_lane_that_caught_nothing_in_three_runs_is_listed_not_enforced
  - **Verified:** yes (2026-09-25)
- **AC5:** Given a commit refused by the commit-msg hook's message rules, when the hook exits, then one line naming the message lane and the staged blobs is appended to sdlc-studio/.local/refusals.jsonl and no repo-writes snapshot is left open
  - **Verify:** pytest tools/tests/test_lean_refusal_log.py::RefusalLogTests::test_a_refused_message_is_logged_and_leaves_no_snapshot_open
  - **Verified:** yes (2026-09-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | engineering seat | BG0761: AC2 reworded to the blob rule the classifier applies; AC5 added for the message refusal |
