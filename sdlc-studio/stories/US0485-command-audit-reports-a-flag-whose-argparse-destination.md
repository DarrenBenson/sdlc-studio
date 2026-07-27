# US0485: command_audit reports a flag whose argparse destination no line ever reads

> **Status:** Ready
> **Delivers:** CR0448
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/command_audit.py, .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py
> **Epic:** EP0175
> **Points:** 5

## User Story

**As a** operator trusting a documented flag to change what a command does
**I want** a flag whose destination is never read to be reported as dead
**So that** a flag cannot ship wearing live documentation while doing nothing

## Acceptance Criteria

### AC1: a flag whose destination is never CONSUMED is reported

- **Given** a module defining a flag whose parsed value is passed on but never consumed by any line that acts on it
- **When** the detector runs
- **Then** it reports that flag, naming the module and the destination - the analysis follows the value into the callee rather than counting the sites that mention it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::DeadFlagTests::test_a_flag_whose_value_is_never_consumed_is_reported

### AC2: it is proven on verify_batch as gate.py carries it today

- **Given** gate.py's three live verify_batch sites - the argparse definition, the defaulted lookup that forwards it, and the run_gate parameter no line of the body reads - pinned as a fixture rather than described as a past state
- **When** the detector runs over that fixture
- **Then** it reports verify_batch, so the defence is validated against the exact shape that motivated it; this holds whether or not US0479 has deleted the flag, because the fixture pins the three lines
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::DeadFlagTests::test_the_detector_catches_verify_batch_from_a_pinned_fixture

### AC3: a defaulted lookup whose value IS consumed is not reported

- **Given** a flag read through a defaulted attribute lookup whose receiving parameter is then acted on
- **When** the detector runs
- **Then** it does not report that flag - the discriminator is consumption, not the access pattern, which is what made the first specification unable to catch verify_batch
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::DeadFlagTests::test_a_consumed_defaulted_lookup_is_not_reported

### AC4: the detector runs where it can be seen

- **Given** the repo's quality gate
- **When** it runs
- **Then** the dead-flag report is one of its lanes, because a detector nothing invokes cannot stop a flag shipping
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::DeadFlagTests::test_the_detector_is_wired_into_the_gate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: acceptance criteria authored against the slice |
| 2026-07-27 | Claude Fable 5 | ACs repaired against the independent adversarial review |
