# US0372: validate the commit-message rules ahead of the test lanes, no lane lost or duplicated, order pinned

> **Status:** Draft
> **Delivers:** CR0367
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0131
> **Points:** 5
> **Affects:** .githooks/pre-commit, .githooks/commit-msg, tools/tests/test_message_first_gate.py, tools/tests/test_precommit_lane_order.py, tools/tests/test_commit_msg_hook.py

## User Story

**As an** author committing work that touches scripts
**I want** the commit-message rules checked before the unit suites run
**So that** a one-line message defect is refused in seconds instead of costing two full suite runs, which is what teaches an agent to reach for `--no-verify`

## Acceptance Criteria

### AC1: A refused message never pays for the unit suites

- **Given** a staged change that selects the unit suites, and a subject naming two work-item ids with no `Refs:` trailer
- **When** the commit is attempted against the tracked hooks
- **Then** the commit is refused with the same message and paste-ready trailers as today, and neither the skill-tests nor the tool-tests lane executed - git runs `pre-commit` before the message exists, so the expensive lanes sit behind the message check in `commit-msg`
- **Verify:** pytest tools/tests/test_message_first_gate.py::MessageBeforeSuitesTests::test_a_refused_message_never_reaches_the_unit_suites

### AC2: A valid message leaves the verdict and the coverage unchanged

- **Given** the same staged change with a message the rules accept
- **When** the commit runs
- **Then** every lane that ran before the move still runs, exactly once across the hook pair, and a failure in any of them still blocks the commit - the move adds no refusal and removes no check
- **Verify:** pytest tools/tests/test_message_first_gate.py::LaneInventoryTests::test_every_lane_runs_exactly_once_across_the_hook_pair

### AC3: The order is pinned so it cannot silently revert

- **Given** the tracked hooks as shipped
- **When** the lane order is read from them
- **Then** the commit-message check is invoked before the first expensive lane, and the timing and budget recording still wraps the suites wherever they now run
- **Verify:** pytest tools/tests/test_precommit_lane_order.py::MessageCheckOrderTests::test_the_message_check_precedes_the_expensive_lanes

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: real ACs + Affects authored |
