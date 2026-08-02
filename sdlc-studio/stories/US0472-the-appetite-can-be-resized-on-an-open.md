# US0472: The appetite can be resized on an open run with a recorded reason, and the standing capacity it is measured against survives the resize

> **Status:** Ready
> **Delivers:** CR0441
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_appetite_resize.py, .claude/skills/sdlc-studio/help/sprint.md, changelog.d/US0472.md
> **Epic:** EP0171
> **Points:** 3

## User Story

**As a** operator who has decided a running sprint should be bigger
**I want** to change the run's appetite with a stated reason on the record
**So that** making the sprint bigger is a decision with a trail rather than a number quietly exceeded

## Acceptance Criteria

### AC1: AC1: a resize writes the new accepted appetite and a change record

- **Given** an open run with a recorded appetite
- **When** `sprint.py appetite --units N --minutes M --reason "..."` runs
- **Then** the run state's accepted `units`/`minutes` are the new pair and an appetite-change entry records the previous pair, the new pair, the reason and the timestamp
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_appetite_resize.py::AppetiteResizeTests::test_a_resize_writes_the_new_pair_and_records_the_reason
- **Verified:** yes (2026-08-02)

### AC2: AC2: a resize with no reason, or with no open run, writes nothing

- **Given** an open run, and separately a tree with no open run
- **When** the resize is invoked without `--reason`, and again against the tree with no run
- **Then** both exit non-zero naming the cause, and in the open-run case run-state.json is byte-identical
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_appetite_resize.py::AppetiteResizeTests::test_a_reasonless_resize_and_a_runless_resize_both_write_nothing
- **Verified:** yes (2026-08-02)

### AC3: AC3: the standing pair is preserved, so the close still reports the overage honestly

- **Given** a run whose appetite is raised past `appetite.standing_units` / `standing_minutes` (run_state.appetite_record)
- **When** the close's over-appetite line is rendered after the resize
- **Then** the standing pair on the run state is unchanged, `appetite_overage` returns the raised accepted pair against the original standing pair with the axis flagged, and the line reports the over-commitment against the standing capacity, never against the raised ceiling
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_appetite_resize.py::AppetiteResizeTests::test_a_raised_appetite_reports_the_overage_against_the_unchanged_standing_pair
- **Verified:** yes (2026-08-02)

### AC4: AC4: the run breaker stops on the resized number, not the planned one

- **Given** a run planned at a unit appetite the loop has already reached
- **When** the appetite is raised and `loop_guard._resolve_appetite` / `budget_verdict` resolve the run's budget at the next unit boundary
- **Then** the breaker resolves the RESIZED accepted pair off run-state.json and does not fire, so the planner and the breaker still read one number
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_appetite_resize.py::AppetiteResizeTests::test_loop_guard_resolves_the_resized_appetite_and_does_not_fire
- **Verified:** yes (2026-08-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
